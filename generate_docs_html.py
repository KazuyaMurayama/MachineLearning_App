"""
MDドキュメントをワンクリックで閲覧できるHTMLファイルを生成するスクリプト。

使い方:
    python generate_docs_html.py

生成物:
    docs/index.html — ブラウザで開くだけで全ドキュメントを閲覧可能
"""

import os
import re
import html

DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")

# 表示順序とタイトル
STEPS = [
    ("step1_usecase_catalog.md", "Step 1: ユースケースカタログ", "18業界×140件のユースケース調査"),
    ("step2_monetization_scoring.md", "Step 2: マネタイズ評価", "6軸×30点満点スコアリング"),
    ("step3_prioritization.md", "Step 3: 優先順位付け", "GTM+リスク+ポートフォリオ統合"),
    ("step4_marketing_strategy.md", "Step 4: マーケティング戦略", "STP/4P/ジャーニー/KPI/予算"),
    ("step5_strategy_review.md", "Step 5: 多角的レビュー", "5つの思考パターンで問題特定"),
    ("step6_revised_strategy.md", "Step 6: 修正戦略 v2", "PMF検証+KPI修正+ピボット設計"),
    ("step7_second_review.md", "Step 7: 第2回レビュー", "Step 6検証+最終提言"),
]


def md_to_html(md_text):
    """簡易Markdownパーサー。外部ライブラリ不要。"""
    lines = md_text.split("\n")
    out = []
    in_table = False
    in_code = False
    in_list = False
    table_rows = []

    def flush_table():
        nonlocal table_rows, in_table
        if not table_rows:
            return ""
        result = '<div class="table-wrap"><table>\n'
        for i, row in enumerate(table_rows):
            cells = [c.strip() for c in row.split("|")]
            cells = [c for c in cells if c != ""]
            # 区切り行をスキップ
            if all(re.match(r"^[-:]+$", c) for c in cells):
                continue
            tag = "th" if i == 0 else "td"
            result += "<tr>"
            for cell in cells:
                cell_html = inline_format(html.escape(cell))
                result += f"<{tag}>{cell_html}</{tag}>"
            result += "</tr>\n"
        result += "</table></div>\n"
        table_rows = []
        in_table = False
        return result

    def inline_format(text):
        # Bold
        text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
        # Italic
        text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
        # Strikethrough
        text = re.sub(r"~~(.+?)~~", r"<del>\1</del>", text)
        # Inline code
        text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
        # Links
        text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)
        # Star ratings
        text = text.replace("★", '<span class="star">★</span>')
        return text

    i = 0
    while i < len(lines):
        line = lines[i]

        # コードブロック
        if line.strip().startswith("```"):
            if in_table:
                out.append(flush_table())
            if in_code:
                out.append("</code></pre>\n")
                in_code = False
            else:
                in_code = True
                out.append('<pre><code>')
            i += 1
            continue

        if in_code:
            out.append(html.escape(line) + "\n")
            i += 1
            continue

        stripped = line.strip()

        # 空行
        if not stripped:
            if in_table:
                out.append(flush_table())
            if in_list:
                out.append("</ul>\n")
                in_list = False
            i += 1
            continue

        # テーブル
        if "|" in stripped and stripped.startswith("|"):
            if not in_table:
                if in_list:
                    out.append("</ul>\n")
                    in_list = False
                in_table = True
            table_rows.append(stripped)
            i += 1
            continue
        elif in_table:
            out.append(flush_table())

        # 見出し
        m = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if m:
            if in_list:
                out.append("</ul>\n")
                in_list = False
            level = len(m.group(1))
            text = inline_format(html.escape(m.group(2)))
            anchor = re.sub(r"[^\w\s-]", "", m.group(2).lower()).strip().replace(" ", "-")
            out.append(f'<h{level} id="{anchor}">{text}</h{level}>\n')
            i += 1
            continue

        # 水平線
        if re.match(r"^---+$", stripped):
            out.append("<hr>\n")
            i += 1
            continue

        # blockquote
        if stripped.startswith("> "):
            if in_list:
                out.append("</ul>\n")
                in_list = False
            text = inline_format(html.escape(stripped[2:]))
            out.append(f"<blockquote>{text}</blockquote>\n")
            i += 1
            continue

        # リスト
        m_list = re.match(r"^[-*]\s+(.+)$", stripped) or re.match(r"^\d+\.\s+(.+)$", stripped)
        if m_list:
            if not in_list:
                out.append("<ul>\n")
                in_list = True
            text = inline_format(html.escape(m_list.group(1)))
            out.append(f"<li>{text}</li>\n")
            i += 1
            continue

        # 通常のパラグラフ
        if in_list:
            out.append("</ul>\n")
            in_list = False
        text = inline_format(html.escape(stripped))
        out.append(f"<p>{text}</p>\n")
        i += 1

    if in_table:
        out.append(flush_table())
    if in_code:
        out.append("</code></pre>\n")
    if in_list:
        out.append("</ul>\n")

    return "".join(out)


def generate_html():
    """全MDドキュメントを統合した単一HTMLを生成"""

    # 各ドキュメントの内容を読み込み・変換
    sections = []
    for filename, title, subtitle in STEPS:
        filepath = os.path.join(DOCS_DIR, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                md_content = f.read()
            html_content = md_to_html(md_content)
        else:
            html_content = f"<p>ファイルが見つかりません: {filename}</p>"
        sections.append((filename, title, subtitle, html_content))

    # サイドバーナビゲーション生成
    nav_items = []
    for filename, title, subtitle in STEPS:
        step_id = filename.replace(".md", "")
        short_title = title.split(": ", 1)[-1] if ": " in title else title
        step_num = title.split(":")[0]
        nav_items.append(
            f'<a href="#{step_id}" class="nav-item" onclick="showSection(\'{step_id}\')">'
            f'<span class="nav-step">{step_num}</span>'
            f'<span class="nav-title">{short_title}</span>'
            f'<span class="nav-sub">{subtitle}</span>'
            f'</a>'
        )
    nav_html = "\n".join(nav_items)

    # セクション生成
    section_blocks = []
    for i, (filename, title, subtitle, content) in enumerate(sections):
        step_id = filename.replace(".md", "")
        display = "block" if i == 0 else "none"
        section_blocks.append(
            f'<section id="{step_id}" class="doc-section" style="display:{display}">'
            f'{content}'
            f'</section>'
        )
    sections_html = "\n".join(section_blocks)

    page_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ML予測アプリ — マネタイズ戦略ドキュメント</title>
<style>
:root {{
  --bg: #0f172a;
  --surface: #1e293b;
  --surface2: #334155;
  --border: #475569;
  --text: #e2e8f0;
  --text-muted: #94a3b8;
  --accent: #38bdf8;
  --accent2: #818cf8;
  --green: #4ade80;
  --orange: #fb923c;
  --red: #f87171;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Hiragino Sans', 'Noto Sans JP', sans-serif;
  background: var(--bg);
  color: var(--text);
  display: flex;
  height: 100vh;
  overflow: hidden;
}}

/* サイドバー */
.sidebar {{
  width: 280px;
  min-width: 280px;
  background: var(--surface);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}}
.sidebar-header {{
  padding: 20px;
  border-bottom: 1px solid var(--border);
}}
.sidebar-header h1 {{
  font-size: 16px;
  color: var(--accent);
  margin-bottom: 4px;
}}
.sidebar-header p {{
  font-size: 11px;
  color: var(--text-muted);
}}
.nav-item {{
  display: block;
  padding: 12px 20px;
  text-decoration: none;
  color: var(--text);
  border-bottom: 1px solid rgba(71,85,105,0.3);
  transition: background 0.15s;
  cursor: pointer;
}}
.nav-item:hover {{ background: var(--surface2); }}
.nav-item.active {{
  background: var(--surface2);
  border-left: 3px solid var(--accent);
}}
.nav-step {{
  display: block;
  font-size: 10px;
  color: var(--accent);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 2px;
}}
.nav-title {{
  display: block;
  font-size: 14px;
  font-weight: 600;
}}
.nav-sub {{
  display: block;
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}}

/* メインコンテンツ */
.main {{
  flex: 1;
  overflow-y: auto;
  padding: 40px 60px;
  max-width: 900px;
}}
.main h1 {{
  font-size: 28px;
  color: var(--accent);
  margin-bottom: 8px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--border);
}}
.main h2 {{
  font-size: 22px;
  color: var(--accent2);
  margin-top: 36px;
  margin-bottom: 12px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border);
}}
.main h3 {{
  font-size: 17px;
  color: var(--green);
  margin-top: 24px;
  margin-bottom: 8px;
}}
.main h4 {{
  font-size: 15px;
  color: var(--orange);
  margin-top: 18px;
  margin-bottom: 6px;
}}
.main p {{
  margin-bottom: 10px;
  line-height: 1.7;
  color: var(--text);
}}
.main ul, .main ol {{
  margin-bottom: 12px;
  padding-left: 24px;
}}
.main li {{
  margin-bottom: 4px;
  line-height: 1.6;
}}
.main blockquote {{
  border-left: 3px solid var(--accent);
  padding: 10px 16px;
  margin: 12px 0;
  background: rgba(56,189,248,0.08);
  border-radius: 0 6px 6px 0;
  color: var(--text-muted);
  font-style: italic;
}}
.main hr {{
  border: none;
  border-top: 1px solid var(--border);
  margin: 24px 0;
}}
.main pre {{
  background: #0c1222;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px;
  overflow-x: auto;
  margin: 12px 0;
}}
.main pre code {{
  font-family: 'JetBrains Mono', 'Fira Code', 'Source Code Pro', monospace;
  font-size: 13px;
  color: var(--green);
  background: none;
  padding: 0;
}}
.main code {{
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 13px;
  background: var(--surface2);
  padding: 2px 6px;
  border-radius: 4px;
  color: var(--orange);
}}
.main strong {{ color: #f1f5f9; }}
.main del {{ color: var(--red); text-decoration: line-through; }}
.star {{ color: #facc15; }}

/* テーブル */
.table-wrap {{
  overflow-x: auto;
  margin: 12px 0;
}}
.main table {{
  border-collapse: collapse;
  width: 100%;
  font-size: 13px;
}}
.main th {{
  background: var(--surface2);
  color: var(--accent);
  font-weight: 600;
  text-align: left;
  padding: 8px 12px;
  border: 1px solid var(--border);
  white-space: nowrap;
}}
.main td {{
  padding: 8px 12px;
  border: 1px solid var(--border);
  vertical-align: top;
}}
.main tr:nth-child(even) td {{
  background: rgba(30,41,59,0.5);
}}
.main tr:hover td {{
  background: rgba(56,189,248,0.06);
}}

/* スクロールバー */
::-webkit-scrollbar {{ width: 8px; height: 8px; }}
::-webkit-scrollbar-track {{ background: var(--bg); }}
::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 4px; }}
::-webkit-scrollbar-thumb:hover {{ background: var(--text-muted); }}

/* レスポンシブ */
@media (max-width: 768px) {{
  body {{ flex-direction: column; }}
  .sidebar {{ width: 100%; min-width: 100%; max-height: 200px; }}
  .main {{ padding: 20px; }}
}}
</style>
</head>
<body>

<nav class="sidebar">
  <div class="sidebar-header">
    <h1>ML予測アプリ</h1>
    <p>マネタイズ戦略ドキュメント</p>
    <p style="margin-top:4px;color:#4ade80;font-size:10px;">最終更新: 2026-03-08</p>
  </div>
  {nav_html}
</nav>

<main class="main">
  {sections_html}
</main>

<script>
function showSection(id) {{
  // 全セクションを非表示
  document.querySelectorAll('.doc-section').forEach(s => s.style.display = 'none');
  // 指定セクションを表示
  const target = document.getElementById(id);
  if (target) {{
    target.style.display = 'block';
    document.querySelector('.main').scrollTop = 0;
  }}
  // ナビゲーションのアクティブ状態更新
  document.querySelectorAll('.nav-item').forEach(a => a.classList.remove('active'));
  const navLink = document.querySelector(`a[onclick="showSection('${{id}}')"]`);
  if (navLink) navLink.classList.add('active');
}}
// 初期状態: 最初のナビをアクティブに
document.querySelector('.nav-item')?.classList.add('active');
</script>

</body>
</html>"""

    output_path = os.path.join(DOCS_DIR, "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(page_html)
    print(f"生成完了: {output_path}")
    print(f"ブラウザで開いてください: file://{output_path}")


if __name__ == "__main__":
    generate_html()
