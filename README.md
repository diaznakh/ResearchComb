# ResearchComb

ResearchComb is a free, MIT-licensed research skill for AI assistants. It helps find papers and citations, inspect linked code, draft reports, review weaknesses, and check claims against sources. It uses the assistant's existing tools; there is no server, API key, or paid service to configure.

## Install by asking your AI

Paste this into a coding agent with GitHub access and permission to install local skills, such as Codex, Claude Code, Gemini CLI, or Antigravity:

> Install ResearchComb from https://github.com/diaznakh/ResearchComb for my user account. Read `skills/researchcomb/SKILL.md`, place that skill in your native user-level skills directory, and verify it appears in your available skills. Use the repository's native plugin or extension format if your host supports direct GitHub installation. Do not run scripts from the repository. If you cannot install skills from this chat, tell me the exact manual step for this host.

The skill itself is [skills/researchcomb/SKILL.md](skills/researchcomb/SKILL.md). An agent can copy that directory into its user skills location. Installation may require the host's normal approval for fetching a GitHub repository or writing to its skills directory.

## Native package formats

- **Gemini CLI:** `gemini extensions install https://github.com/diaznakh/ResearchComb` installs the repository as an extension with the same skill.
- **Claude Code:** The repository includes `.claude-plugin/plugin.json` and `skills/researchcomb/`. An agent can install the skill into `~/.claude/skills/researchcomb/` directly from GitHub.
- **Codex:** An agent can install the skill into `~/.codex/skills/researchcomb/` directly from GitHub. The repository also includes a portable `plugin.json` for clients that support Agent Plugins.
- **Antigravity:** An agent can install the skill into `~/.gemini/config/skills/researchcomb/` or a project's `.agent/skills/researchcomb/`.

Codex and Claude Code also support plugin installation from this GitHub repository through their built-in marketplace commands. Those commands register this repository as the source; they do not require a third-party marketplace listing. The chat prompt above uses each host's skill directory when a direct plugin command is unavailable.

Browser-only chats can use the linked skill as instructions during a conversation, but they cannot persistently install files unless their host exposes a skill or plugin installation feature. Live paper search, code execution, and background monitoring depend on the host's available tools.

Try: “Use ResearchComb to find recent papers on retrieval-augmented generation, compare their findings, inspect linked code, and give verified DOI links.”

## License

ResearchComb is available under the [MIT License](LICENSE).
