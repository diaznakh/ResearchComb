"""Test that the artifact checks reject unsupported verification and short drafts."""

import unittest

from check_results import body_word_count, linked_sources_present, validate_record


class EvidenceChecks(unittest.TestCase):
    def record(self):
        return {
            "question": "Test a claim",
            "sources": [{"id": "S1", "title": "Fixture", "authors": [], "year": None,
                         "url": "fixture.md", "doi": None, "access": "excerpt",
                         "identity_status": "provided", "link_status": "not_checked"}],
            "claims": [{"id": "C1", "text": "Claim", "status": "supported",
                        "evidence": [{"source_id": "S1", "location": "section 1", "observation": "Evidence"}],
                        "note": "Checked against the supplied excerpt"}],
        }

    def test_supported_claim_requires_evidence(self):
        record = self.record()
        validate_record(record)
        record["claims"][0]["evidence"] = []
        with self.assertRaises(ValueError):
            validate_record(record)

    def test_handoff_cannot_reference_a_missing_source(self):
        record = self.record()
        record["claims"][0]["evidence"][0]["source_id"] = "S9"
        with self.assertRaises(ValueError):
            validate_record(record)

    def test_count_excludes_numbered_bibliography(self):
        text = "# Report\nOne two three.\n## 8. References\n" + "reference " * 7000
        self.assertEqual(body_word_count(text), 5)
        self.assertLess(body_word_count(text), 6000)

    def test_canonical_publisher_link_is_a_valid_reference(self):
        record = {"sources": [{"doi": "10.1038/s41467-018-03793-w", "url": "https://www.nature.com/articles/s41467-018-03793-w"}]}
        self.assertTrue(linked_sources_present(record, "[Paper](https://www.nature.com/articles/s41467-018-03793-w)"))
        self.assertFalse(linked_sources_present(record, "Paper with no link"))
        record["sources"][0]["url"] = None
        self.assertFalse(linked_sources_present(record, "None of the sources is linked"))


if __name__ == "__main__":
    unittest.main()
