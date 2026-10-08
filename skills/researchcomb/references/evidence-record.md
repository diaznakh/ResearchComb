# Shared evidence record

Use one record across discovery, comparison, writing, critique, and verification. Reuse a record supplied by the user or an earlier workflow. Preserve source and claim IDs when refining entries; add evidence or change a status only after an actual check. Do not treat an earlier model's status as proof.

For a substantial task with file access, save `evidence.json` beside the deliverable. For a narrow lookup or a host without persistent files, keep an equivalent compact table in the working context. Follow a user-requested format. Read only the records needed for the task, and avoid copying large source texts into the record.

## Structure

The JSON form has a question, a source register, and a claim register:

```json
{
  "question": "",
  "sources": [],
  "claims": []
}
```

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
