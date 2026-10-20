# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses three-part version numbers of the form `major.minor.patch`
as stored in `plugin.json` and `skills/researchcomb/VERSION`.

Entries below are taken from git history and the GitHub Releases for tags
`v0.5.21`, `v0.5.22`, and `v0.5.23`. Dates are the annotated-tag dates.

## [Unreleased]

### Added

- Keep a Changelog covering tags `v0.5.21`, `v0.5.22`, and `v0.5.23` from git
  history and the GitHub Releases for those tags.
- Live GitHub Actions status badge for `.github/workflows/test.yml` in the README
  header.
- `CONTRIBUTING.md`, `.github/ISSUE_TEMPLATE/` issue forms, and
  `.github/pull_request_template.md`.
- Draft 2020-12 JSON Schema for `evidence.json` at
  `skills/researchcomb/references/evidence.schema.json`, linked from
  `evidence-record.md`, with a standard-library test that validates every fixture
  `evidence.json`. Closed objects (`source`, `claim`, evidence items, search
  entries, citation trails, trail leads, and search rounds) set
  `additionalProperties` to false. Schema tests cross-check with `jsonschema`
  when that library is importable and include invalid evidence fixtures.

### Changed

- Pin README install instructions to ResearchComb `v0.5.23` at commit
  `c43d1dcaef4d930c463fe51ab31ae60a1999fc73` ([#4](https://github.com/diaznakh/ResearchComb/pull/4)).
- Reframe `comb-paper` for academic integrity: remind users to check institutional
  policy, refuse producing a finished coursework essay for submission, and append
  an `## AI Assistance Disclosure` section ([#5](https://github.com/diaznakh/ResearchComb/pull/5),
  [#6](https://github.com/diaznakh/ResearchComb/pull/6)).
- Rewrite focused-workflow descriptions in ResearchComb's own voice
  ([#7](https://github.com/diaznakh/ResearchComb/pull/7)).
- Update the README local-checker count to 32 after adding a disclosure word-count
  test ([#6](https://github.com/diaznakh/ResearchComb/pull/6)).

## [0.5.23] - 2026-10-11

GitHub Release: [ResearchComb v0.5.23](https://github.com/diaznakh/ResearchComb/releases/tag/v0.5.23).

Merged pull requests listed on that release:

- [#1](https://github.com/diaznakh/ResearchComb/pull/1) Fix word counting, HTTP headers, stale docs, test coverage, and add 3 owner-approved features
- [#2](https://github.com/diaznakh/ResearchComb/pull/2) Release v0.5.23: Fix proxy support, accept HTTP 2xx, improve guidance
- [#3](https://github.com/diaznakh/ResearchComb/pull/3) Security hardening: DNS rebinding fix, API etiquette, prompt injection guidance, CI

### Added

- Opt-in sandbox/proxy fetch mode (`--allow-private` / `RESEARCHCOMB_ALLOW_PRIVATE=1`)
  that honours `HTTP_PROXY`, `HTTPS_PROXY`, and `NO_PROXY` and allows non-global
  resolved addresses; record `"fetch_mode": "allow_private"` on the source when used.
- `tests/local_proxy.py` helper for CONNECT-proxy testing.
- Search checker acceptance of API hosts for Crossref (`api.crossref.org`),
  OpenAlex (`api.openalex.org`), Semantic Scholar (`api.semanticscholar.org`),
  Europe PMC (`www.ebi.ac.uk/europepmc`), and PubMed (`eutils.ncbi.nlm.nih.gov`).
- PASS line that reports searched, inaccessible, and unavailable counts separately.
- `comb-check` steps to identify document version (preprint, accepted manuscript,
  version of record) and compare a DOI's reference list with Crossref metadata.
- Optional evidence-record fields documented in the source table: `checked_date`,
  `source_type`, `commit`, `version`, and `reference_issues`.
- `comb-paper` case in `tests/check_results.py`.
- GitHub Actions workflow `.github/workflows/test.yml` (push and pull request to
  `main`, Python 3.11, `python3 -m unittest discover -s tests -p 'test_*.py'`,
  `contents: read`, actions pinned by commit SHA).
- `SECURITY.md` with private vulnerability reporting, supported versions, scope,
  and known limitations.
- Prompt-injection guidance: treat fetched pages, PDFs, repositories, and search
  results as untrusted data, not instructions.
- API etiquette notes in the search-source guide (Crossref `mailto`, OpenAlex API
  key after the polite-pool change, NCBI rate limits, Semantic Scholar limits,
  backoff on HTTP 429).

### Changed

- Manuscript word counting strips table pipe characters and recognizes additional
  bibliography heading aliases, including Works Cited.
- `safe_fetch.py` sends `User-Agent: ResearchComb`.
- Documentation skill and test counts updated to thirteen workflow skills.
- Root `.gitignore` patterns anchored so tracked fixtures such as
  `tests/fixtures/workflows/evidence.json` are not ignored.
- Version set to `0.5.23` in `plugin.json` and `skills/researchcomb/VERSION`.

### Fixed

- `safe_fetch.py` proxy support, including HTTPS targets through an HTTP CONNECT
  proxy; HTTPS proxy URLs remain rejected.
- HTTP 2xx responses accepted (not only 200).
- Stub detection and temporary-file handling in `safe_fetch.py`.
- Proxy environment variables no longer disable private-address checks outside
  opt-in mode.
- Europe PMC direct URLs must use the `/europepmc` path prefix.
- README and other stale documentation corrections from the v0.5.23 release
  commits.

### Security

- Connections pin to the validated address after DNS (including `--allow-private`
  non-proxy paths) to prevent DNS rebinding.
- `--allow-private` continues to block loopback (`127.0.0.0/8`, `::1`), link-local
  / cloud metadata (`169.254.0.0/16`, `fe80::/10`), and unspecified addresses
  (`0.0.0.0/8`, `::`). The unspecified-address block covers the full `0.0.0.0/8`
  range, not only `0.0.0.0`.

## [0.5.22] - 2026-10-09

GitHub Release: [ResearchComb v0.5.22](https://github.com/diaznakh/ResearchComb/releases/tag/v0.5.22)
(compare link only: [v0.5.21...v0.5.22](https://github.com/diaznakh/ResearchComb/compare/v0.5.21...v0.5.22)).

### Changed

- `comb-critique` requires checking each central claim against its main-text
  location, accessible supplementary material, and the cited source; classify
  findings as demonstrated error, unsupported claim, or concern needing a check;
  add ML-specific inspection items; and end with an inspection inventory of
  supplementary material, data, code, and cited sources.
- Version set to `0.5.22` in `plugin.json` and `skills/researchcomb/VERSION`.
- README install pin updated to `v0.5.22`.

## [0.5.21] - 2026-10-09

GitHub Release: [ResearchComb v0.5.21](https://github.com/diaznakh/ResearchComb/releases/tag/v0.5.21)
(compare link only: [v0.5.20...v0.5.21](https://github.com/diaznakh/ResearchComb/compare/v0.5.20...v0.5.21)).

### Added

- `paper-search` mode in `check_completion.py` for open-ended `comb-paper`
  discovery.
- Evidence-record `citation_trails`, `trail_leads`, and `search_rounds` for
  paper search: trail `kind` is `references`, `cited_by`, or `related`; trail
  `outcome` is `screened` or `inaccessible` (with a reason when inaccessible);
  each trail lead has a title and status `included` (with `source_id`),
  `excluded` (with a reason), or `inaccessible`; each search round has a
  nonnegative `new_relevant` count, and the final count is zero only after
  screening encountered relevant leads.
- Completion-gate tests that require all eleven scholarly source attempts and
  screened citation trails.

### Changed

- Open-ended `comb-paper` discovery attempts every scholarly source in the search
  guide (with a separate `site:` fallback when direct search fails), screens
  backward references and forward or related-paper trails, queues encountered
  relevant leads, and continues until a further round yields no new relevant
  leads. A five-paper checker PASS is only a floor. Inaccessible trails or leads
  fail the paper completion gate.
- Version set to `0.5.21` in `plugin.json` and `skills/researchcomb/VERSION`.
- README install pin updated to `v0.5.21`.

[Unreleased]: https://github.com/diaznakh/ResearchComb/compare/v0.5.23...HEAD
[0.5.23]: https://github.com/diaznakh/ResearchComb/compare/v0.5.22...v0.5.23
[0.5.22]: https://github.com/diaznakh/ResearchComb/compare/v0.5.21...v0.5.22
[0.5.21]: https://github.com/diaznakh/ResearchComb/compare/v0.5.20...v0.5.21
