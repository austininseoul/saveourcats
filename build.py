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
import datetime
import html as _html

import blog as blogmod
import blogpages

ROOT = pathlib.Path(__file__).parent
TODAY = datetime.date.today().isoformat()
BLOG_CSS = blogpages.EXTRA
SRC = ROOT / "src" / "page.html"

DESC = (
    "Orion and Nova entered Malaysia legally on 16 July 2026 with every document "
    "and fee in order. They were cleared for release on 30 July. They are still held "
    "at KLIA quarantine, under a regulation issued twelve days after they arrived."
)
SHARE_TITLE = "Save Our Cats From Over 27+ Days Of Captivity. No Answer From Authorities."
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

# ── blog ──────────────────────────────────────────────────────────────
posts = blogmod.load_all()
n = blogpages.build(posts)
print(f"  blog: {n} post(s) -> blog/index.html + {n} post page(s)")

if posts:
    latest = posts[:3]
    cards = "".join(
        f'''      <a class="dcard" href="/blog/{p["slug"]}/">
        {'<span class="dcard-img"><img src="' + p["hero"] + '" alt=""></span>' if p.get("hero") else ''}
        <span class="dcard-d">{p["pretty"]}</span>
        <span class="dcard-t">{_html.escape(p["title"])}</span>
        <span class="dcard-s">{_html.escape(p["summary"])}</span>
        <span class="dcard-go">Read the dispatch →</span>
      </a>\n'''
        for p in latest
    )
    DISPATCHES = f'''
  <section id="dispatches">
    <p class="eyebrow">Dispatches</p>
    <h2>We are writing down what happens each day.</h2>
    <p class="dispatch-lead">
      Every time we have relied on something being said rather than written, it has changed.
      So there is now a dated record of every development, kept as it happens.
    </p>
    <div class="dgrid">
{cards}    </div>
    <a class="dispatch-more" href="/blog/">All {len(posts)} dispatches →</a>
  </section>
'''
    body = body.replace("  <div class=\"note\">", DISPATCHES + "\n  <div class=\"note\">", 1)


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

<link rel="preload" as="font" type="font/woff2" 
<link rel="preload" as="font" type="font/woff2" href="fonts/editorial-regular.woff2" crossorigin>
<link rel="preload" as="font" type="font/woff2" href="fonts/montreal-regular.woff2" crossorigin>

<style>
  *, *::before, *::after {{ box-sizing: border-box; }}
  html {{ color-scheme: light; }}
  body {{ margin: 0; }}
  img {{ max-width: 100%; height: auto; display: block; }}
</style>
<style>{BLOG_CSS}</style>

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "NewsArticle",
  "headline": "{SHARE_TITLE}",
  "description": "{SHARE_DESC}",
  "image": ["https://saveourcats.my/og-image.jpg"],
  "datePublished": "2026-08-12T00:00:00+08:00",
  "dateModified": "{TODAY}T00:00:00+08:00",
  "inLanguage": ["en", "ms"],
  "isAccessibleForFree": true,
  "author": {{ "@type": "Person", "name": "The owners of Orion and Nova" }},
  "publisher": {{
    "@type": "Organization",
    "name": "saveourcats.my",
    "url": "https://saveourcats.my/",
    "logo": {{ "@type": "ImageObject", "url": "https://saveourcats.my/img/logo.png" }}
  }},
  "mainEntityOfPage": {{ "@type": "WebPage", "@id": "https://saveourcats.my/" }},
  "contentLocation": {{
    "@type": "Place",
    "name": "KLIA Animal Quarantine Station",
    "address": {{
      "@type": "PostalAddress",
      "streetAddress": "Kompleks MAQIS KLIA, Jalan Pekeliling 4",
      "addressLocality": "Sepang",
      "addressRegion": "Selangor",
      "postalCode": "64050",
      "addressCountry": "MY"
    }}
  }},
  "about": [
    {{ "@type": "Thing", "name": "Animal quarantine" }},
    {{ "@type": "Thing", "name": "Pet import Malaysia" }},
    {{ "@type": "GovernmentOrganization", "name": "Malaysian Quarantine and Inspection Services Department (MAQIS)" }}
  ]
}}
</script>
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

# ── sitemap (regenerated so new dispatches are always included) ───────
urls = [("https://saveourcats.my/", "daily", "1.0")]
if posts:
    urls.append(("https://saveourcats.my/blog/", "daily", "0.8"))
    urls += [(f"https://saveourcats.my/blog/{p['slug']}/", "monthly", "0.7") for p in posts]

def _entry(loc, freq, pri, images=""):
    return (f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{TODAY}</lastmod>\n"
            f"    <changefreq>{freq}</changefreq>\n    <priority>{pri}</priority>\n{images}  </url>\n")

IMAGES = """    <image:image>
      <image:loc>https://saveourcats.my/og-image.jpg</image:loc>
      <image:title>Orion and Nova</image:title>
      <image:caption>Two cats held at the KLIA Animal Quarantine Station beyond their confirmed release date.</image:caption>
    </image:image>
    <image:image>
      <image:loc>https://saveourcats.my/img/before-the-flight.jpg</image:loc>
      <image:caption>Orion and Nova the night before their flight to Malaysia, 10 July 2026.</image:caption>
    </image:image>
    <image:image>
      <image:loc>https://saveourcats.my/img/visit-day-22.jpg</image:loc>
      <image:caption>A supervised visit at the KLIA quarantine station, 6 August 2026.</image:caption>
    </image:image>
"""

sm = ['<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
      '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
for i, (loc, freq, pri) in enumerate(urls):
    sm.append(_entry(loc, freq, pri, IMAGES if i == 0 else "").rstrip("\n"))
sm.append("</urlset>")
(ROOT / "sitemap.xml").write_text("\n".join(sm) + "\n")
print(f"  sitemap: {len(urls)} URL(s)")
