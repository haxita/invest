#!/usr/bin/env python3
"""Convert each .md in 'AI mindset explore/' to a styled, navigable .html."""
import re
import sys
from pathlib import Path

import markdown

DIR = Path("/home/user/invest/AI mindset explore")

CHAPTERS = [
    ("总览", "README · 顶层整合", "README.md", "README.html"),
    ("01", "技术演进与本质", "01-tech-evolution-essence.md", "01-tech-evolution-essence.html"),
    ("02", "操控术分层演进", "02-control-stack-evolution.md", "02-control-stack-evolution.html"),
    ("03", "工程实践与架构", "03-engineering-patterns.md", "03-engineering-patterns.html"),
    ("04", "行业替代地图", "04-industry-displacement.md", "04-industry-displacement.html"),
    ("05", "投资与商业模式", "05-investment-business-models.md", "05-investment-business-models.html"),
    ("06", "个人工作流与认知重塑", "06-personal-workflow.md", "06-personal-workflow.html"),
    ("07", "基础设施 算力 地缘", "07-infra-compute-geopolitics.md", "07-infra-compute-geopolitics.html"),
    ("08", "安全 对齐 伦理", "08-safety-alignment-ethics.md", "08-safety-alignment-ethics.html"),
    ("09", "认知科学与智能本质", "09-cognitive-science-intelligence.md", "09-cognitive-science-intelligence.html"),
    ("10", "前瞻与争议", "10-forecasts-controversies.md", "10-forecasts-controversies.html"),
]

CSS = r"""
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

/* === Sticky Navigation === */
.chapter-nav {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(251, 249, 244, 0.94);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border);
  padding: 10px 24px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  font-size: 13px;
}

.nav-brand {
  font-family: var(--serif);
  font-weight: 700;
  font-size: 14px;
  color: var(--accent);
  margin-right: 16px;
  padding: 6px 4px;
  letter-spacing: 0.02em;
}

.nav-item {
  display: inline-flex;
  align-items: baseline;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 6px;
  text-decoration: none;
  color: var(--text-soft);
  border: none;
  transition: background 0.15s ease, color 0.15s ease;
  white-space: nowrap;
}
.nav-item:hover {
  background: var(--code-bg);
  color: var(--text);
  border-bottom: none;
}
.nav-item.current {
  background: var(--accent);
  color: #fff;
}
.nav-item.current .nav-num { color: rgba(255,255,255,0.85); }
.nav-num {
  font-family: var(--mono);
  font-weight: 500;
  font-size: 11.5px;
  color: var(--text-faded);
  letter-spacing: 0.04em;
}
.nav-title { font-weight: 500; }

/* === Article === */
.content {
  max-width: 760px;
  margin: 64px auto 60px;
  padding: 0 32px;
}

.content > h1:first-child {
  font-family: var(--serif);
  font-size: 40px;
  line-height: 1.25;
  font-weight: 700;
  color: var(--heading);
  margin: 0 0 12px 0;
  padding: 0;
  border: none;
  letter-spacing: -0.015em;
}

.content > h1:first-child + blockquote {
  margin-top: 16px;
  border-left-width: 3px;
  background: transparent;
  font-style: normal;
  color: var(--text-soft);
  padding: 6px 18px;
}

h1, h2, h3, h4 {
  font-family: var(--serif);
  font-weight: 700;
  color: var(--heading);
  letter-spacing: -0.005em;
}

h1 {
  font-size: 30px;
  margin: 72px 0 22px;
  padding-top: 16px;
  border-top: 2px solid var(--border);
}

h2 {
  font-size: 25px;
  margin: 56px 0 18px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}

h3 {
  font-size: 20px;
  margin: 38px 0 12px;
}

h4 {
  font-size: 17px;
  margin: 26px 0 10px;
  font-family: var(--sans);
  font-weight: 600;
  color: var(--text);
}

p {
  margin: 16px 0;
  word-break: break-word;
  overflow-wrap: anywhere;
}

a {
  color: var(--link);
  text-decoration: none;
  border-bottom: 1px dashed var(--accent-soft);
  transition: color 0.15s ease, border-bottom-style 0.15s ease;
}
a:hover {
  color: var(--link-hover);
  border-bottom-style: solid;
}

strong { font-weight: 600; color: var(--heading); }
em { font-style: italic; color: var(--text-soft); }

ul, ol {
  margin: 16px 0 16px 26px;
  padding: 0;
}
li {
  margin: 8px 0;
  line-height: 1.85;
}
li > ul, li > ol { margin: 6px 0 6px 20px; }
li::marker { color: var(--accent); }

blockquote {
  margin: 24px 0;
  padding: 14px 22px;
  background: var(--bg-card);
  border-left: 4px solid var(--accent);
  border-radius: 0 4px 4px 0;
  color: var(--text-soft);
  font-family: var(--serif);
  font-size: 16px;
  font-style: italic;
}
blockquote p { margin: 8px 0; }
blockquote p:first-child { margin-top: 0; }
blockquote p:last-child { margin-bottom: 0; }

code {
  font-family: var(--mono);
  font-size: 0.88em;
  background: var(--code-bg);
  padding: 2px 6px;
  border-radius: 3px;
  border: 1px solid var(--code-border);
  color: #6b3a2e;
}

pre {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 16px 20px;
  margin: 22px 0;
  overflow-x: auto;
  font-family: var(--mono);
  font-size: 13.5px;
  line-height: 1.65;
  color: var(--text);
}
pre code {
  background: transparent;
  padding: 0;
  border: none;
  font-size: inherit;
  color: inherit;
}

.codehilite {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 6px;
  margin: 22px 0;
  overflow-x: auto;
}
.codehilite pre { margin: 0; border: none; }

table {
  width: 100%;
  margin: 26px 0;
  border-collapse: collapse;
  font-size: 14.5px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
  display: table;
}
thead { background: var(--code-bg); }
th, td {
  padding: 10px 14px;
  text-align: left;
  border-bottom: 1px solid var(--border-soft);
  vertical-align: top;
  line-height: 1.6;
}
th {
  font-weight: 600;
  color: var(--heading);
  font-family: var(--serif);
  font-size: 14px;
  letter-spacing: 0.01em;
}
tbody tr:nth-child(even) td { background: var(--table-stripe); }
tbody tr:last-child td { border-bottom: none; }
table a { word-break: keep-all; }

.table-wrap {
  overflow-x: auto;
  margin: 26px 0;
  border-radius: 6px;
}
.table-wrap > table { margin: 0; }

.mermaid-wrap {
  margin: 28px 0;
  padding: 24px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  text-align: center;
  overflow-x: auto;
}
.mermaid { font-family: var(--sans); display: inline-block; min-width: 100%; }

hr {
  border: none;
  height: 1px;
  background: linear-gradient(to right, transparent, var(--border), transparent);
  margin: 48px 0;
}

.site-footer {
  text-align: center;
  padding: 36px 24px 60px;
  border-top: 1px solid var(--border);
  margin-top: 60px;
  color: var(--text-faded);
  font-size: 13px;
  font-family: var(--serif);
  letter-spacing: 0.02em;
}
.site-footer a {
  color: var(--text-soft);
  border-bottom: none;
}
.site-footer a:hover { color: var(--accent); }

.chapter-bottom-nav {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin: 56px 0 16px;
  padding: 24px 0;
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
}
.chapter-bottom-nav a {
  flex: 1;
  padding: 12px 16px;
  border-radius: 6px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  text-decoration: none;
  color: var(--text);
  font-size: 14px;
  transition: all 0.15s ease;
}
.chapter-bottom-nav a:hover {
  border-color: var(--accent);
  color: var(--accent);
  border-bottom: 1px solid var(--accent);
}
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
  .chapter-nav, .site-footer, .chapter-bottom-nav { display: none; }
  body { background: #fff; font-size: 11pt; }
  .content { max-width: none; padding: 0; margin: 0; }
  a { color: var(--text); border-bottom: none; }
  pre, blockquote, table, .mermaid-wrap { page-break-inside: avoid; }
}
"""


def preprocess_mermaid(md_text: str):
    blocks = []
    pattern = re.compile(r"```mermaid\n(.*?)\n```", re.DOTALL)

    def replace(m):
        idx = len(blocks)
        blocks.append(m.group(1))
        return f"\n\nMERMAIDPLACEHOLDER{idx}MERMAIDPLACEHOLDER\n\n"

    new_md = pattern.sub(replace, md_text)
    return new_md, blocks


def restore_mermaid(html: str, blocks):
    for i, code in enumerate(blocks):
        marker = f"MERMAIDPLACEHOLDER{i}MERMAIDPLACEHOLDER"
        replacement = f'<div class="mermaid-wrap"><pre class="mermaid">{code}</pre></div>'
        html = html.replace(f"<p>{marker}</p>", replacement)
        html = html.replace(marker, replacement)
    return html


def wrap_tables(html: str) -> str:
    """Wrap each top-level <table> in a scrollable container for mobile."""
    return re.sub(
        r"(<table[\s\S]*?</table>)",
        r'<div class="table-wrap">\1</div>',
        html,
    )


def build_top_nav(current_html: str) -> str:
    items = ['<span class="nav-brand">AI mindset</span>']
    for num, title, _md, fname in CHAPTERS:
        cls = "nav-item current" if fname == current_html else "nav-item"
        items.append(
            f'<a href="{fname}" class="{cls}">'
            f'<span class="nav-num">{num}</span>'
            f'<span class="nav-title">{title}</span>'
            f"</a>"
        )
    return '<nav class="chapter-nav">' + "".join(items) + "</nav>"


def build_bottom_nav(current_idx: int) -> str:
    parts = ['<nav class="chapter-bottom-nav">']
    if current_idx > 0:
        prev_num, prev_title, _, prev_fname = CHAPTERS[current_idx - 1]
        parts.append(
            f'<a href="{prev_fname}" class="prev">'
            f'<span class="nav-arrow">← 上一章 / {prev_num}</span>'
            f'<span class="nav-label">{prev_title}</span>'
            f"</a>"
        )
    else:
        parts.append('<span class="prev"></span>')

    if current_idx < len(CHAPTERS) - 1:
        next_num, next_title, _, next_fname = CHAPTERS[current_idx + 1]
        parts.append(
            f'<a href="{next_fname}" class="next">'
            f'<span class="nav-arrow">下一章 / {next_num} →</span>'
            f'<span class="nav-label">{next_title}</span>'
            f"</a>"
        )
    else:
        parts.append('<span class="next"></span>')

    parts.append("</nav>")
    return "".join(parts)


def fix_internal_links(html: str) -> str:
    return re.sub(r'href="([^"]+)\.md"', r'href="\1.html"', html)


def extract_title(body: str, fallback: str) -> str:
    m = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.DOTALL)
    if not m:
        return fallback
    text = re.sub(r"<[^>]+>", "", m.group(1)).strip()
    return text or fallback


def convert_one(md_path: Path, html_path: Path, idx: int) -> None:
    md_text = md_path.read_text(encoding="utf-8")
    md_text, mermaid_blocks = preprocess_mermaid(md_text)

    md = markdown.Markdown(
        extensions=[
            "extra",
            "tables",
            "fenced_code",
            "codehilite",
            "attr_list",
            "toc",
            "sane_lists",
            "nl2br",
        ],
        extension_configs={
            "codehilite": {"guess_lang": False, "css_class": "codehilite"},
            "toc": {"permalink": False},
        },
    )
    body = md.convert(md_text)
    body = restore_mermaid(body, mermaid_blocks)
    body = wrap_tables(body)
    body = fix_internal_links(body)

    title = extract_title(body, html_path.stem)
    top_nav = build_top_nav(html_path.name)
    bottom_nav = build_bottom_nav(idx)

    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} · AI mindset explore</title>
<meta name="description" content="个人 AI 认知框架 · {title}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Noto+Sans+SC:wght@300;400;500;600;700&family=Noto+Serif+SC:wght@400;500;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
{top_nav}
<main class="content">
{body}
{bottom_nav}
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
    html_path.write_text(page, encoding="utf-8")


def main():
    written = []
    for idx, (_num, _title, md_name, html_name) in enumerate(CHAPTERS):
        md_path = DIR / md_name
        html_path = DIR / html_name
        if not md_path.exists():
            print(f"SKIP (missing): {md_path}", file=sys.stderr)
            continue
        convert_one(md_path, html_path, idx)
        written.append(html_path.name)
        print(f"  ✓ {html_path.name}")
    print(f"\nWrote {len(written)} HTML files.")


if __name__ == "__main__":
    main()
