#!/usr/bin/env python3
"""Verify the target app still builds after each workflow step.

Checks only layers that exist (BE, FE, contract). Missing layers are skipped.
Exit 0 = all present layers build; non-zero = fix before marking step done.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], *, cwd: Path, label: str) -> int:
    print(f"==> {label}")
    print(f"    {' '.join(cmd)}")
    rc = subprocess.call(cmd, cwd=cwd)
    if rc != 0:
        print(f"app_build_verify failed: {label}")
    return rc


def verify_contract(contract_dir: Path) -> list[tuple[str, int]]:
    checks: list[tuple[str, int]] = []
    openapi = contract_dir / "openapi.yaml"
    if not openapi.is_file():
        return checks

    text = openapi.read_text(encoding="utf-8")
    if "openapi:" not in text:
        print("app_build_verify failed: contract openapi.yaml missing openapi: key")
        checks.append(("contract/openapi.yaml", 1))
        return checks

    types_ts = contract_dir / "types.ts"
    if types_ts.is_file() and not types_ts.read_text(encoding="utf-8").strip():
        print("app_build_verify failed: contract types.ts is empty")
        checks.append(("contract/types.ts", 1))
        return checks

    print("==> contract OK")
    checks.append(("contract", 0))
    return checks


def verify_backend(api_dir: Path, py: str) -> list[tuple[str, int]]:
    app_dir = api_dir / "app"
    if not app_dir.is_dir():
        return []

    results: list[tuple[str, int]] = []
    rc = run([py, "-m", "compileall", "app", "-q"], cwd=api_dir, label="backend compileall")
    results.append(("backend/compileall", rc))
    if rc != 0:
        return results

    rc = run(
        [py, "-c", "from app.main import app"],
        cwd=api_dir,
        label="backend import app.main",
    )
    results.append(("backend/import", rc))
    return results


def verify_frontend(web_dir: Path) -> list[tuple[str, int]]:
    package_json = web_dir / "package.json"
    if not package_json.is_file():
        return []

    data = json.loads(package_json.read_text(encoding="utf-8"))
    if "build" not in (data.get("scripts") or {}):
        print("==> frontend skipped (no build script in package.json)")
        return []

    npm = shutil.which("npm")
    if not npm:
        print("app_build_verify failed: npm not found on PATH")
        return [("frontend/npm", 1)]

    node_modules = web_dir / "node_modules"
    if not node_modules.is_dir():
        rc = run([npm, "install"], cwd=web_dir, label="frontend npm install")
        if rc != 0:
            return [("frontend/npm install", rc)]

    rc = run([npm, "run", "build"], cwd=web_dir, label="frontend npm run build")
    return [("frontend/build", rc)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify target app builds")
    parser.add_argument("--repo", type=Path, default=Path("."))
    args = parser.parse_args()
    repo = args.repo.resolve()
    py = sys.executable

    api_dir = repo / "apps" / "api"
    web_dir = repo / "apps" / "web-react"
    contract_dir = repo / "packages" / "contract"

    all_results: list[tuple[str, int]] = []
    all_results.extend(verify_contract(contract_dir))
    all_results.extend(verify_backend(api_dir, py))
    all_results.extend(verify_frontend(web_dir))

    if not all_results:
        print("app_build_verify OK (no app layers scaffolded yet)")
        return 0

    failed = [name for name, rc in all_results if rc != 0]
    if failed:
        print(f"app_build_verify FAILED: {', '.join(failed)}")
        return 1

    layers = ", ".join(name for name, _ in all_results)
    print(f"app_build_verify OK ({layers})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
