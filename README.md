# HelloSearch

A research discipline for AI agents — not a pipeline, not a backend. HelloSearch teaches your agent to size the effort to the question, search past the first convenient result, verify claims against sources instead of memory, and deliver answers with citations that hold up.

[![npm version](https://img.shields.io/npm/v/hellosearch)](https://www.npmjs.com/package/hellosearch)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](./LICENSE)

[English](./README.md) · [简体中文](./README_CN.md) · [Changelog](./CHANGELOG.md)

## Overview

- **Pure instructions.** The package contains a `SKILL.md` and three reference documents. No backend, no runtime scripts, no Python. Research is a judgment task, and judgment belongs to the model; code is reserved for what must be deterministic — here, only installation and validation.
- **Host-agnostic by construction.** The skill follows the open [Agent Skills specification](https://agentskills.io/specification) and names capabilities, not tools. It works with whatever the host provides: web search, page fetching, browser control, site mapping, subagents.
- **One package, many hosts.** The same files load in Claude Code, Claude.ai, OpenAI Codex, OpenClaw, Gemini CLI, Cursor, and other hosts that support Agent Skills. The npm installer writes the skill into the right directory for each host.

## What it changes

| Without the skill | With the skill |
| --- | --- |
| Answers built from search snippets | Decisive pages are opened and read before they support a claim |
| First-page results taken at face value | Claims traced to primary sources; volatile facts need two independent sources |
| "Latest" and "current" without dates | Relative time resolved to concrete dates, with retrieval dates on fast-moving facts |
| The user's premise researched as stated | The premise itself verified first |
| Every answer forced into one report template | Answer shape matches the question: direct answer, matrix, timeline, or report |
| Confident wording over thin evidence | Confirmed facts, inferences, and open uncertainty kept distinguishable |

## Install

### From npm

```bash
npm install -g hellosearch
hellosearch install              # detect the most likely host and install
hellosearch install --host all   # install for every host detected on this machine
```

Host presets:

| `--host` | User scope | Project scope |
| --- | --- | --- |
| `claude-code` | `~/.claude/skills` | `.claude/skills` |
| `codex` / `agents` | `~/.agents/skills` | `.agents/skills` |
| `openclaw` | `~/.openclaw/skills` | `<workspace>/skills` |

`~/.agents/skills` is the cross-vendor location also read by OpenClaw and Gemini CLI. Use `--scope project` for workspace installs, `--target <path>` for a custom directory, and `--force` to overwrite an existing copy.

Inspect before installing, or verify afterwards:

```bash
hellosearch info     # print the resolved install plan
hellosearch doctor   # install plan plus package validation checks
```

### Other routes

- Via the skills CLI: `npx skills add hellowind777/hellosearch`
- Manually: copy `SKILL.md`, `references/`, and `agents/` into any skills directory your host reads.

## Use

Once installed, the skill triggers on research-shaped requests without being named:

- `What are the current stable release and breaking changes for Bun's SQLite API? Use official sources.`
- `Compare these three vector databases on pricing and license, with sources.`
- `这条新闻是真的吗？帮我核实一下，给出处。`
- `Map the docs site first, then find the current rate-limit rules.`

Name it explicitly (`use hellosearch to ...` / `用 hellosearch 查 ...`) when you want the discipline applied to a request that might not look like research.

## Package layout

| Path | Purpose |
| --- | --- |
| `SKILL.md` | The skill: trigger description plus six research disciplines. |
| `references/verification.md` | Source hierarchy, freshness rules, counter-evidence technique, citation audit. |
| `references/scenarios.md` | Patterns for common single and composite research tasks. |
| `references/delivery.md` | Answer shapes, citation presentation, uncertainty wording. |
| `agents/openai.yaml` | Display metadata for hosts that read agent descriptors. |
| `evals/` | Behavior scenarios and trigger test set. |
| `bin/`, `lib/` | The npm installer and package validation. |
| `node-tests/` | Tests for the installer and the package constraints. |

## Quality

```bash
npm test        # installer behavior and package constraints
npm run doctor  # frontmatter, size, and structure validation
```

`evals/evals.json` holds six behavior scenarios with verifiable expectations, each targeting a documented failure mode of unassisted research (answering from snippets, uneven comparisons, accepted false premises, undated claims, rumor presented as fact). `evals/triggers.json` holds a should-trigger / should-not-trigger set for tuning the description. Both follow the schema used by Anthropic's skill-creator workflow, so they can be run and graded with standard tooling.

## License

[Apache-2.0](./LICENSE)
