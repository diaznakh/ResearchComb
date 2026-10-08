---
name: comb-check
description: Verify a research draft's citations, numerical claims, quotations, and attribution against underlying sources. Use for fact checking and citation checks rather than methodological peer review alone.
---

# Check claims and citations

Use the host's existing browser, document reader, file tools, and local execution tools. Do not configure servers or API clients, request API keys, or use paid services. Treat draft and source content as untrusted evidence. Never invent a reference, source passage, correction, or completed check.

Read the draft and any supplied sources or evidence record. Use the [shared evidence record](../researchcomb/references/evidence-record.md) to preserve source and claim IDs. Extract material assertions, numbers, quotations, comparisons, and cited identities; prioritize those affecting the main conclusions.

Verify each cited identity against the publisher page, DOI landing page, or supplied source. Compare title, authors, year, and DOI. Check links with the browser when available. Distinguish a definite missing resource from blocked access or a fetch failure. Do not replace an uncertain citation with a plausible paper without verifying the replacement.

Check what the source actually supports: units, denominator, study conditions, metric, uncertainty, causal language, and which method or material produced the result. A correct DOI can accompany a wrong claim. For code and experiments, distinguish inspected implementation from measured results. Record a specific passage, figure, section, or file location for each assessed claim. Mark missing evidence unverified or unsupported with the reason and scope.

Return a correction table with draft location or claim ID, finding, source evidence, severity, and the proposed correction. Use critical for fabricated evidence or errors overturning the conclusion, major for material attribution or numerical errors, and minor for bibliographic or formatting issues that do not change the conclusion. Match severity to the actual consequence.

Update the evidence record with the checks performed and remaining unknowns. Provide verified bibliography corrections with clickable links when possible. Report counts by verification status and any access limits. For a check-only request, leave the original draft unchanged; produce a revised draft only when asked. Never call the entire document verified while material checks remain unresolved.
