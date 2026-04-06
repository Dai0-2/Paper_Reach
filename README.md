<div align="center">

# 📚 Paper-Reach

给你的 AI Agent 一键装上严谨文献筛选能力

MIT License · Python 3.8+ · Agent Skill · OpenAlex Ready

[快速开始](#快速开始) · [English](#english) · [支持平台](#支持平台) · [设计理念](#设计理念)

</div>

---

## 为什么是 Paper-Reach？

AI Agent 已经能写代码、改文档、管仓库了，但一旦进入真实文献综述流程，通常就会出问题：

- “帮我找这个主题真正符合条件的论文。” -> 很容易只看标题就过度判断
- “帮我确认哪些论文真的用了这个数据或监督信号。” -> 仅靠摘要证据往往不够
- “帮我把论文下下来再确认方法。” -> PDF 获取经常失败，流程容易中断
- “给我一个我真正能看的 shortlist。” -> 最后只吐一大坨 JSON，人根本不想翻

难点不在搜索，而在于 **基于证据的筛选**。

Paper-Reach 把这件事拆成可复用的步骤：

1. 先检索一个较大的候选池
2. 在摘要层做保守初筛
3. 能拿到全文时继续下载
4. 用更强的证据做细筛
5. 同时导出给机器和给人看的结果

### 开始之前

| 项目 | 含义 |
|---|---|
| **默认保守** | 只看标题的相关性绝不会被当成强证据 |
| **Agent 友好** | 可单独作为 CLI 用，也可作为可复用 skill bundle 用 |
| **优雅回退** | 全文下不下来，流程也不会直接废掉 |
| **人类可读** | 支持 `brief` 和 `titles` 导出，不只是大 JSON |
| **易扩展** | 搜索后端、解析器、ranking profile、下载逻辑都可插拔 |

---

## 快速开始

本地安装：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
paper-reach doctor
```

生成一个示例 query：

```bash
paper-reach example-query > query.json
```

跑一次高召回初筛：

```bash
paper-reach screen \
  --input query.json \
  --output screen.json \
  --high-recall \
  --retrieval-limit 200
```

跑完整流程，并保存所有中间结果：

```bash
paper-reach run \
  --input query.json \
  --output result.json \
  --bundle-dir ./runs/demo \
  --high-recall \
  --retrieval-limit 200 \
  --workers 8
```

导出适合人工查看的 shortlist：

```bash
paper-reach summarize \
  --input result.json \
  --output brief.json \
  --format brief \
  --top-k 20
```

`bundle-dir` 目录大概长这样：

```text
runs/demo/
├─ 00_query.json
├─ 10_screen.json
├─ 20_fetched_papers.json
├─ 30_result_full.json
├─ 40_result_brief.json
├─ 50_result_titles.json
├─ manifest.json
└─ downloads/
```

> 如果已经安装过，更新通常就是：
>
> ```bash
> git pull
> pip install -e .[dev]
> ```

---

## English

Paper-Reach gives your AI agent a rigorous literature review workflow.

It is an open-source Skill + CLI for literature search, abstract screening, full-text review, evidence extraction, and conservative ranking.

It is designed for Codex, Claude Code, OpenClaw, Cursor, and similar coding agents, while also working as a standalone Python command-line tool.

### Why It Exists

Searching papers is easy. Screening them rigorously is hard.

Most AI agents can collect titles and abstracts, but they often:

- overclaim relevance from titles
- treat abstract-only evidence as if it were full-text evidence
- fail when PDFs cannot be downloaded
- return giant JSON outputs that are hard for humans to inspect

Paper-Reach keeps the workflow explicit:

1. retrieve a broad candidate pool
2. screen conservatively using titles and abstracts
3. fetch full text when available
4. review with stronger evidence
5. export both full machine-readable JSON and compact human-readable shortlists

### Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
paper-reach doctor
paper-reach example-query > query.json
```

Run the full workflow:

```bash
paper-reach run \
  --input query.json \
  --output result.json \
  --bundle-dir ./runs/demo \
  --high-recall \
  --retrieval-limit 200 \
  --workers 8
```

Export a compact shortlist:

```bash
paper-reach summarize \
  --input result.json \
  --output brief.json \
  --format brief \
  --top-k 20
```

### Supported Sources And Hosts

- OpenAlex metadata search and optional content API PDF download
- arXiv search
- local PDFs, TXT files, and JSON metadata
- publisher landing pages with best-effort open-access fallback
- optional cookie / header session reuse for logged-in scholarly platforms
- Codex / OpenAI-style skill hosts
- Claude-style skill hosts
- Gemini-style extension metadata

Typical message to an agent:

```text
Install and use Paper-Reach from this repository. Run a high-recall literature screening workflow, keep the output conservative, and export both a full JSON result and a brief shortlist.
```

### Design Philosophy

Paper-Reach is not a giant autonomous research platform. It is a practical literature workflow scaffold.

The core principle is simple:

- title relevance is weak evidence
- abstract evidence is useful but provisional
- full-text evidence is stronger
- unavailable PDFs should not break the whole workflow
- final outputs should be usable by both agents and humans

---

## 支持平台

| 平台 | 现在可用 | 配置后更强 | 怎么开启 |
|---|---|---|---|
| **OpenAlex** | Metadata 检索、摘要初筛 | 官方 content API PDF 下载 | 设置 `OPENALEX_API_KEY` |
| **arXiv** | 搜索和 metadata 检索 | PDF / 本地 review | 无需额外配置 |
| **本地 PDF / TXT / JSON** | 离线筛选与 review | 更强的本地证据提取 | 无需额外配置 |
| **出版社落地页** | best-effort OA 回退 | 登录态 session 复用 | 提供 cookies / headers |
| **Codex / OpenAI 风格宿主** | Skill 发现 + CLI 调用 | bundle 安装 | `bash scripts/sync.sh` |
| **Claude 风格宿主** | Skill 发现 + CLI 调用 | bundle 安装 | `bash scripts/sync.sh` |
| **Gemini 风格宿主** | 已提供 extension metadata | bundle 安装 | `bash scripts/sync.sh` |

### 需要 Cookie 的学术平台怎么处理

有些学术平台需要登录状态，或者依赖机构浏览器会话。

对这类平台，最实用的方式是：

**浏览器登录 -> 用 Cookie-Editor 导出 Cookie -> 交给 Agent / Paper-Reach 使用**

推荐流程：

- 在 Chrome 里登录目标出版社或平台
- 用 Chrome 插件 `Cookie-Editor` 导出 Cookie
- 把 Cookie 文件作为 `--cookie-file` 传给 Paper-Reach

示例：

```bash
paper-reach fetch-fulltext \
  --input query.json \
  --output review.json \
  --download-dir ./downloads \
  --cookie-file ./cookies.json
```

这通常比自动模拟登录或反复做人机验证更简单，也更稳定。

Cookie 处理原则：

- Cookie 留在本地
- 核心工作流不强依赖 Cookie
- Cookie 缺失或失效时，Paper-Reach 会自动回退

详情见 [docs/browser-cookies.md](docs/browser-cookies.md)。

---

## 设计理念

Paper-Reach 不是一个重型自治研究框架。

它是一个实用的文献工作流 starter repo / scaffolding。

它的核心设计原则是：

- **搜索不难，筛选更难**
  - 真正的价值在于筛得更准，而不是源更多
- **弱证据就该保持弱**
  - 不能把标题相关直接说成“已确认”
- **摘要和全文是不同证据层级**
  - 摘要支持有用，但全文支持更强
- **离线模式很重要**
  - 必须能处理本地 PDF、metadata、DOI 列表
- **JSON 优先**
  - 输出要适合 agent 和脚本继续消费
- **人工复核依然重要**
  - 最终应该产出人真正能看的 shortlist

### Paper-Reach 是什么

- 一个给 AI Agent 复用的文献工作流
- 一个 Python CLI
- 一个适配多宿主的 skill bundle
- 一个适合 literature review / gap analysis 的 starter scaffold

### Paper-Reach 不是什么

- 不是一个庞大的自治 multi-agent 系统
- 不承诺每篇论文都一定能下载
- 不是一个黑盒排序器

---

## 核心能力

- 高召回文献检索与 query expansion
- 保守的摘要级初筛与 explainable reasons
- PDF 可用时的全文 review
- OpenAlex 优先下载与自动回退
- profile-based ranking，支持硬门槛和加权维度
- 面向人的紧凑输出：`titles` 与 `brief`
- 面向 agent 的结构化完整 JSON 输出

## 一个具体示例

下面是一个真实可用的 query：

```json
{
  "topic": "China static population exposure assessment for disasters and infectious disease",
  "keywords": [
    "China",
    "static population",
    "gridded population",
    "census population",
    "population exposure",
    "population at risk",
    "disaster exposure",
    "hazard exposure",
    "infectious disease exposure",
    "WorldPop",
    "LandScan",
    "GPW"
  ],
  "inclusion_criteria": [
    "study area is in China",
    "uses static population data or gridded population as exposure input",
    "focuses on disaster exposure or infectious-disease exposure",
    "estimates exposed population or population at risk"
  ],
  "exclusion_criteria": [
    "study area outside China only",
    "not an exposure study",
    "generic epidemiology without exposure modeling",
    "dynamic mobility only without static population baseline"
  ],
  "year_range": [2005, 2026],
  "max_results": 200,
  "need_gap_analysis": true,
  "mode": "auto",
  "require_fulltext_for_selection": false,
  "profile": "static_population_exposure_baseline"
}
```

## OpenAlex 优先下载

如果配置了 `OPENALEX_API_KEY` 或 `OPENALEX_CONTENT_API_KEY`，Paper-Reach 会优先尝试 OpenAlex content API：

```bash
export OPENALEX_API_KEY=your_key
```

下载优先级：

1. OpenAlex content API
2. open-access PDF URL
3. 落地页提取
4. cookie / header session 复用
5. 回退到摘要级 review

也就是说，OpenAlex API key 是增强项，不是硬依赖。

## 多宿主 Skill 支持

Paper-Reach 采用和成熟跨宿主 skill 项目类似的结构：

- 一个共享执行引擎
  - `paper-reach` CLI + `paper_reach/`
- 一个宿主无关的 skill 入口
  - `SKILL.md`
- 几个宿主专用的轻量 manifest
  - `agents/openai.yaml`
  - `.claude-plugin/plugin.json`
  - `gemini-extension.json`

这样可以把核心逻辑放在一处，同时让不同 agent 宿主都能发现和调用它。

## 仓库结构

```text
paper-reach/
├─ README.md
├─ AGENTS.md
├─ SKILL.md
├─ docs/
├─ examples/
├─ skills/
├─ agents/
├─ .claude-plugin/
├─ paper_reach/
├─ scripts/
└─ tests/
```

## 文档

- [docs/install.md](docs/install.md)
- [docs/usage.md](docs/usage.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/agent-integration.md](docs/agent-integration.md)
- [docs/browser-cookies.md](docs/browser-cookies.md)
- [docs/publishing.md](docs/publishing.md)
- [docs/roadmap.md](docs/roadmap.md)

## 后续还值得继续优化的地方

- 安装体验还能更一键化
- 首页还能更强调结果导向
- Cookie 配置可以再做得更“照着就能用”
- shortlist 质量还值得继续提升

## Contributing

Contributions are most useful when they improve:

- screening quality
- evidence extraction
- backend extensibility
- offline usability
- agent integration

The project should stay modular, conservative, and easy to extend.
