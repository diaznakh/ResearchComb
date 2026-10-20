# Paper and topic search sources

Use this directory when live source discovery is needed. Search through the host's existing browser or web-search tools. Respect the user's date range, domain restrictions, supplied-only corpus, and search budget; do not browse for a task restricted to local sources.

## Execution contract

For open-ended live academic searches in `comb-survey`, `comb-investigate`, and `comb-paper`:

1. Conduct source discovery in this conversation. Do not delegate searches or source verification to a subagent or autonomous background process; browser calls must appear in this chat's tool log. Running the local checker is allowed.
2. Make a real host browser or web-search call for each broad scholarly source before recording its outcome. Try the site's own search; if inaccessible, run its separate `site:` fallback. If the host has no direct browsing tool, record `unavailable` with the capability reason and no attempted URL, then run the source's fallback query. Copy URLs and queries from actual tool calls, never from memory or inference.
3. Before drafting, save `evidence.json` and run `python3 <researchcomb-folder>/scripts/check_completion.py search evidence.json` when local files and Python are available. For an open-ended `comb-paper` search, use `paper-search` instead. On FAIL, complete the missing work; include the actual PASS line in the report's Search Log. If the checker cannot run, disclose that and do not claim a PASS.
4. Count a discovered paper only when a DOI or stable HTTP(S) URL was confirmed in a tool result. List memory-only leads separately as unverified; do not count or cite them as inspected papers.

## Choose sources

| Source | Useful for |
| --- | --- |
| [Google Scholar](https://scholar.google.com/) | Broad academic topic, title, and author searches; citation trails and alternative versions. |
| [ResearchGate](https://www.researchgate.net/search/publications) | Publication discovery by topic, title, author, or DOI; researcher profiles and publicly accessible paper copies. |
| [Crossref](https://search.crossref.org/) and [OpenAlex](https://openalex.org/) | Broad discovery and bibliographic metadata. |
| [Semantic Scholar](https://www.semanticscholar.org/) | Related papers and academic discovery. |
| [PubMed](https://pubmed.ncbi.nlm.nih.gov/) and [Europe PMC](https://europepmc.org/) | Biomedical literature. |
| [alphaXiv](https://www.alphaxiv.org/), [arXiv](https://arxiv.org/), [bioRxiv](https://www.biorxiv.org/), and [medRxiv](https://www.medrxiv.org/) | Preprints and early research; verify publication status separately. |
| [GitHub](https://github.com/) and [Hugging Face](https://huggingface.co/) | Companion code, models, datasets, and technical documentation. |

For an open-ended academic topic or paper survey, first attempt one focused search through each broad source's own site: Google Scholar, ResearchGate, Crossref, OpenAlex, and Semantic Scholar. Open them individually through the host's browser tools; an access failure at one site says nothing about the others. Then use general web search and relevant field sources: PubMed and Europe PMC for biomedicine; arXiv or alphaXiv for AI and computing; bioRxiv or medRxiv for relevant life-science or medical preprints; GitHub or Hugging Face when code, models, or datasets matter. Use relevant primary websites, official documentation, and public institutional sources for broader topics. Follow promising results with further searches as needed. Narrow lookups, user-limited source sets, and explicit time or search budgets can use a smaller set; honor named sources even in a narrow task.

For an open-ended `comb-paper` run, also attempt PubMed, Europe PMC, alphaXiv, arXiv, bioRxiv, and medRxiv, even when the topic is outside their main field. Record an actual outcome: `searched` with result counts, `inaccessible` when the site failed, or `out_of_scope` with a one-line reason when the direct search succeeded but the source is a poor fit (e.g. bioRxiv for physical chemistry). Do not infer outcomes from the field label alone. For out-of-scope sources, a separate fallback is not required when the direct search worked. Search relevant reviews and article bibliographies for primary studies, and follow backward references plus forward citations or related-paper links from key sources. Screen each relevant lead found against the paper question, deduplicate it, and repeat focused searches until a new round finds no new relevant leads. Report partial if access, the user's budget, or the host prevents this check. This is saturation within the stated scope, not a claim to have searched every paper ever published.

## Search and follow the evidence

- On Google Scholar, use topic terms, a quoted paper title, or `author:` queries. Apply available year filters for recent work. Follow "Cited by," "Related articles," or "All versions" when useful for the question. Open the underlying paper or available abstract before attributing findings.
- On ResearchGate, search publications by research area, exact title, author, or DOI. Inspect public publication pages and full texts where available. Profiles and questions can help discovery, but a profile listing or discussion does not establish peer review or support a scientific claim. Match any uploaded version to the title, authors, DOI, and publication status.
- Deduplicate discoveries by DOI or stable identifier. Prefer canonical publisher or repository links in the bibliography; retain the discovery page separately when useful for provenance. Record the version and actual access level in the shared evidence record.
- Before drafting, check the actual browser tool log against the applicable source list. Report a compact table with source, query, attempted URL, and outcome. Copy each attempted URL from a real tool call; never construct it afterward to fill the table. Use `searched directly` only when that site's search results were opened, `inaccessible` only after an actual direct attempt, and `unavailable` with a capability reason when the host lacks direct browsing (no attempted URL; a real fallback search is still required). Use `not attempted` for other skipped searches. Give the reason when a source was outside the topic or excluded by the user's scope or budget. List domain-restricted web searches separately as fallback searches. Do not infer attempts or outcomes for one site from another. Search snippets and citation counts are discovery clues, not verified findings.
- For an open-ended live academic search with file access, save these attempts and at least five distinct, relevant discovered papers in `evidence.json` as described in the [evidence record](evidence-record.md). Before drafting, run `python3 <installed-researchcomb-folder>/scripts/check_completion.py search evidence.json`. If it fails, complete the missing attempts or report the task partial. Five is a discovery floor, not proof of adequate evidence; never add irrelevant or invented papers to pass. The checker cannot prove that recorded searches really happened; reconcile each entry with the browser tool log.
- For `comb-paper`, run the `paper-search` checker instead. It requires the eleven scholarly source attempts, a backward and forward/related citation-trail log, screening outcomes for encountered leads, and a final round with no new relevant leads. Keep searching if a source, theme, or relevant lead is outstanding. The checker validates the record's structure, not whether the logged work happened or whether the review is exhaustive.

## Access limits and fallback

If a relevant site's search interface cannot be used because the host lacks direct browsing, login is required, a CAPTCHA appears, or access is blocked, run a **separate general web query for that source**: `<topic terms> site:<domain>`. Do this once per relevant source, including each of the five broad sources above. Keep the query terms focused on the user's topic; a search tool may batch these as distinct queries in one call. Use these suffixes:

| Source | Web search suffix |
| --- | --- |
| Google Scholar | `site:scholar.google.com` |
| ResearchGate | `site:researchgate.net/publication` |
| Crossref | `site:search.crossref.org` |
| OpenAlex | `site:openalex.org` |
| Semantic Scholar | `site:semanticscholar.org/paper` |
| PubMed / Europe PMC | `site:pubmed.ncbi.nlm.nih.gov` / `site:europepmc.org` |
| alphaXiv / arXiv | `site:alphaxiv.org` / `site:arxiv.org` |
| bioRxiv / medRxiv | `site:biorxiv.org` / `site:medrxiv.org` |
| GitHub / Hugging Face | `site:github.com` / `site:huggingface.co` |

Record the exact fallback query and whether it returned relevant pages. A search engine may index only part of a site or no pages at all; no results do not establish that the site has no relevant papers. Label these as domain-restricted web searches, not searches inside the index. Never claim to have searched or read a blocked service. Continue with accessible publishers, repositories, and other sources for the underlying evidence.

Public scholarly APIs (Crossref, Europe PMC REST, arXiv export API, PubMed E-utilities, and Semantic Scholar public API) count as direct search attempts when the site's browser interface is unavailable or times out. OpenAlex is free for light use without a key but requires a free API key at scale. Record `method: api` in the evidence log. These APIs return bibliographic metadata and abstracts that site search would surface. Do not bypass access controls, bulk scrape search results, configure authentication-required APIs, install search services, or add paid access. ResearchGate's "Request full-text" contacts authors; use it only with explicit user authorization to send that request. If browsing is unavailable, work from supplied sources and mark live discovery unavailable.

### API etiquette

Follow polite-access practices when using scholarly APIs:

- **Crossref:** Add a `mailto` parameter with a user-provided contact email (e.g., `?mailto=user@example.org`) to access the polite pool with faster rate limits. Never invent an email address; ask the user or omit the parameter.
- **OpenAlex:** Free for casual use; heavier use needs a free API key from [openalex.org/settings/api](https://openalex.org/settings/api). See [rate limits and authentication](https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication).
- **NCBI E-utilities (PubMed):** Limit requests to 3 per second without an API key (10/sec with a key). Include `tool` and `email` parameters when available. See [E-utilities usage guidelines](https://www.ncbi.nlm.nih.gov/books/NBK25497/).
- **Semantic Scholar:** Respect the public API rate limits documented in their [API license](https://www.semanticscholar.org/product/api/license).
- **General:** On HTTP 429 (Too Many Requests), back off exponentially before retrying. Record rate-limit encounters in the evidence log.

### Local fetch cache

On a long review, `safe_fetch.py` can reuse successful 2xx bodies when you pass `--cache` or set `RESEARCHCOMB_CACHE=1`. The cache is opt-in. Entries live in `.researchcomb-cache/` under the current working directory (or `RESEARCHCOMB_CACHE_DIR`), are keyed by the final validated URL after redirects plus the User-Agent, and expire after 24 hours so `link_status` in `evidence.json` does not go stale. A cache hit still runs DNS and host checks, then copies the body into a fresh output path; it never returns or symlinks the shared cache file. Use a new output path for each fetch, as the evidence guide requires. For re-verification, pass `--no-cache` or set `RESEARCHCOMB_NO_CACHE=1`. Error responses, HTTP 429, non-2xx statuses, and `Cache-Control: no-store` are never stored. Default remains uncached.

## Known access limits

**Publisher blocking:** ACS (pubs.acs.org), RSC (pubs.rsc.org), and Elsevier (sciencedirect.com) block automated requests with HTTP 403. Direct fetch attempts will fail. Use Crossref, OpenAlex, or Europe PMC APIs for metadata and abstracts instead, or mark the publisher source inaccessible. DOI.org redirects to these publishers may also fail.

**Stub pages:** Elsevier's linkinghub (doi.org → linkinghub.elsevier.com) returns a ~2.7 KB meta-refresh stub instead of the paper. Nature may redirect to a cookie error page. These stubs do not establish full-text access. Fetch tools detect and reject them; fallback to metadata APIs.

**Non-functional search patterns:** Some documented search URLs no longer work:
- alphaXiv `/search?q=` returns HTTP 404
- Google Scholar direct search may return HTTP 400 for some queries; use the `site:` fallback
- Semantic Scholar site shows JavaScript challenges; use the public API
- bioRxiv, medRxiv, OpenAlex, and Europe PMC sites may time out due to JavaScript rendering; use their APIs
- Crossref UI may not display DOIs; use the API
- The Google Scholar `site:` fallback (`site:scholar.google.com`) may return author profiles instead of papers

For reliable access, prefer the keyless APIs listed above over site browsing when both are available.

Official search guidance: [Google Scholar help](https://scholar.google.com/intl/en/scholar/help.html) and [ResearchGate discovery help](https://help.researchgate.net/research-and-publications/discovering-and-requesting-research).
