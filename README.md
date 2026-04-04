<h1 align="center">Paper-Reach</h1>

<p align="center">
  <strong>Give your AI agent a rigorous literature review workflow</strong>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10+-green.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+"></a>
</p>

<p align="center">
  <a href="#快速开始">快速开始</a> · <a href="#english">English</a> · <a href="#支持平台">支持平台</a> · <a href="#设计理念">设计理念</a>
</p>

---

## 为什么需要 Paper-Reach？

AI Agent 已经能帮你写代码、改文档、跑脚本，但你让它做一轮严谨的文献筛选时，通常会遇到这些问题：

- “标题看起来相关”被误当成“论文真的相关”
- 摘要里没有证据，Agent 却直接给出强结论
- 下载不了 PDF，整个流程就卡住
- 结果 JSON 很完整，但人根本看不动
- 每次换一个研究问题，都要重新写 prompt、重新定义筛选规则

`Paper-Reach` 把文献综述拆成一个可复用的 Skill / CLI 工作流：

1. 高召回检索候选论文
2. 用摘要做第一轮保守粗筛
3. 对可获得全文的论文继续下载和细筛
4. 用 profile-based ranking 做任务相关排序
5. 同时输出完整 JSON 和精炼清单

这个项目不是一个重型自治研究系统，而是一个给 Agent 使用的文献筛选脚手架。

## 核心能力

- 高召回检索：OpenAlex、arXiv、本地 metadata、本地 PDF / TXT
- 摘要级粗筛：明确区分 title-only、abstract-supported、full-text-supported
- 全文获取：优先 OpenAlex Content API，失败后回退到开放 PDF、落地页解析、cookie/header 会话
- 任务评分：支持 profile-based ranking，用硬门槛和加权维度定义不同研究任务
- 结果打包：`run --bundle-dir` 一次输出 query、粗筛、下载、完整版、brief、titles
- 精炼输出：`summarize --format titles|brief` 直接给人看的短清单
- 多宿主适配：Codex / Claude Code / OpenClaw / Cursor 等能跑命令行的 Agent 都可以调用
- 离线可用：没有互联网时，也可以用用户提供的 PDFs、DOI 列表、BibTeX、metadata 文件

## 快速开始

### 1. 安装 CLI

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
paper-reach doctor
```

### 2. 准备一个 query

```bash
paper-reach example-query > query.json
```

也可以自己写一个更具体的 query，例如：

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
    "focuses on disaster exposure or infectious-disease exposure",
    "estimates exposed population or population at risk"
  ],
  "exclusion_criteria": [
    "study area outside China only",
    "not an exposure study",
    "generic epidemiology without exposure modeling"
  ],
  "year_range": [2005, 2026],
  "max_results": 200,
  "need_gap_analysis": true,
  "mode": "auto",
  "require_fulltext_for_selection": false,
  "profile": "static_population_exposure_baseline"
}
```

### 3. 跑完整流程

```bash
paper-reach run \
  --input query.json \
  --output result.json \
  --bundle-dir ./runs/china_static_population \
  --high-recall \
  --retrieval-limit 200 \
  --workers 8
```

### 4. 查看精炼结果

```bash
paper-reach summarize \
  --input result.json \
  --output brief.json \
  --format brief \
  --top-k 20
```

`--bundle-dir` 会生成一个完整结果包：

```text
runs/china_static_population/
├─ 00_query.json
├─ 10_screen.json
├─ 20_fetched_papers.json
├─ 30_result_full.json
├─ 40_result_brief.json
├─ 50_result_titles.json
├─ manifest.json
└─ downloads/
```

## 需要 Cookie 的网站怎么处理？

很多出版社或平台会要求登录、机构认证或浏览器验证。Paper-Reach 不会绕过验证，但支持复用你本地已经授权的浏览器会话。

推荐流程统一为：

```text
浏览器登录目标网站 -> Cookie-Editor 导出 Cookie -> 发给 Agent / 保存成本地文件 -> paper-reach 使用 --cookie-file
```

建议使用 Chrome 插件 [Cookie-Editor](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)：

1. 在浏览器里登录目标网站
2. 打开目标论文页面，确认浏览器能访问
3. 用 Cookie-Editor 导出当前域名 cookie
4. 保存为 `cookies.json`
5. 运行：

```bash
paper-reach run \
  --input query.json \
  --output result.json \
  --bundle-dir ./runs/my-topic \
  --cookie-file ./cookies.json \
  --workers 8
```

也可以同时提供 headers：

```bash
paper-reach run \
  --input query.json \
  --output result.json \
  --bundle-dir ./runs/my-topic \
  --cookie-file ./cookies.json \
  --header-file ./headers.json
```

Cookie 只保存在你本地，不要提交到 GitHub，也不要发送给不可信的人。

## English

Paper-Reach is a skill-oriented literature review scaffold for AI coding agents.

It helps agents:

- retrieve candidate papers from OpenAlex, arXiv, or local files
- screen papers conservatively using title and abstract evidence
- fetch full text when available
- review downloaded PDFs or fall back to abstract-level review
- rank papers with task-specific profiles
- export both full JSON and compact human-readable shortlists

Minimal usage:

```bash
pip install -e .[dev]
paper-reach example-query > query.json
paper-reach run \
  --input query.json \
  --output result.json \
  --bundle-dir ./runs/demo \
  --high-recall \
  --retrieval-limit 200 \
  --workers 8
paper-reach summarize --input result.json --output brief.json --format brief --top-k 20
```

Optional OpenAlex full-text access:

```bash
export OPENALEX_API_KEY=your_key
```

When configured, Paper-Reach tries the OpenAlex Content API first and falls back to normal open-access download strategies when quota or content is unavailable.

## 支持平台

| 类型 | 默认可用 | 配置后增强 | 说明 |
|------|---------|-----------|------|
| OpenAlex metadata | 是 | OpenAlex Content API | 用于检索、摘要、venue、开放获取信息 |
| OpenAlex PDF | 否 | 需要 `OPENALEX_API_KEY` | 优先下载 `content.openalex.org` PDF |
| arXiv | 是 | 无 | 适合作为补充检索源 |
| 本地 PDF / TXT | 是 | 无 | 离线模式可直接筛选用户提供文件 |
| 本地 JSON metadata | 是 | 无 | 支持用户已有 DOI/title/metadata 列表 |
| 出版社网页 | 部分 | Cookie / header | 可尝试开放 PDF、landing page、已授权会话 |
| Codex / OpenAI 风格宿主 | 是 | `scripts/sync.sh` | 读取 `SKILL.md` 和 `agents/openai.yaml` |
| Claude Code 风格宿主 | 是 | `scripts/sync.sh` | 读取 `.claude-plugin/plugin.json` |
| OpenClaw / Cursor 等 | 是 | 需要能执行 CLI | Agent 读 Skill 后调用 `paper-reach` |

不知道怎么配？直接告诉 Agent：

```text
帮我用 Paper-Reach 跑这个 query，先粗筛 200 篇，再下载能下载的全文，最后输出 top 20 brief 结果。
```

如果需要 Cookie：

```text
我已经用 Cookie-Editor 导出了 cookies.json，请用 --cookie-file ./cookies.json 运行 Paper-Reach。
```

## 设计理念

### Paper-Reach 是脚手架，不是重型框架

这个项目不试图做一个庞大的自治多 Agent 系统。它只把文献筛选里最容易混乱的部分标准化：

- 怎么检索
- 怎么粗筛
- 怎么下载全文
- 怎么在证据不足时保守处理
- 怎么输出人能看、Agent 也能继续用的结果

### 证据强度必须分层

Paper-Reach 默认区分：

- title-only relevance
- abstract-supported relevance
- full-text-supported relevance

标题相关不能直接进入最终结论。摘要相关可以进入候选池。只有摘要或全文支持足够强时，才应该进入最终名单。

### 下载失败不是流程失败

现实里很多论文没有开放 PDF，或者需要机构认证。Paper-Reach 的设计不是强行下载所有论文，而是：

- 能下载就做全文细筛
- 下载不了就做摘要级细筛
- 明确记录 `fulltext_status`
- 不把弱证据伪装成强证据

### 同时服务 Agent 和人

完整 JSON 用于复现、调试和后续 Agent 处理。`brief` / `titles` 输出用于人快速浏览。

这就是为什么 Paper-Reach 同时保留：

- `30_result_full.json`
- `40_result_brief.json`
- `50_result_titles.json`

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

关键目录：

- `paper_reach/`：CLI、workflow、models、ranking、fetchers、parsers
- `skills/`：paper-search、paper-reader、paper-ranker
- `docs/`：安装、使用、架构、发布和路线图
- `examples/`：query 示例、agent recipes、auth 示例
- `scripts/`：skill 同步和安装检查脚本

## 文档

- [docs/install.md](docs/install.md)
- [docs/usage.md](docs/usage.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/agent-integration.md](docs/agent-integration.md)
- [docs/browser-cookies.md](docs/browser-cookies.md)
- [docs/publishing.md](docs/publishing.md)
- [docs/roadmap.md](docs/roadmap.md)

## 贡献

欢迎 PR 和 issue，尤其是这些方向：

- 更好的 scholarly backend
- 更稳定的全文下载回退策略
- 更强的 abstract / full-text evidence extraction
- 更合理的 ranking profile
- 更好的 Codex / Claude / OpenClaw 兼容性

项目原则：保持简单、模块化、证据导向，不把它做成笨重的自治研究平台。
