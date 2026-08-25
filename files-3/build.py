#!/usr/bin/env python3
"""
Build the MEDucation site from content.json.

    python3 build.py

Publishing a summary is then:
  1. drop the PDF into  pdfs/
  2. drop the summary body (the HTML WeasyPrint prints from) into  bodies/
  3. flip "published": true in content.json and name those two files
  4. run this

Everything else — the block spine, the home ticker, the counts, prev/next —
is derived. Nothing is edited by hand twice.
"""

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "dist"
BODIES = ROOT / "bodies"
PDFS = ROOT / "pdfs"

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link href="https://fonts.googleapis.com/css2?'
    "family=IBM+Plex+Mono:wght@400;500&"
    "family=IBM+Plex+Sans:wght@400;500;600&"
    "family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&display=swap\" rel=\"stylesheet\">"
)

MARK = (
    '<svg viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="5" '
    'stroke-linecap="round" aria-hidden="true">'
    '<circle cx="50" cy="50" r="40"/>'
    '<path d="M35 28 v14 a15 15 0 0 0 30 0 V28"/>'
    '<path d="M50 57 v9"/>'
    '<circle cx="50" cy="72" r="6"/>'
    "</svg>"
)


def slug(text):
    keep = [c.lower() if c.isalnum() else "-" for c in text]
    out = "".join(keep)
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-")


def page(title, theme, depth, body, extra_body_class=""):
    """Wrap page content in the shared shell."""
    up = "../" * depth
    classes = f"subj-{theme} {extra_body_class}".strip()
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
{FONTS}
<link rel="stylesheet" href="{up}assets/style.css">
</head>
<body class="{classes}">
{body}
</body>
</html>
"""


def masthead(depth, home_href, back_label=None):
    up = "../" * depth
    back = f'<span class="masthead__back">{back_label}</span>' if back_label else ""
    return f"""<header class="masthead">
  <div class="wrap">
    <a class="masthead__inner" href="{up}{home_href}">
      <span class="mark">{MARK}</span>
      <span class="wordmark">MED<em>ucation</em></span>
      {back}
    </a>
  </div>
</header>"""


def footer(line, second=None):
    tail = f"<br>{second}" if second else ""
    return f'<footer class="foot"><strong>{line}</strong>{tail}</footer>'


def build_home(data):
    site = data["site"]
    cards = []
    exams = []

    for b in data["blocks"]:
        lectures = b["lectures"]
        done = sum(1 for l in lectures if l.get("published"))
        pips = "".join(
            f'<span class="pip{" pip--done" if l.get("published") else ""}"></span>'
            for l in lectures
        )
        state = "complete" if done == len(lectures) else "in progress"
        cards.append(f"""    <a class="blockcard subj-{b['theme']}" href="blocks/{b['id']}.html">
      <div class="blockcard__subject">{b['subject']}</div>
      <div class="blockcard__title">{b['title']}</div>
      <div class="ticker">{pips}</div>
      <div class="blockcard__count">{done} of {len(lectures)} published &nbsp;·&nbsp; {state}</div>
    </a>""")

        ex = b.get("exam")
        if ex:
            exams.append(f"""    <a class="examcard subj-{b['theme']}" href="exam/{ex['id']}.html">
      <div class="blockcard__subject">{b['subject']} · {b['title']}</div>
      <div class="examcard__title">{ex['title']}</div>
      <div class="examcard__meta">{ex['questions']} questions · {ex['minutes']} minutes · {ex['note']}</div>
    </a>""")

    exam_section = ""
    if exams:
        exam_section = (
            '  <section>\n    <h2 class="seclabel">Mock exams</h2>\n'
            + "\n".join(exams)
            + "\n  </section>\n"
        )

    body = f"""{masthead(0, "index.html")}

<main class="wrap">

  <div class="pagehead">
    <h1>{site['tagline']}</h1>
    <p>{site['subtitle']}</p>
  </div>

  <section>
    <h2 class="seclabel">Blocks</h2>
{chr(10).join(cards)}
  </section>

{exam_section}
  <p class="notice">
    Summaries are made to study <strong>alongside</strong> the lecture, not instead of it.
    Read the slides first — only your lecturer knows what he stressed out loud.
  </p>

  {footer(f"{site['name']} by {site['author']}", site['institution'])}

</main>"""

    (OUT / "index.html").write_text(page(site["name"], "brand", 0, body), encoding="utf-8")


def build_block(data, b):
    lectures = b["lectures"]
    done = sum(1 for l in lectures if l.get("published"))
    rows = []

    for l in lectures:
        if l.get("published"):
            node = "node node--done"
            href = f"../lectures/{b['id']}-{slug(l['code'])}.html"
            meta = f"{l.get('lecturer', '')} &nbsp;·&nbsp; " if l.get("lecturer") else ""
            inner = f"""<a class="lecrow" href="{href}">
        <div class="lecrow__code">{l['code']}</div>
        <div class="lecrow__title">{l['title']}</div>
        <div class="lecrow__meta">{meta}<span class="tag">Read</span></div>
      </a>"""
        else:
            node = "node"
            inner = f"""<div class="lecrow lecrow--soon">
        <div class="lecrow__code">{l['code']}</div>
        <div class="lecrow__title">{l['title']}</div>
        <div class="lecrow__meta"><span class="tag tag--soon">Coming</span></div>
      </div>"""
        rows.append(f'    <li>\n      <span class="{node}"></span>\n      {inner}\n    </li>')

    exam_section = ""
    ex = b.get("exam")
    if ex:
        exam_section = f"""
  <section>
    <h2 class="seclabel">When the block ends</h2>
    <a class="examcard" href="../exam/{ex['id']}.html">
      <div class="blockcard__subject">Mock exam</div>
      <div class="examcard__title">{ex['title']}</div>
      <div class="examcard__meta">{ex['questions']} questions · {ex['minutes']} minutes · {ex['note']}</div>
    </a>
  </section>
"""

    byline = f"{b['subject']} {b['block']} Block · MEDucation by {data['site']['author']}"

    body = f"""{masthead(1, "index.html", "← blocks")}

<main class="wrap">

  <div class="pagehead">
    <p class="eyebrow">{b['subject']}</p>
    <h1>{b['title']}</h1>
    <p>{done} of {len(lectures)} published · new summaries drop as the lectures happen</p>
  </div>

  <ul class="spine">
{chr(10).join(rows)}
  </ul>
{exam_section}
  {footer(byline)}

</main>"""

    path = OUT / "blocks" / f"{b['id']}.html"
    path.write_text(
        page(f"{b['subject']} · {b['title']} — MEDucation", b["theme"], 1, body),
        encoding="utf-8",
    )


def build_lectures(data, b):
    published = [l for l in b["lectures"] if l.get("published")]
    order = b["lectures"]

    for l in published:
        i = order.index(l)
        prev_l = next((x for x in reversed(order[:i]) if x.get("published")), None)
        next_l = next((x for x in order[i + 1:] if x.get("published")), None)
        next_pending = order[i + 1] if i + 1 < len(order) else None

        if prev_l:
            left = f'<a href="{b["id"]}-{slug(prev_l["code"])}.html">← {prev_l["code"]}</a>'
        else:
            left = "<span>← First lecture</span>"

        if next_l:
            right = f'<a href="{b["id"]}-{slug(next_l["code"])}.html">{next_l["code"]} →</a>'
        elif next_pending:
            right = f'<span>{next_pending["code"]} coming</span>'
        else:
            right = "<span>End of block</span>"

        body_file = BODIES / l["body"]
        if body_file.exists():
            summary = body_file.read_text(encoding="utf-8")
        else:
            summary = (
                '<p class="notice"><strong>No summary body found.</strong> '
                f'Expected <code>bodies/{l["body"]}</code>. The page structure is here; '
                "drop the file in and rebuild.</p>"
            )

        pdf_bar = ""
        if l.get("pdf"):
            pdf_bar = f"""
<div class="downloadbar">
  <div class="downloadbar__inner">
    <span class="downloadbar__label">PDF · {l.get('pdf_note', 'download')}</span>
    <a class="btn" href="../pdfs/{l['pdf']}" download>Download PDF</a>
  </div>
</div>"""

        byline = f"{b['subject']} {b['block']} Block · MEDucation by {data['site']['author']}"

        content = f"""{masthead(1, "index.html", f"← {b['title']}")}

<main class="wrap summary">

  <div class="pagehead">
    <p class="eyebrow">{b['subject']} · {b['title']} · {l['code']}</p>
    <h1>{l['title']}</h1>
    <p>{l.get('lecturer', '')}</p>
  </div>

{summary}

  <h2>Spaced review</h2>
  <div class="review">
    <span>Day 1</span><span>Day 3</span><span>Day 7</span><span>Day 21</span><span>Pre-exam</span>
  </div>

  <div class="pager">
    {left}
    {right}
  </div>

  {footer(byline, "Study alongside the lecture, not instead of it.")}

</main>
{pdf_bar}"""

        path = OUT / "lectures" / f"{b['id']}-{slug(l['code'])}.html"
        path.write_text(
            page(f"{l['title']} — MEDucation", b["theme"], 1, content),
            encoding="utf-8",
        )


def build_exam(data, b):
    ex = b.get("exam")
    if not ex:
        return

    if ex["state"] == "closed":
        cta = f'<p class="notice">Not open yet. The exam {ex["note"]}.</p>'
    else:
        cta = '<p style="margin-top:26px"><a class="btn" href="#">Begin</a></p>'

    body = f"""<div class="examshell">

  <div class="examtop">
    <span class="examtop__id">{b['subject']} · {b['title']}</span>
    <span class="timer">{ex['minutes']}:00</span>
  </div>

  <div class="pagehead" style="padding-top:0">
    <h1>{ex['title']}</h1>
    <p>{ex['questions']} questions · {ex['minutes']} minutes · one attempt</p>
  </div>

  <ul>
    <li>The timer starts when you press begin and does not pause.</li>
    <li>You can move between questions freely and change answers.</li>
    <li>It submits itself when the time runs out.</li>
    <li>Your score and the answers appear as soon as you submit.</li>
  </ul>

  {cta}

  <p style="margin-top:26px">
    <a class="btn btn--quiet" href="../blocks/{b['id']}.html">Back to the {b['title']}</a>
  </p>

  {footer(f"MEDucation by {data['site']['author']}")}

</div>"""

    path = OUT / "exam" / f"{ex['id']}.html"
    path.write_text(
        page(f"{ex['title']} — MEDucation", b["theme"], 1, body, "exam-mode"),
        encoding="utf-8",
    )


def main():
    data = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))

    if OUT.exists():
        shutil.rmtree(OUT)
    for sub in ("blocks", "lectures", "exam", "assets", "pdfs"):
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    shutil.copytree(ROOT / "assets", OUT / "assets", dirs_exist_ok=True)
    if PDFS.exists():
        shutil.copytree(PDFS, OUT / "pdfs", dirs_exist_ok=True)

    build_home(data)
    for b in data["blocks"]:
        build_block(data, b)
        build_lectures(data, b)
        build_exam(data, b)

    pages = sum(1 for _ in OUT.rglob("*.html"))
    print(f"Built {pages} pages into {OUT}")


if __name__ == "__main__":
    main()
