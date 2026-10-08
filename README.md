# ResearchComb

ResearchComb is a free, MIT-licensed research skill for **Codex, ChatGPT, and Antigravity**. It helps find papers and citations, inspect linked code, draft reports, review weaknesses, and check claims against sources. It uses the host's existing tools; there is no ResearchComb server, API key, or paid service to configure.

The package contains one [researchcomb skill](skills/researchcomb/SKILL.md), a portable [plugin manifest](plugin.json), and a [Codex/ChatGPT marketplace](.agents/plugins/marketplace.json). No scripts run during installation.

## Install from GitHub

In an agent with GitHub and local file access, paste:

> Install ResearchComb from https://github.com/diaznakh/ResearchComb for my account. Use your native plugin installer if it accepts this GitHub repository; otherwise copy `skills/researchcomb/` into your user skills directory. Confirm that `researchcomb` appears in your available skills. Do not run repository code.

The host may ask you to approve GitHub access or a local file write. A link by itself may only open or summarize the repository; use the instruction above to request installation.

### Codex

For the plugin in Codex CLI or the ChatGPT desktop app, register this repository as a marketplace, then install `researchcomb@researchcomb`:

```text
codex plugin marketplace add https://github.com/diaznakh/ResearchComb.git
codex plugin add researchcomb@researchcomb
```

Start a new chat and ask Codex to use ResearchComb, or select its skill with `$researchcomb`. If plugin installation is unavailable, ask `$skill-installer` to install `skills/researchcomb/` from this repository.

### ChatGPT

In the **ChatGPT desktop app**, add this repository as a personal plugin marketplace using the Codex command above, restart the app, and install ResearchComb from the Plugins Directory. Then start a new Chat or Work conversation and select `@researchcomb` or ask for a research task.

For a **ChatGPT workspace**, an admin can import `https://github.com/diaznakh/ResearchComb` under **Admin → Plugins → Add → Import marketplace**. The marketplace file is `.agents/plugins/marketplace.json`. After the admin makes the plugin available, members can install it in ChatGPT on the web, desktop, or mobile. A regular ChatGPT web chat cannot persistently install an unpublished plugin just because you paste a GitHub URL. Public directory installation would require a separate plugin submission and review.

### Antigravity

In the Antigravity IDE, ask its agent to copy `skills/researchcomb/` from this repository to `~/.gemini/config/skills/researchcomb/` for all workspaces, or `<workspace-root>/.agents/skills/researchcomb/` for one workspace. Check **Customizations → Skills** or ask which skills are available. Antigravity CLI can also install the GitHub package with:

```text
agy plugin install https://github.com/diaznakh/ResearchComb
```

## Use

Try: “Use ResearchComb to find recent papers on retrieval-augmented generation, compare their findings, inspect linked code, and give verified DOI links.”

Live paper search, code execution, and background monitoring depend on the host's available browsing, execution, and scheduling tools. ResearchComb will state when one of those tools is unavailable.

## License

ResearchComb is available under the [MIT License](LICENSE).
