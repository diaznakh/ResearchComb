# Recorded regression results

Checked on 8 October 2026 against the ResearchComb 0.5.0 skill source in four
fresh, ephemeral native Codex CLI runs, using the account's existing configuration.
The manuscript intentionally consumed the survey's saved record. Test artifacts
were written to isolated temporary directories, not into the source repository.
No API client, server, dependency installation, or cloud compute was added.

| Case | Observed result | Outcome |
| --- | --- | --- |
| Literature survey | 971 body words, three requested sources, eight recorded claims, comparison matrix, linked references, and explicit full-text/abstract/excerpt access limits. | Passed |
| Citation check | Detected the catalyst attribution and author/year errors, rejected support for the universal emissions claim, retained the correct reactor temperature, and left the unresolved DOI unverified. Input unchanged. | Passed |
| Paper-to-code audit | Detected batch-size, dropout, and evaluation-split mismatches; correctly qualified the seed declaration because no run record exists. Inspected commit recorded; no code execution or measured accuracy claimed. Inputs unchanged. | Passed |
| Long manuscript and handoff | 6,201 measured body words within the requested 6,000–6,500 range; nine sources and sixteen claims; original S1–S3 and C1–C8 IDs preserved; bibliography links present; unrendered page count left null. | Passed |

All four artifact checks and four checker unit tests passed. The reports were also
reviewed for source access disclosure, attribution, inspection-versus-execution
claims, and honest completion reporting. The artifact checks do not prove every
scientific assertion correct.

Two grading assumptions were corrected during evaluation: a seed declaration can
be qualified when its implementation is absent, and a canonical publisher link is
a valid reference even when the DOI is not written literally in the document.
These changes accept accurate, appropriately qualified outputs; the three actual
code mismatches and two citation errors remain required findings.

## Limits

Several publisher pages were inaccessible. The survey and manuscript explicitly
recorded abstract or indexed-excerpt access for those sources. Only two of the
manuscript's nine sources were inspected in full text, so a passing run does not
establish complete verification of the wider literature.

An Antigravity plan with the same cases was prepared, but native window input was
unavailable and the local browser interface was blocked. No Antigravity behavior
pass is claimed. Further evaluation was kept in Codex as requested.
