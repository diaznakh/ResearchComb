# Source A: CPU threshold classifier

Synthetic regression excerpt, not an actual publication. Supplied identity:
ResearchComb Tests, 2024. No DOI. Source ID: S-A. Access: excerpt.

On a held-out set of 100 examples with equal positive and negative classes,
Method A achieves 90% accuracy. The majority-class baseline achieves 50%.
Only one deterministic evaluation is reported; there are no confidence intervals
or repeated runs. The study does not establish a causal or universal advantage.

The implementation is a threshold rule on a numeric feature. It uses CPU-only
Python and the standard library, with no model downloads or additional packages.
The companion demonstration benchmark is MIT-licensed synthetic code; its six
examples are a separate fixture, not the study's 100-example evaluation set.
