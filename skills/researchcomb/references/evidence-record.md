# Shared evidence record

Use one record across discovery, comparison, writing, critique, and verification. Reuse a record supplied by the user or an earlier workflow. Preserve source and claim IDs when refining entries; add evidence or change a status only after an actual check. Do not treat an earlier model's status as proof.

For a substantial task with file access, save `evidence.json` beside the deliverable. For a narrow lookup or a host without persistent files, keep an equivalent compact table in the working context. Follow a user-requested format. Read only the records needed for the task, and avoid copying large source texts into the record.

When a workflow needs live paper or topic discovery, read the [search source guide](search-sources.md), including Google Scholar and ResearchGate. Follow the user's source restrictions and record the searches and access actually available. Supplied-only tasks do not require live searches.

## Structure

The JSON form has a question, a source register, and a claim register:

```json
{
  "question": "",
  "sources": [],
  "claims": []
}
```

For an open-ended live academic search with file access, add a `searches` list. Include one entry per broad source in the [search guide](search-sources.md), using the URL from the actual browser call. Example:

```json
{"source":"Crossref","direct":{"url":"https://search.crossref.org/?q=example","outcome":"inaccessible"},"fallback":{"query":"example site:search.crossref.org","outcome":"relevant results found"}}
```

Use `searched` or `inaccessible` after a real direct attempt. If the host has no direct browsing tool, use `"direct":{"outcome":"unavailable","reason":"Host only offers web search"}` with no `url`. Both `inaccessible` and `unavailable` require the exact source-specific fallback query and its outcome. Never fill this record from an imagined tool call. The local coverage checker tests completeness of the record, not whether a browser call really occurred; compare it with the host tool log.

Each source contains:

| Field | Content |
| --- | --- |
| `id` | Stable local identifier, such as `S1`. |
| `title`, `authors`, `year` | Bibliographic identity; authors is a list. Leave unknown fields null rather than guessing. |
| `url` | Canonical publisher, repository, or supplied local source location. |
| `doi` | DOI when established, otherwise null. |
| `access` | `full_text`, `abstract`, `excerpt`, `metadata`, `code`, or `run`; record what was actually inspected. |
| `identity_status` | `verified`, `provided`, or `unverified`. Provided notes alone do not verify publisher metadata. |
| `link_status` | `accessible`, `inaccessible`, `broken`, or `not_checked`. A login wall, timeout, or rate limit is inaccessible; use broken only after a definite missing-resource response. Local files use `not_checked` unless an external link was also opened. |

Before opening a discovered web link, reject local or private network destinations, embedded credentials, and non-HTTP(S) schemes. Use the host's protected browser for public links; do not bypass its network restrictions with shell fetches. If a redirect reaches a blocked destination, stop and mark the link unverified. A supplied local file is a separate input, not a web citation.

Record a checked date and source type when they matter. Deduplicate by DOI or stable URL; a preprint and a published revision can remain separate versions when their findings differ. For code, record the inspected commit; for a run, record the command and result artifact.

Each material claim contains:

| Field | Content |
| --- | --- |
| `id` | Stable identifier, preserving any IDs supplied in a draft. |
| `text` | The claim, including relevant conditions, units, population, or evaluation protocol. |
| `status` | One of the statuses below. |
| `evidence` | A list of objects with `source_id`, `location` (page, section, figure, or file and lines), and `observation` (a short paraphrase or bounded quotation). |
| `note` | Check performed, qualification, reason for the status, or correction required. |

Use these claim statuses:

- `supported`: The inspected evidence supports the claim under its stated conditions.
- `qualified`: Evidence supports a narrower or conditional version; state the qualification.
- `contradicted`: Inspected evidence directly conflicts with the claim.
- `unsupported`: The reviewed relevant evidence does not substantiate the claim; state the search or inspection scope.
- `unverified`: Missing access, missing tools, or incomplete checks prevent an assessment.

Mark inference and proposed work explicitly in the claim text or note. A resolving DOI establishes a source identity, not claim support. A source can have verified metadata while its claims remain unverified. A failed fetch does not prove a claim false or a paper nonexistent.

## Handoff and delivery

Use the same register when writing citations, comparison matrices, and review findings. Match each bibliography entry to its source ID. Cite the public DOI or publisher URL in user-facing documents; internal IDs supplement those links.

Before delivery, resolve or qualify material contradicted and unsupported assertions. If a verification task is review-only, report them without editing the user's draft. Include a brief verification summary describing evidence access, unresolved claims, and what was actually checked. Keep unknowns visible rather than silently promoting them to supported.

For the live search completion gate, each discovered paper needs a nonempty `id`, `title`, and a DOI or stable HTTP(S) URL. Empty records and duplicate IDs, normalized DOIs, or URLs fail the gate; merge duplicates before counting. DOI resolver URLs are matched to DOI identifiers. URL matching ignores scheme and fragments but preserves paths and queries. These checks validate record structure, not paper relevance or authenticity.
