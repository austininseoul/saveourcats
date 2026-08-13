#!/usr/bin/env python3
"""
Build the site from src/page.html.

    python3 build.py

Outputs:
  index.html     for GitHub Pages - relative asset URLs, so fonts and images
                 are cached by the browser across visits
  artifact.html  for claude.ai - every asset inlined as a data URI, because
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
import i18n

ROOT = pathlib.Path(__file__).parent
TODAY = datetime.date.today().isoformat()

# ── day counts ────────────────────────────────────────────────────────
# The browser keeps these live and animates them. The figures below are what
# gets written into the file, so search engines, share previews and anyone
# without JavaScript see the count as it stood when the site was last built.
MYT = datetime.timezone(datetime.timedelta(hours=8))
ADMITTED = datetime.datetime(2026, 7, 16, 0, 10, tzinfo=MYT)   # into quarantine
RELEASE_DUE = datetime.datetime(2026, 7, 30, 0, 0, tzinfo=MYT)  # confirmed, not honoured
_now = datetime.datetime.now(MYT)
DAYS = max((_now - ADMITTED).days, 0)
OVERDUE = max((_now - RELEASE_DUE).days, 0)
COUNTS = {"dh": DAYS, "days": DAYS, "d3": DAYS, "d4": OVERDUE}


def stamp_counts(html: str) -> str:
    """Write today's day counts into the spans the browser then keeps live."""
    for el, n in COUNTS.items():
        html = re.sub(rf'(<span id="{el}">)\d+(</span>)', rf"\g<1>{n}\g<2>", html)
    return html


def rooted(html: str) -> str:
    """Make img/ and fonts/ URLs absolute.

    src/page.html writes them relative because artifact.html's inliner matches
    on that form. Relative only resolves at the site root, so /ms/ and
    /blog/<slug>/ asked for /ms/fonts/... and got 404s - no webfonts, broken
    images. Every hosted page therefore gets absolute paths; the artifact is
    built from the relative version first.
    """
    html = re.sub(r'src="((?:img|fonts)/)', r'src="/\1', html)
    html = re.sub(r"url\('((?:img|fonts)/)", r"url('/\1", html)
    return html

LANG_CSS = """
  .langsw {
    display: inline-flex; border: 2px solid var(--ink);
    font-family: var(--sans); font-size: 0.72rem; font-weight: 600;
    letter-spacing: 0.08em; text-transform: uppercase;
    overflow: hidden; align-self: center;
  }
  .langsw a { padding: 0.32rem 0.6rem; text-decoration: none; color: var(--ink); }
  .langsw a[aria-current="true"] { background: var(--accent); }
  .langsw a:not([aria-current="true"]):hover { background: var(--mark-soft); }
  .pub { align-items: center; }
  .pub-right { display: flex; align-items: center; gap: 1.1rem; flex-wrap: wrap; }
"""

def switcher(active, home):
    en = ' aria-current="true"' if active == "en" else ""
    ms = ' aria-current="true"' if active == "ms" else ""
    return (f'<span class="langsw"><a href="{home}"{en} lang="en" hreflang="en">EN</a>'
            f'<a href="{home}ms/" {ms} lang="ms" hreflang="ms">BM</a></span>')

def with_toggle(body, active):
    old = '<p class="tag">An ongoing record · Kuala Lumpur</p>'
    if old not in body:
        import re as _re
        m = _re.search(r'<p class="tag">.*?</p>', body, _re.S)
        old = m.group(0) if m else None
    if not old:
        return body
    return body.replace(old, f'<div class="pub-right">{old}{switcher(active, "/")}</div>', 1)

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
    "quarantine at KLIA - under a rule issued after they arrived."
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

title_tag = re.sub(r"Over \d+\+? Days", f"Over {DAYS} Days", src[t0:t1])
body = src[t1:].lstrip()


# ── blog (needed before the homepage teaser is injected) ──────────────
posts = blogmod.load_all()
n = blogpages.build(posts)
print(f"  blog: {n} post(s)")

if posts:
    cards = "".join(
        f'''      <a class="dcard" href="/blog/{q["slug"]}/">
        {'<span class="dcard-img"><img src="' + q["hero"] + '" alt=""></span>' if q.get("hero") else ''}
        <span class="dcard-d">{q["pretty"]}</span>
        <span class="dcard-t">{_html.escape(q["title"])}</span>
        <span class="dcard-s">{_html.escape(q["summary"])}</span>
        <span class="dcard-go">Read the dispatch →</span>
      </a>\n'''
        for q in posts[:3]
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
    body = body.replace('  <div class="note">', DISPATCHES + '\n  <div class="note">', 1)

# ── translate, then add the language switch to each edition ───────────
ms_body, done, missing = i18n.translate(body, i18n.load_ms())
i18n.report(done, missing)

# stamped after translation, so editing a number never changes an i18n hash
en_body = stamp_counts(with_toggle(body, "en"))
ms_body = stamp_counts(with_toggle(ms_body, "ms"))

MS_TITLE = "Selamatkan Kucing Kami - Ditahan di Kuarantin KLIA - saveourcats.my"
MS_DESC = ("Orion dan Nova masuk ke Malaysia secara sah dengan dokumen dan bayaran lengkap. "
           "Tarikh pelepasan disahkan 30 Julai. Mereka masih ditahan di Stesen Kuarantin Haiwan "
           "KLIA, di bawah peraturan yang dikeluarkan dua belas hari selepas mereka tiba.")

ALT = ('<link rel="alternate" hreflang="en" href="https://saveourcats.my/">\n'
       '<link rel="alternate" hreflang="ms" href="https://saveourcats.my/ms/">\n'
       '<link rel="alternate" hreflang="x-default" href="https://saveourcats.my/">')

JSONLD = """<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"NewsArticle",
"headline":"{t}","description":"{d}",
"image":["https://saveourcats.my/og-image.jpg"],
"datePublished":"2026-08-12T00:00:00+08:00","dateModified":"{today}T00:00:00+08:00",
"inLanguage":"{lang}","isAccessibleForFree":true,
"author":{{"@type":"Person","name":"The owners of Orion and Nova"}},
"publisher":{{"@type":"Organization","name":"saveourcats.my","url":"https://saveourcats.my/",
"logo":{{"@type":"ImageObject","url":"https://saveourcats.my/img/logo.png"}}}},
"mainEntityOfPage":{{"@type":"WebPage","@id":"{url}"}},
"contentLocation":{{"@type":"Place","name":"KLIA Animal Quarantine Station",
"address":{{"@type":"PostalAddress","streetAddress":"Kompleks MAQIS KLIA, Jalan Pekeliling 4",
"addressLocality":"Sepang","addressRegion":"Selangor","postalCode":"64050","addressCountry":"MY"}}}},
"about":[{{"@type":"Thing","name":"Animal quarantine"}},
{{"@type":"GovernmentOrganization","name":"Malaysian Quarantine and Inspection Services Department (MAQIS)"}}]}}
</script>"""


def page(lang, title, desc, canonical, body_html):
    pre = "" if lang == "en" else ".."
    ld = JSONLD.format(t=_html.escape(title, quote=True), d=_html.escape(desc, quote=True),
                       today=TODAY, lang=lang, url=canonical)
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_html.escape(title)}</title>
<meta name="description" content="{_html.escape(desc, quote=True)}">
<link rel="canonical" href="{canonical}">
{ALT}
<meta property="og:type" content="article">
<meta property="og:site_name" content="saveourcats.my">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{_html.escape(title, quote=True)}">
<meta property="og:description" content="{_html.escape(desc, quote=True)}">
<meta property="og:locale" content="{'en_GB' if lang == 'en' else 'ms_MY'}">
<meta property="og:image" content="https://saveourcats.my/og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{_html.escape(title, quote=True)}">
<meta name="twitter:description" content="{_html.escape(desc, quote=True)}">
<meta name="twitter:image" content="https://saveourcats.my/og-image.jpg">
<meta name="theme-color" content="#FBFAF8">
<link rel="icon" href="/img/favicon.png" sizes="64x64">
<link rel="apple-touch-icon" href="/img/apple-touch-icon.png">
<link rel="preload" as="font" type="font/woff2" href="/fonts/museum-light.woff2" crossorigin>
<link rel="preload" as="font" type="font/woff2" href="/fonts/montreal-regular.woff2" crossorigin>
<style>
  *, *::before, *::after {{ box-sizing: border-box; }}
  html {{ color-scheme: light; }}
  body {{ margin: 0; }}
  img {{ max-width: 100%; height: auto; display: block; }}
</style>
<style>{BLOG_CSS}{LANG_CSS}</style>
{ld}
</head>
<body>
{body_html}
</body>
</html>
"""


EN_TITLE = re.sub(r"</?title>", "", title_tag)

# the artifact inlines assets, so it needs the relative URLs - build it first
(ROOT / "artifact.html").write_text(title_tag + "\n\n" + inline_assets(en_body))

(ROOT / "index.html").write_text(
    page("en", EN_TITLE, DESC, "https://saveourcats.my/", rooted(en_body)))

msdir = ROOT / "ms"
msdir.mkdir(exist_ok=True)
(msdir / "index.html").write_text(
    page("ms", MS_TITLE, MS_DESC, "https://saveourcats.my/ms/", rooted(ms_body)))

print(f"  index.html     {(ROOT / 'index.html').stat().st_size:,} bytes  (en)")
print(f"  ms/index.html  {(msdir / 'index.html').stat().st_size:,} bytes  (ms)")
print(f"  artifact.html  {(ROOT / 'artifact.html').stat().st_size:,} bytes")

# ── sitemap ───────────────────────────────────────────────────────────
urls = [("https://saveourcats.my/", "daily", "1.0"),
        ("https://saveourcats.my/ms/", "daily", "0.9")]
if posts:
    urls.append(("https://saveourcats.my/blog/", "daily", "0.8"))
    urls += [(f"https://saveourcats.my/blog/{q['slug']}/", "monthly", "0.7") for q in posts]

IMAGES = """    <image:image>
      <image:loc>https://saveourcats.my/og-image.jpg</image:loc>
      <image:title>Orion and Nova</image:title>
      <image:caption>Two cats held at the KLIA Animal Quarantine Station beyond their confirmed release date.</image:caption>
    </image:image>
    <image:image>
      <image:loc>https://saveourcats.my/img/before-the-flight.jpg</image:loc>
      <image:caption>Orion and Nova the night before their flight to Malaysia, 10 July 2026.</image:caption>
    </image:image>
"""

sm = ['<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
      '        xmlns:xhtml="http://www.w3.org/1999/xhtml"',
      '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
for i, (loc, freq, pri) in enumerate(urls):
    links = ""
    if loc in ("https://saveourcats.my/", "https://saveourcats.my/ms/"):
        links = ('    <xhtml:link rel="alternate" hreflang="en" href="https://saveourcats.my/"/>\n'
                 '    <xhtml:link rel="alternate" hreflang="ms" href="https://saveourcats.my/ms/"/>\n')
    sm.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{TODAY}</lastmod>\n"
              f"    <changefreq>{freq}</changefreq>\n    <priority>{pri}</priority>\n"
              f"{links}{IMAGES if i == 0 else ''}  </url>")
sm.append("</urlset>")
(ROOT / "sitemap.xml").write_text("\n".join(sm) + "\n")
print(f"  sitemap: {len(urls)} URL(s), with hreflang pairs")
