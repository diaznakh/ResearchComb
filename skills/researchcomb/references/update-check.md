# Check for ResearchComb updates

On the first ResearchComb workflow use in a new chat, check once for a newer release. Remember in this chat that the attempt was made; later ResearchComb workflows in the same chat must not repeat it. Do not create a persistent cache or interrupt the user's research task. A new chat starts a new check. A resumed chat may retain its earlier check even after an app restart.

1. Read the installed version from `../VERSION` in this installed skill folder. Do not use a version from the user's project or an unrelated ResearchComb checkout.
2. If the user requested offline or supplied-source-only work, or the host has no browsing, skip the remote check. Otherwise open `https://raw.githubusercontent.com/diaznakh/ResearchComb/main/plugin.json` with the host's existing browser. If raw GitHub access fails, try `https://github.com/diaznakh/ResearchComb/blob/main/plugin.json` and read its displayed file contents. These are public GitHub pages; no API key or ResearchComb server is needed.
3. Read the remote `version` field only if the file was retrieved successfully. Compare the three numeric components of `major.minor.patch`. If either version cannot be read or parsed, continue the task without claiming that the installation is current.
4. Only when the remote version is newer, briefly tell the user the installed and available versions and show the update step for the current host. Continue the requested workflow unless the user asks to update now. Do not auto-install.

For a Codex marketplace installation, show:

```sh
codex plugin marketplace upgrade researchcomb
codex plugin add researchcomb@researchcomb
```

For copied Antigravity skills, show this prompt:

```text
Update my installed ResearchComb skills from https://github.com/diaznakh/ResearchComb.
Replace only the ResearchComb folders with the complete current folders under skills/,
including their supporting files. Preserve unrelated skills. Start a new chat afterward.
```

If the installation method is uncertain, give the matching instructions from the repository's README or ask which method was used. Never report an update based on a failed fetch, a search snippet, or an unverified version.
