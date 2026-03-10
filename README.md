# Paper-Reach

给你的 AI Agent 一套严谨的文献筛选工作流。

`Paper-Reach` 是一个面向 Codex、Claude Code、OpenClaw、Cursor 等智能编码代理的开源 Skill / CLI 项目，重点不是“多搜几个站”，而是把**文献初筛、细筛、证据提取、保守排序**这件事做得更可靠。

它适合这样的场景：
- 先高召回检索 100 到 300 篇候选文献
- 用 abstract 做第一轮保守筛选
- 对可下载全文继续做细筛
- 最终输出结构化 JSON 和适合人工阅读的简版列表

## What's New

- `OpenAlex Content API` 下载链路已接入
- 支持 `run --bundle-dir` 一次输出完整结果包
- 支持 `summarize` 导出 `titles` / `brief` 两种精炼结果
- 支持 profile-based ranking，可按任务定义硬门槛和加权评分
- 支持多宿主 Skill 元数据，适配 Codex / Claude / Gemini 风格宿主

## 核心能力

- ✅ 文献粗筛：基于标题、摘要、年份、来源、研究区做高召回初筛
- ✅ 文献细筛：优先读取已下载全文，没有全文时退回摘要级细筛
- ✅ 保守排序：区分 `selected`、`ambiguous`、`rejected`
- ✅ 证据导向：标题相关不等于真正相关，摘要和全文证据分层处理
- ✅ OpenAlex 优先下载：有 API key 时优先走官方内容接口，失败自动回退
- ✅ 离线可用：支持本地 PDF / TXT / JSON metadata / DOI 列表
- ✅ 面向 Agent：保留 `SKILL.md`、`AGENTS.md`、多宿主 manifest
- ✅ JSON 优先：适合继续被 agent 消费、复查、或接下游分析脚本

## 这个项目解决什么问题

搜索论文很容易，真正难的是：

- 标题看起来相关，但摘要并不支持
- 摘要看起来相关，但全文并没有你要的方法或数据
- 很多文献没有开放 PDF，不能假装“已读全文”
- 最终输出如果只有一大坨 JSON，人根本看不动

`Paper-Reach` 的设计目标就是把这些步骤拆清楚：

1. `screen`
   - 只做摘要级粗筛
2. `fetch-fulltext`
   - 尝试下载全文，优先 OpenAlex content API
3. `review`
   - 结合摘要或全文做保守细筛
4. `summarize`
   - 导出人类可读的精炼清单

## 一个最小示例

```bash
paper-reach doctor
paper-reach example-query > query.json

paper-reach screen \
  --input query.json \
  --output screen.json \
  --high-recall \
  --retrieval-limit 200

paper-reach run \
  --input query.json \
  --output result.json \
  --bundle-dir ./runs/demo \
  --high-recall \
  --retrieval-limit 200 \
  --workers 8

paper-reach summarize \
  --input result.json \
  --output brief.json \
  --format brief
```

## 结果输出长什么样

`run --bundle-dir ./runs/demo` 会产出一个结果包：

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

这里面：

- `30_result_full.json`
  - 给 agent 和程序继续消费的完整版结果
- `40_result_brief.json`
  - 给人看的精炼版，保留标题、链接、年份、decision、原因、venue 等
- `50_result_titles.json`
  - 最短版，只保留标题和链接

## 安装

### 方法 1：本地直接安装 CLI

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
paper-reach doctor
```

### 方法 2：作为 Skill 安装到 Codex / Claude / OpenClaw 风格宿主

```bash
pip install -e .[dev]
bash scripts/sync.sh
bash scripts/check-install.sh
```

默认会同步到：

- `~/.codex/skills/paper-reach`
- `~/.claude/skills/paper-reach`
- `~/.agents/skills/paper-reach`

## OpenAlex 下载增强

如果你配置了 OpenAlex API key，`Paper-Reach` 会优先尝试：

- `content.openalex.org/works/{work_id}.pdf`

没有 key 或额度不足时，会自动回退到原来的下载逻辑，不需要手动切换。

启用方式：

```bash
export OPENALEX_API_KEY=你的_key
```

## 典型使用方式

### 1. 只做粗筛

```bash
paper-reach screen \
  --input query.json \
  --output screen.json \
  --high-recall \
  --retrieval-limit 200
```

### 2. 跑完整工作流

```bash
paper-reach run \
  --input query.json \
  --output result.json \
  --bundle-dir ./runs/my-topic \
  --high-recall \
  --retrieval-limit 200 \
  --workers 8
```

### 3. 只看精炼结果

```bash
paper-reach summarize \
  --input result.json \
  --output titles.json \
  --format titles
```

或：

```bash
paper-reach summarize \
  --input result.json \
  --output brief.json \
  --format brief \
  --top-k 20
```

## 多 AI 工具适配

`Paper-Reach` 不是只给某一个 agent 写的 prompt 仓库，而是按“一个核心执行层 + 多宿主包装层”的方式实现：

- `paper_reach/`
  - 统一执行逻辑，CLI、workflow、ranking、fetchers、parsers
- `SKILL.md`
  - 宿主无关的 Skill 入口
- `agents/openai.yaml`
  - OpenAI / Codex 风格宿主元数据
- `.claude-plugin/plugin.json`
  - Claude 风格插件元数据
- `gemini-extension.json`
  - Gemini 风格扩展元数据

这也是它能同时兼容多种 agent 宿主的原因。

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

- `paper_reach/`
  - Python 包和主逻辑
- `skills/`
  - paper-search / paper-reader / paper-ranker
- `docs/`
  - 安装、架构、使用、路线图、发布说明
- `examples/`
  - 查询示例、agent recipes、auth 示例
- `scripts/`
  - 宿主同步和安装检查脚本

## 为什么不是重型多 Agent 框架

这个项目故意不是“自动组很多 agent 自治研究”的方向。

我更关心的是：

- 把筛选步骤拆清楚
- 让证据强弱可解释
- 没有全文时也能给保守结论
- 让输出既能给 agent 用，也能给人直接看

所以它更像：

- 一个可安装的 Skill 工具
- 一个可复用的文献筛选脚手架
- 一个适合二次开发的 starter repo

而不是：

- 一个上来就很重的自治研究系统

## 文档

- 安装：[docs/install.md](docs/install.md)
- 使用：[docs/usage.md](docs/usage.md)
- 架构：[docs/architecture.md](docs/architecture.md)
- Agent 集成：[docs/agent-integration.md](docs/agent-integration.md)
- 浏览器 Cookie：[docs/browser-cookies.md](docs/browser-cookies.md)
- 发布：[docs/publishing.md](docs/publishing.md)
- 路线图：[docs/roadmap.md](docs/roadmap.md)

## 贡献

欢迎提 issue 和 PR，尤其是这些方向：

- 更好的 scholarly backend
- 更稳定的全文下载与回退策略
- 更强的 abstract / full-text evidence extraction
- 更合理的 ranking profile
- 更好的宿主兼容性

如果你想把它装进自己的 Codex / Claude / OpenClaw 工作流，也欢迎直接 fork 之后按你的场景扩展。
