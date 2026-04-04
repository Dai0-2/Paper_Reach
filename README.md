# Paper-Reach

给你的 AI Agent 一套严谨的文献综述工作流。

`Paper-Reach` 是一个面向 Codex、Claude Code、OpenClaw、Cursor 等智能编码代理的开源 Skill / CLI 项目，用来完成文献检索、摘要初筛、全文细筛、证据抽取和保守排序。

它的重点不是“多搜几个来源”，而是让 agent 能够更可靠地判断一篇论文到底是不是符合你的纳入标准。

[快速开始](#快速开始) · [English](#english) · [支持平台](#支持平台) · [设计理念](#设计理念)

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

导出适合人看的简版：

```bash
paper-reach summarize \
  --input result.json \
  --output brief.json \
  --format brief \
  --top-k 20
```

`--bundle-dir` 会生成：

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

---

## English

Paper-Reach can be used fully in English.

The CLI commands, JSON schema, skill files, and most documentation are English-friendly. The repository README is Chinese-first because the current primary users are Chinese-speaking agent builders, but the project itself is designed for international use.

Typical English prompt to an agent:

```text
Use Paper-Reach to run a high-recall literature screening workflow. Keep decisions conservative, fetch full text when possible, and export both a full JSON result and a brief shortlist.
```

---

## 支持平台

| 平台 / 来源 | 当前支持 | 增强方式 |
|---|---|---|
| OpenAlex | 元数据检索、摘要初筛、content API 下载 | 配置 `OPENALEX_API_KEY` |
| arXiv | 检索与元数据获取 | 无需额外配置 |
| 本地 PDF / TXT / JSON | 离线初筛和细筛 | 无需额外配置 |
| 出版社落地页 | 尝试 OA 链接和页面解析 | 可提供 cookie / header |
| Codex / OpenAI 风格宿主 | 可识别 `SKILL.md` 和 `agents/openai.yaml` | `bash scripts/sync.sh` |
| Claude 风格宿主 | 支持 `.claude-plugin/plugin.json` | `bash scripts/sync.sh` |
| Gemini 风格宿主 | 支持 `gemini-extension.json` | `bash scripts/sync.sh` |

### 需要 Cookie 的平台怎么处理

有些出版社或机构访问入口需要浏览器登录、机构授权或人机验证。

推荐统一流程：

**浏览器登录 -> Cookie-Editor 导出 Cookie -> 发给 Agent / 作为参数传给 Paper-Reach**

具体做法：

1. 用 Chrome 打开目标网站并登录
2. 安装 Chrome 插件 `Cookie-Editor`
3. 导出当前域名 cookie，保存为 `cookies.json`
4. 运行：

```bash
paper-reach fetch-fulltext \
  --input query.json \
  --output review.json \
  --download-dir ./downloads \
  --cookie-file ./cookies.json
```

这样通常比让 agent 扫码、模拟登录或处理验证码更稳定。

注意：

- cookie 只在本地使用
- cookie 不是必须项
- 没有 cookie 时，系统仍然会自动退回到开放获取下载和摘要级细筛

更多说明见：[docs/browser-cookies.md](docs/browser-cookies.md)

---

## 设计理念

Paper-Reach 不是一个很重的自治多智能体系统。

它更像：

- 一个可安装的文献筛选 Skill
- 一个可复用的 Python CLI
- 一个适合二次开发的 literature workflow scaffold

核心设计原则：

- **搜索很容易，筛选才难**
  - 项目的价值不是更多来源，而是更好的筛选
- **弱证据不能被说成强证据**
  - 标题相关不能直接等于论文符合条件
- **摘要证据和全文证据必须分层**
  - 摘要只能支撑粗筛，全文才更适合强结论
- **离线模式很重要**
  - 没网、没有 PDF、只有本地 metadata 时也应该能用
- **JSON first**
  - 输出应当能继续被 agent、脚本和下游分析流程消费
- **人也要能看**
  - 所以保留 `brief` 和 `titles` 两种简版输出

---

## 核心能力

- 高召回文献检索与 query expansion
- 摘要级保守初筛
- 可选全文下载和全文细筛
- OpenAlex content API 优先下载，失败自动回退
- profile-based ranking，支持硬门槛和加权评分
- `titles` / `brief` 两种人类可读导出
- 完整 JSON 输出，适合 agent 和下游程序继续处理

## 一个具体例子

目标：

> 找到“在中国使用静态人口或栅格人口做灾害、流感、传染病暴露评估”的论文，用来作为动态人口方法的基线对照。

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

## OpenAlex 下载增强

如果配置了：

- `OPENALEX_API_KEY`
- 或 `OPENALEX_CONTENT_API_KEY`

Paper-Reach 会优先尝试 OpenAlex 官方 content API：

```bash
export OPENALEX_API_KEY=your_key
```

下载顺序：

1. OpenAlex content API
2. 开放获取 PDF URL
3. landing page 解析
4. cookie / header 会话复用
5. 摘要级 fallback

这个 key 是可选增强，不是硬依赖。

## 多宿主 Skill 支持

Paper-Reach 采用“一个核心执行层 + 多宿主包装层”的结构：

- `paper_reach/`
  - CLI、workflow、ranking、fetchers、parsers
- `SKILL.md`
  - 宿主无关的 skill 入口
- `agents/openai.yaml`
  - Codex / OpenAI 风格元数据
- `.claude-plugin/plugin.json`
  - Claude 风格元数据
- `gemini-extension.json`
  - Gemini 风格扩展元数据

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

## 贡献

欢迎提交 issue 和 PR，尤其是这些方向：

- 更强的筛选质量
- 更好的全文证据抽取
- 更多 scholarly backend
- 更稳定的下载回退逻辑
- 更顺滑的 agent 集成体验
