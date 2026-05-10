#!/usr/bin/env python3
"""Build HTML + PDF for each chapter under 'AI mindset explore/'.

Source markdown lives in 'AI mindset explore/markdown/'.
HTML output goes to 'AI mindset explore/' (interactive, mermaid via CDN).
PDF output goes to 'AI mindset explore/pdf/' (offline-friendly, no JS).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import markdown

# Monkey-patch fontTools to tolerate Unicode range bit > 122 that some
# system CJK fonts declare. Otherwise weasyprint's subsetter crashes.
from fontTools.ttLib.tables import O_S_2f_2 as _os2

_orig_set_unicode_ranges = _os2.table_O_S_2f_2.setUnicodeRanges

def _safe_set_unicode_ranges(self, bits):
    return _orig_set_unicode_ranges(self, [b for b in bits if 0 <= b <= 122])

_os2.table_O_S_2f_2.setUnicodeRanges = _safe_set_unicode_ranges

from weasyprint import HTML  # noqa: E402

ROOT = Path("/home/user/invest/AI mindset explore")
MD_DIR = ROOT / "markdown"
PDF_DIR = ROOT / "pdf"

CHAPTERS = [
    ("总览", "README · 顶层整合", "README.md", "README.html", "README.pdf"),
    ("01", "技术演进与本质", "01-tech-evolution-essence.md",
     "01-tech-evolution-essence.html", "01-tech-evolution-essence.pdf"),
    ("02", "操控术分层演进", "02-control-stack-evolution.md",
     "02-control-stack-evolution.html", "02-control-stack-evolution.pdf"),
    ("03", "工程实践与架构", "03-engineering-patterns.md",
     "03-engineering-patterns.html", "03-engineering-patterns.pdf"),
    ("04", "行业替代地图", "04-industry-displacement.md",
     "04-industry-displacement.html", "04-industry-displacement.pdf"),
    ("05", "投资与商业模式", "05-investment-business-models.md",
     "05-investment-business-models.html", "05-investment-business-models.pdf"),
    ("06", "个人工作流与认知重塑", "06-personal-workflow.md",
     "06-personal-workflow.html", "06-personal-workflow.pdf"),
    ("07", "基础设施 算力 地缘", "07-infra-compute-geopolitics.md",
     "07-infra-compute-geopolitics.html", "07-infra-compute-geopolitics.pdf"),
    ("08", "安全 对齐 伦理", "08-safety-alignment-ethics.md",
     "08-safety-alignment-ethics.html", "08-safety-alignment-ethics.pdf"),
    ("09", "认知科学与智能本质", "09-cognitive-science-intelligence.md",
     "09-cognitive-science-intelligence.html", "09-cognitive-science-intelligence.pdf"),
    ("10", "前瞻与争议", "10-forecasts-controversies.md",
     "10-forecasts-controversies.html", "10-forecasts-controversies.pdf"),
]

# ============================================================
# CSS for browser HTML
# ============================================================

CSS_BROWSER = r"""
* { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg: #fbf9f4;
  --bg-card: #ffffff;
  --text: #2a2a2a;
  --text-soft: #555;
  --text-faded: #8a8580;
  --heading: #1a1a1a;
  --accent: #b85042;
  --accent-soft: #e7b8a0;
  --border: #e5dfd2;
  --border-soft: #efeae0;
  --code-bg: #f3eee2;
  --code-border: #e0d9c8;
  --table-stripe: #f7f3eb;
  --link: #8a3a2e;
  --link-hover: #b85042;
  --serif: 'Noto Serif SC', 'Source Han Serif SC', 'Songti SC', 'STSong', Georgia, 'Times New Roman', serif;
  --sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Noto Sans SC', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  --mono: 'JetBrains Mono', 'SF Mono', Menlo, Consolas, monospace;
}

html { scroll-behavior: smooth; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--sans);
  font-size: 17px;
  line-height: 1.85;
  font-weight: 400;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

.chapter-nav {
  position: sticky; top: 0; z-index: 50;
  background: rgba(251, 249, 244, 0.94);
  backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border);
  padding: 10px 24px;
  display: flex; flex-wrap: wrap; gap: 4px;
  font-size: 13px;
}
.nav-brand {
  font-family: var(--serif); font-weight: 700; font-size: 14px;
  color: var(--accent); margin-right: 16px; padding: 6px 4px;
  letter-spacing: 0.02em;
}
.nav-item {
  display: inline-flex; align-items: baseline; gap: 6px;
  padding: 6px 10px; border-radius: 6px; text-decoration: none;
  color: var(--text-soft); border: none;
  transition: background 0.15s ease, color 0.15s ease;
  white-space: nowrap;
}
.nav-item:hover { background: var(--code-bg); color: var(--text); border-bottom: none; }
.nav-item.current { background: var(--accent); color: #fff; }
.nav-item.current .nav-num { color: rgba(255,255,255,0.85); }
.nav-num { font-family: var(--mono); font-weight: 500; font-size: 11.5px; color: var(--text-faded); letter-spacing: 0.04em; }
.nav-title { font-weight: 500; }

.content { max-width: 760px; margin: 64px auto 60px; padding: 0 32px; }

.content > h1:first-child {
  font-family: var(--serif); font-size: 40px; line-height: 1.25; font-weight: 700;
  color: var(--heading); margin: 0 0 12px 0; padding: 0; border: none;
  letter-spacing: -0.015em;
}
.content > h1:first-child + blockquote {
  margin-top: 16px; border-left-width: 3px; background: transparent;
  font-style: normal; color: var(--text-soft); padding: 6px 18px;
}

h1, h2, h3, h4 { font-family: var(--serif); font-weight: 700; color: var(--heading); letter-spacing: -0.005em; }
h1 { font-size: 30px; margin: 72px 0 22px; padding-top: 16px; border-top: 2px solid var(--border); }
h2 { font-size: 25px; margin: 56px 0 18px; padding-bottom: 8px; border-bottom: 1px solid var(--border); }
h3 { font-size: 20px; margin: 38px 0 12px; }
h4 { font-size: 17px; margin: 26px 0 10px; font-family: var(--sans); font-weight: 600; color: var(--text); }
p { margin: 16px 0; word-break: break-word; overflow-wrap: anywhere; }

a { color: var(--link); text-decoration: none; border-bottom: 1px dashed var(--accent-soft); transition: color 0.15s ease, border-bottom-style 0.15s ease; }
a:hover { color: var(--link-hover); border-bottom-style: solid; }
strong { font-weight: 600; color: var(--heading); }
em { font-style: italic; color: var(--text-soft); }

ul, ol { margin: 16px 0 16px 26px; padding: 0; }
li { margin: 8px 0; line-height: 1.85; }
li > ul, li > ol { margin: 6px 0 6px 20px; }
li::marker { color: var(--accent); }

blockquote {
  margin: 24px 0; padding: 14px 22px; background: var(--bg-card);
  border-left: 4px solid var(--accent); border-radius: 0 4px 4px 0;
  color: var(--text-soft); font-family: var(--serif); font-size: 16px; font-style: italic;
}
blockquote p { margin: 8px 0; }
blockquote p:first-child { margin-top: 0; }
blockquote p:last-child { margin-bottom: 0; }

code {
  font-family: var(--mono); font-size: 0.88em;
  background: var(--code-bg); padding: 2px 6px; border-radius: 3px;
  border: 1px solid var(--code-border); color: #6b3a2e;
}
pre {
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 6px;
  padding: 16px 20px; margin: 22px 0; overflow-x: auto;
  font-family: var(--mono); font-size: 13.5px; line-height: 1.65; color: var(--text);
}
pre code { background: transparent; padding: 0; border: none; font-size: inherit; color: inherit; }
.codehilite { background: var(--bg-card); border: 1px solid var(--border); border-radius: 6px; margin: 22px 0; overflow-x: auto; }
.codehilite pre { margin: 0; border: none; }

table {
  width: 100%; margin: 26px 0; border-collapse: collapse; font-size: 14.5px;
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 6px;
  overflow: hidden; display: table;
}
thead { background: var(--code-bg); }
th, td { padding: 10px 14px; text-align: left; border-bottom: 1px solid var(--border-soft); vertical-align: top; line-height: 1.6; }
th { font-weight: 600; color: var(--heading); font-family: var(--serif); font-size: 14px; letter-spacing: 0.01em; }
tbody tr:nth-child(even) td { background: var(--table-stripe); }
tbody tr:last-child td { border-bottom: none; }
table a { word-break: keep-all; }
.table-wrap { overflow-x: auto; margin: 26px 0; border-radius: 6px; }
.table-wrap > table { margin: 0; }

.mermaid-wrap {
  margin: 28px 0; padding: 24px 16px; background: var(--bg-card);
  border: 1px solid var(--border); border-radius: 8px;
  text-align: center; overflow-x: auto;
}
.mermaid { font-family: var(--sans); display: inline-block; min-width: 100%; }

hr { border: none; height: 1px; background: linear-gradient(to right, transparent, var(--border), transparent); margin: 48px 0; }

.site-footer {
  text-align: center; padding: 36px 24px 60px; border-top: 1px solid var(--border);
  margin-top: 60px; color: var(--text-faded); font-size: 13px;
  font-family: var(--serif); letter-spacing: 0.02em;
}
.site-footer a { color: var(--text-soft); border-bottom: none; }
.site-footer a:hover { color: var(--accent); }

.format-banner {
  margin: 24px 0 0; padding: 12px 16px;
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 6px;
  font-size: 13px; color: var(--text-soft); display: flex; gap: 16px; flex-wrap: wrap;
  align-items: center;
}
.format-banner .label { font-family: var(--serif); font-weight: 600; color: var(--heading); }
.format-banner a { font-family: var(--mono); font-size: 12px; }

.chapter-bottom-nav {
  display: flex; justify-content: space-between; gap: 16px;
  margin: 56px 0 16px; padding: 24px 0;
  border-top: 1px solid var(--border); border-bottom: 1px solid var(--border);
}
.chapter-bottom-nav a {
  flex: 1; padding: 12px 16px; border-radius: 6px;
  background: var(--bg-card); border: 1px solid var(--border);
  text-decoration: none; color: var(--text); font-size: 14px;
  transition: all 0.15s ease;
}
.chapter-bottom-nav a:hover { border-color: var(--accent); color: var(--accent); border-bottom: 1px solid var(--accent); }
.chapter-bottom-nav .next { text-align: right; }
.chapter-bottom-nav .nav-arrow { color: var(--text-faded); font-size: 12px; display: block; margin-bottom: 2px; font-family: var(--mono); }
.chapter-bottom-nav .nav-label { font-weight: 500; color: var(--heading); font-family: var(--serif); }

@media (max-width: 720px) {
  body { font-size: 16px; line-height: 1.8; }
  .content { padding: 0 20px; margin: 36px auto 40px; }
  .content > h1:first-child { font-size: 28px; }
  h1 { font-size: 22px; margin: 48px 0 16px; }
  h2 { font-size: 19px; margin: 40px 0 14px; }
  h3 { font-size: 17px; }
  .chapter-nav { padding: 8px 14px; gap: 2px; }
  .nav-brand { display: none; }
  .nav-item { padding: 5px 8px; font-size: 12px; }
  .nav-title { display: none; }
  .nav-item.current .nav-title { display: inline; }
  table { font-size: 13.5px; }
  th, td { padding: 8px 10px; }
  .chapter-bottom-nav { flex-direction: column; }
}

@media print {
  .chapter-nav, .site-footer, .chapter-bottom-nav, .format-banner { display: none; }
  body { background: #fff; font-size: 11pt; }
  .content { max-width: none; padding: 0; margin: 0; }
  a { color: var(--text); border-bottom: none; }
  pre, blockquote, table, .mermaid-wrap { page-break-inside: avoid; }
}
"""

# ============================================================
# CSS for PDF (weasyprint)
# ============================================================

CSS_PDF = r"""
@page {
  size: A4;
  margin: 22mm 18mm 22mm 18mm;
  @top-right {
    content: string(chapter-title);
    font-family: 'Songti SC', 'STSong', 'Source Han Serif SC', serif;
    font-size: 9pt;
    color: #888;
  }
  @bottom-center {
    content: counter(page) " / " counter(pages);
    font-family: 'PingFang SC', 'Hiragino Sans GB', sans-serif;
    font-size: 9pt;
    color: #aaa;
  }
}
@page :first {
  @top-right { content: ""; }
}

* { box-sizing: border-box; margin: 0; padding: 0; }

html { font-size: 11pt; }
body {
  font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Source Han Sans SC', 'Noto Sans SC', sans-serif;
  color: #2a2a2a;
  line-height: 1.75;
  font-weight: 400;
}

h1, h2, h3, h4 {
  font-family: 'Songti SC', 'STSong', 'Source Han Serif SC', 'Noto Serif SC', serif;
  color: #1a1a1a;
  font-weight: 700;
  page-break-after: avoid;
}

h1 {
  font-size: 22pt;
  margin: 0 0 8pt 0;
  string-set: chapter-title content();
}
.content > h1:first-child {
  font-size: 26pt;
  margin: 0 0 12pt 0;
  padding-bottom: 8pt;
  border-bottom: 2pt solid #b85042;
}
.content > h1 {
  font-size: 18pt;
  margin: 24pt 0 10pt 0;
  padding-top: 12pt;
  border-top: 1pt solid #ddd;
  page-break-before: auto;
}

h2 {
  font-size: 15pt;
  margin: 18pt 0 8pt 0;
  padding-bottom: 4pt;
  border-bottom: 0.5pt solid #ddd;
}
h3 { font-size: 12.5pt; margin: 14pt 0 6pt 0; }
h4 {
  font-size: 11.5pt; margin: 10pt 0 4pt 0;
  font-family: 'PingFang SC', sans-serif; font-weight: 600;
}

p { margin: 6pt 0; orphans: 3; widows: 3; }

a { color: #8a3a2e; text-decoration: none; }
a::after {
  content: " [" attr(href) "]";
  font-size: 8pt; color: #888; word-break: break-all;
}
a[href^="#"]::after, a[href^="./"]::after, a[href$=".html"]::after { content: ""; }

strong { font-weight: 600; color: #1a1a1a; }
em { font-style: italic; color: #555; }

ul, ol { margin: 6pt 0 6pt 18pt; }
li { margin: 3pt 0; line-height: 1.7; }
li > ul, li > ol { margin: 3pt 0 3pt 14pt; }

blockquote {
  margin: 10pt 0;
  padding: 6pt 12pt;
  border-left: 3pt solid #b85042;
  background: #faf7f0;
  color: #555;
  font-family: 'Songti SC', serif;
  font-size: 10.5pt;
  page-break-inside: avoid;
}
blockquote p { margin: 4pt 0; }

code {
  font-family: 'SF Mono', Menlo, Consolas, monospace;
  font-size: 9.5pt;
  background: #f3eee2;
  padding: 1pt 4pt;
  border-radius: 2pt;
  color: #6b3a2e;
}

pre {
  background: #faf7f0;
  border: 0.5pt solid #ddd;
  border-radius: 3pt;
  padding: 8pt 10pt;
  margin: 8pt 0;
  font-family: 'SF Mono', Menlo, Consolas, monospace;
  font-size: 9pt;
  line-height: 1.5;
  color: #333;
  page-break-inside: avoid;
  white-space: pre-wrap;
  word-wrap: break-word;
}
pre code { background: transparent; padding: 0; color: inherit; font-size: inherit; }

table {
  width: 100%;
  margin: 10pt 0;
  border-collapse: collapse;
  font-size: 9.5pt;
  page-break-inside: avoid;
}
thead { background: #f3eee2; }
th, td {
  padding: 5pt 7pt;
  text-align: left;
  border: 0.5pt solid #ccc;
  vertical-align: top;
  line-height: 1.55;
}
th {
  font-weight: 600;
  color: #1a1a1a;
  font-family: 'Songti SC', serif;
  font-size: 9.5pt;
}
tbody tr:nth-child(even) td { background: #faf7f0; }

.mermaid-pdf-box {
  margin: 12pt 0;
  padding: 10pt 12pt;
  background: #faf7f0;
  border: 0.5pt solid #b85042;
  border-radius: 4pt;
  page-break-inside: avoid;
}
.mermaid-pdf-label {
  font-family: 'Songti SC', serif;
  font-weight: 700;
  font-size: 10pt;
  color: #b85042;
  margin-bottom: 6pt;
  letter-spacing: 0.02em;
}
.mermaid-pdf-box pre {
  background: transparent;
  border: none;
  padding: 0;
  margin: 0;
  font-size: 8.5pt;
  color: #444;
  line-height: 1.5;
}
.mermaid-pdf-note {
  margin-top: 6pt;
  font-size: 8pt;
  color: #999;
  font-style: italic;
  font-family: 'PingFang SC', sans-serif;
}

hr {
  border: none;
  height: 0.5pt;
  background: #ddd;
  margin: 18pt 0;
}

.cover-meta {
  font-family: 'Songti SC', serif;
  font-size: 10pt;
  color: #888;
  margin-bottom: 24pt;
  letter-spacing: 0.05em;
}

/* Hide elements not needed in PDF */
.chapter-nav, .chapter-bottom-nav, .site-footer, .format-banner { display: none; }

/* Avoid awkward breaks */
h1, h2, h3, h4 { page-break-after: avoid; }
table, blockquote, pre, .mermaid-pdf-box { page-break-inside: avoid; }
"""

# ============================================================
# Markdown processing
# ============================================================

def preprocess_mermaid(md_text: str):
    blocks = []
    pattern = re.compile(r"```mermaid\n(.*?)\n```", re.DOTALL)

    def replace(m):
        idx = len(blocks)
        blocks.append(m.group(1))
        return f"\n\nMERMAIDPLACEHOLDER{idx}MERMAIDPLACEHOLDER\n\n"

    return pattern.sub(replace, md_text), blocks


def restore_mermaid_browser(html: str, blocks):
    for i, code in enumerate(blocks):
        marker = f"MERMAIDPLACEHOLDER{i}MERMAIDPLACEHOLDER"
        repl = f'<div class="mermaid-wrap"><pre class="mermaid">{code}</pre></div>'
        html = html.replace(f"<p>{marker}</p>", repl).replace(marker, repl)
    return html


def restore_mermaid_pdf(html: str, blocks):
    for i, code in enumerate(blocks):
        marker = f"MERMAIDPLACEHOLDER{i}MERMAIDPLACEHOLDER"
        # Escape HTML special chars in source code
        safe = (code.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;"))
        repl = (
            '<div class="mermaid-pdf-box">'
            '<div class="mermaid-pdf-label">思维导图（Mermaid 源）</div>'
            f'<pre>{safe}</pre>'
            '<div class="mermaid-pdf-note">完整图形渲染请查看 HTML 版本。</div>'
            '</div>'
        )
        html = html.replace(f"<p>{marker}</p>", repl).replace(marker, repl)
    return html


def wrap_tables(html: str) -> str:
    return re.sub(r"(<table[\s\S]*?</table>)", r'<div class="table-wrap">\1</div>', html)


def fix_links_for_html(html: str) -> str:
    """Inside HTML output, .md links become .html (peer files)."""
    return re.sub(r'href="([^"]+)\.md"', r'href="\1.html"', html)


def convert_md(md_text: str, mode: str):
    """mode: 'browser' or 'pdf'"""
    md_text, mermaid_blocks = preprocess_mermaid(md_text)
    md = markdown.Markdown(
        extensions=["extra", "tables", "fenced_code", "codehilite", "attr_list",
                    "toc", "sane_lists", "nl2br"],
        extension_configs={
            "codehilite": {"guess_lang": False, "css_class": "codehilite"},
            "toc": {"permalink": False},
        },
    )
    body = md.convert(md_text)
    if mode == "browser":
        body = restore_mermaid_browser(body, mermaid_blocks)
    else:
        body = restore_mermaid_pdf(body, mermaid_blocks)
    body = wrap_tables(body)
    body = fix_links_for_html(body)
    return body


def extract_title(body: str, fallback: str) -> str:
    m = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.DOTALL)
    if not m:
        return fallback
    return re.sub(r"<[^>]+>", "", m.group(1)).strip() or fallback


# ============================================================
# Browser HTML build
# ============================================================

def build_top_nav(current_html: str) -> str:
    items = ['<span class="nav-brand">AI mindset</span>']
    for num, title, _md, html_name, _pdf in CHAPTERS:
        cls = "nav-item current" if html_name == current_html else "nav-item"
        items.append(
            f'<a href="{html_name}" class="{cls}">'
            f'<span class="nav-num">{num}</span>'
            f'<span class="nav-title">{title}</span></a>'
        )
    return '<nav class="chapter-nav">' + "".join(items) + "</nav>"


def build_bottom_nav(idx: int) -> str:
    parts = ['<nav class="chapter-bottom-nav">']
    if idx > 0:
        n, t, _, hn, _ = CHAPTERS[idx - 1]
        parts.append(
            f'<a href="{hn}" class="prev">'
            f'<span class="nav-arrow">← 上一章 / {n}</span>'
            f'<span class="nav-label">{t}</span></a>'
        )
    else:
        parts.append('<span class="prev"></span>')
    if idx < len(CHAPTERS) - 1:
        n, t, _, hn, _ = CHAPTERS[idx + 1]
        parts.append(
            f'<a href="{hn}" class="next">'
            f'<span class="nav-arrow">下一章 / {n} →</span>'
            f'<span class="nav-label">{t}</span></a>'
        )
    else:
        parts.append('<span class="next"></span>')
    parts.append("</nav>")
    return "".join(parts)


def build_format_banner(pdf_name: str, md_name: str) -> str:
    return (
        '<div class="format-banner">'
        '<span class="label">本章其他版本</span>'
        f'<a href="pdf/{pdf_name}">PDF（离线打印）</a>'
        f'<a href="markdown/{md_name}">Markdown 源</a>'
        '</div>'
    )


def build_browser_html(md_name: str, html_name: str, pdf_name: str, idx: int) -> str:
    md_text = (MD_DIR / md_name).read_text(encoding="utf-8")
    body = convert_md(md_text, mode="browser")
    title = extract_title(body, html_name)
    top = build_top_nav(html_name)
    bottom = build_bottom_nav(idx)
    banner = build_format_banner(pdf_name, md_name)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} · AI mindset explore</title>
<meta name="description" content="个人 AI 认知框架 · {title}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Noto+Sans+SC:wght@300;400;500;600;700&family=Noto+Serif+SC:wght@400;500;700&display=swap" rel="stylesheet">
<style>{CSS_BROWSER}</style>
</head>
<body>
{top}
<main class="content">
{banner}
{body}
{bottom}
</main>
<footer class="site-footer">
  <p>AI mindset explore · 个人 AI 认知框架 · 持续维护中 · <a href="README.html">回到总览</a></p>
</footer>
<script type="module">
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
mermaid.initialize({{
  startOnLoad: true,
  theme: 'base',
  themeVariables: {{
    primaryColor: '#fbf9f4',
    primaryTextColor: '#1a1a1a',
    primaryBorderColor: '#b85042',
    lineColor: '#8a3a2e',
    secondaryColor: '#f7f3eb',
    tertiaryColor: '#fff',
    fontFamily: 'Noto Sans SC, Inter, sans-serif',
  }},
}});
</script>
</body>
</html>
"""


# ============================================================
# PDF build
# ============================================================

def build_pdf_html(md_name: str) -> str:
    md_text = (MD_DIR / md_name).read_text(encoding="utf-8")
    body = convert_md(md_text, mode="pdf")
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>{CSS_PDF}</style>
</head>
<body>
<div class="content">
<div class="cover-meta">AI mindset explore · 个人 AI 认知框架</div>
{body}
</div>
</body>
</html>
"""


# ============================================================
# Main
# ============================================================

def main():
    PDF_DIR.mkdir(exist_ok=True)
    print("→ Building browser HTML...")
    for idx, (_n, _t, md_name, html_name, pdf_name) in enumerate(CHAPTERS):
        if not (MD_DIR / md_name).exists():
            print(f"  SKIP (missing): {md_name}", file=sys.stderr)
            continue
        html = build_browser_html(md_name, html_name, pdf_name, idx)
        (ROOT / html_name).write_text(html, encoding="utf-8")
        print(f"  ✓ {html_name}")

    print("→ Building PDF...")
    for _n, _t, md_name, _h, pdf_name in CHAPTERS:
        if not (MD_DIR / md_name).exists():
            print(f"  SKIP (missing): {md_name}", file=sys.stderr)
            continue
        html_str = build_pdf_html(md_name)
        HTML(string=html_str).write_pdf(str(PDF_DIR / pdf_name), hinting=True)
        size_kb = (PDF_DIR / pdf_name).stat().st_size // 1024
        print(f"  ✓ pdf/{pdf_name}  ({size_kb} KB)")


if __name__ == "__main__":
    main()
