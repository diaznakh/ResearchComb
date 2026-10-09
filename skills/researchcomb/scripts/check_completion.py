"""Check observable ResearchComb search coverage and manuscript length."""

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit


BROAD_SOURCES = {
    "Google Scholar": "site:scholar.google.com",
    "ResearchGate": "site:researchgate.net/publication",
    "Crossref": "site:search.crossref.org",
    "OpenAlex": "site:openalex.org",
    "Semantic Scholar": "site:semanticscholar.org/paper",
}


def check_search(path):
    record = json.loads(path.read_text())
    if not isinstance(record, dict):
        raise ValueError("evidence record must be an object")
    searches = record.get("searches", [])
    if not isinstance(searches, list) or not all(isinstance(entry, dict) and isinstance(entry.get("source"), str) for entry in searches):
        raise ValueError("searches must be a list of source entries")
    by_source = {entry["source"]: entry for entry in searches}
    if len(by_source) != len(searches):
        raise ValueError("duplicate search source")
    for source, suffix in BROAD_SOURCES.items():
        entry = by_source.get(source)
        if not entry:
            raise ValueError(f"missing search attempt: {source}")
        direct = entry.get("direct", {})
        if not isinstance(direct, dict) or direct.get("outcome") not in {"searched", "inaccessible"} or not isinstance(direct.get("url"), str) or not direct["url"].strip():
            raise ValueError(f"{source}: record the attempted URL and direct outcome")
        url = urlsplit(direct["url"])
        domain = suffix.removeprefix("site:").split("/", 1)[0]
        if url.scheme not in {"http", "https"} or not url.hostname or not (url.hostname == domain or url.hostname.endswith("." + domain)):
            raise ValueError(f"{source}: direct URL must belong to {domain}")
        if direct["outcome"] == "inaccessible":
            fallback = entry.get("fallback", {})
            if not isinstance(fallback, dict) or not isinstance(fallback.get("query"), str) or suffix not in fallback["query"] or not isinstance(fallback.get("outcome"), str) or not fallback["outcome"].strip():
                raise ValueError(f"{source}: record a separate {suffix} fallback query and outcome")
    sources = record.get("sources", [])
    if not isinstance(sources, list):
        raise ValueError("'sources' must be a list of discovered papers")
    if len(sources) < 5:
        raise ValueError(
            f"only {len(sources)} source(s) recorded in 'sources'; "
            "a live survey must record at least 5 discovered papers before drafting"
        )
    return (
        f"PASS: recorded direct attempts for {len(BROAD_SOURCES)} broad sources, "
        f"fallbacks where needed, and {len(sources)} discovered paper(s)"
    )


def check_manuscript(path, minimum, maximum):
    if minimum < 1 or maximum < minimum:
        raise ValueError("invalid word range")
    body = re.split(
        r"(?im)^#{1,6}\s+(?:\d+[.)]?\s+)?(?:references|bibliography)\b.*$",
        path.read_text(),
        maxsplit=1,
    )[0]
    count = len(body.split())
    if not minimum <= count <= maximum:
        raise ValueError(f"{count} body words; requested {minimum}–{maximum}. Continue drafting or report partial with a concrete evidence/access gap")
    return f"PASS: {count} body words within {minimum}–{maximum}"


if __name__ == "__main__":
    try:
        if len(sys.argv) == 3 and sys.argv[1] == "search":
            print(check_search(Path(sys.argv[2])))
        elif len(sys.argv) == 5 and sys.argv[1] == "manuscript":
            print(check_manuscript(Path(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])))
        else:
            raise ValueError("usage: check_completion.py search evidence.json | manuscript manuscript.md MIN MAX")
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        sys.exit(f"FAIL: {error}")
