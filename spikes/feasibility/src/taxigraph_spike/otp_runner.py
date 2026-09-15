"""Wrapper around the pinned OTP 2.9.0 shaded jar: build, then load/serve.

Builds and serves on loopback only, using only the spike's own graph
directory. Does not reimplement any street/transit graph algorithm.
"""

from __future__ import annotations

import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from .process_utils import popen_hidden, run_hidden

GRAPHQL_PATH = "/otp/gtfs/v1"
LOOPBACK_PORT = 8080


@dataclass(frozen=True)
class BuildResult:
    status: str  # "ok" | "build_failed" | "missing_prerequisite" | "error"
    detail: str
    graph_dir: Path | None = None
    build_log: str = ""


def build_graph(
    jar_path: Path,
    gtfs_zip: Path,
    osm_pbf: Path,
    build_dir: Path,
    graph_dir: Path,
    heap: str = "-Xmx2G",
    timeout_seconds: int = 900,
) -> BuildResult:
    if not jar_path.is_file():
        return BuildResult("missing_prerequisite", f"OTP jar not found at {jar_path}")
    if not gtfs_zip.is_file():
        return BuildResult("error", f"GTFS feed not found at {gtfs_zip}")
    if not osm_pbf.is_file():
        return BuildResult("missing_prerequisite", f"OSM extract not found at {osm_pbf}")

    build_dir.mkdir(parents=True, exist_ok=True)
    graph_dir.mkdir(parents=True, exist_ok=True)

    # Build input dir must hold only the intended GTFS/PBF, per SOL-HANDOFF.
    for existing in build_dir.iterdir():
        if existing.is_file():
            existing.unlink()
    shutil.copy2(gtfs_zip, build_dir / gtfs_zip.name)
    shutil.copy2(osm_pbf, build_dir / osm_pbf.name)

    args = [
        "java",
        heap,
        "-jar",
        str(jar_path.resolve()),
        "--build",
        "--save",
        str(build_dir.resolve()),
    ]

    try:
        proc = run_hidden(args, timeout=timeout_seconds)
    except FileNotFoundError:
        return BuildResult("missing_prerequisite", "java not found on PATH")
    except subprocess.TimeoutExpired:
        return BuildResult("error", f"OTP build did not finish within {timeout_seconds}s")

    build_log = proc.stdout + proc.stderr
    built_graph = build_dir / "graph.obj"
    if proc.returncode != 0 or not built_graph.is_file():
        return BuildResult("build_failed", f"OTP build exited {proc.returncode}; no graph.obj produced", build_log=build_log)

    shutil.move(str(built_graph), str(graph_dir / "graph.obj"))
    return BuildResult("ok", "graph built", graph_dir=graph_dir, build_log=build_log)


def start_server(jar_path: Path, graph_dir: Path, heap: str = "-Xmx2G", port: int = LOOPBACK_PORT) -> subprocess.Popen:
    args = [
        "java",
        heap,
        "-jar",
        str(jar_path.resolve()),
        "--load",
        str(graph_dir.resolve()),
        "--port",
        str(port),
    ]
    return popen_hidden(args)


def wait_for_ready(base_url: str, timeout_seconds: int = 120, poll_interval_seconds: float = 2.0) -> bool:
    import urllib.error
    import urllib.request

    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(base_url, timeout=5):
                return True
        except (urllib.error.URLError, OSError):
            time.sleep(poll_interval_seconds)
    return False


def stop_server(proc: subprocess.Popen, timeout_seconds: int = 20) -> None:
    proc.terminate()
    try:
        proc.wait(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=timeout_seconds)
