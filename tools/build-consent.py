#!/usr/bin/env python3
"""
Put Google Analytics behind Consent Mode v2 on every page.

Before this, gtag.js fired unconditionally on 167 pages while the site
publishes in German, French, Italian, Dutch, Polish, Spanish and more - i.e.
it set analytics cookies for EU readers with no legal basis. This script:

  * replaces the hand-written gtag snippet with a generated block that arms
    Consent Mode v2 with analytics_storage denied BEFORE gtag.js can run, and
    re-applies a previously stored answer
  * injects the banner itself, in the page's own language where we have
    checked copy for it (tools/consent-strings.json) and in English otherwise
  * covers 404.html and glowcompare/privacy.html too, which had no analytics
    at all - a 404 page with no analytics means no way to see which URLs are
    breaking

Ordering is the whole point: consent defaults are set in <head>, the banner is
drawn at the end of <body>. If the banner script never runs, consent is simply
never granted.

Run:  python tools/build-consent.py
Idempotent: both generated regions are delimited and replaced on each run.
"""
import html
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", "tools", "_src"}
STRINGS = os.path.join(ROOT, "tools", "consent-strings.json")

GA_ID = "G-T0S5ZW1QGM"

HEAD_BEGIN = "  <!-- BEGIN generated analytics + consent block -->"
HEAD_END = "  <!-- END generated analytics + consent block -->"
BAR_BEGIN = "<!-- BEGIN generated consent banner -->"
BAR_END = "<!-- END generated consent banner -->"

with io.open(STRINGS, encoding="utf-8") as _fh:
    L = json.load(_fh)

HEAD_BLOCK = """%s
  <!-- Google tag (gtag.js), gated by Consent Mode v2. -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=%s"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    /* Denied until the reader says otherwise. This runs before gtag.js has
       loaded, so there is no window in which analytics_storage is granted by
       default. wait_for_update gives a returning reader's stored answer time
       to be applied before the first hit is sent. */
    gtag('consent', 'default', {
      'ad_storage': 'denied',
      'ad_user_data': 'denied',
      'ad_personalization': 'denied',
      'analytics_storage': 'denied',
      'functionality_storage': 'granted',
      'security_storage': 'granted',
      'wait_for_update': 500
    });
    try {
      if (localStorage.getItem('dhin-consent') === 'granted') {
        gtag('consent', 'update', {'analytics_storage': 'granted'});
      }
    } catch (e) { /* storage blocked - stay denied */ }
    gtag('js', new Date());
    gtag('config', '%s');
  </script>
%s""" % (HEAD_BEGIN, GA_ID, GA_ID, HEAD_END)

# The exact snippet this replaces, as it appears on all 167 pages that had one.
OLD_GA = re.compile(
    r"[ \t]*<!-- Google tag \(gtag\.js\) -->\s*"
    r"<script async src=\"https://www\.googletagmanager\.com/gtag/js\?id=[^\"]+\"></script>\s*"
    r"<script>.*?gtag\('config',\s*'[^']+'\);\s*</script>\n?",
    re.S)

HEAD_RE = re.compile(re.escape(HEAD_BEGIN) + r".*?" + re.escape(HEAD_END) + r"\n?", re.S)
BAR_RE = re.compile(re.escape(BAR_BEGIN) + r".*?" + re.escape(BAR_END) + r"\n?", re.S)


def banner(code):
    t = L.get(code) or L["en"]
    return """%s
<div class="consent-bar" id="consentBar" role="region" aria-label="%s" hidden>
  <p class="consent-bar-text">%s <a href="/privacy.html" class="consent-bar-link">%s</a></p>
  <div class="consent-bar-actions">
    <button type="button" class="consent-btn consent-btn-ghost" data-consent="deny">%s</button>
    <button type="button" class="consent-btn consent-btn-solid" data-consent="allow">%s</button>
  </div>
</div>
<script src="/assets/js/consent.js"></script>
%s""" % (BAR_BEGIN, html.escape(t["aria"], quote=True), html.escape(t["body"]),
         html.escape(L.get(code, L["en"]).get("privacy", "Privacy Policy")),
         html.escape(t["decline"]), html.escape(t["accept"]), BAR_END)


def locale_of(rel):
    """Directory code for a page, e.g. glowcompare/de/index.html -> 'de'."""
    parts = rel.split("/")
    if len(parts) == 3 and parts[2] == "index.html" and len(parts[1]) <= 3:
        return parts[1]
    return "en"


def html_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in sorted(filenames):
            if fn.endswith(".html"):
                yield os.path.join(dirpath, fn)


def main():
    n_head = n_bar = n_new = 0
    translated = set()

    for path in html_files():
        rel = os.path.relpath(path, ROOT).replace("\\", "/")
        with io.open(path, encoding="utf-8") as fh:
            doc = fh.read()
        before = doc

        # ---- head: consent defaults + gtag ------------------------------
        # "Gained analytics" means the page had neither the old hand-written
        # snippet nor a block from a previous run - checked before either is
        # stripped, so a re-run reports 0 rather than counting them all again.
        had_ga = bool(HEAD_RE.search(doc)) or bool(OLD_GA.search(doc))
        doc = HEAD_RE.sub("", doc)
        doc = OLD_GA.sub("", doc)
        if "<head>" in doc:
            doc = doc.replace("<head>", "<head>\n" + HEAD_BLOCK, 1)
            n_head += 1
            if not had_ga:
                n_new += 1

        # ---- body: the banner -------------------------------------------
        code = locale_of(rel)
        if code in L:
            translated.add(code)
        doc = BAR_RE.sub("", doc)
        if "</body>" in doc:
            doc = doc.replace("</body>", banner(code) + "\n</body>", 1)
            n_bar += 1

        if doc != before:
            with io.open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(doc)

    print("consent head block : %d pages (%d gained analytics they lacked)"
          % (n_head, n_new))
    print("consent banner     : %d pages" % n_bar)
    print("translated copy    : %d locales, rest fall back to English"
          % len(translated))
    return 0


if __name__ == "__main__":
    sys.exit(main())
