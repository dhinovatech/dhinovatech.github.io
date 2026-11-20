#!/usr/bin/env python3
"""
Generate /Sortwise/ - "Sortwise: AI Photo & File Organizer", the free
Microsoft Store (WinUI 3) app that tidies Downloads, Desktop, Documents and
Pictures, finds duplicate files and photos, and can undo every change, in the
app's 23 languages.

Built on the same template as /steptell/, /KeepOne/ and /smart-photos/: its
own navigation tree whose language switcher lists only the Sortwise locales,
every CTA pointing at the Microsoft Store listing, real store slides in the
hero and the gallery, and the install bar / back-to-top chrome wrapped in
tools/build-ux.py's BEGIN/END markers so that builder replaces it rather than
appending a copy.

The folder is /Sortwise/ with a capital S because /Sortwise/privacy.html was
published there first (and given to Partner Center); the generated pages
join it. This builder writes index.html files only; privacy.html is
hand-written.

Sortwise shares its engine with Stow but is sold as a separate, free product
with a look of its own. The page deliberately never mentions Stow (the app's
own plan rules out Stow promotion inside Sortwise, and the two listings must
read as different products), and none of Stow's page copy is reused.

The copy comes from two files:

  * tools/sortwise-listing.json - the store listing's own translated text
    (localized title, short description, the 19 description paragraphs, the
    20 feature bullets, the 9 slide captions) and the words on the store
    slides, refreshed from the app repository by tools/build-sortwise-shots.py.
  * tools/sortwise-strings.json - what is written for this page: the
    at-a-glance facts, the comparison with tidying by hand, the three steps,
    what it tidies, the free plan explained, and the FAQ. Claims were checked
    against the app repo's docs/SORTWISE-PLAN.md, the Store description and
    the privacy policy on 2026-11-15.

Pricing: every feature is free, with 1,000 file changes a month (moving,
copying, renaming or removing a file; scanning, searching, finding duplicates,
backups and undo never count; undo refunds; resets on the 1st). Two optional
Durable add-ons remove the limit: "Pro for 24 hours" and "Pro forever". The
page prints no price: the Store sets it per market and the app shows only the
Store's prices. The Offer in the structured data is the app's own price, 0.

Store links are ordinary https://apps.microsoft.com/detail/... URLs so they
work everywhere and stay crawlable; assets/js/ux.js upgrades them to
ms-windows-store:// in place when the visitor is on Windows.

Run:  python tools/build-sortwise.py
Idempotent: every page is rewritten from the two JSON files on each run.
"""
import html
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")


def _load(name):
    with open(os.path.join(TOOLS, name), encoding="utf-8") as fh:
        return json.load(fh)


S = _load("sortwise-strings.json")
LISTING = _load("sortwise-listing.json")
CONSENT_L = _load("consent-strings.json")

SECTION = "Sortwise"
SITE = "https://www.dhinovatech.com"
STORE_ID = "9NSTWXHBQBJ0"
STORE = "https://apps.microsoft.com/detail/" + STORE_ID
STORE_UTM = STORE + "?ocid=dhinovatech_sortwise"

ICON = "/assets/images/sortwise-icon.png"
ICON_WEBP = "/assets/images/sortwise-icon.webp"
PRIVACY = "/Sortwise/privacy.html"
# When the page's copy last changed in substance; the WebPage schema reports it.
MODIFIED = "2026-11-15"
OGIMG = "/assets/images/sortwise-og.png"
OGW, OGH = 1200, 630
OGALT = ("Sortwise - free AI photo and file organizer for Windows: tidy Downloads, "
         "find duplicates, undo anything")

# The store slides tools/build-sortwise-shots.py writes. HERO is slide 1; the
# other seven are slides 3-9, in the order of listing "shots" (and of listing
# "captions"[2:]).
HERO = "ai-photo-file-organizer"
SHOTS = ["ai-photo-search", "sort-files-by-type-or-date", "preview-every-move",
         "duplicate-file-finder", "find-files", "tidy-downloads-folder", "undo-timeline"]
SHOT_W, SHOT_H = 1200, 675
SHOT_ICONS = ["bi-search-heart", "bi-ui-checks-grid", "bi-list-check", "bi-files",
              "bi-search", "bi-check2-circle", "bi-arrow-counterclockwise"]
# The eight overview tiles of store slide 2, keyed by the kit's own icon names.
TILE_ICONS = {"tidy": "bi-folder2-open", "search": "bi-search-heart", "copy": "bi-files",
              "similar": "bi-images", "ai": "bi-stars", "rename": "bi-input-cursor-text",
              "undo": "bi-arrow-counterclockwise", "lock": "bi-shield-lock"}
CHIP_ICONS = ["bi-lightning-charge text-warning", "bi-eye text-info",
              "bi-cloud-slash text-success"]
USE_ICONS = ["bi-download", "bi-display", "bi-camera", "bi-hdd", "bi-receipt",
             "bi-music-note-beamed"]
# Store description paragraphs 4-10 are "HEADING\n• item\n• item" blocks.
DETAIL = [(4, "bi-folder-check"), (5, "bi-input-cursor-text"), (6, "bi-search"),
          (7, "bi-camera"), (8, "bi-hdd"), (9, "bi-receipt"), (10, "bi-hdd-stack")]

# How Sortwise and tidying by hand in File Explorer fare on each row of the
# comparison, the same in every language: y = yes, p = partly, n = no.
# Rows follow t["cmp_rows"]. File Explorer facts: no duplicate finder; search
# is by name and file details (describing a photo needs a Copilot+ PC);
# renaming a selection gives numbered names only; Ctrl+Z undoes recent steps.
CMP_MARKS = [
    "yp",   # sort a messy folder by type
    "yp",   # photos by date taken
    "yn",   # duplicates by content
    "yp",   # find photos by what is in them
    "yp",   # batch rename
    "yn",   # see the plan first
    "yp",   # undo a whole clean-up days later
    "yy",   # price
]
MARK_ICON = {"y": "bi-check-circle-fill peer-y", "p": "bi-dash-circle-fill peer-p",
             "n": "bi-x-circle-fill peer-n"}

# Strings keys that are the same in every language, so only "en" carries them.
SAME_IN_ALL = {"cmp_us"}

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

# (code, menu label, dir, hreflang, og locale) - the app's 23 languages.
# Portuguese is the Brazilian listing ("arquivos").
LANGS = [
    ("en", "English", "ltr", "en", "en_US"),
    ("de", "Deutsch (German)", "ltr", "de", "de_DE"),
    ("fr", "Français (French)", "ltr", "fr", "fr_FR"),
    ("es", "Español (Spanish)", "ltr", "es", "es_ES"),
    ("it", "Italiano (Italian)", "ltr", "it", "it_IT"),
    ("pt", "Português (Brasil)", "ltr", "pt-BR", "pt_BR"),
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
BY_CODE = {row[0]: row for row in LANGS}

E = html.escape


def url_for(code):
    return "/%s/" % SECTION if code == "en" else "/%s/%s/" % (SECTION, code)


def abs_url(code):
    return SITE + url_for(code)


def shot_url(code, slug):
    rel = "assets/images/sortwise/%s/%s.webp" % (code, slug)
    if code != "en" and not os.path.exists(os.path.join(ROOT, rel)):
        rel = "assets/images/sortwise/en/%s.webp" % slug
    return "/" + rel


def built_langs():
    return [x for x in LANGS if x[0] in LISTING and x[0] in S]


def split_head(p):
    """A description block "HEADING\\nbody" -> (heading, body lines)."""
    head, _sep, rest = p.partition("\n")
    return head.strip(), [l.strip() for l in rest.split("\n") if l.strip()]


def bullet(line):
    return line.lstrip("•·-– ").strip()


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


def _consent(code):
    return CONSENT_L.get(code) or CONSENT_L.get(code.split("-")[0]) or CONSENT_L["en"]


def consent_banner_html(code):
    c = _consent(code)
    return """%s
<div class="consent-bar" id="consentBar" role="region" aria-label="%s" hidden>
  <p class="consent-bar-text">%s <a href="/privacy.html" class="consent-bar-link">%s</a></p>
  <div class="consent-bar-actions">
    <button type="button" class="consent-btn consent-btn-ghost" data-consent="deny">%s</button>
    <button type="button" class="consent-btn consent-btn-solid" data-consent="allow">%s</button>
  </div>
</div>
<script src="/assets/js/consent.js"></script>
%s""" % (BAR_BEGIN, E(c["aria"]), E(c["body"]), E(c.get("privacy", "Privacy Policy")),
         E(c["decline"]), E(c["accept"]), BAR_END)


def privacy_label(code):
    return _consent(code).get("privacy", "Privacy Policy")


# --------------------------------------------------------------------------
# Shared navigation - Sortwise owns its own language tree.
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
               icon_cls, E(label)))
    return "".join(out)


def navbar(code, t):
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

          <!-- Our Apps - Sortwise owns its own language tree; build-nav-apps.py
               adds Smart Photos, KeepOne, Steptell and Mortgage above it -->
          <li class="nav-item dropdown">
            <a class="nav-link nav-link-custom dropdown-toggle active" href="#" id="appsDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
              Our Apps
            </a>
            <ul class="dropdown-menu dropdown-menu-dark border-secondary shadow-lg mt-2" aria-labelledby="appsDropdown">
              <li class="dropdown-submenu position-relative">
                <a class="dropdown-item py-2 d-flex align-items-center justify-content-between" href="/Sortwise/">
                  <span><img src="__ICON__" alt="Sortwise Icon" style="width: 20px; height: 20px; border-radius: 5px; object-fit: contain;" class="me-2" decoding="async" width="256" height="256">Sortwise File Organizer</span>
                  <span class="badge bg-primary-subtle text-primary border border-primary-subtle rounded-pill ms-2 extra-small submenu-toggle-btn" role="button" title="View __N__ Languages">__N__ Languages <i class="bi bi-chevron-down ms-1" aria-hidden="true"></i></span>
                </a>
                <ul class="dropdown-menu dropdown-menu-dark border-secondary shadow-lg scrollable-menu" style="max-height: 360px; overflow-y: auto;">
                  __LANG_SUBMENU__
                </ul>
              </li>
              <li><a class="dropdown-item py-2" href="/nudge/"><img src="/assets/images/nudge-icon.webp" alt="Nudge Icon" style="width: 20px; height: 20px; border-radius: 5px; object-fit: cover;" class="me-2" decoding="async" width="512" height="512">Nudge Offline Journal</a></li>
              <li><a class="dropdown-item py-2" href="/stow/"><img src="/assets/images/stow-icon.png" alt="Stow Icon" style="width: 20px; height: 20px; border-radius: 5px; object-fit: cover;" class="me-2" decoding="async">Stow Photo &amp; File Organizer</a></li>
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

          <!-- Language Selector - Sortwise only -->
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
   .replace("__LANG_LABEL__", E(BY_CODE[code][1])) \
   .replace("__ICON__", ICON_WEBP) \
   .replace("__N__", str(len(built_langs()))) \
   .replace("__STORE__", E(STORE_UTM)) \
   .replace("__STORE_CTA__", E(t["cta_store"]))


FOOTER = """  <footer class="footer-dhin">
    <div class="container">
      <div class="row gy-4 mb-5">
        <div class="col-lg-4">
          <a class="d-flex align-items-center gap-2 mb-3" href="/">
            <img src="/assets/images/LogoWithText.webp" alt="Dhinovatech Logo" class="brand-logo-with-text-img" loading="lazy" decoding="async" width="512" height="82">
          </a>
          <p class="text-secondary small pe-lg-4">
            Dhinovatech is an independent app studio making privacy-first mobile &amp; desktop apps, available on Google Play and Microsoft Store.
          </p>
        </div>
        <div class="col-lg-2 col-6">
          <h4 class="h6 text-white fw-bold mb-3">Studio</h4>
          <ul class="list-unstyled small d-flex flex-column gap-2 mb-0">
            <li><a href="/" class="footer-link">Home</a></li>
            <li><a href="/about.html" class="footer-link">About Us</a></li>
            <li><a href="/contact.html" class="footer-link">Contact Us</a></li>
            <li><a href="/privacy.html" class="footer-link">Privacy Policy</a></li>
            <li><a href="/terms.html" class="footer-link">Terms of Service</a></li>
          </ul>
        </div>
        <div class="col-lg-3 col-6">
          <h4 class="h6 text-white fw-bold mb-3">Our Applications</h4>
          <ul class="list-unstyled small d-flex flex-column gap-2 mb-0">
            <li><a href="/smart-photos/" class="footer-link">Smart Photos</a></li>
            <li><a href="/KeepOne/" class="footer-link">KeepOne Duplicate Finder</a></li>
            <li><a href="/steptell/" class="footer-link">Steptell Steps Recorder</a></li>
            <li><a href="/Sortwise/" class="footer-link text-primary fw-semibold">Sortwise File Organizer</a></li>
            <li><a href="/pubmaker/" class="footer-link">PubMaker Pub File Editor</a></li>
            <li><a href="/nudge/" class="footer-link">Nudge Offline Journal &amp; AI</a></li>
            <li><a href="/stow/" class="footer-link">Stow Photo &amp; File Organizer</a></li>
            <li><a href="/glowcompare/" class="footer-link">GlowCompare</a></li>
            <li><a href="/glowcompare-windows/" class="footer-link">GlowCompare for Windows</a></li>
            <li><a href="/milk-monthly-expense-calendar/" class="footer-link">Milk Calendar</a></li>
            <li><a href="/slouch-guard/" class="footer-link">Slouch Guard AI</a></li>
            <li><a href="/notelock/" class="footer-link">Notelock</a></li>
            <li><a href="/mortgage-loan-emi-pro/" class="footer-link">Mortgage EMI Pro</a></li>
            <li><a href="/aes-vault/" class="footer-link">AES Vault</a></li>
          </ul>
        </div>
        <div class="col-lg-3">
          <h4 class="h6 text-white fw-bold mb-3">Support &amp; Legal</h4>
          <p class="small text-secondary mb-2"><i class="bi bi-envelope-fill me-2 text-primary" aria-hidden="true"></i>dhinovatech@gmail.com</p>
          <p class="small text-secondary mb-2"><i class="bi bi-globe me-2 text-primary" aria-hidden="true"></i>www.dhinovatech.com</p>
          <p class="small mb-0"><a href="/Sortwise/privacy.html" class="footer-link"><i class="bi bi-shield-check me-2 text-primary" aria-hidden="true"></i>Sortwise Privacy Policy</a></p>
        </div>
      </div>
      <div class="pt-4 border-top border-secondary text-center text-secondary small">
        <p class="mb-0">&copy; 2026 Dhinovatech. All rights reserved.</p>
      </div>
    </div>
  </footer>
"""

# Same structure as the Steptell, KeepOne and Smart Photos pages, re-keyed to
# the emerald and amber of the Sortwise store slides (green backdrop, amber
# "ALL FEATURES FREE" pill). The custom properties are declared site-wide in
# custom.css, so re-declaring them here re-keys the shared chrome for this
# section only. Blue stays reserved for the Microsoft Store buttons
# (.btn-primary and .btn-store-ms are not touched).
PAGE_CSS = """  <style>
    :root {
      --dhin-accent-blue: #2ed39b;
      --dhin-border-glow: rgba(46, 211, 155, 0.32);
      --dhin-shadow-glow: 0 0 25px rgba(46, 211, 155, 0.18);
      --dhin-gradient-primary: linear-gradient(135deg, #2ed39b 0%, #0e8b63 100%);
      --sw-green: #2ed39b;
      --sw-deep: #0e8b63;
      --sw-amber: #ffd366;
      --sw-ink: #032c1f;
    }
    :root, [data-bs-theme="dark"] {
      --bs-primary-rgb: 46, 211, 155;
      --bs-primary-bg-subtle: rgba(46, 211, 155, 0.12);
      --bs-primary-border-subtle: rgba(46, 211, 155, 0.32);
      --bs-primary-text-emphasis: #9cf0d0;
    }
    .text-gradient {
      background: linear-gradient(135deg, #b8f5df 0%, #2ed39b 55%, #ffd366 100%);
      -webkit-background-clip: text;
      background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .btn-dhin-primary { box-shadow: 0 4px 15px rgba(46, 211, 155, 0.24); }
    .btn-dhin-primary:hover { box-shadow: 0 8px 25px rgba(46, 211, 155, 0.38); }
    .btn-dhin-outline:hover { background: rgba(46, 211, 155, 0.1); }
    .hero-section {
      padding: 56px 0 64px;
      background: radial-gradient(circle at 22% 18%, rgba(14, 139, 99, 0.34) 0%, rgba(8, 12, 20, 0) 62%);
    }
    @media (max-width: 991.98px) { .hero-section { padding: 32px 0 48px; } }
    .hero-title { overflow-wrap: anywhere; }

    .glow-aura-green { box-shadow: 0 0 45px rgba(14, 139, 99, 0.35); }
    .sw-icon-box {
      width: 52px; height: 52px; border-radius: 14px;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.4rem; flex-shrink: 0;
      background: linear-gradient(135deg, rgba(46,211,155,0.16), rgba(255,211,102,0.12));
      color: var(--sw-green); border: 1px solid rgba(46,211,155,0.3);
    }
    .sw-icon-box-sm { width: 38px; height: 38px; font-size: 1.1rem; border-radius: 10px; }
    .sw-badge-row { display: flex; flex-wrap: wrap; gap: .5rem; }
    .sw-step {
      width: 42px; height: 42px; border-radius: 50%; flex-shrink: 0;
      display: flex; align-items: center; justify-content: center;
      font-weight: 800; font-size: 1.1rem;
      background: rgba(46,211,155,0.16); color: var(--sw-green);
      border: 1px solid rgba(46,211,155,0.4);
    }

    /* Hero */
    .sw-hero-icon { width: 60px; height: 60px; flex-shrink: 0; }
    .sw-hero-icon img { width: 100%; height: 100%; object-fit: contain; display: block; }
    .sw-hero-kind { font-weight: 600; color: #e2e8f0; font-size: .95rem; line-height: 1.3; }
    .sw-hero-tagline {
      font-size: clamp(1.15rem, 1rem + 0.8vw, 1.6rem); font-weight: 500;
      line-height: 1.35; letter-spacing: 0; color: #9cf0d0; margin-top: .6rem;
    }
    .sw-cta-strip .sw-price { margin: 0; }
    .sw-price {
      display: flex; align-items: center; gap: .5rem; flex-wrap: wrap;
      font-size: .92rem; color: #cbd5e1;
    }
    .sw-price-tag {
      background: var(--sw-amber); color: var(--sw-ink);
      border-radius: 20px; padding: 3px 14px; font-size: .95rem; font-weight: 800;
      white-space: nowrap; text-decoration: none;
      box-shadow: 0 0 18px rgba(255, 211, 102, .3);
    }
    .sw-price-tag:hover { color: var(--sw-ink); background: #ffe08f; }
    .sw-window {
      border-radius: 14px; overflow: hidden; background: #06402f;
      border: 1px solid rgba(255,255,255,.12);
      box-shadow: 0 30px 70px -25px rgba(0,0,0,.9);
    }
    .sw-window img { display: block; width: 100%; height: auto; }

    .sw-narrow { max-width: 760px; }

    /* At a glance */
    .sw-glance-def { font-size: 1.1rem; color: #e2e8f0; line-height: 1.6; }
    .sw-facts { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 0; margin: 0; }
    .sw-fact { padding: 1rem 1.1rem; border-top: 1px solid rgba(255,255,255,.08); }
    .sw-fact dt { font-size: .75rem; text-transform: uppercase; letter-spacing: .06em; color: var(--sw-green); font-weight: 700; margin-bottom: .3rem; }
    .sw-fact dd { margin: 0; font-size: .92rem; color: #cbd5e1; }

    /* Screenshot gallery */
    .sw-shot { overflow: hidden; margin: 0; }
    .sw-shot img { display: block; width: 100%; height: auto; border-bottom: 1px solid rgba(255,255,255,.07); }
    .sw-shot figcaption { padding: 1rem 1.1rem 1.1rem; }
    .sw-shot-kicker { font-size: .72rem; letter-spacing: .08em; font-weight: 700; color: var(--sw-green); text-transform: uppercase; }
    .sw-shot-title { font-size: 1.02rem; font-weight: 700; color: #fff; margin: .25rem 0 .6rem; }
    .sw-shot ul { margin: 0; padding: 0; list-style: none; }
    .sw-shot li { font-size: .86rem; color: #cbd5e1; display: flex; gap: .5rem; margin-bottom: .25rem; }
    .sw-shot li i { color: var(--sw-green); flex-shrink: 0; }

    /* Cards */
    .invariant-card { border-left: 3px solid var(--sw-green) !important; transition: transform .2s ease, box-shadow .2s ease; }
    [dir="rtl"] .invariant-card { border-left: 0 !important; border-right: 3px solid var(--sw-green) !important; }
    .invariant-card:hover { transform: translateY(-3px); box-shadow: 0 10px 30px rgba(46, 211, 155, 0.1); }
    .pillar-card { transition: transform .2s ease, border-color .2s ease; }
    .pillar-card:hover { transform: translateY(-3px); border-color: rgba(46, 211, 155, 0.4) !important; }
    .sw-check-list li { display: flex; gap: .6rem; margin-bottom: .6rem; font-size: .9rem; color: #cbd5e1; }
    .sw-check-list li i { color: var(--sw-green); flex-shrink: 0; margin-top: .1rem; }
    .sw-detail-head { font-size: .78rem; letter-spacing: .07em; font-weight: 700; color: var(--sw-amber); text-transform: uppercase; }
    .sw-oneapp { background: rgba(255, 211, 102, .07); border: 1px solid rgba(255, 211, 102, .28) !important; }

    /* Sortwise vs by hand */
    .peer-table { font-size: .9rem; border-collapse: separate; border-spacing: 0; }
    .peer-table th, .peer-table td { padding: .8rem .85rem; border-bottom: 1px solid rgba(255,255,255,.07); vertical-align: top; min-width: 150px; }
    .peer-table thead th { background: rgba(17, 24, 39, .95); color: #94a3b8; font-weight: 600; }
    .peer-table th.sw-col, .peer-table td.sw-col { background: rgba(46, 211, 155, .07); border-left: 1px solid rgba(46,211,155,.25); border-right: 1px solid rgba(46,211,155,.25); }
    .peer-table thead th.sw-col { color: var(--sw-green); border-top: 2px solid var(--sw-green); }
    .peer-table tbody th { min-width: 170px; font-weight: 600; }
    .peer-cell { display: flex; gap: .45rem; align-items: flex-start; }
    .peer-cell i { flex-shrink: 0; margin-top: .15rem; }
    .peer-y { color: #34d399; }
    .peer-p { color: var(--sw-amber); }
    .peer-n { color: #f87171; }

    /* Pricing */
    .sw-plan { display: flex; flex-direction: column; border: 1px solid rgba(255,255,255,.1) !important; }
    .sw-plan-free { border: 2px solid var(--sw-green) !important; box-shadow: 0 0 40px rgba(46, 211, 155, .14); }
    .sw-plan-price { font-size: 2.6rem; font-weight: 800; line-height: 1.1; color: var(--sw-green); }
    .sw-plan-price-sm { font-size: 1.15rem; font-weight: 600; color: #e2e8f0; line-height: 1.4; min-height: 2.6rem; display: flex; align-items: center; }
    .sw-plan-opt { background: rgba(255,255,255,.08); color: #cbd5e1; font-size: .72rem; font-weight: 600; }
    .sw-quota {
      display: flex; align-items: center; gap: .9rem;
      padding: .9rem 1.1rem; border-radius: 14px;
      background: rgba(255, 211, 102, .1); border: 1px solid rgba(255, 211, 102, .38);
    }
    .sw-quota-num { font-size: 2.2rem; font-weight: 800; line-height: 1; color: var(--sw-amber); flex-shrink: 0; }
    .sw-quota-label { font-weight: 700; color: #fff; line-height: 1.3; }
    .sw-quota-pro { background: rgba(46, 211, 155, .1); border-color: rgba(46, 211, 155, .38); }
    .sw-quota-pro .sw-quota-num { color: var(--sw-green); }

    /* FAQ */
    .accordion-button:not(.collapsed) { background: rgba(46, 211, 155, 0.08); color: var(--sw-green); box-shadow: none; }
    .accordion-button:focus { box-shadow: 0 0 0 0.2rem rgba(46, 211, 155, 0.25); }
    .accordion-button::after { filter: invert(1) grayscale(100%) brightness(200%); }
    [dir="rtl"] .accordion-button::after { margin-left: 0; margin-right: auto; }

    @media (prefers-reduced-motion: reduce) {
      .invariant-card, .pillar-card { transition: none; }
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


def schema(code, t, lst, title, desc):
    graph = [
        {"@type": "Organization", "@id": SITE + "/#organization",
         "name": "Dhinovatech", "url": SITE + "/"},
        {"@type": "SoftwareApplication",
         "@id": SITE + "/Sortwise/#software",
         "name": "Sortwise",
         "alternateName": lst["title"],
         "operatingSystem": "Windows 10 version 2004 (build 19041) and later, Windows 11",
         "applicationCategory": "UtilitiesApplication",
         "applicationSubCategory": "File organizer, photo organizer and duplicate file finder",
         "description": desc,
         "abstract": lst["description"][0],
         "url": abs_url(code),
         "inLanguage": [hl for _c, _l, _d, hl, _og in built_langs()],
         "image": SITE + ICON,
         "downloadUrl": STORE,
         "installUrl": STORE,
         "featureList": lst["features"],
         "isAccessibleForFree": True,
         "processorRequirements": "x64 or ARM64",
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD",
                    "availability": "https://schema.org/InStock", "url": STORE},
         "screenshot": [SITE + shot_url(code, s) for s in [HERO] + SHOTS],
         "publisher": {"@id": SITE + "/#organization"},
         "author": {"@id": SITE + "/#organization"}},
        {"@type": "WebPage", "@id": abs_url(code) + "#webpage", "url": abs_url(code),
         "name": title, "description": desc, "inLanguage": BY_CODE[code][3],
         "dateModified": MODIFIED, "about": {"@id": SITE + "/Sortwise/#software"},
         "mainEntity": {"@id": SITE + "/Sortwise/#software"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Sortwise", "item": abs_url("en")},
        ]},
        {"@type": "FAQPage", "@id": abs_url(code) + "#faq",
         "inLanguage": BY_CODE[code][3],
         "mainEntity": [{"@type": "Question", "name": f["q"],
                         "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
                        for f in t["faqs"]]},
    ]
    if code != "en":
        graph[3]["itemListElement"].append(
            {"@type": "ListItem", "position": 3,
             "name": "Sortwise (%s)" % code, "item": abs_url(code)})
    return json.dumps({"@context": "https://schema.org", "@graph": graph},
                      ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


# ---------------------------------------------------------------- sections

def eyebrow(icon, text):
    return ('<span class="badge bg-primary-subtle text-primary border border-primary-subtle '
            'rounded-pill px-3 py-2 fw-semibold mb-2"><i class="bi %s me-1" aria-hidden="true">'
            '</i> %s</span>' % (icon, E(text)))


def section_head(icon, eb, h, sub):
    return """      <div class="text-center mx-auto mb-5 sw-narrow">
        %s
        <h2 class="display-5 fw-bold text-white">%s</h2>
        %s
      </div>""" % (eyebrow(icon, eb), E(h),
                   '<p class="text-secondary fs-5 mb-0">%s</p>' % E(sub) if sub else "")


def store_button(t):
    return """<a href="%s" target="_blank" rel="noopener" class="btn btn-store btn-store-ms shadow-lg">
              <i class="bi bi-microsoft" aria-hidden="true"></i>
              <span class="btn-store-copy">
                <span class="btn-store-pre">%s</span>
                <span class="btn-store-name">Microsoft Store</span>
              </span>
            </a>""" % (E(STORE_UTM), E(t["store_pre"]))


def store_kind(lst):
    """The descriptor of the localized store title ("AI Photo & File Organizer").

    Each language's title was written from that market's Store searches, so
    the hero shows it rather than a second, invented one.
    """
    title = lst["title"]
    for sep in (": ", " : ", "：", " - ", " – "):
        if title.startswith("Sortwise" + sep):
            return title[len("Sortwise" + sep):]
    return lst["kind"]


def check_items(rows, indent="              "):
    return "\n".join(
        '%s<li><i class="bi bi-check2-circle" aria-hidden="true"></i><span>%s</span></li>'
        % (indent, E(r)) for r in rows)


def render_price(lst, centred=False):
    return ('<p class="sw-price mt-3 mb-0%s"><a class="sw-price-tag" href="#pricing">'
            '<i class="bi bi-gift-fill me-1" aria-hidden="true"></i>%s</a>'
            '<span>%s &middot; %s</span></p>'
            % (" justify-content-center" if centred else "",
               E(lst["free"]), E(lst["scans"]), E(lst["changes"])))


def cta_strip(t, lst):
    """The store button again, where a reader who is convinced looks for it."""
    return """      <div class="sw-cta-strip d-flex flex-column flex-md-row align-items-center justify-content-center gap-3 mt-5">
        %s
        %s
      </div>
""" % (store_button(t), render_price(lst).replace(" mt-3", ""))


def render_hero(code, t, lst):
    badges = "\n".join(
        '            <span class="badge bg-dark border border-secondary text-white-50 px-3 py-2 rounded-pill">'
        '<i class="bi %s me-1" aria-hidden="true"></i> %s</span>' % (i, E(b))
        for i, b in zip(CHIP_ICONS, lst["chips"]))
    return """  <section class="hero-section position-relative overflow-hidden">
    <div class="container">
      <div class="row align-items-center gy-5">
        <div class="col-lg-6">
          <div class="d-flex align-items-center gap-3 mb-4">
            <span class="sw-hero-icon">
              <img src="%(icon)s" alt="" decoding="async" width="256" height="256">
            </span>
            <span>
              <span class="d-block sw-hero-kind">%(kind)s</span>
              <span class="d-block small text-secondary">
                <i class="bi bi-microsoft me-1" aria-hidden="true"></i>Microsoft Store &middot; Windows 10 &amp; 11
              </span>
            </span>
          </div>

          <h1 class="hero-title mb-3"><span class="d-block">Sortwise</span> <span class="d-block sw-hero-tagline">%(h1)s</span></h1>
          <p class="lead text-secondary mb-4 pe-lg-4 fs-5">%(lead)s</p>

          <div class="d-flex flex-wrap gap-3 align-items-center">
            %(store)s
            <a href="#screenshots" class="btn btn-dhin-outline btn-lg rounded-pill px-4">
              <i class="bi bi-images me-2" aria-hidden="true"></i> %(cta_see)s
            </a>
          </div>
          %(price)s

          <div class="sw-badge-row pt-4 mt-2">
%(badges)s
          </div>
        </div>

        <div class="col-lg-6">
          <div class="position-relative">
            <div class="position-absolute top-50 start-50 translate-middle w-100 h-100 rounded-circle bg-primary opacity-25 blur-3xl glow-aura-green" aria-hidden="true"></div>
            <div class="sw-window position-relative">
              <img src="%(hero)s" alt="%(hero_alt)s" decoding="async" fetchpriority="high" width="%(w)d" height="%(h)d">
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
""" % dict(icon=ICON_WEBP, kind=E(store_kind(lst)),
           h1=E(lst["headline"]), lead=E(lst["description"][1]),
           store=store_button(t), cta_see=E(t["shots"]), price=render_price(lst),
           badges=badges, hero=shot_url(code, HERO), hero_alt=E(lst["captions"][0]),
           w=SHOT_W, h=SHOT_H)


def render_glance(t, lst):
    """One definition paragraph and the key facts, as a description list.

    Written to be quoted: search snippets and AI answers lift a page's own
    plain statement of what a thing is, what it costs and what it needs far
    more readily than they assemble one from marketing copy. The definition is
    the store description's opening paragraph, already keyword-tuned per market.
    """
    facts = "\n".join(
        '            <div class="sw-fact"><dt>%s</dt><dd>%s</dd></div>' % (E(k), E(v))
        for k, v in t["glance"])
    return """  <!-- At a glance -->
  <section class="py-5 border-top border-secondary-subtle" id="at-a-glance">
    <div class="container py-3">
      <div class="row justify-content-center">
        <div class="col-lg-10">
          <h2 class="h3 text-white fw-bold mb-3"><i class="bi bi-info-circle text-primary me-2" aria-hidden="true"></i>%s</h2>
          <p class="sw-glance-def mb-4">%s</p>
          <dl class="sw-facts card card-glass border border-secondary-subtle overflow-hidden">
%s
          </dl>
        </div>
      </div>
    </div>
  </section>
""" % (E(t["glance_h"]), E(lst["description"][0]), facts)


def render_overview(lst):
    """Store slide 2 as real text: everything in one app, all free."""
    ov = lst["overview"]
    tiles = []
    for key, name, what in ov["tiles"]:
        tiles.append("""        <div class="col-xl-3 col-md-6">
          <div class="card card-glass h-100 p-4 pillar-card border border-secondary-subtle">
            <div class="d-flex align-items-center gap-3 mb-2">
              <span class="sw-icon-box sw-icon-box-sm"><i class="bi %s" aria-hidden="true"></i></span>
              <h3 class="h6 text-white fw-bold mb-0">%s</h3>
            </div>
            <p class="text-secondary small mb-0">%s</p>
          </div>
        </div>""" % (TILE_ICONS.get(key, "bi-check2-circle"), E(name), E(what)))
    one_h, one_body = split_head(lst["description"][16])
    return """  <!-- Overview -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="overview">
    <div class="container py-4">
%s
      <div class="sw-narrow mx-auto mb-5">
        <p class="text-secondary">%s</p>
        <p class="text-secondary mb-0">%s</p>
      </div>
      <div class="row g-4 justify-content-center">
%s
      </div>
      <div class="card card-glass sw-oneapp p-4 mt-4">
        <h3 class="sw-detail-head mb-2">%s</h3>
        <p class="text-secondary mb-0">%s</p>
      </div>
    </div>
  </section>
""" % (section_head("bi-grid-3x3-gap", ov["kicker"], ov["title"], lst["subline"]),
       E(lst["description"][2]), E(lst["description"][3]), "\n".join(tiles),
       E(one_h), E(" ".join(one_body)))


def render_gallery(code, t, lst):
    cards = []
    for i, (slug, icon) in enumerate(zip(SHOTS, SHOT_ICONS)):
        shot = lst["shots"][i]
        cap = lst["captions"][i + 2]
        points = "".join('<li><i class="bi bi-check2" aria-hidden="true"></i><span>%s</span></li>'
                         % E(p) for p in shot["points"])
        cards.append("""        <div class="col-md-6">
          <figure class="card card-glass sw-shot h-100">
            <img src="%s" alt="%s" loading="lazy" decoding="async" width="%d" height="%d">
            <figcaption>
              <div class="sw-shot-kicker"><i class="bi %s me-1" aria-hidden="true"></i>%s</div>
              <h3 class="sw-shot-title">%s</h3>
              <ul>%s</ul>
            </figcaption>
          </figure>
        </div>""" % (shot_url(code, slug), E(cap), SHOT_W, SHOT_H, icon, E(shot["kicker"]),
                     E(shot["title"]), points))
    return """  <!-- Screenshots -->
  <section class="py-5" id="screenshots">
    <div class="container py-4">
%s
      <div class="row g-4 justify-content-center">
%s
      </div>
%s    </div>
  </section>
""" % (section_head("bi-images", t["shots"], t["shots_h"], ""), "\n".join(cards),
       cta_strip(t, lst))


def render_pricing(t, lst):
    """Every feature free, with 1,000 file changes a month; Pro lifts the cap.

    No price: the Store sets it per market and the app shows only the Store's.
    """
    return """  <!-- Pricing -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="pricing">
    <div class="container py-4">
%s
      <div class="row justify-content-center g-4">
        <div class="col-md-6 col-lg-5">
          <div class="card card-glass h-100 p-4 p-lg-5 sw-plan sw-plan-free">
            <h3 class="h5 text-white fw-bold mb-1">%s</h3>
            <p class="sw-plan-price mb-3">%s</p>
            <div class="sw-quota mb-4">
              <span class="sw-quota-num">%s</span>
              <span class="sw-quota-label">%s</span>
            </div>
            <ul class="list-unstyled sw-check-list mb-4">
%s
            </ul>
            <div class="mt-auto">%s</div>
          </div>
        </div>
        <div class="col-md-6 col-lg-5">
          <div class="card card-glass h-100 p-4 p-lg-5 sw-plan">
            <h3 class="h5 text-white fw-bold mb-1">%s <span class="badge rounded-pill sw-plan-opt align-middle ms-1">%s</span></h3>
            <p class="sw-plan-price sw-plan-price-sm mb-3">%s</p>
            <div class="sw-quota sw-quota-pro mb-4">
              <span class="sw-quota-num"><i class="bi bi-infinity" aria-hidden="true"></i></span>
              <span class="sw-quota-label">%s</span>
            </div>
            <ul class="list-unstyled sw-check-list mb-0">
%s
            </ul>
          </div>
        </div>
      </div>
      <p class="text-secondary small text-center mx-auto mt-4 mb-0 sw-narrow">%s</p>
    </div>
  </section>
""" % (section_head("bi-gift", t["price_eb"], t["price_h"], t["price_sub"]),
       E(t["free_title"]), E(t["free_price"]), E(t["quota_num"]), E(t["quota_label"]),
       check_items(t["free_items"]), store_button(t),
       E(t["pro_title"]), E(t["pro_badge"]), E(t["pro_price"]), E(t["pro_label"]),
       check_items(t["pro_items"]), E(t["price_fine"]))


def render_steps(t, lst):
    steps = []
    for n, s in enumerate(t["steps"], 1):
        steps.append("""        <div class="col-md-4">
          <div class="card card-glass h-100 p-4">
            <div class="d-flex align-items-center gap-3 mb-2">
              <div class="sw-step">%d</div>
              <h3 class="h6 text-white fw-bold mb-0">%s</h3>
            </div>
            <p class="text-secondary small mb-0">%s</p>
          </div>
        </div>""" % (n, E(s["t"]), E(s["d"])))
    return """  <!-- How it works -->
  <section class="py-5" id="how-it-works">
    <div class="container py-4">
%s
      <div class="row g-4">
%s
      </div>
%s    </div>
  </section>
""" % (section_head("bi-signpost-split", t["steps_eb"], t["steps_h"], ""), "\n".join(steps),
       cta_strip(t, lst))


def render_compare(t):
    head = "\n".join([
        '                <th scope="col">%s</th>' % E(t["cmp_feature"]),
        '                <th scope="col" class="sw-col">%s</th>' % E(t["cmp_us"]),
        '                <th scope="col">%s</th>' % E(t["cmp_them"]),
    ])
    rows = []
    for marks, row in zip(CMP_MARKS, t["cmp_rows"]):
        cells = ['                  <th scope="row" class="text-white">%s</th>' % E(row[0])]
        for i, (m, cell) in enumerate(zip(marks, row[1:])):
            cells.append('                  <td%s><span class="peer-cell"><i class="bi %s" aria-hidden="true"></i>'
                         '<span class="%s">%s</span></span></td>'
                         % (' class="sw-col"' if i == 0 else "", MARK_ICON[m],
                            "text-white fw-semibold" if i == 0 else "text-secondary", E(cell)))
        rows.append("                <tr>\n%s\n                </tr>" % "\n".join(cells))
    return """  <!-- Sortwise or by hand -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="compare">
    <div class="container py-4">
%s
      <div class="card card-glass p-2 p-md-3 border border-secondary-subtle shadow-lg">
        <div class="table-responsive">
          <table class="table table-dark table-borderless mb-0 peer-table">
            <thead>
              <tr class="border-bottom border-secondary">
%s
              </tr>
            </thead>
            <tbody>
%s
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </section>
""" % (section_head("bi-arrow-left-right", t["cmp_eb"], t["cmp_h"], t["cmp_sub"]),
       head, "\n".join(rows))


def render_uses(t):
    cards = []
    for icon, c in zip(USE_ICONS, t["use_cards"]):
        cards.append("""        <div class="col-lg-4 col-md-6">
          <div class="card card-glass h-100 p-4 pillar-card border border-secondary-subtle">
            <span class="sw-icon-box mb-3"><i class="bi %s" aria-hidden="true"></i></span>
            <h3 class="h6 text-white fw-bold mb-2">%s</h3>
            <p class="text-secondary small mb-0">%s</p>
          </div>
        </div>""" % (icon, E(c["t"]), E(c["d"])))
    return """  <!-- What it tidies -->
  <section class="py-5" id="use-cases">
    <div class="container py-4">
%s
      <div class="row g-4">
%s
      </div>
    </div>
  </section>
""" % (section_head("bi-stars", t["use_eb"], t["use_h"], ""), "\n".join(cards))


def render_detail(t, lst):
    """The store description's feature blocks, set as cards."""
    cards = []
    for n, icon in DETAIL:
        head, lines = split_head(lst["description"][n])
        cards.append("""        <div class="col-lg-6">
          <div class="card card-glass h-100 p-4 invariant-card">
            <div class="d-flex align-items-center gap-3 mb-3">
              <span class="sw-icon-box sw-icon-box-sm"><i class="bi %s" aria-hidden="true"></i></span>
              <h3 class="sw-detail-head mb-0">%s</h3>
            </div>
            <ul class="list-unstyled sw-check-list mb-0">
%s
            </ul>
          </div>
        </div>""" % (icon, E(head), check_items([bullet(l) for l in lines])))
    return """  <!-- In detail -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="features-in-detail">
    <div class="container py-4">
%s
      <div class="row g-4">
%s
      </div>
    </div>
  </section>
""" % (section_head("bi-list-stars", t["detail_eb"], t["detail_h"], ""), "\n".join(cards))


def render_privacy(code, t, lst):
    _h, body = split_head(lst["description"][11])
    net = [l.strip() for l in lst["description"][12].split("\n") if l.strip()]
    net_lead, net_items = net[0], [bullet(l) for l in net[1:]]
    return """  <!-- Private by design -->
  <section class="py-5" id="privacy">
    <div class="container py-4">
%s
      <div class="card card-glass p-4 p-md-5 invariant-card">
        <p class="text-white mb-4">%s</p>
        <p class="text-secondary mb-2">%s</p>
        <ul class="list-unstyled sw-check-list mb-4">
%s
        </ul>
        <p class="text-secondary mb-4">%s</p>
        <a class="small" href="%s"><i class="bi bi-shield-check me-1" aria-hidden="true"></i>%s</a>
      </div>
    </div>
  </section>
""" % (section_head("bi-shield-lock", t["priv_eb"], t["priv_h"], t["priv_sub"]),
       E(" ".join(body)), E(net_lead), check_items(net_items, "          "),
       E(lst["description"][13]), PRIVACY, E(privacy_label(code)))


def render_windows(lst):
    cards = []
    for n, icon in ((14, "bi-windows"), (15, "bi-translate")):
        head, body = split_head(lst["description"][n])
        cards.append("""        <div class="col-lg-6">
          <div class="card card-glass h-100 p-4 pillar-card border border-secondary-subtle">
            <div class="d-flex align-items-center gap-3 mb-3">
              <span class="sw-icon-box sw-icon-box-sm"><i class="bi %s" aria-hidden="true"></i></span>
              <h2 class="sw-detail-head mb-0">%s</h2>
            </div>
            <p class="text-secondary small mb-0">%s</p>
          </div>
        </div>""" % (icon, E(head), E(" ".join(body))))
    return """  <!-- Built for Windows, in your language -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="windows">
    <div class="container py-4">
      <div class="row g-4">
%s
      </div>
    </div>
  </section>
""" % "\n".join(cards)


def render_features(t, lst):
    feats = lst["features"]
    half = (len(feats) + 1) // 2
    cols = []
    for chunk in (feats[:half], feats[half:]):
        cols.append("""          <div class="col-md-6">
            <ul class="list-unstyled sw-check-list mb-0">
%s
            </ul>
          </div>""" % check_items(chunk))
    return """  <!-- Every feature -->
  <section class="py-5" id="features">
    <div class="container py-4">
      <div class="card card-glass p-4 p-md-5 border border-primary border-opacity-25">
        <h2 class="h4 text-white fw-bold mb-4"><i class="bi bi-list-check text-primary me-2" aria-hidden="true"></i>%s</h2>
        <div class="row g-3">
%s
        </div>
      </div>
    </div>
  </section>
""" % (E(t["feat_h"]), "\n".join(cols))


def render_faq(t):
    items = []
    for i, f in enumerate(t["faqs"], 1):
        first = i == 1
        items.append("""            <div class="accordion-item bg-transparent border-bottom border-secondary">
              <h3 class="accordion-header" id="faq%dHeading">
                <button class="accordion-button%s bg-transparent text-white fw-semibold py-4" type="button" data-bs-toggle="collapse" data-bs-target="#faq%d" aria-expanded="%s" aria-controls="faq%d">
                  %s
                </button>
              </h3>
              <div id="faq%d" class="accordion-collapse collapse%s" aria-labelledby="faq%dHeading" data-bs-parent="#sortwiseFaqAccordion">
                <div class="accordion-body text-secondary small pb-4">
                  %s
                </div>
              </div>
            </div>""" % (i, "" if first else " collapsed", i, "true" if first else "false", i,
                         E(f["q"]), i, " show" if first else "", i, E(f["a"])))
    return """  <!-- FAQ -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="faq">
    <div class="container py-4">
%s
      <div class="row justify-content-center">
        <div class="col-lg-9">
          <div class="accordion accordion-flush" id="sortwiseFaqAccordion">
%s
          </div>
        </div>
      </div>
    </div>
  </section>
""" % (section_head("bi-question-circle", t["faq_eb"], t["faq_h"], ""), "\n".join(items))


def render_final(code, t, lst):
    return """  <!-- Final CTA -->
  <section class="py-5">
    <div class="container py-4">
      <div class="card card-glass p-5 text-center border-0 position-relative overflow-hidden" style="background: linear-gradient(135deg, rgba(14,139,99,0.22) 0%%, rgba(255,211,102,0.08) 100%%);">
        <div class="sw-narrow mx-auto position-relative" style="z-index: 2;">
          <div class="mx-auto mb-3" style="width: 90px; height: 90px;">
            <img src="%s" alt="Sortwise Icon" class="w-100 h-100 object-fit-contain" loading="lazy" decoding="async" width="256" height="256">
          </div>
          <h2 class="display-6 fw-bold text-white mb-3">%s</h2>
          <p class="text-secondary fs-5 mb-2">%s</p>
          <p class="text-white fs-5 mb-4">%s</p>
          <div class="d-flex justify-content-center">
            %s
          </div>
          %s
          <p class="small mt-4 mb-0"><a href="%s"><i class="bi bi-shield-check me-1" aria-hidden="true"></i>%s</a></p>
        </div>
      </div>
    </div>
  </section>
""" % (ICON_WEBP, E(lst["headline"]), E(lst["description"][17]), E(lst["description"][18]),
       store_button(t), render_price(lst, True), PRIVACY, E(privacy_label(code)))


def build(code):
    t = dict(S["en"])
    t.update(S.get(code, {}))
    lst = LISTING[code]
    _c, _label, direction, hl, og = BY_CODE[code]
    title = t["seo_title"]
    desc = t["seo_desc"]

    og_alts = "\n".join('  <meta property="og:locale:alternate" content="%s">' % o
                        for c2, _l, _d, _h, o in built_langs() if c2 != code)

    body = "\n".join([
        render_hero(code, t, lst),
        # What it is and what it costs, stated plainly; then everything it
        # does; then what it looks like; then the free plan, since that is the
        # first question for a free app with a monthly allowance; then how,
        # why not by hand, for what, and the detail.
        render_glance(t, lst),
        render_overview(lst),
        render_gallery(code, t, lst),
        render_pricing(t, lst),
        render_steps(t, lst),
        render_compare(t),
        render_uses(t),
        render_detail(t, lst),
        render_privacy(code, t, lst),
        render_windows(lst),
        render_features(t, lst),
        render_faq(t),
        render_final(code, t, lst),
    ])

    return """<!DOCTYPE html>
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
<!-- Navigation Bar (independent Sortwise tree) -->
{navbar}
<main id="main">

{body}
</main>
{footer}
  <!-- Bootstrap 5.3 JS Bundle -->
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
  <script src="/assets/js/nav.js"></script>

  <!-- BEGIN generated UX block -->
  <div class="install-bar" role="complementary" aria-label="Sortwise">
    <img src="{icon}" alt="" width="42" height="42" loading="lazy" decoding="async">
    <div class="install-bar-text">
      <div class="install-bar-title">Sortwise</div>
      <div class="install-bar-sub"><i class="bi bi-microsoft" aria-hidden="true"></i> Microsoft Store</div>
    </div>
    <a href="{store}" target="_blank" rel="noopener" class="btn btn-primary btn-sm rounded-pill px-3">Install</a>
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
        hl=hl, dir=direction, title=E(title), desc=E(desc),
        analytics_block=analytics_block(), page_css=PAGE_CSS,
        hreflang=hreflang_block(code), canonical=abs_url(code), site=SITE,
        ogimg=OGIMG, ogw=OGW, ogh=OGH, ogalt=E(OGALT), og=og, og_alts=og_alts,
        schema=schema(code, t, lst, title, desc), hero_shot=shot_url(code, HERO),
        navbar=navbar(code, t), body=body, footer=FOOTER, icon=ICON_WEBP,
        store=E(STORE_UTM), consent_banner=consent_banner_html(code))


def check(code, t, lst):
    """Fail loudly when the listing or strings no longer have the shape used above."""
    problems = []
    d = lst["description"]
    if len(d) != 19:
        problems.append("description has %d paragraphs, expected 19" % len(d))
    else:
        problems += ["description paragraph %d has no heading line" % n
                     for n in [n for n, _i in DETAIL] + [11, 14, 15, 16] if "\n" not in d[n]]
        if d[12].count("\n") < 2:
            problems.append("description paragraph 12 lost its two internet bullets")
    for key, n in (("cmp_rows", len(CMP_MARKS)), ("steps", 3), ("use_cards", len(USE_ICONS)),
                   ("glance", 9), ("free_items", 5), ("pro_items", 4)):
        if len(t[key]) != n:
            problems.append("%s has %d items, expected %d" % (key, len(t[key]), n))
    if any(len(r) != 3 for r in t["cmp_rows"]):
        problems.append("a cmp_rows row does not have 3 cells")
    if len(lst["shots"]) != len(SHOTS) or len(lst["captions"]) != 9:
        problems.append("listing shots/captions do not match the seven gallery slides")
    if len(lst["overview"]["tiles"]) != 8 or len(lst["chips"]) != 3:
        problems.append("slide text no longer has 8 tiles and 3 hero chips")
    if problems:
        raise SystemExit("%s: %s" % (code, "; ".join(problems)))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    base = os.path.join(ROOT, SECTION)
    for code, _label, _d, _hl, _og in built_langs():
        t = dict(S["en"])
        t.update(S.get(code, {}))
        check(code, t, LISTING[code])
        folder = base if code == "en" else os.path.join(base, code)
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, "index.html")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(build(code))
        missing = [k for k in S["en"] if k not in S.get(code, {}) and k not in SAME_IN_ALL]
        print("wrote %s%s" % (os.path.relpath(path, ROOT),
                              "  (English fallback: %d keys)" % len(missing) if code != "en" and missing else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
