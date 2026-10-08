# ResearchComb

ResearchComb is a free, MIT-licensed research skill for **Codex and Antigravity**. It helps find papers and citations, inspect linked code, draft reports, review weaknesses, and check claims against sources. It uses the host's existing tools; there is no ResearchComb server, API key, or paid service to configure.

The package contains the general [researchcomb skill](skills/researchcomb/SKILL.md), ten focused workflow skills, a portable [plugin manifest](plugin.json), and a [Codex marketplace](.agents/plugins/marketplace.json). The skills contain instructions only. There are no bundled servers, API clients, or executable scripts.

## Install from GitHub

In Codex or Antigravity with GitHub and local file access, paste:

> Install ResearchComb from https://github.com/diaznakh/ResearchComb for my account. Use your native plugin installer if it accepts this GitHub repository; otherwise copy every skill folder under `skills/` into your user skills directory. Confirm that `researchcomb` and the ten `comb-*` workflows appear in your available skills. Do not run repository code.

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
| `/comb-digest` | Summarize a paper, PDF, report, README, or local artifact through focused reading. |

Try: “Use ResearchComb to find recent papers on retrieval-augmented generation, compare their findings, inspect linked code, and give verified DOI links.”

Live paper search, code execution, and background monitoring depend on the host's available browsing, execution, and scheduling tools. ResearchComb will state when one of those tools is unavailable.

## License

ResearchComb is available under the [MIT License](LICENSE).
