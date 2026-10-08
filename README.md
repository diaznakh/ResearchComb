# ResearchComb

An installable research skill that works inside AI chats. It plans, gathers, reviews, writes, and verifies research. It has no background server, separate app window, API key, or paid service.

The skill uses the AI host's existing browsing and file tools to find papers on Crossref, OpenAlex, Semantic Scholar, PubMed, Europe PMC, alphaXiv, arXiv, bioRxiv, and medRxiv, and to inspect public GitHub and Hugging Face pages. It verifies citations against the source pages it can open.

The [skill](plugins/researchcomb/skills/researchcomb/SKILL.md) guides paper and code auditing, structured peer review, drafts, claim verification, local replication, and monitoring. Execution and schedules require the AI host's own tools and the user's chosen environment.

## Install

In Codex, install from GitHub:

```sh
codex plugin marketplace add diaznakh/ResearchComb
codex plugin add researchcomb@researchcomb
```

In ChatGPT desktop Work mode, open the repository as a project, restart the app, then choose **Plugins → ResearchComb → Install**. A public ChatGPT web listing would require separate plugin publication.

For another Agent Plugins-compatible host, install `plugins/researchcomb`. For a skill-only host, import its `SKILL.md`. Support and tool access vary by host. A host without browsing cannot fetch new papers; a host without local execution cannot run replications; a host without scheduling cannot monitor in the background.

Try: “Use ResearchComb to find recent papers on retrieval-augmented generation, compare their findings, inspect linked code, and give verified DOI links.”

## License

ResearchComb is available under the [MIT License](LICENSE).
