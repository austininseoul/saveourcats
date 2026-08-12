# saveourcats.my

The public record of two cats — **Orion and Nova** — held at the KLIA Animal Quarantine
Station in Malaysia beyond their confirmed release date.

They entered Malaysia legally on **16 July 2026** through a MAQIS-registered agent, with
every document, vaccination and fee in order. Release was confirmed for **30 July 2026**.
They are still inside.

---

## The case in short

| | |
|---|---|
| Admitted to quarantine | 16 July 2026, KLIA |
| Release confirmed for | 30 July 2026 — not honoured |
| Regulation applied | issued ~28 July 2026, **twelve days after admission** |
| Compound demanded and paid | MYR 2,000 on 7 August 2026 (ref R39656871355) |
| Assurance given at the time | no repeat titre test required |
| Position three days later | repeat titre test now required |
| Boarding charges | MYR 80/day, still accruing |
| Official receipt for the compound | none issued |
| Written compound notice naming an offence | none issued |

---

## Editing the site

`src/page.html` is the source. `index.html` is generated — **never edit it by hand.**

```bash
python3 build.py     # src/page.html -> index.html
```

The build step wraps the source in a full HTML document and injects the meta
description, Open Graph and Twitter share cards, theme colours and favicon.

The day counter in the headline and byline is computed in the browser from the
16 July admission date. It does not need updating.

## Before the site goes public

1. **Add `og-image.jpg`** to the repo root — a real photograph of Orion and Nova,
   1200×630. This is the image that appears when the link is shared. Without it the
   share cards render blank.
2. **Confirm DNS** — see below.
3. **Flip the repo to public** and enable Pages.

## Hosting

GitHub Pages, custom domain `saveourcats.my` (see `CNAME`).

DNS at the registrar:

```
A     @    185.199.108.153
A     @    185.199.109.153
A     @    185.199.110.153
A     @    185.199.111.153
AAAA  @    2606:50c0:8000::153
AAAA  @    2606:50c0:8001::153
AAAA  @    2606:50c0:8002::153
AAAA  @    2606:50c0:8003::153
CNAME www  austininseoul.github.io
```

Then: Settings → Pages → Custom domain → `saveourcats.my` → Enforce HTTPS.

---

## Sourcing

Every date, quotation and figure published on this site is drawn from dated
correspondence, payment records and photographs held by the owners. Quotations are
reproduced verbatim from written messages. Nothing is reconstructed from memory.

**Evidence files are deliberately not committed to this repository.** They contain
personal information and are held privately. They are available to journalists, to
other affected owners, and to any officer who requests them.

## Scope

This account concerns the conduct of a process and the decisions of a department.
It makes no allegation against any individual officer. Any correction from MAQIS,
DVS or the Ministry of Agriculture and Food Security will be published in full and
without edit.

---

## Share kit

`share/` holds ready-to-post graphics at platform dimensions. Generated from
`src/cards.html` — edit that, re-render, replace.

| File | Size | Use |
|---|---|---|
| `card-1-hook.jpg` | 1080×1350 | Instagram / Threads — the opener, with the photo |
| `card-2-quotes.jpg` | 1080×1350 | The documented reversal, both quotes side by side |
| `card-3-numbers.jpg` | 1080×1080 | Square — the case in five figures |
| `card-4-malay.jpg` | 1080×1350 | Bahasa Malaysia version |
| `og-image.jpg` | 1200×630 | Link preview card (referenced by index.html) |

Rendering is done by loading `src/cards.html?only=<id>` in a browser, printing to
PDF at the exact pixel dimensions, then downsampling from 2× for crisp text.
Screenshot capture was unreliable at these sizes; PDF is exact.

---

## Typefaces

**PP Editorial Old Regular** sets the headlines, pull quotes and the documentary quotations —
at display sizes its high contrast carries the page without needing weight. Everything else,
including all body copy, labels and dates, is **PP Neue Montreal**. No monospace anywhere;
labels get their character from case, tracking and weight instead.

Both by [Pangram Pangram](https://pangrampangram.com).

Both are the **Free For Personal Use** cuts. This is a non-commercial advocacy site, but if
it ever carries donations, sponsorship, or anything commercial, the licence must be upgraded
first. The EULAs are in the original font pack.

`fonts/` holds Latin-subset WOFF2 builds — 68 KB for four faces. Regenerate with:

```bash
bash tools-make-fonts.sh    # needs fonttools + brotli, paths at the top of the file
```

## Asset strategy

- `index.html` references `img/` and `fonts/` normally, so browsers cache them between visits
- `artifact.html` inlines every asset as a data URI, because the claude.ai artifact CSP
  blocks external requests and relative paths do not resolve there

Both are produced by the same `build.py` run.

---

## Dispatches (the blog)

Write a post as markdown in `posts/`, named **`YYYY-MM-DD-slug.md`**:

```markdown
---
title: Day 28 — still no collection date
date: 2026-08-13
summary: One sentence. Used on the archive page and in the share card.
---

Body in markdown. `##` for section headings, `>` for quotes,
`-` for lists, `**bold**`, `*italic*`, `[links](https://…)`.
```

Then:

```bash
python3 build.py
```

That regenerates, in one pass:

- `blog/index.html` — the archive, newest first
- `blog/<slug>/index.html` — one page per post, with BlogPosting schema and prev/next links
- the **Dispatches** section on the homepage, showing the three most recent
- `sitemap.xml`, now including every post

The markdown parser lives in `blog.py` and has no dependencies — it covers headings,
paragraphs, lists, blockquotes, rules, images, links and inline emphasis. Page templates
are in `blogpages.py` and pull their CSS straight out of `src/page.html`, so the blog can
never drift from the main article's design.
