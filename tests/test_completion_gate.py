"""Regression checks for the installed, offline completion gate."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "skills/researchcomb/scripts/check_completion.py"
SOURCES = {
    "Google Scholar": "site:scholar.google.com",
    "ResearchGate": "site:researchgate.net/publication",
    "Crossref": "site:search.crossref.org",
    "OpenAlex": "site:openalex.org",
    "Semantic Scholar": "site:semanticscholar.org/paper",
}


class CompletionGateTests(unittest.TestCase):
    def run_gate(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True)

    def test_short_manuscript_fails_and_revised_body_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manuscript.md"
            path.write_text("one two three\n## References\n" + "reference " * 100)
            result = self.run_gate("manuscript", path, 5, 7)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("3 body words", result.stderr)
            path.write_text("one two three four five six\n## References\n" + "reference " * 100)
            result = self.run_gate("manuscript", path, 5, 7)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("6 body words", result.stdout)
            self.assertNotEqual(self.run_gate("manuscript", path, 7, 9).returncode, 0)
            self.assertEqual(self.run_gate("manuscript", path, 6, 6).returncode, 0)

    def test_missing_sources_and_fallback_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            searches = [
                {"source": name, "direct": {"url": "https://" + suffix.removeprefix("site:").split("/", 1)[0] + "/search", "outcome": "searched"}}
                for name, suffix in SOURCES.items()
            ]
            papers = [{"id": f"S{i}", "url": f"https://example.org/paper/{i}"} for i in range(6)]
            path.write_text(json.dumps({"searches": searches[:2], "sources": papers}))
            self.assertIn("missing search attempt", self.run_gate("search", path).stderr)
            searches[0]["direct"]["outcome"] = "inaccessible"
            path.write_text(json.dumps({"searches": searches, "sources": papers}))
            self.assertIn("fallback query", self.run_gate("search", path).stderr)
            searches[0]["fallback"] = {"query": "topic " + SOURCES["Google Scholar"], "outcome": "no results"}
            path.write_text(json.dumps({"searches": searches, "sources": []}))
            self.assertIn("only 0 source(s)", self.run_gate("search", path).stderr)
            path.write_text(json.dumps({"searches": searches, "sources": papers}))
            result = self.run_gate("search", path)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("6 discovered paper(s)", result.stdout)
            searches[0]["direct"]["url"] = "https://example.org/search"
            path.write_text(json.dumps({"searches": searches, "sources": papers}))
            self.assertIn("direct URL must belong", self.run_gate("search", path).stderr)


if __name__ == "__main__":
    unittest.main()
