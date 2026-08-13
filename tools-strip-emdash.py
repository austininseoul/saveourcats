#!/usr/bin/env python3
"""Replace every em dash in the site copy with a plain hyphen.

    python3 tools-strip-emdash.py

Every translatable English element is keyed in src/ms.json by a hash of its own
inner HTML, so editing the English would orphan its Malay. This reads the keys
first, rewrites the English, reads the keys again, and moves each translation
onto its new key by position; the element order cannot change, because the edit
is a pure character substitution.

En dashes are left alone: they mark numeric ranges (5–10 days, 11am–5pm).
"""
import json
import pathlib
import re

import i18n

ROOT = pathlib.Path(__file__).parent
PAGE = ROOT / "src" / "page.html"
MS = ROOT / "src" / "ms.json"
POSTS = sorted((ROOT / "posts").glob("*.md"))

# the bare character, not the spaced form: several sit at the end of a wrapped
# line, with a space before and a newline after, and a spaced pattern walks
# straight past those
EM = "—"
PLAIN = "-"


def keys_of(html: str) -> list[str]:
    return [i18n.key(inner) for _, inner in i18n.elements(html)]


before = PAGE.read_text()
old_keys = keys_of(before)

after = before.replace(EM, PLAIN)
new_keys = keys_of(after)

if len(old_keys) != len(new_keys):
    raise SystemExit(f"element count changed: {len(old_keys)} -> {len(new_keys)}")

PAGE.write_text(after)
print(f"  src/page.html   {before.count(EM)} em dashes replaced")

ms = json.loads(MS.read_text())
remap = dict(zip(old_keys, new_keys))
moved = kept = dropped = 0
out = {}
for k, v in ms.items():
    if k in remap:
        out[remap[k]] = v.replace(EM, PLAIN)
        moved += remap[k] != k
    else:
        out[k] = v.replace(EM, PLAIN)
        dropped += 1
    kept += 1
MS.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
print(f"  src/ms.json     {kept} strings, {moved} re-keyed, {dropped} not found in the page")

for p in POSTS:
    t = p.read_text()
    n = t.count(EM)
    if n:
        p.write_text(t.replace(EM, PLAIN))
        print(f"  {p.name:<46} {n} replaced")

# the share cards, the build scripts and the repo docs. Box-drawing rules in
# the section comments are U+2500, a different character, and are left alone.
REST = [ROOT / "src" / "cards.html", ROOT / "build.py", ROOT / "blogpages.py",
        ROOT / "blog.py", ROOT / "i18n.py", ROOT / "README.md",
        ROOT / "img" / "CREDITS.md"]
for f in REST:
    if not f.exists():
        continue
    t = f.read_text()
    n = t.count(EM)
    if n:
        f.write_text(t.replace(EM, PLAIN))
        print(f"  {f.name:<46} {n} replaced")
