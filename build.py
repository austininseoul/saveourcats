#!/usr/bin/env python3
"""
Build the site from src/page.html.

    python3 build.py

Outputs:
  index.html     standalone page for GitHub Pages (full document, images inlined)
  artifact.html  same page in claude.ai artifact format (no doctype/head wrapper)

src/page.html is the editable source. It references images with ordinary relative
paths (img/foo.jpg); the build inlines them as data URIs so the published page is
self-contained and renders identically wherever it is hosted.

Never hand-edit index.html or artifact.html.
"""
import base64
import mimetypes
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src" / "page.html"

DESC = (
    "Orion and Nova entered Malaysia legally on 16 July 2026 with every document "
    "and fee in order. They were cleared for release on 30 July. They are still held "
    "at KLIA quarantine, under a regulation issued twelve days after they arrived."
)
SHARE_TITLE = "Caged 27 days. We paid the fine. Then nothing."
SHARE_DESC = (
    "Two cats cleared every requirement to enter Malaysia. They are still locked in "
    "quarantine at KLIA — under a rule issued after they arrived."
)

if not SRC.exists():
    sys.exit(f"missing source: {SRC}")

src = SRC.read_text()


def inline_images(html: str) -> str:
    """Replace src="img/..." with a data: URI."""
    def sub(m):
        path = ROOT / m.group(1)
        if not path.exists():
            print(f"  ! missing image, left as-is: {m.group(1)}")
            return m.group(0)
        mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
        b64 = base64.b64encode(path.read_bytes()).decode()
        print(f"  inlined {m.group(1)}  ({len(b64)//1024} KB base64)")
        return f'src="data:{mime};base64,{b64}"'
    return re.sub(r'src="(img/[^"]+)"', sub, html)


src = inline_images(src)

try:
    t0 = src.index("<title>")
    t1 = src.index("</title>") + len("</title>")
except ValueError:
    sys.exit("source must contain a <title> tag")

title_tag = src[t0:t1]
body = src[t1:].lstrip()

# ── artifact format: title + content, no document wrapper ──
(ROOT / "artifact.html").write_text(title_tag + "\n\n" + body)

# ── standalone document for GitHub Pages ──
doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

{title_tag}
<meta name="description" content="{DESC}">
<link rel="canonical" href="https://saveourcats.my/">

<meta property="og:type" content="article">
<meta property="og:site_name" content="saveourcats.my">
<meta property="og:url" content="https://saveourcats.my/">
<meta property="og:title" content="{SHARE_TITLE}">
<meta property="og:description" content="{SHARE_DESC}">
<meta property="og:image" content="https://saveourcats.my/og-image.jpg">
<meta property="og:image:alt" content="Orion and Nova">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{SHARE_TITLE}">
<meta name="twitter:description" content="{SHARE_DESC}">
<meta name="twitter:image" content="https://saveourcats.my/og-image.jpg">

<meta name="theme-color" content="#FBFAF8">
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>&#128008;</text></svg>">

<style>
  *, *::before, *::after {{ box-sizing: border-box; }}
  html {{ color-scheme: light; }}
  body {{ margin: 0; }}
  img {{ max-width: 100%; height: auto; display: block; }}
</style>
</head>
<body>
{body}
</body>
</html>
"""
(ROOT / "index.html").write_text(doc)

print(f"\n  index.html     {len(doc):,} bytes")
print(f"  artifact.html  {len(title_tag) + len(body):,} bytes")
