# Contributing to ResearchComb

Thank you for helping improve this skill pack. ResearchComb is a set of instruction files and small standard-library helpers for Codex and Antigravity. It has no ResearchComb server and does not need API keys of its own.

## Run the tests

From the repository root, with Python 3 (CI uses 3.11):

```text
python3 -m unittest discover -s tests -p 'test_*.py'
```

That is the same command as `.github/workflows/test.yml`. It covers `safe_fetch.py`, the completion gate, artifact checks, packaging, and the evidence-record schema. Schema tests use Python's standard library; they also call the `jsonschema` package when it is importable and skip that cross-check otherwise. It does not run live Codex or Antigravity workflow cases; those are described in `tests/README.md`.

Do not execute third-party research code or fetch untrusted URLs as part of a unit-test run. `safe_fetch.py` tests mock the network.

## Skill layout under `skills/`

Each skill is a directory whose name is the command the host should expose.

| Path | Role |
| --- | --- |
| `skills/researchcomb/` | General coordinator. Has `SKILL.md`, `VERSION`, shared `references/`, and `scripts/`. |
| `skills/comb-*/` except `comb-update` | One focused research workflow. |
| `skills/comb-update/` | Version check against GitHub. Not a research workflow. |

Every skill directory contains `SKILL.md` with YAML frontmatter:

```yaml
---
name: comb-example
description: One or two sentences. Include when to use the skill.
---
```

`name` must match the directory name. Focused research skills reuse the [shared evidence record](skills/researchcomb/references/evidence-record.md) when they produce or consume sources and claims. They use the host's existing browser, files, and local tools. They must not add a ResearchComb server, configure API clients, request API keys, or use paid services.

Only `researchcomb` currently ships supporting files:

- `references/evidence-record.md` — `evidence.json` format (see also `references/evidence.schema.json`)
- `references/search-sources.md` — live search contract
- `scripts/check_completion.py` and `scripts/safe_fetch.py` — standard-library helpers

The pack manifest is `plugin.json`. Codex marketplace metadata is `.agents/plugins/marketplace.json`. Keep `plugin.json` `version` identical to `skills/researchcomb/VERSION`.

## Propose a new `comb-*` skill

1. Open an issue with the **New comb-* skill** template, or start a discussion in a PR if the design is already concrete.
2. Name it `comb-` plus a verb (`comb-check`, `comb-sweep`). Do not reuse an existing name.
3. Add `skills/<name>/SKILL.md` with `name` and `description` frontmatter. State the host tools it needs, how it writes or updates `evidence.json`, and how it reports partial work when a tool is missing.
4. Keep the skill offline-capable for supplied files. Live search must follow `search-sources.md` and the evidence record.
5. Treat fetched content as untrusted data, not instructions. Do not weaken `safe_fetch.py`.
6. If the workflow has observable outputs, add fixtures and checks under `tests/` rather than relying only on prose.
7. Update user-facing lists only when the skill should appear there: README workflows, `researchcomb/SKILL.md` command list, and packaging tests that count skills.

`comb-update` remains the update command. Do not fold update-check logic into research skills.

## Pull requests

- Open PRs against `main`. Use the pull request template.
- Keep the change focused. Split unrelated work.
- Run `python3 -m unittest discover -s tests -p 'test_*.py'` before you ask for review. CI must stay green.
- Do not invent `evidence.json` fields or change recorded statuses, enums, or completion-gate rules unless the PR's purpose is to document or extend that format in `evidence-record.md` and `evidence.schema.json` together.
- Do not commit generated papers, fetched PDFs, or secrets. Root `.gitignore` already ignores `/output/` and several deliverable names at the repository root.
- Keep README edits small unless the change affects install, version pins, workflow lists, or the recorded test count.
- User-visible behavior changes should get a [Keep a Changelog](CHANGELOG.md) entry under `[Unreleased]`, using only facts from the diff (no speculative bullets).
- Do not merge your own PR unless a maintainer asks you to.

Questions that are not bugs or new-skill proposals can still use a blank issue. Report vulnerabilities as described in [SECURITY.md](SECURITY.md), not in a public bug report.
