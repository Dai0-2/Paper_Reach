# Paper-Reach

给 AI Agent 一套严谨的文献检索、初筛、全文细筛和证据排序工作流。

`Paper-Reach` 是一个开源 Skill + CLI 项目，面向 Codex、Claude Code、OpenClaw、Cursor 等 AI 编码代理，也可以作为普通 Python 命令行工具独立使用。

项目目标不是“多搜几个来源”，而是让 Agent **更可靠地筛选论文，并明确区分 title、abstract、full-text 三种证据强度**。

[快速开始](#快速开始) · [English](#english) · [支持平台](#支持平台) · [设计理念](#设计理念)

---

## 为什么需要 Paper-Reach？

AI Agent 已经很擅长写代码、改文档、整理文件。但一旦让它做真实文献综述，常见问题就会出现：

- 标题看起来相关，就被误判成真正相关
- 摘要里证据很弱，但 Agent 直接给强结论
- PDF 下载失败后，整个流程卡住
- 最后输出一大坨 JSON，人根本看不动

`Paper-Reach` 把这个流程拆成可复现的几步：

1. 高召回检索候选文献
2. 用 abstract 做保守初筛
3. 能下载全文就继续全文细筛
4. 下载不了就退回摘要级细筛，并降低证据等级
5. 同时输出完整 JSON 和人类可读的精炼清单

### 使用前你需要知道

| 项目 | 含义 |
|---|---|
| **默认保守** | 只看标题不允许给强结论 |
| **Agent 友好** | 既能作为 CLI 使用，也能作为 Skill bundle 使用 |
| **可降级** | PDF 下载失败不会让流程失败 |
| **人类可读** | 除了完整 JSON，还会输出 `brief` 和 `titles` |
| **可扩展** | 检索后端、PDF 解析器、排序 profile 都可以替换 |

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

先跑高召回初筛：

```bash
paper-reach screen \
  --input query.json \
  --output screen.json \
  --high-recall \
  --retrieval-limit 200
```

跑完整流程，并把每个阶段的结果都保存下来：

```bash
paper-reach run \
  --input query.json \
  --output result.json \
  --bundle-dir ./runs/demo \
  --high-recall \
  --retrieval-limit 200 \
  --workers 8
```

导出适合人工阅读的 top 20 精炼清单：

```bash
paper-reach summarize \
  --input result.json \
  --output brief.json \
  --format brief \
  --top-k 20
```

`--bundle-dir` 会生成这样的结果文件夹：

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

如果你已经安装过，更新通常只需要：

```bash
git pull
pip install -e .[dev]
```

---

## English

Paper-Reach gives AI agents a rigorous literature review workflow.

It is an open-source skill + CLI scaffold for:

- literature search
- abstract screening
- full-text fetching
- evidence extraction
- conservative ranking
- structured JSON output

Typical prompt for an agent:

```text
Install and use Paper-Reach from this repository. Run a high-recall literature screening workflow, keep the output conservative, and export both a full JSON result and a brief shortlist.
```

The public repository can support English users, but the default README is currently written in Chinese for easier development and usage in this project stage.

---

## 支持平台

| 平台 / 来源 | 当前支持 | 配置后更好 | 启用方式 |
|---|---|---|---|
| **OpenAlex** | 元数据检索、摘要初筛 | 官方 content API 下载 PDF | 配置 `OPENALEX_API_KEY` |
| **arXiv** | 检索与元数据获取 | PDF / 本地 review | 无需额外配置 |
| **本地 PDF / TXT / JSON** | 离线筛选和细筛 | 更强的本地证据抽取 | 无需额外配置 |
| **出版社 landing page** | 尝试 OA 链接和 PDF 链接解析 | 复用登录会话 | 提供 cookie / header |
| **Codex / OpenAI 风格宿主** | Skill 发现 + CLI 调用 | 同步 skill bundle | `bash scripts/sync.sh` |
| **Claude 风格宿主** | Skill 发现 + CLI 调用 | 同步 skill bundle | `bash scripts/sync.sh` |
| **Gemini 风格宿主** | 扩展元数据 | 同步 skill bundle | `bash scripts/sync.sh` |

### OpenAlex API

如果配置了 `OPENALEX_API_KEY` 或 `OPENALEX_CONTENT_API_KEY`，`Paper-Reach` 会优先使用 OpenAlex 官方内容接口：

```bash
export OPENALEX_API_KEY=your_key
```

下载优先级：

1. OpenAlex content API
2. Open-access PDF URL
3. landing page PDF 链接解析
4. cookie / header 会话复用
5. 回退到 abstract-only review

OpenAlex API key 是可选增强，不是硬依赖。

### 需要 Cookie 的平台

有些出版社或学校代理需要浏览器登录态。对于这类平台，推荐统一流程：

**浏览器登录 -> Cookie-Editor 导出 -> 发给 Agent / 保存为 cookie 文件 -> Paper-Reach 使用**

推荐方式：

- 在 Chrome 里打开目标出版社网站并登录
- 使用 Chrome 插件 `Cookie-Editor` 导出 cookie
- 把 cookie 保存成本地 JSON 文件
- 运行时通过 `--cookie-file` 提供给 Paper-Reach

示例：

```bash
paper-reach fetch-fulltext \
  --input query.json \
  --output review.json \
  --download-dir ./downloads \
  --cookie-file ./cookies.json
```

这个方式通常比自动扫码、自动过验证更简单可靠。

注意：

- cookie 只保存在本地
- 不要把 cookie 提交到 GitHub
- cookie 不是必须的；没有 cookie 时会自动回退

更多说明见 [docs/browser-cookies.md](docs/browser-cookies.md)。

---

## 设计理念

`Paper-Reach` 不是一个重型自治多 Agent 系统。

它更像一个可安装、可复用、可扩展的文献工作流脚手架。

核心理念：

- **Search is easy, screening is hard**
  - 项目价值不是“多搜几个来源”，而是更好地筛文献
- **弱证据不能装成强证据**
  - 标题相关只能说明“可能相关”
- **摘要和全文是不同证据等级**
  - 摘要可用于初筛，全文更适合做最终确认
- **离线模式很重要**
  - 没有网络时，也应该能用本地 PDF、metadata、DOI 列表继续工作
- **JSON first**
  - 完整输出应该能继续被 agent、脚本或下游分析使用
- **人类审查仍然重要**
  - 所以必须有 `brief` / `titles` 这种短输出

### Paper-Reach 是什么

- AI Agent 的文献筛选 Skill
- 一个 Python CLI
- 一个多宿主 skill bundle
- 一个适合二次开发的 literature-review starter repo

### Paper-Reach 不是什么

- 不是一上来就很重的多 Agent 框架
- 不承诺所有 PDF 都能下载
- 不做隐藏逻辑的黑盒排序

---

## 核心能力

- 高召回检索与 query expansion
- 基于 abstract 的保守初筛
- 可选全文下载与全文细筛
- OpenAlex content API 优先下载
- profile-based ranking：硬门槛 + 加权评分
- 人类可读的 `titles` / `brief` 输出
- 给 agent 和程序用的完整 JSON 输出

## 示例 Query

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

## 多 AI 工具适配

`Paper-Reach` 采用“一个核心执行层 + 多宿主包装层”的结构：

- `paper_reach/`
  - CLI、workflow、ranking、fetchers、parsers
- `SKILL.md`
  - 宿主无关的 skill 入口
- `agents/openai.yaml`
  - OpenAI / Codex 风格宿主元数据
- `.claude-plugin/plugin.json`
  - Claude 风格插件元数据
- `gemini-extension.json`
  - Gemini 风格扩展元数据

这样可以避免每个 agent 平台都复制一套逻辑。

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

## 后续还值得改什么

参考 `Agent-Reach` 的项目形态，我觉得 `Paper-Reach` 下一步最值得继续补的是：

- 更“一句话安装”的 agent 安装文档
- 更直观的 examples 截图或输出样例
- 更强的 shortlist 质量评估
- 更清楚地区分“能下载全文”和“只能摘要细筛”的最终输出

## Contributing

欢迎贡献：

- 更好的 scholarly backend
- 更强的 evidence extraction
- 更稳定的全文下载与回退策略
- 更好的 ranking profile
- 更完整的 agent host 适配

这个项目应该保持模块化、保守、可扩展。
