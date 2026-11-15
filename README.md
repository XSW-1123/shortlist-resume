# shortlist-resume

**Stop listing skills. Start getting shortlisted.**
**别再罗列技能了，把简历写成面试官愿意深挖的那一页。**

一个**不绑定任何平台的通用简历技能包**：遵循 `SKILL.md` 约定，可放进任意兼容的 Agent 技能目录；也可以完全不用 Agent，直接跑 Python 脚本。它先主动把你的真实经历问清楚，再把每一行都钉在可核验的出处上，最后交付一页、机器可解析、扛得住三层追问的中文简历。
A **platform-agnostic resume skill package**: drop it into any `SKILL.md`-compatible agent's skills directory, or run the Python scripts standalone with no agent at all. It interviews you for the facts, pins every line to a verifiable source, then ships a one-page, ATS-readable Chinese resume that survives three rounds of interviewer follow-ups.

---

## 它到底做什么 / What it actually does

| 阶段 | 动作 |
|---|---|
| Intake | 分 2–4 轮、每轮最多 4 个问题，收集基本信息、教育硬指标、目标岗位与 JD、同栈项目源码位置、带测量方式的数字、奖项实习。答不上来就标 `[需确认]`，不替你猜。 |
| Evidence | 建 `evidence/numbers.md` + `evidence/achievements.md`，每个数字写清怎么测的；每个技术词必须同时有「面试官权重来源」和「项目源码出处」。 |
| Rules | 18 条现行硬规则（R1–R18）：标准板块名与顺序、项目板块 ≥ 60% 字符、PQR bullet 且必须写「为什么 / 边界 / 代价」、渲染 ≤ 2 行、程度词三级、项目板块非岗位技术词 0。 |
| Review | 24 条挑刺面试官问题逐条跑一遍：7 秒首屏、一票否决、逐行审计、三层追问、弱动词、数字口径、交付链路。 |
| Render | 一条命令出 PDF（Typst，文本层可复制）+ DOCX（无表格）+ 150dpi 预览图 + 内容源副本。 |
| Validate | 自动校验页数、文本层、板块顺序（PDF 与 DOCX 一致）、项目占比、底部留白、bullet 行数、词表覆盖、弱词、根目录交付一致性、证据报告存在性。**退出码非 0 禁止交付。** |

| Stage | What happens |
|---|---|
| Intake | 2–4 short rounds, at most 4 questions each: basics, education, target role and JD, same-stack project source locations, metrics with measurement methods, awards. Unknowns stay `[需确认]`; nothing is guessed. |
| Evidence | Every number gets a measurement method; every technical term needs both a weight source (JD item / P0 list) and a verifiable source (file + line, command output, URL). |
| Rules | 18 active hard rules: standard section names and order, projects ≥ 60% of characters, PQR bullets with an explicit why / boundary / cost, ≤ 2 rendered lines, graded proficiency verbs, zero off-stack terms in the project section. |
| Review | 24 hostile-interviewer questions: 7-second first screen, relevance veto, line-by-line audit, three-layer follow-ups, weak verbs, number consistency, delivery chain. |
| Render | One command produces a text-layer PDF, a table-free DOCX, a 150dpi preview, and a copy of the content source. |
| Validate | Automated checks on page count, text layer, section order in both PDF and DOCX, project ratio, bottom whitespace, bullet line count, keyword coverage, weak words, root-delivery consistency, and evidence report. A non-zero exit code blocks delivery. |

## 为什么值得试 / Why people try it

- **它先问，再写。** 大多数简历工具上来就替你编；这个先追问「这个数字怎么测的」「这段实现的源码在哪一行」，问不出来就不写。
  It asks before it writes. No invented projects, no invented QPS, no "improved significantly".
- **每个词都要过两道门。** 面试官会问到什么（权重）+ 你项目里真的有吗（证据），缺一道就删。写不实在 AI 面试官面前是致命的。
  Every term passes two gates: interviewer weight and verifiable evidence. Missing either, it is deleted.
- **它按挑刺面试官的思路复查自己。** 内置 24 条反面问题，专门找「功能清单式 bullet」「自造板块名」「为凑版面塞水货」「根目录其实还是旧版」这类真实翻车点。
  It reviews its own draft as a hostile interviewer, hunting the exact failure modes that got real resumes rejected.
- **交付是机器验过的。** 用户实际打开的 `deliver/` 与推荐版逐字比对，不是「生成完就扔在深层目录」。
  The file the user actually opens is byte-checked against the recommended version, not buried in a nested build folder.
- **自带可跑通的虚构样例。** 30 秒看到成品长什么样，再决定要不要填自己的信息。
  A bundled fictional demo renders end-to-end in about 30 seconds.

## 它不做什么 / What it will not do

- 不保证面试邀请或 offer，也不声称「面试官一定喜欢」；它保证的是每一行有出处、能扛追问、版式可解析。
  It does not guarantee an interview or an offer. It guarantees traceable lines, defensible depth, and a parseable layout.
- 不编造经历、工具、数字、部署或压测结论；缺信息就返回给你确认。
  It never fabricates experience, tools, metrics, deployment, or benchmark claims.
- 不做代投递、不做英文简历的本土化措辞；版式与规则针对中文招聘市场（一页 A4、文本型 PDF、标准板块名）。
  No auto-applying, no Western-market English resume conventions. The layout and rules target the Chinese hiring market.
- 匹配分只是同版回归工具，不是优化目标；不会为刷分加词。
  The keyword match score is a regression tool, never an optimization target.
- 内置的 Java 后端参考档是「有出处的样例基线」，不是硬编码要求；其他岗位用 `role-profile.yaml` 现场生成词表。
  The bundled Java-backend profile is a sourced reference, not a hard-coded requirement. Other roles generate their own profile.

## 安装 / Install

不依赖任何特定产品，两种用法任选。No vendor lock-in — pick either path.

**方式一 · 作为 Agent 技能包** / As an agent skill package（任何支持 `SKILL.md` + YAML frontmatter 约定的 Agent 都能加载）：

```bash
git clone https://github.com/XSW-1123/shortlist-resume.git
cp -r shortlist-resume "$AGENT_SKILLS_DIR"/
```

Windows 同理，把整个 `shortlist-resume/` 目录复制进你的 Agent 读取技能的目录即可。加载后在对话里说「帮我写一份 Java 后端实习简历」「按这份 JD 改简历」「检查我的简历能不能过初筛」即可触发。
Then say "write me a resume for a Java backend internship", "tailor my resume to this JD", or "will my resume pass first-round screening".

**方式二 · 纯命令行** / Standalone CLI（完全不需要 Agent，`SKILL.md` 与 `references/` 当人工 SOP 读，或喂给任意模型）：

```bash
git clone https://github.com/XSW-1123/shortlist-resume.git
cd shortlist-resume
python -m pip install typst pyyaml python-docx pymupdf
cp assets/resume.template.yaml source.yaml   # 填写真实信息
python scripts/build_resume.py source.yaml --out deliver
python scripts/validate.py --deliver deliver
```

依赖仅 Python 3.10+ 与 4 个 pip 包，跨平台可用；中文字体按操作系统自动探测，也可在 `source.yaml` 的 `theme.font` 指定。
Only Python 3.10+ and four pip packages; works on Windows, macOS and Linux. The CJK font is auto-detected and can be overridden via `theme.font`.

## 使用 / Use

```
你：帮我做一份简历，目标岗位是 <岗位>，JD 在 jd.md
skill：分轮提问 → 核验源码 → 建证据库 → 起草 source.yaml → 24 条挑刺复核 → 渲染 → 自动校验
你：拿到 deliver/ 下的 PDF + DOCX + preview.png，以及逐行证据台账 report.md
```

中间任何一步都可以打断：`[需确认]` 的字段会明确列出，不会静默填成看起来很像真的假数据。
Every unresolved field is listed explicitly; nothing is silently filled with plausible-looking fiction.

## 30 秒自测 / Run the bundled demo

```bash
python scripts/build_resume.py assets/demo.yaml --out /tmp/demo-build
cp assets/demo.yaml /tmp/demo-build/source.yaml
python scripts/validate.py --deliver /tmp/demo-build --role-profile assets/demo-role-profile.yaml
```

`demo.yaml` 的人物、学校、项目与数字全部虚构，只用来证明链路能跑通，不可投递。
The demo person, school, project, and numbers are fictional and must never be submitted.

## 规则从哪来 / Where the rules come from

这套规则不是凭经验拍的：它来自 5 份同届高分简历样本、批注版简历标准、一组 2026 年面试官偏好检索（E1–E10，完整 URL 见 `references/java-backend-profile.md`）、一份真实项目源码的逐行核验，以及六轮用户反馈的失败模式登记（`references/rulebook.md` 0.2）。每条现行规则都能追溯到一次真实翻车。
Every active rule traces back to a documented failure mode, an observable sample, or a verifiable source; the registry is in `references/rulebook.md` section 0.2.

## 目录 / Layout

```
shortlist-resume/
├── SKILL.md                      唯一执行入口（中英双语）
├── references/                   rulebook / intake / jd-and-keywords / reviewer-checklist / evidence-ledger / java-backend-profile
├── scripts/                      build_resume.py / validate.py / ats_match.py
└── assets/                      内容源模板 / 采集表 / 报告模板 / 岗位档模板 / 虚构 demo
```

## 许可 / License

MIT. 见 `LICENSE`。
