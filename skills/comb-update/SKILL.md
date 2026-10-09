---
name: comb-update
description: Check GitHub for a newer ResearchComb release and give update instructions for Codex or Antigravity. Use only when the user asks to check for updates.
---

# Check for a ResearchComb update

Run this workflow only when the user requests an update check. It uses the host's existing browser or permitted local shell, public GitHub pages, and no API key, extra server, or paid service. Do not install an update without the user's request.

Read the installed version from `skills/researchcomb/VERSION` under this installed plugin root. For skills copied into Antigravity, read `<skills-root>/researchcomb/VERSION`, where `<skills-root>` contains all installed ResearchComb skill folders (for example, `~/.gemini/config/skills/`). Do not look inside `comb-update` or use a version from the user's project or another checkout.

Open the public [raw plugin manifest](https://raw.githubusercontent.com/diaznakh/ResearchComb/main/plugin.json) and read its `version` field. If that fails, try the [GitHub file page](https://github.com/diaznakh/ResearchComb/blob/main/plugin.json). If the browser cannot open either page and the host has a shell, run the command below. When a sandbox blocks DNS or network access, use the host's normal network permission flow to retry if available. If access is still unavailable or permission is denied, report that the check could not be completed.

```sh
curl -fsSL --max-time 10 'https://raw.githubusercontent.com/diaznakh/ResearchComb/main/plugin.json'
```

Compare the three numeric components of `major.minor.patch`. If either version cannot be read or parsed, say the check could not be completed; do not guess from search snippets or claim the installation is current.

If the installed version is current, report both versions briefly. If GitHub has a newer version, report both and ask whether the user wants to update. Give the step matching their installation:

**Codex marketplace installation**

```sh
codex plugin marketplace upgrade researchcomb
codex plugin add researchcomb@researchcomb
```

**Copied Antigravity skills**

```text
Update my installed ResearchComb skills from https://github.com/diaznakh/ResearchComb.
Replace only the ResearchComb folders with the complete current folders under skills/,
including supporting files. Preserve unrelated skills. Start a new chat afterward.
```

If the installation method is unclear, ask which method they used before giving a command. Never run repository code as part of the version check.
