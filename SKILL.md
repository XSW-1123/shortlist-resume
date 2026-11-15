---
name: shortlist-resume
description: |
  把零散的真实经历打磨成一页「能过初筛、扛得住面试官三层追问」的中文简历，并交付 PDF + DOCX + 逐行证据台账。
  Turn scattered, real project facts into a one-page, ATS-readable resume that survives three rounds of interviewer follow-ups, delivered as PDF + DOCX with a line-by-line evidence ledger.
  This skill should be used when a user asks to write, rewrite, tailor, polish, review, or export a resume, CV, 简历, or 履历; prepare a campus-recruitment or internship application; match a resume to a job description; or judge whether a resume will pass first-round screening.
  It proactively interviews the user for the necessary facts (basics, education, target role and JD, project source code, verifiable numbers, awards), writes nothing that cannot be traced to a source, then applies 18 hard rules, an adversarial interviewer review, and an automated validator before delivery.
agent_created: true
---

# Shortlist Resume / 简历打磨工作流

## Purpose / 目标

Produce a one-page, text-layer Chinese resume that a screener can parse and an interviewer can drill into three layers deep. Every line must have a source. The skill turns a structured conversation into a single content source (`source.yaml`), renders it, then machine-verifies the delivery.

产出的是「一页、文本型可解析、每一行都能被追问出技术细节」的简历。核心不是把话说漂亮，而是让每一句都有出处、且扛得住追问。

## When to use / 触发场景

- 写、改、定制、复查、导出简历 / CV / 履历
- 校招、实习、社招投递前按 JD 定向
- 判断简历能否过初筛、有没有减分行
- 已有简历要重排版或转 PDF / DOCX

不适用：虚构经历或数字、代投递、面向欧美市场的纯英文 resume 措辞（本 skill 的版式与规则针对中文招聘市场）。

## Non-negotiable constraints / 红线

1. 不编造经历、工具、数字、奖项、部署或压测结论。未知字段写 `[需确认]` 并返回给用户，不靠推断补齐。
2. 只有一个内容源 `source.yaml`；禁止手工改 PDF / DOCX / `.typ` 产物。
3. 每个技术词须同时有「权重来源」（JD 条目或岗位 P0 清单）与「可核验来源」（源码文件行号、命令输出、URL 或 `evidence/` 记录）。缺一即删。
4. 同一事实全文只有一套数字；两套口径冲突时整组弃用。
5. `scripts/validate.py` 退出码非 0，禁止交付。
6. 展示给用户的是他实际会打开的 `deliver/` 成品，不是 `apps/` 深层产物。

## Workflow / 工作流

### Phase 0 — 主动采集（必做，不得跳过）

Read `references/intake.md`; copy `assets/intake.form.md` into the workspace. Collect information in 2–4 short rounds, at most 4 questions per round, preferring the structured question tool. Minimum required: 姓名与联系方式、教育背景与排名、目标岗位、一份 JD（或明确「无 JD，按基线」）、1–2 个同技术栈项目及其源码位置、带测量方式的数字、奖项 / 实习。

缺失的硬性字段标 `[需确认]` 并当轮追问；未解决前不进入 Phase 3。把跨方向经历按「整块删除 / 教育背景下 1–2 行略写 / 仅面试口述」三级归类，并在报告里记录去向。

### Phase 1 — JD 拆成考点清单

Read `references/jd-and-keywords.md`. Split the JD into four buckets, extract Top 12 keywords, build the role's P0/P1 word list and the no-evidence blacklist. 无 JD 时用 `references/java-backend-profile.md` 或用户提供的 `role-profile.yaml` 作基线，并在 `report.md` 显式写出该假设。

### Phase 2 — 建证据库

Create `evidence/numbers.md` and `evidence/achievements.md`：每个数字带测量方式，每条项目 bullet 带出处。Copy `assets/report.template.md` to `apps/<date>-<version>/report.md`，逐行填「内容 → 来源 → 面试官权重 → 项目证据 → 三层追问链」。

### Phase 3 — 起草单一内容源

Copy `assets/resume.template.yaml` to `source.yaml`，只填有出处的事实。Apply `references/rulebook.md` R1–R18：标准板块名、`education → projects → skills`、项目板块 ≥ 60% 字符、PQR bullet 且至少一处「为什么 / 边界 / 代价」、渲染 ≤ 2 行、技能栏程度词三级且无「精通」、项目板块非岗位技术词命中 0。

### Phase 4 — 对抗式复核

Read `references/reviewer-checklist.md`，以挑刺面试官视角把 24 条问题逐条跑一遍。每条弱相关行及其处置写入 `report.md`。仍有 blocker 时回到 Phase 3，不带着问题渲染。

### Phase 5 — 渲染

```
python scripts/build_resume.py source.yaml --out apps/<date>-<version>
```

产出 PDF、DOCX、`preview.png`、`resume.typ` 与一份 `source.yaml` 副本。放大目检预览图，查孤字、重叠、截断、溢出第 2 页。

### Phase 6 — 自检与交付

把 4 件产物 + `source.yaml` 复制进 `deliver/`，然后：

```
python scripts/validate.py --deliver deliver --version apps/<date>-<version> [--role-profile role-profile.yaml]
```

逐条修 FAIL 并重跑，直到退出码 0。之后才把 `deliver/` 里的文件呈现给用户，并在投递台账追加一行。绝不让用户默认打开的文件停留在旧版。

## Resource index / 资源索引

| 文件 | 何时读 |
|---|---|
| `references/intake.md` | Phase 0：问什么、按什么顺序、未知项怎么处理 |
| `references/jd-and-keywords.md` | Phase 1：JD 四桶、Top 12、P0/P1、难度闸门 |
| `references/rulebook.md` | Phase 3 及任何规则争议：R1–R18、失败模式、交付 SOP |
| `references/reviewer-checklist.md` | Phase 4：24 条挑刺问题 |
| `references/evidence-ledger.md` | Phase 2：台账格式、引用标准、报告结构 |
| `references/java-backend-profile.md` | 无 JD 或目标为 Java 后端：内置参考档，不是硬编码要求 |
| `assets/intake.form.md` | Phase 0 复制到工作区 |
| `assets/resume.template.yaml` | Phase 3 复制为 `source.yaml` |
| `assets/report.template.md` | Phase 2 复制为 `apps/<version>/report.md` |
| `assets/role-profile.template.yaml` | 非 Java 后端岗位时复制，填 P0 词表与非岗位词表 |
| `assets/demo.yaml` / `assets/demo-jd.md` | 虚构冒烟样例，永不投递 |
| `scripts/build_resume.py` | Phase 5 渲染器 |
| `scripts/validate.py` | Phase 6 校验器，非 0 退出码阻塞交付 |
| `scripts/ats_match.py` | 可选的同版回归匹配分，不作优化目标 |

## Environment / 运行环境

Python 3.10+，依赖 `typst`、`PyYAML`、`python-docx`、`PyMuPDF`：

```
python -m pip install typst pyyaml python-docx pymupdf
```

中文字体由 `source.yaml` 的 `theme.font` 指定；未指定时按操作系统自动探测（Windows 微软雅黑 / macOS 苹方 / Linux Noto Sans CJK SC），也可用 `--font` 覆盖。字体缺失时 Typst 会报错，此时显式指定本机已有的中文字体名即可，不要改用图片或截图充当 PDF。

## Failure modes this workflow exists to prevent / 六类已发生过的失败

| 失败 | 兜住它的机制 |
|---|---|
| 只改措辞不改结构，简历仍旧「内容很杂」 | R1 岗位相关性一票否决 + 校验按板块扫描 |
| 用户打开的一直是根目录旧版 | R13 / R18 + `validate.py` 比对 `deliver/` |
| 为纯净把真实经历删过头 | R4 合法略写承载位 |
| 为略写自造「补充信息」板块 | R2 / R3 标准板块名与顺序 |
| 技术词凭经验选，被追问三层就露馅 | R7–R10 双闸门 + 难度闸门 + 逐行台账 |
| 规则散落、摘要与正文失同步 | 单一执行入口 R1–R18 + 自动校验器 |

新增规则前先问：它兜住的是哪一类已发生过的失败模式？没有对应失败模式的规则不要加。
