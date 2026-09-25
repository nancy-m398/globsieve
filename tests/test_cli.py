import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

from globsieve.cli import main


class FromStdinTests(unittest.TestCase):
    def _run(self, argv, stdin_text):
        out = io.StringIO()
        with mock.patch("sys.stdin", io.StringIO(stdin_text)):
            with redirect_stdout(out):
                code = main(argv)
        return code, out.getvalue().splitlines()

    def test_filters_piped_paths(self):
        stdin_text = "src/app.py\nsrc/app_test.py\nbuild/app.py\nREADME.md\n"
        code, lines = self._run(
            ["--from-stdin", "--include", "**/*.py", "--exclude", "**/*_test.py"],
            stdin_text,
        )
        self.assertEqual(code, 0)
        self.assertEqual(lines, ["src/app.py"])

    def test_blank_lines_are_ignored(self):
        code, lines = self._run(["--from-stdin"], "a.py\n\n\nb.py\n")
        self.assertEqual(code, 0)
        self.assertEqual(lines, ["a.py", "b.py"])

    def test_root_argument_conflicts_with_from_stdin(self):
        with self.assertRaises(SystemExit):
            self._run(["some/dir", "--from-stdin"], "a.py\n")


class WalkTests(unittest.TestCase):
    def test_walks_directory_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "src"))
            os.makedirs(os.path.join(tmp, "build"))
            open(os.path.join(tmp, "src", "app.py"), "w").close()
            open(os.path.join(tmp, "build", "app.py"), "w").close()
            open(os.path.join(tmp, "README.md"), "w").close()

            out = io.StringIO()
            with redirect_stdout(out):
                code = main([tmp, "--include", "**/*.py", "--exclude", "build/**"])

            self.assertEqual(code, 0)
            self.assertEqual(out.getvalue().splitlines(), ["src/app.py"])


if __name__ == "__main__":
    unittest.main()
