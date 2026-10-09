"""Check observable ResearchComb search coverage and manuscript length."""

import json
import ipaddress
import re
import socket
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


BROAD_SOURCES = {
    "Google Scholar": "site:scholar.google.com",
    "ResearchGate": "site:researchgate.net/publication",
    "Crossref": "site:search.crossref.org",
    "OpenAlex": "site:openalex.org",
    "Semantic Scholar": "site:semanticscholar.org/paper",
}
PAPER_SOURCES = {
    **BROAD_SOURCES,
    "PubMed": "site:pubmed.ncbi.nlm.nih.gov",
    "Europe PMC": "site:europepmc.org",
    "alphaXiv": "site:alphaxiv.org",
    "arXiv": "site:arxiv.org",
    "bioRxiv": "site:biorxiv.org",
    "medRxiv": "site:medrxiv.org",
}


def check_search(path, paper_mode=False):
    record = json.loads(path.read_text())
    if not isinstance(record, dict):
        raise ValueError("evidence record must be an object")
    searches = record.get("searches", [])
    if not isinstance(searches, list) or not all(isinstance(entry, dict) and isinstance(entry.get("source"), str) for entry in searches):
        raise ValueError("searches must be a list of source entries")
    by_source = {entry["source"]: entry for entry in searches}
    if len(by_source) != len(searches):
        raise ValueError("duplicate search source")
    unavailable = 0
    required_sources = PAPER_SOURCES if paper_mode else BROAD_SOURCES
    for source, suffix in required_sources.items():
        entry = by_source.get(source)
        if not entry:
            raise ValueError(f"missing search attempt: {source}")
        direct = entry.get("direct", {})
        if not isinstance(direct, dict) or direct.get("outcome") not in {"searched", "inaccessible", "unavailable"}:
            raise ValueError(f"{source}: record a valid direct outcome")
        if direct["outcome"] == "unavailable":
            if not isinstance(direct.get("reason"), str) or not direct["reason"].strip() or direct.get("url") is not None:
                raise ValueError(f"{source}: unavailable browsing needs a reason and no attempted URL")
            unavailable += 1
        else:
            if not isinstance(direct.get("url"), str) or not direct["url"].strip():
                raise ValueError(f"{source}: record the attempted URL")
            url = urlsplit(direct["url"])
            domain = suffix.removeprefix("site:").split("/", 1)[0]
            if url.scheme not in {"http", "https"} or not url.hostname or not (url.hostname == domain or url.hostname.endswith("." + domain)):
                raise ValueError(f"{source}: direct URL must belong to {domain}")
        if direct["outcome"] in {"inaccessible", "unavailable"}:
            fallback = entry.get("fallback", {})
            if not isinstance(fallback, dict) or not isinstance(fallback.get("query"), str) or suffix not in fallback["query"] or not isinstance(fallback.get("outcome"), str) or not fallback["outcome"].strip():
                raise ValueError(f"{source}: record a separate {suffix} fallback query and outcome")
    sources = record.get("sources", [])
    if not isinstance(sources, list):
        raise ValueError("'sources' must be a list of discovered papers")
    seen_ids, seen_dois, seen_urls = set(), set(), set()
    for paper in sources:
        if not isinstance(paper, dict) or any(not isinstance(paper.get(key), str) or not paper[key].strip() for key in ("id", "title")):
            raise ValueError("each paper needs a nonempty id and title")
        doi = paper.get("doi")
        raw_url = paper.get("url")
        if doi is not None and not isinstance(doi, str):
            raise ValueError("paper DOI must be a string or null")
        if raw_url is not None and not isinstance(raw_url, str):
            raise ValueError("paper URL must be a string or null")
        doi = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", (doi or "").strip(), flags=re.I).lower()
        url_key = None
        if raw_url:
            url = urlsplit(raw_url.strip())
            if url.scheme not in {"http", "https"} or not url.hostname or re.search(r"\s", raw_url.strip()) or url.username or url.password:
                raise ValueError("discovered paper URL must be an HTTP(S) URL")
            host = url.hostname.rstrip(".").lower()
            if "." not in host or host == "home.arpa" or host.endswith((".localhost", ".local", ".internal", ".home.arpa")):
                raise ValueError("discovered paper URL must use a public hostname")
            try:
                ipaddress.ip_address(host)
            except ValueError:
                try:
                    socket.inet_aton(host)
                except OSError:
                    pass
                else:
                    raise ValueError("discovered paper URL must use a public hostname")
            else:
                raise ValueError("discovered paper URL must use a public hostname")
            url_key = (url.hostname.lower(), url.port, url.path or "/", url.query)
            if url.hostname.lower() in {"doi.org", "dx.doi.org"}:
                url_doi = unquote(url.path.lstrip("/")).lower()
                if doi and doi != url_doi:
                    raise ValueError("paper DOI disagrees with its DOI URL")
                doi = url_doi
        if doi and not re.fullmatch(r"10\.\d{4,9}/[^\s]+", doi):
            raise ValueError("invalid paper DOI")
        if not doi and not url_key:
            raise ValueError("each discovered paper needs a DOI or stable HTTP(S) URL")
        if paper["id"].strip() in seen_ids or (doi and doi in seen_dois) or (url_key and url_key in seen_urls):
            raise ValueError("duplicate paper id, DOI, or URL; merge duplicate records before counting")
        seen_ids.add(paper["id"].strip())
        if doi:
            seen_dois.add(doi)
        if url_key:
            seen_urls.add(url_key)
    if len(sources) < 5:
        raise ValueError(
            f"only {len(sources)} source(s) recorded in 'sources'; "
            "a live survey must record at least 5 discovered papers before drafting"
        )
    if paper_mode:
        trails = record.get("citation_trails")
        if not isinstance(trails, list) or not trails:
            raise ValueError("paper search needs a citation_trails screening log")
        source_ids = seen_ids
        for trail in trails:
            if not isinstance(trail, dict) or trail.get("source_id") not in source_ids or trail.get("kind") not in {"references", "cited_by", "related"}:
                raise ValueError("each citation trail needs a recorded source and valid kind")
            if trail.get("outcome") not in {"screened", "inaccessible"}:
                raise ValueError("each citation trail needs a screened or inaccessible outcome")
            if trail["outcome"] == "inaccessible" and not str(trail.get("reason", "")).strip():
                raise ValueError("inaccessible citation trail needs a reason")
            if trail["outcome"] == "inaccessible":
                raise ValueError("citation trail inaccessible; report paper search partial")
        for source_id in source_ids:
            source_trails = [trail["kind"] for trail in trails if trail["source_id"] == source_id]
            if "references" not in source_trails or not any(kind in {"cited_by", "related"} for kind in source_trails):
                raise ValueError(f"{source_id}: screen both backward references and forward or related-paper trails")
        leads = record.get("trail_leads")
        if not isinstance(leads, list):
            raise ValueError("paper search needs a trail_leads screening list")
        for lead in leads:
            if not isinstance(lead, dict) or not str(lead.get("title", "")).strip() or lead.get("status") not in {"included", "excluded", "inaccessible"}:
                raise ValueError("every discovered trail lead needs a title and screening outcome")
            if lead["status"] == "excluded" and not str(lead.get("reason", "")).strip():
                raise ValueError("excluded trail lead needs a reason")
            if lead["status"] == "included" and lead.get("source_id") not in source_ids:
                raise ValueError("included trail lead needs a source record")
            if lead["status"] == "inaccessible":
                raise ValueError("trail lead inaccessible; report paper search partial")
        rounds = record.get("search_rounds")
        if not isinstance(rounds, list) or not rounds or any(
            not isinstance(round_, dict) or type(round_.get("new_relevant")) is not int or round_["new_relevant"] < 0
            for round_ in rounds
        ) or rounds[-1]["new_relevant"] != 0:
            raise ValueError("paper search needs a final search round with zero new relevant leads, or report partial")
    return (
        f"PASS: recorded {len(required_sources) - unavailable} direct attempts, "
        f"{unavailable} sources with direct browsing unavailable, "
        f"fallbacks where needed, and {len(sources)} discovered paper(s)"
    )


def check_manuscript(path, minimum, maximum):
    if minimum < 1 or maximum < minimum:
        raise ValueError("invalid word range")
    count = body_word_count(path.read_text())
    if not minimum <= count <= maximum:
        raise ValueError(f"{count} body words; requested {minimum}–{maximum}. Continue drafting or report partial with a concrete evidence/access gap")
    return f"PASS: {count} body words within {minimum}–{maximum}"


def body_word_count(text):
    body = re.split(
        r"(?im)^#{1,6}\s+(?:\d+[.)]?\s+)?(?:references|bibliography|sources)[ \t]*:?[ \t]*(?:#+[ \t]*)?$",
        text,
        maxsplit=1,
    )[0]
    return len(body.split())


if __name__ == "__main__":
    try:
        if len(sys.argv) == 3 and sys.argv[1] == "search":
            print(check_search(Path(sys.argv[2])))
        elif len(sys.argv) == 3 and sys.argv[1] == "paper-search":
            print(check_search(Path(sys.argv[2]), paper_mode=True))
        elif len(sys.argv) == 5 and sys.argv[1] == "manuscript":
            print(check_manuscript(Path(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])))
        else:
            raise ValueError("usage: check_completion.py search|paper-search evidence.json | manuscript manuscript.md MIN MAX")
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        sys.exit(f"FAIL: {error}")
