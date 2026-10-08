#!/usr/bin/env python3
"""
Generate /smart-photos/ - "Smart Photos", the Microsoft Store (WinUI 3) AI photo
gallery, in 25 languages, positioned as a private Google Photos alternative
for Windows.

Built on the same template as /stow/ (tools/build-stow.py): its own navigation
tree whose language switcher lists only the Smart Photos locales, every CTA
pointing at the Microsoft Store listing, and the install bar / back-to-top
chrome wrapped in tools/build-ux.py's BEGIN/END markers so that builder
replaces it rather than appending a second copy.

The copy comes from two files:

  * tools/smart-photos-listing.json - the store listing's own translated text
    (title, short description, description paragraphs, feature bullets and
    slide captions), refreshed from the app repository by
    tools/build-smart-photos-shots.py. Reusing it keeps the page and the store
    listing saying the same thing, in the same words, in every language.
  * tools/smart-photos-strings.json - the copy written for this page: the
    Google Photos comparison, the switching steps, the FAQ. Any key a locale
    lacks falls back to English.

Store links are ordinary https://apps.microsoft.com/detail/... URLs so they
work everywhere and stay crawlable; assets/js/ux.js upgrades them to
ms-windows-store:// in place when the visitor is on Windows.

Run:  python tools/build-smart-photos.py
Idempotent: every page is rewritten from the two JSON files on each run.
"""
import datetime
import html
import importlib.util
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")


def _load(name):
    with open(os.path.join(TOOLS, name), encoding="utf-8") as fh:
        return json.load(fh)


S = _load("smart-photos-strings.json")
LISTING = _load("smart-photos-listing.json")
CONSENT_L = _load("consent-strings.json")

SECTION = "smart-photos"
SITE = "https://www.dhinovatech.com"
STORE_ID = "9N1J0MC0V89G"
STORE = "https://apps.microsoft.com/detail/" + STORE_ID
STORE_UTM = STORE + "?ocid=dhinovatech_smart-photos"

ICON = "/assets/images/smart-photos-icon.png"
PRIVACY_URL = "/smart-photos/privacy.html"
# The app's own privacy policy, copied from the app repository by
# tools/build-smart-photos-shots.py. Partner Center needs it at a public URL
# (Store Policy 10.5.1), so it is published here, next to the product page.
PRIVACY_MD = os.path.join(TOOLS, "smart-photos-privacy.md")
OGIMG = "/assets/images/smart-photos-og.png"
OGW, OGH = 1200, 630
OGALT = "Smart Photos - private Google Photos alternative for Windows, on the Microsoft Store"

# The store slides tools/build-smart-photos-shots.py writes, in store order.
# Slide 1 is the hero; each of the others is captioned with the store's own
# translated caption for that slide (listing "captions"[n]).
SLIDES = ["hero", "search", "people", "switch", "map", "memories",
          "explore", "albums", "cleanup", "privacy"]
SHOT_W, SHOT_H = 1200, 675
GALLERY_ICONS = ["bi-search", "bi-people", "bi-box-arrow-in-down", "bi-geo-alt",
                 "bi-stars", "bi-grid-3x3-gap", "bi-collection", "bi-copy",
                 "bi-shield-lock"]

# Description paragraphs 2..9 of the store listing, each "Heading. Body.",
# rendered as the feature cards.
FEATURE_ICONS = ["bi-search", "bi-people", "bi-geo-alt", "bi-play-btn",
                 "bi-stars", "bi-magic", "bi-shield-lock", "bi-plug"]
INV_ICONS = ["bi-pc-display", "bi-person-slash", "bi-file-earmark-lock",
             "bi-wifi-off", "bi-bookmark-check", "bi-bag-check"]
STEP_ICONS = ["bi-cloud-download", "bi-file-earmark-zip", "bi-check2-all"]

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
    ("pt", "Português (Portuguese)", "ltr", "pt-BR", "pt_BR"),
    ("nl", "Nederlands (Dutch)", "ltr", "nl", "nl_NL"),
    ("pl", "Polski (Polish)", "ltr", "pl", "pl_PL"),
    ("cs", "Čeština (Czech)", "ltr", "cs", "cs_CZ"),
    ("da", "Dansk (Danish)", "ltr", "da", "da_DK"),
    ("sv", "Svenska (Swedish)", "ltr", "sv", "sv_SE"),
    ("nb", "Norsk (Norwegian)", "ltr", "nb", "nb_NO"),
    ("fi", "Suomi (Finnish)", "ltr", "fi", "fi_FI"),
    ("tr", "Türkçe (Turkish)", "ltr", "tr", "tr_TR"),
    ("ja", "日本語 (Japanese)", "ltr", "ja", "ja_JP"),
    ("ko", "한국어 (Korean)", "ltr", "ko", "ko_KR"),
    ("zh", "简体中文 (Simplified Chinese)", "ltr", "zh-Hans", "zh_CN"),
    ("zh-tw", "繁體中文 (Traditional Chinese)", "ltr", "zh-Hant", "zh_TW"),
    ("th", "ไทย (Thai)", "ltr", "th", "th_TH"),
    ("vi", "Tiếng Việt (Vietnamese)", "ltr", "vi", "vi_VN"),
    ("id", "Bahasa Indonesia (Indonesian)", "ltr", "id", "id_ID"),
    ("hi", "हिन्दी (Hindi)", "ltr", "hi", "hi_IN"),
    ("ta", "தமிழ் (Tamil)", "ltr", "ta", "ta_IN"),
    ("ar", "العربية (Arabic)", "rtl", "ar", "ar_AR"),
    ("he", "עברית (Hebrew)", "rtl", "he", "he_IL"),
]
BY_CODE = {c: row for row in LANGS for c in [row[0]]}

E = html.escape


def url_for(code):
    return "/%s/" % SECTION if code == "en" else "/%s/%s/" % (SECTION, code)


def abs_url(code):
    return SITE + url_for(code)


def shot_url(code, slug):
    rel = "assets/images/smart-photos/%s/%s.webp" % (code, slug)
    if code != "en" and not os.path.exists(os.path.join(ROOT, rel)):
        rel = "assets/images/smart-photos/en/%s.webp" % slug
    return "/" + rel


def built_langs():
    return [x for x in LANGS if x[0] in LISTING]


# Store description paragraphs open with a short heading sentence. Thai marks
# sentences with a space rather than punctuation, so it splits on the first
# space instead.
_HEAD = re.compile(r"^(.+?[.。！？!?।؟:：])\s*(.+)$", re.S)


def split_heading(code, para):
    if code == "th":
        head, _sp, body = para.partition(" ")
        return head, body
    m = _HEAD.match(para)
    if m and len(m.group(1)) < 70:
        return m.group(1).rstrip(".。:："), m.group(2)
    return "", para


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


# --------------------------------------------------------------------------
# Shared navigation - Smart Photos owns its own language tree.
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

          <!-- Our Apps - Smart Photos owns its own language tree -->
          <li class="nav-item dropdown">
            <a class="nav-link nav-link-custom dropdown-toggle active" href="#" id="appsDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
              Our Apps
            </a>
            <ul class="dropdown-menu dropdown-menu-dark border-secondary shadow-lg mt-2" aria-labelledby="appsDropdown">
              <li class="dropdown-submenu position-relative">
                <a class="dropdown-item py-2 d-flex align-items-center justify-content-between" href="/smart-photos/">
                  <span><img src="__ICON__" alt="Smart Photos Icon" style="width: 20px; height: 20px; border-radius: 5px; object-fit: cover;" class="me-2" decoding="async" width="256" height="256">Smart Photos</span>
                  <span class="badge bg-primary-subtle text-primary border border-primary-subtle rounded-pill ms-2 extra-small submenu-toggle-btn" role="button" title="View __N__ Languages">__N__ Languages <i class="bi bi-chevron-down ms-1" aria-hidden="true"></i></span>
                </a>
                <ul class="dropdown-menu dropdown-menu-dark border-secondary shadow-lg scrollable-menu" style="max-height: 360px; overflow-y: auto;">
                  __LANG_SUBMENU__
                </ul>
              </li>
              <li><a class="dropdown-item py-2" href="/nudge/"><img src="/assets/images/nudge-icon.png" alt="Nudge Icon" style="width: 20px; height: 20px; border-radius: 5px; object-fit: cover;" class="me-2" decoding="async">Nudge Offline Journal</a></li>
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

          <!-- Language Selector - Smart Photos only -->
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
   .replace("__ICON__", ICON) \
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
          </ul>
        </div>
        <div class="col-lg-3 col-6">
          <h4 class="h6 text-white fw-bold mb-3">Our Applications</h4>
          <ul class="list-unstyled small d-flex flex-column gap-2 mb-0">
            <li><a href="/smart-photos/" class="footer-link text-primary fw-semibold"><i class="bi bi-images me-1" aria-hidden="true"></i> Smart Photos</a></li>
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
          <p class="small text-secondary"><i class="bi bi-globe me-2 text-primary" aria-hidden="true"></i>www.dhinovatech.com</p>
        </div>
      </div>
      <div class="pt-4 border-top border-secondary text-center text-secondary small">
        <p class="mb-0">&copy; 2026 Dhinovatech. All rights reserved.</p>
      </div>
    </div>
  </footer>
"""

# Same structure as the Stow page, re-keyed from amber to the mint-teal the
# application's own brand colour and store slides use. The custom properties
# are declared site-wide in custom.css, so re-declaring them here re-keys the
# shared chrome for this section only.
PAGE_CSS = """  <style>
    :root {
      --dhin-accent-blue: #5fd3ae;
      --dhin-border-glow: rgba(95, 211, 174, 0.32);
      --dhin-shadow-glow: 0 0 25px rgba(95, 211, 174, 0.22);
      --dhin-gradient-primary: linear-gradient(135deg, #5fd3ae 0%, #1f9c7c 100%);
      --sp-mint: #5fd3ae;
      --sp-sun: #ffc24a;
      --sp-ink: #04201a;
    }
    :root, [data-bs-theme="dark"] {
      --bs-primary-rgb: 95, 211, 174;
      --bs-primary-bg-subtle: rgba(95, 211, 174, 0.12);
      --bs-primary-border-subtle: rgba(95, 211, 174, 0.32);
      --bs-primary-text-emphasis: #8fe6c9;
    }
    .text-gradient {
      background: linear-gradient(135deg, #a6eed6 0%, #5fd3ae 55%, #1f9c7c 100%);
      -webkit-background-clip: text;
      background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .btn-dhin-primary { box-shadow: 0 4px 15px rgba(95, 211, 174, 0.28); }
    .btn-dhin-primary:hover { box-shadow: 0 8px 25px rgba(95, 211, 174, 0.42); }
    .btn-dhin-outline:hover { background: rgba(95, 211, 174, 0.1); }
    .hero-section {
      padding: 56px 0 64px;
      background: radial-gradient(circle at 22% 18%, rgba(95, 211, 174, 0.14) 0%, rgba(8, 12, 20, 0) 62%);
    }
    @media (max-width: 991.98px) { .hero-section { padding: 32px 0 48px; } }
    .hero-title { overflow-wrap: anywhere; }

    .glow-aura-teal { box-shadow: 0 0 45px rgba(95, 211, 174, 0.26); }
    .sp-icon-box {
      width: 52px; height: 52px; border-radius: 14px;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.4rem; flex-shrink: 0;
      background: linear-gradient(135deg, rgba(95,211,174,0.18), rgba(31,156,124,0.12));
      color: var(--sp-mint); border: 1px solid rgba(95,211,174,0.3);
    }
    .sp-icon-box-sm { width: 38px; height: 38px; font-size: 1.1rem; border-radius: 10px; }
    .sp-badge-row { display: flex; flex-wrap: wrap; gap: .5rem; }
    .sp-step {
      width: 42px; height: 42px; border-radius: 50%; flex-shrink: 0;
      display: flex; align-items: center; justify-content: center;
      font-weight: 800; font-size: 1.1rem;
      background: rgba(95,211,174,0.18); color: var(--sp-mint);
      border: 1px solid rgba(95,211,174,0.4);
    }

    /* Hero */
    .sp-hero-icon { width: 60px; height: 60px; flex-shrink: 0; }
    .sp-hero-icon img { width: 100%; height: 100%; object-fit: contain; display: block; }
    .sp-hero-kind { font-weight: 600; color: #e2e8f0; font-size: .95rem; line-height: 1.3; }
    .sp-note {
      max-width: 820px; padding: 1rem 1.25rem; border-radius: 14px;
      background: rgba(95, 211, 174, 0.06); border: 1px solid rgba(95, 211, 174, 0.22);
    }
    .sp-cta-strip .sp-price { margin: 0; }
    .sp-hero-tagline {
      font-size: clamp(1.15rem, 1rem + 0.8vw, 1.6rem); font-weight: 500;
      line-height: 1.35; letter-spacing: 0; color: #a6eed6; margin-top: .6rem;
    }
    .sp-price {
      display: flex; align-items: center; gap: .5rem; flex-wrap: wrap;
      font-size: .92rem; color: #cbd5e1;
    }
    .sp-price-tag {
      background: var(--sp-mint); color: var(--sp-ink);
      border-radius: 20px; padding: 3px 14px; font-size: .95rem; font-weight: 800;
      white-space: nowrap; text-decoration: none;
      box-shadow: 0 0 18px rgba(95, 211, 174, .35);
    }
    .sp-price-tag:hover { color: var(--sp-ink); background: #7fe0c0; }

    /* Pricing */
    .sp-plan { display: flex; flex-direction: column; border: 1px solid rgba(255,255,255,.1) !important; }
    .sp-plan-free { border: 2px solid var(--sp-mint) !important; box-shadow: 0 0 40px rgba(95, 211, 174, .18); }
    .sp-plan-price { font-size: 2.6rem; font-weight: 800; line-height: 1.1; color: var(--sp-mint); }
    .sp-plan-price-sm { font-size: 1.15rem; font-weight: 600; color: #e2e8f0; line-height: 1.4; min-height: 2.6rem; display: flex; align-items: center; }
    .sp-plan-opt { background: rgba(255,255,255,.08); color: #cbd5e1; font-size: .72rem; font-weight: 600; }
    .sp-quota {
      display: flex; align-items: center; gap: .9rem;
      padding: .9rem 1.1rem; border-radius: 14px;
      background: rgba(255, 194, 74, .1); border: 1px solid rgba(255, 194, 74, .38);
    }
    .sp-quota-num { font-size: 2.4rem; font-weight: 800; line-height: 1; color: var(--sp-sun); flex-shrink: 0; }
    .sp-quota-label { font-weight: 700; color: #fff; line-height: 1.3; }
    .sp-quota-pro { background: rgba(95, 211, 174, .08); border-color: rgba(95, 211, 174, .3); }
    .sp-quota-pro .sp-quota-num { color: var(--sp-mint); }
    .sp-window {
      border-radius: 14px; overflow: hidden; background: #0d2a26;
      border: 1px solid rgba(255,255,255,.12);
      box-shadow: 0 30px 70px -25px rgba(0,0,0,.9);
    }
    .sp-window img { display: block; width: 100%; height: auto; }

    /* Screenshot gallery */
    .sp-shot { overflow: hidden; margin: 0; }
    .sp-shot img { display: block; width: 100%; height: auto; border-bottom: 1px solid rgba(255,255,255,.07); }
    .sp-shot figcaption { padding: .85rem 1rem; font-size: .9rem; font-weight: 600; color: #e2e8f0; }
    .sp-shot figcaption i { color: var(--sp-mint); }

    /* Cards */
    .invariant-card { border-left: 3px solid var(--sp-mint) !important; transition: transform .2s ease, box-shadow .2s ease; }
    [dir="rtl"] .invariant-card { border-left: 0 !important; border-right: 3px solid var(--sp-mint) !important; }
    .invariant-card:hover { transform: translateY(-3px); box-shadow: 0 10px 30px rgba(95, 211, 174, 0.14); }
    .pillar-card { transition: transform .2s ease, border-color .2s ease; }
    .pillar-card:hover { transform: translateY(-3px); border-color: rgba(95, 211, 174, 0.4) !important; }
    .sp-check-list li { display: flex; gap: .6rem; margin-bottom: .6rem; font-size: .9rem; color: #cbd5e1; }
    .sp-check-list li i { color: var(--sp-mint); flex-shrink: 0; margin-top: .1rem; }

    /* Comparison table */
    .compare-table { font-size: 0.9rem; border-collapse: separate; border-spacing: 0; }
    .compare-table th, .compare-table td { padding: 0.9rem 1rem; border-bottom: 1px solid rgba(255, 255, 255, 0.07); }
    .compare-table thead th { background: rgba(17, 24, 39, 0.95); color: #94a3b8; font-weight: 600; }
    .compare-table th.sp-col, .compare-table td.sp-col {
      background: rgba(95, 211, 174, 0.06);
      border-left: 1px solid rgba(95, 211, 174, 0.25);
      border-right: 1px solid rgba(95, 211, 174, 0.25);
    }
    .compare-table thead th.sp-col { background: rgba(95, 211, 174, 0.14); color: var(--sp-mint); border-top: 2px solid var(--sp-mint); }
    .compare-table td:first-child { min-width: 170px; }
    .compare-table td { min-width: 210px; }

    /* FAQ */
    .accordion-button:not(.collapsed) { background: rgba(95, 211, 174, 0.08); color: var(--sp-mint); box-shadow: none; }
    .accordion-button:focus { box-shadow: 0 0 0 0.2rem rgba(95, 211, 174, 0.25); }
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


def schema(code, t, desc):
    # Free since 2.0 (2026-10-07). Smart Photos Pro, the add-on that unlocks
    # unlimited searches, is priced per market in Partner Center and has sales,
    # so only the app's own price, which is the same everywhere, goes here.
    graph = [
        {"@type": "Organization", "@id": SITE + "/#organization",
         "name": "Dhinovatech", "url": SITE + "/"},
        {"@type": "SoftwareApplication",
         "@id": SITE + "/smart-photos/#software",
         "name": "Smart Photos",
         "alternateName": LISTING[code]["title"],
         "operatingSystem": "Windows 10 version 2004 (build 19041) and later, x64 and ARM64",
         "applicationCategory": "MultimediaApplication",
         "applicationSubCategory": "Photo gallery",
         "description": desc,
         "url": abs_url(code),
         "inLanguage": [hl for _c, _l, _d, hl, _og in built_langs()],
         "image": SITE + ICON,
         "downloadUrl": STORE,
         "installUrl": STORE,
         "featureList": LISTING[code]["features"],
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD",
                    "availability": "https://schema.org/InStock", "url": STORE},
         "screenshot": [SITE + shot_url(code, s) for s in SLIDES],
         "publisher": {"@id": SITE + "/#organization"},
         "author": {"@id": SITE + "/#organization"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Smart Photos", "item": abs_url("en")},
        ]},
        {"@type": "FAQPage", "@id": abs_url(code) + "#faq",
         "inLanguage": BY_CODE[code][3],
         "mainEntity": [{"@type": "Question", "name": f["q"],
                         "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
                        for f in t["faqs"]]},
    ]
    if code != "en":
        graph[2]["itemListElement"].append(
            {"@type": "ListItem", "position": 3,
             "name": "Smart Photos (%s)" % code, "item": abs_url(code)})
    return json.dumps({"@context": "https://schema.org", "@graph": graph},
                      ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


# ---------------------------------------------------------------- sections

def eyebrow(icon, text):
    return ('<span class="badge bg-primary-subtle text-primary border border-primary-subtle '
            'rounded-pill px-3 py-2 fw-semibold mb-2"><i class="bi %s me-1" aria-hidden="true">'
            '</i> %s</span>' % (icon, E(text)))


def section_head(icon, eb, h, sub):
    return """      <div class="text-center max-w-700 mx-auto mb-5">
        %s
        <h2 class="display-5 fw-bold text-white">%s</h2>
        %s
      </div>""" % (eyebrow(icon, eb), E(h),
                   '<p class="text-secondary fs-5">%s</p>' % E(sub) if sub else "")


def store_button(t):
    return """<a href="%s" target="_blank" rel="noopener" class="btn btn-store btn-store-ms shadow-lg">
              <i class="bi bi-microsoft" aria-hidden="true"></i>
              <span class="btn-store-copy">
                <span class="btn-store-pre">%s</span>
                <span class="btn-store-name">Microsoft Store</span>
              </span>
            </a>""" % (E(STORE_UTM), E(t["store_pre"]))


def store_kind(lst):
    """The descriptor of the localized store title ("AI Photo Viewer & Gallery").

    Every listing title is "Smart Photos - <descriptor>", and the descriptor is
    the store's own keyword choice for that market, so the hero shows it
    rather than a second, invented phrase.
    """
    title = lst["title"]
    for sep in (" - ", " \u2013 ", ": "):
        if title.startswith("Smart Photos" + sep):
            return title[len("Smart Photos" + sep):]
    return ""


def privacy_label(code):
    c = CONSENT_L.get(code) or CONSENT_L.get(code.split("-")[0]) or CONSENT_L["en"]
    return c.get("privacy", "Privacy Policy")


def cta_strip(t):
    """The store button again, where a reader who is convinced looks for it.

    The page is long; before this the only buttons were the hero, the navbar
    and the last section, which left the whole middle of the page with
    nothing to click once the comparison or the feature list had done its job.
    """
    return """      <div class="sp-cta-strip d-flex flex-column flex-md-row align-items-center justify-content-center gap-3 mt-5">
        %s
        %s
      </div>
""" % (store_button(t), render_price(t).replace(" mt-3", ""))


def render_price(t, centred=False):
    return ('<p class="sp-price mt-3 mb-0%s"><a class="sp-price-tag" href="#pricing">'
            '<i class="bi bi-gift-fill me-1" aria-hidden="true"></i>%s</a>'
            '<span>%s</span></p>'
            % (" justify-content-center" if centred else "",
               E(t["free_badge"]), E(t["free_note"])))


def render_pricing(t):
    """Free vs Smart Photos Pro, with the free version's monthly searches in view.

    The app is free (ADR 0009 in the app repo); the one limit is 30 typed
    searches a month, and the owner wants it stated plainly rather than found
    later, so it is the largest thing on the free card. Pro is presented as the
    app presents it: an optional one-time way to support the developer that
    also unlocks unlimited searches. No Pro price here: it differs by market
    and has sales, and the app shows the live one.
    """
    def items(rows):
        return "\n".join(
            '              <li><i class="bi bi-check2-circle" aria-hidden="true"></i><span>%s</span></li>' % E(r)
            for r in rows)
    return """  <!-- Pricing -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="pricing">
    <div class="container py-4">
%s
      <div class="row justify-content-center g-4">
        <div class="col-md-6 col-lg-5">
          <div class="card card-glass h-100 p-4 p-lg-5 sp-plan sp-plan-free">
            <h3 class="h5 text-white fw-bold mb-1">Smart Photos</h3>
            <p class="sp-plan-price mb-3">%s</p>
            <div class="sp-quota mb-4">
              <span class="sp-quota-num">30</span>
              <span class="sp-quota-label">%s</span>
            </div>
            <ul class="list-unstyled sp-check-list mb-4">
%s
            </ul>
            <div class="mt-auto">%s</div>
          </div>
        </div>
        <div class="col-md-6 col-lg-5">
          <div class="card card-glass h-100 p-4 p-lg-5 sp-plan">
            <h3 class="h5 text-white fw-bold mb-1">Smart Photos Pro <span class="badge rounded-pill sp-plan-opt align-middle ms-1">%s</span></h3>
            <p class="sp-plan-price sp-plan-price-sm mb-3">%s</p>
            <div class="sp-quota sp-quota-pro mb-4">
              <span class="sp-quota-num"><i class="bi bi-infinity" aria-hidden="true"></i></span>
              <span class="sp-quota-label">%s</span>
            </div>
            <ul class="list-unstyled sp-check-list mb-0">
%s
            </ul>
          </div>
        </div>
      </div>
      <p class="text-secondary small text-center mx-auto mt-4 mb-0 max-w-700">%s</p>
    </div>
  </section>
""" % (section_head("bi-gift-fill", t["price_eyebrow"], t["price_h"], t["price_sub"]),
       E(t["free_price"]), E(t["quota_label"]), items(t["free_items"]), store_button(t),
       E(t["pro_badge"]), E(t["pro_price"]), E(t["pro_items"][0]), items(t["pro_items"][1:]),
       E(t["price_fine"]))


def render_hero(code, t, lst):
    badge_icons = ["bi-cpu text-primary", "bi-person-slash text-info", "bi-cloud-slash text-warning",
                   "bi-box-arrow-in-down text-success", "bi-globe-americas text-info",
                   "bi-windows text-primary"]
    badges = "\n".join(
        '            <span class="badge bg-dark border border-secondary text-white-50 px-3 py-2 rounded-pill">'
        '<i class="bi %s me-1" aria-hidden="true"></i> %s</span>' % (i, E(b))
        for i, b in zip(badge_icons, t["badges"]))
    return """  <section class="hero-section position-relative overflow-hidden">
    <div class="container">
      <div class="row align-items-center gy-5">
        <div class="col-lg-6">
          <div class="d-flex align-items-center gap-3 mb-4">
            <span class="sp-hero-icon">
              <img src="%(icon)s" alt="" decoding="async" width="256" height="256">
            </span>
            <span>
              <span class="d-block sp-hero-kind">%(kind)s</span>
              <span class="d-block small text-secondary">
                <i class="bi bi-microsoft me-1" aria-hidden="true"></i>Microsoft Store &middot; Windows 10 &amp; 11
              </span>
            </span>
          </div>

          <!-- The product name is the headline; the Google Photos line stays
               inside the h1 for search, but reads as its subtitle. -->
          <h1 class="hero-title mb-3"><span class="d-block">Smart Photos</span> <span class="d-block sp-hero-tagline">%(h1)s</span></h1>
          <p class="lead text-secondary mb-4 pe-lg-4 fs-5">%(lead)s</p>

          <div class="d-flex flex-wrap gap-3 align-items-center">
            %(store)s
            <a href="#screenshots" class="btn btn-dhin-outline btn-lg rounded-pill px-4">
              <i class="bi bi-images me-2" aria-hidden="true"></i> %(cta_see)s
            </a>
          </div>
          %(price)s

          <div class="sp-badge-row pt-4 mt-2">
%(badges)s
          </div>
        </div>

        <div class="col-lg-6">
          <div class="position-relative">
            <div class="position-absolute top-50 start-50 translate-middle w-100 h-100 rounded-circle bg-primary opacity-25 blur-3xl glow-aura-teal" aria-hidden="true"></div>
            <div class="sp-window position-relative">
              <img src="%(hero)s" alt="%(hero_alt)s" decoding="async" fetchpriority="high" width="%(w)d" height="%(h)d">
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
""" % dict(icon=ICON, kind=E(store_kind(lst)), h1=E(t["h1"]), lead=E(lst["short"]), store=store_button(t),
           cta_see=E(t["gal_eyebrow"]), price=render_price(t), badges=badges,
           hero=shot_url(code, "hero"), hero_alt=E(lst["captions"][0]),
           w=SHOT_W, h=SHOT_H)


def render_why(t, lst):
    return """  <!-- Why people switch -->
  <section class="py-5" id="why">
    <div class="container py-3">
      <div class="row justify-content-center">
        <div class="col-lg-9 text-center">
          <span class="text-gradient fw-bold text-uppercase tracking-wider">%s</span>
          <h2 class="display-6 fw-bold text-white mt-2 mb-4">%s</h2>
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
""" % (E(t["why_eyebrow"]), E(t["why_h"]), E(t["why_p1"]), E(t["why_p2"]),
       E(lst["description"][0]), E(lst["description"][1]))


def render_compare(t, lst):
    rows = []
    for feat, sp, gp in t["cmp_rows"]:
        rows.append("""                <tr>
                  <td class="text-white fw-semibold small align-middle">%s</td>
                  <td class="sp-col small align-middle">
                    <span class="d-flex align-items-start gap-2">
                      <i class="bi bi-check-circle-fill text-success flex-shrink-0 mt-1" aria-hidden="true"></i>
                      <span class="text-white fw-semibold">%s</span>
                    </span>
                  </td>
                  <td class="text-secondary small align-middle">
                    <span class="d-flex align-items-start gap-2">
                      <i class="bi bi-dash-circle text-secondary flex-shrink-0 mt-1" aria-hidden="true"></i>
                      <span>%s</span>
                    </span>
                  </td>
                </tr>""" % (E(feat), E(sp), E(gp)))
    head = t["cmp_head"]
    return """  <!-- Smart Photos vs Google Photos -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="comparison">
    <div class="container py-4">
%s
      <div class="card card-glass p-3 p-md-4 border border-secondary-subtle shadow-lg">
        <div class="table-responsive">
          <table class="table table-dark table-borderless align-middle mb-0 compare-table">
            <thead>
              <tr class="border-bottom border-secondary">
                <th scope="col">%s</th>
                <th scope="col" class="sp-col text-primary fw-bold"><i class="bi bi-shield-check me-1" aria-hidden="true"></i>%s</th>
                <th scope="col">%s</th>
              </tr>
            </thead>
            <tbody>
%s
            </tbody>
          </table>
        </div>
      </div>
      <p class="extra-small text-secondary text-center mt-3 mb-0">%s</p>
%s    </div>
  </section>
""" % (section_head("bi-arrow-left-right", t["cmp_eyebrow"], t["cmp_h"], t["cmp_sub"]),
       E(head[0]), E(head[1]), E(head[2]), "\n".join(rows), E(lst["description"][12]),
       cta_strip(t))


def render_invariants(code, t):
    cards = []
    for icon, inv in zip(INV_ICONS, t["inv"]):
        cards.append("""        <div class="col-lg-4 col-md-6">
          <div class="card card-glass h-100 p-4 invariant-card">
            <div class="d-flex align-items-center gap-3 mb-3">
              <span class="sp-icon-box"><i class="bi %s" aria-hidden="true"></i></span>
              <h3 class="h6 text-white fw-bold mb-0">%s</h3>
            </div>
            <p class="text-secondary small mb-0">%s</p>
          </div>
        </div>""" % (icon, E(inv["t"]), E(inv["d"])))
    return """  <!-- Private by design -->
  <section class="py-5" id="privacy">
    <div class="container py-4">
%s
      <div class="row g-4">
%s
      </div>
      <p class="text-center mt-4 mb-0"><a class="link-primary fw-semibold" href="%s"><i class="bi bi-file-earmark-lock me-1" aria-hidden="true"></i>%s</a></p>
    </div>
  </section>
""" % (section_head("bi-shield-lock-fill", t["inv_eyebrow"], t["inv_h"], t["inv_sub"]),
       "\n".join(cards), PRIVACY_URL, E(privacy_label(code)))


def render_steps(code, t, lst):
    out = []
    for n, (icon, s) in enumerate(zip(STEP_ICONS, t["steps"]), 1):
        out.append("""          <div class="col-lg-4">
            <div class="card card-glass h-100 p-4 text-center">
              <div class="sp-step mx-auto mb-3">%d</div>
              <i class="bi %s text-primary fs-3 mb-2" aria-hidden="true"></i>
              <h3 class="h5 text-white fw-bold mb-2">%s</h3>
              <p class="text-secondary small mb-0">%s</p>
            </div>
          </div>""" % (n, icon, E(s["t"]), E(s["d"])))
    return """  <!-- Switching from Google Photos -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="switch">
    <div class="container py-4">
%s
      <div class="row g-4 mb-4">
%s
      </div>
      <div class="sp-note d-flex gap-3 align-items-start mx-auto mb-5">
        <i class="bi bi-arrow-repeat text-primary fs-4 flex-shrink-0" aria-hidden="true"></i>
        <p class="text-secondary mb-0">%s</p>
      </div>
      <div class="row justify-content-center">
        <div class="col-lg-10">
          <figure class="card card-glass sp-shot m-0">
            <img src="%s" alt="%s" loading="lazy" decoding="async" width="%d" height="%d">
            <figcaption><i class="bi bi-box-arrow-in-down me-2" aria-hidden="true"></i>%s</figcaption>
          </figure>
        </div>
      </div>
    </div>
  </section>
""" % (section_head("bi-box-arrow-in-down", t["steps_eyebrow"], t["steps_h"], t["steps_sub"]),
       "\n".join(out), E(t["steps_more"]), shot_url(code, "switch"), E(lst["captions"][3]), SHOT_W, SHOT_H,
       E(lst["captions"][3]))


def render_gallery(code, t, lst):
    cards = []
    # The import slide already has its own place under the switching steps.
    for i, slug in enumerate(SLIDES[1:], 1):
        if slug == "switch":
            continue
        cap = lst["captions"][i]
        cards.append("""        <div class="col-md-6">
          <figure class="card card-glass sp-shot h-100">
            <img src="%s" alt="%s" loading="lazy" decoding="async" width="%d" height="%d">
            <figcaption><i class="bi %s me-2" aria-hidden="true"></i>%s</figcaption>
          </figure>
        </div>""" % (shot_url(code, slug), E(cap), SHOT_W, SHOT_H, GALLERY_ICONS[i - 1], E(cap)))
    return """  <!-- Screenshots -->
  <section class="py-5" id="screenshots">
    <div class="container py-4">
%s
      <div class="row g-4">
%s
      </div>
    </div>
  </section>
""" % (section_head("bi-images", t["gal_eyebrow"], t["gal_h"], t["gal_sub"]), "\n".join(cards))


def render_features(code, t, lst):
    cards = []
    for icon, para in zip(FEATURE_ICONS, lst["description"][2:10]):
        head, body = split_heading(code, para)
        cards.append("""        <div class="col-lg-3 col-md-6">
          <div class="card card-glass h-100 p-4 pillar-card border border-secondary-subtle">
            <div class="d-flex align-items-center gap-2 mb-3">
              <span class="sp-icon-box sp-icon-box-sm"><i class="bi %s" aria-hidden="true"></i></span>
              <h3 class="h6 text-white fw-bold mb-0">%s</h3>
            </div>
            <p class="text-secondary small mb-0">%s</p>
          </div>
        </div>""" % (icon, E(head), E(body)))
    feats = lst["features"]
    half = (len(feats) + 1) // 2
    cols = []
    for chunk in (feats[:half], feats[half:]):
        cols.append("""          <div class="col-md-6">
            <ul class="list-unstyled sp-check-list mb-0">
%s
            </ul>
          </div>""" % "\n".join(
            '              <li><i class="bi bi-check2-circle" aria-hidden="true"></i><span>%s</span></li>' % E(f)
            for f in chunk))
    return """  <!-- Features -->
  <section class="py-5 border-top border-secondary-subtle" id="features">
    <div class="container py-4">
%s
      <div class="row g-4 mb-5">
%s
      </div>
      <div class="card card-glass p-4 p-md-5 border border-primary border-opacity-25">
        <h3 class="h4 text-white fw-bold mb-4"><i class="bi bi-list-check text-primary me-2" aria-hidden="true"></i>%s</h3>
        <div class="row g-3">
%s
        </div>
      </div>
%s    </div>
  </section>
""" % (section_head("bi-stars", t["feat_eyebrow"], t["feat_h"], t["feat_sub"]),
       "\n".join(cards), E(t["all_h"]), "\n".join(cols), cta_strip(t))


def render_ai(code, t, lst):
    _h, privacy_body = split_heading(code, lst["description"][8])
    reqs = "\n".join(
        '              <li><i class="bi bi-check2-circle" aria-hidden="true"></i><span>%s</span></li>' % E(r)
        for r in t["req"])
    return """  <!-- On-device AI -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="ai">
    <div class="container py-4">
      <div class="row gy-5 align-items-center">
        <div class="col-lg-6">
          <div class="sp-icon-box mb-3"><i class="bi bi-cpu-fill" aria-hidden="true"></i></div>
          <h2 class="display-6 fw-bold text-white mb-3">%s</h2>
          <p class="text-secondary mb-3">%s</p>
          <p class="text-secondary mb-0">%s</p>
        </div>
        <div class="col-lg-6">
          <div class="card card-glass p-4 p-md-5 border border-primary border-opacity-25">
            <h3 class="h5 text-white fw-bold mb-3"><i class="bi bi-pc-display text-primary me-2" aria-hidden="true"></i>%s</h3>
            <ul class="list-unstyled sp-check-list mb-0">
%s
            </ul>
          </div>
        </div>
      </div>
    </div>
  </section>
""" % (E(t["ai_h"]), E(privacy_body), E(lst["description"][10]), E(t["req_h"]), reqs)


def render_not_who(t):
    nots = "\n".join("""            <li class="d-flex gap-3 mb-3">
              <i class="bi bi-x-circle text-danger flex-shrink-0 mt-1" aria-hidden="true"></i>
              <span class="text-secondary small">%s</span>
            </li>""" % E(it) for it in t["not_items"])
    return """  <!-- What it is not + who it is for -->
  <section class="py-5">
    <div class="container py-4">
      <div class="row g-4">
        <div class="col-lg-6">
          <div class="card card-glass h-100 p-4">
            <h2 class="h3 text-white fw-bold mb-4">%s</h2>
            <ul class="list-unstyled mb-0">
%s
            </ul>
          </div>
        </div>
        <div class="col-lg-6">
          <div class="card card-glass h-100 p-4 border border-primary border-opacity-25">
            <div class="sp-icon-box mb-3"><i class="bi bi-people-fill" aria-hidden="true"></i></div>
            <h2 class="h3 text-white fw-bold mb-3">%s</h2>
            <p class="text-secondary small mb-0">%s</p>
          </div>
        </div>
      </div>
    </div>
  </section>
""" % (E(t["h_not"]), nots, E(t["h_who"]), E(t["who"]))


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
              <div id="faq%d" class="accordion-collapse collapse%s" aria-labelledby="faq%dHeading" data-bs-parent="#spFaqAccordion">
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
          <div class="accordion accordion-flush" id="spFaqAccordion">
%s
          </div>
        </div>
      </div>
    </div>
  </section>
""" % (section_head("bi-question-circle", t["faq_eyebrow"], t["faq_h"], ""), "\n".join(items))


def render_final(code, t, lst):
    return """  <!-- Final CTA -->
  <section class="py-5">
    <div class="container py-4">
      <div class="card card-glass p-5 text-center border-0 position-relative overflow-hidden" style="background: linear-gradient(135deg, rgba(95,211,174,0.13) 0%%, rgba(31,156,124,0.08) 100%%);">
        <div class="max-w-700 mx-auto position-relative" style="z-index: 2;">
          <div class="mx-auto mb-3" style="width: 90px; height: 90px;">
            <img src="%s" alt="Smart Photos Icon" class="w-100 h-100 object-fit-contain" loading="lazy" decoding="async" width="256" height="256">
          </div>
          <h2 class="display-6 fw-bold text-white mb-3">%s</h2>
          <p class="text-secondary fs-5 mb-4">%s</p>
          <div class="d-flex justify-content-center">
            %s
          </div>
          %s
        </div>
      </div>

      <div class="mt-4 p-4 rounded-4 bg-black border border-warning-subtle">
        <div class="d-flex gap-3">
          <i class="bi bi-info-circle-fill text-warning fs-4" aria-hidden="true"></i>
          <div>
            <h2 class="h6 text-warning fw-bold mb-1">%s</h2>
            <p class="small text-secondary mb-2">%s</p>
            <p class="small mb-2"><a class="link-primary" href="%s">%s</a></p>
            <p class="extra-small text-secondary mb-0">%s</p>
          </div>
        </div>
      </div>
    </div>
  </section>
""" % (ICON, E(t["final_h"]), E(lst["short"]), store_button(t), render_price(t, True),
       E(t["h_important"]), E(lst["description"][11]), PRIVACY_URL, E(privacy_label(code)),
       E(lst["description"][12]))


# ------------------------------------------------------------ privacy policy

def _privacy_module():
    """tools/build-privacy.py, for the chrome every app policy page shares."""
    spec = importlib.util.spec_from_file_location(
        "build_privacy", os.path.join(TOOLS, "build-privacy.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_URL = re.compile(r"https?://[^\s)<]+")


def _inline(text):
    """The few inline Markdown constructs the policy uses, as HTML."""
    out = html.escape(text, quote=False)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"<em>\1</em>", out)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    return _URL.sub(lambda m: '<a href="%s" target="_blank" rel="noopener">%s</a>'
                    % (m.group(0), m.group(0)), out)


def _slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def parse_policy(md):
    """Split docs/store/privacy-policy.md into (effective, lead, sections).

    Block quotes are notes to the owner ("host this page at a public URL")
    and are never published. The bold paragraph before the first heading is
    the policy's own short version, which the page shows as its lead.
    """
    effective, lead, sections = "", "", []
    blocks, para, items = None, [], None

    def flush():
        nonlocal para, items, lead
        if para:
            text = " ".join(para)
            if blocks is None:
                lead = text
            else:
                blocks.append(("p", text))
            para = []
        if items is not None:
            if blocks is not None:
                blocks.append(("ul", items))
            items = None

    for raw in md.replace("\r\n", "\n").split("\n"):
        line = raw.rstrip()
        if line.startswith(">"):
            flush()
            continue
        if line.startswith("# "):
            continue
        if line.startswith("Effective:"):
            effective = line[len("Effective:"):].split("\u00b7")[0].strip()
            continue
        if line.startswith("## "):
            flush()
            blocks = []
            sections.append((line[3:].strip(), blocks))
            continue
        if not line.strip():
            flush()
            continue
        if line.startswith("- "):
            if para:
                flush()
            if items is None:
                items = []
            items.append(line[2:].strip())
            continue
        if items is not None and raw.startswith("  "):
            items[-1] += " " + line.strip()
            continue
        para.append(line.strip())
    flush()
    return effective, lead, sections


def privacy_page():
    if not os.path.exists(PRIVACY_MD):
        return None
    mod = _privacy_module()
    with open(PRIVACY_MD, encoding="utf-8") as fh:
        effective, lead, sections = parse_policy(fh.read())
    try:
        d = datetime.date.fromisoformat(effective)
        effective = "%s %d, %d" % (d.strftime("%B"), d.day, d.year)
    except ValueError:
        pass

    secs, items = "", []
    for n, (heading, blocks) in enumerate(sections, 1):
        inner = ""
        for kind, value in blocks:
            if kind == "p":
                inner += "      <p>%s</p>\n" % _inline(value)
            else:
                inner += ("      <ul>\n"
                          + "".join("        <li>%s</li>\n" % _inline(v) for v in value)
                          + "      </ul>\n")
        sid = _slug(heading)
        items.append((sid, heading))
        secs += mod.section(n, sid, heading, inner)

    body = """<main id="main" class="page">

    <header class="header">
      <a href="/smart-photos/">&larr; Smart Photos</a>
      <h1>Privacy Policy</h1>
      <p class="subtitle">Smart Photos, the on-device AI photo gallery for Windows</p>
      <span class="effective-date">Effective date: %s</span>
    </header>

    <div class="callout highlight">
      <p>%s</p>
    </div>

%s
%s%s""" % (E(effective), _inline(lead), mod.toc(items), secs, mod.footer())
    return mod.shell("Privacy Policy | Smart Photos",
                     "How Smart Photos handles your data: photos, faces and "
                     "searches stay on your PC, nothing is collected, and the only "
                     "download is the AI models.", body)


def build(code):
    t = dict(S["en"])
    t.update(S.get(code, {}))
    lst = LISTING[code]
    _c, label, direction, hl, og = BY_CODE[code]
    # No " | Dhinovatech" suffix: Google shows the site name on its own line
    # above the title now, and the suffix only pushed the keyword out of the
    # ~60 characters a result shows.
    title = t["seo_title"]
    desc = t["seo_desc"]

    og_alts = "\n".join('  <meta property="og:locale:alternate" content="%s">' % o
                        for c2, _l, _d, _h, o in built_langs() if c2 != code)

    body = "\n".join([
        # What the app does comes first; the Google Photos comparison, which
        # is mostly there for search, follows once the reader has seen it.
        render_hero(code, t, lst),
        render_gallery(code, t, lst),
        render_pricing(t),
        render_features(code, t, lst),
        render_steps(code, t, lst),
        render_why(t, lst),
        render_compare(t, lst),
        render_invariants(code, t),
        render_ai(code, t, lst),
        render_not_who(t),
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
<!-- Navigation Bar (independent Smart Photos tree) -->
{navbar}
<main id="main">

{body}
</main>
{footer}
  <!-- Bootstrap 5.3 JS Bundle -->
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
  <script src="/assets/js/nav.js"></script>

  <!-- BEGIN generated UX block -->
  <div class="install-bar" role="complementary" aria-label="Smart Photos">
    <img src="{icon}" alt="" width="42" height="42" loading="lazy" decoding="async">
    <div class="install-bar-text">
      <div class="install-bar-title">Smart Photos</div>
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
        hl=hl, dir=direction, title=E(title), desc=E(desc),
        analytics_block=analytics_block(), page_css=PAGE_CSS,
        hreflang=hreflang_block(code), canonical=abs_url(code), site=SITE,
        ogimg=OGIMG, ogw=OGW, ogh=OGH, ogalt=E(OGALT), og=og, og_alts=og_alts,
        schema=schema(code, t, desc), hero_shot=shot_url(code, "hero"),
        navbar=navbar(code, t), body=body, footer=FOOTER, icon=ICON,
        store=E(STORE_UTM), cta_install=E(t["cta_install"]),
        consent_banner=consent_banner_html(code))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    base = os.path.join(ROOT, SECTION)
    for code, _label, _d, _hl, _og in built_langs():
        folder = base if code == "en" else os.path.join(base, code)
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, "index.html")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(build(code))
        missing = [k for k in S["en"] if k not in S.get(code, {})]
        print("wrote %s%s" % (os.path.relpath(path, ROOT),
                              "  (English fallback: %d keys)" % len(missing) if code != "en" and missing else ""))
    page = privacy_page()
    if page:
        path = os.path.join(base, "privacy.html")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(page)
        print("wrote %s" % os.path.relpath(path, ROOT))
    else:
        print("  ! %s missing - privacy page not written" % os.path.relpath(PRIVACY_MD, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
