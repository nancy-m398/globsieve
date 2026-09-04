# globsieve

Most tools that need "which files match these glob patterns" logic end up
tangling the matching rules with a real directory walk. That makes the rules
annoying to test: you need a temp directory, real files on disk, and cleanup,
just to check that `**/*.py` excludes `build/`.

globsieve splits the two apart. The matching logic operates on plain path
strings and returns plain lists, no filesystem involved, so it can be tested
with ordinary Python lists. The CLI is a thin wrapper that does the actual
`os.walk` and hands the results to the library.

## Library

```python
from globsieve import filter_paths, match

match("src/app.py", "**/*.py")          # True
match("src/app.py", "*.py")             # False, * doesn't cross "/"

paths = [
    "src/app.py",
    "src/app_test.py",
    "build/app.py",
    "README.md",
]

filter_paths(paths, include=["**/*.py"], exclude=["**/*_test.py", "build/**"])
# ["src/app.py"]
```

`filter_paths` keeps a path if it matches at least one `include` pattern and
none of the `exclude` patterns, preserving the input order.

## Pattern syntax

| Pattern | Meaning |
|---|---|
| `*` | any characters except `/` |
| `**` | any characters including `/` (zero or more path segments) |
| `?` | one character except `/` |
| `[abc]` | one character from the set |
| `[!abc]` | one character not in the set |

Known limitation: a trailing `**` (as in `build/**`) matches everything
*under* `build/` but not `build` itself. Use `build` and `build/**` together
if you need both.

## CLI

```
$ globsieve . --include '**/*.py' --exclude '**/*_test.py'
src/app.py
```

`--include` and `--exclude` can be given more than once. With no `--include`,
everything under `root` is a candidate.

## Install

No dependencies beyond the standard library.

```
$ pip install -e .
```
