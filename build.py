#!/usr/bin/env python3
"""
Build the MEDucation site from content.json.

    python3 build.py

Structure is three levels deep:

    home            the four Stage 3 blocks
      block         the eight subjects in that block
        subject     the LGs and SGLs for that subject
          lecture   the summary itself, with its PDF

Publishing a summary:
  1. drop the PDF into            pdfs/
  2. drop the summary body into   bodies/
  3. in content.json, add the lecture (or flip "published": true) and name those files
  4. python3 build.py

Everything derived — counts, dots, spine nodes, prev/next — updates itself.
"""

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "docs"
BODIES = ROOT / "bodies"
PDFS = ROOT / "pdfs"

# GitHub Pages recommends a published site under 1 GB. Warn well before that.
SIZE_WARN_MB = 700

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link href="https://fonts.googleapis.com/css2?'
    "family=IBM+Plex+Mono:wght@400;500&"
    "family=IBM+Plex+Sans:wght@400;500;600&"
    'family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&display=swap" rel="stylesheet">'
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
    out = "".join(c.lower() if c.isalnum() else "-" for c in text)
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-")


def page(title, theme, depth, body, body_class=""):
    up = "../" * depth
    classes = f"subj-{theme} {body_class}".strip()
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


def masthead(depth, back=None):
    up = "../" * depth
    back_html = f'<span class="masthead__back">{back}</span>' if back else ""
    return f"""<header class="masthead">
  <div class="wrap">
    <a class="masthead__inner" href="{up}index.html">
      <span class="mark">{MARK}</span>
      <span class="wordmark">MED<em>ucation</em></span>
      {back_html}
    </a>
  </div>
</header>"""


def footer(line, second=None):
    tail = f"<br>{second}" if second else ""
    return f'<footer class="foot"><strong>{line}</strong>{tail}</footer>'


def published(lectures):
    return [l for l in lectures if l.get("published")]


def build_home(data):
    site = data["site"]
    subjects = data["subjects"]
    cards, exams = [], []

    for b in data["blocks"]:
        total = sum(len(published(v)) for v in b["subjects"].values())
        dots = "".join(
            f'<span class="dot subj-{s["theme"]}'
            f'{" dot--on" if published(b["subjects"].get(s["id"], [])) else ""}"></span>'
            for s in subjects
        )
        count = f"{total} summar{'y' if total == 1 else 'ies'}" if total else "Nothing yet"
        cards.append(f"""    <a class="blockcard subj-brand" href="blocks/{b['id']}.html">
      <div class="blockcard__subject">{site['stage']} · {b['short']}</div>
      <div class="blockcard__title">{b['title']}</div>
      <div class="dots">{dots}</div>
      <div class="blockcard__count">{count} &nbsp;·&nbsp; 8 subjects</div>
    </a>""")

        ex = b.get("exam")
        if ex:
            exams.append(f"""    <a class="examcard subj-{ex['theme']}" href="exam/{ex['id']}.html">
      <div class="blockcard__subject">{b['short']} Block</div>
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

    body = f"""{masthead(0)}

<main class="wrap">

  <div class="pagehead">
    <p class="eyebrow">{site['stage']}</p>
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
    site = data["site"]
    cards = []

    for s in data["subjects"]:
        lectures = b["subjects"].get(s["id"], [])
        n = len(published(lectures))
        if n:
            label = f"{n} summar{'y' if n == 1 else 'ies'}"
            cards.append(f"""    <a class="subjcard subj-{s['theme']}" href="../subjects/{b['id']}-{s['id']}.html">
      <div class="subjcard__name">{s['name']}</div>
      <div class="subjcard__count">{label}</div>
    </a>""")
        else:
            cards.append(f"""    <div class="subjcard subjcard--empty">
      <div class="subjcard__name">{s['name']}</div>
      <div class="subjcard__count">Nothing yet</div>
    </div>""")

    exam_section = ""
    ex = b.get("exam")
    if ex:
        exam_section = f"""
  <section>
    <h2 class="seclabel">When the block ends</h2>
    <a class="examcard subj-{ex['theme']}" href="../exam/{ex['id']}.html">
      <div class="blockcard__subject">Mock exam</div>
      <div class="examcard__title">{ex['title']}</div>
      <div class="examcard__meta">{ex['questions']} questions · {ex['minutes']} minutes · {ex['note']}</div>
    </a>
  </section>
"""

    body = f"""{masthead(1, "← blocks")}

<main class="wrap">

  <div class="pagehead">
    <p class="eyebrow">{site['stage']} · {b['short']}</p>
    <h1>{b['title']}</h1>
    <p>Pick a subject.</p>
  </div>

  <div class="subjgrid">
{chr(10).join(cards)}
  </div>
{exam_section}
  {footer(f"{b['title']} Block · MEDucation by {site['author']}")}

</main>"""

    (OUT / "blocks" / f"{b['id']}.html").write_text(
        page(f"{b['title']} — MEDucation", "brand", 1, body), encoding="utf-8"
    )


def build_subject(data, b, s):
    site = data["site"]
    lectures = b["subjects"].get(s["id"], [])
    done = len(published(lectures))

    if not lectures:
        inner = '<div class="empty">No summaries for this subject yet.<br>They appear here as the lectures happen.</div>'
    else:
        rows = []
        for l in lectures:
            if l.get("published"):
                href = f"../lectures/{b['id']}-{s['id']}-{slug(l['code'])}.html"
                meta = f"{l['lecturer']} &nbsp;·&nbsp; " if l.get("lecturer") else ""
                rows.append(f"""    <li>
      <span class="node node--done"></span>
      <a class="lecrow" href="{href}">
        <div class="lecrow__code">{l['code']}</div>
        <div class="lecrow__title">{l['title']}</div>
        <div class="lecrow__meta">{meta}<span class="tag">Read</span></div>
      </a>
    </li>""")
            else:
                rows.append(f"""    <li>
      <span class="node"></span>
      <div class="lecrow lecrow--soon">
        <div class="lecrow__code">{l['code']}</div>
        <div class="lecrow__title">{l['title']}</div>
        <div class="lecrow__meta"><span class="tag tag--soon">Coming</span></div>
      </div>
    </li>""")
        inner = '<ul class="spine">\n' + "\n".join(rows) + "\n  </ul>"

    sub = f"{done} of {len(lectures)} published" if lectures else "Nothing published yet"

    body = f"""{masthead(1, f"← {b['short']}")}

<main class="wrap">

  <div class="pagehead">
    <p class="crumb"><a href="../blocks/{b['id']}.html">{b['short']}</a> &nbsp;/&nbsp; {s['name']}</p>
    <h1>{s['name']}</h1>
    <p>{sub}</p>
  </div>

  {inner}

  {footer(f"{s['name']} · {b['title']} Block · MEDucation by {site['author']}")}

</main>"""

    (OUT / "subjects" / f"{b['id']}-{s['id']}.html").write_text(
        page(f"{s['name']} · {b['short']} — MEDucation", s["theme"], 1, body), encoding="utf-8"
    )


def build_lectures(data, b, s):
    site = data["site"]
    lectures = b["subjects"].get(s["id"], [])

    for l in published(lectures):
        i = lectures.index(l)
        prev_l = next((x for x in reversed(lectures[:i]) if x.get("published")), None)
        next_l = next((x for x in lectures[i + 1:] if x.get("published")), None)
        pending = lectures[i + 1] if i + 1 < len(lectures) else None

        base = f"{b['id']}-{s['id']}"
        left = (
            f'<a href="{base}-{slug(prev_l["code"])}.html">← {prev_l["code"]}</a>'
            if prev_l else "<span>← First one</span>"
        )
        if next_l:
            right = f'<a href="{base}-{slug(next_l["code"])}.html">{next_l["code"]} →</a>'
        elif pending:
            right = f'<span>{pending["code"]} coming</span>'
        else:
            right = "<span>End of subject</span>"

        body_file = BODIES / l.get("body", "")
        if l.get("body") and body_file.exists():
            summary = body_file.read_text(encoding="utf-8")
        else:
            summary = (
                '<p class="notice"><strong>No summary body found.</strong> Expected '
                f'<code>bodies/{l.get("body", "?")}</code>. Drop it in and rebuild.</p>'
            )

        pdf_bar = ""
        if l.get("pdf"):
            missing = "" if (PDFS / l["pdf"]).exists() else " — file not in pdfs/ yet"
            pdf_bar = f"""
<div class="downloadbar">
  <div class="downloadbar__inner">
    <span class="downloadbar__label">{l['code']} · PDF{f" · {l['pdf_note']}" if l.get('pdf_note') else ''}{missing}</span>
    <a class="btn" href="../pdfs/{l['pdf']}" download>Download PDF</a>
  </div>
</div>"""

        byline = f"{s['name']} · {b['title']} Block · MEDucation by {site['author']}"

        content = f"""{masthead(1, f"← {s['name']}")}

<main class="wrap summary">

  <div class="pagehead">
    <p class="crumb"><a href="../blocks/{b['id']}.html">{b['short']}</a> &nbsp;/&nbsp;
      <a href="../subjects/{b['id']}-{s['id']}.html">{s['name']}</a> &nbsp;/&nbsp; {l['code']}</p>
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

        (OUT / "lectures" / f"{base}-{slug(l['code'])}.html").write_text(
            page(f"{l['title']} — MEDucation", s["theme"], 1, content), encoding="utf-8"
        )


def build_exam(data, b):
    ex = b.get("exam")
    if not ex:
        return
    site = data["site"]

    if ex["state"] == "closed":
        cta = f'<p class="notice">Not open yet. The exam {ex["note"]}.</p>'
    else:
        cta = '<p style="margin-top:26px"><a class="btn" href="#">Begin</a></p>'

    body = f"""<div class="examshell">

  <div class="examtop">
    <span class="examtop__id">{b['short']} Block</span>
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
    <a class="btn btn--quiet" href="../blocks/{b['id']}.html">Back to {b['short']}</a>
  </p>

  {footer(f"MEDucation by {site['author']}")}

</div>"""

    (OUT / "exam" / f"{ex['id']}.html").write_text(
        page(f"{ex['title']} — MEDucation", ex["theme"], 1, body, "exam-mode"), encoding="utf-8"
    )


def report_size():
    total = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file())
    mb = total / 1_048_576
    pdfs = sorted(OUT.glob("pdfs/*.pdf"), key=lambda p: -p.stat().st_size)
    print(f"Site size: {mb:.1f} MB")
    if pdfs:
        biggest = pdfs[0]
        print(f"Largest PDF: {biggest.name} ({biggest.stat().st_size / 1_048_576:.1f} MB)")
    if mb > SIZE_WARN_MB:
        print(
            f"  WARNING — over {SIZE_WARN_MB} MB. GitHub Pages wants the site under 1 GB.\n"
            "  Shrink the PDFs, e.g.:\n"
            "    gs -sDEVICE=pdfwrite -dPDFSETTINGS=/ebook -dNOPAUSE -dBATCH \\\n"
            "       -sOutputFile=small.pdf big.pdf"
        )


def main():
    data = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))

    if OUT.exists():
        shutil.rmtree(OUT)
    for sub in ("blocks", "subjects", "lectures", "exam", "assets", "pdfs"):
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    shutil.copytree(ROOT / "assets", OUT / "assets", dirs_exist_ok=True)
    if PDFS.exists():
        shutil.copytree(PDFS, OUT / "pdfs", dirs_exist_ok=True)

    # serve files as-is instead of running Jekyll over them
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    build_home(data)
    for b in data["blocks"]:
        build_block(data, b)
        for s in data["subjects"]:
            build_subject(data, b, s)
            build_lectures(data, b, s)
        build_exam(data, b)

    pages = sum(1 for _ in OUT.rglob("*.html"))
    print(f"Built {pages} pages into {OUT}")
    report_size()


if __name__ == "__main__":
    main()
