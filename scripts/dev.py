from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable

import tomllib

ROOT = Path(__file__).resolve().parents[1]
CLEAN_PATHS = (
    ROOT / "build",
    ROOT / "dist",
    ROOT / ".tmp_dist",
    ROOT / ".pytest_cache",
    ROOT / ".ruff_cache",
    ROOT / "__pycache__",
    ROOT / "ru_normalizr.egg-info",
)
CLEAN_GLOBS = (
    "**/__pycache__",
    "dictionaries/**/dictionaries_*.pkl",
)


def run(*args: str) -> int:
    print(f"> {' '.join(args)}")
    completed = subprocess.run(args, cwd=ROOT)
    return completed.returncode


def clean() -> int:
    for path in CLEAN_PATHS:
        if path.exists():
            shutil.rmtree(path)
    for pattern in CLEAN_GLOBS:
        for path in ROOT.glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
            elif path.exists():
                path.unlink()
    return 0


def project_version() -> str:
    with (ROOT / "pyproject.toml").open("rb") as fh:
        return tomllib.load(fh)["project"]["version"]


def package_version() -> str:
    init_text = (ROOT / "__init__.py").read_text(encoding="utf-8")
    match = re.search(r'^__version__ = "([^"]+)"$', init_text, re.MULTILINE)
    if not match:
        raise RuntimeError("Could not find __version__ in __init__.py")
    return match.group(1)


def check_versions() -> int:
    pyproject_version = project_version()
    init_version = package_version()
    if pyproject_version != init_version:
        sys.stderr.write(
            "Version mismatch:\n"
            f"  pyproject.toml: {pyproject_version}\n"
            f"  __init__.py:    {init_version}\n"
        )
        return 1
    print(f"Version OK: {pyproject_version}")
    return 0


def lint() -> int:
    return run(sys.executable, "-m", "ruff", "check", ".")


def test() -> int:
    return run(sys.executable, "-m", "pytest", "-q")


def build() -> int:
    clean()
    return run(sys.executable, "-m", "build", ".")


def dist_artifacts() -> list[Path]:
    dist_dir = ROOT / "dist"
    if not dist_dir.exists():
        return []
    return sorted(
        path
        for path in dist_dir.iterdir()
        if path.is_file() and (path.suffix == ".whl" or path.name.endswith(".tar.gz"))
    )


def twine_check() -> int:
    artifacts = dist_artifacts()
    if not artifacts:
        sys.stderr.write("No distribution artifacts found in dist/.\n")
        return 1
    return run(sys.executable, "-m", "twine", "check", *(str(path) for path in artifacts))


def upload(repository: str | None = None) -> int:
    artifacts = dist_artifacts()
    if not artifacts:
        sys.stderr.write("No distribution artifacts found in dist/. Run build or check first.\n")
        return 1
    args = [sys.executable, "-m", "twine", "upload"]
    if repository and repository != "pypi":
        args.extend(["--repository", repository])
    args.extend(str(path) for path in artifacts)
    return run(*args)


def check() -> int:
    steps: list[tuple[str, Callable[[], int]]] = [
        ("clean", clean),
        ("version", check_versions),
        ("lint", lint),
        ("test", test),
        ("build", lambda: run(sys.executable, "-m", "build", ".")),
        ("twine-check", twine_check),
    ]
    for name, step in steps:
        print(f"\n== {name} ==")
        code = step()
        if code:
            return code
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Local developer and release helper.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ("clean", "lint", "test", "build", "check"):
        subparsers.add_parser(command)

    publish_parser = subparsers.add_parser("publish")
    publish_parser.add_argument(
        "--repository",
        choices=("pypi", "testpypi"),
        default="pypi",
        help="Upload target. Defaults to PyPI.",
    )
    publish_parser.add_argument(
        "--skip-check",
        action="store_true",
        help="Upload existing dist/* artifacts without rerunning checks.",
    )

    args = parser.parse_args(argv or sys.argv[1:])
    if args.command == "clean":
        return clean()
    if args.command == "lint":
        return lint()
    if args.command == "test":
        return test()
    if args.command == "build":
        return build()
    if args.command == "check":
        return check()
    if not args.skip_check:
        code = check()
        if code:
            return code
    return upload(args.repository)


if __name__ == "__main__":
    raise SystemExit(main())
