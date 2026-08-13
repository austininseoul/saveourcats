#!/usr/bin/env python3
"""
Bilingual build for saveourcats.my - English at /, Malay at /ms/.

How it works
------------
Every translatable element in src/page.html is identified by a short hash of its
own inner HTML. src/ms.json maps those hashes to Malay. The Malay page is the
English page with matching elements swapped.

The consequence worth understanding: **if you edit an English sentence, its hash
changes and its translation is reported missing.** That is deliberate - it means
a stale Malay translation can never silently survive an English edit. Run the
build, read the coverage report, update src/ms.json.

Untranslated strings fall back to English rather than breaking the page.
"""
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
MS_FILE = ROOT / "src" / "ms.json"

# Elements whose text is prose worth translating.
TAGS = r"(p|h1|h2|h3|blockquote|figcaption|li|dd|dt)"

# Never translate: addresses, phone numbers, references, the wordmark.
SKIP = re.compile(
    r"^(?:\s*(?:[\w.+-]+@[\w.-]+"          # emails
    r"|(?:https?://|www\.)\S+"             # urls
    r"|[\d\s.·-–\-|,:+()]+"                # pure numbers/punctuation
    r"|saveourcats.*"                      # the wordmark
    r"|\d{2}-\d{4}\s?\d{4}.*"              # phone numbers
    r")\s*)$",
    re.I,
)


def key(inner: str) -> str:
    norm = re.sub(r"\s+", " ", inner).strip()
    return hashlib.sha1(norm.encode()).hexdigest()[:10]


def elements(html: str):
    """Yield (match, inner) for each translatable leaf element."""
    for m in re.finditer(rf"<{TAGS}(\s[^>]*)?>(.*?)</\1>", html, re.S):
        inner = m.group(3)
        stripped = re.sub(r"<[^>]+>", "", inner).strip()
        if not stripped or len(stripped) < 4:
            continue
        if SKIP.match(stripped):
            continue
        if re.search(rf"<{TAGS}[\s>]", inner):    # container, not a leaf
            continue
        yield m, inner


def load_ms() -> dict:
    if MS_FILE.exists():
        return json.loads(MS_FILE.read_text())
    return {}


def translate(html: str, ms: dict):
    """Return (malay_html, translated_count, missing_list)."""
    missing, done = [], 0
    out, last = [], 0

    for m, inner in elements(html):
        k = key(inner)
        if k in ms and ms[k].strip():
            out.append(html[last:m.start(3)])
            out.append(ms[k])
            last = m.end(3)
            done += 1
        else:
            missing.append((k, re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", inner)).strip()))
    out.append(html[last:])
    return "".join(out), done, missing


def report(done: int, missing: list) -> None:
    total = done + len(missing)
    pct = (done / total * 100) if total else 100
    print(f"  i18n: {done}/{total} strings translated ({pct:.0f}%)")
    if missing:
        print(f"  ── {len(missing)} awaiting Malay (falling back to English):")
        for k, txt in missing[:12]:
            print(f'     "{k}": {txt[:74]}')
        if len(missing) > 12:
            print(f"     … and {len(missing) - 12} more")
        stub = {k: "" for k, _ in missing}
        (ROOT / "src" / "ms.todo.json").write_text(
            json.dumps(stub, indent=1, ensure_ascii=False)
        )
        print("     stub written to src/ms.todo.json")
