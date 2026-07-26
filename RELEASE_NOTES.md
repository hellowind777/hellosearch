# Release Notes — HelloSearch v1.0.1

> v1.0.0 was the major version that completed the transformation from a Python-based pipeline to a pure-instruction research skill. v1.0.1 is a maintenance release that bumps the package version for npm distribution alignment.
>
> These notes cover substantive changes across both releases.

## English

### Breaking: Python runtime removed

The entire Python codebase (~2100 lines across `scripts/`, `tests/`, and `scripts/hellosearch_runtime/`) has been removed. This includes all query-classification heuristics, template-based sub-query generators, regex citation parsers, URL-based source scoring, file-system host detection, and the adapter/router skeleton layer. None of these were providing value that the host model could not perform better on its own.

**Impact**: The skill is now zero runtime scripts and zero Python dependencies. It works fully in hosts without Python or shell access (e.g., claude.ai web). The npm package no longer lists `scripts/` or `tests/` in its payload.

### New: Pure-instruction SKILL.md

SKILL.md was rewritten from a script-execution guide into six research disciplines:

1. **Calibrate before the first search** — classify the question shape, resolve time references, verify the user's premise, confirm scope for large tasks.
2. **Scale effort to the question** — tiered guidance (straightforward: 3–10 calls, comparison: 10–15 per option, deep/broad research: tens of calls) with explicit stopping rules.
3. **Search craft** — wide-then-narrow strategy, angle variation, snippet-vs-page discipline, source judgment by content not domain appearance.
4. **Verify against sources, not against yourself** — claim-level grounding, two-source rule for volatile facts, counter-evidence search, conflict surfacing.
5. **Consolidate or drown** — periodic integration checkpoints every 8–10 sources to prevent context degradation.
6. **Deliver research, not a template** — shape-matched answers (direct, matrix, timeline, report), citation audit, uncertainty layering.

### New: Reference documents

Three reference files replace the old evidence-policy, host-routing, and runtime-adapters docs:

- `references/verification.md` — source hierarchy, freshness rules, counter-evidence technique, conflict resolution, citation audit checklist, failure modes.
- `references/scenarios.md` — patterns for 7 single-focus tasks (fact check, version check, price check, news timeline, doc coverage, person background, academic literature) and 5 composite tasks (comparison, due diligence, market scan, research-backed writing, monitoring brief).
- `references/delivery.md` — answer shapes, citation presentation, uncertainty wording, coverage statements, date discipline.

### Enhanced: Multi-host installer

- `--host agents` preset writes to `~/.agents/skills` / `.agents/skills` — the cross-vendor directory recognized by Codex, OpenClaw, and Gemini CLI.
- `--host all` installs into every host detected on the machine in one command.
- `hellosearch doctor` now runs a full validation suite: frontmatter parse, name match, description length, line count, reference file existence, evals JSON validity.
- Detection priority updated: workspace markers > home markers > cross-vendor default.

### New: Evaluation framework

- `evals/evals.json` — 6 behavior scenarios with verifiable expectations, each targeting a documented failure mode of unassisted research (snippet-only answers, uneven comparisons, false premises, undated claims, rumor-as-fact).
- `evals/triggers.json` — 20 test cases (10 should-trigger, 10 should-not-trigger) for tuning the skill description.
- Both follow the Anthropic skill-creator schema for standard tooling compatibility.

### New: Package constraints test suite

`node-tests/skill-package.test.mjs` adds tests for:
- Full validation pass (all doctor checks green)
- Frontmatter spec compliance
- SKILL.md size limit (≤500 lines) and reference linkage
- Evals schema validation (≥5 behavior scenarios, ≥16 trigger cases)
- Package payload integrity (required files present, no Python tooling, legacy directories absent)

### CI improvements

- `test.yml` workflow added: runs on push to main and PRs, executes `npm test`, `npm run doctor`, and `npm pack --dry-run`.
- `npm-publish.yml` made idempotent: checks npm registry before publishing, skips if version already exists.

### Other

- `LICENSE` added: Apache-2.0.
- `REFACTOR_PLAN.md` documents the full rationale, external evidence, and design decisions behind the v1.0.0 transformation (not shipped in the npm package).

---

## 中文

### 破坏性变更：移除 Python 运行时

删除了全部 Python 代码（约 2100 行，涵盖 `scripts/`、`tests/` 和 `scripts/hellosearch_runtime/`），包括所有关键词查询分类、模板式子查询生成、正则引用解析、URL 字符串来源打分、文件系统宿主检测以及适配器/路由器骨架层。这些层所做的事，宿主模型在每一个维度上都做得更好。

**影响**：技能运行时脚本为零、Python 依赖为零。在无 Python 或无 shell 的宿主（如 claude.ai 网页版）中完整可用。npm 包的 `files` 字段不再包含 `scripts/` 或 `tests/`。

### 新增：纯指令 SKILL.md

SKILL.md 从脚本执行指南重写为六项研究纪律：

1. **搜索前先定标** — 判断问题形状、解析时间引用、核验用户前提、大规模任务确认范围。
2. **按问题分配研究强度** — 分层指引（直答型 3–10 次调用、对比型每个对象 10–15 次、深研/铺开型数十次），附带明确的停止规则。
3. **搜索工艺** — 先宽后窄策略、变换搜索角度、区分片段与页面证据、按内容而非域名判断来源权威性。
4. **对照来源核验，而非对照自己** — 论断级接地、易变事实双源规则、反向搜索、冲突呈现。
5. **整合或淹没** — 每消化 8–10 个来源做一次上下文整合，防止认知退化。
6. **交付研究，而非模板** — 形状匹配的答案（直答、矩阵、时间线、报告）、引用审计、确定程度分层。

### 新增：参考文档

三篇参考文档替代了旧的 evidence-policy、host-routing、runtime-adapters：

- `references/verification.md` — 来源等级、新鲜度规则、反向核验方法、冲突裁决、引用审计清单、失败模式。
- `references/scenarios.md` — 7 种单一任务模式（事实核验、版本查证、价格核实、新闻时间线、文档站点覆盖、人物背景、学术文献）和 5 种复合任务模式（对比评测、技术尽调、市场扫描、研究型写作、定期监测）。
- `references/delivery.md` — 答案形状、引用呈现、不确定性措辞、覆盖声明、日期规范。

### 增强：多宿主安装器

- `--host agents` 预设写入 `~/.agents/skills` / `.agents/skills` — Codex、OpenClaw、Gemini CLI 共同识别的跨厂商目录。
- `--host all` 一条命令安装到本机检测到的全部宿主。
- `hellosearch doctor` 现在执行完整校验：frontmatter 解析、名称匹配、描述长度、行数限制、引用文件存在性、evals JSON 有效性。
- 检测优先级更新：工作区标记 > 用户目录标记 > 跨厂商默认。

### 新增：评测框架

- `evals/evals.json` — 6 个行为场景，每个带可验证的期望，分别瞄准无技能研究的已知失败模式（只看摘要、对比不对齐、接受错误前提、论断无日期、传闻当事实）。
- `evals/triggers.json` — 20 个测试用例（10 个应触发、10 个不应触发），用于打磨技能描述。
- 两者均遵循 Anthropic skill-creator 数据格式，可直接用标准工具运行和评分。

### 新增：包体约束测试

`node-tests/skill-package.test.mjs` 新增测试：
- 全量校验通过（doctor 全部检查绿灯）
- frontmatter 规范合规
- SKILL.md 体量限制（≤500 行）与引用链接完整性
- 评测数据格式校验（≥5 个行为场景、≥16 个触发用例）
- 包体完整性（必需文件存在、无 Python 工具链、无遗留目录）

### CI 改进

- 新增 `test.yml` 工作流：main 分支推送和 PR 时运行 `npm test`、`npm run doctor`、`npm pack --dry-run`。
- `npm-publish.yml` 幂等化：发布前检查 npm registry，版本已存在则跳过。

### 其他

- 新增 `LICENSE`：Apache-2.0。
- `REFACTOR_PLAN.md` 记录了 v1.0.0 改造的完整理由、外部证据和设计决策（不随 npm 包发布）。
