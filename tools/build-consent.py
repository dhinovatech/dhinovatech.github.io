#!/usr/bin/env python3
"""
Put Google Analytics behind Consent Mode v2 on every page.

Before this, gtag.js fired unconditionally on 167 pages while the site
publishes in German, French, Italian, Dutch, Polish, Spanish and more - i.e.
it set analytics cookies for EU readers with no legal basis. This script:

  * replaces the hand-written gtag snippet with a generated block that arms
    Consent Mode v2 BEFORE gtag.js can run, and re-applies a previously
    stored answer
  * scopes that default by region: denied in the EEA, UK and Switzerland,
    where the notice is a gate; granted elsewhere, where it is an opt-out.
    Google resolves the region from the request, so the pages never look up
    or store a location - see DENIED_REGIONS below
  * injects the banner itself, in the page's own language where we have
    checked copy for it (tools/consent-strings.json) and in English otherwise
  * covers 404.html and glowcompare/privacy.html too, which had no analytics
    at all - a 404 page with no analytics means no way to see which URLs are
    breaking

Ordering is the whole point: consent defaults are set in <head>, the banner is
drawn at the end of <body>. If the banner script never runs, the defaults are
what stands - which in the EEA means consent is simply never granted.

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
SKIP_FILES = {"landing.html", "ads.html"}
STRINGS = os.path.join(ROOT, "tools", "consent-strings.json")

GA_ID = "G-T0S5ZW1QGM"

# Google Ads. Conversion tracking for the campaigns that point at the app
# pages. It is configured through the same gtag.js instance and the same
# Consent Mode defaults as Analytics - loading the second snippet Google's
# setup page hands you would pull in a second copy of gtag.js and, far worse,
# would run it before the consent defaults below are armed.
ADS_ID = "AW-18122344867"

# Microsoft Advertising UET. Same role as ADS_ID, for the Bing/Microsoft side
# of the campaigns. UET keeps its own consent state rather than reading
# Google's, so the denied default has to be pushed onto the uetq queue
# separately - and before the tag script is inserted, because the tag reads
# the queue as it initialises.
UET_ID = "97267869"

HEAD_BEGIN = "  <!-- BEGIN generated analytics + consent block -->"
HEAD_END = "  <!-- END generated analytics + consent block -->"
BAR_BEGIN = "<!-- BEGIN generated consent banner -->"
BAR_END = "<!-- END generated consent banner -->"

with io.open(STRINGS, encoding="utf-8") as _fh:
    L = json.load(_fh)

# EEA + UK + Switzerland, as ISO 3166-2 codes. Consent Mode has no shorthand
# for the bloc - 'EEA' is not a value it accepts - so the 27 member states are
# spelled out, then IS/LI/NO to complete the EEA, then GB and CH.
DENIED_REGIONS = [
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR",
    "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL",
    "PL", "PT", "RO", "SK", "SI", "ES", "SE",
    "IS", "LI", "NO",
    "GB", "CH",
]


def _region_js(codes, per_row=10, indent=" " * 8):
    """The region array, wrapped so the generated <head> stays readable."""
    rows = [", ".join("'%s'" % c for c in codes[i:i + per_row])
            for i in range(0, len(codes), per_row)]
    return (",\n" + indent).join(rows)


NOTICE = "2026-09-09b"

HEAD_BLOCK = """%s
  <!-- Google tag (gtag.js), gated by Consent Mode v2. -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=%s"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}

    /* Which version of the consent notice this page is showing.
       assets/js/consent.js draws the banner again when a reader's stored
       answer was given against an older one, and the block further down
       refuses to read an older acceptance as consent to advertising. It is
       declared here rather than in consent.js because the head block needs it
       before consent.js has loaded, and one value beats two that can drift. */
    window.DHIN_NOTICE = '%s';

    /* Two defaults. Order between them does not matter: Consent Mode applies
       the most specific region match, and the call without a region key is the
       catch-all for everyone the first one does not name.

       Google resolves which one applies on its own side, from the request.
       Nothing here reads, derives or stores a location, and the page itself
       never learns where the reader is - which is why the banner below is
       drawn for everyone rather than being hidden by region.

       EEA/UK/CH: everything denied until the reader accepts. This runs before
       gtag.js has loaded, so there is no window in which anything is granted
       by default, and it holds even if the banner script never runs at all.
       wait_for_update gives a returning reader's stored answer time to land
       before the first hit is sent. */
    gtag('consent', 'default', {
      'ad_storage': 'denied',
      'ad_user_data': 'denied',
      'ad_personalization': 'denied',
      'analytics_storage': 'denied',
      'functionality_storage': 'granted',
      'security_storage': 'granted',
      'region': [
        %s
      ],
      'wait_for_update': 500
    });
    /* Everywhere else the notice is an opt-out rather than a gate, and that
       now covers ad measurement as well as analytics. Section 2 of
       /privacy.html says so in as many words.

       ad_personalization stays denied in every region, accepted or not. It is
       the one that builds remarketing audiences and personalises ads, and
       none of the campaigns need it: what they need is to know whether a
       click became a visit to a store listing, which is ad_storage and
       ad_user_data. Denying the third costs nothing and is the difference
       between measuring an ad and profiling a reader. */
    gtag('consent', 'default', {
      'ad_storage': 'granted',
      'ad_user_data': 'granted',
      'ad_personalization': 'denied',
      'analytics_storage': 'granted',
      'functionality_storage': 'granted',
      'security_storage': 'granted'
    });
    /* A stored answer overrides the default in either direction. 'denied' has
       to be re-applied and not just skipped: a reader outside the EEA who
       declined would otherwise be granted again by the catch-all on their
       next visit.

       An acceptance only reaches advertising if it was given against the
       notice currently on the page. Readers who accepted the previous one
       agreed to analytics at a time when the notice promised no advertising
       cookie was set; treating that as agreement to advertising would be
       helping ourselves to consent that was never given. They keep analytics
       and are asked again. A refusal carries in full either way - nobody who
       declined meant "except for ads". */
    (function () {
      try {
        var answered = localStorage.getItem('dhin-consent');
        if (answered !== 'granted' && answered !== 'denied') return;
        var update = {'analytics_storage': answered};
        if (answered === 'denied') {
          update.ad_storage = 'denied';
          update.ad_user_data = 'denied';
        } else if (localStorage.getItem('dhin-consent-notice') === window.DHIN_NOTICE) {
          update.ad_storage = 'granted';
          update.ad_user_data = 'granted';
        }
        gtag('consent', 'update', update);
      } catch (e) { /* storage blocked - the defaults above stand */ }
    })();
    gtag('js', new Date());
    gtag('config', '%s');
    gtag('config', '%s');
  </script>
  <!-- Microsoft Advertising UET. -->
  <script>
    /* UET reads window.uetq as it initialises, so the default is queued
       before the tag is inserted, exactly as the gtag defaults above are
       armed before gtag.js loads.

       Denied here for everyone, in every region, which is stricter than the
       Google side above - not by preference but because UET has no region
       parameter. Google resolves the reader's region on its own side, so a
       default can be scoped to the EEA; Microsoft's consent call takes
       ad_storage and nothing else, and this site deliberately never works out
       where anyone is. Denying by default everywhere and granting on
       acceptance is the only version of that which is correct in the EEA, so
       it is the version everyone gets.

       Microsoft's own guidance is that the tag must load before the reader
       answers, with the default denied, and be updated to granted once they
       accept - which is what the block below does on a return visit and
       consent.js does on the click itself. */
    window.uetq = window.uetq || [];
    window.uetq.push('consent', 'default', {'ad_storage': 'denied'});
    (function () {
      try {
        if (localStorage.getItem('dhin-consent') === 'granted' &&
            localStorage.getItem('dhin-consent-notice') === window.DHIN_NOTICE) {
          window.uetq.push('consent', 'update', {'ad_storage': 'granted'});
        }
      } catch (e) { /* storage blocked - denied stands */ }
    })();
  </script>
  <script>(function(w, d, t, u, o) {w[u] = w[u] || [], o.ts = (new Date).getTime();var n = d.createElement(t);n.src = "https://bat.bing.net/bat.js?ti=" + o.ti + ("uetq" != u ? "&q=" + u : ""),n.async = 1, n.onload = n.onreadystatechange = function() {var s = this.readyState;s && "loaded" !== s && "complete" !== s ||(o.q = w[u], w[u] = new UET(o), w[u].push("pageLoad"),n.onload = n.onreadystatechange = null)};var i = d.getElementsByTagName(t)[0];i.parentNode.insertBefore(n, i);})(window, document, "script", "uetq", {ti:"%s",enableAutoSpaTracking: true});</script>
%s""" % (HEAD_BEGIN, GA_ID, NOTICE, _region_js(DENIED_REGIONS), GA_ID, ADS_ID,
         UET_ID, HEAD_END)

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
            if fn.endswith(".html") and fn not in SKIP_FILES:
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
            for attempt in range(5):
                try:
                    with io.open(path, "w", encoding="utf-8", newline="") as fh:
                        fh.write(doc)
                    break
                except OSError:
                    if attempt == 4:
                        raise
                    import time
                    time.sleep(0.15)

    print("consent head block : %d pages (%d gained analytics they lacked)"
          % (n_head, n_new))
    print("consent banner     : %d pages" % n_bar)
    print("translated copy    : %d locales, rest fall back to English"
          % len(translated))
    return 0


if __name__ == "__main__":
    sys.exit(main())
