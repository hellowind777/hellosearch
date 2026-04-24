---
name: hellosearch
description: Host-agnostic real-web research, source verification, and evidence synthesis using the current environment's native search and page tools. Use when a task needs live web search, latest fact checking, official-document lookup, news or product research, release-note or changelog verification, source-backed comparison, documentation-site mapping, or any answer that should cite current web sources; also use when the user says “use hellosearch”, “用 hellosearch 搜”, “帮我搜一下”, “查官网确认”, or asks to verify what is true now without adding third-party APIs or backends.
---

# HelloSearch

## Overview

Use the current host's real web capability to run disciplined search workflows without assuming any fixed vendor backend or third-party search service.

Treat `hellosearch` as a pure skill. It should guide and structure how the host searches the web, not introduce extra integration layers or backend requirements.

## Workflow

### 1. Detect the live-search path

- Prefer the current host's native web search tool when available.
- Pair native search with native page open or fetch tools when the question needs full-page context.
- Use site mapping when the task asks for all docs pages, site structure, endpoint inventories, or broad documentation coverage.
- If no real web path exists, say so clearly and stop claiming live verification.
- Read `references/host-routing.md` when the backend choice is unclear.

### 2. Frame the query before searching

- Distill the core question, required freshness, target geography, likely primary sources, and whether the task needs mapping before fetching.
- Rewrite broad asks into concrete search rounds and sub-queries before searching.
- Turn relative dates such as “today”, “latest”, or “this week” into exact dates in both the search and the answer.
- Add domain filters when official docs, standards bodies, vendors, or repositories exist.
- For complex or time-sensitive tasks, run `python scripts/plan_search.py "<question>" --json` first and use the generated complexity, sub-queries, and execution order as your checklist.

### 3. Search broad, then narrow

- Start with broad discovery queries to map the landscape.
- Follow with targeted queries against official docs, release notes, repos, changelogs, standards, filings, or primary reporting.
- If the task is documentation-wide, use site mapping first, then fetch the most relevant pages.
- For technical topics, search English first unless the task is clearly China-local or the source of truth is Chinese.
- For comparisons, collect the same facts for each option before judging.

### 4. Fetch, verify, and reconcile

- Open or fetch the strongest sources instead of answering from snippets alone.
- Cross-check unstable or high-stakes claims across multiple independent sources.
- Reconcile conflicts in titles, dates, versions, and pricing before answering.
- If the host returns mixed answer-plus-citation text, run `python scripts/extract_sources.py --input answer.md` or pipe the text through the script before ranking.
- Treat official docs, release notes, standards, repos, and direct statements as higher priority than summaries or reposts.
- Read `references/evidence-policy.md` when the answer needs stronger source discipline.
- After collecting candidate sources, run `python scripts/rank_sources.py "<question>" --input sources.json` to dedupe and rank them before synthesis.

### 5. Synthesize the answer

- Lead with the best-supported conclusion.
- Separate confirmed facts, reasonable inference, and unresolved uncertainty.
- Include direct links when the host allows them.
- Mention exact dates for time-sensitive facts.
- Name the source type when it helps the user judge confidence.

## Guardrails

- Do not rely on model memory for unstable facts.
- Do not pretend a generic `chat/completions` model has real web access unless the environment actually provides it.
- Do not turn this skill into a vendor-specific wrapper or backend-dependent shortcut.
- Do not hide missing evidence, ambiguity, backend limits, or site-map gaps.
- Do not answer from a single snippet when the task requires page-level context.

## Trigger examples

- “用 hellosearch 搜一下这个库最近的 breaking changes”
- “Use hellosearch to verify today's NVIDIA news”
- “查官网文档，确认这个 API 现在的参数”
- “Use hellosearch to map this docs site before answering”
- “用 hellosearch 比较这三个产品，给出处和更新时间”

## Resources

- Run `scripts/detect_runtime.py` to inspect the current workspace and choose the first routing target.
- Run `scripts/plan_search.py "<question>" --json` to generate one structured search plan with complexity, sub-queries, and execution order.
- Run `scripts/build_workflow.py "<question>"` to generate one combined routing + workflow bundle.
- Run `scripts/extract_sources.py --input answer.md` when host output mixes answer text with trailing citations or raw links.
- Read `references/host-routing.md` when deciding which search path to use in Codex, Claude Code, or OpenClaw.
- Read `references/evidence-policy.md` when ranking sources, handling freshness, parsing mixed citation blocks, or formatting a source-backed answer.
- Read `references/runtime-adapters.md` when implementing or extending a host-agnostic search backend.
