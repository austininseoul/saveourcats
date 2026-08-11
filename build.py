#!/usr/bin/env python3
"""
Build the site from src/page.html.

    python3 build.py

Outputs:
  index.html     for GitHub Pages — relative asset URLs, so fonts and images
                 are cached by the browser across visits
  artifact.html  for claude.ai — every asset inlined as a data URI, because
                 the artifact CSP blocks external requests and relative paths
                 do not resolve there

src/page.html is the editable source. Never hand-edit either output.
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

ASSET_RE = re.compile(r"""(?:src="|url\(')((?:img|fonts)/[^"')]+)""")


def inline_assets(html: str) -> str:
    """Replace img/ and fonts/ references with data: URIs."""
    total = 0

    def datauri(rel: str) -> str | None:
        nonlocal total
        path = ROOT / rel
        if not path.exists():
            print(f"  ! missing asset: {rel}")
            return None
        mime = mimetypes.guess_type(path.name)[0] or (
            "font/woff2" if path.suffix == ".woff2" else "application/octet-stream"
        )
        b64 = base64.b64encode(path.read_bytes()).decode()
        total += len(b64)
        print(f"  inlined {rel:<34} {len(b64)//1024:>4} KB")
        return f"data:{mime};base64,{b64}"

    def sub_src(m):
        uri = datauri(m.group(1))
        return f'src="{uri}"' if uri else m.group(0)

    def sub_url(m):
        uri = datauri(m.group(1))
        return f"url('{uri}')" if uri else m.group(0)

    html = re.sub(r'src="((?:img|fonts)/[^"]+)"', sub_src, html)
    html = re.sub(r"url\('((?:img|fonts)/[^']+)'\)", sub_url, html)
    print(f"  ── inlined total: {total//1024} KB base64")
    return html


try:
    t0 = src.index("<title>")
    t1 = src.index("</title>") + len("</title>")
except ValueError:
    sys.exit("source must contain a <title> tag")

title_tag = src[t0:t1]
body = src[t1:].lstrip()

# ── artifact: everything inlined ──
print("building artifact.html")
(ROOT / "artifact.html").write_text(title_tag + "\n\n" + inline_assets(body))

# ── standalone: relative URLs, preload the two faces above the fold ──
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
<link rel="icon" href="img/favicon.png" sizes="64x64">
<link rel="apple-touch-icon" href="img/apple-touch-icon.png">

<link rel="preload" as="font" type="font/woff2" href="fonts/editorial-ultrabold.woff2" crossorigin>
<link rel="preload" as="font" type="font/woff2" href="fonts/editorial-regular.woff2" crossorigin>
<link rel="preload" as="font" type="font/woff2" href="fonts/montreal-regular.woff2" crossorigin>

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

print(f"\nbuilding index.html")
print(f"  index.html     {len(doc):,} bytes (assets served separately)")
print(f"  artifact.html  {(ROOT / 'artifact.html').stat().st_size:,} bytes (all inlined)")
