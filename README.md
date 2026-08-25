# MEDucation site

Static site, generated from one config file. Python 3, no other dependencies.

## Build

    python3 build.py

Output goes to `docs/`. That folder is the website. GitHub Pages is set to serve
`/docs` on the main branch.

## Structure

    home          the four Stage 3 blocks
      block       the eight subjects in that block
        subject   the LGs and SGLs
          lecture the summary, with its PDF download

## Publishing a summary — the weekly job

1. Put the PDF in `pdfs/`, named `<block>-<subject>-<code>.pdf`
   e.g. `git-pathology-lgl-2.pdf`
2. Put the summary body in `bodies/` with the same name but `.html` —
   this is the HTML WeasyPrint prints from, without the `<html>` wrapper
3. In `content.json`, find that lecture and set:

       "published": true,
       "body": "git-pathology-lgl-2.html",
       "pdf":  "git-pathology-lgl-2.pdf",
       "pdf_note": "3 pages"

4. `python3 build.py`
5. Commit and push. Pages redeploys on its own.

The subject count, the block dots, the spine node, and the prev/next links all
update from that one edit. If the PDF is missing, the download button says so
instead of breaking silently.

A lecture with no `pdf` key just has no download button. A summary can be
web-only if you want.

## Adding a lecture that isn't listed yet

Append it to the right subject array in `content.json` with
`"published": false`. It shows as a greyed "Coming" row, so students can see it
exists and isn't lost.

## Subject colours

    anatomy       #0F6E72   teal
    physiology    #1B7A4B   green
    biochemistry  #A32552   raspberry
    histology     #6B3FA0   purple
    genetics      #3C4A5A   steel
    microbiology  #1F5FA8   blue
    pharmacology  #C2610A   orange
    pathology     #B3322B   brick

Change any of them in one line at the top of `assets/style.css`.

## PDF size

The build prints the total site size and the largest PDF. GitHub Pages wants the
published site under 1 GB. Over roughly 200 summaries that means keeping each PDF
in single-digit MB. To shrink one:

    gs -sDEVICE=pdfwrite -dPDFSETTINGS=/ebook -dNOPAUSE -dBATCH \
       -sOutputFile=small.pdf big.pdf

## Files

    content.json   what exists — the only file edited when publishing
    build.py       generator
    assets/        stylesheet and logo mark
    bodies/        summary bodies (HTML fragments)
    pdfs/          the downloadable PDFs
    docs/          generated — wiped and rebuilt each time, never edit by hand

## Still to do

- Real lecture lists for every subject. The GIT pathology list is a guess.
- GUE, NS and Transitional have no lectures listed at all yet.
- The exam page is a shell — no timer, no questions, no leaderboard.
