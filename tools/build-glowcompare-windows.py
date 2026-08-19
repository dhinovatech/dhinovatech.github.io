#!/usr/bin/env python3
"""
Generate /glowcompare-windows/ - the Microsoft Store (WinUI 3) edition of
GlowCompare, in 28 languages.

This section keeps its own navigation on purpose: its language switcher lists
only the 28 Windows locales, and every store CTA points at the Microsoft Store
listing, never Google Play. The Android tree under /glowcompare/ is unaffected
and is reached through a single cross-link in the "Our Apps" menu.

Copy lives in tools/glowcompare-windows-strings.json (one block per locale).

Run:  python tools/build-glowcompare-windows.py
Idempotent: every page is rewritten from the strings file on each run.
"""
import html
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STRINGS = os.path.join(ROOT, "tools", "glowcompare-windows-strings.json")

with open(STRINGS, encoding="utf-8") as _fh:
    L = json.load(_fh)

SECTION = "glowcompare-windows"

SITE = "https://www.dhinovatech.com"
STORE = "https://apps.microsoft.com/detail/9N4QM1FDQ1CB"
STORE_UTM = STORE + "?ocid=dhinovatech_glowcompare_windows"

# code, menu label, dir, hreflang, og locale
LANGS = [
    ("en", "English", "ltr", "en", "en_US"),
    ("es", "Español (Spanish)", "ltr", "es", "es_ES"),
    ("fr", "Français (French)", "ltr", "fr", "fr_FR"),
    ("de", "Deutsch (German)", "ltr", "de", "de_DE"),
    ("it", "Italiano (Italian)", "ltr", "it", "it_IT"),
    ("nl", "Nederlands (Dutch)", "ltr", "nl", "nl_NL"),
    ("pl", "Polski (Polish)", "ltr", "pl", "pl_PL"),
    ("pt", "Português (Portuguese)", "ltr", "pt", "pt_BR"),
    ("ru", "Русский (Russian)", "ltr", "ru", "ru_RU"),
    ("uk", "Українська (Ukrainian)", "ltr", "uk", "uk_UA"),
    ("tr", "Türkçe (Turkish)", "ltr", "tr", "tr_TR"),
    ("ja", "日本語 (Japanese)", "ltr", "ja", "ja_JP"),
    ("ko", "한국어 (Korean)", "ltr", "ko", "ko_KR"),
    ("zh", "简体中文 (Simplified Chinese)", "ltr", "zh-Hans", "zh_CN"),
    ("vi", "Tiếng Việt (Vietnamese)", "ltr", "vi", "vi_VN"),
    ("id", "Bahasa Indonesia (Indonesian)", "ltr", "id", "id_ID"),
    ("jv", "Basa Jawa (Javanese)", "ltr", "jv", "jv_ID"),
    ("tl", "Tagalog (Filipino)", "ltr", "tl", "tl_PH"),
    ("hi", "हिन्दी (Hindi)", "ltr", "hi", "hi_IN"),
    ("bn", "বাংলা (Bengali)", "ltr", "bn", "bn_IN"),
    ("mr", "मराठी (Marathi)", "ltr", "mr", "mr_IN"),
    ("te", "తెలుగు (Telugu)", "ltr", "te", "te_IN"),
    ("ta", "தமிழ் (Tamil)", "ltr", "ta", "ta_IN"),
    ("ar", "العربية (Arabic)", "rtl", "ar", "ar_AR"),
    ("ur", "اردو (Urdu)", "rtl", "ur", "ur_PK"),
    ("fa", "فارسی (Persian)", "rtl", "fa", "fa_IR"),
    ("sw", "Kiswahili (Swahili)", "ltr", "sw", "sw_KE"),
    ("ha", "Hausa", "ltr", "ha", "ha_NG"),
]

BY_CODE = {c: (c, label, d, hl, og) for c, label, d, hl, og in LANGS}
assert set(BY_CODE) == set(L), (set(BY_CODE) ^ set(L))

E = html.escape


def url_for(code):
    return "/%s/" % SECTION if code == "en" else "/%s/%s/" % (SECTION, code)


def abs_url(code):
    return SITE + url_for(code)


# --------------------------------------------------------------------------
# Shared navigation - independent of the Android /glowcompare/ tree.
# --------------------------------------------------------------------------

def lang_submenu(icon_colour, active=None):
    out = []
    for code, label, _d, _hl, _og in LANGS:
        cls = "dropdown-item py-1 small"
        if code == active:
            cls += " active fw-bold text-primary"
        out.append(
            '<li><a class="%s" href="%s"><i class="bi bi-globe %s me-2" aria-hidden="true"></i>%s</a></li>'
            % (cls, url_for(code), icon_colour, E(label))
        )
    return "".join(out)


def lang_selector(active):
    items = []
    for code, label, _d, _hl, _og in LANGS:
        cls = "dropdown-item py-1 small"
        if code == active:
            cls += " active fw-bold text-primary"
        items.append(
            '<li><a class="%s" href="%s"><i class="bi bi-translate text-primary me-2" aria-hidden="true"></i>%s</a></li>'
            % (cls, url_for(code), E(label))
        )
    return "".join(items)


def navbar(code):
    label = BY_CODE[code][1]
    return """  <nav class="navbar navbar-expand-lg navbar-dhin sticky-top py-3">
    <div class="container">
      <a class="navbar-brand d-flex align-items-center gap-2" href="/">
        <img src="/assets/images/LogoWithText.png" alt="Dhinovatech" class="brand-logo-with-text-img" decoding="async">
      </a>
      <button class="navbar-toggler border-0 text-white" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <i class="bi bi-list fs-2" aria-hidden="true"></i>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto align-items-lg-center">
          <li class="nav-item">
            <a class="nav-link nav-link-custom" href="/">Home</a>
          </li>

          <!-- Our Apps - GlowCompare for Windows owns its own language tree -->
          <li class="nav-item dropdown">
            <a class="nav-link nav-link-custom dropdown-toggle active" href="#" id="appsDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
              Our Apps
            </a>
            <ul class="dropdown-menu dropdown-menu-dark border-secondary shadow-lg mt-2" aria-labelledby="appsDropdown">
              <li class="dropdown-submenu position-relative">
                <a class="dropdown-item py-2 d-flex align-items-center justify-content-between" href="/glowcompare-windows/">
                  <span><img src="/assets/images/glowcompare-icon.png" alt="GlowCompare Icon" style="width: 20px; height: 20px; border-radius: 5px; object-fit: cover;" class="me-2" decoding="async">GlowCompare for Windows</span>
                  <span class="badge bg-primary-subtle text-primary border border-primary-subtle rounded-pill ms-2 extra-small submenu-toggle-btn" role="button" title="View 28 Languages">28 Languages <i class="bi bi-chevron-down ms-1" aria-hidden="true"></i></span>
                </a>
                <ul class="dropdown-menu dropdown-menu-dark border-secondary shadow-lg scrollable-menu" style="max-height: 360px; overflow-y: auto;">
                  __LANG_SUBMENU__
                </ul>
              </li>
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

          <!-- Language Selector - Windows edition only -->
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
              <i class="bi bi-microsoft fs-5" aria-hidden="true"></i> Get on Microsoft Store
            </a>
          </li>
        </ul>
      </div>
    </div>
  </nav>
""".replace("__LANG_SUBMENU__", lang_submenu("text-primary", code)) \
   .replace("__LANG_SELECTOR__", lang_selector(code)) \
   .replace("__LANG_LABEL__", E(label)) \
   .replace("__STORE__", E(STORE_UTM))


FOOTER = """  <footer class="footer-dhin">
    <div class="container">
      <div class="row gy-4 mb-5">
        <div class="col-lg-4">
          <a class="d-flex align-items-center gap-2 mb-3" href="/">
            <img src="/assets/images/LogoWithText.png" alt="Dhinovatech Logo" class="brand-logo-with-text-img" loading="lazy" decoding="async">
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
            <li><a href="/glowcompare-windows/" class="footer-link text-primary fw-semibold"><i class="bi bi-microsoft me-1" aria-hidden="true"></i> GlowCompare for Windows</a></li>
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
    /* Scoped GlowCompare for Windows accents */
    .glow-aura-blue { box-shadow: 0 0 45px rgba(56, 189, 248, 0.35); }
    .win-icon-box {
      width: 52px; height: 52px; border-radius: 14px;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.4rem; flex-shrink: 0;
      background: linear-gradient(135deg, rgba(56,189,248,0.18), rgba(255,117,140,0.18));
      color: #38bdf8; border: 1px solid rgba(56,189,248,0.3);
    }
    .metric-chip {
      display: flex; align-items: center; justify-content: space-between; gap: .75rem;
      padding: .7rem 1rem; border-radius: 12px;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .metric-chip .metric-score {
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: .8rem; color: #38bdf8; white-space: nowrap;
    }
    .metric-progress-bar {
      height: 6px; border-radius: 4px; margin-top: .5rem;
      background: rgba(255, 255, 255, 0.08); overflow: hidden;
    }
    .metric-fill {
      height: 100%; border-radius: 4px;
      background: linear-gradient(90deg, #38bdf8, #ff758c);
    }
    .ghost-stack { position: relative; }
    .ghost-stack img { display: block; width: 100%; border-radius: 18px; }
    .ghost-stack .ghost-layer {
      position: absolute; inset: 0; opacity: .35; border-radius: 18px; overflow: hidden;
    }
    .ghost-stack .ghost-layer img { filter: grayscale(1); }
    .win-badge-row { display: flex; flex-wrap: wrap; gap: .5rem; }
  </style>
"""


def hreflang_block(code):
    rows = ['  <link rel="canonical" href="%s">' % abs_url(code),
            '  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">',
            '  <link rel="alternate" hreflang="x-default" href="%s">' % abs_url("en")]
    for c, _label, _d, hl, _og in LANGS:
        rows.append('  <link rel="alternate" hreflang="%s" href="%s">' % (hl, abs_url(c)))
    return "\n".join(rows)


def schema(code, t, title, desc):
    graph = [
        {"@type": "Organization", "@id": SITE + "/#organization",
         "name": "Dhinovatech", "url": SITE + "/"},
        {"@type": "SoftwareApplication",
         "@id": SITE + "/glowcompare-windows/#software",
         "name": t["name"],
         "operatingSystem": "Windows 10, Windows 11",
         "applicationCategory": "HealthApplication",
         "description": desc,
         "url": abs_url(code),
         "inLanguage": [hl for _c, _l, _d, hl, _og in LANGS],
         "image": SITE + "/assets/images/glowcompare-icon.png",
         "downloadUrl": STORE,
         "installUrl": STORE,
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
         "publisher": {"@id": SITE + "/#organization"},
         "author": {"@id": SITE + "/#organization"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "GlowCompare for Windows",
             "item": abs_url("en")},
        ]},
    ]
    if code != "en":
        graph[2]["itemListElement"].append(
            {"@type": "ListItem", "position": 3,
             "name": "GlowCompare for Windows (%s)" % code, "item": abs_url(code)})
    return json.dumps({"@context": "https://schema.org", "@graph": graph},
                      ensure_ascii=False, separators=(",", ":"))


def metric_cards(metrics):
    icons = ["bi-clipboard2-pulse", "bi-droplet-fill", "bi-heart-pulse-fill",
             "bi-grid-3x3-gap-fill", "bi-palette-fill", "bi-brightness-high-fill",
             "bi-arrows-angle-contract", "bi-bullseye", "bi-stars"]
    widths = [88, 74, 62, 70, 66, 80, 72, 58, 84]
    out = []
    for i, m in enumerate(metrics):
        out.append("""          <div class="col-lg-4 col-md-6">
            <div class="card card-glass h-100 p-3">
              <div class="metric-chip border-0 bg-transparent p-0">
                <span class="fw-semibold text-white"><i class="bi %s text-primary me-2" aria-hidden="true"></i>%s</span>
                <span class="metric-score">0 - 100</span>
              </div>
              <div class="metric-progress-bar"><div class="metric-fill" style="width: %d%%;"></div></div>
            </div>
          </div>""" % (icons[i], E(m), widths[i]))
    return "\n".join(out)


def build(code):
    t = L[code]
    _c, label, direction, hl, og = BY_CODE[code]
    title = "%s | Windows (Microsoft Store) | Dhinovatech" % t["name"]
    desc = ("%s. %s %s" % (t["tagline"], t["intro1"], t["h_win"] + ": WinUI 3."))[:300]

    og_alts = "\n".join(
        '  <meta property="og:locale:alternate" content="%s">' % o
        for c2, _l, _d, _h, o in LANGS if c2 != code)

    doc = """<!DOCTYPE html>
<html lang="{hl}" dir="{dir}" data-bs-theme="dark">
<head>
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-T0S5ZW1QGM"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());

    gtag('config', 'G-T0S5ZW1QGM');
  </script>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{desc}">

  <!-- Bootstrap 5.3 CDN & Icons -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" integrity="sha384-XGjxtQfXaH2tnPFa9x+ruJTuLE3Aa6LhHSWRr1XeTyhezb4abCG4ccI5AkVDxqC+" crossorigin="anonymous">

  <!-- Inter is linked here rather than @imported from custom.css: an @import
       cannot start downloading until custom.css itself has parsed, which puts
       a render-blocking request behind a render-blocking request. -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap">

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
  <meta property="og:image" content="{site}/assets/images/glowcompare-slider-after.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="896">
  <meta property="og:image:alt" content="GlowCompare split-slider skincare progress comparison">
  <meta property="og:locale" content="{og}">
{og_alts}
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="{site}/assets/images/glowcompare-slider-after.jpg">
  <meta name="twitter:image:alt" content="GlowCompare split-slider skincare progress comparison">
  <script type="application/ld+json">
{schema}
  </script>
  <!-- END SEO block -->
  <!-- BEGIN resource hints -->
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
<!-- Navigation Bar (independent GlowCompare for Windows tree) -->
{navbar}
<main id="main">

  <!-- Hero -->
  <section class="hero-section py-5 position-relative overflow-hidden">
    <div class="container py-4">
      <div class="row align-items-center gy-5">
        <div class="col-lg-7">
          <div class="d-flex flex-wrap align-items-center gap-2 mb-3">
            <span class="badge-store-ms"><i class="bi bi-microsoft me-1" aria-hidden="true"></i> Microsoft Store</span>
            <span class="badge bg-primary-subtle text-primary border border-primary-subtle rounded-pill px-3 py-1 small">WinUI 3 &middot; Windows 10 &amp; 11</span>
            <span class="badge bg-success-subtle text-success border border-success-subtle rounded-pill px-3 py-1 small"><i class="bi bi-slash-circle me-1" aria-hidden="true"></i> No ads</span>
          </div>
          <h1 class="hero-title mb-3">{name}</h1>
          <p class="lead text-gradient-rose fw-semibold mb-3 fs-4">{tagline}</p>
          <p class="lead text-secondary mb-2 pe-lg-4 fs-5">{intro1}</p>
          <p class="text-secondary mb-4 pe-lg-4">{intro2}</p>

          <div class="d-flex flex-wrap gap-3 align-items-center mb-4">
            <a href="{store}" target="_blank" rel="noopener" class="btn btn-store btn-store-ms">
              <i class="bi bi-microsoft" aria-hidden="true"></i>
              <span class="btn-store-copy">
                <span class="btn-store-pre">Get it from</span>
                <span class="btn-store-name">Microsoft Store</span>
              </span>
            </a>
            <a href="#see-the-difference" class="btn btn-dhin-outline btn-lg rounded-pill px-4">
              <i class="bi bi-sliders me-2" aria-hidden="true"></i> {h_see}
            </a>
          </div>

          <div class="win-badge-row pt-2">
            <span class="badge bg-dark border border-secondary text-white-50 px-3 py-2 rounded-pill"><i class="bi bi-shield-lock-fill text-primary me-1" aria-hidden="true"></i> {h_privacy}</span>
            <span class="badge bg-dark border border-secondary text-white-50 px-3 py-2 rounded-pill"><i class="bi bi-fingerprint text-info me-1" aria-hidden="true"></i> Windows Hello</span>
            <span class="badge bg-dark border border-secondary text-white-50 px-3 py-2 rounded-pill"><i class="bi bi-slash-circle-fill text-success me-1" aria-hidden="true"></i> {h_price}</span>
            <span class="badge bg-dark border border-secondary text-white-50 px-3 py-2 rounded-pill"><i class="bi bi-translate text-warning me-1" aria-hidden="true"></i> 28 languages</span>
          </div>
        </div>

        <div class="col-lg-5 text-center">
          <div class="position-relative d-inline-block p-4 w-100">
            <div class="position-absolute top-50 start-50 translate-middle w-100 h-100 rounded-circle bg-primary opacity-25 blur-3xl glow-aura-blue"></div>

            <div class="card card-glass p-4 text-center border-0 animated-float position-relative" style="background: rgba(17, 24, 39, 0.85);">
              <div class="mx-auto mb-3" style="width: 140px; height: 140px; border-radius: 30px; overflow: hidden; border: 3px solid rgba(56,189,248,0.5); box-shadow: 0 15px 35px rgba(56,189,248,0.3);">
                <img src="/assets/images/glowcompare-icon.png" alt="GlowCompare App Icon" class="w-100 h-100 object-fit-cover" decoding="async" fetchpriority="high">
              </div>
              <p class="h4 text-white fw-bold mb-1">GlowCompare</p>
              <p class="small text-primary fw-semibold mb-3"><i class="bi bi-microsoft me-1" aria-hidden="true"></i> Store ID: 9N4QM1FDQ1CB</p>

              <a href="{store}" target="_blank" rel="noopener" class="btn btn-primary btn-lg w-100 fw-bold rounded-3 shadow py-3 d-flex align-items-center justify-content-center gap-2">
                <i class="bi bi-microsoft fs-5" aria-hidden="true"></i> Get on Microsoft Store
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Why progress photos fail -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle">
    <div class="container py-4">
      <div class="row align-items-center gy-5">
        <div class="col-lg-6">
          <span class="badge bg-primary-subtle text-primary border border-primary-subtle rounded-pill px-3 py-2 fw-semibold mb-3">
            <i class="bi bi-camera-fill me-1" aria-hidden="true"></i> Ghost overlay
          </span>
          <h2 class="display-6 fw-bold text-white mb-3">{h_why}</h2>
          <p class="text-secondary fs-5 mb-3">{why1}</p>
          <p class="text-secondary mb-0">{why2}</p>
        </div>
        <div class="col-lg-6">
          <div class="card card-glass p-3 border border-primary border-opacity-25 shadow-lg">
            <div class="ghost-stack">
              <img src="/assets/images/glowcompare-slider-after.jpg" alt="Camera preview with alignment guide" loading="lazy" decoding="async">
              <div class="ghost-layer">
                <img src="/assets/images/glowcompare-slider-before.jpg" alt="" aria-hidden="true" loading="lazy" decoding="async">
              </div>
            </div>
            <p class="extra-small text-muted mt-3 mb-0 text-center">
              <i class="bi bi-layers-half text-primary me-1" aria-hidden="true"></i> Ghost overlay &middot; front / left / right timelines
            </p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- See the difference + interactive comparator -->
  <section id="see-the-difference" class="py-5">
    <div class="container py-4">
      <div class="text-center max-w-700 mx-auto mb-5">
        <span class="text-gradient-rose fw-bold text-uppercase tracking-wider">Before / after</span>
        <h2 class="display-5 fw-bold text-white mt-2">{h_see}</h2>
        <p class="text-secondary fs-5">{see}</p>
      </div>

      <div class="row justify-content-center">
        <div class="col-lg-8">
          <div class="before-after-slider-container" id="webSplitSlider">
            <img src="/assets/images/glowcompare-slider-after.jpg" alt="After skincare progress view" class="slider-base-img" loading="lazy" decoding="async">
            <div class="before-after-slider-overlay" id="sliderOverlay">
              <img src="/assets/images/glowcompare-slider-before.jpg" alt="Before skincare baseline view" class="slider-overlay-img" id="sliderOverlayImg" loading="lazy" decoding="async">
            </div>
            <div class="before-after-slider-handle" id="sliderHandle">
              <i class="bi bi-arrows-left-right" aria-hidden="true"></i>
            </div>
          </div>
          <p class="text-center text-secondary small mt-3 mb-0">
            <i class="bi bi-arrow-left-right me-1 text-primary" aria-hidden="true"></i> Drag left or right
          </p>
        </div>
      </div>
    </div>
  </section>

  <!-- AI skin analysis -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle">
    <div class="container py-4">
      <div class="text-center max-w-700 mx-auto mb-5">
        <span class="badge bg-primary-subtle text-primary border border-primary-subtle rounded-pill px-3 py-2 fw-semibold mb-2">
          <i class="bi bi-cpu-fill me-1" aria-hidden="true"></i> 9 &times; 100
        </span>
        <h2 class="display-5 fw-bold text-white">{h_ai}</h2>
        <p class="text-secondary fs-5">{ai1}</p>
      </div>

      <div class="row g-3 mb-4">
{metric_cards}
      </div>

      <div class="p-4 rounded-4 bg-black border border-secondary">
        <p class="text-secondary mb-0"><i class="bi bi-clipboard2-check text-primary me-2" aria-hidden="true"></i>{ai2}</p>
      </div>
    </div>
  </section>

  <!-- AI chat -->
  <section class="py-5">
    <div class="container py-4">
      <div class="row align-items-center gy-5">
        <div class="col-lg-6">
          <span class="badge bg-rose-subtle-custom rounded-pill px-3 py-2 fw-semibold mb-3">
            <i class="bi bi-stars me-1" aria-hidden="true"></i> Ask &amp; attach photos
          </span>
          <h2 class="display-6 fw-bold text-white mb-3">{h_chat}</h2>
          <p class="text-secondary fs-5 mb-0">{chat}</p>
        </div>
        <div class="col-lg-6">
          <div class="ai-chat-panel p-4">
            <div class="d-flex align-items-center gap-2 mb-4 pb-3 border-bottom border-secondary-subtle">
              <span class="feature-icon-box"><i class="bi bi-robot" aria-hidden="true"></i></span>
              <span class="fw-bold text-white">{h_chat}</span>
            </div>
            <div class="d-flex flex-column gap-3">
              <div class="ai-chat-bubble ai-chat-bubble-user"><i class="bi bi-person-circle me-2" aria-hidden="true"></i><i class="bi bi-image me-1" aria-hidden="true"></i><i class="bi bi-three-dots" aria-hidden="true"></i></div>
              <div class="ai-chat-bubble ai-chat-bubble-ai"><i class="bi bi-robot me-2" aria-hidden="true"></i><i class="bi bi-three-dots" aria-hidden="true"></i></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Product shelf + routines -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle">
    <div class="container py-4">
      <div class="row g-4">
        <div class="col-lg-6">
          <div class="card card-glass h-100 p-4">
            <div class="win-icon-box mb-3"><i class="bi bi-upc-scan" aria-hidden="true"></i></div>
            <h2 class="h3 text-white fw-bold mb-3">{h_scan}</h2>
            <p class="text-secondary mb-0">{scan}</p>
          </div>
        </div>
        <div class="col-lg-6">
          <div class="card card-glass h-100 p-4">
            <div class="win-icon-box mb-3"><i class="bi bi-calendar2-check" aria-hidden="true"></i></div>
            <h2 class="h3 text-white fw-bold mb-3">{h_routine}</h2>
            <p class="text-secondary mb-0">{routine}</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Built for Windows -->
  <section class="py-5">
    <div class="container py-4">
      <div class="row align-items-center gy-5">
        <div class="col-lg-6">
          <span class="badge-store-ms mb-3 d-inline-block"><i class="bi bi-microsoft me-1" aria-hidden="true"></i> WinUI 3</span>
          <h2 class="display-5 fw-bold text-white mb-3">{h_win}</h2>
          <p class="text-secondary fs-5 mb-0">{win}</p>
        </div>
        <div class="col-lg-6">
          <div class="row g-3">
            <div class="col-sm-6">
              <div class="card card-glass h-100 p-3 text-center">
                <div class="win-icon-box mx-auto mb-2"><i class="bi bi-window-desktop" aria-hidden="true"></i></div>
                <p class="small text-white fw-semibold mb-0">Native WinUI 3</p>
              </div>
            </div>
            <div class="col-sm-6">
              <div class="card card-glass h-100 p-3 text-center">
                <div class="win-icon-box mx-auto mb-2"><i class="bi bi-bell-fill" aria-hidden="true"></i></div>
                <p class="small text-white fw-semibold mb-0">Windows notifications</p>
              </div>
            </div>
            <div class="col-sm-6">
              <div class="card card-glass h-100 p-3 text-center">
                <div class="win-icon-box mx-auto mb-2"><i class="bi bi-fingerprint" aria-hidden="true"></i></div>
                <p class="small text-white fw-semibold mb-0">Windows Hello lock</p>
              </div>
            </div>
            <div class="col-sm-6">
              <div class="card card-glass h-100 p-3 text-center">
                <div class="win-icon-box mx-auto mb-2"><i class="bi bi-folder2-open" aria-hidden="true"></i></div>
                <p class="small text-white fw-semibold mb-0">Backup &amp; restore</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Honest / privacy / pricing -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle">
    <div class="container py-4">
      <div class="row g-4">
        <div class="col-lg-4">
          <div class="card card-glass h-100 p-4">
            <div class="win-icon-box mb-3"><i class="bi bi-hand-thumbs-up" aria-hidden="true"></i></div>
            <h2 class="h4 text-white fw-bold mb-2">{h_honest}</h2>
            <p class="text-secondary small mb-0">{honest}</p>
          </div>
        </div>
        <div class="col-lg-4">
          <div class="card card-glass h-100 p-4 border border-primary border-opacity-25">
            <div class="win-icon-box mb-3"><i class="bi bi-shield-lock-fill" aria-hidden="true"></i></div>
            <h2 class="h4 text-white fw-bold mb-2">{h_privacy}</h2>
            <p class="text-secondary small mb-0">{privacy}</p>
          </div>
        </div>
        <div class="col-lg-4">
          <div class="card card-glass h-100 p-4 border border-success-subtle">
            <div class="win-icon-box mb-3" style="background: linear-gradient(135deg, rgba(25,135,84,0.2), rgba(56,189,248,0.15)); color: #4ade80; border-color: rgba(25,135,84,0.35);"><i class="bi bi-wallet2" aria-hidden="true"></i></div>
            <h2 class="h4 text-white fw-bold mb-2">{h_price}</h2>
            <p class="text-secondary small mb-0">{price}</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Final CTA + disclaimer -->
  <section class="py-5">
    <div class="container py-4">
      <div class="card card-glass p-5 text-center border-0 position-relative overflow-hidden" style="background: linear-gradient(135deg, rgba(56,189,248,0.14) 0%, rgba(255,117,140,0.16) 100%);">
        <div class="max-w-700 mx-auto position-relative" style="z-index: 2;">
          <div class="mx-auto mb-3" style="width: 90px; height: 90px; border-radius: 20px; overflow: hidden; border: 2px solid rgba(56,189,248,0.5);">
            <img src="/assets/images/glowcompare-icon.png" alt="GlowCompare Icon" class="w-100 h-100 object-fit-cover" loading="lazy" decoding="async">
          </div>
          <h2 class="display-6 fw-bold text-white mb-3">{name}</h2>
          <p class="text-secondary fs-5 mb-4">{tagline}</p>
          <div class="d-flex justify-content-center">
            <a href="{store}" target="_blank" rel="noopener" class="btn btn-primary btn-lg rounded-pill px-5 shadow">
              <i class="bi bi-microsoft me-2 fs-5" aria-hidden="true"></i> Get on Microsoft Store
            </a>
          </div>
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
  <script src="/assets/js/glowcompare-slider.js"></script>

  <div class="install-bar" role="complementary" aria-label="GlowCompare for Windows">
    <img src="/assets/images/glowcompare-icon.png" alt="" width="42" height="42" loading="lazy" decoding="async">
    <div class="install-bar-text">
      <div class="install-bar-title">GlowCompare</div>
      <div class="install-bar-sub"><i class="bi bi-microsoft" aria-hidden="true"></i> Microsoft Store</div>
    </div>
    <a href="{store}" target="_blank" rel="noopener" class="btn btn-primary btn-sm rounded-pill px-3">Install</a>
  </div>
  <button type="button" class="to-top" aria-label="Back to top" title="Back to top">
    <i class="bi bi-arrow-up" aria-hidden="true"></i>
  </button>
  <script src="/assets/js/ux.js"></script>
</body>
</html>
""".format(
        hl=hl,
        dir=direction,
        title=E(title),
        desc=E(desc),
        page_css=PAGE_CSS,
        hreflang=hreflang_block(code),
        canonical=abs_url(code),
        site=SITE,
        og=og,
        og_alts=og_alts,
        schema=schema(code, t, title, desc),
        navbar=navbar(code),
        footer=FOOTER,
        store=E(STORE_UTM),
        metric_cards=metric_cards(t["metrics"]),
        name=E(t["name"]),
        tagline=E(t["tagline"]),
        intro1=E(t["intro1"]),
        intro2=E(t["intro2"]),
        h_why=E(t["h_why"]), why1=E(t["why1"]), why2=E(t["why2"]),
        h_see=E(t["h_see"]), see=E(t["see"]),
        h_ai=E(t["h_ai"]), ai1=E(t["ai1"]), ai2=E(t["ai2"]),
        h_chat=E(t["h_chat"]), chat=E(t["chat"]),
        h_scan=E(t["h_scan"]), scan=E(t["scan"]),
        h_routine=E(t["h_routine"]), routine=E(t["routine"]),
        h_win=E(t["h_win"]), win=E(t["win"]),
        h_honest=E(t["h_honest"]), honest=E(t["honest"]),
        h_privacy=E(t["h_privacy"]), privacy=E(t["privacy"]),
        h_price=E(t["h_price"]), price=E(t["price"]),
        h_important=E(t["h_important"]), important=E(t["important"]),
    )
    return doc


def main():
    base = os.path.join(ROOT, SECTION)
    for code, _label, _d, _hl, _og in LANGS:
        folder = base if code == "en" else os.path.join(base, code)
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, "index.html")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(build(code))
        print("wrote", path)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
