<div align="center">

# 👁️ Paper-Reach

给你的 AI Agent 一套严谨的文献检索与筛选工作流

[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.8%2B](https://img.shields.io/badge/python-3.8%2B-blue.svg)](pyproject.toml)
[![GitHub Stars](https://img.shields.io/github/stars/Dai0-2/paper_reach?style=social)](https://github.com/Dai0-2/paper_reach)

`Paper-Reach` 是一个面向 AI Agent 的开源 Skill + CLI，用于文献检索、摘要初筛、全文细筛、证据提取和保守排序。

[快速开始](#快速开始) · [English](README_EN.md) · [支持平台](#支持平台) · [设计理念](#设计理念)

</div>

---

## 为什么需要 Paper-Reach

很多 agent 能搜到论文标题和摘要，但真正做文献综述时，经常会出问题：

- 只看标题就说相关
- 摘要证据很弱，却给出很强结论
- 下载不到 PDF，整个流程就停住
- 输出是巨大 JSON，人根本不想读

Paper-Reach 把这个过程拆成几个明确阶段：

1. 高召回检索候选论文
2. 基于摘要做保守初筛
3. 能下载全文就下载全文
4. 用摘要或全文做细筛
5. 输出完整版 JSON 和人能直接看的精炼版

### 它适合什么场景

| 场景 | Paper-Reach 怎么做 |
|---|---|
| 先拉 200-300 篇候选论文 | `screen --high-recall --retrieval-limit 200` |
| 只想看最终标题和链接 | `summarize --format titles` |
| 希望看到完整证据和原因 | 查看 `30_result_full.json` |
| 下载不到全文 | 自动退回摘要级细筛，不会假装已读全文 |
| 想让 Codex / OpenClaw 直接调用 | 使用 `SKILL.md` 和 `scripts/sync.sh` |

---

## 快速开始

安装：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
paper-reach doctor
```

生成示例 query：

```bash
paper-reach example-query > query.json
```

只做粗筛：

```bash
paper-reach screen \
  --input query.json \
  --output screen.json \
  --high-recall \
  --retrieval-limit 200
```

跑完整流程，并把每个阶段都输出到一个文件夹：

```bash
paper-reach run \
  --input query.json \
  --output result.json \
  --bundle-dir ./runs/demo \
  --high-recall \
  --retrieval-limit 200 \
  --workers 8
```

导出适合人工阅读的精简版：

```bash
paper-reach summarize \
  --input result.json \
  --output brief.json \
  --format brief \
  --top-k 20
```

输出目录大概长这样：

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

> 已经安装过的话，更新通常就是：
>
> ```bash
> git pull
> pip install -e .[dev]
> ```

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

有些学术平台需要登录状态，或者依赖机构浏览器会话。对这类平台，最实用的方式是：

**浏览器登录 -> 用 Cookie-Editor 导出 Cookie -> 发给 Agent / Paper-Reach 使用**

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

Paper-Reach 不是一个重型自治研究框架，而是一个实用的文献工作流 starter repo / scaffolding。

核心设计原则：

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

## 文档

- [docs/install.md](docs/install.md)
- [docs/usage.md](docs/usage.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/agent-integration.md](docs/agent-integration.md)
- [docs/browser-cookies.md](docs/browser-cookies.md)
- [docs/publishing.md](docs/publishing.md)
- [docs/roadmap.md](docs/roadmap.md)

## Contributing

Contributions are most useful when they improve:

- screening quality
- evidence extraction
- backend extensibility
- offline usability
- agent integration

The project should stay modular, conservative, and easy to extend.
