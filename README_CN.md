# HelloSearch

面向 AI 智能体的研究纪律——不是流水线，不是后端。HelloSearch 教你的智能体按问题分配研究强度，不停在第一个顺手的结果上，对照来源而不是记忆去核验论断，并交付经得起检查的引用。

[![npm 版本](https://img.shields.io/npm/v/hellosearch)](https://www.npmjs.com/package/hellosearch)
[![许可证：Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](./LICENSE)

[English](./README.md) · [简体中文](./README_CN.md) · [更新日志](./CHANGELOG.md)

## 概览

- **纯指令构成。** 包内只有一份 `SKILL.md` 和三篇参考文档，没有后端、没有运行时脚本、不依赖 Python。研究是判断型任务，判断应当交给模型；代码只保留给必须确定性执行的部分——在这里就是安装与校验。
- **从结构上做到宿主无关。** 技能遵循开放的 [Agent Skills 规范](https://agentskills.io/specification)，正文描述能力而不指名具体工具，宿主提供什么就用什么：网页搜索、页面抓取、浏览器控制、站点测绘、子智能体。
- **一个包，多个宿主。** 同一份文件可被 Claude Code、Claude.ai、OpenAI Codex、OpenClaw、Gemini CLI、Cursor 等支持 Agent Skills 的宿主加载；npm 安装器会把技能写入各宿主对应的目录。

## 它改变了什么

| 没有这个技能 | 有这个技能 |
| --- | --- |
| 靠搜索结果摘要拼出答案 | 关键页面先打开读全文，再支撑论断 |
| 首页结果照单全收 | 论断追溯到一手来源；易变事实需要两个独立来源 |
| 通篇"最新""目前"却没有日期 | 相对时间解析成具体日期，快变事实标注查证日期 |
| 顺着用户的前提往下查 | 先独立核验前提本身 |
| 所有答案套同一个报告模板 | 答案形状随问题而定：直答、矩阵、时间线或报告 |
| 证据单薄时用语依然笃定 | 已确认、推断、未决三种确定程度清晰可辨 |

## 安装

### 通过 npm

```bash
npm install -g hellosearch
hellosearch install              # 自动检测最可能的宿主并安装
hellosearch install --host all   # 安装到本机检测到的全部宿主
```

宿主预设：

| `--host` | 用户级 | 项目级 |
| --- | --- | --- |
| `claude-code` | `~/.claude/skills` | `.claude/skills` |
| `codex` / `agents` | `~/.agents/skills` | `.agents/skills` |
| `openclaw` | `~/.openclaw/skills` | `<工作区>/skills` |

`~/.agents/skills` 是跨厂商通用目录，OpenClaw 与 Gemini CLI 同样会读取。项目级安装用 `--scope project`，自定义目录用 `--target <路径>`，覆盖已有副本用 `--force`。

安装前查看计划，或安装后验证：

```bash
hellosearch info     # 输出解析后的安装计划
hellosearch doctor   # 安装计划加包体校验结果
```

### 其他方式

- 通过 skills 命令行工具：`npx skills add hellowind777/hellosearch`
- 手动复制：把 `SKILL.md`、`references/`、`agents/` 拷入宿主读取的任意技能目录。

## 使用

安装后，研究类请求会自动触发技能，无需点名：

- `帮我确认这个 SDK 当前稳定版的 breaking changes，要官方来源。`
- `对比这三个向量数据库的价格和许可证，给出处。`
- `这条新闻是真的吗？帮我核实一下，给出处。`
- `先测绘一遍文档站，再找现在的限流规则。`

当请求看起来不像研究、但你希望套用这套纪律时，可以显式点名：`用 hellosearch 查 ...`。

## 包结构

| 路径 | 说明 |
| --- | --- |
| `SKILL.md` | 技能本体：触发描述与六项研究纪律。 |
| `references/verification.md` | 来源等级、新鲜度规则、反向核验方法、引用审计。 |
| `references/scenarios.md` | 常见单一与复合研究任务的模式。 |
| `references/delivery.md` | 答案形状、引用呈现、不确定性措辞。 |
| `agents/openai.yaml` | 供部分宿主读取的展示元数据。 |
| `evals/` | 行为评测场景与触发测试集。 |
| `bin/`、`lib/` | npm 安装器与包体校验。 |
| `node-tests/` | 安装器与包体约束的测试。 |

## 质量

```bash
npm test        # 安装器行为与包体约束
npm run doctor  # frontmatter、体量与结构校验
```

`evals/evals.json` 包含六个带可验证预期的行为场景，分别对应无技能研究的已知失败模式（只看摘要作答、对比字段不对齐、接受错误前提、论断无日期、把传闻当事实）。`evals/triggers.json` 是"应触发/不应触发"测试集，用于打磨触发描述。两者都遵循 Anthropic skill-creator 工作流的数据格式，可直接用标准工具运行与评分。

## 许可证

[Apache-2.0](./LICENSE)
