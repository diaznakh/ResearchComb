<p align="center">
  <img src="assets/logo.png" alt="ResearchComb logo: a comb passing through a sheet of paper" width="220" height="220">
</p>

<h1 align="center">ResearchComb</h1>

<p align="center"><strong>Find the paper. Follow the evidence.</strong></p>
<p align="center">Research workflows for Codex and Antigravity, right inside your AI chat.</p>

<p align="center">
  <img src="assets/badges.svg" alt="Supports Codex and Antigravity; eleven workflows; MIT licensed" width="366" height="28">
</p>

<p align="center">
  <a href="#quick-start">Quick start</a> ·
  <a href="#workflows">Workflows</a> ·
  <a href="#prompt-examples">Prompt examples</a> ·
  <a href="#tested-in-codex">Test results</a> ·
  <a href="#faq">FAQ</a> ·
  <a href="#accuracy-responsibility-and-liability">Notice</a>
</p>

---

ResearchComb helps your AI assistant find literature, connect findings, inspect companion code, write manuscripts, and check claims against sources. Bring a question, a paper, or a draft; choose a workflow or let the general `researchcomb` skill guide the task.

**Free and open source. Eleven focused workflows. No ResearchComb server or API keys to configure.** It uses your host's existing browsing, file, execution, and scheduling tools.

## Quick start

### 1. Ask your AI to install it

Paste this into Codex or Antigravity with GitHub and local file access:

```text
Install ResearchComb from
https://github.com/diaznakh/ResearchComb for my account.
Use your native plugin installer if it accepts this
GitHub repository; otherwise copy every complete skill
folder under skills/, including supporting files, into
your user skills directory. Confirm researchcomb and all
eleven comb-* workflows are available. Do not run
repository code.
```

The host may ask for its normal approval to fetch GitHub or write to its skills directory. Use the instruction above to request installation; a bare link may only open the repository.

### 2. Start a new chat and give it a task

```text
Use comb-survey to review recent work on
retrieval-augmented generation. Compare methods and
limitations, distinguish preprints from published
studies, and give a literature matrix with linked
references.
```

In **Codex**, type `$` and select a skill. In **Antigravity**, use its `/comb-*` slash command. Plain-language requests such as “Use comb-check to…” work in either host. A plugin may display the ResearchComb namespace with the skill name.

### Install manually

<details>
<summary><strong>Codex — CLI or desktop</strong></summary>

Register the GitHub source and install the plugin:

```sh
codex plugin marketplace add https://github.com/diaznakh/ResearchComb.git
codex plugin add researchcomb@researchcomb
```

Start a new chat after installation. If plugins are unavailable in your Codex surface, ask `$skill-installer` to install every complete folder under `skills/` from this repository.

</details>

<details>
<summary><strong>Antigravity — global skills, workspace skills, or CLI</strong></summary>

Ask the agent to copy every complete folder under `skills/`, preserving names and supporting files, into one of these locations:

| Scope | Location |
| --- | --- |
| All workspaces | `~/.gemini/config/skills/` |
| One workspace | `<workspace-root>/.agents/skills/` |

Check **Customizations → Installed → Skills & Rules** for `researchcomb` and the eleven `comb-*` skills.

Antigravity CLI also supports the GitHub package:

```sh
agy plugin install https://github.com/diaznakh/ResearchComb
```

</details>

<details>
<summary><strong>Update an existing installation</strong></summary>

For a GitHub marketplace installed in Codex:

```sh
codex plugin marketplace upgrade researchcomb
codex plugin add researchcomb@researchcomb
```

For copied Antigravity skills, replace the ResearchComb folders with the current complete versions from `skills/`. Preserve unrelated skills. Start a new chat after updating.

</details>

## Workflows

Use [`researchcomb`](skills/researchcomb/SKILL.md) for a task spanning several stages, or select the focused skill that fits your goal. The commands below use Antigravity's slash syntax; Codex exposes the same names through its skill selector.

| Your goal | Workflow | What you receive |
| --- | --- | --- |
| Find the literature | [`/comb-survey`](skills/comb-survey/SKILL.md) | A literature matrix, themes, gaps, and bibliography |
| Investigate a question | [`/comb-investigate`](skills/comb-investigate/SKILL.md) | A cited brief with a search strategy and verification record |
| Understand a source | [`/comb-digest`](skills/comb-digest/SKILL.md) | A focused summary with source locations and limitations |
| Compare findings | [`/comb-align`](skills/comb-align/SKILL.md) | Agreements, disagreements, and a grounded comparison matrix |
| Check a paper's code | [`/comb-trace`](skills/comb-trace/SKILL.md) | Claim-to-code findings and reproducibility gaps |
| Plan an implementation | [`/comb-blueprint`](skills/comb-blueprint/SKILL.md) | Ranked options and a concrete technical plan |
| Write a manuscript | [`/comb-manuscript`](skills/comb-manuscript/SKILL.md) | A sourced draft with a checked length target |
| Challenge the reasoning | [`/comb-critique`](skills/comb-critique/SKILL.md) | Severity-graded findings and a revision plan |
| Verify claims and citations | [`/comb-check`](skills/comb-check/SKILL.md) | A correction table with evidence and unresolved statuses |
| Try measured improvements | [`/comb-cycle`](skills/comb-cycle/SKILL.md) | A bounded experiment ledger and the best measured configuration |
| Reproduce a result | [`/comb-rerun`](skills/comb-rerun/SKILL.md) | Expected-versus-observed results with commands and deviations |

## A citation check in practice

In our [citation regression fixture](tests/fixtures/citation-draft.md), a draft uses a real DOI to claim that FeNi and NiPt are equally selective for producing propylene. `comb-check` reads the underlying evidence and returns:

| Check | Finding |
| --- | --- |
| Source identity | The DOI belongs to Gomez et al. (2018); the draft gives another paper's author and year. |
| Claim support | Under the studied conditions, FeNi favors propylene while NiPt favors dry reforming. |
| Revision | Correct the citation identity and describe the distinct catalyst pathways. |

The supporting source is the [Nature Communications paper](https://www.nature.com/articles/s41467-018-03793-w). This is a recorded test outcome. A resolving DOI identifies a source; checking the source determines whether it supports the nearby claim.

## How it works

1. **Frame the task.** Set the question, scope, output, and any execution budget.
2. **Gather evidence.** Read public research pages or supplied sources and record what was accessible.
3. **Carry the record forward.** Reuse source and claim IDs across comparisons, drafts, and reviews.
4. **Challenge and check.** Examine methodology, attribution, numbers, and source-to-claim support.
5. **Deliver with limits visible.** Report the result, measured completion checks, and remaining unknowns.

The [shared evidence record](skills/researchcomb/references/evidence-record.md) keeps bibliographic identity, link access, and claim support separate. Claims can be **supported**, **qualified**, **contradicted**, **unsupported**, or **unverified**. A substantial task can save the record as `evidence.json`; a narrow lookup can use a compact table in context.

### Paper and topic search sources

The [shared search guide](skills/researchcomb/references/search-sources.md) includes **Google Scholar** and **ResearchGate**, alongside Crossref, OpenAlex, Semantic Scholar, PubMed, Europe PMC, and preprint repositories. It also covers GitHub and Hugging Face when code or datasets matter, and official primary websites for broader topics.

- **Google Scholar:** topic, title, and author searches; citation trails and alternative paper versions.
- **ResearchGate:** publication and researcher discovery, with public paper copies where available.

These sources use the host's existing browser; ResearchComb maintains no separate search index or API integration. Access depends on the host and website. Blocked or login-only content is recorded as inaccessible, with accessible sources used instead. A search result or profile listing does not verify a paper's claims.

```text
Use comb-survey to find papers on battery recycling.
Search Google Scholar and ResearchGate alongside other
relevant sources. Record searches and access limits,
deduplicate papers, and verify findings against the
underlying papers or abstracts before citing them.
```

## Prompt examples

Expand a workflow and copy its prompt. Replace filenames, topics, folders, and environment choices with your own.

<details>
<summary><strong>General research</strong> · <code>researchcomb</code></summary>

```text
Use ResearchComb to research when retrieval-augmented
generation improves factual accuracy and when it fails.
Find primary sources, compare their findings, and
produce a cited brief with an evidence record and
unresolved questions.
```

</details>

<details>
<summary><strong>Implementation consistency</strong> · <code>comb-trace</code></summary>

```text
Use comb-trace to audit paper.pdf against its companion
repository in ./paper-code. Check data splits,
hyperparameters, and evaluation metrics. Cite paper
sections and code locations, grade mismatches by
severity, and inspect without running the code.
```

</details>

<details>
<summary><strong>Experiment loop</strong> · <code>comb-cycle</code></summary>

```text
Use comb-cycle to optimize validation F1 in ./benchmark
using my existing local .venv. You may run the benchmark
and change only the decision threshold. Keep the
validation data fixed, use at most three trials and
fifteen minutes, preserve the original configuration,
and record which measured changes you keep or reject.
```

</details>

<details>
<summary><strong>Source comparison</strong> · <code>comb-align</code></summary>

```text
Use comb-align to compare paper-a.pdf and paper-b.pdf.
Build a cited matrix covering study design, datasets,
baselines, results, and limitations. Explain agreements
and disagreements, and identify results that cannot be
compared directly.
```

</details>

<details>
<summary><strong>Deep investigation</strong> · <code>comb-investigate</code></summary>

```text
Use comb-investigate to examine whether CO2-assisted
propane dehydrogenation can reduce emissions under
industrial conditions. Find evidence supporting and
challenging the claim, separate laboratory results from
life-cycle estimates, and save a research brief and
evidence.json.
```

</details>

<details>
<summary><strong>Manuscript writing</strong> · <code>comb-manuscript</code></summary>

```text
Use comb-manuscript to turn findings.md and
evidence.json into a 6,000–6,500-word review, excluding
the bibliography. Include an abstract, introduction,
thematic comparison, limitations, research priorities,
and conclusion. Preserve source IDs, use linked
references, save manuscript.md, and report its measured
word count.
```

</details>

<details>
<summary><strong>Literature survey</strong> · <code>comb-survey</code></summary>

```text
Use comb-survey to review research on CO2-assisted
propane dehydrogenation published during the past five
years. Record search terms and screening criteria,
distinguish primary studies from reviews and preprints,
and deliver a literature matrix, thematic synthesis,
gaps, and linked bibliography.
```

</details>

<details>
<summary><strong>Implementation planning</strong> · <code>comb-blueprint</code></summary>

```text
Use comb-blueprint to rank practical methods for
searching my local document collection on a CPU-only
laptop with 8 GB RAM. Support the options with papers,
code, and documentation. Give prerequisites, resource
estimates, evaluation plans, and failure points. Produce
a plan without installing or executing anything.
```

</details>

<details>
<summary><strong>Result reproduction</strong> · <code>comb-rerun</code></summary>

```text
Use comb-rerun to reproduce the accuracy in Table 2 of
paper.pdf using ./paper-code, ./data, and my existing
local .venv. Local execution is authorized; preserve the
original code and data and do not install dependencies.
Record the protocol, commands, expected and observed
results, and deviations. Report whether the result
reproduces within one percentage point.
```

</details>

<details>
<summary><strong>Research critique</strong> · <code>comb-critique</code></summary>

```text
Use comb-critique to review draft.md with evidence.json.
Check methods, controls, baselines, uncertainty, and
whether the conclusions follow from the evidence. Give
critical, major, and minor findings with source
locations and a prioritized revision plan. Leave the
draft unchanged.
```

</details>

<details>
<summary><strong>Citation and claim verification</strong> · <code>comb-check</code></summary>

```text
Use comb-check to verify draft.md against evidence.json
and the underlying sources. Check citation identities,
numerical claims, quotations, and attribution. Return a
correction table and updated verification statuses,
distinguish inaccessible sources from broken links, and
leave the draft unchanged.
```

</details>

<details>
<summary><strong>Source summary</strong> · <code>comb-digest</code></summary>

```text
Use comb-digest to summarize paper.pdf in about 300
words. Cover its question, method, main findings,
important numerical conditions, and limitations, with
page or section references. State whether you inspected
the full text or only part of it.
```

</details>

## Tested in Codex

Recorded on **8 October 2026**, using native Codex runs and the host's existing tools:

| Check | Recorded result |
| --- | --- |
| Focused workflow cases | **11 / 11 passed** |
| General command discovery and routing | **Passed** — twelve skills discovered and four requests routed |
| Local checker tests | **4 / 4 passed** |
| Long manuscript case | **6,201 measured body words**, within the requested range |
| Experiment loop | Improvement kept, regression rejected, two-trial budget respected |
| Reproduction case | A mismatched claimed result correctly reported as not reproduced |

Coverage is one representative case per workflow. Seven cases use local synthetic fixtures; the initial survey and citation checks use real public paper sources. Some publisher text was inaccessible and remained labelled as abstract or excerpt evidence. Antigravity skill installation was checked; its behavioral tests remain unverified.

[Read the results and limits](tests/RESULTS.md) · [Run the regression checks](tests/README.md)

## FAQ

<details>
<summary><strong>Do I need a server, API key, or extra account?</strong></summary>

ResearchComb is an instruction-based skill bundle. It has no bundled server or API client and requires no ResearchComb account. Your AI host's normal access and usage limits still apply.

</details>

<details>
<summary><strong>Can it work offline?</strong></summary>

It can use supplied local papers, reports, code, and data through the host's existing tools. Finding new papers and checking public links requires browsing. It records missing access rather than inventing source content.

</details>

<details>
<summary><strong>Does it guarantee every claim is correct?</strong></summary>

It guides verification and records the evidence behind conclusions. Read the verification summary: missing sources, limited text access, and unchecked claims stay visible. Representative passing tests do not establish accuracy for every research task.

</details>

<details>
<summary><strong>Can it run experiments or monitor a topic?</strong></summary>

Experiments need available local execution tools and an authorized environment. Recurring monitoring needs the host's scheduler and a user request. ResearchComb does not provision cloud compute or paid services; it provides a plan when execution or scheduling is unavailable.

</details>

## Inside the repository

- [`skills/`](skills/) — the general skill, eleven workflows, and shared evidence guidance.
- [`plugin.json`](plugin.json) — portable package and Codex presentation metadata.
- [Codex marketplace](.agents/plugins/marketplace.json) — GitHub installation source.
- [`tests/`](tests/) — fixtures, local checks, and recorded native Codex outcomes.
- [`assets/`](assets/) — the ResearchComb logo and local README badges.

## License

[MIT](LICENSE). Free to use, modify, and share under the license terms.

## Accuracy, responsibility, and liability

ResearchComb assists with research; its outputs may be incorrect, incomplete, or outdated. AI models may invent or misattribute citations, misinterpret sources, overlook conflicting evidence, or produce faulty code and experimental conclusions. Citation checks, evidence records, and passing tests do not guarantee accuracy, completeness, or reproducibility.

Users are responsible for independently checking sources, citations, calculations, code, and conclusions before publishing, executing, or relying on an output. ResearchComb does not replace qualified professional advice or the user's own judgment. Review the host AI's permissions and any proposed commands before authorizing execution.

ResearchComb is provided **"as is," without warranty**, under the [MIT License](LICENSE). To the extent permitted by applicable law, the authors and copyright holders disclaim warranties and liability for claims, damages, or other losses arising from the software or its use, including reliance on generated outputs. This notice summarizes the license; it does not replace or expand its terms or exclude liability that cannot lawfully be excluded.
