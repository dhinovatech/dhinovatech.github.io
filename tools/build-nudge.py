#!/usr/bin/env python3
"""
Generate /nudge/ - "Nudge — Offline Journal & Diary with AI Companion",
the native WinUI 3 desktop journal for Windows, in 51 languages.

Store ID: 9MV92P7RLDGB
Price: $0.99 (One-time buy, 15-day unrestricted trial, zero subscriptions)

Run: python tools/build-nudge.py
"""
import html
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STRINGS = os.path.join(ROOT, "tools", "nudge-strings.json")
CONSENT_STRINGS = os.path.join(ROOT, "tools", "consent-strings.json")

with open(STRINGS, encoding="utf-8") as _fh:
    L = json.load(_fh)

with open(CONSENT_STRINGS, encoding="utf-8") as _fh:
    CONSENT_L = json.load(_fh)

SECTION = "nudge"
SITE = "https://www.dhinovatech.com"
STORE_ID = "9MV92P7RLDGB"
STORE = "https://apps.microsoft.com/detail/" + STORE_ID
STORE_UTM = STORE + "?ocid=dhinovatech_nudge"

ICON = "/assets/images/nudge-icon.png"
OGIMG = "/assets/images/nudge-icon.png"
OGW, OGH = 512, 512
OGALT = "Nudge offline journal and diary with AI companion icon"

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
    ("ms", "Bahasa Melayu (Malay)", "ltr", "ms", "ms_MY"),
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

BY_CODE = {c: (c, label, d, hl, og) for c, label, d, hl, og in LANGS}
NLANG = len(LANGS)

E = html.escape

def url_for(code):
    return "/%s/" % SECTION if code == "en" else "/%s/%s/" % (SECTION, code)

def abs_url(code):
    return SITE + url_for(code)

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

def lang_items(active, icon):
    out = []
    for code, label, _d, _hl, _og in built_langs():
        cls = "dropdown-item py-1 small"
        icon_cls = "bi %s text-warning me-2" % icon
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

          <!-- Our Apps dropdown -->
          <li class="nav-item dropdown">
            <a class="nav-link nav-link-custom dropdown-toggle active" href="#" id="appsDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
              Our Apps
            </a>
            <ul class="dropdown-menu dropdown-menu-dark border-secondary shadow-lg mt-2" aria-labelledby="appsDropdown">
              <li class="dropdown-submenu position-relative">
                <a class="dropdown-item py-2 d-flex align-items-center justify-content-between" href="/nudge/">
                  <span><img src="__ICON__" alt="Nudge Icon" style="width: 20px; height: 20px; border-radius: 5px; object-fit: cover;" class="me-2" decoding="async" width="256" height="256">Nudge Offline Journal</span>
                  <span class="badge bg-warning-subtle text-warning border border-warning-subtle rounded-pill ms-2 extra-small submenu-toggle-btn" role="button" title="View __N__ Languages">__N__ Languages <i class="bi bi-chevron-down ms-1" aria-hidden="true"></i></span>
                </a>
                <ul class="dropdown-menu dropdown-menu-dark border-secondary shadow-lg scrollable-menu" style="max-height: 360px; overflow-y: auto;">
                  __LANG_SUBMENU__
                </ul>
              </li>
              <li><a class="dropdown-item py-2" href="/stow/"><i class="bi bi-folder-symlink text-info me-2" aria-hidden="true"></i>Stow Photo &amp; File Organizer</a></li>
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

          <!-- Language Selector -->
          <li class="nav-item dropdown ms-lg-2 mt-2 mt-lg-0">
            <button class="btn btn-outline-warning dropdown-toggle fw-semibold px-3 py-2 rounded-3 shadow d-flex align-items-center gap-2" type="button" id="langSelector" data-bs-toggle="dropdown" aria-expanded="false">
              <i class="bi bi-translate fs-5" aria-hidden="true"></i> <span>__LANG_LABEL__</span>
            </button>
            <ul class="dropdown-menu dropdown-menu-dark dropdown-menu-end border-secondary shadow-lg mt-2 scrollable-menu" style="max-height: 380px; overflow-y: auto;" aria-labelledby="langSelector">
              __LANG_SELECTOR__
            </ul>
          </li>

          <!-- Microsoft Store CTA -->
          <li class="nav-item ms-lg-2 mt-3 mt-lg-0">
            <a href="__STORE__" target="_blank" rel="noopener" class="btn btn-warning fw-bold px-3 py-2 rounded-3 shadow d-flex align-items-center gap-2 text-dark">
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
            <li><a href="/privacy.html" class="footer-link">Privacy Policy</a></li>
            <li><a href="/terms.html" class="footer-link">Terms of Service</a></li>
          </ul>
        </div>
        <div class="col-lg-3 col-6">
          <h4 class="h6 text-white fw-bold mb-3">Our Applications</h4>
          <ul class="list-unstyled small d-flex flex-column gap-2 mb-0">
            <li><a href="/nudge/" class="footer-link text-warning fw-semibold"><i class="bi bi-journal-bookmark-fill me-1" aria-hidden="true"></i> Nudge Offline Journal &amp; AI</a></li>
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
          <h4 class="h6 text-white fw-bold mb-3">Support &amp; Ethics</h4>
          <p class="small text-secondary mb-2"><i class="bi bi-envelope-fill me-2 text-warning" aria-hidden="true"></i>support@dhinovatech.com</p>
          <p class="small text-secondary mb-2"><i class="bi bi-shield-check me-2 text-warning" aria-hidden="true"></i>100% Offline Epistemic Privacy</p>
          <p class="small text-secondary"><i class="bi bi-globe me-2 text-warning" aria-hidden="true"></i>www.dhinovatech.com</p>
        </div>
      </div>
      <div class="pt-4 border-top border-secondary text-center text-secondary small">
        <p class="mb-0">&copy; 2026 Dhinovatech. All rights reserved. Nudge is a trademark of Dhinovatech.</p>
      </div>
    </div>
  </footer>
"""

PAGE_CSS = """  <style>
    /* Scoped Nudge accents - warm golden amber & fine stationery leather palette */
    :root {
      --nudge-amber: #f59e0b;
      --nudge-gold: #fbbf24;
      --nudge-amber-glow: rgba(245, 158, 11, 0.32);
      --nudge-bg-dark: #0a0b0d;
      --nudge-card-bg: #121316;
      --nudge-card-border: rgba(245, 158, 11, 0.22);
    }
    .glow-aura-amber {
      box-shadow: 0 0 55px var(--nudge-amber-glow);
    }
    .nudge-icon-box {
      width: 52px; height: 52px; border-radius: 14px;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.4rem; flex-shrink: 0;
      background: linear-gradient(135deg, rgba(245,158,11,0.18), rgba(251,191,36,0.12));
      color: #fbbf24; border: 1px solid rgba(245,158,11,0.35);
    }
    .nudge-num {
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 1.6rem; font-weight: 700; color: #fbbf24; line-height: 1;
    }
    .theme-pill {
      display: inline-flex; align-items: center; gap: 6px;
      padding: 6px 14px; border-radius: 20px;
      background: rgba(245, 158, 11, 0.08);
      border: 1px solid rgba(245, 158, 11, 0.25);
      font-size: 0.85rem; color: #fde68a; text-decoration: none;
      transition: all 0.2s ease;
    }
    .theme-pill:hover {
      background: rgba(245, 158, 11, 0.18);
      border-color: #fbbf24; color: #fff;
    }
    .invariant-card {
      border-left: 3px solid #f59e0b !important;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .invariant-card:hover {
      transform: translateY(-3px);
      box-shadow: 0 10px 30px rgba(245, 158, 11, 0.15);
    }
    .pillar-card {
      transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .pillar-card:hover {
      transform: translateY(-3px);
      border-color: rgba(245, 158, 11, 0.45) !important;
    }
    .feature-bullet-list li {
      position: relative;
      padding-left: 1.4rem;
      margin-bottom: 0.5rem;
      font-size: 0.88rem;
      color: #94a3b8;
    }
    .feature-bullet-list li::before {
      content: "\\u2022";
      position: absolute;
      left: 0.35rem;
      color: #fbbf24;
      font-size: 1.1rem;
      line-height: 1.2;
    }
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
    .compare-table th.nudge-col, .compare-table td.nudge-col {
      background: rgba(245, 158, 11, 0.08);
      border-left: 1px solid rgba(245, 158, 11, 0.25);
      border-right: 1px solid rgba(245, 158, 11, 0.25);
    }
    .nudge-code-box {
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 0.82rem; background: #08090b;
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 12px; padding: 1.25rem; color: #cbd5e1;
      white-space: pre; overflow-x: auto;
    }
    .stationery-token {
      display: inline-block; width: 14px; height: 14px; border-radius: 3px; vertical-align: middle; margin-right: 6px;
    }
    /* RTL adjustments */
    [dir="rtl"] .feature-bullet-list li {
      padding-left: 0;
      padding-right: 1.4rem;
    }
    [dir="rtl"] .feature-bullet-list li::before {
      left: auto;
      right: 0.35rem;
    }
    [dir="rtl"] .invariant-card {
      border-left: none !important;
      border-right: 3px solid #f59e0b !important;
    }
    [dir="rtl"] .dropdown-menu-end {
      right: auto !important;
      left: 0 !important;
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
        {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/",
         "name": "Dhinovatech", "publisher": {"@id": SITE + "/#organization"}},
        {"@type": "SoftwareApplication",
         "@id": abs_url(code) + "#app",
         "name": t["name"],
         "applicationCategory": "LifestyleApplication",
         "operatingSystem": "Windows 10, Windows 11",
         "description": desc,
         "url": abs_url(code),
         "image": SITE + ICON,
         "inLanguage": BY_CODE[code][3],
         "offers": {
             "@type": "Offer",
             "price": "0.99",
             "priceCurrency": "USD",
             "url": STORE,
             "availability": "https://schema.org/InStock",
             "seller": {"@id": SITE + "/#organization"}
         },
         "publisher": {"@id": SITE + "/#organization"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Nudge Offline Journal", "item": abs_url("en")},
        ]},
    ]
    if code != "en":
        graph[2]["itemListElement"].append(
            {"@type": "ListItem", "position": 3,
             "name": "Nudge (%s)" % code, "item": abs_url(code)})

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

def render_pillars(t):
    pillars = t.get("pillars", [])
    cards = []
    for p in pillars:
        cards.append("""          <div class="col-lg-4">
            <div class="card card-glass h-100 p-4 invariant-card border border-secondary-subtle">
              <div class="d-flex align-items-center gap-3 mb-3">
                <span class="nudge-icon-box"><i class="bi %s" aria-hidden="true"></i></span>
                <div>
                  <span class="badge bg-warning-subtle text-warning border border-warning-subtle rounded-pill extra-small px-2 py-0 mb-1">Pillar %s</span>
                  <h3 class="h5 text-white fw-bold mb-0">%s</h3>
                </div>
              </div>
              <p class="text-secondary small mb-0 lh-base">%s</p>
            </div>
          </div>""" % (E(p["icon"]), E(p["num"]), E(p["title"]), E(p["desc"])))
    return """  <!-- The Three Pillars -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="pillars">
    <div class="container py-4">
      <div class="text-center max-w-700 mx-auto mb-5">
        <span class="badge bg-warning-subtle text-warning border border-warning-subtle rounded-pill px-3 py-2 fw-semibold mb-2">
          <i class="bi bi-shield-lock-fill me-1" aria-hidden="true"></i> Architectural Invariants
        </span>
        <h2 class="display-5 fw-bold text-white">%s</h2>
        <p class="text-secondary fs-5">%s</p>
      </div>
      <div class="row g-4">
%s
      </div>
    </div>
  </section>""" % (E(t["h_pillars"]), E(t["pillars_sub"]), "\n".join(cards))

def render_specs_table(t):
    headers = t.get("specs_headers", ["Dimension", "Specification", "Architectural Guarantees"])
    rows = t.get("specs_rows", [])
    rows_html = []
    for r in rows:
        rows_html.append("""              <tr>
                <td class="text-white fw-semibold small text-nowrap align-middle">%s</td>
                <td class="text-warning small align-middle fw-medium">%s</td>
                <td class="text-secondary small align-middle">%s</td>
              </tr>""" % (E(r[0]), E(r[1]), E(r[2])))
    return """  <!-- Technical Specifications Matrix -->
  <section class="py-5" id="specs">
    <div class="container py-4">
      <div class="text-center max-w-700 mx-auto mb-5">
        <span class="badge bg-warning-subtle text-warning border border-warning-subtle rounded-pill px-3 py-2 fw-semibold mb-2">
          <i class="bi bi-table me-1" aria-hidden="true"></i> Technical Matrix
        </span>
        <h2 class="display-5 fw-bold text-white">%s</h2>
        <p class="text-secondary fs-5">%s</p>
      </div>
      <div class="card card-glass p-3 p-md-4 border border-secondary-subtle shadow-lg">
        <div class="table-responsive">
          <table class="table table-dark table-borderless align-middle mb-0 compare-table">
            <thead>
              <tr class="border-bottom border-secondary">
                <th scope="col" style="width: 22%%;">%s</th>
                <th scope="col" style="width: 28%%;" class="text-warning fw-bold">%s</th>
                <th scope="col" style="width: 50%%;">%s</th>
              </tr>
            </thead>
            <tbody>
%s
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </section>""" % (E(t["h_specs"]), E(t["specs_sub"]), E(headers[0]), E(headers[1]), E(headers[2]), "\n".join(rows_html))

def render_manifesto(t):
    return """  <!-- The Manifesto -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="manifesto">
    <div class="container py-4">
      <div class="text-center max-w-700 mx-auto mb-5">
        <span class="badge bg-warning-subtle text-warning border border-warning-subtle rounded-pill px-3 py-2 fw-semibold mb-2">
          <i class="bi bi-feather me-1" aria-hidden="true"></i> First Principles
        </span>
        <h2 class="display-5 fw-bold text-white">%s</h2>
        <p class="text-secondary fs-5">%s</p>
      </div>
      <div class="row g-4">
        <div class="col-lg-4">
          <div class="card card-glass h-100 p-4 border border-secondary-subtle">
            <div class="nudge-icon-box mb-3"><i class="bi bi-cloud-slash" aria-hidden="true"></i></div>
            <h3 class="h5 text-white fw-bold mb-3">%s</h3>
            <p class="text-secondary small mb-0 lh-base">%s</p>
          </div>
        </div>
        <div class="col-lg-4">
          <div class="card card-glass h-100 p-4 border border-secondary-subtle">
            <div class="nudge-icon-box mb-3"><i class="bi bi-eye-slash" aria-hidden="true"></i></div>
            <h3 class="h5 text-white fw-bold mb-3">%s</h3>
            <p class="text-secondary small mb-0 lh-base">%s</p>
          </div>
        </div>
        <div class="col-lg-4">
          <div class="card card-glass h-100 p-4 border border-secondary-subtle">
            <div class="nudge-icon-box mb-3"><i class="bi bi-hourglass-split" aria-hidden="true"></i></div>
            <h3 class="h5 text-white fw-bold mb-3">%s</h3>
            <p class="text-secondary small mb-0 lh-base">%s</p>
          </div>
        </div>
      </div>
    </div>
  </section>""" % (E(t["h_manifesto"]), E(t["manifesto_sub"]),
                   E(t["manifesto_cloud_title"]), E(t["manifesto_cloud_desc"]),
                   E(t["manifesto_epistemic_title"]), E(t["manifesto_epistemic_desc"]),
                   E(t["manifesto_longevity_title"]), E(t["manifesto_longevity_desc"]))

def render_architecture(t):
    code_snippet = """---
id: 01JN9Z8K7P3QW9E1R4T6Y8U2I0
date: 2026-03-15T19:42:10+05:30
language: en
title: Walking Through the Rain in Spring
themes:
  - everyday
  - creativity
mood: 4
weather: overcast
tags:
  - rain
  - reflection
content_hash: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

# Walking Through the Rain in Spring

The smell of damp pine needles hung thick in the cool evening air. I took the longer trail past the old reservoir...
I realized today that the friction I've been feeling isn't a lack of inspiration; it's a surplus of noise."""

    return """  <!-- Zero-Cloud Architecture -->
  <section class="py-5" id="architecture">
    <div class="container py-4">
      <div class="text-center max-w-700 mx-auto mb-5">
        <span class="badge bg-warning-subtle text-warning border border-warning-subtle rounded-pill px-3 py-2 fw-semibold mb-2">
          <i class="bi bi-diagram-3 me-1" aria-hidden="true"></i> System Architecture
        </span>
        <h2 class="display-5 fw-bold text-white">%s</h2>
        <p class="text-secondary fs-5">%s</p>
      </div>

      <div class="row g-4 align-items-center mb-5">
        <div class="col-lg-6">
          <div class="card card-glass p-4 border border-secondary-subtle">
            <h3 class="h5 text-white fw-bold mb-3"><i class="bi bi-folder2-open text-warning me-2" aria-hidden="true"></i>%s</h3>
            <p class="text-secondary small mb-3 lh-base">%s</p>
            <div class="p-3 bg-black rounded-3 border border-secondary-subtle mb-3">
              <span class="text-white-50 extra-small">Journal Folder Hierarchy (ULID Naming):</span>
              <pre class="text-warning extra-small mb-0 mt-1"><code>Journal/
└── 2026/
    └── 03-March/
        ├── 2026-03-15-01JN9Z8K7P3QW9E1R4T6Y8U2I0.md
        └── 2026-03-16-01JN9ZB2M4X7V1A8C3D5E6F7G8.md</code></pre>
            </div>
          </div>
        </div>
        <div class="col-lg-6">
          <div class="card card-glass p-4 border border-secondary-subtle">
            <div class="d-flex align-items-center justify-content-between mb-2">
              <span class="text-white-50 extra-small fw-semibold"><i class="bi bi-filetype-md me-1 text-warning" aria-hidden="true"></i>Standard Markdown + YAML Front Matter</span>
              <span class="badge bg-dark border border-secondary text-white-50 extra-small">Plain Text UTF-8</span>
            </div>
            <div class="nudge-code-box">%s</div>
          </div>
        </div>
      </div>

      <div class="row g-4">
        <div class="col-lg-6">
          <div class="card card-glass h-100 p-4 border border-secondary-subtle">
            <h3 class="h5 text-white fw-bold mb-2"><i class="bi bi-shield-check text-warning me-2" aria-hidden="true"></i>%s</h3>
            <p class="text-secondary small mb-0 lh-base">%s</p>
          </div>
        </div>
        <div class="col-lg-6">
          <div class="card card-glass h-100 p-4 border border-secondary-subtle">
            <h3 class="h5 text-white fw-bold mb-2"><i class="bi bi-lightning-charge text-warning me-2" aria-hidden="true"></i>%s</h3>
            <p class="text-secondary small mb-0 lh-base">%s</p>
          </div>
        </div>
      </div>
    </div>
  </section>""" % (E(t["h_arch"]), E(t["arch_sub"]),
                   E(t["arch_fs_title"]), E(t["arch_fs_desc"]),
                   E(code_snippet),
                   E(t["arch_atomic_title"]), E(t["arch_atomic_desc"]),
                   E(t["arch_bm25_title"]), E(t["arch_bm25_desc"]))

def render_ai_companion(t):
    moments = t.get("moments", [])
    moment_cards = []
    for m in moments:
        moment_cards.append("""          <div class="col-lg-4">
            <div class="card card-glass h-100 p-4 border border-secondary-subtle">
              <div class="d-flex align-items-center justify-content-between mb-3">
                <span class="badge bg-warning-subtle text-warning border border-warning-subtle rounded-pill extra-small px-3 py-1">Moment %s</span>
                <span class="extra-small text-white-50"><i class="bi bi-clock me-1" aria-hidden="true"></i>%s</span>
              </div>
              <h3 class="h5 text-white fw-bold mb-2">%s</h3>
              <p class="text-secondary small mb-0 lh-base">%s</p>
            </div>
          </div>""" % (E(m["num"]), E(m["timing"]), E(m["title"]), E(m["desc"])))

    return """  <!-- On-Device AI Companion -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="ai-companion">
    <div class="container py-4">
      <div class="text-center max-w-700 mx-auto mb-5">
        <span class="badge bg-warning-subtle text-warning border border-warning-subtle rounded-pill px-3 py-2 fw-semibold mb-2">
          <i class="bi bi-cpu-fill me-1" aria-hidden="true"></i> 100%% On-Device SLM
        </span>
        <h2 class="display-5 fw-bold text-white">%s</h2>
        <p class="text-secondary fs-5">%s</p>
      </div>

      <div class="card card-glass p-4 border border-warning-subtle mb-4">
        <div class="row align-items-center gy-3">
          <div class="col-lg-8">
            <h3 class="h5 text-white fw-bold mb-1"><i class="bi bi-eyeglasses text-warning me-2" aria-hidden="true"></i>%s</h3>
            <p class="text-secondary small mb-0 lh-base">%s</p>
          </div>
          <div class="col-lg-4 text-lg-end">
            <span class="badge bg-dark border border-warning text-warning px-3 py-2 fw-semibold">GBNF Formal Grammars • Zero Advice</span>
          </div>
        </div>
      </div>

      <div class="row g-4 mb-4">
%s
      </div>

      <div class="row g-4">
        <div class="col-lg-6">
          <div class="card card-glass h-100 p-4 border border-secondary-subtle">
            <h3 class="h5 text-white fw-bold mb-2"><i class="bi bi-calendar2-range text-warning me-2" aria-hidden="true"></i>%s</h3>
            <p class="text-secondary small mb-0 lh-base">%s</p>
          </div>
        </div>
        <div class="col-lg-6">
          <div class="card card-glass h-100 p-4 border border-secondary-subtle">
            <h3 class="h5 text-white fw-bold mb-2"><i class="bi bi-chat-left-quote text-warning me-2" aria-hidden="true"></i>%s</h3>
            <p class="text-secondary small mb-0 lh-base">%s</p>
          </div>
        </div>
      </div>
    </div>
  </section>""" % (E(t["h_ai"]), E(t["ai_sub"]),
                   E(t["ai_rule_title"]), E(t["ai_rule_desc"]),
                   "\n".join(moment_cards),
                   E(t["ai_recap_title"]), E(t["ai_recap_desc"]),
                   E(t["ai_search_title"]), E(t["ai_search_desc"]))

def render_psychology(t):
    themes = ["Work", "Relationships", "Family", "Health", "Money", "Identity", "Creativity", "Learning", "Travel", "Everyday", "Plans"]
    pills = "".join('<span class="theme-pill"><i class="bi bi-tag-fill text-warning me-1" aria-hidden="true"></i>%s</span>' % th for th in themes)

    return """  <!-- Shame-Free Metrics -->
  <section class="py-5" id="metrics">
    <div class="container py-4">
      <div class="text-center max-w-700 mx-auto mb-5">
        <span class="badge bg-warning-subtle text-warning border border-warning-subtle rounded-pill px-3 py-2 fw-semibold mb-2">
          <i class="bi bi-heart-pulse-fill me-1" aria-hidden="true"></i> Compassionate Habits
        </span>
        <h2 class="display-5 fw-bold text-white">%s</h2>
        <p class="text-secondary fs-5">%s</p>
      </div>

      <div class="row g-4 mb-4">
        <div class="col-lg-4">
          <div class="card card-glass h-100 p-4 border border-secondary-subtle">
            <div class="nudge-icon-box mb-3"><i class="bi bi-shield-slash" aria-hidden="true"></i></div>
            <h3 class="h5 text-white fw-bold mb-2">%s</h3>
            <p class="text-secondary small mb-0 lh-base">%s</p>
          </div>
        </div>
        <div class="col-lg-4">
          <div class="card card-glass h-100 p-4 border border-secondary-subtle">
            <div class="nudge-icon-box mb-3"><i class="bi bi-arrow-return-right" aria-hidden="true"></i></div>
            <h3 class="h5 text-white fw-bold mb-2">%s</h3>
            <p class="text-secondary small mb-0 lh-base">%s</p>
          </div>
        </div>
        <div class="col-lg-4">
          <div class="card card-glass h-100 p-4 border border-secondary-subtle">
            <div class="nudge-icon-box mb-3"><i class="bi bi-bar-chart-line" aria-hidden="true"></i></div>
            <h3 class="h5 text-white fw-bold mb-2">%s</h3>
            <p class="text-secondary small mb-0 lh-base">%s</p>
          </div>
        </div>
      </div>

      <div class="card card-glass p-4 border border-secondary-subtle">
        <div class="row align-items-center gy-4">
          <div class="col-lg-4">
            <h3 class="h5 text-white fw-bold mb-2">%s</h3>
            <p class="text-secondary small mb-0 lh-base">%s</p>
          </div>
          <div class="col-lg-8">
            <div class="d-flex flex-wrap gap-2">
              %s
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>""" % (E(t["h_psych"]), E(t["psych_sub"]),
                   E(t["psych_grace_title"]), E(t["psych_grace_desc"]),
                   E(t["psych_return_title"]), E(t["psych_return_desc"]),
                   E(t["psych_median_title"]), E(t["psych_median_desc"]),
                   E(t["psych_themes_title"]), E(t["psych_themes_desc"]),
                   pills)

def render_writing(t):
    return """  <!-- Deep Work Writing Environment -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="writing">
    <div class="container py-4">
      <div class="text-center max-w-700 mx-auto mb-5">
        <span class="badge bg-warning-subtle text-warning border border-warning-subtle rounded-pill px-3 py-2 fw-semibold mb-2">
          <i class="bi bi-pen-fill me-1" aria-hidden="true"></i> Deep Work
        </span>
        <h2 class="display-5 fw-bold text-white">%s</h2>
        <p class="text-secondary fs-5">%s</p>
      </div>

      <div class="row g-4">
        <div class="col-lg-6 col-md-6">
          <div class="card card-glass h-100 p-4 border border-secondary-subtle">
            <h3 class="h5 text-white fw-bold mb-2"><i class="bi bi-speedometer2 text-warning me-2" aria-hidden="true"></i>%s</h3>
            <p class="text-secondary small mb-0 lh-base">%s</p>
          </div>
        </div>
        <div class="col-lg-6 col-md-6">
          <div class="card card-glass h-100 p-4 border border-secondary-subtle">
            <h3 class="h5 text-white fw-bold mb-2"><i class="bi bi-palette text-warning me-2" aria-hidden="true"></i>%s</h3>
            <p class="text-secondary small mb-0 lh-base">%s</p>
          </div>
        </div>
        <div class="col-lg-6 col-md-6">
          <div class="card card-glass h-100 p-4 border border-secondary-subtle">
            <h3 class="h5 text-white fw-bold mb-2"><i class="bi bi-fullscreen text-warning me-2" aria-hidden="true"></i>%s</h3>
            <p class="text-secondary small mb-0 lh-base">%s</p>
          </div>
        </div>
        <div class="col-lg-6 col-md-6">
          <div class="card card-glass h-100 p-4 border border-secondary-subtle">
            <h3 class="h5 text-white fw-bold mb-2"><i class="bi bi-window-stack text-warning me-2" aria-hidden="true"></i>%s</h3>
            <p class="text-secondary small mb-0 lh-base">%s</p>
          </div>
        </div>
      </div>
    </div>
  </section>""" % (E(t["h_writing"]), E(t["writing_sub"]),
                   E(t["writing_launch_title"]), E(t["writing_launch_desc"]),
                   E(t["writing_palette_title"]), E(t["writing_palette_desc"]),
                   E(t["writing_focus_title"]), E(t["writing_focus_desc"]),
                   E(t["writing_capture_title"]), E(t["writing_capture_desc"]))

def render_security(t):
    return """  <!-- Security & Biometrics -->
  <section class="py-5" id="security">
    <div class="container py-4">
      <div class="text-center max-w-700 mx-auto mb-5">
        <span class="badge bg-warning-subtle text-warning border border-warning-subtle rounded-pill px-3 py-2 fw-semibold mb-2">
          <i class="bi bi-fingerprint me-1" aria-hidden="true"></i> Fortified Security
        </span>
        <h2 class="display-5 fw-bold text-white">%s</h2>
        <p class="text-secondary fs-5">%s</p>
      </div>

      <div class="row g-4">
        <div class="col-lg-4">
          <div class="card card-glass h-100 p-4 border border-secondary-subtle">
            <h3 class="h5 text-white fw-bold mb-2"><i class="bi bi-fingerprint text-warning me-2" aria-hidden="true"></i>%s</h3>
            <p class="text-secondary small mb-0 lh-base">%s</p>
          </div>
        </div>
        <div class="col-lg-4">
          <div class="card card-glass h-100 p-4 border border-secondary-subtle">
            <h3 class="h5 text-white fw-bold mb-2"><i class="bi bi-key-fill text-warning me-2" aria-hidden="true"></i>%s</h3>
            <p class="text-secondary small mb-0 lh-base">%s</p>
          </div>
        </div>
        <div class="col-lg-4">
          <div class="card card-glass h-100 p-4 border border-secondary-subtle">
            <h3 class="h5 text-white fw-bold mb-2"><i class="bi bi-display text-warning me-2" aria-hidden="true"></i>%s</h3>
            <p class="text-secondary small mb-0 lh-base">%s</p>
          </div>
        </div>
        <div class="col-lg-6">
          <div class="card card-glass h-100 p-4 border border-secondary-subtle">
            <h3 class="h5 text-white fw-bold mb-2"><i class="bi bi-box-arrow-in-right text-warning me-2" aria-hidden="true"></i>%s</h3>
            <p class="text-secondary small mb-0 lh-base">%s</p>
          </div>
        </div>
        <div class="col-lg-6">
          <div class="card card-glass h-100 p-4 border border-secondary-subtle">
            <h3 class="h5 text-white fw-bold mb-2"><i class="bi bi-box-arrow-up-right text-warning me-2" aria-hidden="true"></i>%s</h3>
            <p class="text-secondary small mb-0 lh-base">%s</p>
          </div>
        </div>
      </div>
    </div>
  </section>""" % (E(t["h_security"]), E(t["security_sub"]),
                   E(t["sec_hello_title"]), E(t["sec_hello_desc"]),
                   E(t["sec_aes_title"]), E(t["sec_aes_desc"]),
                   E(t["sec_privacy_title"]), E(t["sec_privacy_desc"]),
                   E(t["sec_import_title"]), E(t["sec_import_desc"]),
                   E(t["sec_export_title"]), E(t["sec_export_desc"]))

def render_comparison_table(t):
    headers = t.get("compare_headers", ["Feature / Attribute", "Nudge", "Day One", "Obsidian", "Notion", "AI Chatbots"])
    rows = t.get("compare_rows", [])
    rows_html = []
    for r in rows:
        rows_html.append("""              <tr>
                <td class="text-white fw-semibold small text-nowrap align-middle">%s</td>
                <td class="nudge-col small align-middle">
                  <span class="d-flex align-items-center gap-2">
                    <i class="bi bi-check-circle-fill text-warning flex-shrink-0" aria-hidden="true"></i>
                    <span class="text-white fw-bold">%s</span>
                  </span>
                </td>
                <td class="text-secondary small align-middle">%s</td>
                <td class="text-secondary small align-middle">%s</td>
                <td class="text-secondary small align-middle">%s</td>
                <td class="text-secondary small align-middle">%s</td>
              </tr>""" % (E(r[0]), E(r[1]), E(r[2]), E(r[3]), E(r[4]), E(r[5])))

    return """  <!-- Comparison Table -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="comparison">
    <div class="container py-4">
      <div class="text-center max-w-700 mx-auto mb-5">
        <span class="badge bg-warning-subtle text-warning border border-warning-subtle rounded-pill px-3 py-2 fw-semibold mb-2">
          <i class="bi bi-sliders me-1" aria-hidden="true"></i> Product Comparison
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
                <th scope="col" class="nudge-col text-warning fw-bold"><i class="bi bi-award-fill me-1" aria-hidden="true"></i>%s</th>
                <th scope="col">%s</th>
                <th scope="col">%s</th>
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
  </section>""" % (E(t["h_compare"]), E(t["compare_sub"]),
                   E(headers[0]), E(headers[1]), E(headers[2]), E(headers[3]), E(headers[4]), E(headers[5]),
                   "\n".join(rows_html))

def render_workflows(t):
    workflows = t.get("workflows", [])
    cards = []
    for w in workflows:
        cards.append("""        <div class="col-lg-4 col-md-6">
          <div class="card card-glass h-100 p-4 border border-secondary-subtle">
            <div class="d-flex align-items-center justify-content-between mb-3">
              <span class="badge bg-warning-subtle text-warning border border-warning-subtle rounded-pill extra-small px-3 py-1">Workflow %s</span>
              <span class="extra-small text-white-50"><i class="bi bi-clock-history me-1" aria-hidden="true"></i>%s</span>
            </div>
            <h3 class="h5 text-white fw-bold mb-2">%s</h3>
            <p class="text-secondary small mb-0 lh-base">%s</p>
          </div>
        </div>""" % (E(w["num"]), E(w["time"]), E(w["title"]), E(w["desc"])))

    return """  <!-- Master Workflows -->
  <section class="py-5" id="workflows">
    <div class="container py-4">
      <div class="text-center max-w-700 mx-auto mb-5">
        <span class="badge bg-warning-subtle text-warning border border-warning-subtle rounded-pill px-3 py-2 fw-semibold mb-2">
          <i class="bi bi-journal-text me-1" aria-hidden="true"></i> Daily Rhythms
        </span>
        <h2 class="display-5 fw-bold text-white">%s</h2>
        <p class="text-secondary fs-5">%s</p>
      </div>
      <div class="row g-4 justify-content-center">
%s
      </div>
    </div>
  </section>""" % (E(t["h_workflows"]), E(t["workflows_sub"]), "\n".join(cards))

def render_hardware(t):
    tiers = t.get("hardware_tiers", [])
    tier_cards = []
    for tr in tiers:
        tier_cards.append("""        <div class="col-lg-4">
          <div class="card card-glass h-100 p-4 border border-secondary-subtle">
            <h3 class="h6 text-warning fw-bold mb-2"><i class="bi bi-cpu me-2" aria-hidden="true"></i>%s</h3>
            <p class="text-white-50 extra-small mb-2 fw-semibold">%s</p>
            <p class="text-secondary small mb-0 lh-base">%s</p>
          </div>
        </div>""" % (E(tr["tier"]), E(tr["specs"]), E(tr["perf"])))

    return """  <!-- Hardware Tiers -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="hardware">
    <div class="container py-4">
      <div class="text-center max-w-700 mx-auto mb-5">
        <span class="badge bg-warning-subtle text-warning border border-warning-subtle rounded-pill px-3 py-2 fw-semibold mb-2">
          <i class="bi bi-motherboard me-1" aria-hidden="true"></i> Computational Efficiency
        </span>
        <h2 class="display-5 fw-bold text-white">%s</h2>
        <p class="text-secondary fs-5">%s</p>
      </div>
      <div class="row g-4 mb-4">
%s
      </div>
      <div class="p-4 rounded-4 card-glass border border-secondary-subtle">
        <div class="row gy-3">
          <div class="col-md-6">
            <span class="text-warning small fw-bold"><i class="bi bi-check2-circle me-1" aria-hidden="true"></i>Minimum System Requirements:</span>
            <p class="text-secondary small mb-0 mt-1">%s</p>
          </div>
          <div class="col-md-6">
            <span class="text-warning small fw-bold"><i class="bi bi-stars me-1" aria-hidden="true"></i>Recommended Configuration:</span>
            <p class="text-secondary small mb-0 mt-1">%s</p>
          </div>
        </div>
      </div>
    </div>
  </section>""" % (E(t["h_hardware"]), E(t["hardware_sub"]), "\n".join(tier_cards), E(t["sys_min"]), E(t["sys_rec"]))

def render_pricing(t):
    return """  <!-- Transparent Licensing -->
  <section class="py-5" id="pricing">
    <div class="container py-4">
      <div class="text-center max-w-700 mx-auto mb-5">
        <span class="badge bg-warning-subtle text-warning border border-warning-subtle rounded-pill px-3 py-2 fw-semibold mb-2">
          <i class="bi bi-tag-fill me-1" aria-hidden="true"></i> Transparent Pricing
        </span>
        <h2 class="display-5 fw-bold text-white">%s</h2>
        <p class="text-secondary fs-5">%s</p>
      </div>

      <div class="row g-4 justify-content-center mb-4">
        <div class="col-lg-5 col-md-6">
          <div class="card card-glass h-100 p-4 border border-secondary-subtle text-center">
            <span class="badge bg-dark border border-secondary text-white-50 px-3 py-1 rounded-pill mx-auto mb-3">15-Day Trial</span>
            <h3 class="display-6 fw-bold text-white mb-1">$0.00</h3>
            <p class="text-white-50 small mb-4">Zero credit card required</p>
            <p class="text-secondary small mb-4 lh-base text-start">%s</p>
            <a href="%s" target="_blank" rel="noopener" class="btn btn-outline-warning rounded-pill px-4 py-2 fw-bold w-100 mt-auto">
              <i class="bi bi-download me-1" aria-hidden="true"></i> Download Free Trial
            </a>
          </div>
        </div>
        <div class="col-lg-5 col-md-6">
          <div class="card card-glass h-100 p-4 border border-warning text-center glow-aura-amber">
            <span class="badge bg-warning text-dark px-3 py-1 rounded-pill mx-auto mb-3 fw-bold">Lifetime License</span>
            <h3 class="display-6 fw-bold text-warning mb-1">$0.99 USD</h3>
            <p class="text-white-50 small mb-4">Single one-time purchase • Pay once, own forever</p>
            <p class="text-secondary small mb-4 lh-base text-start">%s</p>
            <a href="%s" target="_blank" rel="noopener" class="btn btn-warning rounded-pill px-4 py-2 fw-bold w-100 mt-auto text-dark">
              <i class="bi bi-microsoft me-1" aria-hidden="true"></i> %s
            </a>
          </div>
        </div>
      </div>

      <div class="row g-4">
        <div class="col-lg-6">
          <div class="card card-glass h-100 p-4 border border-secondary-subtle">
            <h4 class="h6 text-white fw-bold mb-2"><i class="bi bi-unlock-fill text-warning me-2" aria-hidden="true"></i>%s</h4>
            <p class="text-secondary small mb-0 lh-base">%s</p>
          </div>
        </div>
        <div class="col-lg-6">
          <div class="card card-glass h-100 p-4 border border-secondary-subtle">
            <h4 class="h6 text-white fw-bold mb-2"><i class="bi bi-file-earmark-check text-warning me-2" aria-hidden="true"></i>%s</h4>
            <p class="text-secondary small mb-0 lh-base">%s</p>
          </div>
        </div>
      </div>
    </div>
  </section>""" % (E(t["h_pricing"]), E(t["pricing_sub"]),
                   E(t["pricing_trial_desc"]), E(STORE_UTM),
                   E(t["pricing_buy_desc"]), E(STORE_UTM),
                   E(t.get("cta_buy", "Buy Once — $0.99 Lifetime")),
                   E(t["pricing_failopen_title"]), E(t["pricing_failopen_desc"]),
                   E(t["pricing_expired_title"]), E(t["pricing_expired_desc"]))

def render_faqs(t):
    faqs = t.get("faqs", [])
    items = []
    for i, f in enumerate(faqs):
        num = i + 1
        collapsed = "collapsed" if i > 0 else ""
        show = "show" if i == 0 else ""
        items.append("""            <!-- FAQ %d -->
            <div class="accordion-item bg-transparent border-bottom border-secondary">
              <h3 class="accordion-header" id="faq%dHeading">
                <button class="accordion-button %s bg-transparent text-white fw-semibold py-4" type="button" data-bs-toggle="collapse" data-bs-target="#faq%d" aria-expanded="%s" aria-controls="faq%d">
                  Q%d: %s
                </button>
              </h3>
              <div id="faq%d" class="accordion-collapse collapse %s" aria-labelledby="faq%dHeading" data-bs-parent="#nudgeFaqAccordion">
                <div class="accordion-body text-secondary small pb-4 lh-base">
                  %s
                </div>
              </div>
            </div>""" % (num, num, collapsed, num, "true" if i == 0 else "false", num, num, E(f["q"]), num, show, num, E(f["a"])))

    return """  <!-- FAQ Section -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="faq">
    <div class="container py-4">
      <div class="text-center max-w-700 mx-auto mb-5">
        <span class="badge bg-warning-subtle text-warning border border-warning-subtle rounded-pill px-3 py-2 fw-semibold mb-2">
          <i class="bi bi-question-circle-fill me-1" aria-hidden="true"></i> Clear Answers
        </span>
        <h2 class="display-5 fw-bold text-white">%s</h2>
        <p class="text-secondary fs-5">%s</p>
      </div>
      <div class="max-w-900 mx-auto">
        <div class="accordion accordion-flush" id="nudgeFaqAccordion">
%s
        </div>
      </div>
    </div>
  </section>""" % (E(t["h_faq"]), E(t["faq_sub"]), "\n".join(items))

def render_quotes(t):
    quotes = t.get("quotes", [])
    cards = []
    for q in quotes:
        cards.append("""        <div class="col-lg-4">
          <div class="card card-glass h-100 p-4 border border-secondary-subtle d-flex flex-column justify-content-between">
            <p class="text-secondary small fst-italic mb-4 lh-base">"%s"</p>
            <div class="border-top border-secondary-subtle pt-3">
              <span class="text-white fw-bold small d-block">%s</span>
              <span class="text-white-50 extra-small">%s</span>
            </div>
          </div>
        </div>""" % (E(q["quote"]), E(q["author"]), E(q["role"])))

    return """  <!-- Testimonials -->
  <section class="py-5" id="quotes">
    <div class="container py-4">
      <div class="text-center max-w-700 mx-auto mb-5">
        <span class="badge bg-warning-subtle text-warning border border-warning-subtle rounded-pill px-3 py-2 fw-semibold mb-2">
          <i class="bi bi-chat-quote-fill me-1" aria-hidden="true"></i> Independent Perspectives
        </span>
        <h2 class="display-5 fw-bold text-white">%s</h2>
      </div>
      <div class="row g-4">
%s
      </div>
    </div>
  </section>""" % (E(t["h_quotes"]), "\n".join(cards))

def render_final_cta(t):
    return """  <!-- Final CTA -->
  <section class="py-5 bg-dark border-top border-secondary-subtle" id="download">
    <div class="container py-5 text-center max-w-800 mx-auto">
      <div class="d-inline-block position-relative mb-4">
        <img src="%s" alt="Nudge Icon" class="rounded-4 shadow-lg glow-aura-amber" width="96" height="96" decoding="async">
      </div>
      <h2 class="display-4 fw-bold text-white mb-3">%s</h2>
      <p class="lead text-secondary mb-4">%s</p>
      <div class="d-flex flex-wrap justify-content-center gap-3 mb-4">
        <a href="%s" target="_blank" rel="noopener" class="btn btn-warning btn-lg rounded-pill px-4 fw-bold shadow text-dark">
          <i class="bi bi-microsoft me-2" aria-hidden="true"></i> %s
        </a>
        <a href="%s" target="_blank" rel="noopener" class="btn btn-outline-warning btn-lg rounded-pill px-4 fw-bold">
          <i class="bi bi-download me-2" aria-hidden="true"></i> %s
        </a>
      </div>
      <p class="extra-small text-white-50 mb-0">%s</p>
    </div>
  </section>""" % (ICON, E(t["h_cta"]), E(t["cta_lead"]),
                   E(STORE_UTM), E(t["cta_buy_btn"]),
                   E(STORE_UTM), E(t["cta_trial_btn"]),
                   E(t["cta_guarantee"]))

def build(code):
    t = L.get(code) or L["en"]
    direction = BY_CODE[code][2]
    hl = BY_CODE[code][3]
    og = BY_CODE[code][4]
    title = "%s | Microsoft Store (Windows 10 & 11) | Dhinovatech" % t["name"]
    desc = t["intro_lead"][:240] + "..."

    og_alts = "\n".join(
        '  <meta property="og:locale:alternate" content="%s">' % o
        for c2, _l, _d, _h, o in built_langs() if c2 != code)

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
  <!-- Open Graph / Facebook -->
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

  <!-- Twitter -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="{site}{ogimg}">
  <meta name="twitter:image:alt" content="{ogalt}">

  <!-- JSON-LD Structured Data -->
  <script type="application/ld+json">
{schema}
  </script>
  <!-- END SEO block -->
  <!-- BEGIN resource hints -->
  <link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
  <link rel="dns-prefetch" href="https://cdn.jsdelivr.net">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap">
  <link rel="preconnect" href="https://www.googletagmanager.com">
  <link rel="dns-prefetch" href="https://www.googletagmanager.com">
  <link rel="manifest" href="/site.webmanifest">
  <meta name="theme-color" content="#080c14">
  <meta name="color-scheme" content="dark light">
  <!-- END resource hints -->
</head>
<body>
<a class="skip-link" href="#main">Skip to main content</a>
{navbar}

<main id="main">
  <!-- Hero Section -->
  <section class="py-5 overflow-hidden" id="hero">
    <div class="container py-4">
      <div class="row align-items-center gy-5">
        <div class="col-lg-7">
          <span class="badge bg-warning-subtle text-warning border border-warning-subtle rounded-pill px-3 py-2 fw-semibold mb-3">
            <i class="bi bi-shield-check me-1" aria-hidden="true"></i> {platform_badge}
          </span>
          <h1 class="display-4 fw-bold text-white mb-3">
            {name}
          </h1>
          <p class="fs-4 text-warning fw-semibold mb-3">
            "{tagline}"
          </p>
          <p class="lead text-secondary mb-4 pe-lg-4 fs-5 lh-base">
            {intro_lead}
          </p>
          <p class="text-secondary small mb-4 pe-lg-4 lh-base">
            {intro_p2}
          </p>

          <!-- Badges Grid -->
          <div class="d-flex flex-wrap gap-2 mb-4">
            <span class="badge bg-dark border border-warning text-warning px-3 py-2 rounded-pill"><i class="bi bi-wifi-off me-1" aria-hidden="true"></i>{badge_offline}</span>
            <span class="badge bg-dark border border-secondary text-white px-3 py-2 rounded-pill"><i class="bi bi-cpu me-1 text-warning" aria-hidden="true"></i>{badge_ai}</span>
            <span class="badge bg-dark border border-secondary text-white px-3 py-2 rounded-pill"><i class="bi bi-markdown me-1 text-warning" aria-hidden="true"></i>{badge_markdown}</span>
            <span class="badge bg-dark border border-secondary text-white px-3 py-2 rounded-pill"><i class="bi bi-slash-circle me-1 text-warning" aria-hidden="true"></i>{badge_telemetry}</span>
            <span class="badge bg-dark border border-secondary text-white px-3 py-2 rounded-pill"><i class="bi bi-fingerprint me-1 text-warning" aria-hidden="true"></i>{badge_hello}</span>
            <span class="badge bg-dark border border-secondary text-white px-3 py-2 rounded-pill"><i class="bi bi-tag-fill me-1 text-warning" aria-hidden="true"></i>{badge_price}</span>
          </div>

          <!-- CTAs -->
          <div class="d-flex flex-wrap gap-3 align-items-center">
            <a href="{store}" target="_blank" rel="noopener" class="btn btn-warning btn-lg rounded-pill px-4 fw-bold shadow d-flex align-items-center gap-2 text-dark">
              <i class="bi bi-microsoft fs-5" aria-hidden="true"></i> {cta_buy}
            </a>
            <a href="{store}" target="_blank" rel="noopener" class="btn btn-outline-warning btn-lg rounded-pill px-4 fw-bold d-flex align-items-center gap-2">
              <i class="bi bi-download fs-5" aria-hidden="true"></i> {cta_trial}
            </a>
            <a href="#specs" class="btn btn-link text-white-50 text-decoration-none small">
              {cta_see} <i class="bi bi-arrow-down ms-1" aria-hidden="true"></i>
            </a>
          </div>
        </div>

        <div class="col-lg-5 text-center">
          <div class="position-relative d-inline-block">
            <div class="position-absolute top-50 start-50 translate-middle w-100 h-100 rounded-circle bg-warning opacity-10 blur-3xl"></div>
            <img src="{icon}" alt="Nudge App Icon" class="img-fluid rounded-4 shadow-lg border border-warning glow-aura-amber animated-float" style="max-height: 420px; object-fit: cover;" decoding="async" width="512" height="512">
          </div>
        </div>
      </div>
    </div>
  </section>

{pillars_section}

{specs_section}

{manifesto_section}

{architecture_section}

{ai_companion_section}

{psychology_section}

{writing_section}

{security_section}

{comparison_section}

{workflows_section}

{hardware_section}

{pricing_section}

{faqs_section}

{quotes_section}

{final_cta_section}
</main>

{footer}

  <!-- Bootstrap 5.3 JS Bundle -->
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
  <script src="/assets/js/nav.js"></script>

  <!-- BEGIN generated UX block -->
  <div class="install-bar" role="complementary" aria-label="Nudge Offline Journal &amp; AI">
    <img src="{icon}" alt="" width="42" height="42" loading="lazy" decoding="async">
    <div class="install-bar-text">
      <div class="install-bar-title">Nudge</div>
      <div class="install-bar-sub"><i class="bi bi-microsoft" aria-hidden="true"></i> Microsoft Store</div>
    </div>
    <a href="{store}" target="_blank" rel="noopener" class="btn btn-warning btn-sm rounded-pill px-3 text-dark fw-bold">{cta_install}</a>
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
        platform_badge=E(t.get("platform_badge", "Native WinUI 3 for Windows 10 & 11 • x64 & ARM64 Copilot+ PC")),
        name=E(t["name"]),
        tagline=E(t["tagline"]),
        intro_lead=E(t["intro_lead"]),
        intro_p2=E(t.get("intro_p2", "")),
        badge_offline=E(t.get("badge_offline", "100% Offline Air-Gapped")),
        badge_ai=E(t.get("badge_ai", "On-Device SLM (Zero Cloud)")),
        badge_markdown=E(t.get("badge_markdown", "Plain Markdown (.md)")),
        badge_telemetry=E(t.get("badge_telemetry", "Zero Telemetry")),
        badge_hello=E(t.get("badge_hello", "Windows Hello Biometrics")),
        badge_price=E(t.get("badge_price", "$0.99 One-Time Buy")),
        store=E(STORE_UTM),
        icon=ICON,
        cta_buy=E(t.get("cta_buy", "Buy Once — $0.99 Lifetime")),
        cta_trial=E(t.get("cta_trial", "Download 15-Day Free Trial")),
        cta_see=E(t.get("cta_see", "Explore Architecture & Specifications")),
        cta_install=E(t.get("cta_trial", "Install")),
        pillars_section=render_pillars(t),
        specs_section=render_specs_table(t),
        manifesto_section=render_manifesto(t),
        architecture_section=render_architecture(t),
        ai_companion_section=render_ai_companion(t),
        psychology_section=render_psychology(t),
        writing_section=render_writing(t),
        security_section=render_security(t),
        comparison_section=render_comparison_table(t),
        workflows_section=render_workflows(t),
        hardware_section=render_hardware(t),
        pricing_section=render_pricing(t),
        faqs_section=render_faqs(t),
        quotes_section=render_quotes(t),
        final_cta_section=render_final_cta(t),
        footer=FOOTER,
        consent_banner=consent_banner_html(code)
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
