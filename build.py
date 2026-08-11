#!/usr/bin/env python3
"""
Build the standalone site from src/page.html.

src/page.html is the editable source — it holds only <title>, <style>,
the page markup and <script>. This wraps it in a full HTML document with
the meta tags, social cards and favicon that the live site needs.

    python3 build.py        # writes index.html

Edit src/page.html, run this, commit. Never hand-edit index.html.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src" / "page.html"
OUT = ROOT / "index.html"

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

try:
    t0 = src.index("<title>")
    t1 = src.index("</title>") + len("</title>")
except ValueError:
    sys.exit("source must contain a <title> tag")

title_tag = src[t0:t1]
body = src[t1:].lstrip()

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

<meta name="theme-color" content="#FBFAF8" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0E0F12" media="(prefers-color-scheme: dark)">
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>&#128008;</text></svg>">

<style>
  *, *::before, *::after {{ box-sizing: border-box; }}
  body {{ margin: 0; }}
  img {{ max-width: 100%; height: auto; display: block; }}
</style>
</head>
<body>
{body}
</body>
</html>
"""

OUT.write_text(doc)
print(f"built {OUT.relative_to(ROOT)}  ({len(doc):,} bytes)")
