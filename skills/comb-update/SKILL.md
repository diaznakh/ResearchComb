---
name: comb-update
description: Check GitHub for a newer ResearchComb release and give update instructions for Codex or Antigravity. Use only when the user asks to check for updates.
---

# Check for a ResearchComb update

Run this workflow only when the user requests an update check. It uses the host's existing browser or permitted local shell, public GitHub pages, and no API key, extra server, or paid service. Do not install an update without the user's request.

Read the installed version from `skills/researchcomb/VERSION` under this installed plugin root. For skills copied into Antigravity, read `<skills-root>/researchcomb/VERSION`, where `<skills-root>` contains all installed ResearchComb skill folders (for example, `~/.gemini/config/skills/`). Do not look inside `comb-update` or use a version from the user's project or another checkout.

Open the public [GitHub raw file](https://github.com/diaznakh/ResearchComb/raw/refs/heads/main/plugin.json) and read its `version` field. If that fails, try the [raw content host](https://raw.githubusercontent.com/diaznakh/ResearchComb/main/plugin.json). If the browser cannot open either URL and the host has a shell, run the commands below in order. When a sandbox blocks DNS or network access, use the host's normal network permission flow to retry if available. If access is still unavailable or permission is denied, report that the check could not be completed.

```sh
curl -fsSL --max-time 10 'https://github.com/diaznakh/ResearchComb/raw/refs/heads/main/plugin.json'
curl -fsSL --max-time 10 'https://raw.githubusercontent.com/diaznakh/ResearchComb/main/plugin.json' # only if the first fails or reports an older version
```

Compare the three numeric components of `major.minor.patch`. If both branch URLs report an older version than installed, they may be cached. If the host has a permitted shell, get the current main commit with `git ls-remote https://github.com/diaznakh/ResearchComb.git refs/heads/main`, then open `https://raw.githubusercontent.com/diaznakh/ResearchComb/<40-character-commit-hash>/plugin.json` using the hash actually returned. Do not invent a hash or run repository code. If this lookup fails, report the check as inconclusive; do not claim the installation is current. If either version cannot be read or parsed, say the check could not be completed; do not guess from search snippets.

If the installed version is current, report both versions briefly. If GitHub has a newer version, resolve the matching `v<latest-version>` tag to its full 40-character commit SHA with `git ls-remote https://github.com/diaznakh/ResearchComb.git 'refs/tags/v<latest-version>^{}'` (use the tag ref itself if lightweight). Verify that the manifest at that commit reports the same version. If the tag or commit cannot be verified, report the update as unverified and do not present an install command. Otherwise report both versions and ask whether the user wants to update. Use the verified SHA in the matching step:

**Codex marketplace installation**

```sh
codex plugin marketplace remove researchcomb
codex plugin marketplace add https://github.com/diaznakh/ResearchComb.git --ref VERIFIED_COMMIT_SHA
codex plugin add researchcomb@researchcomb
```

**Copied Antigravity skills**

```text
Update my installed ResearchComb skills from the verified commit VERIFIED_COMMIT_SHA at https://github.com/diaznakh/ResearchComb.
Replace only the ResearchComb folders with the complete folders under skills/ at that commit,
including supporting files. Preserve unrelated skills. Start a new chat afterward.
```

If the installation method is unclear, ask which method they used before giving a command. Never run repository code as part of the version check.
