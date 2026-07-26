# Changelog

All notable changes to HelloSearch are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] — 2026-07-26

### Changed
- Bumped package version for npm distribution alignment.

## [1.0.0] — 2026-07-26

### Removed
- **Entire Python runtime** (~2100 lines): `scripts/`, `tests/`, `scripts/hellosearch_runtime/` — query-classification heuristics, template-based sub-query generators, regex citation parsers, URL-based source scoring, file-system host detection, and the adapter/router skeleton layer.
- `references/evidence-policy.md`, `references/host-routing.md`, `references/runtime-adapters.md` — replaced by new reference documents.
- Python dependencies from `package.json`.

### Added
- **Pure-instruction SKILL.md** rewritten with six research disciplines: calibrate, scale effort, search craft, verify, consolidate, deliver.
- `references/verification.md` — source hierarchy, freshness rules, counter-evidence technique, conflict resolution, citation audit checklist.
- `references/scenarios.md` — patterns for 7 single-focus and 5 composite research tasks.
- `references/delivery.md` — answer shapes, citation presentation, uncertainty wording, coverage statements.
- `evals/evals.json` — 6 behavior scenarios with verifiable expectations.
- `evals/triggers.json` — 20 trigger test cases (10 should-trigger, 10 should-not-trigger).
- `node-tests/skill-package.test.mjs` — package constraints and validation test suite.
- `.github/workflows/test.yml` — CI workflow for main branch and PRs.
- `LICENSE` — Apache-2.0.
- `REFACTOR_PLAN.md` — full rationale and design decisions behind the v1.0.0 transformation.

### Changed
- **Installer** (`bin/hellosearch.mjs`, `lib/install-skill.mjs`): added `--host agents` preset (cross-vendor), `--host all` (install everywhere), enhanced `doctor` with full validation suite, updated detection priority.
- **npm publish workflow** (`.github/workflows/npm-publish.yml`): made idempotent with pre-publish registry check.
- `.gitignore` and `.npmignore`: updated to exclude legacy directories and include new paths.
- `package.json`: removed Python scripts, updated `files` field, bumped to v1.0.0.
- `agents/openai.yaml`: updated display metadata.

## [0.1.0] — 2026-07-23

### Added
- Initial release with Python-based runtime pipeline (`scripts/`, `tests/`).
- `SKILL.md` with script-execution workflow.
- `references/evidence-policy.md`, `references/host-routing.md`, `references/runtime-adapters.md`.
- npm installer (`bin/hellosearch.mjs`, `lib/install-skill.mjs`) with host detection.
- `agents/openai.yaml` display metadata.
- npm publish CI workflow.

[1.0.1]: https://github.com/hellowind777/hellosearch/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/hellowind777/hellosearch/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/hellowind777/hellosearch/releases/tag/v0.1.0
