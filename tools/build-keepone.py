#!/usr/bin/env python3
"""
Generate /KeepOne/ - "KeepOne: Duplicate Photo & File Finder", the Microsoft
Store (WinUI 3) app that finds duplicate and similar photos, videos, files and
folders and removes the extra copies safely, in the app's 23 languages.

Built on the same template as /smart-photos/, /stow/ and /nudge/: its own
navigation tree whose language switcher lists only the KeepOne locales, every
CTA pointing at the Microsoft Store listing, real store slides in the hero and
the gallery, and the install bar / back-to-top chrome wrapped in
tools/build-ux.py's BEGIN/END markers so that builder replaces it rather than
appending a copy.

The folder is /KeepOne/ in mixed case, unlike the other apps: the privacy
policy URL entered in Partner Center (/KeepOne/privacy.html) was there first,
and a Windows checkout cannot hold a KeepOne and a keepone folder side by
side. GitHub Pages URLs are case-sensitive, so every link must use the same
casing. This builder writes index.html files only; privacy.html is hand-edited.

The copy comes from two files:

  * tools/keepone-listing.json - the store listing's own translated text
    (localized title, short description, description, feature bullets, slide
    captions), the words on the store slides and the app's three similar-photo
    strictness labels, refreshed from the app repository by
    tools/build-keepone-shots.py.
  * tools/keepone-strings.json - what is written for this page: the
    at-a-glance facts, the "why another duplicate finder" argument, the safety
    details the listing has no room for, the three steps, pricing, and the FAQ.
    It follows the app's own website description (store/website-description.md
    in the app repo); every claim there was checked against the app's README.

The app is a free download: scanning, review, history and undo are never
limited, removal is capped at 100 files or 1 GB in total, and one in-app
Durable purchase (KeepOneUnlimited) removes the cap. The add-on's price is set
per market, so the page prints none and the Offer in the structured data is the
app's own price, 0.

Store links are ordinary https://apps.microsoft.com/detail/... URLs so they
work everywhere and stay crawlable; assets/js/ux.js upgrades them to
ms-windows-store:// in place when the visitor is on Windows.

Run:  python tools/build-keepone.py
Idempotent: every page is rewritten from the two JSON files on each run.
"""
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")


def _load(name):
    with open(os.path.join(TOOLS, name), encoding="utf-8") as fh:
        return json.load(fh)


S = _load("keepone-strings.json")
LISTING = _load("keepone-listing.json")
CONSENT_L = _load("consent-strings.json")

SECTION = "KeepOne"
SITE = "https://www.dhinovatech.com"
STORE_ID = "9PP2PKFG978L"
STORE = "https://apps.microsoft.com/detail/" + STORE_ID
STORE_UTM = STORE + "?ocid=dhinovatech_KeepOne"

ICON = "/assets/images/keepone-icon.png"
ICON_WEBP = "/assets/images/keepone-icon.webp"
PRIVACY = "/KeepOne/privacy.html"
# When the page's copy last changed in substance; the WebPage schema reports it.
MODIFIED = "2026-10-14"
OGIMG = "/assets/images/keepone-og.png"
OGW, OGH = 1200, 630
OGALT = "KeepOne - duplicate photo and file finder for Windows, free on the Microsoft Store"

# The store slides tools/build-keepone-shots.py writes. "hero" is slide 1; the
# other eight are slides 3-10, in the order of listing "shots" (and of
# listing "captions"[2:]).
HERO = "hero"
SHOTS = ["similar", "exact", "folders", "videos", "confirm", "undo", "scan", "private"]
SHOT_W, SHOT_H = 1200, 675
SHOT_ICONS = ["bi-images", "bi-patch-check", "bi-folder2", "bi-film",
              "bi-list-check", "bi-arrow-counterclockwise", "bi-hdd-stack", "bi-shield-lock"]
# The eight overview tiles of store slide 2, keyed by the kit's own icon names.
TILE_ICONS = {"photos": "bi-images", "similar": "bi-intersect", "video": "bi-film",
              "document": "bi-file-earmark-text", "folder": "bi-folder2",
              "verified": "bi-patch-check", "undo": "bi-arrow-counterclockwise",
              "lock": "bi-shield-lock"}
CHIP_ICONS = ["bi-intersect text-primary", "bi-arrow-counterclockwise text-info",
              "bi-person-slash text-warning"]
WHY_ICONS = ["bi-shield-check", "bi-chat-square-text", "bi-incognito", "bi-gift"]
SAFE_ICONS = ["bi-patch-check", "bi-1-circle", "bi-trash3", "bi-arrow-repeat",
              "bi-arrow-counterclockwise", "bi-windows"]
KIND_ICONS = ["bi-images", "bi-intersect", "bi-film", "bi-file-earmark-text",
              "bi-folder2", "bi-file-earmark-image"]

# Strings keys that are the same in every language, so only "en" carries them.
SAME_IN_ALL = {"quota_num"}

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
BY_CODE = {row[0]: row for row in LANGS}

E = html.escape


def url_for(code):
    return "/%s/" % SECTION if code == "en" else "/%s/%s/" % (SECTION, code)


def abs_url(code):
    return SITE + url_for(code)


def shot_url(code, slug):
    rel = "assets/images/keepone/%s/%s.webp" % (code, slug)
    if code != "en" and not os.path.exists(os.path.join(ROOT, rel)):
        rel = "assets/images/keepone/en/%s.webp" % slug
    return "/" + rel


def built_langs():
    return [x for x in LANGS if x[0] in LISTING]


def block(lst, n):
    """Store description paragraph n as (heading, [bullets])."""
    lines = [l.strip() for l in lst["description"][n].split("\n") if l.strip()]
    return lines[0], [l.lstrip("•").strip() for l in lines[1:]]


def para(lst, n):
    """Store description paragraph n without its heading line."""
    return lst["description"][n].split("\n", 1)[1].strip()


# "Label: text" at the start of a listing bullet, in any of the kit's scripts.
LABEL_RE = re.compile(r"^(.{2,64}?)\s?[:：]\s*(.+)$", re.S)


def split_label(text):
    """("Label", "Rest, starting with a capital") or ("", text)."""
    m = LABEL_RE.match(text)
    if not m:
        return "", text
    rest = m.group(2)
    return m.group(1), rest[:1].upper() + rest[1:]


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
    c = CONSENT_L.get(code) or CONSENT_L.get(code.split("-")[0]) or CONSENT_L["en"]
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
    c = CONSENT_L.get(code) or CONSENT_L.get(code.split("-")[0]) or CONSENT_L["en"]
    return c.get("privacy", "Privacy Policy")


# --------------------------------------------------------------------------
# Shared navigation - KeepOne owns its own language tree.
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

          <!-- Our Apps - KeepOne owns its own language tree -->
          <li class="nav-item dropdown">
            <a class="nav-link nav-link-custom dropdown-toggle active" href="#" id="appsDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
              Our Apps
            </a>
            <ul class="dropdown-menu dropdown-menu-dark border-secondary shadow-lg mt-2" aria-labelledby="appsDropdown">
              <li class="dropdown-submenu position-relative">
                <a class="dropdown-item py-2 d-flex align-items-center justify-content-between" href="/KeepOne/">
                  <span><img src="__ICON__" alt="KeepOne Icon" style="width: 20px; height: 20px; border-radius: 5px; object-fit: cover;" class="me-2" decoding="async" width="256" height="256">KeepOne Duplicate Finder</span>
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

          <!-- Language Selector - KeepOne only -->
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
            <li><a href="/smart-photos/" class="footer-link"><i class="bi bi-images me-1" aria-hidden="true"></i> Smart Photos</a></li>
            <li><a href="/KeepOne/" class="footer-link text-primary fw-semibold"><i class="bi bi-intersect me-1" aria-hidden="true"></i> KeepOne Duplicate Finder</a></li>
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
          <p class="small mb-0"><a href="/KeepOne/privacy.html" class="footer-link"><i class="bi bi-shield-check me-2 text-primary" aria-hidden="true"></i>KeepOne Privacy Policy</a></p>
        </div>
      </div>
      <div class="pt-4 border-top border-secondary text-center text-secondary small">
        <p class="mb-0">&copy; 2026 Dhinovatech. All rights reserved.</p>
      </div>
    </div>
  </footer>
"""

# Same structure as the Smart Photos and Nudge pages, re-keyed to the cyan
# glow and royal blue of the KeepOne icon and store slides, with the slides'
# sunny yellow for the "Free download" tag. The custom properties are declared
# site-wide in custom.css, so re-declaring them here re-keys the shared chrome
# for this section only. Blue stays reserved for the Microsoft Store buttons
# (.btn-primary, .btn-store-ms are not touched).
PAGE_CSS = """  <style>
    :root {
      --dhin-accent-blue: #22d3ee;
      --dhin-border-glow: rgba(34, 211, 238, 0.32);
      --dhin-shadow-glow: 0 0 25px rgba(34, 211, 238, 0.2);
      --dhin-gradient-primary: linear-gradient(135deg, #22d3ee 0%, #1e6bff 100%);
      --ko-cyan: #22d3ee;
      --ko-blue: #1e6bff;
      --ko-sun: #ffd166;
      --ko-ink: #0c1434;
    }
    :root, [data-bs-theme="dark"] {
      --bs-primary-rgb: 34, 211, 238;
      --bs-primary-bg-subtle: rgba(34, 211, 238, 0.12);
      --bs-primary-border-subtle: rgba(34, 211, 238, 0.32);
      --bs-primary-text-emphasis: #8be9f8;
    }
    .text-gradient {
      background: linear-gradient(135deg, #a5f3fc 0%, #22d3ee 50%, #1e6bff 100%);
      -webkit-background-clip: text;
      background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .btn-dhin-primary { box-shadow: 0 4px 15px rgba(34, 211, 238, 0.26); }
    .btn-dhin-primary:hover { box-shadow: 0 8px 25px rgba(34, 211, 238, 0.4); }
    .btn-dhin-outline:hover { background: rgba(34, 211, 238, 0.1); }
    .hero-section {
      padding: 56px 0 64px;
      background: radial-gradient(circle at 22% 18%, rgba(30, 107, 255, 0.24) 0%, rgba(8, 12, 20, 0) 62%);
    }
    @media (max-width: 991.98px) { .hero-section { padding: 32px 0 48px; } }
    .hero-title { overflow-wrap: anywhere; }

    .glow-aura-cyan { box-shadow: 0 0 45px rgba(34, 211, 238, 0.24); }
    .ko-icon-box {
      width: 52px; height: 52px; border-radius: 14px;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.4rem; flex-shrink: 0;
      background: linear-gradient(135deg, rgba(34,211,238,0.18), rgba(30,107,255,0.14));
      color: var(--ko-cyan); border: 1px solid rgba(34,211,238,0.3);
    }
    .ko-icon-box-sm { width: 38px; height: 38px; font-size: 1.1rem; border-radius: 10px; }
    .ko-badge-row { display: flex; flex-wrap: wrap; gap: .5rem; }
    .ko-step {
      width: 42px; height: 42px; border-radius: 50%; flex-shrink: 0;
      display: flex; align-items: center; justify-content: center;
      font-weight: 800; font-size: 1.1rem;
      background: rgba(34,211,238,0.16); color: var(--ko-cyan);
      border: 1px solid rgba(34,211,238,0.4);
    }

    /* Hero */
    .ko-hero-icon { width: 60px; height: 60px; flex-shrink: 0; }
    .ko-hero-icon img { width: 100%; height: 100%; object-fit: cover; display: block; border-radius: 14px; }
    .ko-hero-kind { font-weight: 600; color: #e2e8f0; font-size: .95rem; line-height: 1.3; }
    .ko-hero-tagline {
      font-size: clamp(1.15rem, 1rem + 0.8vw, 1.6rem); font-weight: 500;
      line-height: 1.35; letter-spacing: 0; color: #a5f3fc; margin-top: .6rem;
    }
    .ko-cta-strip .ko-price { margin: 0; }
    .ko-price {
      display: flex; align-items: center; gap: .5rem; flex-wrap: wrap;
      font-size: .92rem; color: #cbd5e1;
    }
    .ko-price-tag {
      background: var(--ko-sun); color: var(--ko-ink);
      border-radius: 20px; padding: 3px 14px; font-size: .95rem; font-weight: 800;
      white-space: nowrap; text-decoration: none;
      box-shadow: 0 0 18px rgba(255, 209, 102, .3);
    }
    .ko-price-tag:hover { color: var(--ko-ink); background: #ffdd8a; }
    .ko-window {
      border-radius: 14px; overflow: hidden; background: #0a1a4a;
      border: 1px solid rgba(255,255,255,.12);
      box-shadow: 0 30px 70px -25px rgba(0,0,0,.9);
    }
    .ko-window img { display: block; width: 100%; height: auto; }

    .ko-narrow { max-width: 760px; }

    /* At a glance */
    .ko-glance-def { font-size: 1.1rem; color: #e2e8f0; line-height: 1.6; }
    .ko-facts { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 0; margin: 0; }
    .ko-fact { padding: 1rem 1.1rem; border-top: 1px solid rgba(255,255,255,.08); }
    .ko-fact dt { font-size: .75rem; text-transform: uppercase; letter-spacing: .06em; color: var(--ko-cyan); font-weight: 700; margin-bottom: .3rem; }
    .ko-fact dd { margin: 0; font-size: .92rem; color: #cbd5e1; }

    /* Screenshot gallery */
    .ko-shot { overflow: hidden; margin: 0; }
    .ko-shot img { display: block; width: 100%; height: auto; border-bottom: 1px solid rgba(255,255,255,.07); }
    .ko-shot figcaption { padding: .85rem 1rem; font-size: .9rem; font-weight: 600; color: #e2e8f0; }
    .ko-shot figcaption i { color: var(--ko-cyan); }

    /* Cards */
    .invariant-card { border-left: 3px solid var(--ko-cyan) !important; transition: transform .2s ease, box-shadow .2s ease; }
    [dir="rtl"] .invariant-card { border-left: 0 !important; border-right: 3px solid var(--ko-cyan) !important; }
    .invariant-card:hover { transform: translateY(-3px); box-shadow: 0 10px 30px rgba(34, 211, 238, 0.12); }
    .pillar-card { transition: transform .2s ease, border-color .2s ease; }
    .pillar-card:hover { transform: translateY(-3px); border-color: rgba(34, 211, 238, 0.4) !important; }
    .ko-check-list li { display: flex; gap: .6rem; margin-bottom: .6rem; font-size: .9rem; color: #cbd5e1; }
    .ko-check-list li i { color: var(--ko-cyan); flex-shrink: 0; margin-top: .1rem; }
    .ko-block-h { font-size: 1.05rem; line-height: 1.35; }
    .ko-strict { border: 1px solid rgba(34,211,238,.25); border-radius: 14px; background: rgba(34,211,238,.05); }
    .ko-strict-name { color: var(--ko-cyan); font-weight: 700; }

    /* Pricing */
    .ko-plan { display: flex; flex-direction: column; border: 1px solid rgba(255,255,255,.1) !important; }
    .ko-plan-free { border: 2px solid var(--ko-cyan) !important; box-shadow: 0 0 40px rgba(34, 211, 238, .16); }
    .ko-plan-price { font-size: 2.6rem; font-weight: 800; line-height: 1.1; color: var(--ko-cyan); }
    .ko-plan-price-sm { font-size: 1.15rem; font-weight: 600; color: #e2e8f0; line-height: 1.4; min-height: 2.6rem; display: flex; align-items: center; }
    .ko-plan-opt { background: rgba(255,255,255,.08); color: #cbd5e1; font-size: .72rem; font-weight: 600; }
    .ko-quota {
      display: flex; align-items: center; gap: .9rem;
      padding: .9rem 1.1rem; border-radius: 14px;
      background: rgba(255, 209, 102, .1); border: 1px solid rgba(255, 209, 102, .38);
    }
    .ko-quota-num { font-size: 2.4rem; font-weight: 800; line-height: 1; color: var(--ko-sun); flex-shrink: 0; }
    .ko-quota-label { font-weight: 700; color: #fff; line-height: 1.3; }
    .ko-quota-pro { background: rgba(34, 211, 238, .08); border-color: rgba(34, 211, 238, .3); }
    .ko-quota-pro .ko-quota-num { color: var(--ko-cyan); }

    /* FAQ */
    .accordion-button:not(.collapsed) { background: rgba(34, 211, 238, 0.08); color: var(--ko-cyan); box-shadow: none; }
    .accordion-button:focus { box-shadow: 0 0 0 0.2rem rgba(34, 211, 238, 0.25); }
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
         "@id": SITE + "/KeepOne/#software",
         "name": "KeepOne",
         "alternateName": lst["title"],
         "operatingSystem": "Windows 10 version 2004 (build 19041) and later, Windows 11",
         "applicationCategory": "UtilitiesApplication",
         "applicationSubCategory": "Duplicate file finder",
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
         "dateModified": MODIFIED, "about": {"@id": SITE + "/KeepOne/#software"},
         "mainEntity": {"@id": SITE + "/KeepOne/#software"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "KeepOne", "item": abs_url("en")},
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
             "name": "KeepOne (%s)" % code, "item": abs_url(code)})
    return json.dumps({"@context": "https://schema.org", "@graph": graph},
                      ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


# ---------------------------------------------------------------- sections

def eyebrow(icon, text):
    return ('<span class="badge bg-primary-subtle text-primary border border-primary-subtle '
            'rounded-pill px-3 py-2 fw-semibold mb-2"><i class="bi %s me-1" aria-hidden="true">'
            '</i> %s</span>' % (icon, E(text)))


def section_head(icon, eb, h, sub):
    return """      <div class="text-center mx-auto mb-5 ko-narrow">
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
    """The descriptor of the localized title ("Duplicate Photo & File Finder").

    Each language's title was written from that market's measured Store
    searches, so the hero shows it rather than a second, invented phrase.
    """
    title = lst["title"]
    for sep in (": ", " : ", " - ", " – "):
        if title.startswith("KeepOne" + sep):
            return title[len("KeepOne" + sep):]
    return lst["tagline"]


def check_items(rows, indent="              "):
    return "\n".join(
        '%s<li><i class="bi bi-check2-circle" aria-hidden="true"></i><span>%s</span></li>'
        % (indent, E(r)) for r in rows)


def render_price(t, lst, centred=False):
    return ('<p class="ko-price mt-3 mb-0%s"><a class="ko-price-tag" href="#pricing">'
            '<i class="bi bi-gift-fill me-1" aria-hidden="true"></i>%s</a>'
            '<span>%s</span></p>'
            % (" justify-content-center" if centred else "",
               E(lst["free"]), E(t["free_note"])))


def cta_strip(t, lst):
    """The store button again, where a reader who is convinced looks for it."""
    return """      <div class="ko-cta-strip d-flex flex-column flex-md-row align-items-center justify-content-center gap-3 mt-5">
        %s
        %s
      </div>
""" % (store_button(t), render_price(t, lst).replace(" mt-3", ""))


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
            <span class="ko-hero-icon">
              <img src="%(icon)s" alt="" decoding="async" width="256" height="256">
            </span>
            <span>
              <span class="d-block ko-hero-kind">%(kind)s</span>
              <span class="d-block small text-secondary">
                <i class="bi bi-microsoft me-1" aria-hidden="true"></i>Microsoft Store &middot; Windows 10 &amp; 11
              </span>
            </span>
          </div>

          <h1 class="hero-title mb-3"><span class="d-block">KeepOne</span> <span class="d-block ko-hero-tagline">%(h1)s</span></h1>
          <p class="lead text-secondary mb-4 pe-lg-4 fs-5">%(lead)s</p>

          <div class="d-flex flex-wrap gap-3 align-items-center">
            %(store)s
            <a href="#screenshots" class="btn btn-dhin-outline btn-lg rounded-pill px-4">
              <i class="bi bi-images me-2" aria-hidden="true"></i> %(cta_see)s
            </a>
          </div>
          %(price)s

          <div class="ko-badge-row pt-4 mt-2">
%(badges)s
          </div>
        </div>

        <div class="col-lg-6">
          <div class="position-relative">
            <div class="position-absolute top-50 start-50 translate-middle w-100 h-100 rounded-circle bg-primary opacity-25 blur-3xl glow-aura-cyan" aria-hidden="true"></div>
            <div class="ko-window position-relative">
              <img src="%(hero)s" alt="%(hero_alt)s" decoding="async" fetchpriority="high" width="%(w)d" height="%(h)d">
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
""" % dict(icon=ICON_WEBP, kind=E(store_kind(lst)),
           h1=E("%s %s" % (lst["line1"], lst["line2"])), lead=E(lst["short"]),
           store=store_button(t), cta_see=E(t["shots"]), price=render_price(t, lst),
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
        '            <div class="ko-fact"><dt>%s</dt><dd>%s</dd></div>' % (E(k), E(v))
        for k, v in t["glance"])
    return """  <!-- At a glance -->
  <section class="py-5 border-top border-secondary-subtle" id="at-a-glance">
    <div class="container py-3">
      <div class="row justify-content-center">
        <div class="col-lg-10">
          <h2 class="h3 text-white fw-bold mb-3"><i class="bi bi-info-circle text-primary me-2" aria-hidden="true"></i>%s</h2>
          <p class="ko-glance-def mb-4">%s</p>
          <dl class="ko-facts card card-glass border border-secondary-subtle overflow-hidden">
%s
          </dl>
        </div>
      </div>
    </div>
  </section>
""" % (E(t["glance_h"]), E(lst["description"][0]), facts)


def render_overview(lst):
    """Store slide 2 as real text: every kind of duplicate, at a glance."""
    ov = lst["overview"]
    tiles = []
    for key, name, what in ov["tiles"]:
        tiles.append("""        <div class="col-lg-3 col-md-6">
          <div class="card card-glass h-100 p-4 pillar-card border border-secondary-subtle">
            <span class="ko-icon-box mb-3"><i class="bi %s" aria-hidden="true"></i></span>
            <h3 class="h6 text-white fw-bold mb-2">%s</h3>
            <p class="text-secondary small mb-0">%s</p>
          </div>
        </div>""" % (TILE_ICONS.get(key, "bi-check2-circle"), E(name), E(what)))
    return """  <!-- Overview -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="overview">
    <div class="container py-4">
%s
      <div class="row g-4">
%s
      </div>
    </div>
  </section>
""" % (section_head("bi-intersect", ov["kicker"], ov["title"], lst["description"][1]),
       "\n".join(tiles))


def render_gallery(code, t, lst):
    cards = []
    for i, (slug, icon) in enumerate(zip(SHOTS, SHOT_ICONS)):
        cap = lst["captions"][i + 2]
        cards.append("""        <div class="col-md-6">
          <figure class="card card-glass ko-shot h-100">
            <img src="%s" alt="%s" loading="lazy" decoding="async" width="%d" height="%d">
            <figcaption><i class="bi %s me-2" aria-hidden="true"></i>%s</figcaption>
          </figure>
        </div>""" % (shot_url(code, slug), E(cap), SHOT_W, SHOT_H, icon, E(cap)))
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


def render_why(t):
    """Why another duplicate finder: the problems with many, and the answer."""
    cards = []
    for icon, c in zip(WHY_ICONS, t["why_cards"]):
        cards.append("""        <div class="col-lg-3 col-md-6">
          <div class="card card-glass h-100 p-4 pillar-card border border-secondary-subtle">
            <span class="ko-icon-box mb-3"><i class="bi %s" aria-hidden="true"></i></span>
            <h3 class="h6 text-white fw-bold mb-2">%s</h3>
            <p class="text-secondary small mb-0">%s</p>
          </div>
        </div>""" % (icon, E(c["t"]), E(c["d"])))
    return """  <!-- Why another duplicate finder -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="why-keepone">
    <div class="container py-4">
%s
      <div class="ko-narrow mx-auto mb-5">
        <p class="text-secondary fs-5">%s</p>
        <p class="text-white fs-5 mb-0">%s</p>
      </div>
      <div class="row g-4">
%s
      </div>
    </div>
  </section>
""" % (section_head("bi-question-diamond", t["why_eb"], t["why_h"], ""),
       E(t["why_p1"]), E(t["why_p2"]), "\n".join(cards))


def render_safe(t, lst):
    """The safety invariants: the listing's six, then the details behind them."""
    _head, bullets = block(lst, 3)
    cards = []
    for icon, b in zip(SAFE_ICONS, bullets):
        cards.append("""        <div class="col-lg-4 col-md-6">
          <div class="card card-glass h-100 p-4 invariant-card">
            <span class="ko-icon-box ko-icon-box-sm mb-3"><i class="bi %s" aria-hidden="true"></i></span>
            <p class="text-secondary mb-0">%s</p>
          </div>
        </div>""" % (icon, E(b)))
    return """  <!-- Careful by design -->
  <section class="py-5" id="safety">
    <div class="container py-4">
%s
      <div class="row g-4 mb-5">
%s
      </div>
      <div class="card card-glass p-4 p-md-5 border border-primary border-opacity-25">
        <h3 class="h5 text-white fw-bold mb-4"><i class="bi bi-gear-wide-connected text-primary me-2" aria-hidden="true"></i>%s</h3>
        <ul class="list-unstyled ko-check-list mb-0">
%s
        </ul>
      </div>
    </div>
  </section>
""" % (section_head("bi-shield-check", t["safe_eb"], t["safe_h"], t["safe_sub"]),
       "\n".join(cards), E(t["safe_more_h"]), check_items(t["safe_more"], "          "))


def render_kinds(t, lst):
    """The kinds of duplicate (listing paragraph 3) and similar-photo strictness."""
    _head, bullets = block(lst, 2)
    cards = []
    for icon, b in zip(KIND_ICONS, bullets):
        label, text = split_label(b)
        # The formats bullet has no "Label:" of its own.
        title = '<h3 class="h6 text-white fw-bold mb-2">%s</h3>' % E(label or t["formats_h"])
        cards.append("""        <div class="col-lg-4 col-md-6">
          <div class="card card-glass h-100 p-4 pillar-card border border-secondary-subtle">
            <span class="ko-icon-box mb-3"><i class="bi %s" aria-hidden="true"></i></span>
            %s
            <p class="text-secondary small mb-0">%s</p>
          </div>
        </div>""" % (icon, title, E(text)))
    levels = []
    for row in lst["strictness"]:
        name, text = split_label(row)
        levels.append("""          <div class="col-md-4">
            <div class="ko-strict h-100 p-3">
              <div class="ko-strict-name mb-1">%s</div>
              <div class="text-secondary small">%s</div>
            </div>
          </div>""" % (E(name or row), E(text if name else "")))
    return """  <!-- Every kind of duplicate -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="duplicates">
    <div class="container py-4">
%s
      <div class="row g-4 mb-5">
%s
      </div>
      <div class="card card-glass p-4 p-md-5 border border-secondary-subtle">
        <h3 class="h5 text-white fw-bold mb-3"><i class="bi bi-sliders text-primary me-2" aria-hidden="true"></i>%s</h3>
        <div class="row g-3 mb-3">
%s
        </div>
        <p class="text-secondary small mb-0">%s</p>
      </div>
    </div>
  </section>
""" % (section_head("bi-intersect", t["kinds_eb"], t["kinds_h"], t["kinds_sub"]),
       "\n".join(cards), E(t["strict_h"]), "\n".join(levels), E(t["strict_note"]))


def render_steps(t, lst):
    steps = []
    for n, s in enumerate(t["steps"], 1):
        steps.append("""        <div class="col-md-4">
          <div class="card card-glass h-100 p-4">
            <div class="d-flex align-items-center gap-3 mb-2">
              <div class="ko-step">%d</div>
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


def feature_card(icon, head, body):
    return """        <div class="col-lg-6">
          <div class="card card-glass h-100 p-4 invariant-card">
            <div class="d-flex align-items-center gap-3 mb-3">
              <span class="ko-icon-box ko-icon-box-sm"><i class="bi %s" aria-hidden="true"></i></span>
              <h3 class="ko-block-h text-white fw-bold mb-0">%s</h3>
            </div>
%s
          </div>
        </div>""" % (icon, E(head), body)


def render_features(code, t, lst):
    # The listing's own headings are in capitals, which cannot be turned back
    # into sentence case in every language (German nouns), so the card titles
    # come from the strings file.
    _h, clear = block(lst, 4)
    lst_ul = lambda rows: ('            <ul class="list-unstyled ko-check-list mb-0">\n%s\n            </ul>'
                           % check_items(rows))
    private_body = ('            <p class="text-secondary small mb-3">%s</p>\n'
                    '            <a class="small" href="%s"><i class="bi bi-shield-check me-1" aria-hidden="true"></i>%s</a>'
                    % (E(para(lst, 5)), PRIVACY, E(privacy_label(code))))
    cards = [
        feature_card("bi-chat-square-text", t["clear_h"], lst_ul(clear)),
        feature_card("bi-speedometer2", t["big_h"], lst_ul(t["big"])),
        feature_card("bi-incognito", t["private_h"], private_body),
        feature_card("bi-windows", t["req_h"], lst_ul(t["req"])),
    ]
    feats = lst["features"]
    half = (len(feats) + 1) // 2
    cols = []
    for chunk in (feats[:half], feats[half:]):
        cols.append("""          <div class="col-md-6">
            <ul class="list-unstyled ko-check-list mb-0">
%s
            </ul>
          </div>""" % check_items(chunk))
    return """  <!-- Features -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="features">
    <div class="container py-4">
%s
      <div class="row g-4 mb-5">
%s
      </div>
      <div class="card card-glass p-4 p-md-5 border border-primary border-opacity-25">
        <h3 class="h5 text-white fw-bold mb-4">%s</h3>
        <div class="row g-3">
%s
        </div>
      </div>
    </div>
  </section>
""" % (section_head("bi-stars", t["feat_eb"], t["feat_h"], ""), "\n".join(cards),
       E(t["all_h"]), "\n".join(cols))


def render_pricing(t, lst):
    """The free version and the one-time unlock, with the free limit in view.

    The owner's rule for the app: state the limit before anyone scans. So the
    "100 files or 1 GB" cap is the largest thing on the free card, and the
    store's own wording of the offer sits under both cards. No price: the
    add-on is priced per market and the app shows the live one.
    """
    return """  <!-- Pricing -->
  <section class="py-5" id="pricing">
    <div class="container py-4">
%s
      <div class="row justify-content-center g-4">
        <div class="col-md-6 col-lg-5">
          <div class="card card-glass h-100 p-4 p-lg-5 ko-plan ko-plan-free">
            <h3 class="h5 text-white fw-bold mb-1">%s</h3>
            <p class="ko-plan-price mb-3">%s</p>
            <div class="ko-quota mb-4">
              <span class="ko-quota-num">%s</span>
              <span class="ko-quota-label">%s</span>
            </div>
            <ul class="list-unstyled ko-check-list mb-4">
%s
            </ul>
            <div class="mt-auto">%s</div>
          </div>
        </div>
        <div class="col-md-6 col-lg-5">
          <div class="card card-glass h-100 p-4 p-lg-5 ko-plan">
            <h3 class="h5 text-white fw-bold mb-1">%s <span class="badge rounded-pill ko-plan-opt align-middle ms-1">%s</span></h3>
            <p class="ko-plan-price ko-plan-price-sm mb-3">%s</p>
            <div class="ko-quota ko-quota-pro mb-4">
              <span class="ko-quota-num"><i class="bi bi-infinity" aria-hidden="true"></i></span>
              <span class="ko-quota-label">%s</span>
            </div>
            <ul class="list-unstyled ko-check-list mb-0">
%s
            </ul>
          </div>
        </div>
      </div>
      <p class="text-secondary small text-center mx-auto mt-4 mb-2 ko-narrow">%s</p>
      <p class="text-secondary small text-center mx-auto mb-0 ko-narrow">%s</p>
    </div>
  </section>
""" % (section_head("bi-gift-fill", t["price_eb"], t["price_h"], t["price_sub"]),
       E(t["free_title"]), E(t["free_price"]), E(t["quota_num"]), E(t["quota_label"]),
       check_items(t["free_items"]), store_button(t),
       E(t["pro_title"]), E(t["pro_badge"]), E(t["pro_price"]), E(t["pro_label"]),
       check_items(t["pro_items"]), E(para(lst, 6)), E(t["price_fine"]))


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
              <div id="faq%d" class="accordion-collapse collapse%s" aria-labelledby="faq%dHeading" data-bs-parent="#keeponeFaqAccordion">
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
          <div class="accordion accordion-flush" id="keeponeFaqAccordion">
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
      <div class="card card-glass p-5 text-center border-0 position-relative overflow-hidden" style="background: linear-gradient(135deg, rgba(30,107,255,0.16) 0%%, rgba(34,211,238,0.08) 100%%);">
        <div class="ko-narrow mx-auto position-relative" style="z-index: 2;">
          <div class="mx-auto mb-3" style="width: 90px; height: 90px;">
            <img src="%s" alt="KeepOne Icon" class="w-100 h-100 object-fit-cover rounded-4" loading="lazy" decoding="async" width="256" height="256">
          </div>
          <h2 class="display-6 fw-bold text-white mb-3">%s</h2>
          <p class="text-secondary fs-5 mb-4">%s</p>
          <div class="d-flex justify-content-center">
            %s
          </div>
          %s
        </div>
      </div>
    </div>
  </section>
""" % (ICON_WEBP, E("%s %s" % (lst["line1"], lst["line2"])), E(lst["description"][1]),
       store_button(t), render_price(t, lst, True))


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
        # What it is and what it costs, stated plainly; then the eight things
        # it finds; then what it looks like; then why and how, in detail.
        render_glance(t, lst),
        render_overview(lst),
        render_gallery(code, t, lst),
        render_why(t),
        render_safe(t, lst),
        render_kinds(t, lst),
        render_steps(t, lst),
        render_pricing(t, lst),
        render_features(code, t, lst),
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
<!-- Navigation Bar (independent KeepOne tree) -->
{navbar}
<main id="main">

{body}
</main>
{footer}
  <!-- Bootstrap 5.3 JS Bundle -->
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
  <script src="/assets/js/nav.js"></script>

  <!-- BEGIN generated UX block -->
  <div class="install-bar" role="complementary" aria-label="KeepOne">
    <img src="{icon}" alt="" width="42" height="42" loading="lazy" decoding="async">
    <div class="install-bar-text">
      <div class="install-bar-title">KeepOne</div>
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


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    base = os.path.join(ROOT, SECTION)
    for code, _label, _d, _hl, _og in built_langs():
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
