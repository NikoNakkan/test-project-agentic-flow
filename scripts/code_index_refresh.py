#!/usr/bin/env python3
"""Build graph.db → sync context MDs → validate strict symbol_id linkage."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser(description="Full code index refresh")
    parser.add_argument("--repo", type=Path, default=Path("."))
    args = parser.parse_args()
    repo = args.repo.resolve()
    py = sys.executable

    steps = [
        ([py, str(SCRIPTS / "code_index_build.py"), "--repo", str(repo)], "build"),
        ([py, str(SCRIPTS / "code_index_sync_context.py"), "--repo", str(repo)], "sync"),
        ([py, str(SCRIPTS / "code_index_validate.py"), "--repo", str(repo)], "validate"),
    ]
    for cmd, label in steps:
        print(f"==> {label}")
        rc = subprocess.call(cmd)
        if rc != 0:
            print(f"code_index_refresh failed at: {label}")
            return rc
    print("code_index_refresh OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
