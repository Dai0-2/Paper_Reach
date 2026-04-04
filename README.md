<div align="center">

# 👁️ Paper-Reach

给你的 AI Agent 一套更严谨的文献检索、筛选、阅读与证据提取工作流

[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](pyproject.toml)
[![GitHub Stars](https://img.shields.io/github/stars/Dai0-2/Paper_Reach?style=social)](https://github.com/Dai0-2/Paper_Reach)

[快速开始](#快速开始) · [English](README_EN.md) · [支持平台](#支持平台) · [设计理念](#设计理念)

</div>

---

## 为什么做 Paper-Reach？

`Paper-Reach` 是一个开源 Skill + CLI 工具，用来帮助 Codex、Claude Code、OpenClaw、Cursor 等智能编码代理完成文献检索、摘要初筛、全文细筛、证据提取和保守排序。

它也可以作为普通 Python 命令行工具单独使用，不依赖某一个 Agent 平台。

这个项目的重点不是“搜索更多来源”，而是让 Agent **更可靠地筛选文献，并明确说明证据来自标题、摘要还是全文**。

AI Agent 已经很擅长写代码、改文档、跑命令，但一旦让它做真实的文献综述，常见问题就会出现：

- “帮我找真正符合条件的论文。” -> 容易只看标题就过度判断
- “告诉我哪些论文真的用了某个数据集或方法。” -> 摘要证据经常不够
- “下载全文并确认方法。” -> PDF 下载失败后流程容易卡住
- “给我一份能直接看的 shortlist。” -> 输出经常变成一大坨 JSON

文献检索本身不难，真正难的是：

> 搜完之后，如何基于证据进行保守、可解释、可复查的筛选。

Paper-Reach 把它拆成一个可重复执行的流程：

1. 高召回检索候选文献
2. 基于摘要做保守初筛
3. 对可下载的论文尝试获取全文
4. 对全文或摘要进行细筛
5. 输出给 Agent 用的完整 JSON 和给人看的简版清单

## What's New

- OpenAlex content API：配置 API key 后优先走官方全文接口
- `run --bundle-dir`：一次输出完整运行文件夹，包含每个阶段结果
- `summarize`：支持导出 `titles` 和 `brief` 两种精炼结果
- profile-based ranking：支持任务专属硬门槛和加权评分
- 多宿主 Skill 元数据：适配 Codex / Claude 风格 / Gemini 风格宿主

---

## 支持平台

| 平台 / 来源 | 默认支持 | 可选增强 | 如何配置 |
|---|---|---|---|
| OpenAlex metadata | 是 | 更多全文下载 | 设置 `OPENALEX_API_KEY` |
| OpenAlex full-text content API | 否 | 是 | 设置 `OPENALEX_API_KEY` 或 `OPENALEX_CONTENT_API_KEY` |
| arXiv | 是 | PDF / 本地 review | 无需额外配置 |
| 本地 PDF / TXT / JSON metadata | 是 | 离线证据抽取 | 使用 `--local-path` |
| 出版社 landing page | 有限支持 | Cookie / Header 会话复用 | 使用 `--cookie-file` / `--header-file` |
| Codex / Claude / OpenClaw 风格 Skill 宿主 | 是 | 同步到宿主 skill 目录 | 运行 `scripts/sync.sh` |

### 需要 Cookie 的平台怎么处理？

有些出版社页面需要登录、机构访问权限，或者浏览器里已经通过的人机验证。对于这类平台，最推荐的方式不是让 Agent 自动登录，而是复用你浏览器里已经登录好的会话。

统一流程：

`浏览器登录 -> Cookie-Editor 导出 -> 发给 Agent / 保存为 cookie 文件 -> Paper-Reach 使用 --cookie-file`

推荐 Chrome 插件：

- [Cookie-Editor](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)

示例：

```bash
paper-reach fetch-fulltext \
  --input query.json \
  --output review.json \
  --download-dir ./downloads \
  --cookie-file ./cookies.json
```

为什么这样设计：

- 比自动化登录更稳定
- 比扫码流程更容易复用
- 适合出版社、学校代理、机构访问等场景
- Cookie 只在本地使用，不会被仓库上传

详细说明见：[docs/browser-cookies.md](docs/browser-cookies.md)

---

## 快速开始

先给 Agent 一个能跑通的文献筛选工作流，再去优化检索词、ranking profile 和输出格式。

### 1. 安装

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
paper-reach doctor
```

### 2. 跑一轮高召回初筛

```bash
paper-reach example-query > query.json

paper-reach screen \
  --input query.json \
  --output screen.json \
  --high-recall \
  --retrieval-limit 200
```

### 3. 跑完整工作流

```bash
paper-reach run \
  --input query.json \
  --output result.json \
  --bundle-dir ./runs/demo \
  --high-recall \
  --retrieval-limit 200 \
  --workers 8
```

### 4. 导出可读 shortlist

```bash
paper-reach summarize \
  --input result.json \
  --output brief.json \
  --format brief \
  --top-k 20
```

---

## 示例任务

假设你想找：

> 在中国使用静态人口或栅格人口作为暴露输入的灾害暴露、流感暴露、传染病暴露论文，用来和动态人口方法做对照。

示例 query：

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

## 输出结果长什么样？

使用 `run --bundle-dir` 时，Paper-Reach 会输出一个完整结果包：

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

文件含义：

- `30_result_full.json`
  - 完整机器可读结果
  - 适合 Agent、调试和下游处理
- `40_result_brief.json`
  - 人类可读的精炼 review 清单
  - 包含 title、URL、year、decision、reasons、venue、PDF path 等字段
- `50_result_titles.json`
  - 最小 shortlist，只包含 title + URL

这样能同时满足：

- Agent 需要结构化数据
- 人需要快速浏览 shortlist

---

## 多宿主 Skill 支持

Paper-Reach 采用跨宿主包装结构：

- 一个共享执行层
  - `paper-reach` CLI + `paper_reach/` Python 包
- 一个宿主无关 Skill 入口
  - `SKILL.md`
- 多个轻量宿主 manifest
  - `agents/openai.yaml`
  - `.claude-plugin/plugin.json`
  - `gemini-extension.json`

同步到常见宿主目录：

```bash
bash scripts/sync.sh
bash scripts/check-install.sh
```

默认目标：

- `~/.codex/skills/paper-reach`
- `~/.claude/skills/paper-reach`
- `~/.agents/skills/paper-reach`

---

## 设计理念

**Paper-Reach 是脚手架，不是重型框架。**

这意味着：

- 核心工作流应该保持模块化
- 证据强弱必须在输出里可见
- 标题相关不能当成强证据
- 摘要初筛应该保守
- 全文 review 用来增强证据，而不是制造确定性
- 输出必须同时适合 Agent 和人类阅读

这个仓库的目标是帮助 Agent 更好地筛选文献，而不是假装只要搜到了论文就已经理解了论文。

### Paper-Reach 是什么

- 文献检索和筛选工作流
- Agent Skill 工具
- Python CLI
- JSON-first literature review scaffold

### Paper-Reach 不是什么

- 不是保证下载所有论文的爬虫
- 不是绕过人机验证或付费墙的工具
- 不是隐藏逻辑的黑盒排序器
- 不是一上来就很重的多 Agent 平台

---

## 仓库结构

```text
paper-reach/
├─ README.md
├─ README_EN.md
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

- `paper_reach/`
  - CLI、workflow、ranking、fetchers、parsers、schemas
- `skills/`
  - paper-search、paper-reader、paper-ranker
- `examples/`
  - query 示例、auth 示例、agent recipes
- `docs/`
  - 安装、使用、架构、路线图、发布

## 文档

- [docs/install.md](docs/install.md)
- [docs/usage.md](docs/usage.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/agent-integration.md](docs/agent-integration.md)
- [docs/browser-cookies.md](docs/browser-cookies.md)
- [docs/publishing.md](docs/publishing.md)
- [docs/roadmap.md](docs/roadmap.md)

## 贡献

好的贡献通常会改善这些方向：

- 更好的检索后端
- 更强的摘要或全文证据抽取
- 更清晰的 ranking profile
- 更好的离线支持
- 更好的 Agent 宿主适配

项目应该保持保守、模块化、轻量和易扩展。
