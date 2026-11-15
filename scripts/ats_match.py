#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JD keyword match score for same-version regression only (rulebook R15).

Usage:
    python ats_match.py <jd-file> <resume.pdf|docx|txt>

The score is a trend estimate, not a platform score, and never an optimization
target. Deleting content shifts the weighted first third forward and inflates
the number; moving the skills section to the end lowers it without changing any
keyword hit. Explain such changes by word-level diff, do not add words back.

Tokenization:
- English tokens count from a single occurrence (JD usually mentions MySQL once)
- Chinese 2-4 char n-grams need >= 2 occurrences to suppress noise
- Recruiting boilerplate is filtered by a stop-word list
"""
import collections
import re
import sys

STOP = set("""
的 了 和 与 及 或 是 在 对 为 有 并 等 我们 你们 他们 能够 具备 熟悉 了解 掌握 负责
要求 优先 相关 经验 能力 良好 以上 以及 使用 熟练 进行 岗位 任职 职责 描述 工作
开发 人员 公司 面试 加分 满足 具有较强 沟通 协作 学习 团队 意识 精神 执行 熟练使用
者优先 经验者优 经验者优先 参与 良好的 较强 相关专业 计算机
""".split())


def tokens(text):
    text = text.lower()
    text = re.sub(r"者优先|经验者优先", "，", text)
    en = re.findall(r"[a-z][a-z0-9+#.\-]{1,}", text)
    zh = re.findall(r"[\u4e00-\u9fff]{2,}", text)
    grams = []
    for seg in zh:
        for n in (2, 3, 4):
            grams += [seg[i:i + n] for i in range(len(seg) - n + 1)]
    return [t for t in en + grams if t not in STOP]


def top_keywords(jd, k=12):
    c = collections.Counter(tokens(jd))
    en_set = set(re.findall(r"[a-z][a-z0-9+#.\-]{1,}", jd.lower())) - STOP
    cand_en = [(w, n) for w, n in c.items() if w in en_set and re.match(r"^[a-z]", w)]
    cand_zh = [(w, n) for w, n in c.items()
               if not re.match(r"^[a-z]", w) and n >= 2 and len(w) <= 8]
    cand = cand_en + cand_zh
    cand.sort(key=lambda x: (-x[1], -len(x[0])))
    picked = []
    for w, n in cand:
        if any(w in p or p in w for p in picked):
            continue
        picked.append(w)
        if len(picked) == k:
            break
    return picked


def score(resume, jd):
    resume = resume.lower()
    head = resume[:max(1, len(resume) // 3)]
    kws = top_keywords(jd)
    hit = 0.0
    print(f"{'关键词':<18}{'JD频次':>6}{'前1/3命中':>10}{'命中':>6}")
    for w in kws:
        in_head = w in head
        in_all = w in resume
        hit += 1.5 if in_head else (1.0 if in_all else 0.0)
        print(f"{w:<18}{tokens(jd).count(w):>6}{('是' if in_head else '否'):>10}"
              f"{('是' if in_all else '否'):>6}")
    total = 1.5 * len(kws)
    print(f"\n加权匹配分: {hit / total * 100:.1f}%   (参考区间 65%–85%，不作优化目标)")


def load(path):
    low = path.lower()
    if low.endswith(".pdf"):
        import pymupdf
        with pymupdf.open(path) as doc:
            text = "\n".join(page.get_text() for page in doc)
        return re.sub(r"(?<=[\u4e00-\u9fff])\n(?=[\u4e00-\u9fff])", "", text)
    if low.endswith(".docx"):
        from docx import Document
        return "\n".join(p.text for p in Document(path).paragraphs)
    return open(path, encoding="utf-8").read()


if __name__ == "__main__":
    score(load(sys.argv[2]), load(sys.argv[1]))
