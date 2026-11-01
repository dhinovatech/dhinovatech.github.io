#!/usr/bin/env python3
"""
Generate /steptell/ - "Steptell: Steps Recorder & Guide Maker", the Microsoft
Store (WinUI 3) app that records every click as a numbered step with a
screenshot and turns it into a how-to guide, in the app's 25 languages.

Built on the same template as /KeepOne/, /smart-photos/ and /nudge/: its own
navigation tree whose language switcher lists only the Steptell locales,
every CTA pointing at the Microsoft Store listing, real store slides in the
hero and the gallery, and the install bar / back-to-top chrome wrapped in
tools/build-ux.py's BEGIN/END markers so that builder replaces it rather than
appending a copy.

The folder is /steptell/ in lower case because the shipped app (Settings >
About, the consent page) and the Store listing link to dhinovatech.com/steptell,
/steptell/privacy and /steptell/support. This builder writes index.html files
only; privacy.html and support.html are hand-ported from the app repo.

The copy comes from two files:

  * tools/steptell-listing.json - the store listing's own translated text
    (localized title, short description, description, feature bullets, slide
    captions) and the words on the store slides, refreshed from the app
    repository by tools/build-steptell-shots.py.
  * tools/steptell-strings.json - what is written for this page: the
    at-a-glance facts, the Steps Recorder replacement argument and comparison,
    the three steps, who it is for, the privacy and IT details the listing has
    no room for, pricing, and the FAQ. Every claim was checked against the app
    repo's docs/REQUIREMENTS.md, DECISIONS.md and PROGRESS.md (verified items
    only) on 2026-11-01.

Steps Recorder facts (comparison table, FAQ) follow Microsoft's deprecation
notice: psr.exe "is no longer being updated and will be removed in a future
release of Windows", with Snipping Tool, Xbox Game Bar and Clipchamp
suggested for screen recording. Do not give a removal date.

Every feature is free. Free exports carry a small "Created with Steptell"
label on images; Steptell Pro (one-time Durable add-on) removes it or puts the
user's logo there, and a 24-hour pass does the same for a day. Localized
listings print no price (app repo DECISIONS D-020), so neither does the page;
the Offer in the structured data is the app's own price, 0.

Store links are ordinary https://apps.microsoft.com/detail/... URLs so they
work everywhere and stay crawlable; assets/js/ux.js upgrades them to
ms-windows-store:// in place when the visitor is on Windows.

Run:  python tools/build-steptell.py
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


S = _load("steptell-strings.json")
LISTING = _load("steptell-listing.json")
CONSENT_L = _load("consent-strings.json")

SECTION = "steptell"
SITE = "https://www.dhinovatech.com"
STORE_ID = "9MWWT8XPVF5K"
STORE = "https://apps.microsoft.com/detail/" + STORE_ID
STORE_UTM = STORE + "?ocid=dhinovatech_steptell"

ICON = "/assets/images/steptell-icon.png"
ICON_WEBP = "/assets/images/steptell-icon.webp"
PRIVACY = "/steptell/privacy.html"
SUPPORT = "/steptell/support.html"
# When the page's copy last changed in substance; the WebPage schema reports it.
MODIFIED = "2026-11-01"
OGIMG = "/assets/images/steptell-og.png"
OGW, OGH = 1200, 630
OGALT = "Steptell - steps recorder and how-to guide maker for Windows, all features free on the Microsoft Store"

# The store slides tools/build-steptell-shots.py writes. "hero" is slide 1; the
# other eight are slides 3-10, in the order of listing "shots" (and of
# listing "captions"[2:]).
HERO = "hero"
SHOTS = ["record", "edit", "privacy", "export", "guide", "report", "private", "languages"]
SHOT_W, SHOT_H = 1200, 675
SHOT_ICONS = ["bi-record-circle", "bi-pencil-square", "bi-eye-slash", "bi-box-arrow-up-right",
              "bi-file-earmark-richtext", "bi-bug", "bi-shield-lock", "bi-translate"]
# The ten overview tiles of store slide 2, keyed by the kit's own icon names.
TILE_ICONS = {"record": "bi-record-circle", "steps": "bi-list-ol", "annotate": "bi-pencil-square",
              "blur": "bi-eye-slash", "keyboard": "bi-keyboard", "export": "bi-box-arrow-up-right",
              "report": "bi-bug", "offline": "bi-cloud-slash", "import": "bi-file-earmark-arrow-down",
              "languages": "bi-translate"}
CHIP_ICONS = ["bi-arrow-repeat text-info", "bi-eye-slash text-warning",
              "bi-cloud-slash text-success", "bi-file-earmark-pdf text-danger"]
USE_ICONS = ["bi-bug", "bi-journal-check", "bi-mortarboard", "bi-clipboard2-check",
             "bi-briefcase", "bi-backpack"]
# Format names are the same in every language.
FORMATS = ["Word (.docx)", "PDF", "PowerPoint (.pptx)", "HTML", "Markdown", "PNG / JPEG",
           "GIF", "MP4", "SCORM", "XLIFF", "JSON", ".steptell", "ZIP"]

# How Steptell and Steps Recorder fare on each row of the comparison, the same
# in every language: y = yes, p = partly, n = no. Rows follow t["cmp_rows"].
CMP_MARKS = [
    "yy",   # records every click with a screenshot
    "yp",   # step sentence (Steps Recorder: Windows display language only)
    "yn",   # edit, reorder, merge, split
    "yn",   # annotations
    "yn",   # blur
    "yp",   # export formats (Steps Recorder: one ZIP with an MHT file)
    "yy",   # problem report ZIP
    "yn",   # still updated
    "yy",   # price
]
MARK_ICON = {"y": "bi-check-circle-fill peer-y", "p": "bi-dash-circle-fill peer-p",
             "n": "bi-x-circle-fill peer-n"}

# Strings keys that are the same in every language, so only "en" carries them.
SAME_IN_ALL = {"quota_num", "cmp_us"}

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

# (code, menu label, dir, hreflang, og locale) - the app's 25 languages.
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
    ("ro", "Română (Romanian)", "ltr", "ro", "ro_RO"),
    ("da", "Dansk (Danish)", "ltr", "da", "da_DK"),
    ("sv", "Svenska (Swedish)", "ltr", "sv", "sv_SE"),
    ("nb", "Norsk (Norwegian)", "ltr", "nb", "nb_NO"),
    ("fi", "Suomi (Finnish)", "ltr", "fi", "fi_FI"),
    ("uk", "Українська (Ukrainian)", "ltr", "uk", "uk_UA"),
    ("tr", "Türkçe (Turkish)", "ltr", "tr", "tr_TR"),
    ("ja", "日本語 (Japanese)", "ltr", "ja", "ja_JP"),
    ("ko", "한국어 (Korean)", "ltr", "ko", "ko_KR"),
    ("zh", "简体中文 (Simplified Chinese)", "ltr", "zh-Hans", "zh_CN"),
    ("zh-tw", "繁體中文 (Traditional Chinese)", "ltr", "zh-Hant", "zh_TW"),
    ("th", "ไทย (Thai)", "ltr", "th", "th_TH"),
    ("vi", "Tiếng Việt (Vietnamese)", "ltr", "vi", "vi_VN"),
    ("id", "Bahasa Indonesia (Indonesian)", "ltr", "id", "id_ID"),
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
    rel = "assets/images/steptell/%s/%s.webp" % (code, slug)
    if code != "en" and not os.path.exists(os.path.join(ROOT, rel)):
        rel = "assets/images/steptell/en/%s.webp" % slug
    return "/" + rel


def built_langs():
    return [x for x in LANGS if x[0] in LISTING]


def para(lst, n):
    """Store description paragraph n without its heading line."""
    return lst["description"][n].split("\n", 1)[1].strip()


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
# Shared navigation - Steptell owns its own language tree.
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

          <!-- Our Apps - Steptell owns its own language tree; build-nav-apps.py
               adds Smart Photos and KeepOne above it -->
          <li class="nav-item dropdown">
            <a class="nav-link nav-link-custom dropdown-toggle active" href="#" id="appsDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
              Our Apps
            </a>
            <ul class="dropdown-menu dropdown-menu-dark border-secondary shadow-lg mt-2" aria-labelledby="appsDropdown">
              <li class="dropdown-submenu position-relative">
                <a class="dropdown-item py-2 d-flex align-items-center justify-content-between" href="/steptell/">
                  <span><img src="__ICON__" alt="Steptell Icon" style="width: 20px; height: 20px; border-radius: 5px; object-fit: cover;" class="me-2" decoding="async" width="256" height="256">Steptell Steps Recorder</span>
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

          <!-- Language Selector - Steptell only -->
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
            Dhinovatech designs and engineers high-performance, privacy-first mobile &amp; desktop apps available on Google Play and Microsoft Store.
          </p>
        </div>
        <div class="col-lg-2 col-6">
          <h4 class="h6 text-white fw-bold mb-3">Company</h4>
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
            <li><a href="/steptell/" class="footer-link text-primary fw-semibold"><i class="bi bi-record-circle me-1" aria-hidden="true"></i> Steptell Steps Recorder</a></li>
            <li><a href="/smart-photos/" class="footer-link"><i class="bi bi-images me-1" aria-hidden="true"></i> Smart Photos</a></li>
            <li><a href="/KeepOne/" class="footer-link"><i class="bi bi-intersect me-1" aria-hidden="true"></i> KeepOne Duplicate Finder</a></li>
            <li><a href="/nudge/" class="footer-link"><i class="bi bi-journal-bookmark-fill me-1" aria-hidden="true"></i> Nudge Offline Journal &amp; AI</a></li>
            <li><a href="/stow/" class="footer-link"><i class="bi bi-folder-symlink me-1" aria-hidden="true"></i> Stow Photo &amp; File Organizer</a></li>
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
          <p class="small text-secondary mb-2"><i class="bi bi-globe me-2 text-primary" aria-hidden="true"></i>www.dhinovatech.com</p>
          <p class="small mb-2"><a href="/steptell/support.html" class="footer-link"><i class="bi bi-life-preserver me-2 text-primary" aria-hidden="true"></i>Steptell Support</a></p>
          <p class="small mb-0"><a href="/steptell/privacy.html" class="footer-link"><i class="bi bi-shield-check me-2 text-primary" aria-hidden="true"></i>Steptell Privacy Policy</a></p>
        </div>
      </div>
      <div class="pt-4 border-top border-secondary text-center text-secondary small">
        <p class="mb-0">&copy; 2026 Dhinovatech. All rights reserved.</p>
      </div>
    </div>
  </footer>
"""

# Same structure as the KeepOne and Smart Photos pages, re-keyed to the amber
# and royal blue of the Steptell store slides ("ALL FEATURES FREE" is amber on
# slide 1). The custom properties are declared site-wide in custom.css, so
# re-declaring them here re-keys the shared chrome for this section only.
# Blue stays reserved for the Microsoft Store buttons (.btn-primary,
# .btn-store-ms are not touched).
PAGE_CSS = """  <style>
    :root {
      --dhin-accent-blue: #ffc23d;
      --dhin-border-glow: rgba(255, 194, 61, 0.32);
      --dhin-shadow-glow: 0 0 25px rgba(255, 194, 61, 0.18);
      --dhin-gradient-primary: linear-gradient(135deg, #ffc23d 0%, #3d6df2 100%);
      --st-amber: #ffc23d;
      --st-blue: #3d6df2;
      --st-ink: #10122a;
    }
    :root, [data-bs-theme="dark"] {
      --bs-primary-rgb: 255, 194, 61;
      --bs-primary-bg-subtle: rgba(255, 194, 61, 0.12);
      --bs-primary-border-subtle: rgba(255, 194, 61, 0.32);
      --bs-primary-text-emphasis: #ffdc8a;
    }
    .text-gradient {
      background: linear-gradient(135deg, #ffe3a3 0%, #ffc23d 50%, #ff9f43 100%);
      -webkit-background-clip: text;
      background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .btn-dhin-primary { box-shadow: 0 4px 15px rgba(255, 194, 61, 0.24); }
    .btn-dhin-primary:hover { box-shadow: 0 8px 25px rgba(255, 194, 61, 0.38); }
    .btn-dhin-outline:hover { background: rgba(255, 194, 61, 0.1); }
    .hero-section {
      padding: 56px 0 64px;
      background: radial-gradient(circle at 22% 18%, rgba(61, 109, 242, 0.28) 0%, rgba(8, 12, 20, 0) 62%);
    }
    @media (max-width: 991.98px) { .hero-section { padding: 32px 0 48px; } }
    .hero-title { overflow-wrap: anywhere; }

    .glow-aura-blue { box-shadow: 0 0 45px rgba(61, 109, 242, 0.3); }
    .st-icon-box {
      width: 52px; height: 52px; border-radius: 14px;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.4rem; flex-shrink: 0;
      background: linear-gradient(135deg, rgba(255,194,61,0.16), rgba(61,109,242,0.16));
      color: var(--st-amber); border: 1px solid rgba(255,194,61,0.3);
    }
    .st-icon-box-sm { width: 38px; height: 38px; font-size: 1.1rem; border-radius: 10px; }
    .st-badge-row { display: flex; flex-wrap: wrap; gap: .5rem; }
    .st-step {
      width: 42px; height: 42px; border-radius: 50%; flex-shrink: 0;
      display: flex; align-items: center; justify-content: center;
      font-weight: 800; font-size: 1.1rem;
      background: rgba(255,194,61,0.16); color: var(--st-amber);
      border: 1px solid rgba(255,194,61,0.4);
    }

    /* Hero */
    .st-hero-icon { width: 60px; height: 60px; flex-shrink: 0; }
    .st-hero-icon img { width: 100%; height: 100%; object-fit: contain; display: block; }
    .st-hero-kind { font-weight: 600; color: #e2e8f0; font-size: .95rem; line-height: 1.3; }
    .st-hero-tagline {
      font-size: clamp(1.15rem, 1rem + 0.8vw, 1.6rem); font-weight: 500;
      line-height: 1.35; letter-spacing: 0; color: #ffdc8a; margin-top: .6rem;
    }
    .st-cta-strip .st-price { margin: 0; }
    .st-price {
      display: flex; align-items: center; gap: .5rem; flex-wrap: wrap;
      font-size: .92rem; color: #cbd5e1;
    }
    .st-price-tag {
      background: var(--st-amber); color: var(--st-ink);
      border-radius: 20px; padding: 3px 14px; font-size: .95rem; font-weight: 800;
      white-space: nowrap; text-decoration: none;
      box-shadow: 0 0 18px rgba(255, 194, 61, .3);
    }
    .st-price-tag:hover { color: var(--st-ink); background: #ffd36e; }
    .st-window {
      border-radius: 14px; overflow: hidden; background: #0d1d5a;
      border: 1px solid rgba(255,255,255,.12);
      box-shadow: 0 30px 70px -25px rgba(0,0,0,.9);
    }
    .st-window img { display: block; width: 100%; height: auto; }

    .st-narrow { max-width: 760px; }

    /* At a glance */
    .st-glance-def { font-size: 1.1rem; color: #e2e8f0; line-height: 1.6; }
    .st-facts { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 0; margin: 0; }
    .st-fact { padding: 1rem 1.1rem; border-top: 1px solid rgba(255,255,255,.08); }
    .st-fact dt { font-size: .75rem; text-transform: uppercase; letter-spacing: .06em; color: var(--st-amber); font-weight: 700; margin-bottom: .3rem; }
    .st-fact dd { margin: 0; font-size: .92rem; color: #cbd5e1; }

    /* Screenshot gallery */
    .st-shot { overflow: hidden; margin: 0; }
    .st-shot img { display: block; width: 100%; height: auto; border-bottom: 1px solid rgba(255,255,255,.07); }
    .st-shot figcaption { padding: 1rem 1.1rem 1.1rem; }
    .st-shot-kicker { font-size: .72rem; letter-spacing: .08em; font-weight: 700; color: var(--st-amber); text-transform: uppercase; }
    .st-shot-title { font-size: 1.02rem; font-weight: 700; color: #fff; margin: .25rem 0 .6rem; }

    /* Cards */
    .invariant-card { border-left: 3px solid var(--st-amber) !important; transition: transform .2s ease, box-shadow .2s ease; }
    [dir="rtl"] .invariant-card { border-left: 0 !important; border-right: 3px solid var(--st-amber) !important; }
    .invariant-card:hover { transform: translateY(-3px); box-shadow: 0 10px 30px rgba(255, 194, 61, 0.1); }
    .pillar-card { transition: transform .2s ease, border-color .2s ease; }
    .pillar-card:hover { transform: translateY(-3px); border-color: rgba(255, 194, 61, 0.4) !important; }
    .st-check-list li { display: flex; gap: .6rem; margin-bottom: .6rem; font-size: .9rem; color: #cbd5e1; }
    .st-check-list li i { color: var(--st-amber); flex-shrink: 0; margin-top: .1rem; }
    .st-format {
      display: inline-flex; align-items: center; gap: .4rem;
      padding: .45rem .9rem; border-radius: 999px; font-size: .88rem; font-weight: 600;
      background: rgba(61,109,242,.14); border: 1px solid rgba(61,109,242,.38); color: #dbe5ff;
    }
    .st-format i { color: var(--st-amber); }

    /* Steptell vs Steps Recorder */
    .peer-table { font-size: .9rem; border-collapse: separate; border-spacing: 0; }
    .peer-table th, .peer-table td { padding: .8rem .85rem; border-bottom: 1px solid rgba(255,255,255,.07); vertical-align: top; min-width: 150px; }
    .peer-table thead th { background: rgba(17, 24, 39, .95); color: #94a3b8; font-weight: 600; }
    .peer-table th.st-col, .peer-table td.st-col { background: rgba(255, 194, 61, .07); border-left: 1px solid rgba(255,194,61,.25); border-right: 1px solid rgba(255,194,61,.25); }
    .peer-table thead th.st-col { color: var(--st-amber); border-top: 2px solid var(--st-amber); }
    .peer-table tbody th { min-width: 170px; font-weight: 600; }
    .peer-cell { display: flex; gap: .45rem; align-items: flex-start; }
    .peer-cell i { flex-shrink: 0; margin-top: .15rem; }
    .peer-y { color: #34d399; }
    .peer-p { color: var(--st-amber); }
    .peer-n { color: #f87171; }

    /* Pricing */
    .st-plan { display: flex; flex-direction: column; border: 1px solid rgba(255,255,255,.1) !important; }
    .st-plan-free { border: 2px solid var(--st-amber) !important; box-shadow: 0 0 40px rgba(255, 194, 61, .14); }
    .st-plan-price { font-size: 2.6rem; font-weight: 800; line-height: 1.1; color: var(--st-amber); }
    .st-plan-price-sm { font-size: 1.15rem; font-weight: 600; color: #e2e8f0; line-height: 1.4; min-height: 2.6rem; display: flex; align-items: center; }
    .st-plan-opt { background: rgba(255,255,255,.08); color: #cbd5e1; font-size: .72rem; font-weight: 600; }
    .st-quota {
      display: flex; align-items: center; gap: .9rem;
      padding: .9rem 1.1rem; border-radius: 14px;
      background: rgba(255, 194, 61, .1); border: 1px solid rgba(255, 194, 61, .38);
    }
    .st-quota-num { font-size: 2.2rem; font-weight: 800; line-height: 1; color: var(--st-amber); flex-shrink: 0; }
    .st-quota-label { font-weight: 700; color: #fff; line-height: 1.3; }
    .st-quota-pro { background: rgba(61, 109, 242, .1); border-color: rgba(61, 109, 242, .38); }
    .st-quota-pro .st-quota-num { color: #8fb0ff; }

    /* FAQ */
    .accordion-button:not(.collapsed) { background: rgba(255, 194, 61, 0.08); color: var(--st-amber); box-shadow: none; }
    .accordion-button:focus { box-shadow: 0 0 0 0.2rem rgba(255, 194, 61, 0.25); }
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
         "@id": SITE + "/steptell/#software",
         "name": "Steptell",
         "alternateName": lst["title"],
         "operatingSystem": "Windows 10 version 22H2 (build 19045) and later, Windows 11",
         "applicationCategory": "BusinessApplication",
         "applicationSubCategory": "Steps recorder and how-to guide maker",
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
         "memoryRequirements": "8 GB RAM",
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD",
                    "availability": "https://schema.org/InStock", "url": STORE},
         "screenshot": [SITE + shot_url(code, s) for s in [HERO] + SHOTS],
         "publisher": {"@id": SITE + "/#organization"},
         "author": {"@id": SITE + "/#organization"}},
        {"@type": "WebPage", "@id": abs_url(code) + "#webpage", "url": abs_url(code),
         "name": title, "description": desc, "inLanguage": BY_CODE[code][3],
         "dateModified": MODIFIED, "about": {"@id": SITE + "/steptell/#software"},
         "mainEntity": {"@id": SITE + "/steptell/#software"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Steptell", "item": abs_url("en")},
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
             "name": "Steptell (%s)" % code, "item": abs_url(code)})
    return json.dumps({"@context": "https://schema.org", "@graph": graph},
                      ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


# ---------------------------------------------------------------- sections

def eyebrow(icon, text):
    return ('<span class="badge bg-primary-subtle text-primary border border-primary-subtle '
            'rounded-pill px-3 py-2 fw-semibold mb-2"><i class="bi %s me-1" aria-hidden="true">'
            '</i> %s</span>' % (icon, E(text)))


def section_head(icon, eb, h, sub):
    return """      <div class="text-center mx-auto mb-5 st-narrow">
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
    """The descriptor of the localized title ("Steps Recorder & Guide Maker").

    Each language's title was written from that market's measured Store
    searches (the native name Windows gives Steps Recorder plus the common
    how-to phrase), so the hero shows it rather than a second, invented one.
    """
    title = lst["title"]
    for sep in (": ", " : ", " - ", " – "):
        if title.startswith("Steptell" + sep):
            return title[len("Steptell" + sep):]
    return lst["kind"]


def check_items(rows, indent="              "):
    return "\n".join(
        '%s<li><i class="bi bi-check2-circle" aria-hidden="true"></i><span>%s</span></li>'
        % (indent, E(r)) for r in rows)


def render_price(lst, centred=False):
    return ('<p class="st-price mt-3 mb-0%s"><a class="st-price-tag" href="#pricing">'
            '<i class="bi bi-unlock-fill me-1" aria-hidden="true"></i>%s</a>'
            '<span>%s</span></p>'
            % (" justify-content-center" if centred else "",
               E(lst["free"]), E(lst["free_sub"])))


def cta_strip(t, lst):
    """The store button again, where a reader who is convinced looks for it."""
    return """      <div class="st-cta-strip d-flex flex-column flex-md-row align-items-center justify-content-center gap-3 mt-5">
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
            <span class="st-hero-icon">
              <img src="%(icon)s" alt="" decoding="async" width="256" height="256">
            </span>
            <span>
              <span class="d-block st-hero-kind">%(kind)s</span>
              <span class="d-block small text-secondary">
                <i class="bi bi-microsoft me-1" aria-hidden="true"></i>Microsoft Store &middot; Windows 10 &amp; 11
              </span>
            </span>
          </div>

          <h1 class="hero-title mb-3"><span class="d-block">Steptell</span> <span class="d-block st-hero-tagline">%(h1)s</span></h1>
          <p class="lead text-secondary mb-4 pe-lg-4 fs-5">%(lead)s</p>

          <div class="d-flex flex-wrap gap-3 align-items-center">
            %(store)s
            <a href="#screenshots" class="btn btn-dhin-outline btn-lg rounded-pill px-4">
              <i class="bi bi-images me-2" aria-hidden="true"></i> %(cta_see)s
            </a>
          </div>
          %(price)s

          <div class="st-badge-row pt-4 mt-2">
%(badges)s
          </div>
        </div>

        <div class="col-lg-6">
          <div class="position-relative">
            <div class="position-absolute top-50 start-50 translate-middle w-100 h-100 rounded-circle bg-primary opacity-25 blur-3xl glow-aura-blue" aria-hidden="true"></div>
            <div class="st-window position-relative">
              <img src="%(hero)s" alt="%(hero_alt)s" decoding="async" fetchpriority="high" width="%(w)d" height="%(h)d">
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
""" % dict(icon=ICON_WEBP, kind=E(store_kind(lst)),
           h1=E("%s %s" % (lst["line1"], lst["line2"])), lead=E(lst["short"]),
           store=store_button(t), cta_see=E(t["shots"]), price=render_price(lst),
           badges=badges, hero=shot_url(code, HERO), hero_alt=E(lst["captions"][0]),
           w=SHOT_W, h=SHOT_H)


def render_glance(t, lst):
    """One definition sentence and the key facts, as a description list.

    Written to be quoted: search snippets and AI answers lift a page's own
    plain statement of what a thing is, what it costs and what it needs far
    more readily than they assemble one from marketing copy. The definition is
    the store description's opening sentence, already keyword-tuned per market.
    """
    facts = "\n".join(
        '            <div class="st-fact"><dt>%s</dt><dd>%s</dd></div>' % (E(k), E(v))
        for k, v in t["glance"])
    return """  <!-- At a glance -->
  <section class="py-5 border-top border-secondary-subtle" id="at-a-glance">
    <div class="container py-3">
      <div class="row justify-content-center">
        <div class="col-lg-10">
          <h2 class="h3 text-white fw-bold mb-3"><i class="bi bi-info-circle text-primary me-2" aria-hidden="true"></i>%s</h2>
          <p class="st-glance-def mb-4">%s</p>
          <dl class="st-facts card card-glass border border-secondary-subtle overflow-hidden">
%s
          </dl>
        </div>
      </div>
    </div>
  </section>
""" % (E(t["glance_h"]), E(lst["description"][0]), facts)


def render_overview(lst):
    """Store slide 2 as real text: everything included, all free."""
    ov = lst["overview"]
    tiles = []
    for key, name, what in ov["tiles"]:
        tiles.append("""        <div class="col-xl-4 col-md-6">
          <div class="card card-glass h-100 p-4 pillar-card border border-secondary-subtle">
            <div class="d-flex align-items-center gap-3 mb-2">
              <span class="st-icon-box st-icon-box-sm"><i class="bi %s" aria-hidden="true"></i></span>
              <h3 class="h6 text-white fw-bold mb-0">%s</h3>
            </div>
            <p class="text-secondary small mb-0">%s</p>
          </div>
        </div>""" % (TILE_ICONS.get(key, "bi-check2-circle"), E(name), E(what)))
    return """  <!-- Overview -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="overview">
    <div class="container py-4">
%s
      <p class="text-secondary text-center mx-auto mb-5 st-narrow">%s %s</p>
      <div class="row g-4 justify-content-center">
%s
      </div>
    </div>
  </section>
""" % (section_head("bi-stars", lst["free"], ov["title"], ov["sub"]),
       E(lst["description"][1]), E(lst["description"][2]), "\n".join(tiles))


def render_gallery(code, t, lst):
    cards = []
    for i, (slug, icon) in enumerate(zip(SHOTS, SHOT_ICONS)):
        shot = lst["shots"][i]
        cap = lst["captions"][i + 2]
        cards.append("""        <div class="col-md-6">
          <figure class="card card-glass st-shot h-100">
            <img src="%s" alt="%s" loading="lazy" decoding="async" width="%d" height="%d">
            <figcaption>
              <div class="st-shot-kicker"><i class="bi %s me-1" aria-hidden="true"></i>%s</div>
              <h3 class="st-shot-title mb-0">%s</h3>
            </figcaption>
          </figure>
        </div>""" % (shot_url(code, slug), E(cap), SHOT_W, SHOT_H, icon, E(shot["kicker"]),
                     E(shot["title"])))
    return """  <!-- Screenshots -->
  <section class="py-5" id="screenshots">
    <div class="container py-4">
%s
      <div class="row g-4">
%s
      </div>
%s    </div>
  </section>
""" % (section_head("bi-images", t["shots"], t["shots_h"], ""), "\n".join(cards),
       cta_strip(t, lst))


def render_psr(t, lst):
    """Why switch: Steps Recorder is deprecated, and how Steptell compares."""
    head = "\n".join([
        '                <th scope="col">%s</th>' % E(t["cmp_feature"]),
        '                <th scope="col" class="st-col">%s</th>' % E(t["cmp_us"]),
        '                <th scope="col">%s</th>' % E(t["cmp_them"]),
    ])
    rows = []
    for marks, row in zip(CMP_MARKS, t["cmp_rows"]):
        cells = ['                  <th scope="row" class="text-white">%s</th>' % E(row[0])]
        for i, (m, cell) in enumerate(zip(marks, row[1:])):
            cells.append('                  <td%s><span class="peer-cell"><i class="bi %s" aria-hidden="true"></i>'
                         '<span class="%s">%s</span></span></td>'
                         % (' class="st-col"' if i == 0 else "", MARK_ICON[m],
                            "text-white fw-semibold" if i == 0 else "text-secondary", E(cell)))
        rows.append("                <tr>\n%s\n                </tr>" % "\n".join(cells))
    return """  <!-- Steps Recorder replacement -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="steps-recorder">
    <div class="container py-4">
%s
      <div class="st-narrow mx-auto mb-5">
        <p class="text-secondary fs-5">%s</p>
        <p class="text-white fs-5 mb-0">%s</p>
      </div>
      <h3 class="h4 text-white fw-bold text-center mb-4" id="compare">%s</h3>
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
      <div class="card card-glass p-4 mt-4 border border-primary border-opacity-25">
        <div class="d-flex gap-3 align-items-start">
          <span class="st-icon-box st-icon-box-sm"><i class="bi bi-file-earmark-arrow-down" aria-hidden="true"></i></span>
          <p class="text-secondary mb-0">%s</p>
        </div>
      </div>
      <p class="extra-small text-secondary text-center mt-3 mb-0">%s</p>
    </div>
  </section>
""" % (section_head("bi-arrow-repeat", t["psr_eb"], t["psr_h"], ""),
       E(t["psr_p1"]), E(t["psr_p2"]), E(t["cmp_h"]), head, "\n".join(rows),
       E(para(lst, 7)), E(lst["description"][9]))


def render_steps(t, lst):
    steps = []
    for n, s in enumerate(t["steps"], 1):
        steps.append("""        <div class="col-md-4">
          <div class="card card-glass h-100 p-4">
            <div class="d-flex align-items-center gap-3 mb-2">
              <div class="st-step">%d</div>
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


def render_uses(t):
    cards = []
    for icon, c in zip(USE_ICONS, t["use_cards"]):
        cards.append("""        <div class="col-lg-4 col-md-6">
          <div class="card card-glass h-100 p-4 pillar-card border border-secondary-subtle">
            <span class="st-icon-box mb-3"><i class="bi %s" aria-hidden="true"></i></span>
            <h3 class="h6 text-white fw-bold mb-2">%s</h3>
            <p class="text-secondary small mb-0">%s</p>
          </div>
        </div>""" % (icon, E(c["t"]), E(c["d"])))
    return """  <!-- Who it is for -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="use-cases">
    <div class="container py-4">
%s
      <div class="row g-4">
%s
      </div>
    </div>
  </section>
""" % (section_head("bi-people", t["use_eb"], t["use_h"], ""), "\n".join(cards))


def render_privacy(code, t, lst):
    half = (len(t["priv_items"]) + 1) // 2
    cols = []
    for chunk in (t["priv_items"][:half], t["priv_items"][half:]):
        cols.append("""          <div class="col-md-6">
            <ul class="list-unstyled st-check-list mb-0">
%s
            </ul>
          </div>""" % check_items(chunk))
    return """  <!-- Private by design -->
  <section class="py-5" id="privacy">
    <div class="container py-4">
%s
      <div class="card card-glass p-4 p-md-5 invariant-card">
        <p class="text-white mb-4">%s</p>
        <div class="row g-3 mb-3">
%s
        </div>
        <a class="small" href="%s"><i class="bi bi-shield-check me-1" aria-hidden="true"></i>%s</a>
      </div>
    </div>
  </section>
""" % (section_head("bi-shield-lock", t["priv_eb"], t["priv_h"], t["priv_sub"]),
       E(para(lst, 5)), "\n".join(cols), PRIVACY, E(privacy_label(code)))


def render_export(t, lst):
    chips = "\n".join('          <span class="st-format"><i class="bi bi-file-earmark" aria-hidden="true"></i>%s</span>'
                      % E(f) for f in FORMATS)
    return """  <!-- Export anywhere -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="export">
    <div class="container py-4">
%s
      <div class="d-flex flex-wrap justify-content-center gap-2 mx-auto mb-5" style="max-width: 900px;">
%s
      </div>
      <div class="row g-4">
        <div class="col-lg-6">
          <div class="card card-glass h-100 p-4 invariant-card">
            <div class="d-flex align-items-center gap-3 mb-3">
              <span class="st-icon-box st-icon-box-sm"><i class="bi bi-file-earmark-richtext" aria-hidden="true"></i></span>
              <h3 class="h6 text-white fw-bold mb-0">%s</h3>
            </div>
            <p class="text-secondary small mb-0">%s</p>
          </div>
        </div>
        <div class="col-lg-6">
          <div class="card card-glass h-100 p-4 invariant-card">
            <div class="d-flex align-items-center gap-3 mb-3">
              <span class="st-icon-box st-icon-box-sm"><i class="bi bi-bug" aria-hidden="true"></i></span>
              <h3 class="h6 text-white fw-bold mb-0">%s</h3>
            </div>
            <p class="text-secondary small mb-0">%s</p>
          </div>
        </div>
      </div>
    </div>
  </section>
""" % (section_head("bi-box-arrow-up-right", t["exp_eb"], t["exp_h"], para(lst, 6)), chips,
       E(t["use_cards"][1]["t"]), E(para(lst, 4)), E(t["use_cards"][0]["t"]), E(para(lst, 3)))


def render_it(t):
    return """  <!-- For IT -->
  <section class="py-5" id="it">
    <div class="container py-4">
%s
      <div class="card card-glass p-4 p-md-5 border border-primary border-opacity-25 mx-auto" style="max-width: 900px;">
        <ul class="list-unstyled st-check-list mb-0">
%s
        </ul>
      </div>
    </div>
  </section>
""" % (section_head("bi-building-gear", t["it_eb"], t["it_h"], ""),
       check_items(t["it_items"], "          "))


def render_pricing(t, lst):
    """Everything free; Pro only removes the label on exported images.

    No price: the localized listings print none (app repo DECISIONS D-020),
    the Store sets it per market, and the app shows the live one.
    """
    return """  <!-- Pricing -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="pricing">
    <div class="container py-4">
%s
      <div class="row justify-content-center g-4">
        <div class="col-md-6 col-lg-5">
          <div class="card card-glass h-100 p-4 p-lg-5 st-plan st-plan-free">
            <h3 class="h5 text-white fw-bold mb-1">%s</h3>
            <p class="st-plan-price mb-3">%s</p>
            <div class="st-quota mb-4">
              <span class="st-quota-num">%s</span>
              <span class="st-quota-label">%s</span>
            </div>
            <ul class="list-unstyled st-check-list mb-4">
%s
            </ul>
            <div class="mt-auto">%s</div>
          </div>
        </div>
        <div class="col-md-6 col-lg-5">
          <div class="card card-glass h-100 p-4 p-lg-5 st-plan">
            <h3 class="h5 text-white fw-bold mb-1">%s <span class="badge rounded-pill st-plan-opt align-middle ms-1">%s</span></h3>
            <p class="st-plan-price st-plan-price-sm mb-3">%s</p>
            <div class="st-quota st-quota-pro mb-4">
              <span class="st-quota-num"><i class="bi bi-patch-check" aria-hidden="true"></i></span>
              <span class="st-quota-label">%s</span>
            </div>
            <ul class="list-unstyled st-check-list mb-0">
%s
            </ul>
          </div>
        </div>
      </div>
      <p class="text-secondary small text-center mx-auto mt-4 mb-2 st-narrow">%s</p>
      <p class="text-secondary small text-center mx-auto mb-0 st-narrow">%s</p>
    </div>
  </section>
""" % (section_head("bi-unlock-fill", t["price_eb"], t["price_h"], t["price_sub"]),
       E(t["free_title"]), E(t["free_price"]), E(t["quota_num"]), E(t["quota_label"]),
       check_items(t["free_items"]), store_button(t),
       E(t["pro_title"]), E(t["pro_badge"]), E(t["pro_price"]), E(t["pro_label"]),
       check_items(t["pro_items"]), E(para(lst, 8)), E(t["price_fine"]))


def render_features(t, lst):
    feats = lst["features"]
    half = (len(feats) + 1) // 2
    cols = []
    for chunk in (feats[:half], feats[half:]):
        cols.append("""          <div class="col-md-6">
            <ul class="list-unstyled st-check-list mb-0">
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
              <div id="faq%d" class="accordion-collapse collapse%s" aria-labelledby="faq%dHeading" data-bs-parent="#steptellFaqAccordion">
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
          <div class="accordion accordion-flush" id="steptellFaqAccordion">
%s
          </div>
        </div>
      </div>
    </div>
  </section>
""" % (section_head("bi-question-circle", t["faq_eb"], t["faq_h"], ""), "\n".join(items))


def render_final(t, lst):
    return """  <!-- Final CTA -->
  <section class="py-5">
    <div class="container py-4">
      <div class="card card-glass p-5 text-center border-0 position-relative overflow-hidden" style="background: linear-gradient(135deg, rgba(61,109,242,0.18) 0%%, rgba(255,194,61,0.08) 100%%);">
        <div class="st-narrow mx-auto position-relative" style="z-index: 2;">
          <div class="mx-auto mb-3" style="width: 90px; height: 90px;">
            <img src="%s" alt="Steptell Icon" class="w-100 h-100 object-fit-contain" loading="lazy" decoding="async" width="256" height="256">
          </div>
          <h2 class="display-6 fw-bold text-white mb-3">%s</h2>
          <p class="text-secondary fs-5 mb-4">%s</p>
          <div class="d-flex justify-content-center">
            %s
          </div>
          %s
          <p class="small mt-4 mb-0"><a href="%s"><i class="bi bi-life-preserver me-1" aria-hidden="true"></i>Steptell support</a></p>
        </div>
      </div>
    </div>
  </section>
""" % (ICON_WEBP, E("%s %s" % (lst["line1"], lst["line2"])), E(lst["short"]),
       store_button(t), render_price(lst, True), SUPPORT)


def build(code):
    t = dict(S["en"])
    t.update(S.get(code, {}))
    lst = LISTING[code]
    _c, _label, direction, hl, og = BY_CODE[code]
    title = t["seo_title"]
    desc = lst["short"]

    og_alts = "\n".join('  <meta property="og:locale:alternate" content="%s">' % o
                        for c2, _l, _d, _h, o in built_langs() if c2 != code)

    body = "\n".join([
        render_hero(code, t, lst),
        # What it is and what it costs, stated plainly; then everything it
        # does; then what it looks like; then why switch, how, and for whom.
        render_glance(t, lst),
        render_overview(lst),
        render_gallery(code, t, lst),
        render_psr(t, lst),
        render_steps(t, lst),
        render_uses(t),
        render_privacy(code, t, lst),
        render_export(t, lst),
        render_it(t),
        render_pricing(t, lst),
        render_features(t, lst),
        render_faq(t),
        render_final(t, lst),
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
<!-- Navigation Bar (independent Steptell tree) -->
{navbar}
<main id="main">

{body}
</main>
{footer}
  <!-- Bootstrap 5.3 JS Bundle -->
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
  <script src="/assets/js/nav.js"></script>

  <!-- BEGIN generated UX block -->
  <div class="install-bar" role="complementary" aria-label="Steptell">
    <img src="{icon}" alt="" width="42" height="42" loading="lazy" decoding="async">
    <div class="install-bar-text">
      <div class="install-bar-title">Steptell</div>
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
    if len(lst["description"]) != 10:
        problems.append("description has %d paragraphs, expected 10" % len(lst["description"]))
    else:
        problems += ["description paragraph %d has no heading line" % n
                     for n in range(3, 9) if "\n" not in lst["description"][n]]
    for key, n in (("cmp_rows", len(CMP_MARKS)), ("steps", 3), ("use_cards", len(USE_ICONS))):
        if len(t[key]) != n:
            problems.append("%s has %d items, expected %d" % (key, len(t[key]), n))
    if len(lst["shots"]) != len(SHOTS) or len(lst["captions"]) != 10:
        problems.append("listing shots/captions do not match the eight gallery slides")
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
