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
            papers = [{"id": f"S{i}", "title": f"Paper {i}", "url": f"https://example.org/paper/{i}"} for i in range(6)]
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

    def test_paper_search_requires_all_indexes_and_screened_trails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            names = ["PubMed", "Europe PMC", "alphaXiv", "arXiv", "bioRxiv", "medRxiv"]
            suffixes = ["site:pubmed.ncbi.nlm.nih.gov", "site:europepmc.org", "site:alphaxiv.org", "site:arxiv.org", "site:biorxiv.org", "site:medrxiv.org"]
            searches = [
                {"source": name, "direct": {"outcome": "unavailable", "reason": "No direct browser"},
                 "fallback": {"query": "topic " + suffix, "outcome": "no results"}}
                for name, suffix in list(SOURCES.items()) + list(zip(names, suffixes))
            ]
            record = {
                "searches": searches,
                "sources": [{"id": f"S{i}", "title": f"Paper {i}", "url": f"https://example.org/paper/{i}"} for i in range(5)],
                "citation_trails": [{"source_id": f"S{i}", "kind": kind, "outcome": "screened"}
                                    for i in range(5) for kind in ("references", "cited_by")],
                "trail_leads": [{"title": "Paper 1", "status": "included", "source_id": "S1"}],
                "search_rounds": [{"new_relevant": 1}, {"new_relevant": 0}],
            }
            def run():
                path.write_text(json.dumps(record))
                return self.run_gate("paper-search", path)
            self.assertEqual(run().returncode, 0, run().stderr)
            record["searches"] = searches[:-1]
            self.assertIn("missing search attempt: medRxiv", run().stderr)
            record["searches"] = searches
            record["citation_trails"].pop()
            self.assertIn("backward references", run().stderr)
            record["citation_trails"].append({"source_id": "S4", "kind": "related", "outcome": "screened"})
            record["trail_leads"][0]["status"] = "pending"
            self.assertIn("screening outcome", run().stderr)
            record["trail_leads"][0]["status"] = "included"
            record["search_rounds"].pop()
            self.assertIn("final search round", run().stderr)

    def test_bibliography_aliases_and_substantive_sources_heading(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "paper.md"
            for heading in ("## Sources", "## 8. Sources: ##", "## Bibliography", "## References"):
                with self.subTest(heading=heading):
                    path.write_text("one two three\n" + heading + "\n" + "reference " * 100)
                    self.assertIn("3 body words", self.run_gate("manuscript", path, 100, 110).stderr)
            text = "one two three\n## Sources of uncertainty\nmore evidence"
            path.write_text(text)
            self.assertEqual(self.run_gate("manuscript", path, len(text.split()), len(text.split())).returncode, 0)

    def test_distinct_paper_validation_and_unavailable_browser(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            searches = [
                {"source": name, "direct": {"outcome": "unavailable", "reason": "Host only offers web search"},
                 "fallback": {"query": "topic " + suffix, "outcome": "results found"}}
                for name, suffix in SOURCES.items()
            ]
            papers = [{"id": f"S{i}", "title": f"Paper {i}", "url": f"https://example.org/paper/{i}"} for i in range(5)]
            def run(entries=papers):
                path.write_text(json.dumps({"searches": searches, "sources": entries}))
                return self.run_gate("search", path)
            result = run()
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("0 direct attempts", result.stdout)
            for entries in ([{}] * 5, [papers[0]] * 5, papers[:4]):
                self.assertNotEqual(run(entries).returncode, 0)
            for replacement in (
                {"url": "http://EXAMPLE.org/paper/0#section"},
                {"id": "S0"}, {"title": " "}, {"url": None}, {"url": "not a URL"}, {"doi": []},
            ):
                with self.subTest(replacement=replacement):
                    entries = [dict(paper) for paper in papers]
                    entries[1].update(replacement)
                    self.assertNotEqual(run(entries).returncode, 0)
            for unsafe_url in (
                "http://127.0.0.1:8080/private", "http://127.1/private", "http://169.254.169.254/latest/meta-data/",
                "http://[::1]/private", "http://localhost/private", "http://papers.local/private",
                "http://records.home.arpa/private", "http://intranet.internal/private",
            ):
                with self.subTest(unsafe_url=unsafe_url):
                    entries = [dict(paper) for paper in papers]
                    entries[1]["url"] = unsafe_url
                    self.assertIn("public hostname", run(entries).stderr)
            for alias in ("https://doi.org/10.1234/ABC", "doi:10.1234/abc"):
                entries = [dict(paper) for paper in papers]
                entries[0]["doi"] = "10.1234/abc"
                entries[1]["doi"] = alias
                self.assertIn("duplicate paper", run(entries).stderr)
            entries[1].pop("doi")
            entries[1]["url"] = "https://dx.doi.org/10.1234/ABC"
            self.assertIn("duplicate paper", run(entries).stderr)
            for paper in entries:
                paper["url"] = None
                paper["doi"] = "10.1234/" + paper["id"]
            self.assertEqual(run(entries).returncode, 0)
            searches[0]["direct"].pop("reason")
            self.assertIn("needs a reason", run().stderr)
            searches[0]["direct"]["reason"] = "No direct browser"
            searches[0]["direct"]["url"] = "https://scholar.google.com/"
            self.assertIn("no attempted URL", run().stderr)
            searches[0]["direct"].pop("url")
            searches[0].pop("fallback")
            self.assertIn("fallback query", run().stderr)


if __name__ == "__main__":
    unittest.main()
