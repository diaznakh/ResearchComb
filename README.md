# ResearchComb

<img src="assets/logo.jpg" alt="ResearchComb logo: a comb passing through a sheet of paper" width="180" height="180">

ResearchComb is a free, MIT-licensed research skill for **Codex and Antigravity**. It helps find papers and citations, inspect linked code, draft reports, review weaknesses, and check claims against sources. It uses the host's existing tools; there is no ResearchComb server, API key, or paid service to configure.

The package contains the general [researchcomb skill](skills/researchcomb/SKILL.md), eleven focused workflow skills, a portable [plugin manifest](plugin.json), and a [Codex marketplace](.agents/plugins/marketplace.json). The skills contain instructions and a shared evidence-record reference. There are no bundled servers or API clients. The regression checks under `tests/` run locally and are not runtime tools.

## Install from GitHub

In Codex or Antigravity with GitHub and local file access, paste:

> Install ResearchComb from https://github.com/diaznakh/ResearchComb for my account. Use your native plugin installer if it accepts this GitHub repository; otherwise copy every complete skill folder under `skills/`, including its supporting files, into your user skills directory. Confirm that `researchcomb` and the eleven `comb-*` workflows appear in your available skills. Do not run repository code.

The host may ask you to approve GitHub access or a local file write. A link by itself may only open or summarize the repository; use the instruction above to request installation.

### Codex

For the plugin in Codex CLI or the Codex desktop app, register this repository as a marketplace, then install `researchcomb@researchcomb`:

```text
codex plugin marketplace add https://github.com/diaznakh/ResearchComb.git
codex plugin add researchcomb@researchcomb
```

Start a new chat and ask Codex to use ResearchComb, or type `$` and choose a ResearchComb skill. If plugin installation is unavailable, ask `$skill-installer` to install every skill folder under `skills/` from this repository. To update an installed plugin, refresh its marketplace with `codex plugin marketplace upgrade researchcomb`, then run `codex plugin add researchcomb@researchcomb` again.

### Antigravity

In Antigravity, ask its agent to copy every folder under `skills/` from this repository into `~/.gemini/config/skills/` for all workspaces, or `<workspace-root>/.agents/skills/` for one workspace. Preserve each skill's folder name. Check **Customizations → Installed → Skills & Rules** or ask which skills are available. To update a previous installation, replace only the ResearchComb skill folders with the current versions. Antigravity CLI can also install the GitHub package with:

```text
agy plugin install https://github.com/diaznakh/ResearchComb
```

## Use

The workflow names are shared across both hosts. Antigravity exposes them as slash commands. In Codex, type `$` and select the matching skill. Plugin hosts may display a ResearchComb namespace. A skill does not create a slash-command UI in a host that uses another selector. You can also write “Use comb-survey to…” in plain language.

| Antigravity command | Workflow |
| --- | --- |
| `/comb-trace` | Check paper claims against companion code and reproducibility evidence. |
| `/comb-cycle` | Try hypotheses in a bounded local experiment loop and retain measured improvements. |
| `/comb-align` | Compare sources in a cited matrix of findings and disagreements. |
| `/comb-investigate` | Produce a substantial research brief with sources and verification records. |
| `/comb-manuscript` | Write a paper or report with citations and a checked length target. |
| `/comb-survey` | Map literature on a topic, lab, investigator, or author. |
| `/comb-blueprint` | Rank feasible technical approaches and provide implementation plans. |
| `/comb-rerun` | Plan or execute a local reproduction with expected-versus-observed results. |
| `/comb-critique` | Produce critical, major, and minor findings with a revision plan. |
| `/comb-check` | Check citations, attribution, quotations, and numbers against source evidence. |
| `/comb-digest` | Summarize a paper, PDF, report, README, or local artifact through focused reading. |

Live paper search, code execution, and background monitoring depend on the host's available browsing, execution, and scheduling tools. ResearchComb will state when one of those tools is unavailable.

Research, writing, comparison, and review reuse a [shared evidence record](skills/researchcomb/references/evidence-record.md). It records which source passage supports each claim and keeps inaccessible or unchecked evidence visible. A resolving DOI alone does not verify a scientific claim. Manuscripts check requested length against a measured count before being marked complete.

See [workflow regression checks](tests/README.md) for realistic test prompts, local checks, and recorded results.

## Prompt examples

These plain-language prompts work in both Codex and Antigravity. You can also select the corresponding skill with `$` in Codex or `/` in Antigravity before entering the request. Replace example filenames, folders, topics, and environment choices with your own.

**General research — `researchcomb`**

> Use ResearchComb to research when retrieval-augmented generation improves factual accuracy and when it fails. Find primary sources, compare their findings, and produce a cited brief with an evidence record and unresolved questions.

**Paper-to-code audit — `comb-trace`**

> Use comb-trace to audit paper.pdf against its companion repository in ./paper-code. Check data splits, hyperparameters, and evaluation metrics. Cite paper sections and code locations, grade mismatches by severity, and inspect without running the code.

**Experiment loop — `comb-cycle`**

> Use comb-cycle to optimize validation F1 in ./benchmark using my existing local .venv. You may run the benchmark and change only the decision threshold. Keep the validation data fixed, use at most three trials and fifteen minutes, preserve the original configuration, and record which measured changes you keep or reject.

**Source comparison — `comb-align`**

> Use comb-align to compare paper-a.pdf and paper-b.pdf. Build a cited matrix covering study design, datasets, baselines, results, and limitations. Explain agreements and disagreements, and identify results that cannot be compared directly.

**Deep investigation — `comb-investigate`**

> Use comb-investigate to examine whether CO2-assisted propane dehydrogenation can reduce emissions under industrial conditions. Find evidence supporting and challenging the claim, separate laboratory results from life-cycle estimates, and save a research brief and evidence.json.

**Manuscript writing — `comb-manuscript`**

> Use comb-manuscript to turn findings.md and evidence.json into a 6,000–6,500-word review, excluding the bibliography. Include an abstract, introduction, thematic comparison, limitations, research priorities, and conclusion. Preserve source IDs, use linked references, save manuscript.md, and report its measured word count.

**Literature survey — `comb-survey`**

> Use comb-survey to review research on CO2-assisted propane dehydrogenation published during the past five years. Record search terms and screening criteria, distinguish primary studies from reviews and preprints, and deliver a literature matrix, thematic synthesis, gaps, and linked bibliography.

**Implementation planning — `comb-blueprint`**

> Use comb-blueprint to rank practical methods for searching my local document collection on a CPU-only laptop with 8 GB RAM. Support the options with papers, code, and documentation. Give prerequisites, resource estimates, evaluation plans, and failure points. Produce a plan without installing or executing anything.

**Result reproduction — `comb-rerun`**

> Use comb-rerun to reproduce the accuracy in Table 2 of paper.pdf using ./paper-code, ./data, and my existing local .venv. Local execution is authorized; preserve the original code and data and do not install dependencies. Record the protocol, commands, expected and observed results, and deviations. Report whether the result reproduces within one percentage point.

**Research critique — `comb-critique`**

> Use comb-critique to review draft.md with evidence.json. Check methods, controls, baselines, uncertainty, and whether the conclusions follow from the evidence. Give critical, major, and minor findings with source locations and a prioritized revision plan. Leave the draft unchanged.

**Citation and claim verification — `comb-check`**

> Use comb-check to verify draft.md against evidence.json and the underlying sources. Check citation identities, numerical claims, quotations, and attribution. Return a correction table and updated verification statuses, distinguish inaccessible sources from broken links, and leave the draft unchanged.

**Source summary — `comb-digest`**

> Use comb-digest to summarize paper.pdf in about 300 words. Cover its question, method, main findings, important numerical conditions, and limitations, with page or section references. State whether you inspected the full text or only part of it.

## License

ResearchComb is available under the [MIT License](LICENSE).
