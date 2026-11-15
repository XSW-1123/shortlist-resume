#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Delivery validator (rulebook R16). Exit code 0 = deliverable, non-zero = blocked.

Usage:
    python validate.py --deliver deliver --version apps/2026-11-15-v1 \
        [--source source.yaml] [--role-profile role-profile.yaml]

Machine-checkable items only. Content truthfulness is verified by the
line-by-line evidence ledger in report.md, not by this script.
"""
import argparse
import re
import sys
from pathlib import Path

import pymupdf
import yaml
from docx import Document

SECTION_TITLES = {"education": "教育背景", "internship": "实习经历",
                  "projects": "项目经历", "skills": "专业技能"}
DEFAULT_ORDER = ["education", "projects", "skills"]
DEFAULT_BANNED = ("补充信息", "其他信息", "荣誉奖项", "科研与荣誉", "个人优势")
WEAK_WORDS = ("精通", "显著提升", "效果良好", "参与开发", "协助完成", "负责开发")
ARTIFACTS = ("preview.png", "resume.typ")

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok)))
    print("  [%s] %-46s %s" % ("OK  " if ok else "FAIL", name, detail if not ok else ""))


def skip(name, reason):
    print("  [SKIP] %-46s %s" % (name, reason))


def pdf_rows(pdf_path):
    page = pymupdf.open(str(pdf_path))[0]
    rows = []
    for block in page.get_text("dict")["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            text = "".join(s["text"] for s in line["spans"]).strip()
            if text:
                rows.append((line["bbox"][1], line["bbox"][3], text))
    rows.sort()
    return page, rows


def stem_of(data):
    raw = data.get("output_stem") or f"{data.get('name', 'resume')}_{data.get('intent', '')}"
    return re.sub(r'[\\/:*?"<>|\r\n\t]', "_", str(raw)).strip(" _") or "resume"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deliver", required=True, help="directory holding the files the user opens")
    ap.add_argument("--version", default=None, help="apps/<date>-<version> directory")
    ap.add_argument("--source", default=None, help="root source.yaml")
    ap.add_argument("--role-profile", default=None, help="role-profile.yaml")
    args = ap.parse_args()

    deliver = Path(args.deliver)
    version = Path(args.version) if args.version else None
    profile = yaml.safe_load(Path(args.role_profile).read_text(encoding="utf-8")) if args.role_profile else {}

    order_keys = profile.get("section_order") or DEFAULT_ORDER
    expected_titles = [SECTION_TITLES[k] for k in order_keys if k in SECTION_TITLES]
    banned = tuple(profile.get("banned_sections") or DEFAULT_BANNED)
    min_ratio = float(profile.get("min_project_ratio", 60))
    p0 = list(profile.get("p0_words") or [])
    off_stack = list(profile.get("off_stack_words") or [])
    known_titles = set(SECTION_TITLES.values()) | set(banned)

    print("=== validate · shortlist-resume / R16 ===")
    if not deliver.is_dir():
        print("FATAL: deliver 目录不存在: %s" % deliver)
        sys.exit(2)
    src = deliver / "source.yaml"
    if not src.exists():
        print("FATAL: deliver/source.yaml 缺失（单一内容源，R13）")
        sys.exit(2)
    data = yaml.safe_load(src.read_text(encoding="utf-8"))
    stem = stem_of(data)
    pdf_name, docx_name = f"{stem}.pdf", f"{stem}.docx"
    pdf_path, docx_path = deliver / pdf_name, deliver / docx_name

    # 1. 单一内容源 / 交付链路一致性（R13 / R18）
    check("deliver 含 PDF/DOCX/preview/typ/source",
          pdf_path.exists() and docx_path.exists()
          and all((deliver / f).exists() for f in ARTIFACTS) and src.exists())
    if args.source:
        root_src = Path(args.source)
        check("根 source.yaml == deliver/source.yaml",
              root_src.exists() and root_src.read_bytes() == src.read_bytes())
    else:
        skip("根 source.yaml == deliver/source.yaml", "未传 --source")

    if version and version.is_dir():
        same = [f for f in [pdf_name, docx_name] + list(ARTIFACTS) + ["source.yaml"]
                if (version / f).exists() and (deliver / f).exists()
                and (version / f).read_bytes() == (deliver / f).read_bytes()]
        check("deliver 五件 == apps/<version> 字节", len(same) == 5, "一致 %d/5" % len(same))
        check("deliver PDF 文本层 == apps/<version>",
              (version / pdf_name).exists()
              and "\n".join(t for _, _, t in pdf_rows(version / pdf_name)[1])
              == "\n".join(t for _, _, t in pdf_rows(pdf_path)[1]))
        report = version / "report.md"
        body = report.read_text(encoding="utf-8") if report.exists() else ""
        check("report.md 含逐行证据台账", "证据台账" in body or "evidence ledger" in body.lower(),
              "缺 report.md 或台账章节" if not body else "台账章节缺失")
    else:
        skip("交付链路一致性", "未传 --version")
        skip("report.md 含逐行证据台账", "未传 --version")

    # 2. 内容源规则（R2 / R3）
    src_order = data.get("section_order") or DEFAULT_ORDER
    check("source.yaml 只用标准板块键",
          all(k in SECTION_TITLES for k in src_order), str(src_order))
    check("source.yaml 板块顺序符合岗位档",
          [SECTION_TITLES[k] for k in src_order if k in SECTION_TITLES] == expected_titles,
          "实得 %s 期望 %s" % (src_order, expected_titles))
    check("source.yaml 无未确认字段", "[需确认]" not in src.read_text(encoding="utf-8"))

    # 3. PDF 可解析性（R14）
    page, rows = pdf_rows(pdf_path)
    full = "\n".join(t for _, _, t in rows)
    with pymupdf.open(str(pdf_path)) as doc:
        pages = doc.page_count
    check("1 页 A4 / 文本型 / 中文可提取 / 无替换符",
          pages == 1 and "\ufffd" not in full
          and re.search(r"[\u4e00-\u9fff]", full) is not None,
          "页数 %d / 替换符 %d" % (pages, full.count("\ufffd")))

    # 4. 板块命名与顺序（R2 / R3）
    sections = [t for _, _, t in rows if t in known_titles]
    check("PDF 板块顺序 == 岗位档", sections == expected_titles, "实得 %s" % sections)
    check("自造板块名命中 0", sum(full.count(w) for w in banned) == 0)
    docx_sections = [p.text.strip() for p in Document(str(docx_path)).paragraphs
                     if p.text.strip() in known_titles]
    check("DOCX 板块顺序一致", docx_sections == expected_titles, "实得 %s" % docx_sections)

    # 5. 项目板块占比、留白、bullet 行数（R3 / R11 / R14）
    marks = [(i, t) for i, (_, _, t) in enumerate(rows) if t in known_titles]
    proj_mark = next((i for i, (_, t) in enumerate(marks) if t == "项目经历"), None)
    if proj_mark is None:
        check("项目板块存在", False, "未找到 项目经历 标题")
        proj_rows, proj = [], ""
    else:
        start = marks[proj_mark][0]
        end = marks[proj_mark + 1][0] if proj_mark + 1 < len(marks) else len(rows)
        proj_rows = rows[start:end]
        proj = "\n".join(t for _, _, t in proj_rows)
    ratio = len(proj) / max(1, len(full)) * 100
    check("项目板块占比 ≥ %.0f%%" % min_ratio, ratio >= min_ratio, "实测 %.1f%%" % ratio)
    max_y = max((y1 for _, y1, _ in rows), default=0)
    blank = (page.rect.height - max_y) / page.rect.height * 100
    check("底部留白 5–15%", 5 <= blank <= 15, "实测 %.1f%%" % blank)
    starts = [i for i, (_, _, t) in enumerate(proj_rows) if t.startswith("•")]
    over = [k for k, i in enumerate(starts)
            if (starts[k + 1] if k + 1 < len(starts) else len(proj_rows)) - i > 2]
    check("项目 bullet 全部 ≤ 2 行", not over and len(starts) > 0,
          "bullet %d 条 / 超长 %s" % (len(starts), over))

    # 5.5 R19：项目块三层标签 + 条内局部加粗
    # 用 span 级 bold flag 核验（文本层看不出加粗，这正是「整条加粗 / 只加粗小标题」
    # 这类退化能混过去的原因）。
    BOLD = 16
    lb = {"tech_stack": "技术栈", "desc": "项目简介", "highlights": "技术亮点"}
    lb.update(data.get("labels") or {})
    spans = []
    for _b in page.get_text("dict")["blocks"]:
        for _l in _b.get("lines", []):
            _sp = [(s["text"], bool(s["flags"] & BOLD))
                   for s in _l["spans"] if s["text"].strip()]
            if _sp:
                spans.append((_l["bbox"][1], "".join(t for t, _ in _sp).strip(), _sp))
    if proj_rows:
        lo, hi = proj_rows[0][0], proj_rows[-1][0] + 1
        block = [(t, sp) for y, t, sp in spans if lo <= y < hi]
    else:
        block = []
    found = {t.split("　")[0] for t, _ in block if t.split("　")[0] in lb.values()}
    check("项目块三层标签齐备", found == set(lb.values()), "实得 %s" % sorted(found))
    lab = [(t, sp) for t, sp in block if t.split("　")[0] in lb.values()]
    check("标签本身加粗", all(sp[0][1] for _, sp in lab if sp),
          "未加粗 %s" % [t[:6] for t, sp in lab if sp and not sp[0][1]])
    w = lambda s: sum(1.0 if ord(c) > 0x2E80 else 0.55 for c in s)
    pbul = [(t, sp) for t, sp in block if t.startswith("•")]
    thin = [t[:14] for t, sp in pbul if sum(1 for x, b in sp if b) < 2]
    check("每条 bullet ≥ 2 处局部加粗", not thin, "偏少 %s" % thin)
    fat = [t[:14] for t, sp in pbul
           if w("".join(x for x, b in sp if b)) / max(w(t), 1) > 0.45]
    check("无整条加粗（粗体视觉宽度 ≤ 45%）", not fat, "过粗 %s" % fat)

    # 6. 岗位相关性与词表（R1 / R7 / R9）
    # 视觉换行与中英混排空格会影响逐字比对，两侧统一去掉全部空白后再比。
    norm = lambda s: re.sub(r"\s+", "", str(s))
    proj_flat, full_flat = norm(proj), norm(full)
    if off_stack:
        hits = [(w, proj_flat.count(norm(w))) for w in off_stack if norm(w) in proj_flat]
        check("项目板块非岗位技术词 0", not hits, str(hits))
    else:
        skip("项目板块非岗位技术词 0", "岗位档未提供 off_stack_words")
    if p0:
        miss = [w for w in p0 if norm(w) not in full_flat]
        check("P0 词表全命中", not miss, "缺 %s" % miss)
    else:
        skip("P0 词表全命中", "岗位档未提供 p0_words")
    weak = [w for w in WEAK_WORDS if norm(w) in full_flat]
    check("无「精通」及弱动词", not weak, str(weak))

    fails = [n for n, ok in results if not ok]
    print("\n汇总: %d 项检查，%d OK / %d FAIL" %
          (len(results), len(results) - len(fails), len(fails)))
    if fails:
        print("未通过: " + "、".join(fails))
        print("按 R16，全绿且退出码 0 前禁止交付。")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
