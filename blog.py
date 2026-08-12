#!/usr/bin/env python3
"""
Blog builder for saveourcats.my — imported by build.py, or run standalone.

Write posts as markdown in posts/, named YYYY-MM-DD-slug.md, with frontmatter:

    ---
    title: Day 28 — still no collection date
    date: 2026-08-13
    summary: One sentence for the index and the share card.
    ---

    Body in markdown.

Then `python3 build.py`. Produces:

    blog/index.html                 the archive
    blog/<slug>/index.html          one page per post

No dependencies — the markdown subset below covers everything a dispatch needs.
"""
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
POSTS = ROOT / "posts"

MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]


# ──────────────────────────── markdown ────────────────────────────

def _inline(t: str) -> str:
    """Escape, then apply inline markdown. Order matters."""
    t = html.escape(t, quote=False)
    t = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1">', t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    # markdown's two-space line break
    t = re.sub(r"  \n", "<br>\n", t)
    return t


def markdown(src: str) -> str:
    """A deliberately small markdown subset: headings, paragraphs, lists,
    blockquotes, rules, images. Everything a dispatch actually uses."""
    out, buf, mode = [], [], None

    def flush():
        nonlocal buf, mode
        if not buf:
            return
        if mode == "p":
            out.append(f"<p>{_inline(' '.join(buf))}</p>")
        elif mode == "ul":
            items = "".join(f"<li>{_inline(b)}</li>" for b in buf)
            out.append(f"<ul>{items}</ul>")
        elif mode == "ol":
            items = "".join(f"<li>{_inline(b)}</li>" for b in buf)
            out.append(f"<ol>{items}</ol>")
        elif mode == "quote":
            out.append(f"<blockquote><p>{_inline(' '.join(buf))}</p></blockquote>")
        buf, mode = [], None

    for raw in src.split("\n"):
        line = raw.rstrip()

        if not line.strip():
            flush()
            continue
        if re.match(r"^---+$", line.strip()):
            flush()
            out.append("<hr>")
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            flush()
            # h1 is the post title, so body headings start at h2:
            # '#' and '##' both -> h2, '###' -> h3, '####' -> h4
            lvl = min(max(len(m.group(1)), 2), 4)
            out.append(f"<h{lvl}>{_inline(m.group(2))}</h{lvl}>")
            continue

        m = re.match(r"^>\s?(.*)$", line)
        if m:
            if mode != "quote":
                flush()
                mode = "quote"
            buf.append(m.group(1))
            continue

        m = re.match(r"^[-*]\s+(.*)$", line)
        if m:
            if mode != "ul":
                flush()
                mode = "ul"
            buf.append(m.group(1))
            continue

        m = re.match(r"^\d+\.\s+(.*)$", line)
        if m:
            if mode != "ol":
                flush()
                mode = "ol"
            buf.append(m.group(1))
            continue

        if mode not in (None, "p"):
            flush()
        mode = "p"
        buf.append(line.strip())

    flush()
    return "\n".join(out)


# ──────────────────────────── posts ────────────────────────────

def parse(path: pathlib.Path) -> dict:
    raw = path.read_text()
    meta, body = {}, raw
    if raw.startswith("---"):
        end = raw.index("\n---", 3)
        for line in raw[3:end].strip().split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        body = raw[end + 4:].lstrip()

    stem = path.stem
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})-(.+)$", stem)
    if not m:
        raise SystemExit(f"post filename must be YYYY-MM-DD-slug.md — got {path.name}")
    y, mo, d, slug = m.groups()

    return {
        "slug": slug,
        "iso": f"{y}-{mo}-{d}",
        "pretty": f"{int(d)} {MONTHS[int(mo) - 1]} {y}",
        "title": meta.get("title", slug.replace("-", " ").capitalize()),
        "summary": meta.get("summary", ""),
        "html": markdown(body),
        "words": len(body.split()),
    }


def load_all() -> list:
    if not POSTS.exists():
        return []
    posts = [parse(p) for p in POSTS.glob("*.md")]
    posts.sort(key=lambda p: (p["iso"], p["slug"]), reverse=True)
    return posts
