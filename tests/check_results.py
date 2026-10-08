"""Check observable outcomes of the four native-host workflow regression cases."""

import json
import re
import sys
from pathlib import Path


STATUSES = {"supported", "qualified", "contradicted", "unsupported", "unverified"}
DOIS = {
    "10.1038/s41467-018-03793-w",
    "10.1021/acscatal.2c01374",
    "10.3390/catal16020163",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text())


def body_word_count(text):
    # The cases explicitly use whitespace-separated words before the bibliography.
    body = re.split(
        r"(?im)^#{1,6}\s+(?:\d+[.)]?\s+)?(?:references|bibliography)\b.*$",
        text,
        maxsplit=1,
    )[0]
    return len(body.split())


def validate_record(record):
    require(isinstance(record.get("question"), str), "Missing research question")
    sources, claims = record["sources"], record["claims"]
    source_ids = [source["id"] for source in sources]
    require(len(set(source_ids)) == len(source_ids), "Duplicate source IDs")
    claim_ids = [claim["id"] for claim in claims]
    require(len(set(claim_ids)) == len(claim_ids), "Duplicate claim IDs")
    for source in sources:
        require(
            {"id", "title", "authors", "year", "url", "doi", "access", "identity_status", "link_status"}
            <= source.keys(),
            f"Incomplete source: {source.get('id')}",
        )
        require(source["authors"] is None or isinstance(source["authors"], list), "Authors must be a list or unknown")
        require(source["access"] in {"full_text", "abstract", "excerpt", "metadata", "code", "run"}, "Invalid source access")
        require(source["identity_status"] in {"verified", "provided", "unverified"}, "Invalid identity status")
        require(source["link_status"] in {"accessible", "inaccessible", "broken", "not_checked"}, "Invalid link status")
    for claim in claims:
        require({"id", "text", "status", "evidence", "note"} <= claim.keys(), f"Incomplete claim: {claim.get('id')}")
        require(claim["status"] in STATUSES, "Invalid claim status")
        if claim["status"] in {"supported", "qualified", "contradicted"}:
            require(bool(claim["evidence"]), f"Assessed claim lacks evidence: {claim['id']}")
        for evidence in claim["evidence"]:
            require(evidence["source_id"] in source_ids, "Evidence refers to an unknown source")
            require(bool(evidence["location"]) and bool(evidence["observation"]), "Evidence lacks a location or observation")
    return {claim["id"]: claim for claim in claims}


def linked_sources_present(record, report):
    text = report.lower()
    return all(
        source["doi"].lower() in text
        or (isinstance(source.get("url"), str) and source["url"].lower() in text)
        for source in record["sources"] if source.get("doi") in DOIS
    )


def check_case(root, case):
    directory = root / case
    record = read_json(directory / "evidence.json")
    claims = validate_record(record)
    report = (directory / ("manuscript.md" if case == "manuscript" else "report.md")).read_text()
    require(bool(report.strip()), "Missing workflow report")
    if case == "trace":
        fixture = Path(__file__).parent / "fixtures" / "code-study"
        for filename in ("paper.md", "config.json", "evaluate.py"):
            require((directory / "study" / filename).read_bytes() == (fixture / filename).read_bytes(), "Audit changed a study input")
        for claim_id in ("T1", "T2", "T3"):
            require(claims[claim_id]["status"] == "contradicted", f"Missed code mismatch: {claim_id}")
        require(claims["T4"]["status"] in {"supported", "qualified"}, "Incorrect seed finding")
        require(any(source["access"] == "code" for source in record["sources"]), "No inspected code recorded")
    elif case == "check":
        fixture = Path(__file__).parent / "fixtures" / "citation-draft.md"
        require((directory / "draft.md").read_bytes() == fixture.read_bytes(), "Citation check changed the input draft")
        require(claims["C1"]["status"] == "contradicted", "Missed catalyst attribution error")
        require(claims["C2"]["status"] == "contradicted", "Missed bibliographic identity error")
        require(claims["C3"]["status"] in {"unsupported", "unverified"}, "Invented support for emission claim")
        require(claims["C4"]["status"] == "supported", "Rejected the supported temperature claim")
        unknown = [source for source in record["sources"] if "researchcomb.nonexistent-test" in str(source.get("url"))]
        require(len(unknown) == 1, "Missing unresolved supplied citation")
        require(unknown[0]["identity_status"] != "verified" and unknown[0]["link_status"] != "accessible", "Unresolved citation was falsely verified")
    elif case == "survey":
        doi_set = {str(source.get("doi")).lower() for source in record["sources"]}
        require(DOIS <= doi_set, "Survey omitted a requested source")
        require(700 <= body_word_count(report) <= 1000, "Survey did not meet requested length")
        require(bool(claims), "Survey recorded no claims")
        require(linked_sources_present(record, report), "Survey lacks canonical source links")
    elif case == "manuscript":
        count = body_word_count(report)
        require(6000 <= count <= 6500, f"Manuscript has {count} body words, expected 6000–6500")
        completion = read_json(directory / "completion.json")
        require(completion["status"] == "complete", "Manuscript reported partial completion")
        require(completion["measured_word_count"] == count, "Claimed word count differs from the saved artifact")
        require(completion["rendered_page_count"] is None, "Unrendered pages were presented as measured")
        original = read_json(root / "survey" / "evidence.json")
        new_sources = {source["id"]: source for source in record["sources"]}
        for source in original["sources"]:
            require(source["id"] in new_sources, "Lost a source ID during handoff")
            require(new_sources[source["id"]]["doi"] == source["doi"], "Changed a source identity during handoff")
        require(set(claims) >= {claim["id"] for claim in original["claims"]}, "Lost claim IDs during handoff")
        require(linked_sources_present(record, report), "Manuscript lacks canonical source links")
    else:
        raise ValueError(f"Unknown case: {case}")
    return f"{case}: passed ({len(record['sources'])} sources, {len(claims)} claims, {body_word_count(report)} body words)"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python3 tests/check_results.py OUTPUT_ROOT [survey check trace manuscript]")
    try:
        for name in sys.argv[2:] or ["survey", "check", "trace", "manuscript"]:
            print(check_case(Path(sys.argv[1]), name))
    except (ValueError, KeyError, OSError, TypeError) as error:
        sys.exit(f"FAILED: {error}")
