#!/usr/bin/env python3
"""
Generate /stow/ - "Stow: Photo & File Organizer - Offline AI", the Microsoft
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
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STRINGS = os.path.join(ROOT, "tools", "stow-strings.json")

with open(STRINGS, encoding="utf-8") as _fh:
    L = json.load(_fh)

SECTION = "stow"

SITE = "https://www.dhinovatech.com"
STORE_ID = "9NHBR7SW2TZ0"
STORE = "https://apps.microsoft.com/detail/" + STORE_ID
STORE_UTM = STORE + "?ocid=dhinovatech_stow"

ICON = "/assets/images/stow-icon.png"
OGIMG = "/assets/images/stow-icon.png"
OGW, OGH = 512, 512
OGALT = "Stow photo and file organizer icon"

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

# The strings file is the source of truth for which locales have copy; the page
# is only emitted for locales that actually have a block, so a partially
# translated strings file still builds rather than raising KeyError.
MISSING = set(BY_CODE) - set(L)
EXTRA = set(L) - set(BY_CODE)
assert not EXTRA, "strings for unknown locales: %s" % sorted(EXTRA)

E = html.escape

# The four model bundles. Names, licences and sizes are proper nouns and
# figures, so they are identical in every locale; only the "what it does"
# column comes from the strings file.
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


def built_langs():
    return [x for x in LANGS if x[0] in L]


# --------------------------------------------------------------------------
# Shared navigation - Stow owns its own language tree.
# --------------------------------------------------------------------------

def lang_items(active, icon):
    """One <li> per locale for the language menus.

    The selected row gets Bootstrap's .active, which paints a solid primary
    background and sets its own foreground colour. Adding text-primary on top
    of that would repaint the label and the icon blue on blue and make the row
    unreadable, so the accent colour is applied only to the inactive rows.
    """
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

          <!-- Our Apps - Stow owns its own language tree -->
          <li class="nav-item dropdown">
            <a class="nav-link nav-link-custom dropdown-toggle active" href="#" id="appsDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
              Our Apps
            </a>
            <ul class="dropdown-menu dropdown-menu-dark border-secondary shadow-lg mt-2" aria-labelledby="appsDropdown">
              <li class="dropdown-submenu position-relative">
                <a class="dropdown-item py-2 d-flex align-items-center justify-content-between" href="/stow/">
                  <span><img src="__ICON__" alt="Stow Icon" style="width: 20px; height: 20px; border-radius: 5px; object-fit: cover;" class="me-2" decoding="async">Stow Photo &amp; File Organizer</span>
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
              <i class="bi bi-microsoft fs-5" aria-hidden="true"></i> Get on Microsoft Store
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
    /* Scoped Stow accents - emerald/teal, to sit apart from the other
       Microsoft Store pages on this site. */
    .glow-aura-teal { box-shadow: 0 0 45px rgba(45, 212, 191, 0.32); }
    .stow-icon-box {
      width: 52px; height: 52px; border-radius: 14px;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.4rem; flex-shrink: 0;
      background: linear-gradient(135deg, rgba(45,212,191,0.18), rgba(56,189,248,0.16));
      color: #2dd4bf; border: 1px solid rgba(45,212,191,0.3);
    }
    .stow-badge-row { display: flex; flex-wrap: wrap; gap: .5rem; }
    .stow-num {
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 1.6rem; font-weight: 700; color: #2dd4bf; line-height: 1;
    }
    .stow-num-zero { color: #4ade80; }
    /* The plan preview mock. It is decorative, so it is built from text rather
       than an image - it stays sharp, translates with the page and costs
       nothing to download. */
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
    .plan-table .plan-dest { color: #2dd4bf; }
    .plan-table .plan-rule { color: #64748b; }
    .plan-scroll { overflow-x: auto; }
    .stow-step {
      width: 34px; height: 34px; border-radius: 50%; flex-shrink: 0;
      display: flex; align-items: center; justify-content: center;
      font-weight: 700; font-size: .9rem;
      background: rgba(45,212,191,0.15); color: #2dd4bf;
      border: 1px solid rgba(45,212,191,0.35);
    }
    .model-table td, .model-table th { vertical-align: middle; }
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
         # Deliberately the https web listing, not ms-windows-store://: a custom
         # scheme is not a crawlable URL and would invalidate the markup.
         "downloadUrl": STORE,
         "installUrl": STORE,
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
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
    return json.dumps({"@context": "https://schema.org", "@graph": graph},
                      ensure_ascii=False, separators=(",", ":"))


# ------------------------------------------------------------------ fragments

def stat_cards(t):
    """The five preview counters. The last one is the point of the screen, so it
    is styled apart and always reads zero."""
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
                "text-success" if last else "text-primary",
                " stow-num-zero" if last else "",
                "0" if last else "&mdash;",
                E(lab)))
    return "\n".join(out)


def numbered_cards(items, icons):
    out = []
    for i, it in enumerate(items):
        out.append(
            """          <div class="col-lg-4 col-md-6">
            <div class="card card-glass h-100 p-4">
              <div class="d-flex align-items-center gap-3 mb-3">
                <span class="stow-icon-box"><i class="bi %s" aria-hidden="true"></i></span>
                <h3 class="h5 text-white fw-bold mb-0">%s</h3>
              </div>
              <p class="text-secondary small mb-0">%s</p>
            </div>
          </div>""" % (icons[i % len(icons)], E(it["t"]), E(it["b"])))
    return "\n".join(out)


def step_rows(items):
    out = []
    for i, it in enumerate(items):
        out.append(
            """          <div class="col-12">
            <div class="card card-glass p-4">
              <div class="d-flex gap-3 align-items-start">
                <span class="stow-step">%d</span>
                <div>
                  <h3 class="h5 text-white fw-bold mb-2">%s</h3>
                  <p class="text-secondary small mb-0">%s</p>
                </div>
              </div>
            </div>
          </div>""" % (i + 1, E(it["t"]), E(it["b"])))
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


# The decorative plan preview. File names and folders are language-neutral, so
# only the column headings are translated.
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


def build(code):
    t = L[code]
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
          <p class="lead text-gradient fw-semibold mb-3 fs-4">{tagline}</p>
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
            <a href="#the-preview" class="btn btn-dhin-outline btn-lg rounded-pill px-4">
              <i class="bi bi-table me-2" aria-hidden="true"></i> {cta_see}
            </a>
          </div>

          <div class="stow-badge-row pt-2">
            <span class="badge bg-dark border border-secondary text-white-50 px-3 py-2 rounded-pill"><i class="bi bi-wifi-off text-primary me-1" aria-hidden="true"></i> 100% offline</span>
            <span class="badge bg-dark border border-secondary text-white-50 px-3 py-2 rounded-pill"><i class="bi bi-arrow-counterclockwise text-info me-1" aria-hidden="true"></i> One-click undo</span>
            <span class="badge bg-dark border border-secondary text-white-50 px-3 py-2 rounded-pill"><i class="bi bi-cpu text-success me-1" aria-hidden="true"></i> x64 &amp; ARM64</span>
            <span class="badge bg-dark border border-secondary text-white-50 px-3 py-2 rounded-pill"><i class="bi bi-translate text-warning me-1" aria-hidden="true"></i> {nlang} languages</span>
          </div>
        </div>

        <div class="col-lg-5 text-center">
          <div class="position-relative d-inline-block p-4 w-100">
            <div class="position-absolute top-50 start-50 translate-middle w-100 h-100 rounded-circle bg-primary opacity-25 blur-3xl glow-aura-teal"></div>

            <div class="card card-glass p-4 text-center border-0 animated-float position-relative" style="background: rgba(17, 24, 39, 0.85);">
              <div class="mx-auto mb-3" style="width: 140px; height: 140px; border-radius: 30px; overflow: hidden; border: 3px solid rgba(45,212,191,0.5); box-shadow: 0 15px 35px rgba(45,212,191,0.3);">
                <img src="{icon}" alt="Stow App Icon" class="w-100 h-100 object-fit-cover" decoding="async" fetchpriority="high" width="512" height="512">
              </div>
              <p class="h4 text-white fw-bold mb-1">Stow</p>
              <p class="small text-primary fw-semibold mb-3"><i class="bi bi-microsoft me-1" aria-hidden="true"></i> Store ID: {store_id}</p>

              <a href="{store}" target="_blank" rel="noopener" class="btn btn-primary btn-lg w-100 fw-bold rounded-3 shadow py-3 d-flex align-items-center justify-content-center gap-2">
                <i class="bi bi-microsoft fs-5" aria-hidden="true"></i> Get on Microsoft Store
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- The problem -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle">
    <div class="container py-4">
      <div class="row align-items-center gy-4">
        <div class="col-lg-6">
          <span class="badge bg-primary-subtle text-primary border border-primary-subtle rounded-pill px-3 py-2 fw-semibold mb-3">
            <i class="bi bi-folder2-open me-1" aria-hidden="true"></i> The backlog
          </span>
          <h2 class="display-6 fw-bold text-white mb-3">{h_problem}</h2>
          <p class="text-secondary fs-5 mb-0">{problem1}</p>
        </div>
        <div class="col-lg-6">
          <p class="text-secondary mb-0">{problem2}</p>
        </div>
      </div>
    </div>
  </section>

  <!-- The preview -->
  <section id="the-preview" class="py-5">
    <div class="container py-4">
      <div class="text-center max-w-700 mx-auto mb-5">
        <span class="text-gradient fw-bold text-uppercase tracking-wider">Nothing has moved yet</span>
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

  <!-- Five principles -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle">
    <div class="container py-4">
      <div class="text-center max-w-700 mx-auto mb-5">
        <span class="badge bg-primary-subtle text-primary border border-primary-subtle rounded-pill px-3 py-2 fw-semibold mb-2">
          <i class="bi bi-shield-lock-fill me-1" aria-hidden="true"></i> By design
        </span>
        <h2 class="display-5 fw-bold text-white">{h_principles}</h2>
      </div>
      <div class="row g-4">
{principle_cards}
      </div>
    </div>
  </section>

  <!-- Five ways in -->
  <section class="py-5">
    <div class="container py-4">
      <div class="text-center max-w-700 mx-auto mb-5">
        <h2 class="display-5 fw-bold text-white">{h_ways}</h2>
        <p class="text-secondary fs-5">{ways}</p>
      </div>
      <div class="row g-3">
{way_rows}
      </div>
    </div>
  </section>

  <!-- Undo -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle">
    <div class="container py-4">
      <div class="row align-items-center gy-4">
        <div class="col-lg-6">
          <div class="stow-icon-box mb-3"><i class="bi bi-arrow-counterclockwise" aria-hidden="true"></i></div>
          <h2 class="display-6 fw-bold text-white mb-3">{h_undo}</h2>
          <p class="text-secondary fs-5 mb-0">{undo1}</p>
        </div>
        <div class="col-lg-6">
          <p class="text-secondary mb-0">{undo2}</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Finding things -->
  <section class="py-5">
    <div class="container py-4">
      <div class="text-center max-w-700 mx-auto mb-5">
        <h2 class="display-5 fw-bold text-white">{h_find}</h2>
        <p class="text-secondary fs-5">{find}</p>
      </div>
      <div class="row g-4">
{find_cards}
      </div>
    </div>
  </section>

  <!-- Duplicates -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle">
    <div class="container py-4">
      <div class="row align-items-center gy-4">
        <div class="col-lg-6">
          <div class="stow-icon-box mb-3"><i class="bi bi-files" aria-hidden="true"></i></div>
          <h2 class="display-6 fw-bold text-white mb-3">{h_dupes}</h2>
          <p class="text-secondary fs-5 mb-0">{dupes1}</p>
        </div>
        <div class="col-lg-6">
          <p class="text-secondary mb-0">{dupes2}</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Three more things -->
  <section class="py-5">
    <div class="container py-4">
      <div class="text-center max-w-700 mx-auto mb-5">
        <h2 class="display-5 fw-bold text-white">{h_more}</h2>
      </div>
      <div class="row g-4">
{more_cards}
      </div>
    </div>
  </section>

  <!-- Privacy -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle">
    <div class="container py-4">
      <div class="row align-items-center gy-4">
        <div class="col-lg-6">
          <span class="badge bg-success-subtle text-success border border-success-subtle rounded-pill px-3 py-2 fw-semibold mb-3">
            <i class="bi bi-wifi-off me-1" aria-hidden="true"></i> No account &middot; no server &middot; no telemetry
          </span>
          <h2 class="display-6 fw-bold text-white mb-3">{h_privacy}</h2>
          <p class="text-secondary fs-5 mb-0">{privacy1}</p>
        </div>
        <div class="col-lg-6">
          <p class="text-secondary mb-0">{privacy2}</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Models -->
  <section class="py-5">
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

  <!-- Final CTA + honest limits -->
  <section class="py-5">
    <div class="container py-4">
      <div class="card card-glass p-5 text-center border-0 position-relative overflow-hidden" style="background: linear-gradient(135deg, rgba(45,212,191,0.14) 0%, rgba(56,189,248,0.16) 100%);">
        <div class="max-w-700 mx-auto position-relative" style="z-index: 2;">
          <div class="mx-auto mb-3" style="width: 90px; height: 90px; border-radius: 20px; overflow: hidden; border: 2px solid rgba(45,212,191,0.5);">
            <img src="{icon}" alt="Stow Icon" class="w-100 h-100 object-fit-cover" loading="lazy" decoding="async" width="512" height="512">
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

  <!-- BEGIN generated UX block -->
  <div class="install-bar" role="complementary" aria-label="Stow Photo &amp; File Organizer">
    <img src="{icon}" alt="" width="42" height="42" loading="lazy" decoding="async">
    <div class="install-bar-text">
      <div class="install-bar-title">Stow</div>
      <div class="install-bar-sub"><i class="bi bi-microsoft" aria-hidden="true"></i> Microsoft Store</div>
    </div>
    <a href="{store}" target="_blank" rel="noopener" class="btn btn-primary btn-sm rounded-pill px-3">Install</a>
  </div>
  <button type="button" class="to-top" aria-label="Back to top" title="Back to top">
    <i class="bi bi-arrow-up" aria-hidden="true"></i>
  </button>
  <script src="/assets/js/ux.js"></script>
  <!-- END generated UX block -->
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
        ogimg=OGIMG, ogw=OGW, ogh=OGH, ogalt=E(OGALT),
        og=og,
        og_alts=og_alts,
        schema=schema(code, t, desc),
        navbar=navbar(code),
        footer=FOOTER,
        store=E(STORE_UTM),
        store_id=STORE_ID,
        icon=ICON,
        nlang=len(built_langs()),
        name=E(t["name"]),
        tagline=E(t["tagline"]),
        intro1=E(t["intro1"]),
        intro2=E(t["intro2"]),
        cta_see=E(t["cta_see"]),
        h_problem=E(t["h_problem"]), problem1=E(t["problem1"]), problem2=E(t["problem2"]),
        h_preview=E(t["h_preview"]), preview1=E(t["preview1"]), preview2=E(t["preview2"]),
        stat_cards=stat_cards(t), stats_note=E(t["stats_note"]),
        plan_head=plan_head, plan_body=plan_body,
        h_principles=E(t["h_principles"]),
        principle_cards=numbered_cards(t["principles"], [
            "bi-wifi-off", "bi-table", "bi-trash", "bi-arrow-counterclockwise", "bi-diagram-3"]),
        h_ways=E(t["h_ways"]), ways=E(t["ways"]),
        way_rows=step_rows(t["way_items"]),
        h_undo=E(t["h_undo"]), undo1=E(t["undo1"]), undo2=E(t["undo2"]),
        h_find=E(t["h_find"]), find=E(t["find"]),
        find_cards=numbered_cards(t["find_items"], [
            "bi-search", "bi-image", "bi-hdd-fill", "bi-geo-alt-fill", "bi-tags-fill"]),
        h_dupes=E(t["h_dupes"]), dupes1=E(t["dupes1"]), dupes2=E(t["dupes2"]),
        h_more=E(t["h_more"]),
        more_cards=numbered_cards(t["more_items"], [
            "bi-input-cursor-text", "bi-eye", "bi-link-45deg"]),
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
    if MISSING:
        print("\nno copy yet (page not emitted): %s" % " ".join(sorted(MISSING)))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
