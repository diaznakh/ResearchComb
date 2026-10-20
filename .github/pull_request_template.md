## Summary

<!-- What changed and why. -->

## Test plan

- [ ] `python3 -m unittest discover -s tests -p 'test_*.py'`

## Checklist

- [ ] Changes stay focused on the stated problem.
- [ ] Skill edits keep `SKILL.md` frontmatter (`name`, `description`) and reuse the shared evidence record when the workflow handles sources or claims.
- [ ] A new `comb-*` skill is named `comb-<verb>`, uses host tools only, and does not add a ResearchComb server or API key.
- [ ] `evidence.json` fields, enums, and completion-gate rules are unchanged unless this PR updates `evidence-record.md` and `evidence.schema.json` together.
- [ ] `safe_fetch.py` security behavior is not weakened.
- [ ] README edits are limited to install pins, workflow lists, badges, or the recorded local-checker count.
- [ ] User-visible changes have a factual `[Unreleased]` note in `CHANGELOG.md`.
