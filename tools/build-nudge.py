#!/usr/bin/env python3
"""
Generate /nudge/ - "Nudge", the Microsoft Store (WinUI 3) offline journal and
diary with an on-device AI companion, in 50 languages.

Built on the same template as /smart-photos/ and /stow/: its own navigation
tree whose language switcher lists only the Nudge locales, every CTA pointing
at the Microsoft Store listing, real store slides in the hero and the gallery,
and the install bar / back-to-top chrome wrapped in tools/build-ux.py's
BEGIN/END markers so that builder replaces it rather than appending a copy.

The copy comes from two files:

  * tools/nudge-listing.json - the store listing's own translated text (title,
    short description, description, feature bullets, slide captions) and the
    words on the store slides (hero lines, overview tiles, slide headlines and
    bullets), refreshed from the app repository by tools/build-nudge-shots.py.
    Almost everything on the page is this text, so the page and the store
    listing say the same thing, in the same words, in every language.
  * tools/nudge-strings.json - the little that is written for this page: the
    button labels, three section headings and the FAQ questions. The FAQ
    answers are lines of the store description, picked by position.

No price is printed. The listing itself never states one (it differs by market
and goes on sale); the only offer named is the 15-day free trial, followed by
a one-time purchase with no subscription.

Store links are ordinary https://apps.microsoft.com/detail/... URLs so they
work everywhere and stay crawlable; assets/js/ux.js upgrades them to
ms-windows-store:// in place when the visitor is on Windows.

Run:  python tools/build-nudge.py
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


S = _load("nudge-strings.json")
LISTING = _load("nudge-listing.json")
CONSENT_L = _load("consent-strings.json")

SECTION = "nudge"
SITE = "https://www.dhinovatech.com"
STORE_ID = "9MV92P7RLDGB"
STORE = "https://apps.microsoft.com/detail/" + STORE_ID
STORE_UTM = STORE + "?ocid=dhinovatech_nudge"
# The US list price, for the Offer in the structured data only (an Offer with
# no price is dropped by search engines). It was checked against the Store on
# 2026-10-14; the page itself prints no price - see the module docstring.
LIST_PRICE_USD = "14.99"

ICON = "/assets/images/nudge-icon.png"
# When the page's copy last changed in substance; the WebPage schema reports it.
MODIFIED = "2026-10-14"
OGIMG = "/assets/images/nudge-og.png"
OGW, OGH = 1200, 630
OGALT = "Nudge - private offline journal and diary for Windows, on the Microsoft Store"

# The store slides tools/build-nudge-shots.py writes. "hero" is slide 1; the
# other eight are slides 3-10, in the order of listing "shots" (and of
# listing "captions"[2:]).
HERO = "hero"
SHOTS = ["companion", "private", "ask", "timeline", "insights", "journeys",
         "files", "languages"]
SHOT_W, SHOT_H = 1200, 675
SHOT_ICONS = ["bi-stars", "bi-shield-lock", "bi-chat-left-quote", "bi-clock-history",
              "bi-pie-chart", "bi-compass", "bi-folder2-open", "bi-translate"]
# The eight overview tiles of store slide 2, in store order.
TILE_ICONS = ["bi-shield-lock", "bi-stars", "bi-fingerprint", "bi-chat-left-quote",
              "bi-graph-up", "bi-compass", "bi-file-earmark-text", "bi-globe2"]
CHIP_ICONS = ["bi-chat-heart text-primary", "bi-fingerprint text-info",
              "bi-cloud-slash text-warning"]
# Description paragraphs 3-6 of the store listing: a heading line, then four
# bullets each.
BLOCKS = [(2, "bi-shield-lock-fill"), (3, "bi-cpu"), (4, "bi-pen"), (5, "bi-search")]

# Locales the tree used to carry and no longer does: old code -> where its
# URL now sends the reader. Malay is not one of the app's 49 interface
# languages and has no store listing, so there is no text or slide to build
# it from; the URL is kept alive as a redirect rather than left to 404.
RETIRED = {"ms": "en"}

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

# (code, menu label, dir, hreflang, og locale)
LANGS = [
    ("en", "English", "ltr", "en", "en_US"),
    ("ar", "العربية (Arabic)", "rtl", "ar", "ar_AR"),
    ("zh", "简体中文 (Simplified Chinese)", "ltr", "zh-Hans", "zh_CN"),
    ("es", "Español (Spanish)", "ltr", "es", "es_ES"),
    ("ja", "日本語 (Japanese)", "ltr", "ja", "ja_JP"),
    ("de", "Deutsch (German)", "ltr", "de", "de_DE"),
    ("fr", "Français (French)", "ltr", "fr", "fr_FR"),
    ("ko", "한국어 (Korean)", "ltr", "ko", "ko_KR"),
    ("hi", "हिन्दी (Hindi)", "ltr", "hi", "hi_IN"),
    ("pt", "Português - Brasil (Portuguese BR)", "ltr", "pt", "pt_BR"),
    ("pt-pt", "Português - Portugal (Portuguese PT)", "ltr", "pt-PT", "pt_PT"),
    ("id", "Bahasa Indonesia (Indonesian)", "ltr", "id", "id_ID"),
    ("ru", "Русский (Russian)", "ltr", "ru", "ru_RU"),
    ("tr", "Türkçe (Turkish)", "ltr", "tr", "tr_TR"),
    ("it", "Italiano (Italian)", "ltr", "it", "it_IT"),
    ("nl", "Nederlands (Dutch)", "ltr", "nl", "nl_NL"),
    ("pl", "Polski (Polish)", "ltr", "pl", "pl_PL"),
    ("th", "ไทย (Thai)", "ltr", "th", "th_TH"),
    ("fa", "فارسی (Persian / Farsi)", "rtl", "fa", "fa_IR"),
    ("sv", "Svenska (Swedish)", "ltr", "sv", "sv_SE"),
    ("vi", "Tiếng Việt (Vietnamese)", "ltr", "vi", "vi_VN"),
    ("bn", "বাংলা (Bengali)", "ltr", "bn", "bn_IN"),
    ("yue", "繁體中文 (Cantonese / Traditional)", "ltr", "zh-HK", "zh_HK"),
    ("tl", "Tagalog (Filipino)", "ltr", "tl", "tl_PH"),
    ("uk", "Українська (Ukrainian)", "ltr", "uk", "uk_UA"),
    ("cs", "Čeština (Czech)", "ltr", "cs", "cs_CZ"),
    ("ro", "Română (Romanian)", "ltr", "ro", "ro_RO"),
    ("he", "עברית (Hebrew)", "rtl", "he", "he_IL"),
    ("el", "Ελληνικά (Greek)", "ltr", "el", "el_GR"),
    ("hu", "Magyar (Hungarian)", "ltr", "hu", "hu_HU"),
    ("da", "Dansk (Danish)", "ltr", "da", "da_DK"),
    ("fi", "Suomi (Finnish)", "ltr", "fi", "fi_FI"),
    ("nb", "Norsk (Norwegian Bokmål)", "ltr", "nb", "nb_NO"),
    ("te", "తెలుగు (Telugu)", "ltr", "te", "te_IN"),
    ("mr", "मराठी (Marathi)", "ltr", "mr", "mr_IN"),
    ("ta", "தமிழ் (Tamil)", "ltr", "ta", "ta_IN"),
    ("gu", "ગુજરાતી (Gujarati)", "ltr", "gu", "gu_IN"),
    ("ur", "اردو (Urdu)", "rtl", "ur", "ur_PK"),
    ("pa", "ਪੰਜਾਬੀ (Punjabi)", "ltr", "pa", "pa_IN"),
    ("ml", "മലയാളം (Malayalam)", "ltr", "ml", "ml_IN"),
    ("kn", "ಕನ್ನಡ (Kannada)", "ltr", "kn", "kn_IN"),
    ("jv", "Basa Jawa (Javanese)", "ltr", "jv", "jv_ID"),
    ("sw", "Kiswahili (Swahili)", "ltr", "sw", "sw_KE"),
    ("ha", "Hausa", "ltr", "ha", "ha_NG"),
    ("yo", "Yorùbá (Yoruba)", "ltr", "yo", "yo_NG"),
    ("my", "မြန်မာစာ (Burmese)", "ltr", "my", "my_MM"),
    ("am", "አማርኛ (Amharic)", "ltr", "am", "am_ET"),
    ("kk", "Қазақ тілі (Kazakh)", "ltr", "kk", "kk_KZ"),
    ("sk", "Slovenčina (Slovak)", "ltr", "sk", "sk_SK"),
    ("ca", "Català (Catalan)", "ltr", "ca", "ca_ES"),
]
BY_CODE = {row[0]: row for row in LANGS}

E = html.escape


def url_for(code):
    return "/%s/" % SECTION if code == "en" else "/%s/%s/" % (SECTION, code)


def abs_url(code):
    return SITE + url_for(code)


def shot_url(code, slug):
    rel = "assets/images/nudge/%s/%s.webp" % (code, slug)
    if code != "en" and not os.path.exists(os.path.join(ROOT, rel)):
        rel = "assets/images/nudge/en/%s.webp" % slug
    return "/" + rel


def built_langs():
    return [x for x in LANGS if x[0] in LISTING]


def block(lst, n):
    """Store description paragraph n as (heading, [bullets])."""
    lines = [l.strip() for l in lst["description"][n].split("\n") if l.strip()]
    return lines[0], [l.lstrip("•").strip() for l in lines[1:]]


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
# Shared navigation - Nudge owns its own language tree.
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

          <!-- Our Apps - Nudge owns its own language tree -->
          <li class="nav-item dropdown">
            <a class="nav-link nav-link-custom dropdown-toggle active" href="#" id="appsDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
              Our Apps
            </a>
            <ul class="dropdown-menu dropdown-menu-dark border-secondary shadow-lg mt-2" aria-labelledby="appsDropdown">
              <li class="dropdown-submenu position-relative">
                <a class="dropdown-item py-2 d-flex align-items-center justify-content-between" href="/nudge/">
                  <span><img src="__ICON__" alt="Nudge Icon" style="width: 20px; height: 20px; border-radius: 5px; object-fit: cover;" class="me-2" decoding="async" width="256" height="256">Nudge Offline Journal</span>
                  <span class="badge bg-primary-subtle text-primary border border-primary-subtle rounded-pill ms-2 extra-small submenu-toggle-btn" role="button" title="View __N__ Languages">__N__ Languages <i class="bi bi-chevron-down ms-1" aria-hidden="true"></i></span>
                </a>
                <ul class="dropdown-menu dropdown-menu-dark border-secondary shadow-lg scrollable-menu" style="max-height: 360px; overflow-y: auto;">
                  __LANG_SUBMENU__
                </ul>
              </li>
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

          <!-- Language Selector - Nudge only -->
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
            <li><a href="/privacy.html" class="footer-link">Privacy Policy</a></li>
            <li><a href="/terms.html" class="footer-link">Terms of Service</a></li>
          </ul>
        </div>
        <div class="col-lg-3 col-6">
          <h4 class="h6 text-white fw-bold mb-3">Our Applications</h4>
          <ul class="list-unstyled small d-flex flex-column gap-2 mb-0">
            <li><a href="/smart-photos/" class="footer-link"><i class="bi bi-images me-1" aria-hidden="true"></i> Smart Photos</a></li>
            <li><a href="/KeepOne/" class="footer-link"><i class="bi bi-intersect me-1" aria-hidden="true"></i> KeepOne Duplicate Finder</a></li>
            <li><a href="/nudge/" class="footer-link text-primary fw-semibold"><i class="bi bi-journal-bookmark-fill me-1" aria-hidden="true"></i> Nudge Offline Journal &amp; AI</a></li>
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

# Same structure as the Smart Photos page, re-keyed to the warm gold the
# store slides and the app's own accent use. The custom properties are
# declared site-wide in custom.css, so re-declaring them here re-keys the
# shared chrome for this section only. Blue stays reserved for the Microsoft
# Store buttons (.btn-primary, .btn-store-ms are not touched).
PAGE_CSS = """  <style>
    :root {
      --dhin-accent-blue: #ffc978;
      --dhin-border-glow: rgba(255, 201, 120, 0.32);
      --dhin-shadow-glow: 0 0 25px rgba(255, 201, 120, 0.2);
      --dhin-gradient-primary: linear-gradient(135deg, #ffc978 0%, #c8853d 100%);
      --nd-gold: #ffc978;
      --nd-ink: #2a1a08;
    }
    :root, [data-bs-theme="dark"] {
      --bs-primary-rgb: 255, 201, 120;
      --bs-primary-bg-subtle: rgba(255, 201, 120, 0.12);
      --bs-primary-border-subtle: rgba(255, 201, 120, 0.32);
      --bs-primary-text-emphasis: #ffdca6;
    }
    .text-gradient {
      background: linear-gradient(135deg, #ffe7c2 0%, #ffc978 55%, #c8853d 100%);
      -webkit-background-clip: text;
      background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .btn-dhin-primary { box-shadow: 0 4px 15px rgba(255, 201, 120, 0.26); }
    .btn-dhin-primary:hover { box-shadow: 0 8px 25px rgba(255, 201, 120, 0.4); }
    .btn-dhin-outline:hover { background: rgba(255, 201, 120, 0.1); }
    .hero-section {
      padding: 56px 0 64px;
      background: radial-gradient(circle at 22% 18%, rgba(200, 133, 61, 0.2) 0%, rgba(8, 12, 20, 0) 62%);
    }
    @media (max-width: 991.98px) { .hero-section { padding: 32px 0 48px; } }
    .hero-title { overflow-wrap: anywhere; }

    .glow-aura-gold { box-shadow: 0 0 45px rgba(255, 201, 120, 0.22); }
    .nd-icon-box {
      width: 52px; height: 52px; border-radius: 14px;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.4rem; flex-shrink: 0;
      background: linear-gradient(135deg, rgba(255,201,120,0.18), rgba(200,133,61,0.12));
      color: var(--nd-gold); border: 1px solid rgba(255,201,120,0.3);
    }
    .nd-icon-box-sm { width: 38px; height: 38px; font-size: 1.1rem; border-radius: 10px; }
    .nd-badge-row { display: flex; flex-wrap: wrap; gap: .5rem; }

    /* Hero */
    .nd-hero-icon { width: 60px; height: 60px; flex-shrink: 0; }
    .nd-hero-icon img { width: 100%; height: 100%; object-fit: cover; display: block; border-radius: 14px; }
    .nd-hero-kind { font-weight: 600; color: #e2e8f0; font-size: .95rem; line-height: 1.3; }
    .nd-hero-tagline {
      font-size: clamp(1.15rem, 1rem + 0.8vw, 1.6rem); font-weight: 500;
      line-height: 1.35; letter-spacing: 0; color: #ffdca6; margin-top: .6rem;
    }
    .nd-cta-strip .nd-price { margin: 0; }
    .nd-price {
      display: flex; align-items: center; gap: .5rem; flex-wrap: wrap;
      font-size: .92rem; color: #cbd5e1;
    }
    .nd-price-tag {
      background: var(--nd-gold); color: var(--nd-ink);
      border-radius: 20px; padding: 3px 14px; font-size: .95rem; font-weight: 800;
      white-space: nowrap; text-decoration: none;
      box-shadow: 0 0 18px rgba(255, 201, 120, .32);
    }
    .nd-price-tag:hover { color: var(--nd-ink); background: #ffd699; }
    .nd-window {
      border-radius: 14px; overflow: hidden; background: #1c1410;
      border: 1px solid rgba(255,255,255,.12);
      box-shadow: 0 30px 70px -25px rgba(0,0,0,.9);
    }
    .nd-window img { display: block; width: 100%; height: auto; }

    .nd-narrow { max-width: 760px; }

    /* Screenshot gallery */
    .nd-shot { overflow: hidden; margin: 0; }
    .nd-shot img { display: block; width: 100%; height: auto; border-bottom: 1px solid rgba(255,255,255,.07); }
    .nd-shot figcaption { padding: .85rem 1rem; font-size: .9rem; font-weight: 600; color: #e2e8f0; }
    .nd-shot figcaption i { color: var(--nd-gold); }

    /* Cards */
    .invariant-card { border-left: 3px solid var(--nd-gold) !important; transition: transform .2s ease, box-shadow .2s ease; }
    [dir="rtl"] .invariant-card { border-left: 0 !important; border-right: 3px solid var(--nd-gold) !important; }
    .invariant-card:hover { transform: translateY(-3px); box-shadow: 0 10px 30px rgba(255, 201, 120, 0.12); }
    .pillar-card { transition: transform .2s ease, border-color .2s ease; }
    .pillar-card:hover { transform: translateY(-3px); border-color: rgba(255, 201, 120, 0.4) !important; }
    .nd-check-list li { display: flex; gap: .6rem; margin-bottom: .6rem; font-size: .9rem; color: #cbd5e1; }
    .nd-check-list li i { color: var(--nd-gold); flex-shrink: 0; margin-top: .1rem; }
    .nd-block-h { font-size: 1.05rem; line-height: 1.35; }

    /* Trial */
    .nd-plan { border: 2px solid var(--nd-gold) !important; box-shadow: 0 0 40px rgba(255, 201, 120, .16); }

    /* FAQ */
    .accordion-button:not(.collapsed) { background: rgba(255, 201, 120, 0.08); color: var(--nd-gold); box-shadow: none; }
    .accordion-button:focus { box-shadow: 0 0 0 0.2rem rgba(255, 201, 120, 0.25); }
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


def faqs(t, lst):
    """The FAQ: this page's questions, answered in the store listing's words.

    Each answer is one or more whole lines of the store description, picked
    by position, so it is already translated and can never drift from what
    the listing promises. The order follows t["faq_q"].
    """
    d = lst["description"]
    _h, private = block(lst, 2)
    _h, ai = block(lst, 3)
    _h, keep = block(lst, 5)
    trial = d[6].split("\n", 1)[1].strip()
    answers = [
        trial,                                      # what it costs
        "%s %s" % (private[3], private[0]),         # works without the internet
        d[1],                                       # where entries live
        "%s %s" % (private[1], private[2]),         # lock
        "%s %s %s" % (ai[0], ai[2], ai[3]),         # the AI companion
        ai[1],                                      # ask your journal
        keep[1],                                    # import and export
        keep[3],                                    # languages
    ]
    return [{"q": q, "a": a} for q, a in zip(t["faq_q"], answers)]


def schema(code, t, lst, title, desc):
    graph = [
        {"@type": "Organization", "@id": SITE + "/#organization",
         "name": "Dhinovatech", "url": SITE + "/"},
        {"@type": "SoftwareApplication",
         "@id": SITE + "/nudge/#software",
         "name": "Nudge",
         "alternateName": lst["title"],
         "operatingSystem": "Windows 10 version 1809 (build 17763) and later, x64 and ARM64",
         "applicationCategory": "LifestyleApplication",
         "applicationSubCategory": "Journal and diary",
         "description": desc,
         "url": abs_url(code),
         "inLanguage": [hl for _c, _l, _d, hl, _og in built_langs()],
         "image": SITE + ICON,
         "downloadUrl": STORE,
         "installUrl": STORE,
         "featureList": lst["features"],
         "processorRequirements": "x64 or ARM64",
         "offers": {"@type": "Offer", "price": LIST_PRICE_USD, "priceCurrency": "USD",
                    "availability": "https://schema.org/InStock", "url": STORE},
         "screenshot": [SITE + shot_url(code, s) for s in [HERO] + SHOTS],
         "publisher": {"@id": SITE + "/#organization"},
         "author": {"@id": SITE + "/#organization"}},
        {"@type": "WebPage", "@id": abs_url(code) + "#webpage", "url": abs_url(code),
         "name": title, "description": desc, "inLanguage": BY_CODE[code][3],
         "dateModified": MODIFIED, "about": {"@id": SITE + "/nudge/#software"},
         "mainEntity": {"@id": SITE + "/nudge/#software"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Nudge", "item": abs_url("en")},
        ]},
        {"@type": "FAQPage", "@id": abs_url(code) + "#faq",
         "inLanguage": BY_CODE[code][3],
         "mainEntity": [{"@type": "Question", "name": f["q"],
                         "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
                        for f in faqs(t, lst)]},
    ]
    if code != "en":
        graph[3]["itemListElement"].append(
            {"@type": "ListItem", "position": 3,
             "name": "Nudge (%s)" % code, "item": abs_url(code)})
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
                   '<p class="text-secondary fs-5 mx-auto nd-narrow">%s</p>' % E(sub) if sub else "")


def store_button(t):
    return """<a href="%s" target="_blank" rel="noopener" class="btn btn-store btn-store-ms shadow-lg">
              <i class="bi bi-microsoft" aria-hidden="true"></i>
              <span class="btn-store-copy">
                <span class="btn-store-pre">%s</span>
                <span class="btn-store-name">Microsoft Store</span>
              </span>
            </a>""" % (E(STORE_UTM), E(t["store_pre"]))


def store_kind(code, lst):
    """What the app is, in the reader's language, for the line beside the icon.

    A listing title is "Nudge - <descriptor>", and where the name has been
    reserved in that language the descriptor is the store's own keyword
    choice for that market. Where it has not, the title is still the English
    one, and the slide tagline ("Journal & diary for Windows"), which is
    translated everywhere, says the same thing.
    """
    title = lst["title"]
    if code != "en" and title == LISTING["en"]["title"]:
        return lst["tagline"]
    for sep in (" - ", " – ", ": "):
        if title.startswith("Nudge" + sep):
            return title[len("Nudge" + sep):]
    return lst["tagline"]


def seo_title(code, lst):
    # No " | Dhinovatech" suffix: search results show the site name on its
    # own line, and the suffix only pushes the keywords out of view.
    if code == "en":
        return lst["title"] + " for Windows"
    return "Nudge - " + store_kind(code, lst)


def render_price(lst, centred=False):
    return ('<p class="nd-price mt-3 mb-0%s"><a class="nd-price-tag" href="#pricing">'
            '<i class="bi bi-gift-fill me-1" aria-hidden="true"></i>%s</a>'
            '<span>%s</span></p>'
            % (" justify-content-center" if centred else "",
               E(lst["trial"]), E(lst["shots"][7]["bullets"][2])))


def cta_strip(t, lst):
    """The store button again, where a reader who is convinced looks for it."""
    return """      <div class="nd-cta-strip d-flex flex-column flex-md-row align-items-center justify-content-center gap-3 mt-5">
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
            <span class="nd-hero-icon">
              <img src="%(icon)s" alt="" decoding="async" width="256" height="256">
            </span>
            <span>
              <span class="d-block nd-hero-kind">%(kind)s</span>
              <span class="d-block small text-secondary">
                <i class="bi bi-microsoft me-1" aria-hidden="true"></i>Microsoft Store &middot; Windows 10 &amp; 11
              </span>
            </span>
          </div>

          <h1 class="hero-title mb-3"><span class="d-block">Nudge</span> <span class="d-block nd-hero-tagline">%(h1)s</span></h1>
          <p class="lead text-secondary mb-4 pe-lg-4 fs-5">%(lead)s</p>

          <div class="d-flex flex-wrap gap-3 align-items-center">
            %(store)s
            <a href="#screenshots" class="btn btn-dhin-outline btn-lg rounded-pill px-4">
              <i class="bi bi-images me-2" aria-hidden="true"></i> %(cta_see)s
            </a>
          </div>
          %(price)s

          <div class="nd-badge-row pt-4 mt-2">
%(badges)s
          </div>
        </div>

        <div class="col-lg-6">
          <div class="position-relative">
            <div class="position-absolute top-50 start-50 translate-middle w-100 h-100 rounded-circle bg-primary opacity-25 blur-3xl glow-aura-gold" aria-hidden="true"></div>
            <div class="nd-window position-relative">
              <img src="%(hero)s" alt="%(hero_alt)s" decoding="async" fetchpriority="high" width="%(w)d" height="%(h)d">
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
""" % dict(icon=ICON, kind=E(store_kind(code, lst)),
           h1=E("%s %s" % (lst["line1"], lst["line2"])), lead=E(lst["short"]),
           store=store_button(t), cta_see=E(t["shots"]), price=render_price(lst),
           badges=badges, hero=shot_url(code, HERO), hero_alt=E(lst["captions"][0]),
           w=SHOT_W, h=SHOT_H)


def render_overview(lst):
    """Store slide 2 as real text: the eight things the app is, at a glance."""
    ov = lst["overview"]
    tiles = []
    for icon, (name, what) in zip(TILE_ICONS, ov["tiles"]):
        tiles.append("""        <div class="col-lg-3 col-md-6">
          <div class="card card-glass h-100 p-4 pillar-card border border-secondary-subtle">
            <span class="nd-icon-box mb-3"><i class="bi %s" aria-hidden="true"></i></span>
            <h3 class="h6 text-white fw-bold mb-2">%s</h3>
            <p class="text-secondary small mb-0">%s</p>
          </div>
        </div>""" % (icon, E(name), E(what)))
    return """  <!-- Overview -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="overview">
    <div class="container py-4">
%s
      <div class="row g-4">
%s
      </div>
    </div>
  </section>
""" % (section_head("bi-journal-bookmark-fill", ov["kicker"], ov["title"],
                    lst["description"][1]), "\n".join(tiles))


def render_gallery(code, t, lst):
    cards = []
    for i, (slug, icon) in enumerate(zip(SHOTS, SHOT_ICONS)):
        cap = lst["captions"][i + 2]
        cards.append("""        <div class="col-md-6">
          <figure class="card card-glass nd-shot h-100">
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


def check_items(rows, indent="              "):
    return "\n".join(
        '%s<li><i class="bi bi-check2-circle" aria-hidden="true"></i><span>%s</span></li>'
        % (indent, E(r)) for r in rows)


def render_features(t, lst):
    cards = []
    for n, icon in BLOCKS:
        head, bullets = block(lst, n)
        cards.append("""        <div class="col-lg-6">
          <div class="card card-glass h-100 p-4 invariant-card">
            <div class="d-flex align-items-center gap-3 mb-3">
              <span class="nd-icon-box nd-icon-box-sm"><i class="bi %s" aria-hidden="true"></i></span>
              <h3 class="nd-block-h text-white fw-bold mb-0">%s</h3>
            </div>
            <ul class="list-unstyled nd-check-list mb-0">
%s
            </ul>
          </div>
        </div>""" % (icon, E(head), check_items(bullets)))
    feats = lst["features"]
    half = (len(feats) + 1) // 2
    cols = []
    for chunk in (feats[:half], feats[half:]):
        cols.append("""          <div class="col-md-6">
            <ul class="list-unstyled nd-check-list mb-0">
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
        <div class="row g-3">
%s
        </div>
      </div>
    </div>
  </section>
""" % (section_head("bi-stars", t["feat"], t["feat_h"], ""), "\n".join(cards), "\n".join(cols))


def render_pricing(t, lst):
    """The offer, exactly as the store listing states it.

    Fifteen days of every feature, then a one-time purchase: no subscription,
    no add-ons, no ads, and entries stay readable if you never buy. No price:
    the Store shows the current one for the reader's market.
    """
    body = lst["description"][6].split("\n", 1)[1].strip()
    points = [lst["shots"][7]["bullets"][2], lst["features"][1], lst["features"][5]]
    return """  <!-- Free trial, then one purchase -->
  <section class="py-5" id="pricing">
    <div class="container py-4">
%s
      <div class="row justify-content-center">
        <div class="col-lg-8">
          <div class="card card-glass p-4 p-lg-5 nd-plan">
            <p class="fs-5 text-white mb-4">%s</p>
            <ul class="list-unstyled nd-check-list mb-4">
%s
            </ul>
            <div>%s</div>
          </div>
        </div>
      </div>
    </div>
  </section>
""" % (section_head("bi-gift-fill", "Microsoft Store", lst["trial"], ""), E(body),
       check_items(points), store_button(t))


def render_faq(t, lst):
    items = []
    for i, f in enumerate(faqs(t, lst), 1):
        first = i == 1
        items.append("""            <div class="accordion-item bg-transparent border-bottom border-secondary">
              <h3 class="accordion-header" id="faq%dHeading">
                <button class="accordion-button%s bg-transparent text-white fw-semibold py-4" type="button" data-bs-toggle="collapse" data-bs-target="#faq%d" aria-expanded="%s" aria-controls="faq%d">
                  %s
                </button>
              </h3>
              <div id="faq%d" class="accordion-collapse collapse%s" aria-labelledby="faq%dHeading" data-bs-parent="#nudgeFaqAccordion">
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
          <div class="accordion accordion-flush" id="nudgeFaqAccordion">
%s
          </div>
        </div>
      </div>
    </div>
  </section>
""" % (section_head("bi-question-circle", "FAQ", t["faq_h"], ""), "\n".join(items))


def render_final(t, lst):
    return """  <!-- Final CTA -->
  <section class="py-5">
    <div class="container py-4">
      <div class="card card-glass p-5 text-center border-0 position-relative overflow-hidden" style="background: linear-gradient(135deg, rgba(255,201,120,0.13) 0%%, rgba(200,133,61,0.08) 100%%);">
        <div class="nd-narrow mx-auto position-relative" style="z-index: 2;">
          <div class="mx-auto mb-3" style="width: 90px; height: 90px;">
            <img src="%s" alt="Nudge Icon" class="w-100 h-100 object-fit-cover rounded-4" loading="lazy" decoding="async" width="256" height="256">
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
""" % (ICON, E("%s %s" % (lst["line1"], lst["line2"])), E(lst["description"][0]),
       store_button(t), render_price(lst, True))


def build(code):
    t = dict(S["en"])
    t.update(S.get(code, {}))
    lst = LISTING[code]
    _c, _label, direction, hl, og = BY_CODE[code]
    title = seo_title(code, lst)
    desc = lst["short"]

    og_alts = "\n".join('  <meta property="og:locale:alternate" content="%s">' % o
                        for c2, _l, _d, _h, o in built_langs() if c2 != code)

    body = "\n".join([
        render_hero(code, t, lst),
        # What the app is in eight tiles, then what it looks like, then the
        # detail - the order a reader who has never seen it needs.
        render_overview(lst),
        render_gallery(code, t, lst),
        render_features(t, lst),
        render_pricing(t, lst),
        render_faq(t, lst),
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
<!-- Navigation Bar (independent Nudge tree) -->
{navbar}
<main id="main">

{body}
</main>
{footer}
  <!-- Bootstrap 5.3 JS Bundle -->
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
  <script src="/assets/js/nav.js"></script>

  <!-- BEGIN generated UX block -->
  <div class="install-bar" role="complementary" aria-label="Nudge">
    <img src="{icon}" alt="" width="42" height="42" loading="lazy" decoding="async">
    <div class="install-bar-text">
      <div class="install-bar-title">Nudge</div>
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
        navbar=navbar(code, t), body=body, footer=FOOTER, icon=ICON,
        store=E(STORE_UTM), consent_banner=consent_banner_html(code))


def redirect_page(target):
    """A page that only sends the reader on, for a locale the tree dropped.

    GitHub Pages cannot answer with a 301, so this is the nearest thing: an
    immediate refresh, a canonical pointing at the destination, and noindex
    so the old URL leaves the index (and stays out of sitemap.xml).
    """
    url = abs_url(target)
    return """<!DOCTYPE html>
<html lang="{hl}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Nudge</title>
  <meta name="robots" content="noindex,follow">
  <link rel="canonical" href="{url}">
  <meta http-equiv="refresh" content="0; url={path}">
</head>
<body>
<main id="main">
  <p><a href="{path}">Nudge</a></p>
</main>
</body>
</html>
""".format(hl=BY_CODE[target][3], url=url, path=url_for(target))


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
    for code, target in RETIRED.items():
        folder = os.path.join(base, code)
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, "index.html")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(redirect_page(target))
        print("wrote %s  (redirect to %s)" % (os.path.relpath(path, ROOT), url_for(target)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
