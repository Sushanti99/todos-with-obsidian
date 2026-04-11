"""Temporary compatibility wrapper for Brain V1."""

from __future__ import annotations

import sys

from brain.cli import main as brain_main


def main() -> int:
    argv = sys.argv[1:]
    if argv[:1] == ["chat"]:
        argv = ["start", *argv[1:]]
    return brain_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
