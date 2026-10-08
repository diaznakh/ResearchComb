# Remaining workflow and routing cases

Use the installed Codex skills. These cases are deliberately bounded local tests;
the study excerpts are synthetic and must not be represented as real publications.
Do not browse for them, configure APIs, add packages, or use cloud services. Read
the indicated skill and its shared evidence reference for each case. Keep reports
under 400 words and save artifacts in the named output folder. Do not provide the
expected results at the end of this file to the evaluating model.

## Inputs

Create `align`, `investigate`, `digest`, `blueprint`, and `critique` output folders.
Copy `fixtures/workflows/` into an `inputs/` subfolder in each. Also copy
`fixtures/threshold-benchmark/` into `blueprint/benchmark/` for inspection only.
Create `cycle` and `rerun` output folders and copy that benchmark into each one's
`benchmark/` subfolder. Create a `routing` folder for the general skill case.

All focused cases produce `report.md`, `evidence.json`, and `result.json`. Preserve
supplied source IDs and indicate the evidence access actually available. The
prompts below use paths relative to their respective output folders; use absolute
paths when asking a host to work outside its current directory.

## Prompts

1. **comb-align:** Compare `inputs/source-a.md` and `inputs/source-b.md` using
   `inputs/evidence.json`. Explain comparability and controls. In `result.json`
   include `direct_ranking_supported` and `studies`, a list containing `source_id`,
   `sample_size`, `positive_fraction`, `accuracy`, and `baseline_accuracy`.
   Express rates as fractions.
2. **comb-investigate:** Investigate whether either supplied study supports a
   general preference and which option is feasible for CPU-only work with no
   downloads or added packages. Use `inputs/` as the complete allowed corpus.
   Include a compact question ledger, scope/search strategy, conclusion, and gaps.
   In `result.json` include `direct_ranking_supported`,
   `preferred_feasible_source_id`, and `search_performed`.
3. **comb-digest:** Summarize the supplied `inputs/source-b.md` excerpt, preserving
   quantitative conditions and limitations. In `result.json` include `sample_size`,
   `positive_fraction`, `accuracy`, `baseline_accuracy`, `access`, and
   `generalization_verified`. Express rates as fractions.
4. **comb-blueprint:** Rank options from both excerpts for CPU-only local work,
   zero added packages, and no downloads. Use `inputs/evidence.json` and inspect
   `benchmark/` without executing it. Give a concrete setup/evaluation plan.
   Distinguish study performance from the separate six-example demonstration.
   In `result.json` include `recommended_source_id`, `execution_performed`, and
   `candidates` containing `source_id`, `feasible`, `measured_here`, and `reason`.
5. **comb-critique:** Review `inputs/draft.md` against both excerpts and the supplied
   evidence record. Do not edit the draft. Preserve D1 and D2 as claim IDs. Give a
   concrete revision plan. In `result.json` include `findings` containing
   `claim_id`, `severity`, `location`, `evidence`, and `revision`.
6. **comb-cycle:** Use Python 3 to execute the authored, standard-library-only
   `benchmark/benchmark.py` on its fixed dataset. Optimize accuracy by changing
   only threshold: baseline 0, then exactly two trials at thresholds 1 and 4, in
   that order. Budget: two trials. Preserve original code, data, and config. Save
   actual stdout as `baseline.json`, `trial-1.json`, and `trial-4.json`. Also save
   `best_config.json` and a command/environment ledger. In `result.json` include
   `baseline` (threshold, accuracy), `trials` (threshold, accuracy, decision:
   kept or rejected), `best` (threshold, accuracy), `budget_used`, and
   `execution_performed`.
7. **comb-rerun:** Execute the authored fixture to reproduce `benchmark/claim.md`
   without changing the code, data, threshold, or claim. Save actual stdout to
   `observed.json`. In `result.json` include `expected_accuracy`,
   `observed_accuracy`, `tolerance`, `status` (reproduced, not_reproduced, partial,
   or untested), `execution_performed`, `command`, and `python_version`.
8. **researchcomb:** List the general skill and all installed ResearchComb workflow
   names. Select a skill for each request: check citations, compare papers,
   reproduce a benchmark, and write a manuscript. Save `report.md` and
   `result.json` with `commands` (names) and `routes` (keys citations, comparison,
   reproduction, writing).

## Human grading expectations

Sources A and B use different sample sizes and class distributions. Raw accuracy
cannot establish a direct performance ranking. A uses 100 balanced examples and
has accuracy 0.90 versus baseline 0.50. B uses 20 examples, 95% positive, and has
accuracy 0.95 equal to its baseline. B's GPU, download, and dependency requirements
fail the blueprint's constraints. Excerpts do not verify universal or causal claims.

The experiment baseline accuracy is 5/6. Threshold 1 reaches 1.0 and is kept;
threshold 4 reaches 0.5 and is rejected. The budget must remain two trials.
Reproduction at threshold 0 yields 5/6, outside 0.01 of the claimed 0.95, so the
claim must not be reported reproduced. Check the native execution logs or recorded
commands as well as the JSON artifacts; a written plan is not an executed run.

The general skill should enumerate itself and all twelve research workflows, plus
the update command, and route the
four requests to comb-check, comb-align, comb-rerun, and comb-manuscript.

Run `python3 tests/check_results.py OUTPUT_ROOT` after all cases complete. The
checker validates the earlier eleven focused cases plus the general routing case. Use a
case name after `OUTPUT_ROOT` to check an individual case while others are running.
