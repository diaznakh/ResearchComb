# Paper and topic search sources

Use this directory when live source discovery is needed. Search through the host's existing browser or web-search tools. Respect the user's date range, domain restrictions, supplied-only corpus, and search budget; do not browse for a task restricted to local sources.

## Execution contract

For open-ended live academic searches in `comb-survey`, `comb-investigate`, and `comb-paper`:

1. Conduct source discovery in this conversation. Do not delegate searches or source verification to a subagent or autonomous background process; browser calls must appear in this chat's tool log. Running the local checker is allowed.
2. Make a real host browser or web-search call for each broad scholarly source before recording its outcome. Try the site's own search; if inaccessible, run its separate `site:` fallback. If the host has no direct browsing tool, record `unavailable` with the capability reason and no attempted URL, then run the source's fallback query. Copy URLs and queries from actual tool calls, never from memory or inference.
3. Before drafting, save `evidence.json` and run `python3 <researchcomb-folder>/scripts/check_completion.py search evidence.json` when local files and Python are available. On FAIL, complete the missing work; include the actual PASS line in the report's Search Log. If the checker cannot run, disclose that and do not claim a PASS.
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

## Search and follow the evidence

- On Google Scholar, use topic terms, a quoted paper title, or `author:` queries. Apply available year filters for recent work. Follow "Cited by," "Related articles," or "All versions" when useful for the question. Open the underlying paper or available abstract before attributing findings.
- On ResearchGate, search publications by research area, exact title, author, or DOI. Inspect public publication pages and full texts where available. Profiles and questions can help discovery, but a profile listing or discussion does not establish peer review or support a scientific claim. Match any uploaded version to the title, authors, DOI, and publication status.
- Deduplicate discoveries by DOI or stable identifier. Prefer canonical publisher or repository links in the bibliography; retain the discovery page separately when useful for provenance. Record the version and actual access level in the shared evidence record.
- Before drafting, check the actual browser tool log against the applicable source list. Report a compact table with source, query, attempted URL, and outcome. Copy each attempted URL from a real tool call; never construct it afterward to fill the table. Use `searched directly` only when that site's search results were opened, `inaccessible` only after an actual direct attempt, and `unavailable` with a capability reason when the host lacks direct browsing (no attempted URL; a real fallback search is still required). Use `not attempted` for other skipped searches. Give the reason when a source was outside the topic or excluded by the user's scope or budget. List domain-restricted web searches separately as fallback searches. Do not infer attempts or outcomes for one site from another. Search snippets and citation counts are discovery clues, not verified findings.
- For an open-ended live academic search with file access, save these attempts and at least five distinct, relevant discovered papers in `evidence.json` as described in the [evidence record](evidence-record.md). Before drafting, run `python3 <installed-researchcomb-folder>/scripts/check_completion.py search evidence.json`. If it fails, complete the missing attempts or report the task partial. Five is a discovery floor, not proof of adequate evidence; never add irrelevant or invented papers to pass. The checker cannot prove that recorded searches really happened; reconcile each entry with the browser tool log.

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

Do not bypass access controls, bulk scrape search results, replace browser searches with `curl` API calls, configure APIs, install search services, or add paid access. ResearchGate's "Request full-text" contacts authors; use it only with explicit user authorization to send that request. If browsing is unavailable, work from supplied sources and mark live discovery unavailable.

Official search guidance: [Google Scholar help](https://scholar.google.com/intl/en/scholar/help.html) and [ResearchGate discovery help](https://help.researchgate.net/research-and-publications/discovering-and-requesting-research).
