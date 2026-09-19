#!/usr/bin/env python3
"""
Generate /stow/ - "Stow: AI Photo & File Organizer, Duplicate Finder", the Microsoft
Store (WinUI 3) file organizer, in 23 languages.

Like /glowcompare-windows/, this section keeps its own navigation: the language
switcher lists only the 23 Stow locales and every store CTA points at the
Microsoft Store listing. Store links are emitted as ordinary
https://apps.microsoft.com/detail/... URLs so they work on every platform and
stay crawlable; assets/js/ux.js upgrades them to ms-windows-store:// in place
when the visitor is actually on Windows.

The install bar / back-to-top / ux.js chrome at the end of the page is wrapped
in tools/build-ux.py's own BEGIN/END markers on purpose: that builder strips and
regenerates whatever sits between them, so running it after this script rewrites
that chrome (translating it) instead of appending a second copy of it.

Copy lives in tools/stow-strings.json (one block per locale).

Run:  python tools/build-stow.py
Idempotent: every page is rewritten from the strings file on each run.
"""
import html
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STRINGS = os.path.join(ROOT, "tools", "stow-strings.json")
CONSENT_STRINGS = os.path.join(ROOT, "tools", "consent-strings.json")

with open(STRINGS, encoding="utf-8") as _fh:
    L = json.load(_fh)

with open(CONSENT_STRINGS, encoding="utf-8") as _fh:
    CONSENT_L = json.load(_fh)

SECTION = "stow"

SITE = "https://www.dhinovatech.com"
STORE_ID = "9NHBR7SW2TZ0"
STORE = "https://apps.microsoft.com/detail/" + STORE_ID
STORE_UTM = STORE + "?ocid=dhinovatech_stow"

ICON = "/assets/images/stow-icon.png"

# The link-preview card. This used to be the 512x512 app icon under
# twitter:card=summary_large_image, which every scraper either letterboxes or
# drops; tools/build-stow-shots.py draws a real 1200x630 card instead.
OGIMG = "/assets/images/stow-og.png"
OGW, OGH = 1200, 630
OGALT = "Stow - photo and file organizer for Windows, on the Microsoft Store"

# Stow is a paid application with a trial, and the page has to say the same
# thing the store listing and the application itself say. The Offer below is
# the machine-readable half of that; t["price_badge"] / t["price_note"] are the
# half a reader sees, and both sit next to every primary call to action.
PRICE = "4.99"
PRICE_CCY = "USD"

# The localised screenshots tools/build-stow-shots.py writes, each paired with
# the already-translated string that best describes it. Reusing existing copy
# rather than inventing seven new captions is what keeps the gallery fully
# translated in all 23 languages on the day it ships.
#
# HERO is the dashboard, and it is deliberately not one of the six in the
# gallery: the heading over that grid says "six screens", and a reader who
# counts five of them, one of which they have already seen, has been given a
# reason to doubt everything else the page claims.
HERO = ("home", lambda t: t["pillars"][0]["features"][0]["title"])
SHOTS = [
    ("find",       "bi-search",            lambda t: t["find_items"][0]["t"]),
    ("space",      "bi-hdd",               lambda t: t["find_items"][2]["t"]),
    ("duplicates", "bi-copy",              lambda t: t["h_dupes"]),
    ("undo",       "bi-arrow-counterclockwise", lambda t: t["h_undo"]),
    ("photos",     "bi-image",             lambda t: t["find_items"][1]["t"]),
    ("privacy",    "bi-shield-lock",       lambda t: t["principles"][0]["t"]),
]
SHOT_W, SHOT_H = 1100, 619

GA_ID = "G-T0S5ZW1QGM"
HEAD_BEGIN = "  <!-- BEGIN generated analytics + consent block -->"
HEAD_END = "  <!-- END generated analytics + consent block -->"
BAR_BEGIN = "<!-- BEGIN generated consent banner -->"
BAR_END = "<!-- END generated consent banner -->"

DENIED_REGIONS = [
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR",
    "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL",
    "PL", "PT", "RO", "SK", "SI", "ES", "SE",
    "IS", "LI", "NO",
    "GB", "CH",
]

# code, menu label, dir, hreflang, og locale
LANGS = [
    ("en", "English", "ltr", "en", "en_US"),
    ("es", "Español (Spanish)", "ltr", "es", "es_ES"),
    ("fr", "Français (French)", "ltr", "fr", "fr_FR"),
    ("de", "Deutsch (German)", "ltr", "de", "de_DE"),
    ("it", "Italiano (Italian)", "ltr", "it", "it_IT"),
    ("pt", "Português (Portuguese)", "ltr", "pt", "pt_BR"),
    ("nl", "Nederlands (Dutch)", "ltr", "nl", "nl_NL"),
    ("pl", "Polski (Polish)", "ltr", "pl", "pl_PL"),
    ("cs", "Čeština (Czech)", "ltr", "cs", "cs_CZ"),
    ("hu", "Magyar (Hungarian)", "ltr", "hu", "hu_HU"),
    ("da", "Dansk (Danish)", "ltr", "da", "da_DK"),
    ("sv", "Svenska (Swedish)", "ltr", "sv", "sv_SE"),
    ("nb", "Norsk (Norwegian)", "ltr", "nb", "nb_NO"),
    ("fi", "Suomi (Finnish)", "ltr", "fi", "fi_FI"),
    ("ru", "Русский (Russian)", "ltr", "ru", "ru_RU"),
    ("uk", "Українська (Ukrainian)", "ltr", "uk", "uk_UA"),
    ("tr", "Türkçe (Turkish)", "ltr", "tr", "tr_TR"),
    ("ja", "日本語 (Japanese)", "ltr", "ja", "ja_JP"),
    ("ko", "한국어 (Korean)", "ltr", "ko", "ko_KR"),
    ("zh", "简体中文 (Simplified Chinese)", "ltr", "zh-Hans", "zh_CN"),
    ("th", "ไทย (Thai)", "ltr", "th", "th_TH"),
    ("ar", "العربية (Arabic)", "rtl", "ar", "ar_AR"),
    ("he", "עברית (Hebrew)", "rtl", "he", "he_IL"),
]

BY_CODE = {c: (c, label, d, hl, og) for c, label, d, hl, og in LANGS}
NLANG = len(LANGS)

E = html.escape

MODELS = [
    ("SigLIP-2 base patch16-224", "Apache-2.0", "365 MB"),
    ("YuNet", "MIT", "227 KB"),
    ("SFace", "Apache-2.0", "37 MB"),
    ("Phi-4-mini-instruct (INT4 CPU)", "MIT", "4.59 GB"),
]


def url_for(code):
    return "/%s/" % SECTION if code == "en" else "/%s/%s/" % (SECTION, code)


def abs_url(code):
    return SITE + url_for(code)


def shot_url(code, slug):
    """Path to one localised screenshot, falling back to the English capture.

    tools/build-stow-shots.py writes a full set per locale, but it only runs
    where the application repository is checked out. Everywhere else this has
    to resolve to a file that is actually committed, or a locale page ends up
    with six broken images.
    """
    rel = "assets/images/stow/%s/%s.webp" % (code, slug)
    if code != "en" and not os.path.exists(os.path.join(ROOT, rel)):
        rel = "assets/images/stow/en/%s.webp" % slug
    return "/" + rel


def built_langs():
    return [x for x in LANGS if x[0] in L]


def _region_js(codes, per_row=10, indent=" " * 8):
    rows = [", ".join("'%s'" % c for c in codes[i:i + per_row])
            for i in range(0, len(codes), per_row)]
    return (",\n" + indent).join(rows)


def analytics_block():
    return """%s
  <!-- Google tag (gtag.js), gated by Consent Mode v2. -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=%s"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
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
    gtag('consent', 'default', {
      'ad_storage': 'denied',
      'ad_user_data': 'denied',
      'ad_personalization': 'denied',
      'analytics_storage': 'granted',
      'functionality_storage': 'granted',
      'security_storage': 'granted'
    });
    (function () {
      try {
        var answered = localStorage.getItem('dhin-consent');
        if (answered === 'granted' || answered === 'denied') {
          gtag('consent', 'update', {'analytics_storage': answered});
        }
      } catch (e) { }
    })();
    gtag('js', new Date());
    gtag('config', '%s');
  </script>
%s""" % (HEAD_BEGIN, GA_ID, _region_js(DENIED_REGIONS), GA_ID, HEAD_END)


def consent_banner_html(code):
    c = CONSENT_L.get(code) or CONSENT_L["en"]
    return """%s
<div class="consent-bar" id="consentBar" role="region" aria-label="%s" hidden>
  <p class="consent-bar-text">%s <a href="/privacy.html" class="consent-bar-link">%s</a></p>
  <div class="consent-bar-actions">
    <button type="button" class="consent-btn consent-btn-ghost" data-consent="deny">%s</button>
    <button type="button" class="consent-btn consent-btn-solid" data-consent="allow">%s</button>
  </div>
</div>
<script src="/assets/js/consent.js"></script>
%s""" % (BAR_BEGIN, E(c["aria"]), E(c["body"]),
         E(CONSENT_L.get(code, CONSENT_L["en"]).get("privacy", "Privacy Policy")),
         E(c["decline"]), E(c["accept"]), BAR_END)


# --------------------------------------------------------------------------
# Shared navigation - Stow owns its own language tree.
# --------------------------------------------------------------------------

def lang_items(active, icon):
    out = []
    for code, label, _d, _hl, _og in built_langs():
        cls = "dropdown-item py-1 small"
        icon_cls = "bi %s text-primary me-2" % icon
        if code == active:
            cls += " active fw-bold"
            icon_cls = "bi %s me-2" % icon
        out.append(
            '<li><a class="%s" href="%s"%s><i class="%s" aria-hidden="true"></i>%s</a></li>'
            % (cls, url_for(code), ' aria-current="true"' if code == active else '',
               icon_cls, E(label))
        )
    return "".join(out)


def navbar(code, t):
    label = BY_CODE[code][1]
    store_cta = t.get("cta_store", "Get on Microsoft Store")
    return """  <nav class="navbar navbar-expand-lg navbar-dhin sticky-top py-3">
    <div class="container">
      <a class="navbar-brand d-flex align-items-center gap-2" href="/">
        <img src="/assets/images/LogoWithText.webp" alt="Dhinovatech" class="brand-logo-with-text-img" decoding="async" width="512" height="82">
      </a>
      <button class="navbar-toggler border-0 text-white" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <i class="bi bi-list fs-2" aria-hidden="true"></i>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto align-items-lg-center">
          <li class="nav-item">
            <a class="nav-link nav-link-custom" href="/">Home</a>
          </li>

          <!-- Our Apps - Stow owns its own language tree -->
          <li class="nav-item dropdown">
            <a class="nav-link nav-link-custom dropdown-toggle active" href="#" id="appsDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
              Our Apps
            </a>
            <ul class="dropdown-menu dropdown-menu-dark border-secondary shadow-lg mt-2" aria-labelledby="appsDropdown">
              <li><a class="dropdown-item py-2" href="/nudge/"><img src="/assets/images/nudge-icon.png" alt="Nudge Icon" style="width: 20px; height: 20px; border-radius: 5px; object-fit: cover;" class="me-2" decoding="async">Nudge Offline Journal</a></li>
              <li class="dropdown-submenu position-relative">
                <a class="dropdown-item py-2 d-flex align-items-center justify-content-between" href="/stow/">
                  <span><img src="__ICON__" alt="Stow Icon" style="width: 20px; height: 20px; border-radius: 5px; object-fit: cover;" class="me-2" decoding="async" width="256" height="256">Stow Photo &amp; File Organizer</span>
                  <span class="badge bg-primary-subtle text-primary border border-primary-subtle rounded-pill ms-2 extra-small submenu-toggle-btn" role="button" title="View __N__ Languages">__N__ Languages <i class="bi bi-chevron-down ms-1" aria-hidden="true"></i></span>
                </a>
                <ul class="dropdown-menu dropdown-menu-dark border-secondary shadow-lg scrollable-menu" style="max-height: 360px; overflow-y: auto;">
                  __LANG_SUBMENU__
                </ul>
              </li>
              <li><a class="dropdown-item py-2" href="/glowcompare-windows/"><i class="bi bi-microsoft text-primary me-2" aria-hidden="true"></i>GlowCompare for Windows</a></li>
              <li><a class="dropdown-item py-2" href="/glowcompare/"><i class="bi bi-google-play text-danger me-2" aria-hidden="true"></i>GlowCompare for Android</a></li>
              <li><hr class="dropdown-divider"></li>
              <li><a class="dropdown-item py-2" href="/slouch-guard/"><i class="bi bi-person-workspace text-info me-2" aria-hidden="true"></i>Slouch Guard</a></li>
              <li><a class="dropdown-item py-2" href="/notelock/"><i class="bi bi-shield-lock text-warning me-2" aria-hidden="true"></i>Notelock Secure Notes</a></li>
              <li><a class="dropdown-item py-2" href="/milk-monthly-expense-calendar/"><i class="bi bi-calendar2-check text-success me-2" aria-hidden="true"></i>Milk Monthly Expense Calendar</a></li>
              <li><a class="dropdown-item py-2" href="/mortgage-loan-emi-pro/"><i class="bi bi-calculator text-primary me-2" aria-hidden="true"></i>Mortgage EMI Pro</a></li>
              <li><a class="dropdown-item py-2" href="/aes-vault/"><i class="bi bi-safe2 text-danger me-2" aria-hidden="true"></i>AES Vault Encryption</a></li>
            </ul>
          </li>

          <li class="nav-item">
            <a class="nav-link nav-link-custom" href="/about.html">About Us</a>
          </li>
          <li class="nav-item">
            <a class="nav-link nav-link-custom" href="/contact.html">Contact Us</a>
          </li>

          <!-- Language Selector - Stow only -->
          <li class="nav-item dropdown ms-lg-2 mt-2 mt-lg-0">
            <button class="btn btn-outline-primary dropdown-toggle fw-semibold px-3 py-2 rounded-3 shadow d-flex align-items-center gap-2" type="button" id="langSelector" data-bs-toggle="dropdown" aria-expanded="false">
              <i class="bi bi-translate fs-5" aria-hidden="true"></i> <span>__LANG_LABEL__</span>
            </button>
            <ul class="dropdown-menu dropdown-menu-dark dropdown-menu-end border-secondary shadow-lg mt-2 scrollable-menu" style="max-height: 380px; overflow-y: auto;" aria-labelledby="langSelector">
              __LANG_SELECTOR__
            </ul>
          </li>

          <!-- Microsoft Store CTA -->
          <li class="nav-item ms-lg-2 mt-3 mt-lg-0">
            <a href="__STORE__" target="_blank" rel="noopener" class="btn btn-primary fw-bold px-3 py-2 rounded-3 shadow d-flex align-items-center gap-2">
              <i class="bi bi-microsoft fs-5" aria-hidden="true"></i> __STORE_CTA__
            </a>
          </li>
        </ul>
      </div>
    </div>
  </nav>
""".replace("__LANG_SUBMENU__", lang_items(code, "bi-globe")) \
   .replace("__LANG_SELECTOR__", lang_items(code, "bi-translate")) \
   .replace("__LANG_LABEL__", E(label)) \
   .replace("__ICON__", ICON) \
   .replace("__N__", str(len(built_langs()))) \
   .replace("__STORE__", E(STORE_UTM)) \
   .replace("__STORE_CTA__", E(store_cta))


FOOTER = """  <footer class="footer-dhin">
    <div class="container">
      <div class="row gy-4 mb-5">
        <div class="col-lg-4">
          <a class="d-flex align-items-center gap-2 mb-3" href="/">
            <img src="/assets/images/LogoWithText.webp" alt="Dhinovatech Logo" class="brand-logo-with-text-img" loading="lazy" decoding="async" width="512" height="82">
          </a>
          <p class="text-secondary small pe-lg-4">
            Dhinovatech designs and engineers high-performance, privacy-first mobile &amp; desktop apps available on Google Play and Microsoft Store.
          </p>
        </div>
        <div class="col-lg-2 col-6">
          <h4 class="h6 text-white fw-bold mb-3">Company</h4>
          <ul class="list-unstyled small d-flex flex-column gap-2 mb-0">
            <li><a href="/" class="footer-link">Home</a></li>
            <li><a href="/about.html" class="footer-link">About Us</a></li>
            <li><a href="/contact.html" class="footer-link">Contact Us</a></li>
          </ul>
        </div>
        <div class="col-lg-3 col-6">
          <h4 class="h6 text-white fw-bold mb-3">Our Applications</h4>
          <ul class="list-unstyled small d-flex flex-column gap-2 mb-0">
            <li><a href="/stow/" class="footer-link text-primary fw-semibold"><i class="bi bi-folder-symlink me-1" aria-hidden="true"></i> Stow Photo &amp; File Organizer</a></li>
            <li><a href="/glowcompare-windows/" class="footer-link"><i class="bi bi-microsoft text-primary me-1" aria-hidden="true"></i> GlowCompare for Windows</a></li>
            <li><a href="/glowcompare/" class="footer-link"><i class="bi bi-sparkles text-danger me-1" aria-hidden="true"></i> GlowCompare for Android</a></li>
            <li><a href="/slouch-guard/" class="footer-link"><i class="bi bi-person-workspace text-info me-1" aria-hidden="true"></i> Slouch Guard AI</a></li>
            <li><a href="/notelock/" class="footer-link"><i class="bi bi-shield-lock text-warning me-1" aria-hidden="true"></i> Notelock Secure Notes</a></li>
            <li><a href="/milk-monthly-expense-calendar/" class="footer-link"><i class="bi bi-calendar2-check text-success me-1" aria-hidden="true"></i> Milk Monthly Calendar</a></li>
            <li><a href="/mortgage-loan-emi-pro/" class="footer-link"><i class="bi bi-calculator text-primary me-1" aria-hidden="true"></i> Mortgage EMI Pro</a></li>
            <li><a href="/aes-vault/" class="footer-link"><i class="bi bi-safe2 text-danger me-1" aria-hidden="true"></i> AES Vault Encryption</a></li>
          </ul>
        </div>
        <div class="col-lg-3">
          <h4 class="h6 text-white fw-bold mb-3">Support &amp; Legal</h4>
          <p class="small text-secondary mb-2"><i class="bi bi-envelope-fill me-2 text-primary" aria-hidden="true"></i>dhinovatech@gmail.com</p>
          <p class="small text-secondary"><i class="bi bi-globe me-2 text-primary" aria-hidden="true"></i>www.dhinovatech.com</p>
        </div>
      </div>
      <div class="pt-4 border-top border-secondary text-center text-secondary small">
        <p class="mb-0">&copy; 2026 Dhinovatech. All rights reserved.</p>
      </div>
    </div>
  </footer>
"""

PAGE_CSS = """  <style>
    /* Stow is the one section that does not use the site's cyan accent.
       The application itself is a WinUI 3 window with an amber-gold accent on
       warm charcoal, and every screenshot on this page is a real capture of
       it - a cyan page wrapped around amber screenshots reads as two products
       rather than one. The four custom properties below are declared
       site-wide in custom.css, so re-declaring them here re-keys the shared
       chrome (buttons, focus rings, card hover, footer links) without a
       single !important and without touching any other section. */
    :root {
      --dhin-accent-blue: #ffb634;
      --dhin-border-glow: rgba(255, 182, 52, 0.32);
      --dhin-shadow-glow: 0 0 25px rgba(255, 182, 52, 0.22);
      --dhin-gradient-primary: linear-gradient(135deg, #ffb634 0%, #f0930d 100%);
      --stow-amber: #ffb634;
      --stow-ink: #1a1204;
    }
    :root, [data-bs-theme="dark"] {
      --bs-primary-rgb: 255, 182, 52;
      --bs-primary-bg-subtle: rgba(255, 182, 52, 0.12);
      --bs-primary-border-subtle: rgba(255, 182, 52, 0.32);
      --bs-primary-text-emphasis: #ffc861;
    }
    /* .text-gradient hardcodes the cyan ramp, so it needs its own override.
       The clip and fill have to be repeated: the `background` shorthand resets
       background-clip, and in custom.css the clip is declared after it. Set
       the ramp alone and every eyebrow on the page turns into a solid amber
       block with invisible text inside it. */
    .text-gradient {
      background: linear-gradient(135deg, #ffc861 0%, #ffb634 55%, #f0930d 100%);
      -webkit-background-clip: text;
      background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .btn-dhin-primary { box-shadow: 0 4px 15px rgba(255, 182, 52, 0.28); }
    .btn-dhin-primary:hover { box-shadow: 0 8px 25px rgba(255, 182, 52, 0.42); }
    .btn-dhin-outline:hover { background: rgba(255, 182, 52, 0.1); }
    .hero-section {
      padding: 56px 0 64px;
      background: radial-gradient(circle at 22% 18%, rgba(255, 182, 52, 0.14) 0%, rgba(8, 12, 20, 0) 62%);
    }
    @media (max-width: 991.98px) { .hero-section { padding: 32px 0 48px; } }

    .glow-aura-teal { box-shadow: 0 0 45px rgba(255, 182, 52, 0.26); }
    .stow-icon-box {
      width: 52px; height: 52px; border-radius: 14px;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.4rem; flex-shrink: 0;
      background: linear-gradient(135deg, rgba(255,182,52,0.18), rgba(240,147,13,0.12));
      color: var(--stow-amber); border: 1px solid rgba(255,182,52,0.3);
    }
    .stow-badge-row { display: flex; flex-wrap: wrap; gap: .5rem; }
    .stow-num {
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 1.6rem; font-weight: 700; line-height: 1;
      color: #64748b;
    }
    .stow-num-zero { color: #4ade80; }
    .plan-table {
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: .74rem; width: 100%; border-collapse: collapse;
    }
    .plan-table th, .plan-table td {
      padding: .45rem .6rem; border-bottom: 1px solid rgba(255,255,255,.07);
      white-space: nowrap; text-align: start;
    }
    .plan-table th { color: #94a3b8; font-weight: 600; }
    .plan-table td { color: #cbd5e1; }
    .plan-table .plan-dest { color: var(--stow-amber); }
    .plan-table .plan-rule { color: #64748b; }
    .plan-scroll { overflow-x: auto; }
    .stow-step {
      width: 42px; height: 42px; border-radius: 50%; flex-shrink: 0;
      display: flex; align-items: center; justify-content: center;
      font-weight: 800; font-size: 1.1rem;
      background: rgba(255,182,52,0.18); color: var(--stow-amber);
      border: 1px solid rgba(255,182,52,0.4);
    }
    .model-table td, .model-table th { vertical-align: middle; }

    /* Hero -------------------------------------------------------------- */
    .stow-hero-icon {
      width: 60px; height: 60px; border-radius: 15px; overflow: hidden;
      flex-shrink: 0; border: 1px solid rgba(255,255,255,.12);
      box-shadow: 0 10px 24px rgba(0,0,0,.45);
    }
    .stow-hero-icon img { width: 100%; height: 100%; object-fit: cover; display: block; }
    .stow-hero-name { font-size: 1.3rem; font-weight: 800; letter-spacing: -.01em; }
    .stow-price {
      display: flex; align-items: center; gap: .5rem; flex-wrap: wrap;
      font-size: .92rem; color: #cbd5e1;
    }
    .stow-price strong { color: #fff; }
    .stow-price-tag {
      background: rgba(255, 182, 52, .14); color: #ffc861;
      border: 1px solid rgba(255, 182, 52, .34);
      border-radius: 20px; padding: 2px 10px; font-size: .8rem; font-weight: 700;
      white-space: nowrap;
    }

    /* The hero screenshot. Border and shadow only - the capture supplies its
       own Windows chrome. */
    .stow-window {
      border-radius: 14px; overflow: hidden; background: #1f2021;
      border: 1px solid rgba(255,255,255,.12);
      box-shadow: 0 30px 70px -25px rgba(0,0,0,.9);
    }
    .stow-window img { display: block; width: 100%; height: auto; }

    /* Screenshot gallery ------------------------------------------------- */
    .stow-shot { overflow: hidden; margin: 0; }
    .stow-shot img {
      display: block; width: 100%; height: auto;
      border-bottom: 1px solid rgba(255,255,255,.07);
    }
    .stow-shot figcaption {
      padding: .85rem 1rem; font-size: .9rem; font-weight: 600; color: #e2e8f0;
    }
    .stow-shot figcaption i { color: var(--stow-amber); }

    /* Release banner ----------------------------------------------------- */
    .release-banner {
      background: linear-gradient(135deg, rgba(255, 182, 52, 0.1) 0%, rgba(240, 147, 13, 0.05) 100%);
      border: 1px solid rgba(255, 182, 52, 0.3);
      border-radius: 16px;
      position: relative;
      overflow: hidden;
    }
    .release-badge {
      background: linear-gradient(135deg, #ffb634 0%, #f0930d 100%);
      color: var(--stow-ink);
      font-weight: 800;
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      padding: 4px 12px;
      border-radius: 20px;
    }
    .release-feature-pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 14px;
      border-radius: 24px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      font-size: 0.85rem;
      color: #cbd5e1;
      text-decoration: none;
      transition: all 0.2s ease;
    }
    .release-feature-pill:hover {
      background: rgba(255, 182, 52, 0.15);
      border-color: rgba(255, 182, 52, 0.4);
      color: var(--stow-amber);
    }

    /* Invariant and Pillar Cards */
    .invariant-card {
      border-left: 3px solid var(--stow-amber) !important;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .invariant-card:hover {
      transform: translateY(-3px);
      box-shadow: 0 10px 30px rgba(255, 182, 52, 0.14);
    }
    .pillar-card {
      transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .pillar-card:hover {
      transform: translateY(-3px);
      border-color: rgba(255, 182, 52, 0.4) !important;
    }
    .feature-bullet-list li {
      position: relative;
      padding-left: 1.4rem;
      margin-bottom: 0.5rem;
      font-size: 0.88rem;
      color: #94a3b8;
    }
    .feature-bullet-list li::before {
      content: "•";
      position: absolute;
      left: 0.35rem;
      color: var(--stow-amber);
      font-size: 1.1rem;
      line-height: 1.2;
    }

    /* Comparison Table */
    .compare-table {
      font-size: 0.88rem;
      border-collapse: separate;
      border-spacing: 0;
    }
    .compare-table th, .compare-table td {
      padding: 0.9rem 1rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.07);
    }
    .compare-table thead th {
      background: rgba(17, 24, 39, 0.95);
      color: #94a3b8;
      font-weight: 600;
    }
    .compare-table th.stow-col, .compare-table td.stow-col {
      background: rgba(255, 182, 52, 0.06);
      border-left: 1px solid rgba(255, 182, 52, 0.25);
      border-right: 1px solid rgba(255, 182, 52, 0.25);
    }
    .compare-table thead th.stow-col {
      background: rgba(255, 182, 52, 0.14);
      color: var(--stow-amber);
      border-top: 2px solid var(--stow-amber);
    }

    /* FAQ accordion styling */
    .accordion-button:not(.collapsed) {
      background: rgba(255, 182, 52, 0.08);
      color: var(--stow-amber);
      box-shadow: none;
    }
    .accordion-button:focus {
      box-shadow: 0 0 0 0.2rem rgba(255, 182, 52, 0.25);
    }
    .accordion-button::after {
      filter: invert(1) grayscale(100%) brightness(200%);
    }

    /* The site honours reduced motion globally, but the hero art's float is
       introduced on this page, so it has to opt out on this page. */
    @media (prefers-reduced-motion: reduce) {
      .animated-float { animation: none !important; }
    }
  </style>
"""


def hreflang_block(code):
    rows = ['  <link rel="canonical" href="%s">' % abs_url(code),
            '  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">',
            '  <link rel="alternate" hreflang="x-default" href="%s">' % abs_url("en")]
    for c, _label, _d, hl, _og in built_langs():
        rows.append('  <link rel="alternate" hreflang="%s" href="%s">' % (hl, abs_url(c)))
    return "\n".join(rows)


def schema(code, t, desc):
    graph = [
        {"@type": "Organization", "@id": SITE + "/#organization",
         "name": "Dhinovatech", "url": SITE + "/"},
        {"@type": "SoftwareApplication",
         "@id": SITE + "/stow/#software",
         "name": t["name"],
         "operatingSystem": "Windows 10 version 2004 (build 19041) and later, x64 and ARM64",
         "applicationCategory": "UtilitiesApplication",
         "description": desc,
         "url": abs_url(code),
         "inLanguage": [hl for _c, _l, _d, hl, _og in built_langs()],
         "image": SITE + ICON,
         "downloadUrl": STORE,
         "installUrl": STORE,
         "offers": {"@type": "Offer", "price": PRICE, "priceCurrency": PRICE_CCY,
                    "availability": "https://schema.org/InStock", "url": STORE},
         "screenshot": ([SITE + shot_url(code, HERO[0])]
                        + [SITE + shot_url(code, slug) for slug, _i, _c in SHOTS]),
         "publisher": {"@id": SITE + "/#organization"},
         "author": {"@id": SITE + "/#organization"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Stow Photo &amp; File Organizer",
             "item": abs_url("en")},
        ]},
    ]
    if code != "en":
        graph[2]["itemListElement"].append(
            {"@type": "ListItem", "position": 3,
             "name": "Stow Photo &amp; File Organizer (%s)" % code, "item": abs_url(code)})

    faqs = t.get("faqs", [])
    if faqs:
        faq_entities = []
        for f in faqs:
            faq_entities.append({
                "@type": "Question",
                "name": f["q"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": f["a"]
                }
            })
        graph.append({
            "@type": "FAQPage",
            "@id": abs_url(code) + "#faq",
            "inLanguage": BY_CODE[code][3],
            "mainEntity": faq_entities
        })

    return json.dumps({"@context": "https://schema.org", "@graph": graph},
                      ensure_ascii=False, separators=(",", ":"))


def stat_cards(t):
    icons = ["bi-arrow-right-circle", "bi-folder-plus", "bi-pin-angle",
             "bi-shield-exclamation", "bi-trash"]
    out = []
    for i, lab in enumerate(t["stats"]):
        last = i == len(t["stats"]) - 1
        out.append(
            """            <div class="col">
              <div class="card card-glass h-100 p-3 text-center%s">
                <i class="bi %s %s mb-2" aria-hidden="true"></i>
                <span class="stow-num%s">%s</span>
                <p class="extra-small text-secondary mb-0 mt-2">%s</p>
              </div>
            </div>""" % (
                " border border-success border-opacity-25" if last else "",
                icons[i],
                "text-success" if last else "text-secondary",
                " stow-num-zero" if last else "",
                "0" if last else "&mdash;",
                E(lab)))
    return "\n".join(out)


def model_rows(t):
    out = []
    for i, (name, lic, size) in enumerate(MODELS):
        out.append(
            """            <tr>
              <td class="text-white fw-semibold small">%s</td>
              <td class="text-secondary small">%s</td>
              <td class="small"><span class="badge bg-dark border border-secondary text-white-50">%s</span></td>
              <td class="text-primary small fw-semibold text-nowrap">%s</td>
            </tr>""" % (E(name), E(t["model_use"][i]), E(lic), E(size)))
    return "\n".join(out)


def not_list(items):
    out = []
    for it in items:
        out.append(
            """            <li class="d-flex gap-3 mb-3">
              <i class="bi bi-x-circle text-danger flex-shrink-0 mt-1" aria-hidden="true"></i>
              <span class="text-secondary small">%s</span>
            </li>""" % E(it))
    return "\n".join(out)


PLAN_ROWS = [
    ("IMG_20240315.jpg", "Pictures\\2024\\03 - March\\", "By year and month"),
    ("invoice-acme-0412.pdf", "Documents\\Invoices\\2024\\", "Invoices"),
    ("Screenshot 2024-06-02.png", "Screenshots\\2024\\", "Screenshots aside"),
    ("holiday.mp4", "Videos\\2024\\", "By file type"),
    ("holiday.srt", "Videos\\2024\\", "Companion file"),
    ("setup_v3.exe", "Installers\\", "By file type"),
]


def plan_table(t):
    head = ("""              <tr><th>%s</th><th>%s</th><th>%s</th></tr>"""
            % (E(t["th_plan_file"]), E(t["th_plan_dest"]), E(t["th_plan_rule"])))
    rows = "\n".join(
        """              <tr><td>%s</td><td class="plan-dest">%s</td><td class="plan-rule">%s</td></tr>"""
        % (E(f), E(d), E(r)) for f, d, r in PLAN_ROWS)
    return head, rows


# ------------------------------------------------------------------ New Sections

def render_problem(t):
    """The reason a cold visitor should keep reading.

    An advertisement drops somebody onto this page who has never heard of
    Stow, and the hero can only afford one promise. This section is where the
    problem gets named before the feature list starts - and the copy for it
    was already written and translated into all 23 languages, it had simply
    never been rendered: h_problem / problem1 / problem2 were passed to
    .format() by a template that did not reference them.

    intro1 and intro2 close the section. They used to be the hero's third and
    fourth paragraphs, which is what pushed the button off a laptop screen;
    they answer "so what does it do about it", which is exactly what a reader
    wants directly after the problem.
    """
    return """  <!-- The problem -->
  <section class="py-5" id="the-problem">
    <div class="container py-3">
      <div class="row justify-content-center">
        <div class="col-lg-9 text-center">
          <h2 class="display-6 fw-bold text-white mb-4">%s</h2>
          <p class="fs-5 text-secondary mb-3">%s</p>
          <p class="text-secondary mb-0">%s</p>
        </div>
      </div>
      <div class="row justify-content-center mt-5 pt-4 border-top border-secondary-subtle g-4">
        <div class="col-md-6 col-lg-5">
          <p class="text-secondary mb-0">%s</p>
        </div>
        <div class="col-md-6 col-lg-5">
          <p class="text-secondary mb-0">%s</p>
        </div>
      </div>
    </div>
  </section>
""" % (E(t["h_problem"]), E(t["problem1"]), E(t["problem2"]),
       E(t["intro1"]), E(t["intro2"]))


def render_gallery(code, t):
    """Six real captures of the running application, in the reader's language."""
    cards = []
    for slug, icon, caption in SHOTS:
        cards.append(
            """        <div class="col-md-6">
          <figure class="card card-glass stow-shot h-100">
            <img src="%s" alt="%s" loading="lazy" decoding="async" width="%d" height="%d">
            <figcaption><i class="bi %s me-2" aria-hidden="true"></i>%s</figcaption>
          </figure>
        </div>""" % (shot_url(code, slug), E(caption(t)), SHOT_W, SHOT_H,
                     E(icon), E(caption(t))))

    return """  <!-- Screenshots -->
  <section class="py-5" id="screenshots">
    <div class="container py-4">
      <div class="text-center max-w-700 mx-auto mb-5">
        <span class="text-gradient fw-bold text-uppercase tracking-wider">%s</span>
        <h2 class="display-5 fw-bold text-white mt-2">%s</h2>
        <p class="text-secondary fs-5">%s</p>
      </div>
      <div class="row g-4">
%s
      </div>
    </div>
  </section>
""" % (E(t["gallery_badge"]), E(t["gallery_heading"]), E(t["gallery_sub"]),
       "\n".join(cards))


def render_price(t, centred=False):
    """The price, in the same eyeful as the button, with the trial after it."""
    return ('<p class="stow-price mt-3 mb-0%s"><span class="stow-price-tag">'
            '<i class="bi bi-tag-fill me-1" aria-hidden="true"></i>%s</span>'
            '<span>%s</span></p>'
            % (" justify-content-center" if centred else "",
               E(t["price_badge"]), E(t["price_note"])))


def render_release_banner(t):
    rb = t.get("release_banner")
    if not rb:
        return ""
    pills_html = []
    for pill in rb.get("pills", []):
        pills_html.append(
            '<a href="%s" class="release-feature-pill">'
            '<i class="bi %s text-primary" aria-hidden="true"></i>'
            '<span>%s</span>'
            '</a>' % (E(pill["href"]), E(pill["icon"]), E(pill["text"]))
        )
    return """  <!-- Release Banner -->
  <section class="py-3 bg-dark border-bottom border-secondary-subtle" id="whats-new">
    <div class="container">
      <div class="release-banner p-3 p-md-4">
        <div class="row align-items-center gy-3">
          <div class="col-lg-8">
            <div class="d-flex align-items-center gap-2 mb-2">
              <span class="release-badge"><i class="bi bi-stars me-1" aria-hidden="true"></i>%s</span>
              <span class="text-white-50 small fw-semibold">%s</span>
            </div>
            <h2 class="h5 text-white fw-bold mb-1">%s</h2>
            <p class="text-secondary small mb-0">%s</p>
          </div>
          <div class="col-lg-4 text-lg-end">
            <a href="#pillar-explorer" class="btn btn-sm btn-dhin-primary rounded-pill px-3 py-2 fw-semibold shadow">
              <i class="bi bi-arrow-down-circle me-1" aria-hidden="true"></i> %s
            </a>
          </div>
        </div>
        <div class="d-flex flex-wrap gap-2 mt-3 pt-3 border-top border-secondary-subtle">
          %s
        </div>
      </div>
    </div>
  </section>""" % (E(rb["badge"]), E(rb.get("suite_name", "Stow 3.0 Desktop Suite")), E(rb["title"]), E(rb["sub"]), E(rb.get("cta", "Explore Latest Features")), "".join(pills_html))


def render_invariants(t):
    invs = t.get("invariants", [])
    if not invs:
        return ""
    cards = []
    for inv in invs:
        badge_text = inv.get("badge", "Invariant %s" % inv["num"])
        cards.append("""          <div class="col-lg-4 col-md-6">
            <div class="card card-glass h-100 p-4 invariant-card">
              <div class="d-flex align-items-center gap-3 mb-3">
                <span class="stow-icon-box"><i class="bi %s" aria-hidden="true"></i></span>
                <div>
                  <span class="badge bg-primary-subtle text-primary border border-primary-subtle rounded-pill extra-small px-2 py-0 mb-1">%s</span>
                  <h3 class="h6 text-white fw-bold mb-0">%s</h3>
                </div>
              </div>
              <p class="text-secondary small mb-0">%s</p>
            </div>
          </div>""" % (E(inv["icon"]), E(badge_text), E(inv["title"]), E(inv["desc"])))
    return """  <!-- Five Invariants -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="invariants">
    <div class="container py-4">
      <div class="text-center max-w-700 mx-auto mb-5">
        <span class="badge bg-primary-subtle text-primary border border-primary-subtle rounded-pill px-3 py-2 fw-semibold mb-2">
          <i class="bi bi-shield-lock-fill me-1" aria-hidden="true"></i> %s
        </span>
        <h2 class="display-5 fw-bold text-white">%s</h2>
        <p class="text-secondary fs-5">%s</p>
      </div>
      <div class="row g-4">
%s
      </div>
    </div>
  </section>""" % (E(t.get("invariants_badge", "Guaranteed by Architecture")),
                   E(t.get("invariants_heading", "The Five Invariants")),
                   E(t.get("invariants_sub", "Five non-negotiable architectural guarantees built into every layer of Stow.")),
                   "\n".join(cards))


def render_how_it_works(t):
    steps = t.get("how_it_works_steps", [])
    if not steps:
        return ""
    out = []
    for s in steps:
        out.append("""          <div class="col-lg-4">
            <div class="card card-glass h-100 p-4 text-center position-relative">
              <div class="stow-step mx-auto mb-3">%s</div>
              <i class="bi %s text-primary fs-3 mb-2" aria-hidden="true"></i>
              <h3 class="h5 text-white fw-bold mb-2">%s</h3>
              <p class="text-secondary small mb-0">%s</p>
            </div>
          </div>""" % (E(s["step"]), E(s["icon"]), E(s["title"]), E(s["desc"])))
    return """  <!-- How it Works -->
  <section class="py-5" id="how-it-works">
    <div class="container py-4">
      <div class="text-center max-w-700 mx-auto mb-5">
        <span class="badge bg-primary-subtle text-primary border border-primary-subtle rounded-pill px-3 py-2 fw-semibold mb-2">
          <i class="bi bi-gear-wide-connected me-1" aria-hidden="true"></i> %s
        </span>
        <h2 class="display-5 fw-bold text-white">%s</h2>
        <p class="text-secondary fs-5">%s</p>
      </div>
      <div class="row g-4">
%s
      </div>
    </div>
  </section>""" % (E(t.get("how_it_works_badge", "Safe Execution Flow")),
                   E(t.get("how_it_works_heading", "How It Works")),
                   E(t.get("how_it_works_sub", "Three simple, transparent steps. Absolute control from start to finish.")),
                   "\n".join(out))


def render_pillars(t):
    pillars = t.get("pillars", [])
    if not pillars:
        return ""
    out = []
    for p in pillars:
        features_html = []
        for feat in p["features"]:
            bullets_html = "".join("<li>%s</li>" % E(b) for b in feat.get("bullets", []))
            features_html.append("""              <div class="col-lg-4 col-md-6">
                <div class="card card-glass h-100 p-4 pillar-card border border-secondary-subtle">
                  <div class="d-flex align-items-center gap-2 mb-3">
                    <span class="stow-icon-box" style="width:38px;height:38px;font-size:1.1rem;border-radius:10px;">
                      <i class="bi %s" aria-hidden="true"></i>
                    </span>
                    <h3 class="h5 text-white fw-bold mb-0">%s</h3>
                  </div>
                  <p class="text-secondary small mb-3">%s</p>
                  <ul class="list-unstyled feature-bullet-list mb-0">
                    %s
                  </ul>
                </div>
              </div>""" % (E(p["icon"]), E(feat["title"]), E(feat["desc"]), bullets_html))
        
        out.append("""  <!-- %s: %s -->
  <section id="%s" class="py-5 border-top border-secondary-subtle">
    <div class="container py-3">
      <div class="d-flex flex-wrap align-items-center justify-content-between gap-3 mb-4">
        <div>
          <span class="badge bg-primary-subtle text-primary border border-primary-subtle rounded-pill px-3 py-1 fw-semibold mb-2">
            <i class="bi %s me-1" aria-hidden="true"></i> %s
          </span>
          <h2 class="display-6 fw-bold text-white mb-1">%s</h2>
          <p class="text-secondary fs-5 mb-0">%s</p>
        </div>
      </div>
      <div class="row g-4">
%s
      </div>
    </div>
  </section>""" % (E(p["tag"]), E(p["title"]), E(p["id"]), E(p["icon"]), E(p["tag"]), E(p["title"]), E(p["lead"]), "\n".join(features_html)))
    return "\n".join(out)


def render_comparison_table(t):
    rows = t.get("comparison_rows", [])
    if not rows:
        return ""
    headers = t.get("comparison_headers", ["Feature & Safety Guarantee", "Stow (Dhinovatech)", "Traditional Tools / Scripts", "Cloud Services"])
    
    rows_html = []
    for r in rows:
        rows_html.append("""                <tr>
                  <td class="text-white fw-semibold small text-nowrap align-middle">%s</td>
                  <td class="stow-col small align-middle">
                    <span class="d-flex align-items-center gap-2">
                      <i class="bi bi-check-circle-fill text-success flex-shrink-0" aria-hidden="true"></i>
                      <span class="text-white fw-semibold">%s</span>
                    </span>
                  </td>
                  <td class="text-secondary small align-middle">
                    <span class="d-flex align-items-center gap-2">
                      <i class="bi bi-dash-circle text-secondary flex-shrink-0" aria-hidden="true"></i>
                      <span>%s</span>
                    </span>
                  </td>
                  <td class="text-secondary small align-middle">
                    <span class="d-flex align-items-center gap-2">
                      <i class="bi bi-x-circle text-danger flex-shrink-0" aria-hidden="true"></i>
                      <span>%s</span>
                    </span>
                  </td>
                </tr>""" % (E(r["feature"]), E(r["stow"]), E(r["trad"]), E(r["cloud"])))
    
    return """  <!-- Comparison Table -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="comparison">
    <div class="container py-4">
      <div class="text-center max-w-700 mx-auto mb-5">
        <span class="badge bg-primary-subtle text-primary border border-primary-subtle rounded-pill px-3 py-2 fw-semibold mb-2">
          <i class="bi bi-sliders me-1" aria-hidden="true"></i> %s
        </span>
        <h2 class="display-5 fw-bold text-white">%s</h2>
        <p class="text-secondary fs-5">%s</p>
      </div>
      <div class="card card-glass p-3 p-md-4 border border-secondary-subtle shadow-lg">
        <div class="table-responsive">
          <table class="table table-dark table-borderless align-middle mb-0 compare-table">
            <thead>
              <tr class="border-bottom border-secondary">
                <th scope="col">%s</th>
                <th scope="col" class="stow-col text-primary fw-bold"><i class="bi bi-shield-check me-1" aria-hidden="true"></i>%s</th>
                <th scope="col">%s</th>
                <th scope="col">%s</th>
              </tr>
            </thead>
            <tbody>
%s
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </section>""" % (E(t.get("comparison_badge", "Uncompromising Privacy & Control")),
                   E(t.get("comparison_heading", "How Stow Compares")),
                   E(t.get("comparison_sub", "Why desktop users choose Stow over scriptable tools and cloud platforms.")),
                   E(headers[0]), E(headers[1]), E(headers[2]), E(headers[3]),
                   "\n".join(rows_html))


def render_faq_accordion(t):
    faqs = t.get("faqs", [])
    if not faqs:
        return ""
    items = []
    for i, f in enumerate(faqs):
        num = i + 1
        collapsed = "collapsed" if i > 0 else ""
        show = "show" if i == 0 else ""
        items.append("""            <!-- FAQ %d -->
            <div class="accordion-item bg-transparent border-bottom border-secondary">
              <h2 class="accordion-header" id="faq%dHeading">
                <button class="accordion-button %s bg-transparent text-white fw-semibold py-4" type="button" data-bs-toggle="collapse" data-bs-target="#faq%d">
                  Q%d: %s
                </button>
              </h2>
              <div id="faq%d" class="accordion-collapse collapse %s" data-bs-parent="#stowFaqAccordion">
                <div class="accordion-body text-secondary small pb-4">
                  %s
                </div>
              </div>
            </div>""" % (num, num, collapsed, num, num, E(f["q"]), num, show, E(f["a"])))
    
    return """  <!-- FAQ Section -->
  <section class="py-5" id="faq">
    <div class="container py-4">
      <div class="text-center max-w-700 mx-auto mb-5">
        <span class="badge bg-primary-subtle text-primary border border-primary-subtle rounded-pill px-3 py-2 fw-semibold mb-2">
          <i class="bi bi-question-circle me-1" aria-hidden="true"></i> %s
        </span>
        <h2 class="display-5 fw-bold text-white">%s</h2>
        <p class="text-secondary fs-5">%s</p>
      </div>
      <div class="row justify-content-center">
        <div class="col-lg-9">
          <div class="accordion accordion-flush" id="stowFaqAccordion">
%s
          </div>
        </div>
      </div>
    </div>
  </section>""" % (E(t.get("faqs_badge", "Clear Answers")),
                   E(t.get("faqs_heading", "Frequently Asked Questions")),
                   E(t.get("faqs_sub", "Everything you need to know about privacy, offline AI, file safety, and system compatibility.")),
                   "\n".join(items))


def build(code):
    # Fallback to English for any key that hasn't been localized yet
    t = dict(L["en"])
    if code in L:
        t.update(L[code])

    _c, label, direction, hl, og = BY_CODE[code]
    title = "%s | Windows (Microsoft Store) | Dhinovatech" % t["name"]
    desc = ("%s %s" % (t["tagline"], t["intro1"]))[:300]

    og_alts = "\n".join(
        '  <meta property="og:locale:alternate" content="%s">' % o
        for c2, _l, _d, _h, o in built_langs() if c2 != code)

    plan_head, plan_body = plan_table(t)

    doc = """<!DOCTYPE html>
<html lang="{hl}" dir="{dir}" data-bs-theme="dark">
<head>
{analytics_block}
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{desc}">

  <!-- Bootstrap 5.3 CDN & Icons -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">

  <!-- Custom CSS -->
  <link rel="stylesheet" href="/assets/css/custom.css">
  <link rel="icon" type="image/x-icon" href="/favicon.ico">
  <link rel="icon" type="image/png" href="/favicon.png">
  <link rel="apple-touch-icon" href="/favicon.png">

{page_css}
  <!-- BEGIN SEO block (canonical/hreflang/social/schema) -->
{hreflang}
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Dhinovatech">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{site}{ogimg}">
  <meta property="og:image:width" content="{ogw}">
  <meta property="og:image:height" content="{ogh}">
  <meta property="og:image:alt" content="{ogalt}">
  <meta property="og:locale" content="{og}">
{og_alts}
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="{site}{ogimg}">
  <meta name="twitter:image:alt" content="{ogalt}">
  <script type="application/ld+json">
{schema}
  </script>
  <!-- END SEO block -->
  <!-- BEGIN resource hints -->
  <link rel="preload" as="image" href="{hero_shot}" fetchpriority="high">
  <link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
  <link rel="dns-prefetch" href="https://cdn.jsdelivr.net">
  <link rel="preconnect" href="https://www.googletagmanager.com">
  <link rel="dns-prefetch" href="https://www.googletagmanager.com">
  <link rel="manifest" href="/site.webmanifest">
  <meta name="theme-color" content="#080c14">
  <meta name="color-scheme" content="dark light">
  <!-- END resource hints -->
</head>
<body>
<a class="skip-link" href="#main">Skip to main content</a>
<!-- Navigation Bar (independent Stow tree) -->
{navbar}
<main id="main">

  <!-- Hero.

       An advertisement pays for the first screenful, so everything that has
       to survive a five-second read is in it: what this is, who it runs on,
       what it costs, the button, and a photograph of the actual application.
       The 3.0 release banner used to sit above all of this and pushed the
       button below the fold on a 1366x768 laptop; it now runs underneath,
       where a returning visitor still finds it and a first-time one is not
       asked to care about a version number before they know what the product
       does. -->
  <section class="hero-section position-relative overflow-hidden">
    <div class="container">
      <div class="row align-items-center gy-5">
        <div class="col-lg-6">
          <div class="d-flex align-items-center gap-3 mb-4">
            <span class="stow-hero-icon">
              <img src="{icon}" alt="" decoding="async" width="512" height="512">
            </span>
            <span>
              <span class="d-block stow-hero-name text-white">Stow</span>
              <span class="d-block small text-secondary">
                <i class="bi bi-microsoft me-1" aria-hidden="true"></i>Microsoft Store &middot; Windows 10 &amp; 11
              </span>
            </span>
          </div>

          <h1 class="hero-title mb-3">{name}</h1>
          <p class="lead text-secondary mb-4 pe-lg-4 fs-5">{tagline}</p>

          <div class="d-flex flex-wrap gap-3 align-items-center">
            <a href="{store}" target="_blank" rel="noopener" class="btn btn-store btn-store-ms shadow-lg">
              <i class="bi bi-microsoft" aria-hidden="true"></i>
              <span class="btn-store-copy">
                <span class="btn-store-pre">Get it from</span>
                <span class="btn-store-name">Microsoft Store</span>
              </span>
            </a>
            <a href="#how-it-works" class="btn btn-dhin-outline btn-lg rounded-pill px-4">
              <i class="bi bi-play-circle me-2" aria-hidden="true"></i> {cta_see}
            </a>
          </div>
          {price_line}

          <div class="stow-badge-row pt-4 mt-2">
            <span class="badge bg-dark border border-secondary text-white-50 px-3 py-2 rounded-pill"><i class="bi bi-wifi-off text-primary me-1" aria-hidden="true"></i> {badge_offline}</span>
            <span class="badge bg-dark border border-secondary text-white-50 px-3 py-2 rounded-pill"><i class="bi bi-table text-info me-1" aria-hidden="true"></i> {badge_preview}</span>
            <span class="badge bg-dark border border-secondary text-white-50 px-3 py-2 rounded-pill"><i class="bi bi-trash3 text-danger me-1" aria-hidden="true"></i> {badge_recycle}</span>
            <span class="badge bg-dark border border-secondary text-white-50 px-3 py-2 rounded-pill"><i class="bi bi-arrow-counterclockwise text-success me-1" aria-hidden="true"></i> {badge_undo}</span>
            <span class="badge bg-dark border border-secondary text-white-50 px-3 py-2 rounded-pill"><i class="bi bi-cloud-slash text-warning me-1" aria-hidden="true"></i> {badge_cloud}</span>
            <span class="badge bg-dark border border-secondary text-white-50 px-3 py-2 rounded-pill"><i class="bi bi-cpu text-info me-1" aria-hidden="true"></i> {badge_arch}</span>
          </div>
        </div>

        <div class="col-lg-6">
          <div class="position-relative">
            <div class="position-absolute top-50 start-50 translate-middle w-100 h-100 rounded-circle bg-primary opacity-25 blur-3xl glow-aura-teal" aria-hidden="true"></div>
            <!-- No drawn window chrome around this: the capture already
                 contains the real Windows title bar, and a second one on top
                 of it reads as a mock-up of the thing it is evidence for. -->
            <div class="stow-window position-relative">
              <img src="{hero_shot}" alt="{hero_shot_alt}" decoding="async" fetchpriority="high" width="{shot_w}" height="{shot_h}">
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

{problem_section}

{invariants_section}

{how_it_works_section}

{gallery_section}

  <!-- The preview -->
  <section id="the-preview" class="py-5">
    <div class="container py-4">
      <div class="text-center max-w-700 mx-auto mb-5">
        <span class="text-gradient fw-bold text-uppercase tracking-wider">Complete Transparency</span>
        <h2 class="display-5 fw-bold text-white mt-2">{h_preview}</h2>
        <p class="text-secondary fs-5">{preview1}</p>
      </div>

      <div class="row row-cols-2 row-cols-lg-5 g-3 mb-4">
{stat_cards}
      </div>
      <p class="text-center extra-small text-success mb-5"><i class="bi bi-shield-check me-1" aria-hidden="true"></i>{stats_note}</p>

      <div class="row justify-content-center">
        <div class="col-lg-10">
          <div class="card card-glass p-3 p-md-4 border border-primary border-opacity-25 shadow-lg">
            <div class="plan-scroll">
              <table class="plan-table">
                <thead>
{plan_head}
                </thead>
                <tbody>
{plan_body}
                </tbody>
              </table>
            </div>
          </div>
          <p class="text-secondary mt-4 mb-0">{preview2}</p>
        </div>
      </div>
    </div>
  </section>

{release_banner}

{pillars_section}

{comparison_section}

  <!-- Models -->
  <section class="py-5" id="models">
    <div class="container py-4">
      <div class="row gy-5">
        <div class="col-lg-5">
          <div class="stow-icon-box mb-3"><i class="bi bi-cpu-fill" aria-hidden="true"></i></div>
          <h2 class="display-6 fw-bold text-white mb-3">{h_models}</h2>
          <p class="text-secondary mb-3">{models1}</p>
          <p class="text-secondary mb-0">{models2}</p>
        </div>
        <div class="col-lg-7">
          <div class="card card-glass p-3 p-md-4">
            <div class="table-responsive">
              <table class="table table-dark table-borderless align-middle mb-0 model-table">
                <thead>
                  <tr class="border-bottom border-secondary">
                    <th scope="col" class="small text-secondary">{th_model}</th>
                    <th scope="col" class="small text-secondary">{th_does}</th>
                    <th scope="col" class="small text-secondary">{th_licence}</th>
                    <th scope="col" class="small text-secondary">{th_size}</th>
                  </tr>
                </thead>
                <tbody>
{model_rows}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- What it is not + who it is for -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle">
    <div class="container py-4">
      <div class="row g-4">
        <div class="col-lg-6">
          <div class="card card-glass h-100 p-4">
            <h2 class="h3 text-white fw-bold mb-4">{h_not}</h2>
            <ul class="list-unstyled mb-0">
{not_list}
            </ul>
          </div>
        </div>
        <div class="col-lg-6">
          <div class="card card-glass h-100 p-4 border border-primary border-opacity-25">
            <div class="stow-icon-box mb-3"><i class="bi bi-people-fill" aria-hidden="true"></i></div>
            <h2 class="h3 text-white fw-bold mb-3">{h_who}</h2>
            <p class="text-secondary small mb-0">{who}</p>
          </div>
        </div>
      </div>
    </div>
  </section>

{faq_section}

  <!-- Final CTA + honest limits -->
  <section class="py-5">
    <div class="container py-4">
      <div class="card card-glass p-5 text-center border-0 position-relative overflow-hidden" style="background: linear-gradient(135deg, rgba(255,182,52,0.13) 0%, rgba(240,147,13,0.08) 100%);">
        <div class="max-w-700 mx-auto position-relative" style="z-index: 2;">
          <div class="mx-auto mb-3" style="width: 90px; height: 90px; border-radius: 20px; overflow: hidden; border: 1px solid rgba(255,255,255,0.14);">
            <img src="{icon}" alt="Stow Icon" class="w-100 h-100 object-fit-cover" loading="lazy" decoding="async" width="512" height="512">
          </div>
          <h2 class="display-6 fw-bold text-white mb-3">{name}</h2>
          <p class="text-secondary fs-5 mb-4">{tagline}</p>
          <div class="d-flex justify-content-center">
            <a href="{store}" target="_blank" rel="noopener" class="btn btn-store btn-store-ms shadow-lg">
              <i class="bi bi-microsoft" aria-hidden="true"></i>
              <span class="btn-store-copy">
                <span class="btn-store-pre">Get it from</span>
                <span class="btn-store-name">Microsoft Store</span>
              </span>
            </a>
          </div>
          {price_line_centred}
        </div>
      </div>

      <div class="mt-4 p-4 rounded-4 bg-black border border-warning-subtle">
        <div class="d-flex gap-3">
          <i class="bi bi-exclamation-triangle-fill text-warning fs-4" aria-hidden="true"></i>
          <div>
            <h2 class="h6 text-warning fw-bold mb-1">{h_important}</h2>
            <p class="small text-secondary mb-0">{important}</p>
          </div>
        </div>
      </div>
    </div>
  </section>

</main>
{footer}
  <!-- Bootstrap 5.3 JS Bundle -->
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
  <script src="/assets/js/nav.js"></script>

  <!-- BEGIN generated UX block -->
  <div class="install-bar" role="complementary" aria-label="Stow Photo &amp; File Organizer">
    <img src="{icon}" alt="" width="42" height="42" loading="lazy" decoding="async">
    <div class="install-bar-text">
      <div class="install-bar-title">Stow</div>
      <div class="install-bar-sub"><i class="bi bi-microsoft" aria-hidden="true"></i> Microsoft Store</div>
    </div>
    <a href="{store}" target="_blank" rel="noopener" class="btn btn-primary btn-sm rounded-pill px-3">{cta_install}</a>
  </div>
  <button type="button" class="to-top" aria-label="Back to top" title="Back to top">
    <i class="bi bi-arrow-up" aria-hidden="true"></i>
  </button>
  <script src="/assets/js/ux.js"></script>
  <!-- END generated UX block -->
{consent_banner}
</body>
</html>
""".format(
        hl=hl,
        dir=direction,
        title=E(title),
        desc=E(desc),
        analytics_block=analytics_block(),
        page_css=PAGE_CSS,
        hreflang=hreflang_block(code),
        canonical=abs_url(code),
        site=SITE,
        ogimg=OGIMG, ogw=OGW, ogh=OGH, ogalt=E(OGALT),
        og=og,
        og_alts=og_alts,
        schema=schema(code, t, desc),
        navbar=navbar(code, t),
        release_banner=render_release_banner(t),
        problem_section=render_problem(t),
        gallery_section=render_gallery(code, t),
        price_line=render_price(t),
        price_line_centred=render_price(t, centred=True),
        hero_shot=shot_url(code, HERO[0]),
        hero_shot_alt=E(HERO[1](t)),
        shot_w=SHOT_W, shot_h=SHOT_H,
        invariants_section=render_invariants(t),
        how_it_works_section=render_how_it_works(t),
        pillars_section=render_pillars(t),
        comparison_section=render_comparison_table(t),
        faq_section=render_faq_accordion(t),
        footer=FOOTER,
        consent_banner=consent_banner_html(code),
        store=E(STORE_UTM),
        store_id=STORE_ID,
        icon=ICON,
        nlang=len(built_langs()),
        name=E(t["name"]),
        tagline=E(t["tagline"]),
        intro1=E(t["intro1"]),
        intro2=E(t["intro2"]),
        cta_store=E(t.get("cta_store", "Get on Microsoft Store")),
        cta_see=E(t.get("cta_see", "See how it works")),
        cta_install=E(t.get("cta_install", "Install")),
        badge_offline=E(t.get("badge_offline", "100% Offline")),
        badge_preview=E(t.get("badge_preview", "Approved Preview First")),
        badge_recycle=E(t.get("badge_recycle", "Never Permanently Deletes")),
        badge_undo=E(t.get("badge_undo", "1-Click Undo")),
        badge_cloud=E(t.get("badge_cloud", "Safe with Cloud Folders")),
        badge_arch=E(t.get("badge_arch", "x64 & ARM64")),
        h_problem=E(t["h_problem"]), problem1=E(t["problem1"]), problem2=E(t["problem2"]),
        h_preview=E(t["h_preview"]), preview1=E(t["preview1"]), preview2=E(t["preview2"]),
        stat_cards=stat_cards(t), stats_note=E(t["stats_note"]),
        plan_head=plan_head, plan_body=plan_body,
        h_principles=E(t["h_principles"]),
        h_undo=E(t["h_undo"]), undo1=E(t["undo1"]), undo2=E(t["undo2"]),
        h_dupes=E(t["h_dupes"]), dupes1=E(t["dupes1"]), dupes2=E(t["dupes2"]),
        h_more=E(t["h_more"]),
        h_privacy=E(t["h_privacy"]), privacy1=E(t["privacy1"]), privacy2=E(t["privacy2"]),
        h_models=E(t["h_models"]), models1=E(t["models1"]), models2=E(t["models2"]),
        th_model=E(t["th_model"]), th_does=E(t["th_does"]),
        th_licence=E(t["th_licence"]), th_size=E(t["th_size"]),
        model_rows=model_rows(t),
        h_not=E(t["h_not"]), not_list=not_list(t["not_items"]),
        h_who=E(t["h_who"]), who=E(t["who"]),
        h_important=E(t["h_important"]), important=E(t["important"]),
    )
    return doc


def main():
    base = os.path.join(ROOT, SECTION)
    for code, _label, _d, _hl, _og in built_langs():
        folder = base if code == "en" else os.path.join(base, code)
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, "index.html")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(build(code))
        print("wrote", path)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
