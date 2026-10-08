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

The GitHub package was installed as ResearchComb 0.5.0. A fresh native Codex run
discovered and loaded `comb-check/SKILL.md` and the shared evidence reference from
the installed plugin cache, confirming activation without a source-tree path.

## Coverage of every workflow

The remaining seven workflows were tested in two bounded native Codex batches
using the installed 0.5.0 plugin and local synthetic fixtures. The native logs
confirmed that each corresponding installed `SKILL.md` was read. All generated
artifacts passed the local checks and their reports were reviewed against the
fixture facts and constraints.

| Workflow | Observed result | Outcome |
| --- | --- | --- |
| comb-align | Preserved sample sizes, class balances, and baseline metrics; declined a direct ranking across incompatible datasets. | Passed |
| comb-investigate | Kept a question ledger and supplied-corpus scope; preferred the CPU-feasible option without claiming a live search or a universal accuracy advantage. | Passed |
| comb-digest | Preserved the 20-example sample, 95% class balance, 95% accuracy, matching baseline, and excerpt-only access limits. | Passed |
| comb-blueprint | Ranked the CPU-only option as feasible, rejected GPU/download/dependency requirements, and separated reported study metrics from an unexecuted six-example demonstration. | Passed |
| comb-critique | Flagged the invalid cross-dataset ranking and causal/generalization claims with severity, evidence, and concrete revisions. Input unchanged. | Passed |
| comb-cycle | Executed baseline and exactly two authorized trials: accuracy 5/6, then 1.0 (kept), then 0.5 (rejected). Saved threshold 1 as best; code, data, and original config unchanged. | Passed |
| comb-rerun | Executed threshold 0 and observed accuracy 5/6, outside tolerance 0.01 of claimed 0.95. Correctly reported not reproduced, with command and Python version. Inputs unchanged. | Passed |

The native logs show the four actual Python benchmark commands for the cycle and
reproduction cases. These were executed tests rather than written run plans.
The general `researchcomb` skill also passed discovery of all twelve skills and
routing of citation, comparison, reproduction, and writing requests.

Coverage now includes one passing representative behavioral case for **all eleven
workflow skills**, plus the general discovery/routing case. This covers the tested
inputs and constraints, not every possible research task. The seven added cases
are local synthetic tests; the original survey and citation check used real public
paper sources. Antigravity behavioral coverage remains unavailable as noted below.

Two grading assumptions were corrected during evaluation: a seed declaration can
be qualified when its implementation is absent, and a canonical publisher link is
a valid reference even when the DOI is not written literally in the document.
These changes accept accurate, appropriately qualified outputs; the three actual
code mismatches and two citation errors remain required findings.

## Search source checks — 8 October 2026

Version 0.5.3 adds a shared browser search guide for Google Scholar and ResearchGate.
All twelve skills reach it through the existing evidence reference. Local links,
skill metadata, and all four checker unit tests passed.

A live lookup for "Attention Is All You Need" could not fetch either service's
direct search results through the host web tool. An ordinary web search restricted
to public ResearchGate publication pages returned candidates, including different
works and later uploaded records; these were not treated as verified original
publication metadata. The canonical arXiv abstract was accessible for checking
identity. Google Scholar search access remains unverified. This is a browser
access check, not a new model behavioral pass; the workflow cases above were not
rerun for this instruction update.

Version 0.5.5 strengthens the guide for open-ended topic searches: attempt the
five broad scholarly search pages, add relevant field sources, and report each
attempted URL and outcome. Three fresh Codex runs on one RAG research prompt
showed a remaining limitation. The first used only domain-restricted web queries;
the next two opened Google Scholar directly, then claimed direct attempts at four
other sites that did not appear in their tool logs. All three produced a research
brief, but **none passed direct-source coverage verification**. Instruction-only
skills cannot enforce tool calls or prevent an AI host from misreporting them.
Check actual browsing activity when complete source coverage is required.

Version 0.5.6 adds a separate general web query with a `site:` suffix for each
relevant source whose own search is unavailable. In one fresh Codex run on the
same RAG prompt, the tool log contained all five broad-source fallback queries.
The fallback search check passed. The final brief still claimed direct attempts
at all five sites, while the log showed only a Google Scholar direct attempt;
direct-source reporting remains unreliable and was not counted as passing.

## Limits

Several publisher pages were inaccessible. The survey and manuscript explicitly
recorded abstract or indexed-excerpt access for those sources. Only two of the
manuscript's nine sources were inspected in full text, so a passing run does not
establish complete verification of the wider literature.

An additional independent review of the entire manuscript was stopped after
installed-skill activation was confirmed. It produced no completed verification
report, and is not counted among the four passing regression cases.

An Antigravity plan with the same cases was prepared, but native window input was
unavailable and the local browser interface was blocked. No Antigravity behavior
pass is claimed. Further evaluation was kept in Codex as requested.
