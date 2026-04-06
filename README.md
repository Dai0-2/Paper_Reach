# Paper-Reach

Give your AI agent a rigorous literature review workflow.

Paper-Reach is a practical, agent-friendly skill bundle and Python CLI for searching papers, screening abstracts, fetching full text when available, ranking evidence, and exporting review-ready literature lists.

It is designed for Codex, Claude Code, OpenClaw, Cursor, and similar coding agents, but it also works as a normal command-line tool.

Quick links: [快速开始](#快速开始) · [English](#english) · [支持平台](#支持平台) · [设计理念](#设计理念)

---

## 快速开始

> 如果文献平台需要登录或机构访问权限，例如 ScienceDirect、Cell、Springer、Wiley 等，优先使用浏览器插件导出 Cookie，再交给 Agent 或 CLI 使用。
> 统一流程：浏览器登录 → Cookie-Editor 导出 → 传给 Paper-Reach。

### 安装

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
paper-reach doctor
```

### 同步到常见 Agent 宿主

```bash
bash scripts/sync.sh
bash scripts/check-install.sh
```

默认同步到：

- `~/.codex/skills/paper-reach`
- `~/.claude/skills/paper-reach`
- `~/.agents/skills/paper-reach`

### 跑一个完整文献筛选任务

```bash
paper-reach example-query > query.json

paper-reach run \
  --input query.json \
  --output result.json \
  --bundle-dir ./runs/demo \
  --high-recall \
  --retrieval-limit 200 \
  --workers 8
```

结果会保存在：

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

你通常最先看这两个文件：

- `40_result_brief.json`：精炼版，适合人工快速审阅
- `50_result_titles.json`：只保留标题和链接

### 配置 OpenAlex PDF 下载增强

OpenAlex API key 不是必需的，但配置后会优先尝试 OpenAlex 官方 content API 下载 PDF，失败时自动回退到默认下载逻辑。

```bash
export OPENALEX_API_KEY=your_key
```

下载优先级：

1. OpenAlex content API
2. 开放获取 PDF 链接
3. DOI / publisher landing page 中的 PDF 链接
4. 用户授权的 cookie / header 会话
5. 下载失败时退回摘要级细筛

### 配置 Cookie

对于需要登录或机构访问权限的平台：

- Chrome / Edge：推荐 `Cookie-Editor`
- Firefox：推荐 `Cookie Quick Manager` 或 `Export Cookies TXT`

示例：

```bash
paper-reach run \
  --input query.json \
  --output result.json \
  --bundle-dir ./runs/my-topic \
  --download-dir ./runs/my-topic/downloads \
  --cookie-file ./cookies.json \
  --header-file ./headers.json \
  --high-recall \
  --retrieval-limit 200 \
  --workers 8
```

Cookie 只是复用你已经登录过的合法会话。Paper-Reach 不会绕过人机验证或访问控制。

## English

Paper-Reach is a lightweight starter project for building literature-review skills that agents can actually execute.

It focuses on:

- high-recall scholarly retrieval
- conservative abstract screening
- optional full-text fetching and review
- profile-based ranking
- JSON-first outputs for agents
- compact summaries for humans

The core philosophy is simple:

- title-only relevance is weak evidence
- abstract-supported relevance is useful but provisional
- full-text-supported relevance is stronger
- unavailable full text should be reported, not hidden

Quick start:

```bash
pip install -e .[dev]
paper-reach doctor
paper-reach example-query > query.json
paper-reach run --input query.json --output result.json --bundle-dir ./runs/demo --high-recall --retrieval-limit 200
paper-reach summarize --input result.json --output brief.json --format brief --top-k 20
```

Example query intent:

> Find papers that use static or gridded population data in China for disaster exposure or infectious-disease exposure assessment, so they can be used as static-population baselines when comparing dynamic population methods.

Minimal query shape:

```json
{
  "topic": "China static population exposure assessment for disasters and infectious disease",
  "keywords": [
    "China",
    "static population",
    "gridded population",
    "population exposure",
    "population at risk",
    "disaster exposure",
    "infectious disease exposure",
    "WorldPop",
    "LandScan",
    "GPW"
  ],
  "inclusion_criteria": [
    "study area is in China",
    "uses static population data or gridded population as exposure input",
    "estimates exposed population or population at risk"
  ],
  "exclusion_criteria": [
    "study area outside China only",
    "not an exposure study",
    "generic epidemiology without exposure modeling"
  ],
  "year_range": [2005, 2026],
  "max_results": 200,
  "mode": "auto",
  "need_gap_analysis": true,
  "require_fulltext_for_selection": false,
  "profile": "static_population_exposure_baseline"
}
```

## 支持平台

Paper-Reach 当前支持或预留了这些来源和输入方式：

- OpenAlex
  - 元数据检索
  - 可选 OpenAlex content API 下载 PDF
- arXiv
  - 轻量检索
- 本地文件
  - PDF
  - TXT
  - JSON metadata
  - DOI / title list
- 出版商 landing page
  - 尝试解析开放 PDF 链接
- Cookie / header 会话复用
  - 适用于需要用户登录后访问的站点

当前推荐策略：

1. 优先用 OpenAlex 做检索和可下载内容发现
2. 有 OpenAlex API key 时优先走 content API
3. 下载不到全文时继续做摘要级细筛
4. 对受限平台使用浏览器登录后导出的 Cookie
5. 永远不要把标题命中当成强证据

## 设计理念

- 一个引擎，多宿主发现
  - `paper-reach` CLI 是统一执行层
  - `SKILL.md`、`agents/openai.yaml`、`.claude-plugin/`、`gemini-extension.json` 是宿主发现层
- 搜索和筛选分离
  - 检索阶段负责召回候选
  - 筛选阶段负责证据判断
- 摘要和全文分层
  - abstract 可以粗筛
  - full text 才能支持强结论
- Cookie 优先，但不绕过访问控制
  - 复用用户已授权会话
  - 遇到人机验证或受限内容时显式标记
- 完整输出和精炼输出并存
  - `30_result_full.json` 给 agent 和程序
  - `40_result_brief.json` 给人快速看
  - `50_result_titles.json` 给最短清单

## 核心命令

```bash
paper-reach doctor
paper-reach example-query
paper-reach screen --input query.json --output screen.json
paper-reach fetch-fulltext --input query.json --output review.json
paper-reach review --input query.json --output review.json
paper-reach run --input query.json --output result.json --bundle-dir ./runs/demo
paper-reach summarize --input result.json --output brief.json --format brief
```

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

重点目录：

- `paper_reach/`：CLI、workflow、models、ranking、fetchers、parsers
- `skills/`：paper-search、paper-reader、paper-ranker
- `examples/`：示例 query、auth 示例、agent recipes
- `docs/`：安装、使用、架构、发布、路线图
- `scripts/`：同步到宿主目录和安装检查

## 文档

- [docs/install.md](docs/install.md)
- [docs/usage.md](docs/usage.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/agent-integration.md](docs/agent-integration.md)
- [docs/browser-cookies.md](docs/browser-cookies.md)
- [docs/publishing.md](docs/publishing.md)
- [docs/roadmap.md](docs/roadmap.md)

## 贡献

欢迎改进：

- scholarly backend
- full-text fetching fallback
- abstract / full-text evidence extraction
- ranking profile
- 多宿主 skill packaging

项目应保持轻量、可执行、可解释，不应膨胀成重型自治多 Agent 系统。
