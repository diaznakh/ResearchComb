"""Check observable outcomes for every ResearchComb workflow and general routing."""

import json
import math
import re
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/researchcomb/scripts"))
from check_completion import body_word_count


STATUSES = {"supported", "qualified", "contradicted", "unsupported", "unverified"}
DOIS = {
    "10.1038/s41467-018-03793-w",
    "10.1021/acscatal.2c01374",
    "10.3390/catal16020163",
}
CASES = ["survey", "check", "trace", "manuscript", "align", "investigate", "digest", "blueprint", "critique", "cycle", "rerun", "paper", "routing"]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text())


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
    if case == "routing":
        result = read_json(directory / "result.json")
        normalize = lambda value: value.rsplit(":", 1)[-1].lstrip("/$")
        expected = {path.parent.name for path in (Path(__file__).parent.parent / "skills").glob("*/SKILL.md")}
        require({normalize(name) for name in result["commands"]} == expected, "General skill did not list the installed workflows")
        for request, skill in {"citations": "comb-check", "comparison": "comb-align", "reproduction": "comb-rerun", "writing": "comb-manuscript"}.items():
            require(normalize(result["routes"][request]) == skill, f"Incorrect routing for {request}")
        return f"routing: passed ({len(expected)} skills discovered and four requests routed)"
    record = read_json(directory / "evidence.json")
    claims = validate_record(record)
    report = (directory / ("manuscript.md" if case == "manuscript" else "report.md")).read_text()
    require(bool(report.strip()), "Missing workflow report")
    if case in {"align", "investigate", "digest", "blueprint", "critique"}:
        source_map = {source["id"]: source for source in record["sources"]}
        for source_id in (("S-B",) if case == "digest" else ("S-A", "S-B")):
            require(source_id in source_map, "Lost supplied source ID")
            require(source_map[source_id]["doi"] is None, "Invented a DOI for a synthetic source")
        result = read_json(directory / "result.json")
        if case == "align":
            require(result["direct_ranking_supported"] is False, "Ranked incompatible study accuracies directly")
            studies = {study["source_id"]: study for study in result["studies"]}
            for source_id, size, fraction, accuracy, baseline in [("S-A", 100, 0.5, 0.9, 0.5), ("S-B", 20, 0.95, 0.95, 0.95)]:
                actual = studies[source_id]
                require(actual["sample_size"] == size, "Wrong study sample size")
                require(all(math.isclose(actual[key], value) for key, value in [("positive_fraction", fraction), ("accuracy", accuracy), ("baseline_accuracy", baseline)]), "Changed study conditions or metrics")
        elif case == "investigate":
            require(result["direct_ranking_supported"] is False, "Investigation overgeneralized performance")
            require(result["preferred_feasible_source_id"] == "S-A", "Ignored the CPU-only constraint")
            require(result["search_performed"] is False, "Claimed a live search for a supplied-only corpus")
        elif case == "digest":
            require(result["sample_size"] == 20, "Digest changed sample size")
            require(all(math.isclose(result[key], 0.95) for key in ["positive_fraction", "accuracy", "baseline_accuracy"]), "Digest lost class balance or baseline")
            require(result["access"] == "excerpt" and result["generalization_verified"] is False, "Digest overstated source access or generalization")
        elif case == "blueprint":
            require(result["recommended_source_id"] == "S-A" and result["execution_performed"] is False, "Blueprint ignored resource limits or claimed execution")
            candidates = {candidate["source_id"]: candidate for candidate in result["candidates"]}
            require(candidates["S-A"]["feasible"] is True and candidates["S-B"]["feasible"] is False, "Blueprint feasibility ranking is incorrect")
            require(all(candidate["measured_here"] is False for candidate in candidates.values()), "Blueprint invented locally measured performance")
        else:
            require((directory / "inputs/draft.md").read_bytes() == (Path(__file__).parent / "fixtures/workflows/draft.md").read_bytes(), "Critique edited the review-only draft")
            findings = {finding["claim_id"]: finding for finding in result["findings"]}
            for claim_id in ("D1", "D2"):
                require(findings[claim_id]["severity"] in {"critical", "major"}, "Critique missed a material methodological error")
                require(bool(findings[claim_id]["evidence"]) and bool(findings[claim_id]["revision"]), "Critique omitted evidence or an actionable revision")
    elif case in {"cycle", "rerun"}:
        fixture = Path(__file__).parent / "fixtures/threshold-benchmark"
        for filename in ("benchmark.py", "data.json", "config.json", "claim.md"):
            require((directory / "benchmark" / filename).read_bytes() == (fixture / filename).read_bytes(), "Experiment changed a fixed input")
        result = read_json(directory / "result.json")
        require(result["execution_performed"] is True, "Execution workflow returned an unexecuted plan")
        require(any(source["access"] == "run" for source in record["sources"]), "No measured result evidence recorded")
        if case == "cycle":
            baseline = read_json(directory / "baseline.json")
            first, second = read_json(directory / "trial-1.json"), read_json(directory / "trial-4.json")
            require(math.isclose(baseline["accuracy"], 5 / 6) and first["accuracy"] == 1 and second["accuracy"] == 0.5, "Incorrect measured trial results")
            require(result["budget_used"] == 2 and len(result["trials"]) == 2, "Experiment exceeded its trial budget")
            require([trial["threshold"] for trial in result["trials"]] == [1, 4], "Changed the permitted hypotheses")
            require([trial["decision"] for trial in result["trials"]] == ["kept", "rejected"], "Kept a regression or rejected an improvement")
            require(result["best"]["threshold"] == 1 and result["best"]["accuracy"] == 1, "Wrong best measured configuration")
            require(read_json(directory / "best_config.json")["threshold"] == 1, "Did not save the best configuration")
        else:
            observed = read_json(directory / "observed.json")
            require(math.isclose(observed["accuracy"], 5 / 6) and math.isclose(result["observed_accuracy"], observed["accuracy"]), "Reproduction did not report the measured result")
            require(result["expected_accuracy"] == 0.95 and result["tolerance"] == 0.01, "Changed the reproduction target")
            require(result["status"] == "not_reproduced", "Falsely claimed reproduction")
    elif case == "trace":
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
    elif case == "paper":
        report = (directory / "paper.md").read_text()
        require(bool(report.strip()), "Missing paper.md")
        checks = (directory / "checks.md").read_text()
        require(bool(checks.strip()), "Missing checks.md")
        source_map = {source["id"]: source for source in record["sources"]}
        for source_id in ("S-A", "S-B"):
            require(source_id in source_map, "Lost supplied source ID")
    else:
        raise ValueError(f"Unknown case: {case}")
    return f"{case}: passed ({len(record['sources'])} sources, {len(claims)} claims, {body_word_count(report)} body words)"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python3 tests/check_results.py OUTPUT_ROOT [case ...]")
    try:
        for name in sys.argv[2:] or CASES:
            print(check_case(Path(sys.argv[1]), name))
    except (ValueError, KeyError, OSError, TypeError) as error:
        sys.exit(f"FAILED: {error}")
