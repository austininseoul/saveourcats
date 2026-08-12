#!/usr/bin/env python3
"""Renders the blog archive and per-post pages. Imported by build.py."""
import datetime
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
TODAY = datetime.date.today().isoformat()

# The post pages reuse the article's own stylesheet, lifted straight out of
# src/page.html so the two can never drift apart.
def site_css() -> str:
    src = (ROOT / "src" / "page.html").read_text()
    blocks = re.findall(r"<style>(.*?)</style>", src, re.S)
    return "\n".join(blocks)


EXTRA = """
  /* ── blog ── */
  .bl-back {
    display: inline-block; margin: 0 0 1.6rem;
    font-family: var(--sans); font-size: 0.82rem; font-weight: 600;
    letter-spacing: 0.05em; text-transform: uppercase;
    color: var(--alarm); text-decoration: none;
    border-bottom: 2px solid var(--accent); padding-bottom: 2px;
  }
  .bl-head { padding: clamp(1.5rem, 4vw, 2.5rem) 0 0; }
  .bl-date {
    font-family: var(--sans); font-size: 0.78rem; font-weight: 600;
    letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--ink-faint); margin: 0 0 0.7rem;
  }
  .bl-title {
    font-family: var(--serif); font-weight: 400;
    font-size: clamp(1.9rem, 4.6vw, 3.1rem);
    line-height: 1.06; letter-spacing: -0.018em;
    margin: 0; max-width: 24ch; text-wrap: balance;
  }
  .bl-sum {
    font-family: var(--sans); font-size: clamp(1rem, 2vw, 1.15rem);
    line-height: 1.5; color: var(--ink-soft);
    margin: 1.1rem 0 0; max-width: 46ch;
  }
  .bl-rule { border: 0; border-top: 2px solid var(--ink); margin: 1.8rem 0 0; }

  .bl-body { padding: 1.8rem 0 0; max-width: 36rem; }
  .bl-body p { margin: 0 0 1.3rem; }
  .bl-body h2 {
    font-family: var(--sans); font-weight: 600;
    font-size: clamp(1.08rem, 2.1vw, 1.3rem);
    margin: 2.5rem 0 0.9rem; max-width: 32ch;
  }
  .bl-body h3 { font-family: var(--sans); font-weight: 600; font-size: 1rem; margin: 2rem 0 0.7rem; }
  .bl-body blockquote {
    margin: 1.8rem 0; padding: 0 0 0 1.4rem;
    border-left: 5px solid var(--accent);
    font-family: var(--serif); font-size: clamp(1.15rem, 2.4vw, 1.4rem);
    line-height: 1.32; max-width: 30ch;
  }
  .bl-body blockquote p { margin: 0; }
  .bl-body ul, .bl-body ol { margin: 0 0 1.3rem; padding-left: 1.3rem; }
  .bl-body li { margin-bottom: 0.5rem; }
  .bl-body hr { border: 0; border-top: 1px solid var(--rule); margin: 2.2rem 0; }
  .bl-body a { color: var(--alarm); }
  .bl-body img { border: 1px solid var(--rule); margin: 1.8rem 0; }

  /* archive list */
  .bl-list { list-style: none; margin: 2rem 0 0; padding: 0; }
  .bl-list li { border-top: 1px solid var(--rule); }
  .bl-list li:last-child { border-bottom: 1px solid var(--rule); }
  .bl-list a {
    display: block; padding: 1.5rem 0; text-decoration: none; color: inherit;
  }
  .bl-list a:hover .bl-list-t, .bl-list a:focus-visible .bl-list-t {
    background: var(--mark-soft);
    box-shadow: 0 0 0 4px var(--mark-soft);
  }
  .bl-list-d {
    font-family: var(--sans); font-size: 0.75rem; font-weight: 600;
    letter-spacing: 0.12em; text-transform: uppercase; color: var(--ink-faint);
  }
  .bl-list-t {
    font-family: var(--serif); font-weight: 400;
    font-size: clamp(1.25rem, 2.8vw, 1.62rem);
    line-height: 1.2; letter-spacing: -0.012em;
    margin: 0.35rem 0 0; max-width: 28ch;
  }
  .bl-list-s {
    font-family: var(--sans); font-size: 0.93rem; line-height: 1.5;
    color: var(--ink-soft); margin: 0.5rem 0 0; max-width: 50ch;
  }

  /* homepage teaser */
  .dispatch-lead { font-family: var(--sans); font-size: 1.02rem; color: var(--ink-soft); max-width: 46ch; }
  .dispatch-more {
    display: inline-block; margin-top: 1.4rem;
    font-family: var(--sans); font-size: 0.86rem; font-weight: 600;
    letter-spacing: 0.05em; text-transform: uppercase;
    color: var(--alarm); text-decoration: none;
    border-bottom: 2px solid var(--accent); padding-bottom: 2px;
  }
"""


def head(title, desc, canonical, extra=""):
    t = html.escape(title, quote=True)
    d = html.escape(desc, quote=True)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="saveourcats.my">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:image" content="https://saveourcats.my/og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{d}">
<meta name="twitter:image" content="https://saveourcats.my/og-image.jpg">
<meta name="theme-color" content="#FBFAF8">
<link rel="icon" href="/img/favicon.png" sizes="64x64">
<link rel="apple-touch-icon" href="/img/apple-touch-icon.png">
<link rel="preload" as="font" type="font/woff2" href="/fonts/editorial-regular.woff2" crossorigin>
<link rel="preload" as="font" type="font/woff2" href="/fonts/montreal-regular.woff2" crossorigin>
<style>
  *, *::before, *::after {{ box-sizing: border-box; }}
  html {{ color-scheme: light; }}
  body {{ margin: 0; }}
  img {{ max-width: 100%; height: auto; display: block; }}
</style>
<style>
{site_css()}
{EXTRA}
</style>
{extra}
</head>
<body>
<div class="wrap">
  <div class="pub">
    <div class="brand">
      <img src="/img/logo.png" alt="" width="512" height="512">
      <p class="name"><a href="/" style="color:inherit;text-decoration:none">saveourcats<span>.my</span></a></p>
    </div>
    <p class="tag">An ongoing record · Kuala Lumpur</p>
  </div>
"""


FOOT = """
</div>
</body>
</html>
"""


def build(posts):
    """Write blog/index.html and blog/<slug>/index.html for every post."""
    blog = ROOT / "blog"
    blog.mkdir(exist_ok=True)

    # ── archive ──
    items = "".join(
        f"""    <li><a href="/blog/{p['slug']}/">
      <span class="bl-list-d">{p['pretty']}</span>
      <p class="bl-list-t">{html.escape(p['title'])}</p>
      <p class="bl-list-s">{html.escape(p['summary'])}</p>
    </a></li>\n"""
        for p in posts
    )
    (blog / "index.html").write_text(
        head("Dispatches — saveourcats.my",
             "A dated record of what happens each day while Orion and Nova remain held at the KLIA Animal Quarantine Station.",
             "https://saveourcats.my/blog/")
        + f"""
  <div class="bl-head">
    <a class="bl-back" href="/">← The full record</a>
    <p class="bl-date">Dispatches</p>
    <h1 class="bl-title">What happened, day by day.</h1>
    <p class="bl-sum">
      Every time we have relied on something being said rather than written, it has changed.
      So we are writing it down. {len(posts)} {'entry' if len(posts) == 1 else 'entries'}.
    </p>
    <hr class="bl-rule">
  </div>

  <ul class="bl-list">
{items}  </ul>
"""
        + FOOT
    )

    # ── one page per post ──
    for i, p in enumerate(posts):
        newer = posts[i - 1] if i > 0 else None
        older = posts[i + 1] if i + 1 < len(posts) else None
        nav = []
        if older:
            nav.append(f'<a class="dispatch-more" href="/blog/{older["slug"]}/">← {html.escape(older["pretty"])}</a>')
        if newer:
            nav.append(f'<a class="dispatch-more" href="/blog/{newer["slug"]}/">{html.escape(newer["pretty"])} →</a>')

        ld = f"""<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"BlogPosting",
"headline":{html.escape(p['title'])!r},
"description":{html.escape(p['summary'])!r},
"datePublished":"{p['iso']}T09:00:00+08:00",
"dateModified":"{TODAY}T00:00:00+08:00",
"image":["https://saveourcats.my/og-image.jpg"],
"author":{{"@type":"Person","name":"The owners of Orion and Nova"}},
"publisher":{{"@type":"Organization","name":"saveourcats.my","url":"https://saveourcats.my/"}},
"mainEntityOfPage":{{"@type":"WebPage","@id":"https://saveourcats.my/blog/{p['slug']}/"}},
"isPartOf":{{"@type":"Blog","name":"Dispatches","url":"https://saveourcats.my/blog/"}}}}
</script>""".replace("'", '"')

        d = blog / p["slug"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(
            head(f"{p['title']} — saveourcats.my", p["summary"],
                 f"https://saveourcats.my/blog/{p['slug']}/", ld)
            + f"""
  <article>
    <div class="bl-head">
      <a class="bl-back" href="/blog/">← Dispatches</a>
      <p class="bl-date">{p['pretty']}</p>
      <h1 class="bl-title">{html.escape(p['title'])}</h1>
      <p class="bl-sum">{html.escape(p['summary'])}</p>
      <hr class="bl-rule">
    </div>
    <div class="bl-body">
{p['html']}
    </div>
  </article>

  <div class="note">
    <p style="display:flex;gap:2rem;flex-wrap:wrap">{''.join(nav)}</p>
    <p>
      Every date, quotation and figure in these dispatches is drawn from dated correspondence,
      payment records and photographs held by the owners. Nothing is reconstructed from memory.
    </p>
  </div>
"""
            + FOOT
        )

    return len(posts)
