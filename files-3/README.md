# MEDucation site

Static site, generated from one config file. No dependencies beyond Python 3.

## Build

    python3 build.py

Output lands in `dist/`. That folder is the website — nothing else gets deployed.

## Publishing a summary

Four steps, and only one of them is an edit:

1. Put the PDF in `pdfs/`
2. Put the summary body — the HTML that WeasyPrint prints from, without the
   `<html>` wrapper — in `bodies/`
3. In `content.json`, set that lecture's `"published": true` and name the two files
4. `python3 build.py`

The block spine, the home page ticker, the "1 of 7" counts and the prev/next links
are all derived from `content.json`. Nothing is edited in two places, so the site
can't disagree with itself about what exists.

## Adding a block

Append an object to `blocks` in `content.json`. It needs `id`, `subject`, `theme`,
`block`, `title`, a `lectures` list, and optionally an `exam`. The home page picks
it up on the next build.

`theme` is one of: `pathology`, `physiology`, `micro`, `history`, `pharm`, `anatomy`.

## Layout

```
content.json      what exists — the only file edited when publishing
build.py          generator
assets/           stylesheet and the logo mark
bodies/           summary bodies (HTML fragments)
pdfs/             the downloadable PDFs
dist/             generated — do not edit, it gets wiped each build
```

## Hosting

Push the repo to GitHub, turn on Pages, point it at `dist/`. Free, and it
redeploys on every push.

## Notes

- One colour themes a whole page, set by a `subj-*` class on `<body>`.
- The lecture numbers currently in `content.json` are a guess at the GIT sequence
  and need replacing with the real ones.
- The exam page is a shell. The timer and questions aren't built yet.
