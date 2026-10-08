# Workflow regression checks

These cases evaluate actual model-generated artifacts. They use the host's normal
skills, browser, and file tools. No test connects an API client, installs a server,
or requires a new API key. The local checker uses Python's standard library.

Create an isolated output directory with four folders: `survey`, `check`, `trace`,
and `manuscript`. Copy `fixtures/citation-draft.md` into `check/draft.md` and
`fixtures/code-study/` into `trace/study/`. The study is synthetic and must not be
run. An optional local Git commit of that fixture lets the audit record provenance.
Do not give the expected findings below to the model being evaluated.

Run these prompts in Codex or Antigravity, substituting absolute paths for `REPO`
and `OUTPUT`. Use the current skill files, including supporting references. Save
deliverables in the named case directory. Use a fresh conversation for independent
cases; the manuscript deliberately reuses the survey artifacts.

## Survey

> Use comb-survey at REPO/skills/comb-survey/SKILL.md to survey CO2-assisted
> oxidative dehydrogenation of propane and how catalyst composition changes
> selectivity or reaction pathways. Restrict this small survey to
> https://www.nature.com/articles/s41467-018-03793-w,
> https://pubs.acs.org/doi/10.1021/acscatal.2c01374, and
> https://doi.org/10.3390/catal16020163. Use the host browser to inspect them,
> distinguish original research from review, and disclose access limits. Write
> 700–1000 words excluding the bibliography, with a comparison matrix, scoped
> gaps, and clickable references. Save OUTPUT/survey/report.md and the shared
> evidence record at OUTPUT/survey/evidence.json. Do not configure API clients.

Check that all three sources appear, that source access is accurately described,
and that catalyst differences are preserved. Do not grade an accessible abstract
as full-text access. Inspect source passages for the recorded numerical claims;
schema validity alone is insufficient.

## Citation check

> Use comb-check at REPO/skills/comb-check/SKILL.md to check
> OUTPUT/check/draft.md against its primary sources using the host browser.
> Leave the input unchanged. Save a correction table and bibliography corrections
> in OUTPUT/check/report.md and a shared record at OUTPUT/check/evidence.json.
> Preserve C1–C4 as claim IDs and include the second supplied reference in the
> source register even if it cannot be resolved. Do not configure API clients.

The primary Nature paper distinguishes Fe3Ni/CeO2's propylene pathway from
Ni3Pt/CeO2's dry reforming pathway. Its DOI belongs to Gomez et al. (2018), not
Rigamonti et al. (2022). Its main flow-reactor experiments use 823 K; it does not
establish the draft's universal 99% emissions reduction. C1 and C2 should be
contradicted, C3 unsupported or unverified with its scope, and C4 supported.
The second supplied DOI must not be falsely verified. An inaccessible fetch alone
does not justify declaring it broken or nonexistent.

## Code audit

> Use comb-trace at REPO/skills/comb-trace/SKILL.md to audit
> OUTPUT/trace/study/paper.md against the companion configuration and code.
> Do not run or edit the study. Save OUTPUT/trace/report.md and
> OUTPUT/trace/evidence.json. Preserve T1–T4 as claim IDs and record the inspected
> commit if available. Distinguish inspected code from a measured experiment.

Expected mismatches: batch size 32 versus 64, dropout 0.1 versus 0.5, and a claimed
test split versus a `train` selector. The seed declaration matches 42, but actual
random-state initialization remains unverified because the fixture has no training
implementation. A supported or qualified T4 is appropriate. No measured accuracy
should be invented. Check the reported source locations against the fixture files.

## Long manuscript and evidence handoff

> Use comb-manuscript at REPO/skills/comb-manuscript/SKILL.md to turn
> OUTPUT/survey/report.md and OUTPUT/survey/evidence.json into a substantial
> review manuscript on CO2-assisted propane dehydrogenation catalyst pathways
> and evidence limitations. Preserve source and claim IDs. You may add verified
> primary sources using the host browser if needed. Write 6000–6500 body words,
> excluding bibliography, as an estimated 20-page draft. Include an abstract,
> introduction, thematic comparison, methodological limitations, research
> priorities, conclusion, and linked bibliography. Build the artifact in sections
> and measure whitespace-separated words before the References or Bibliography
> heading using local tools. Save OUTPUT/manuscript/manuscript.md, evidence.json,
> and completion.json with status, measured_word_count, count_scope, and
> rendered_page_count (null unless rendered). Do not stop at an outline or invent
> findings to meet the target.

Check the saved manuscript's actual length, preservation of source identities and
claim IDs, meaningful development without repeated filler, accurate attribution,
and the distinction between estimated pages and measured pagination. A genuinely
blocked task must be reported partial, which is honest behavior but does not pass
this completion regression.

## Local checks

```text
python3 -m unittest discover -s tests -p 'test_*.py'
python3 tests/check_results.py /absolute/path/to/OUTPUT
```

The artifact checker validates record references, known-case outcomes, measured
length, and evidence handoff. It does not prove scientific correctness: review the
actual reports and supporting source locations too. Native model tests use the
host's existing usage allowance. Results can vary with the model, browsing access,
and runtime permissions; record the environment and any limits rather than
generalizing a passing run to every installation.

See [recorded results](RESULTS.md) for the completed run and remaining host limits.
