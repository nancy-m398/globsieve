"""Thin CLI on top of globsieve.core.

The filesystem walk lives here on purpose: core.py stays free of I/O so its
matching rules can be tested without a real directory tree.
"""

import argparse
import os
import sys
from typing import IO, Iterator, Optional, Sequence

from .core import filter_paths


def _walk_paths(root: str) -> Iterator[str]:
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root)
            yield rel.replace(os.sep, "/")


def _stdin_paths(stream: IO[str]) -> Iterator[str]:
    for line in stream:
        line = line.rstrip("\r\n")
        if line:
            yield line


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="globsieve",
        description="List files under ROOT that match --include and not --exclude glob patterns.",
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=None,
        help="directory to walk (default: current directory; unused with --from-stdin)",
    )
    parser.add_argument(
        "-i",
        "--include",
        action="append",
        default=[],
        help="glob pattern to include (repeatable, default: **)",
    )
    parser.add_argument(
        "-x",
        "--exclude",
        action="append",
        default=[],
        help="glob pattern to exclude (repeatable)",
    )
    parser.add_argument(
        "--from-stdin",
        action="store_true",
        help="read newline-separated paths from stdin instead of walking a directory",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    include = args.include or ["**"]
    if args.from_stdin:
        if args.root is not None:
            parser.error("ROOT is not used with --from-stdin")
        paths = list(_stdin_paths(sys.stdin))
    else:
        paths = list(_walk_paths(args.root or "."))
    for path in filter_paths(paths, include, args.exclude):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
