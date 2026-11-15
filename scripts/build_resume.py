#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""source.yaml -> one-page Chinese resume (PDF via Typst + DOCX + preview).

Usage:
    python build_resume.py source.yaml [--out apps/2026-11-15-v1] [--font "Microsoft YaHei"]

Design constraints (rulebook R14):
- single column, no tables / text boxes / colour blocks in the text body
- one A4 page, text-layer PDF, DOCX without tables when there is no photo
- section order is driven by source.yaml; only standard section keys are accepted
- naming, font, target role and graduation year come from config, never hard-coded
"""
import argparse
import os
import re
import shutil
import sys
from pathlib import Path

import typst
import yaml
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

DEFAULT_THEME = {
    "ink": "1f2328",
    "accent": "1f4e79",
    "muted": "5f6b7a",
    "faint": "8a94a3",
    "rule": "d8dee6",
}

SECTION_TITLES = {
    "education": "教育背景",
    "internship": "实习经历",
    "projects": "项目经历",
    "skills": "专业技能",
}
DEFAULT_ORDER = ["education", "projects", "skills"]

_ESC = {"\\": r"\\", "#": r"\#", "$": r"\$", "[": r"\[", "]": r"\]", "{": r"\{",
        "}": r"\}", "*": r"\*", "_": r"\_", "`": r"\`", "@": r"\@", "~": r"\~",
        "<": r"\<", ">": r"\>"}


def esc(text) -> str:
    """Escape Typst control characters in plain text."""
    return "".join(_ESC.get(ch, ch) for ch in str(text))


def rich(text) -> str:
    """Convert **bold** spans to Typst #strong[]; newlines become #linebreak().

    换行是内容源里少数合法的排版指令：技能栏每行都接近满宽，个别行折出来的尾字
    太少（只剩 5–6 字），用显式换行把两行调匀，比硬压内容或让排版随机折好看。
    """
    text = str(text)
    out, i = [], 0
    while True:
        a = text.find("**", i)
        if a < 0:
            out.append(esc(text[i:]))
            break
        out.append(esc(text[i:a]))
        b = text.find("**", a + 2)
        if b < 0:
            out.append(esc(text[a:]))
            break
        out.append("#strong[" + esc(text[a + 2:b]) + "]")
        i = b + 2
    return "".join(out).replace("\n", "#linebreak()")


def resolve_font(config_font=None, cli_font=None) -> str:
    """Pick a CJK font available on this machine; config and CLI both override."""
    if cli_font:
        return cli_font
    if config_font:
        return config_font
    if sys.platform == "win32":
        for path, name in (("C:/Windows/Fonts/msyh.ttc", "Microsoft YaHei"),
                           ("C:/Windows/Fonts/msyhl.ttc", "Microsoft YaHei Light"),
                           ("C:/Windows/Fonts/simsun.ttc", "SimSun")):
            if Path(path).exists():
                return name
        return "Microsoft YaHei"
    if sys.platform == "darwin":
        return "PingFang SC" if Path("/System/Library/Fonts/PingFang.ttc").exists() else "Songti SC"
    for path in ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                 "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf",
                 "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"):
        if Path(path).exists():
            return "Noto Sans CJK SC"
    return "Noto Sans CJK SC"


def stem_of(data) -> str:
    raw = data.get("output_stem") or f"{data.get('name', 'resume')}_{data.get('intent', '')}"
    cleaned = re.sub(r'[\\/:*?"<>|\r\n\t]', "_", str(raw)).strip(" _")
    return cleaned or "resume"


def order_of(data):
    order = data.get("section_order") or list(DEFAULT_ORDER)
    unknown = [k for k in order if k not in SECTION_TITLES]
    if unknown:
        raise SystemExit("不支持的板块键 %s；只允许 %s（R2 禁止自造板块名）"
                         % (unknown, list(SECTION_TITLES)))
    return order


def spacing_of(data):
    relaxed = data.get("spacing") == "relaxed"
    return {
        "sec_gap": "0.85em" if relaxed else "0.5em",
        "bul_gap": "4.6pt" if relaxed else "3.0pt",
        "skill_gap": "4.8pt" if relaxed else "3.2pt",
        "leading": data.get("leading") or ("0.38em" if data.get("summary") else "0.32em"),
    }


def bullets(items, gap, accent) -> str:
    parts = []
    for it in items or []:
        parts.append(
            f'#v({gap})\n'
            '#grid(columns: (0.9em, 1fr), column-gutter: 0.12em,'
            ' align: (left + top, left),\n'
            f'  [#text(size: 10pt, fill: rgb("#{accent}"))[•]],\n'
            f'  [#text(size: 10pt)[{rich(it)}]]\n)'
        )
    return "\n".join(parts)


def section(title, body, gap, theme) -> str:
    return (
        f'#v({gap})\n'
        f'#text(size: 11pt, weight: "bold", tracking: 0.14em,'
        f' fill: rgb("#{theme["accent"]}"))[{esc(title)}]\n'
        f'#v(0.22em)\n'
        f'#line(length: 100%, stroke: 0.7pt + rgb("#{theme["rule"]}"))\n'
        f'#v(0.42em)\n'
        f"{body}\n"
    )


def typ_education(data, sp, theme):
    out = []
    for e in data.get("education", []):
        # period 可缺省：学员常只写「2027 届」，不缺年份就不该渲染一个有日期的行。
        period = (e.get("period") or "").strip()
        if period:
            row = (
                f'#grid(columns: (1fr, auto),\n'
                f'  [#text(size: 10.5pt, weight: "bold")[{esc(e["school"])}]'
                f'#h(0.7em)#text(size: 10pt)[{esc(e["major"])}]],\n'
                f'  [#text(size: 9pt, fill: rgb("#{theme["muted"]}"))[{esc(period)}]]\n'
                f')\n'
            )
        else:
            row = (
                f'#text(size: 10.5pt, weight: "bold")[{esc(e["school"])}]'
                f'#h(0.7em)#text(size: 10pt)[{esc(e["major"])}]\n'
            )
        out.append(
            f'#v(0.1em)\n{row}'
            f'{bullets(e.get("highlights"), sp["bul_gap"], theme["accent"])}'
        )
    return "\n".join(out)


def typ_skills(data, sp, theme):
    out = []
    for s in data.get("skills", []):
        # 分类名 10pt 加粗、内容 9.5pt：技能行大多接近满宽，行内关键词加粗会加宽
        # 字面把行挤折；降 0.5pt 腾出约 5% 宽度，才能既点出重点又不折行（R19）。
        out.append(
            f'#v({sp["skill_gap"]})\n'
            '#grid(columns: (5.6em, 1fr), column-gutter: 0.4em, align: (left + top, left),\n'
            f'  [#text(size: 10pt, weight: "bold", fill: rgb("#{theme["accent"]}"))'
            f'[{esc(s["label"])}]],\n'
            f'  [#text(size: 9.5pt)[{rich(s["details"])}]]\n)'
        )
    return "\n".join(out)


def typ_items(items, sp, theme, labels=None):
    """条目块：项目名 + 技术栈 + 简介 + 亮点。

    三层标签是简历可读性的关键（示例实证 5/5）：HR 扫简历时先找「技术栈」看关键词
    匹配，再找「亮点」看做过什么。缺了标签，整块会退化成一段连续文字。
    标签可用内容源里的 labels: {tech_stack, desc, highlights} 覆盖（写英文简历时用）。
    """
    lb = {"tech_stack": "技术栈", "desc": "项目简介", "highlights": "技术亮点"}
    lb.update(labels or {})
    out = []
    accent = theme["accent"]
    muted = theme["muted"]
    ink = theme["ink"]
    bul_gap = sp["bul_gap"]
    for i, p in enumerate(items or []):
        gap = "0.1em" if i == 0 else "0.7em"
        period = (p.get("period") or "").strip()
        right = (f'[#text(size: 9pt, fill: rgb("#{muted}"))[{esc(period)}]]'
                 if period else "[]")
        out.append(
            f'#v({gap})\n'
            f'#grid(columns: (1fr, auto), align: (left + bottom, right + bottom),\n'
            f'  [#text(size: 11pt, fill: rgb("#{accent}"))[▍]#h(0.25em)'
            f'#text(size: 10.5pt, weight: "bold")[{esc(p["name"])}]'
            f'   #h(0.55em)#text(size: 9pt, fill: rgb("#{muted}"))'
            f'[{esc(p.get("tag", ""))}]],\n'
            f'  {right}\n'
            f')\n'
            f'#v(0.2em)\n'
            f'#text(size: 9pt, weight: "bold", fill: rgb("#{muted}"))'
            f'[{esc(lb["tech_stack"])}]'
            f'#text(size: 9pt, fill: rgb("#{muted}"))'
            f'[　{esc(p.get("tech", ""))}]\n'
            f'#v(0.3em)\n'
            f'#text(size: 10pt, weight: "bold", fill: rgb("#{ink}"))[{esc(lb["desc"])}]'
            f'#text(size: 10pt)[　{rich(p.get("desc", ""))}]\n'
            f'#v(0.42em)\n'
            f'#text(size: 10pt, weight: "bold", fill: rgb("#{ink}"))'
            f'[{esc(lb["highlights"])}]\n'
            f'{bullets(p.get("bullets"), bul_gap, accent)}'
        )
    return "\n".join(out)


def build_typst(data, base, root, font, theme, sp, order) -> str:
    photo = data.get("photo")
    photo_path = base / photo if photo else None
    has_photo = bool(photo_path and photo_path.exists())
    if has_photo and root:
        photo_ref = "/" + photo_path.resolve().relative_to(Path(root).resolve()).as_posix()
    else:
        photo_ref = photo_path.as_posix() if has_photo else ""

    head_left = f"""
#text(size: 22pt, weight: "bold", tracking: 0.06em, fill: rgb("#{theme['ink']}"))[{esc(data['name'])}]
#v(0.38em)
#text(size: 11pt, fill: rgb("#{theme['muted']}"))[求职意向：]"""
    head_left += (f'#text(size: 11pt, weight: "bold", fill: rgb("#{theme["ink"]}"))'
                  f'[{esc(data["intent"])}]\n')
    head_left += (f'#v(0.22em)\n'
                  f'#text(size: 10.5pt, weight: "bold", fill: rgb("#{theme["ink"]}"))'
                  f'[{esc(data["availability"])}]\n'
                  f'#v(0.24em)\n'
                  f'#text(size: 9pt, fill: rgb("#{theme["muted"]}"))'
                  f'[{"　·　".join(esc(c) for c in data["contacts"])}]\n')

    if has_photo:
        head = f"""#grid(columns: (1fr, auto), column-gutter: 1.1cm, align: (left + top, right + top),[
{head_left}],[
  #box(width: 2.1cm, height: 2.94cm, clip: true, radius: 2pt, stroke: 0.5pt + rgb("#{theme['rule']}"))[
    #image("{photo_ref}", width: 2.1cm, height: 2.94cm, fit: "cover")
  ]
])"""
    else:
        head = f"#grid(columns: (1fr,),[\n{head_left}\n])"

    out = [
        f'#set document(title: "{esc(data["name"])}-简历")',
        '#set page(paper: "a4", margin: (top: 1.2cm, bottom: 1.2cm, x: 1.8cm))',
        f'#set text(font: "{font}", size: 10pt, fill: rgb("#{theme["ink"]}"),'
        ' lang: "zh", region: "cn")',
        f"#set par(leading: {sp['leading']}, justify: false, spacing: 0.5em)",
        head,
        f'#v(0.6em)\n#line(length: 100%, stroke: 1.4pt + rgb("#{theme["accent"]}"))',
    ]
    if data.get("summary"):
        out.append(section("个人优势", f'#text(size: 10pt)[{rich(data["summary"])}]',
                           sp["sec_gap"], theme))

    labels = data.get("labels")
    bodies = {
        "education": typ_education(data, sp, theme),
        "skills": typ_skills(data, sp, theme),
        "projects": typ_items(data.get("projects"), sp, theme, labels),
        "internship": typ_items(data.get("internship"), sp, theme, labels),
    }
    for key in order:
        if bodies.get(key):
            out.append(section(SECTION_TITLES[key], bodies[key], sp["sec_gap"], theme))
    return "\n".join(out)


# ------------------------------------------------------------------ DOCX

def _font(run, size, font, bold=False, color=None):
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run._element.rPr.rFonts.set(qn("w:eastAsia"), font)
    if color:
        run.font.color.rgb = RGBColor.from_string(color)


def _rich(doc, text, font, size=10, color=None, after=1.5, indent=0.0, first=0.0):
    par = doc.add_paragraph()
    par.paragraph_format.space_before = Pt(0)
    par.paragraph_format.space_after = Pt(after)
    if indent:
        par.paragraph_format.left_indent = Cm(indent)
    if first:
        par.paragraph_format.first_line_indent = Cm(first)
    for i, seg in enumerate(str(text).split("**")):
        if seg:
            _font(par.add_run(seg), size, font, bold=(i % 2 == 1), color=color)
    return par


def _section(doc, title, font, theme):
    par = doc.add_paragraph()
    par.paragraph_format.space_before = Pt(10)
    par.paragraph_format.space_after = Pt(4)
    _font(par.add_run(title), 11, font, True, color=theme["accent"])
    p = par._p.get_or_add_pPr()
    border = p.makeelement(qn("w:pBdr"), {})
    border.append(p.makeelement(qn("w:bottom"), {
        qn("w:val"): "single", qn("w:sz"): "6", qn("w:space"): "3",
        qn("w:color"): theme["rule"]}))
    p.append(border)


def _docx_items(doc, items, font, theme, labels=None):
    lb = {"tech_stack": "技术栈", "desc": "项目简介", "highlights": "技术亮点"}
    lb.update(labels or {})
    for item in items or []:
        par = doc.add_paragraph()
        par.paragraph_format.space_before = Pt(7)
        par.paragraph_format.space_after = Pt(0)
        par.paragraph_format.tab_stops.add_tab_stop(Cm(18.0), 2)
        _font(par.add_run(item["name"]), 10.5, font, True)
        _font(par.add_run("　" + item.get("tag", "")), 9, font, color=theme["muted"])
        period = (item.get("period") or "").strip()
        if period:
            _font(par.add_run("\t" + period), 9, font, color=theme["muted"])
        # 与 PDF 同一套三层标签（R19），避免用户在 Word 里改一版就回到无层次的平铺排版
        _rich(doc, f"**{lb['tech_stack']}**　" + item.get("tech", ""),
              font, 9, theme["muted"], after=1)
        _rich(doc, f"**{lb['desc']}**　" + item.get("desc", ""), font, 10, after=2)
        _rich(doc, f"**{lb['highlights']}**", font, 10, after=0.5)
        for b in item.get("bullets", []):
            _rich(doc, "• " + b, font, 10, indent=0.45, first=-0.45, after=1.6)


def build_docx(data, base, out_path, font, theme, order):
    doc = Document()
    for sec in doc.sections:
        sec.top_margin = Cm(1.2)
        sec.bottom_margin = Cm(1.2)
        sec.left_margin = Cm(1.8)
        sec.right_margin = Cm(1.8)
    st = doc.styles["Normal"]
    st.font.name = font
    st.font.size = Pt(10)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), font)

    photo = base / data["photo"] if data.get("photo") else None
    has_photo = bool(photo and photo.exists())
    # ATS: avoid tables entirely unless a photo really needs one.
    if has_photo:
        tbl = doc.add_table(rows=1, cols=2)
        tbl.autofit = False
        left, right = tbl.rows[0].cells
        left.width = Cm(13.9)
        right.width = Cm(3.1)
        p = left.paragraphs[0]
        rp = right.paragraphs[0]
        rp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        rp.add_run().add_picture(str(photo), width=Cm(2.1))
    else:
        left = doc
        p = doc.add_paragraph()

    p.paragraph_format.space_after = Pt(2)
    _font(p.add_run(data["name"]), 22, font, True)
    _rich(left, f"求职意向：**{data['intent']}**", font, 10.5, theme["muted"])
    _rich(left, data["availability"], font, 10, theme["ink"])
    _rich(left, "　·　".join(data["contacts"]), font, 9, theme["muted"], after=0)

    par = doc.add_paragraph()
    par.paragraph_format.space_before = Pt(4)
    par.paragraph_format.space_after = Pt(0)
    p = par._p.get_or_add_pPr()
    border = p.makeelement(qn("w:pBdr"), {})
    border.append(p.makeelement(qn("w:bottom"), {
        qn("w:val"): "single", qn("w:sz"): "12", qn("w:space"): "1",
        qn("w:color"): theme["ink"]}))
    p.append(border)

    if data.get("summary"):
        _section(doc, "个人优势", font, theme)
        _rich(doc, data["summary"], font, 10, after=2)

    for key in order:
        if key == "education":
            _section(doc, SECTION_TITLES[key], font, theme)
            for e in data.get("education", []):
                par = doc.add_paragraph()
                par.paragraph_format.space_after = Pt(1)
                par.paragraph_format.tab_stops.add_tab_stop(Cm(18.0), 2)
                _font(par.add_run(e["school"]), 10.5, font, True)
                _font(par.add_run("　" + e["major"]), 10, font)
                _period = (e.get("period") or "").strip()  # period 可缺省
                if _period:
                    _font(par.add_run("\t" + _period), 9, font, color=theme["muted"])
                for h in e.get("highlights", []):
                    _rich(doc, "• " + h, font, 10, indent=0.45, first=-0.45, after=1.2)
        elif key == "skills":
            _section(doc, SECTION_TITLES[key], font, theme)
            for s in data.get("skills", []):
                # 与 PDF 一致：分类名 10pt 加粗、内容 9.5pt 且支持 **加粗** / 换行
                par = doc.add_paragraph()
                par.paragraph_format.space_before = Pt(0)
                par.paragraph_format.space_after = Pt(2)
                _font(par.add_run(s["label"]), 10, font, True, color=theme["accent"])
                _font(par.add_run("　"), 10, font)
                for i, seg in enumerate(str(s["details"]).split("**")):
                    if not seg:
                        continue
                    for j, part in enumerate(seg.split("\n")):
                        if j:
                            par.add_run().add_break()
                        if part:
                            _font(par.add_run(part), 9.5, font, bold=(i % 2 == 1))
        elif key == "projects":
            if data.get("projects"):
                _section(doc, SECTION_TITLES[key], font, theme)
                _docx_items(doc, data["projects"], font, theme, data.get("labels"))
        elif key == "internship":
            if data.get("internship"):
                _section(doc, SECTION_TITLES[key], font, theme)
                _docx_items(doc, data["internship"], font, theme, data.get("labels"))

    doc.save(str(out_path))
    return out_path


def main():
    ap = argparse.ArgumentParser(description="Render a one-page Chinese resume from source.yaml")
    ap.add_argument("source", help="path to source.yaml")
    ap.add_argument("--out", default=None, help="output directory (defaults to source directory)")
    ap.add_argument("--font", default=None, help="override CJK font name")
    args = ap.parse_args()

    yaml_path = Path(args.source)
    out_dir = Path(args.out) if args.out else yaml_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    base = yaml_path.parent

    for field in ("name", "intent", "availability", "contacts"):
        if not data.get(field):
            raise SystemExit("source.yaml 缺少硬性字段 %s（先完成 Phase 0 信息采集）" % field)
    order = order_of(data)
    theme = dict(DEFAULT_THEME)
    theme.update({k: str(v).lstrip("#") for k, v in (data.get("theme") or {}).items()
                  if k in DEFAULT_THEME})
    font = resolve_font((data.get("theme") or {}).get("font"), args.font)
    sp = spacing_of(data)
    stem = stem_of(data)

    anchors = [out_dir.resolve()]
    ph = data.get("photo")
    if ph and (base / ph).exists():
        anchors.append((base / ph).parent.resolve())
    try:
        root = Path(os.path.commonpath([str(a) for a in anchors]))
    except ValueError:
        root = None

    typ_path = out_dir / "resume.typ"
    typ_path.write_text(build_typst(data, base, root, font, theme, sp, order), encoding="utf-8")
    pdf = out_dir / f"{stem}.pdf"
    typst.compile(str(typ_path), output=str(pdf), root=str(root) if root else None)
    print("PDF  %s" % pdf)

    docx = build_docx(data, base, out_dir / f"{stem}.docx", font, theme, order)
    print("DOCX %s" % docx)

    import pymupdf
    with pymupdf.open(str(pdf)) as doc:
        print("页数 %d（应为 1）" % doc.page_count)
        doc[0].get_pixmap(dpi=150).save(str(out_dir / "preview.png"))

    shutil.copyfile(str(yaml_path), str(out_dir / "source.yaml"))
    print("字体 %s ｜ 板块顺序 %s ｜ stem %s" % (font, " → ".join(order), stem))


if __name__ == "__main__":
    main()
