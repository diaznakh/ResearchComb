# Synthetic reproducibility study

This is a local regression fixture, not an actual publication. It has no DOI.

The study reports a binary classifier with these conditions:

- **T1:** The training batch size is 32.
- **T2:** The dropout setting is 0.1.
- **T3:** Evaluation uses only the held-out test split.
- **T4:** The random seed is 42.

This paper does not report a measured accuracy. Inspect the companion configuration
and evaluation code to assess these claims. Do not run or edit the study code.
