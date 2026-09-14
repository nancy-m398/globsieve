import unittest

from globsieve.core import filter_paths, match, translate


class TranslateTests(unittest.TestCase):
    def test_literal_characters_are_escaped(self):
        # "." must not become "any character" in the resulting regex
        self.assertEqual(translate("a.b"), r"a\.b")

    def test_single_star_excludes_slash(self):
        self.assertEqual(translate("*.py"), r"[^/]*\.py")

    def test_double_star_matches_across_slash(self):
        self.assertEqual(translate("a**b"), r"a.*b")

    def test_trailing_double_star_slash_allows_zero_segments(self):
        # "a/**/b" should match "a/b" as well as "a/x/b"
        self.assertEqual(translate("a/**/b"), r"a/(?:.*/)?b")

    def test_trailing_double_star_matches_directory_itself(self):
        # "build/**" should match "build" as well as anything under it
        self.assertEqual(translate("build/**"), r"build(?:/.*)?")

    def test_bare_double_star_is_unaffected(self):
        self.assertEqual(translate("**"), r".*")

    def test_question_mark_excludes_slash(self):
        self.assertEqual(translate("a?b"), r"a[^/]b")

    def test_character_class(self):
        self.assertEqual(translate("[abc]"), r"[abc]")

    def test_negated_character_class(self):
        self.assertEqual(translate("[!abc]"), r"[^abc]")

    def test_unclosed_bracket_is_treated_as_literal(self):
        self.assertEqual(translate("[abc"), r"\[abc")


class MatchTests(unittest.TestCase):
    def test_star_does_not_cross_slash(self):
        self.assertFalse(match("src/app.py", "*.py"))
        self.assertTrue(match("app.py", "*.py"))

    def test_double_star_crosses_slash(self):
        self.assertTrue(match("src/app.py", "**/*.py"))
        self.assertTrue(match("app.py", "**/*.py"))

    def test_double_star_matches_middle_segment_zero_or_more_times(self):
        self.assertTrue(match("a/b", "a/**/b"))
        self.assertTrue(match("a/x/y/b", "a/**/b"))

    def test_trailing_double_star_matches_the_directory_itself(self):
        self.assertTrue(match("build", "build/**"))
        self.assertTrue(match("build/app.py", "build/**"))
        self.assertTrue(match("build/sub/app.py", "build/**"))
        self.assertFalse(match("buildx", "build/**"))

    def test_question_mark_excludes_slash(self):
        self.assertFalse(match("a/b", "a?b"))
        self.assertTrue(match("axb", "a?b"))

    def test_character_class_matching(self):
        self.assertTrue(match("cat.py", "[bc]at.py"))
        self.assertFalse(match("hat.py", "[bc]at.py"))

    def test_negated_character_class_matching(self):
        self.assertFalse(match("cat.py", "[!bc]at.py"))
        self.assertTrue(match("hat.py", "[!bc]at.py"))

    def test_full_match_required(self):
        self.assertFalse(match("src/app.py.bak", "*.py"))
        self.assertFalse(match("app.py", "app"))


class FilterPathsTests(unittest.TestCase):
    def setUp(self):
        self.paths = [
            "src/app.py",
            "src/app_test.py",
            "build/app.py",
            "README.md",
        ]

    def test_keeps_order_of_input(self):
        result = filter_paths(self.paths, include=["**"])
        self.assertEqual(result, self.paths)

    def test_include_and_exclude_combine(self):
        result = filter_paths(
            self.paths,
            include=["**/*.py"],
            exclude=["**/*_test.py", "build/**"],
        )
        self.assertEqual(result, ["src/app.py"])

    def test_multiple_include_patterns_are_unioned(self):
        result = filter_paths(self.paths, include=["*.md", "build/**"])
        self.assertEqual(result, ["build/app.py", "README.md"])

    def test_empty_include_keeps_nothing(self):
        self.assertEqual(filter_paths(self.paths, include=[]), [])

    def test_no_exclude_given(self):
        result = filter_paths(self.paths, include=["**/*.py"])
        self.assertEqual(result, ["src/app.py", "src/app_test.py", "build/app.py"])

    def test_exclude_removes_everything(self):
        result = filter_paths(self.paths, include=["**"], exclude=["**"])
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
