"""Glob matching over plain path strings.

Nothing in this module touches the filesystem. A "path" is just a string
using "/" as the separator, so the matching rules can be tested with
ordinary lists instead of temp directories.
"""

import re
from typing import Iterable, List, Sequence


def translate(pattern: str) -> str:
    """Convert a glob pattern into an equivalent regular expression pattern.

    Supported syntax:
      *     any run of characters except "/"
      **    any run of characters including "/" (zero or more path segments)
      ?     a single character except "/"
      [abc] one character from the set
      [!abc] one character not in the set
    """
    i, n = 0, len(pattern)
    out: List[str] = []
    while i < n:
        c = pattern[i]
        i += 1
        if c == "*":
            if i < n and pattern[i] == "*":
                i += 1
                if i < n and pattern[i] == "/":
                    i += 1
                    # "**/" may also match zero segments, so "a/**/b" matches "a/b"
                    out.append("(?:.*/)?")
                else:
                    out.append(".*")
            else:
                out.append("[^/]*")
        elif c == "?":
            out.append("[^/]")
        elif c == "[":
            j = i
            if j < n and pattern[j] == "!":
                j += 1
            if j < n and pattern[j] == "]":
                j += 1
            while j < n and pattern[j] != "]":
                j += 1
            if j >= n:
                # no closing bracket found, treat "[" as a literal
                out.append(re.escape(c))
            else:
                body = pattern[i:j]
                if body.startswith("!"):
                    body = "^" + body[1:]
                out.append("[" + body + "]")
                i = j + 1
        else:
            out.append(re.escape(c))
    return "".join(out)


def match(path: str, pattern: str) -> bool:
    """Return True if path matches the glob pattern."""
    return re.fullmatch(translate(pattern), path) is not None


def filter_paths(
    paths: Iterable[str],
    include: Sequence[str],
    exclude: Sequence[str] = (),
) -> List[str]:
    """Keep paths that match at least one include pattern and no exclude pattern.

    Order of the input is preserved.
    """
    result = []
    for path in paths:
        if not any(match(path, pattern) for pattern in include):
            continue
        if any(match(path, pattern) for pattern in exclude):
            continue
        result.append(path)
    return result
