#!/usr/bin/env python3
"""
Generate /mortgage-loan-emi-pro/ - "Mortgage Loan EMI Pro Insights", the
Microsoft Store (WinUI 3) mortgage, EMI and loan calculator, in the app's 23
languages.

Version 3 of the app was rebuilt as a free app with a Pro add-on, and this
page replaces the hand-written one that described the old paid app. It is built
on the same template as /smart-photos/, /KeepOne/ and /steptell/: its own
navigation tree whose language switcher lists only this app's locales, every
CTA pointing at the Store listing, real store slides, and the install bar /
back-to-top chrome wrapped in tools/build-ux.py's BEGIN/END markers so that
builder replaces it rather than appending a copy.

The copy comes from two files:

  * tools/mortgage-listing.json - the store listing's own translated text, the
    words on the slides, the twelve decision tools and the calculator labels
    from the app's AppResources, and each market's demo loan. Refreshed from
    the app repository by tools/build-mortgage-shots.py.
  * tools/mortgage-strings.json - what is written for this page: the at-a-glance
    facts, comparison, who it is for, pricing labels and the FAQ. Every claim
    was checked against the app's code on 2026-11-04: IFeatureGate.ProFeature
    (what Pro gates), ScenarioService.FreeSlotLimit, SettingsService.Currencies,
    ProLicencePolicy (earlier buyers), the absence of any HTTP client or
    telemetry, and the manifest (Windows 10 1809+, x86/x64/ARM64).

The page opens with a small working calculator (assets/js/mortgage-calc.js):
someone searching for a mortgage or EMI calculator expects one. It opens on the
same demo loan as that language's slide 1 and rounds to cents as the app does,
so its "interest saved" matches the slide. Its first result is also rendered
here, so the numbers are in the HTML before any script runs.

No price for Pro: it varies by market, and the Store and the app show the live
one. The Offer in the structured data is the app's own price, 0. No rating
either: the listing has none yet.

Store links are ordinary https://apps.microsoft.com/detail/... URLs so they
work everywhere and stay crawlable; assets/js/ux.js upgrades them to
ms-windows-store:// in place when the visitor is on Windows.

Run:  python tools/build-mortgage.py
Idempotent: every page is rewritten from the two JSON files on each run.
"""
import html
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")


def _load(name):
    with open(os.path.join(TOOLS, name), encoding="utf-8") as fh:
        return json.load(fh)


S = _load("mortgage-strings.json")
LISTING = _load("mortgage-listing.json")
CONSENT_L = _load("consent-strings.json")

APP = "Mortgage Loan EMI Pro Insights"
SECTION = "mortgage-loan-emi-pro"
SITE = "https://www.dhinovatech.com"
STORE_ID = "9PFS2J56BJXR"
STORE = "https://apps.microsoft.com/detail/" + STORE_ID
STORE_UTM = STORE + "?ocid=dhinovatech_mortgage"

ICON = "/assets/images/mortgage-emi-icon.png"
ICON_WEBP = "/assets/images/mortgage-emi-icon.webp"
PRIVACY = "/mortgage-loan-emi-pro/privacy.html"
# When the page's copy last changed in substance; the WebPage schema reports it.
MODIFIED = "2026-11-04"
OGIMG = "/assets/images/mortgage-emi-og.png"
OGW, OGH = 1200, 630
OGALT = "Mortgage Loan EMI Pro Insights - free mortgage, EMI and loan calculator for Windows on the Microsoft Store"

# The store slides tools/build-mortgage-shots.py writes. HERO is slide 1; SHOTS
# are slides 3-10, in the order of listing "shots" (and of "captions"[2:]).
HERO = "mortgage-emi-calculator"
SHOTS = ["loan-calculator", "extra-payment-calculator", "loan-charts", "amortization-schedule",
         "compare-loans", "loan-decision-tools", "inflation-adjusted-loan-cost", "my-loans-tracking"]
SHOT_W, SHOT_H = 1200, 675
SHOT_ICONS = ["bi-calculator", "bi-piggy-bank", "bi-graph-up-arrow", "bi-table",
              "bi-layout-three-columns", "bi-signpost-split", "bi-cash-coin", "bi-bank"]
# (shot index, description paragraph): the three that get a full row.
STORY = [(0, 2), (1, 3), (6, 6)]
GALLERY = [2, 3, 4, 5, 7]
# The ten overview tiles of store slide 2, keyed by the kit's own icon names.
TILE_ICONS = {"calc": "bi-calculator", "savings": "bi-piggy-bank", "schedule": "bi-table",
              "charts": "bi-graph-up-arrow", "compare": "bi-layout-three-columns",
              "tools": "bi-signpost-split", "today": "bi-cash-coin", "tax": "bi-bank",
              "tracker": "bi-bullseye", "report": "bi-file-earmark-spreadsheet"}
CHIP_ICONS = ["bi-house-door text-info", "bi-table text-success",
              "bi-signpost-split text-warning", "bi-shield-lock text-success"]
# In the order of the app's Tools page (listing "tools").
TOOL_ICONS = ["bi-cash-stack", "bi-hourglass-split", "bi-percent", "bi-flag", "bi-wallet2",
              "bi-graph-up", "bi-arrow-left-right", "bi-piggy-bank", "bi-house-heart",
              "bi-box-arrow-in-down", "bi-tag", "bi-calendar3"]
WHO_ICONS = ["bi-house-heart", "bi-graph-down-arrow", "bi-arrow-left-right", "bi-car-front"]
TRUST_ICONS = ["bi-bank", "bi-shield-lock", "bi-globe2"]

# Row order follows t["cmp_rows"]. Columns: this app, a typical website
# calculator, a spreadsheet template. y = yes, p = partly, n = no; the same in
# every language, and hedged by t["cmp_note"] because individual tools vary.
CMP_MARKS = ["yny", "ypy", "ypy", "ypp", "ypp", "ynp", "ynn", "ypn", "ynp"]
MARK_ICON = {"y": "bi-check-circle-fill peer-y", "p": "bi-dash-circle-fill peer-p",
             "n": "bi-x-circle-fill peer-n"}

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
    ("hi", "हिन्दी (Hindi)", "ltr", "hi", "hi_IN"),
    ("de", "Deutsch (German)", "ltr", "de", "de_DE"),
    ("fr", "Français (French)", "ltr", "fr", "fr_FR"),
    ("es", "Español (Spanish)", "ltr", "es", "es_ES"),
    ("it", "Italiano (Italian)", "ltr", "it", "it_IT"),
    ("pt", "Português (Brasil)", "ltr", "pt-BR", "pt_BR"),
    ("nl", "Nederlands (Dutch)", "ltr", "nl", "nl_NL"),
    ("pl", "Polski (Polish)", "ltr", "pl", "pl_PL"),
    ("cs", "Čeština (Czech)", "ltr", "cs", "cs_CZ"),
    ("da", "Dansk (Danish)", "ltr", "da", "da_DK"),
    ("sv", "Svenska (Swedish)", "ltr", "sv", "sv_SE"),
    ("nb", "Norsk (Norwegian)", "ltr", "nb", "nb_NO"),
    ("ru", "Русский (Russian)", "ltr", "ru", "ru_RU"),
    ("tr", "Türkçe (Turkish)", "ltr", "tr", "tr_TR"),
    ("ja", "日本語 (Japanese)", "ltr", "ja", "ja_JP"),
    ("ko", "한국어 (Korean)", "ltr", "ko", "ko_KR"),
    ("zh", "简体中文 (Simplified Chinese)", "ltr", "zh-Hans", "zh_CN"),
    ("zh-tw", "繁體中文 (Traditional Chinese)", "ltr", "zh-Hant", "zh_TW"),
    ("th", "ไทย (Thai)", "ltr", "th", "th_TH"),
    ("vi", "Tiếng Việt (Vietnamese)", "ltr", "vi", "vi_VN"),
    ("id", "Bahasa Indonesia (Indonesian)", "ltr", "id", "id_ID"),
    ("ar", "العربية (Arabic)", "rtl", "ar", "ar_AR"),
]
BY_CODE = {row[0]: row for row in LANGS}

# How money reads in each market, for the figures written into the HTML:
# (group, decimal, prefix, suffix, lakh grouping). assets/js/mortgage-calc.js
# uses Intl for the same job, with the locale in INTL.
NB = " "
MONEY = {
    "en": (",", ".", "$", "", False), "ar": (",", ".", "", NB + "SAR", False),
    "cs": (NB, ",", "", NB + "Kč", False), "da": (".", ",", "", NB + "kr.", False),
    "de": (".", ",", "", NB + "€", False), "es": (".", ",", "", NB + "€", False),
    "fr": (" ", ",", "", NB + "€", False), "hi": (",", ".", "₹", "", True),
    "id": (".", ",", "Rp" + NB, "", False), "it": (".", ",", "", NB + "€", False),
    "ja": (",", ".", "¥", "", False), "ko": (",", ".", "₩", "", False),
    "nb": (NB, ",", "", NB + "kr", False), "nl": (".", ",", "€" + NB, "", False),
    "pl": (NB, ",", "", NB + "zł", False), "pt": (".", ",", "R$" + NB, "", False),
    "ru": (NB, ",", "", NB + "₽", False), "sv": (NB, ",", "", NB + "kr", False),
    "th": (",", ".", "฿", "", False), "tr": (".", ",", "₺", "", False),
    "vi": (".", ",", "", NB + "₫", False), "zh": (",", ".", "¥", "", False),
    "zh-tw": (",", ".", "NT$", "", False),
}
INTL = {"ar": "ar-SA-u-nu-latn"}
FORMULA = "EMI = P × r × (1 + r)ⁿ ÷ ((1 + r)ⁿ − 1)"

E = html.escape


def url_for(code):
    return "/%s/" % SECTION if code == "en" else "/%s/%s/" % (SECTION, code)


def abs_url(code):
    return SITE + url_for(code)


def shot_url(code, slug):
    return "/assets/images/mortgage/%s/%s.webp" % (code, slug)


def built_langs():
    return [x for x in LANGS if x[0] in LISTING]


def lines(paragraph):
    """A description paragraph's lines after its heading."""
    return paragraph.split("\n")[1:]


def para(lst, n):
    """Store description paragraph n without its heading line."""
    return " ".join(lines(lst["description"][n])).strip()


def heading(lst, n):
    return lst["description"][n].split("\n", 1)[0].strip()


def intro(lst, n):
    """The sentence before a bulleted paragraph's list."""
    return " ".join(l for l in lines(lst["description"][n]) if not l.startswith("•")).strip()


def bullets(lst, n):
    return [l.lstrip("• ").strip() for l in lines(lst["description"][n]) if l.startswith("•")]


# ---------------------------------------------------------------- the numbers

def money(code, value):
    group, _dec, pre, suf, lakh = MONEY[code]
    digits = str(int(round(value)))
    if lakh and len(digits) > 3:
        head, tail = digits[:-3], digits[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        body = ",".join(parts + [tail])
    else:
        parts = []
        while len(digits) > 3:
            parts.insert(0, digits[-3:])
            digits = digits[:-3]
        parts.insert(0, digits)
        body = group.join(parts)
    return pre + body + suf


def number(code, value):
    """A rate such as 3.6, with the market's decimal mark."""
    return ("%g" % value).replace(".", MONEY[code][1])


def amortize(demo):
    """The same arithmetic as assets/js/mortgage-calc.js: cents, like the app."""
    r = demo["rate"] / 1200.0
    n = demo["years"] * 12
    emi = round(demo["amount"] * r / (1 - (1 + r) ** -n), 2)

    def run(extra):
        bal, interest, months = float(demo["amount"]), 0.0, 0
        while bal > 0.005 and months < 1200:
            it = round(bal * r, 2)
            months += 1
            pay = bal + it if months == n and not extra else min(emi + extra, bal + it)
            interest += it
            bal = round(bal - (pay - it), 2)
        return interest, months

    base, _m = run(0)
    with_extra, months = run(demo["extra"])
    # The app shows "interest saved" without its cents, so floor it the same way.
    return {"emi": emi, "base": base, "saved": math.floor(base - with_extra + 0.005), "months": n - months}


def plural(n, lang):
    """The CLDR rules for whole numbers, as in the app's TermText.PluralCategory."""
    two, last = n % 100, n % 10
    few = 2 <= last <= 4 and not 12 <= two <= 14
    if lang == "ar":
        if n <= 2:
            return ["Zero", "One", "Two"][n]
        return "Few" if 3 <= two <= 10 else "Many" if two >= 11 else "Other"
    if lang == "ru":
        return "One" if last == 1 and two != 11 else "Few" if few else "Many"
    if lang == "pl":
        return "One" if n == 1 else "Few" if few else "Many"
    if lang == "cs":
        return "One" if n == 1 else "Few" if 2 <= n <= 4 else "Other"
    if lang == "fr":
        return "One" if n <= 1 else "Other"
    return "Other"


def time_text(code, lst, months):
    """A length of time, in the form this language needs for the number."""
    y, m = months // 12, months % 12
    term = lst["term"]
    if not term["years"] or not term["months"]:
        return lst["labels"]["time_fmt"].format(y, m)

    def counted(forms, n):
        return (forms.get(plural(n, code)) or forms["Other"]).format(n)

    if y == 0:
        return counted(term["months"], m)
    if m == 0:
        return counted(term["years"], y)
    return term["join"].format(counted(term["years"], y), counted(term["months"], m))


def figures(code, lst):
    """The values the FAQ's worked examples are written with, per market."""
    demo = lst["demo"]
    res = amortize(demo)
    # Only English and Hindi call the payment an EMI; the rest say what M is.
    formula = FORMULA if code in ("en", "hi") else FORMULA.replace("EMI", "M", 1)
    return {"formula": formula, "amount": money(code, demo["amount"]),
            "rate": number(code, demo["rate"]), "years": str(demo["years"]),
            "emi": money(code, res["emi"]), "extra": money(code, demo["extra"]),
            "saved": money(code, res["saved"]), "time": time_text(code, lst, res["months"])}


# ---------------------------------------------------------------- head blocks

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
# Shared navigation - this app owns its own language tree.
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

          <!-- Our Apps - this app owns its own language tree; build-nav-apps.py
               adds Smart Photos, KeepOne and Steptell above it -->
          <li class="nav-item dropdown">
            <a class="nav-link nav-link-custom dropdown-toggle active" href="#" id="appsDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
              Our Apps
            </a>
            <ul class="dropdown-menu dropdown-menu-dark border-secondary shadow-lg mt-2" aria-labelledby="appsDropdown">
              <li class="dropdown-submenu position-relative">
                <a class="dropdown-item py-2 d-flex align-items-center justify-content-between" href="/mortgage-loan-emi-pro/">
                  <span><img src="__ICON__" alt="Mortgage Loan EMI Pro Insights Icon" style="width: 20px; height: 20px; border-radius: 5px; object-fit: cover;" class="me-2" decoding="async" width="256" height="256">Mortgage EMI Pro</span>
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
              <li><a class="dropdown-item py-2" href="/aes-vault/"><i class="bi bi-safe2 text-danger me-2" aria-hidden="true"></i>AES Vault Encryption</a></li>
            </ul>
          </li>

          <li class="nav-item">
            <a class="nav-link nav-link-custom" href="/about.html">About Us</a>
          </li>
          <li class="nav-item">
            <a class="nav-link nav-link-custom" href="/contact.html">Contact Us</a>
          </li>

          <!-- Language Selector - this app only -->
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
            <li><a href="/mortgage-loan-emi-pro/" class="footer-link text-primary fw-semibold"><i class="bi bi-calculator me-1" aria-hidden="true"></i> Mortgage EMI Pro</a></li>
            <li><a href="/steptell/" class="footer-link"><i class="bi bi-record-circle me-1" aria-hidden="true"></i> Steptell Steps Recorder</a></li>
            <li><a href="/smart-photos/" class="footer-link"><i class="bi bi-images me-1" aria-hidden="true"></i> Smart Photos</a></li>
            <li><a href="/KeepOne/" class="footer-link"><i class="bi bi-intersect me-1" aria-hidden="true"></i> KeepOne Duplicate Finder</a></li>
            <li><a href="/nudge/" class="footer-link"><i class="bi bi-journal-bookmark-fill me-1" aria-hidden="true"></i> Nudge Offline Journal &amp; AI</a></li>
            <li><a href="/stow/" class="footer-link"><i class="bi bi-folder-symlink me-1" aria-hidden="true"></i> Stow Photo &amp; File Organizer</a></li>
            <li><a href="/glowcompare-windows/" class="footer-link"><i class="bi bi-microsoft text-primary me-1" aria-hidden="true"></i> GlowCompare for Windows</a></li>
            <li><a href="/glowcompare/" class="footer-link"><i class="bi bi-sparkles text-danger me-1" aria-hidden="true"></i> GlowCompare for Android</a></li>
            <li><a href="/slouch-guard/" class="footer-link"><i class="bi bi-person-workspace text-info me-1" aria-hidden="true"></i> Slouch Guard AI</a></li>
            <li><a href="/notelock/" class="footer-link"><i class="bi bi-shield-lock text-warning me-1" aria-hidden="true"></i> Notelock Secure Notes</a></li>
            <li><a href="/milk-monthly-expense-calendar/" class="footer-link"><i class="bi bi-calendar2-check text-success me-1" aria-hidden="true"></i> Milk Monthly Calendar</a></li>
            <li><a href="/aes-vault/" class="footer-link"><i class="bi bi-safe2 text-danger me-1" aria-hidden="true"></i> AES Vault Encryption</a></li>
          </ul>
        </div>
        <div class="col-lg-3">
          <h4 class="h6 text-white fw-bold mb-3">Support &amp; Legal</h4>
          <p class="small text-secondary mb-2"><i class="bi bi-envelope-fill me-2 text-primary" aria-hidden="true"></i>dhinovatech@gmail.com</p>
          <p class="small text-secondary mb-2"><i class="bi bi-globe me-2 text-primary" aria-hidden="true"></i>www.dhinovatech.com</p>
          <p class="small mb-0"><a href="/mortgage-loan-emi-pro/privacy.html" class="footer-link"><i class="bi bi-shield-check me-2 text-primary" aria-hidden="true"></i>Mortgage EMI Pro Privacy Policy</a></p>
        </div>
      </div>
      <div class="pt-4 border-top border-secondary text-center text-secondary small">
        <p class="mb-0">&copy; 2026 Dhinovatech. All rights reserved.</p>
      </div>
    </div>
  </footer>
"""

# Same structure as the Smart Photos and Steptell pages, re-keyed to the store
# slides: green for "ALWAYS FREE", amber for "Pay it off years sooner" and Pro,
# on the slides' navy. The custom properties are declared site-wide in
# custom.css, so re-declaring them here re-keys the shared chrome for this
# section only. Blue stays reserved for the Microsoft Store buttons.
PAGE_CSS = """  <style>
    :root {
      --dhin-accent-blue: #34d399;
      --dhin-border-glow: rgba(52, 211, 153, 0.32);
      --dhin-shadow-glow: 0 0 25px rgba(52, 211, 153, 0.18);
      --dhin-gradient-primary: linear-gradient(135deg, #34d399 0%, #2563eb 100%);
      --ml-green: #34d399;
      --ml-green-solid: #22c55e;
      --ml-amber: #fbbf24;
      --ml-ink: #06241a;
    }
    :root, [data-bs-theme="dark"] {
      --bs-primary-rgb: 52, 211, 153;
      --bs-primary-bg-subtle: rgba(52, 211, 153, 0.12);
      --bs-primary-border-subtle: rgba(52, 211, 153, 0.32);
      --bs-primary-text-emphasis: #a7f3d0;
    }
    .text-gradient {
      background: linear-gradient(135deg, #a7f3d0 0%, #34d399 50%, #fbbf24 100%);
      -webkit-background-clip: text;
      background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .btn-dhin-primary { box-shadow: 0 4px 15px rgba(52, 211, 153, 0.24); }
    .btn-dhin-primary:hover { box-shadow: 0 8px 25px rgba(52, 211, 153, 0.38); }
    .btn-dhin-outline:hover { background: rgba(52, 211, 153, 0.1); }
    .hero-section {
      padding: 56px 0 64px;
      background: radial-gradient(circle at 22% 18%, rgba(19, 80, 158, 0.42) 0%, rgba(8, 12, 20, 0) 62%);
    }
    @media (max-width: 991.98px) { .hero-section { padding: 32px 0 48px; } }
    .hero-title { overflow-wrap: anywhere; }

    .glow-aura-blue { box-shadow: 0 0 45px rgba(19, 80, 158, 0.34); }
    .ml-icon-box {
      width: 52px; height: 52px; border-radius: 14px;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.4rem; flex-shrink: 0;
      background: linear-gradient(135deg, rgba(52,211,153,0.16), rgba(37,99,235,0.18));
      color: var(--ml-green); border: 1px solid rgba(52,211,153,0.3);
    }
    .ml-icon-box-sm { width: 38px; height: 38px; font-size: 1.1rem; border-radius: 10px; }
    .ml-badge-row { display: flex; flex-wrap: wrap; gap: .5rem; }
    .ml-step {
      width: 42px; height: 42px; border-radius: 50%; flex-shrink: 0;
      display: flex; align-items: center; justify-content: center;
      font-weight: 800; font-size: 1.1rem;
      background: rgba(52,211,153,0.16); color: var(--ml-green);
      border: 1px solid rgba(52,211,153,0.4);
    }

    /* Hero */
    .ml-hero-icon { width: 60px; height: 60px; flex-shrink: 0; }
    .ml-hero-icon img { width: 100%; height: 100%; object-fit: contain; display: block; border-radius: 13px; }
    .ml-hero-kind { font-weight: 600; color: #e2e8f0; font-size: .95rem; line-height: 1.3; }
    .ml-hero-tagline {
      font-size: clamp(1.15rem, 1rem + 0.8vw, 1.6rem); font-weight: 500;
      line-height: 1.35; letter-spacing: 0; color: #fde68a; margin-top: .6rem;
    }
    .ml-cta-strip .ml-price { margin: 0; }
    .ml-price {
      display: flex; align-items: center; gap: .5rem; flex-wrap: wrap;
      font-size: .92rem; color: #cbd5e1;
    }
    .ml-price-tag {
      background: var(--ml-green-solid); color: var(--ml-ink);
      border-radius: 20px; padding: 3px 14px; font-size: .95rem; font-weight: 800;
      text-decoration: none; box-shadow: 0 0 18px rgba(34, 197, 94, .32);
    }
    .ml-price-tag:hover { color: var(--ml-ink); background: #4ade80; }
    .ml-window {
      border-radius: 14px; overflow: hidden; background: #0d2448;
      border: 1px solid rgba(255,255,255,.12);
      box-shadow: 0 30px 70px -25px rgba(0,0,0,.9);
    }
    .ml-window img { display: block; width: 100%; height: auto; }
    .ml-narrow { max-width: 760px; }

    /* The calculator */
    .ml-calc { border: 1px solid rgba(52,211,153,.28) !important; }
    .ml-field { margin-bottom: 1.05rem; }
    .ml-field label { display: block; font-size: .85rem; font-weight: 600; color: #e2e8f0; margin-bottom: .3rem; }
    .ml-field input[type=number] {
      width: 100%; background: rgba(255,255,255,.06); color: #fff;
      border: 1px solid rgba(255,255,255,.16); border-radius: 10px;
      padding: .5rem .75rem; font-size: 1.02rem; font-weight: 600;
    }
    .ml-field input[type=number]:focus { outline: 2px solid var(--ml-green); outline-offset: 1px; border-color: transparent; }
    .ml-field input[type=range] { width: 100%; margin-top: .45rem; accent-color: var(--ml-green-solid); display: block; }
    .ml-result { background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.09); border-radius: 14px; padding: .9rem 1.05rem; }
    .ml-result-label { font-size: .8rem; color: #94a3b8; line-height: 1.3; }
    .ml-result-value { font-size: clamp(1.25rem, 1rem + 1vw, 1.7rem); font-weight: 800; color: #fff; line-height: 1.2; }
    .ml-saved { background: rgba(6, 36, 26, .75); border: 2px solid var(--ml-green-solid); box-shadow: 0 0 34px rgba(34, 197, 94, .2); }
    .ml-saved .ml-result-label { color: #d1fae5; }
    .ml-saved .ml-result-value { color: #4ade80; font-size: clamp(1.45rem, 1.1rem + 1.4vw, 2.1rem); }
    /* Dong, rupiah and won run to ten or more digits. */
    .ml-calc-long .ml-result-value { font-size: clamp(1.02rem, .9rem + .45vw, 1.28rem); }
    .ml-calc-long .ml-saved .ml-result-value { font-size: clamp(1.1rem, .95rem + .6vw, 1.42rem); }

    /* At a glance */
    .ml-glance-def { font-size: 1.1rem; color: #e2e8f0; line-height: 1.6; }
    .ml-facts { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 0; margin: 0; }
    .ml-fact { padding: 1rem 1.1rem; border-top: 1px solid rgba(255,255,255,.08); }
    .ml-fact dt { font-size: .75rem; text-transform: uppercase; letter-spacing: .06em; color: var(--ml-green); font-weight: 700; margin-bottom: .3rem; }
    .ml-fact dd { margin: 0; font-size: .92rem; color: #cbd5e1; }

    /* Overview tiles */
    .ml-chip { font-size: .68rem; font-weight: 800; letter-spacing: .05em; border-radius: 999px; padding: 2px 10px; white-space: nowrap; }
    .ml-chip-free { background: var(--ml-green-solid); color: var(--ml-ink); }
    .ml-chip-pro { background: var(--ml-amber); color: #2b1d00; }
    .ml-tile-pro { border-color: rgba(251, 191, 36, .42) !important; background: rgba(251, 191, 36, .05) !important; }
    .ml-tile-pro .ml-icon-box { color: var(--ml-amber); border-color: rgba(251,191,36,.4); background: rgba(251,191,36,.12); }

    /* Screenshots */
    .ml-shot { overflow: hidden; margin: 0; }
    .ml-zoom { display: block; cursor: zoom-in; }
    .ml-zoom img { display: block; width: 100%; height: auto; }
    .ml-shot .ml-zoom img { border-bottom: 1px solid rgba(255,255,255,.07); }
    .ml-shot figcaption { padding: 1rem 1.1rem 1.1rem; }
    .ml-kicker { font-size: .74rem; letter-spacing: .08em; font-weight: 700; color: var(--ml-green); text-transform: uppercase; }
    .ml-shot-title { font-size: 1.02rem; font-weight: 700; color: #fff; margin: .25rem 0 .6rem; }
    .ml-shot-pro { border-color: rgba(251,191,36,.42) !important; }
    .ml-shot-pro .ml-kicker { color: var(--ml-amber); }
    .ml-row + .ml-row { margin-top: 3.5rem; }
    @media (min-width: 992px) { .ml-row:nth-child(even) .ml-row-img { order: 2; } }
    .ml-row-title { font-size: clamp(1.45rem, 1.1rem + 1.2vw, 2.1rem); font-weight: 800; color: #fff; line-height: 1.2; margin: .4rem 0 1rem; }
    .ml-lightbox { border: 0; padding: 0; background: transparent; max-width: 96vw; max-height: 94vh; }
    .ml-lightbox::backdrop { background: rgba(3, 7, 14, .9); }
    .ml-lightbox img { display: block; max-width: 96vw; max-height: 94vh; width: auto; height: auto; border-radius: 10px; }
    .ml-lightbox button {
      position: absolute; top: .6rem; inset-inline-end: .6rem; width: 40px; height: 40px;
      border-radius: 50%; border: 0; background: rgba(8,12,20,.8); color: #fff; font-size: 1.2rem;
    }

    /* Cards */
    .invariant-card { border-left: 3px solid var(--ml-green) !important; transition: transform .2s ease, box-shadow .2s ease; }
    [dir="rtl"] .invariant-card { border-left: 0 !important; border-right: 3px solid var(--ml-green) !important; }
    .invariant-card:hover { transform: translateY(-3px); box-shadow: 0 10px 30px rgba(52, 211, 153, 0.1); }
    .pillar-card { transition: transform .2s ease, border-color .2s ease; }
    .pillar-card:hover { transform: translateY(-3px); border-color: rgba(52, 211, 153, 0.4) !important; }
    .ml-check-list li { display: flex; gap: .6rem; margin-bottom: .6rem; font-size: .9rem; color: #cbd5e1; }
    .ml-check-list li i { color: var(--ml-green); flex-shrink: 0; margin-top: .1rem; }
    .ml-term {
      display: inline-flex; align-items: center; gap: .4rem;
      padding: .4rem .85rem; border-radius: 999px; font-size: .85rem; font-weight: 600;
      background: rgba(37,99,235,.14); border: 1px solid rgba(37,99,235,.38); color: #dbe5ff;
    }
    .ml-term i { color: var(--ml-green); }
    .ml-para-h { font-size: .92rem; letter-spacing: .03em; font-weight: 800; color: #fff; margin-bottom: 0; }

    /* Comparison. The wrapper is the containing block for the cells' visually
       hidden labels: they are absolutely positioned, and would otherwise escape
       its overflow and make the whole page scroll sideways on a phone. */
    .table-responsive { position: relative; }
    .peer-table { font-size: .9rem; border-collapse: separate; border-spacing: 0; }
    .peer-table th, .peer-table td { padding: .8rem .85rem; border-bottom: 1px solid rgba(255,255,255,.07); vertical-align: middle; }
    .peer-table td { text-align: center; min-width: 118px; font-size: 1.1rem; }
    .peer-table thead th { background: rgba(17, 24, 39, .95); color: #94a3b8; font-weight: 600; text-align: center; }
    .peer-table thead th:first-child { text-align: start; }
    .peer-table th.ml-col, .peer-table td.ml-col { background: rgba(52, 211, 153, .07); border-left: 1px solid rgba(52,211,153,.25); border-right: 1px solid rgba(52,211,153,.25); }
    .peer-table thead th.ml-col { color: var(--ml-green); border-top: 2px solid var(--ml-green); }
    .peer-table tbody th { min-width: 210px; font-weight: 600; }
    .peer-y { color: #34d399; }
    .peer-p { color: var(--ml-amber); }
    .peer-n { color: #f87171; }

    /* Pricing */
    .ml-plan { display: flex; flex-direction: column; border: 1px solid rgba(255,255,255,.1) !important; }
    .ml-plan-free { border: 2px solid var(--ml-green-solid) !important; box-shadow: 0 0 40px rgba(34, 197, 94, .14); }
    .ml-plan-pro { border: 1px solid rgba(251,191,36,.42) !important; }
    .ml-plan-price { font-size: 2.6rem; font-weight: 800; line-height: 1.1; color: var(--ml-green); overflow-wrap: anywhere; }
    .ml-plan-price-sm { font-size: 1.5rem; font-weight: 700; color: var(--ml-amber); line-height: 1.25; min-height: 2.86rem; display: flex; align-items: center; }
    .ml-plan-opt { background: rgba(255,255,255,.08); color: #cbd5e1; font-size: .72rem; font-weight: 600; }

    /* FAQ */
    .accordion-button:not(.collapsed) { background: rgba(52, 211, 153, 0.08); color: var(--ml-green); box-shadow: none; }
    .accordion-button:focus { box-shadow: 0 0 0 0.2rem rgba(52, 211, 153, 0.25); }
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


def schema(code, t, lst, title, desc, faqs):
    names = [APP + " Calculator"]
    if lst["title"] != names[0]:
        names.insert(0, lst["title"])
    graph = [
        {"@type": "Organization", "@id": SITE + "/#organization",
         "name": "Dhinovatech", "url": SITE + "/"},
        {"@type": "SoftwareApplication",
         "@id": SITE + "/mortgage-loan-emi-pro/#software",
         "name": APP,
         "alternateName": names,
         "operatingSystem": "Windows 10 version 1809 and later, Windows 11",
         "applicationCategory": "FinanceApplication",
         "applicationSubCategory": lst["kind"],
         "softwareVersion": "3.0",
         "description": desc,
         "abstract": lst["description"][0],
         "keywords": ", ".join(lst["terms"]),
         "url": abs_url(code),
         "inLanguage": [hl for _c, _l, _d, hl, _og in built_langs()],
         "image": SITE + ICON,
         "downloadUrl": STORE,
         "installUrl": STORE,
         "featureList": lst["features"],
         "isAccessibleForFree": True,
         "processorRequirements": "x86, x64 or ARM64",
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD",
                    "availability": "https://schema.org/InStock", "url": STORE},
         "screenshot": [SITE + shot_url(code, s) for s in [HERO] + SHOTS],
         "publisher": {"@id": SITE + "/#organization"},
         "author": {"@id": SITE + "/#organization"}},
        {"@type": "WebPage", "@id": abs_url(code) + "#webpage", "url": abs_url(code),
         "name": title, "description": desc, "inLanguage": BY_CODE[code][3],
         "dateModified": MODIFIED, "about": {"@id": SITE + "/mortgage-loan-emi-pro/#software"},
         "mainEntity": {"@id": SITE + "/mortgage-loan-emi-pro/#software"},
         "primaryImageOfPage": SITE + shot_url(code, HERO)},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": APP, "item": abs_url("en")},
        ]},
        {"@type": "FAQPage", "@id": abs_url(code) + "#faq",
         "inLanguage": BY_CODE[code][3],
         "mainEntity": [{"@type": "Question", "name": q,
                         "acceptedAnswer": {"@type": "Answer", "text": a}}
                        for q, a in faqs]},
    ]
    if code != "en":
        graph[3]["itemListElement"].append(
            {"@type": "ListItem", "position": 3, "name": lst["title"], "item": abs_url(code)})
    return json.dumps({"@context": "https://schema.org", "@graph": graph},
                      ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


# ---------------------------------------------------------------- sections

def eyebrow(icon, text):
    return ('<span class="badge bg-primary-subtle text-primary border border-primary-subtle '
            'rounded-pill px-3 py-2 fw-semibold mb-2"><i class="bi %s me-1" aria-hidden="true">'
            '</i> %s</span>' % (icon, E(text)))


def section_head(icon, eb, h, sub):
    return """      <div class="text-center mx-auto mb-5 ml-narrow">
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


def check_items(rows, indent="              "):
    return "\n".join(
        '%s<li><i class="bi bi-check2-circle" aria-hidden="true"></i><span>%s</span></li>'
        % (indent, E(r)) for r in rows)


def render_price(lst, centred=False):
    return ('<p class="ml-price mt-3 mb-0%s"><a class="ml-price-tag" href="#pricing">'
            '<i class="bi bi-unlock-fill me-1" aria-hidden="true"></i>%s</a>'
            '<span>%s</span></p>'
            % (" justify-content-center" if centred else "",
               E(lst["free"]), E(lst["free_sub"])))


def cta_strip(t, lst):
    """The store button again, where a reader who is convinced looks for it."""
    return """      <div class="ml-cta-strip d-flex flex-column flex-md-row align-items-center justify-content-center gap-3 mt-5">
        %s
        %s
      </div>
""" % (store_button(t), render_price(lst).replace(" mt-3", ""))


def zoom_img(src, alt, loading='loading="lazy"'):
    return ('<a class="ml-zoom" href="%s"><img src="%s" alt="%s" %s decoding="async" width="%d" height="%d"></a>'
            % (src, src, E(alt), loading, SHOT_W, SHOT_H))


def render_hero(code, t, lst):
    badges = "\n".join(
        '            <span class="badge bg-dark border border-secondary text-white-50 px-3 py-2 rounded-pill text-wrap">'
        '<i class="bi %s me-1" aria-hidden="true"></i> %s</span>' % (i, E(b))
        for i, b in zip(CHIP_ICONS, lst["chips"]))
    return """  <section class="hero-section position-relative overflow-hidden">
    <div class="container">
      <div class="row align-items-center gy-5">
        <div class="col-lg-6">
          <div class="d-flex align-items-center gap-3 mb-4">
            <span class="ml-hero-icon">
              <img src="%(icon)s" alt="" decoding="async" width="256" height="256">
            </span>
            <span>
              <span class="d-block ml-hero-kind">%(kind)s</span>
              <span class="d-block small text-secondary">
                <i class="bi bi-microsoft me-1" aria-hidden="true"></i>Microsoft Store &middot; Windows 10 &amp; 11
              </span>
            </span>
          </div>

          <h1 class="hero-title mb-3"><span class="d-block">%(name)s</span> <span class="d-block ml-hero-tagline">%(h1)s</span></h1>
          <p class="lead text-secondary mb-4 pe-lg-4 fs-5">%(lead)s</p>

          <div class="d-flex flex-wrap gap-3 align-items-center">
            %(store)s
            <a href="#calculator" class="btn btn-dhin-outline btn-lg rounded-pill px-4">
              <i class="bi bi-calculator me-2" aria-hidden="true"></i> %(cta_try)s
            </a>
          </div>
          %(price)s

          <div class="ml-badge-row pt-4 mt-2">
%(badges)s
          </div>
        </div>

        <div class="col-lg-6">
          <div class="position-relative">
            <div class="position-absolute top-50 start-50 translate-middle w-100 h-100 rounded-circle bg-primary opacity-25 blur-3xl glow-aura-blue" aria-hidden="true"></div>
            <div class="ml-window position-relative">
              %(hero)s
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
""" % dict(icon=ICON_WEBP, kind=E(lst["kind"]), name=E(lst["title"].replace(" Calculator", "")),
           h1=E("%s %s" % (lst["line1"], lst["line2"])), lead=E(lst["short"]),
           store=store_button(t), cta_try=E(t["cta_try"]), price=render_price(lst),
           badges=badges,
           hero=zoom_img(shot_url(code, HERO), lst["captions"][0], 'fetchpriority="high"'))


def field(key, label, value, lo, hi, step):
    return """            <div class="ml-field">
              <label for="ml-%(k)s">%(label)s</label>
              <input type="number" id="ml-%(k)s" data-calc="%(k)s" value="%(v)s" min="%(lo)s" max="%(hi)s" step="%(step)s" inputmode="decimal">
              <input type="range" data-calc-range="%(k)s" value="%(v)s" min="%(lo)s" max="%(hi)s" step="%(step)s" aria-label="%(label)s" tabindex="-1">
            </div>""" % dict(k=key, label=E(label), v=value, lo=lo, hi=hi, step=step)


def render_calc(code, t, lst):
    """A working calculator: what someone searching for one came to find.

    It opens on this language's demo loan, so "interest saved" matches slide 1
    in the hero. The first result is written here and recalculated by
    assets/js/mortgage-calc.js as the fields change.
    """
    d = lst["demo"]
    lab = lst["labels"]
    res = amortize(d)
    a_step = max(1, d["amount"] // 100)
    x_step = max(1, d["extra"] // 10)
    locale = INTL.get(code, d["region"])
    return """  <!-- Calculator -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="calculator">
    <div class="container py-4">
%(head)s
      <div class="card card-glass ml-calc%(long)s p-4 p-lg-5 shadow-lg mx-auto" style="max-width: 1040px;"
           data-mortgage-calc data-locale="%(locale)s" data-currency="%(cur)s" data-time="%(fmt)s" data-term="%(term)s">
        <div class="row g-4 g-lg-5">
          <div class="col-lg-6">
%(f1)s
%(f2)s
%(f3)s
%(f4)s
          </div>
          <div class="col-lg-6">
            <div class="row g-3" aria-live="polite">
              <div class="col-sm-6">
                <div class="ml-result h-100">
                  <div class="ml-result-label">%(l_pay)s</div>
                  <div class="ml-result-value" data-out="payment">%(v_pay)s</div>
                </div>
              </div>
              <div class="col-sm-6">
                <div class="ml-result h-100">
                  <div class="ml-result-label">%(l_int)s</div>
                  <div class="ml-result-value" data-out="interest">%(v_int)s</div>
                </div>
              </div>
              <div class="col-12">
                <div class="ml-result ml-saved">
                  <div class="row g-2">
                    <div class="col-sm-6">
                      <div class="ml-result-label">%(l_saved)s</div>
                      <div class="ml-result-value" data-out="saved">%(v_saved)s</div>
                    </div>
                    <div class="col-sm-6">
                      <div class="ml-result-label">%(l_time)s</div>
                      <div class="ml-result-value" data-out="time">%(v_time)s</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <p class="text-secondary small mt-4 mb-3">%(more)s</p>
            %(store)s
          </div>
        </div>
      </div>
      <p class="extra-small text-secondary text-center mt-3 mb-0 mx-auto ml-narrow">%(note)s</p>
    </div>
  </section>
""" % dict(head=section_head("bi-calculator", t["calc_eb"], t["calc_h"], t["calc_sub"]),
           long=" ml-calc-long" if d["amount"] >= 100000000 else "",
           locale=E(locale), cur=d["currency"], fmt=E(lab["time_fmt"]),
           term=E(json.dumps(lst["term"], ensure_ascii=False, separators=(",", ":")), quote=True),
           f1=field("amount", lab["amount"], d["amount"], a_step * 10, d["amount"] * 4, a_step),
           f2=field("rate", lab["rate"], d["rate"], 0.1, max(20, int(d["rate"] * 2)), 0.05),
           f3=field("years", lab["years"], d["years"], 1, 40, 1),
           f4=field("extra", lab["extra"], d["extra"], 0, d["extra"] * 10, x_step),
           l_pay=E(lab["payment"]), v_pay=E(money(code, res["emi"])),
           l_int=E(lab["interest"]), v_int=E(money(code, res["base"])),
           l_saved=E(lab["saved"]), v_saved=E(money(code, res["saved"])),
           l_time=E(lab["time"]), v_time=E(time_text(code, lst, res["months"])),
           more=E(t["calc_more"]), store=store_button(t), note=E(lst["description"][10]))


def render_glance(t, lst):
    """One definition sentence and the key facts, as a description list.

    Written to be quoted: search snippets and AI answers lift a page's own
    plain statement of what a thing is, what it costs and what it needs far
    more readily than they assemble one from marketing copy. The definition is
    the store description's opening, already keyword-tuned per market.
    """
    facts = "\n".join(
        '            <div class="ml-fact"><dt>%s</dt><dd>%s</dd></div>' % (E(k), E(v))
        for k, v in t["glance"])
    return """  <!-- At a glance -->
  <section class="py-5" id="at-a-glance">
    <div class="container py-3">
      <div class="row justify-content-center">
        <div class="col-lg-10">
          <h2 class="h3 text-white fw-bold mb-3"><i class="bi bi-info-circle text-primary me-2" aria-hidden="true"></i>%s</h2>
          <p class="ml-glance-def mb-4">%s</p>
          <dl class="ml-facts card card-glass border border-secondary-subtle overflow-hidden">
%s
          </dl>
        </div>
      </div>
    </div>
  </section>
""" % (E(t["glance_h"]), E(lst["description"][0]), facts)


def render_overview(lst):
    """Store slide 2 as real text: what is free, what is Pro."""
    ov = lst["overview"]
    tiles = []
    for key, name, what, pro in ov["tiles"]:
        tiles.append("""        <div class="col-lg-6">
          <div class="card card-glass h-100 p-3 p-md-4 pillar-card border border-secondary-subtle%s">
            <div class="d-flex align-items-center gap-3 mb-2">
              <span class="ml-icon-box ml-icon-box-sm"><i class="bi %s" aria-hidden="true"></i></span>
              <h3 class="h6 text-white fw-bold mb-0 flex-grow-1">%s</h3>
              <span class="ml-chip %s">%s</span>
            </div>
            <p class="text-secondary small mb-0">%s</p>
          </div>
        </div>""" % (" ml-tile-pro" if pro else "", TILE_ICONS.get(key, "bi-check2-circle"), E(name),
                     "ml-chip-pro" if pro else "ml-chip-free", "PRO" if pro else E(lst["chip_free"]), E(what)))
    return """  <!-- Overview -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="overview">
    <div class="container py-4">
%s
      <div class="row g-3 g-md-4 justify-content-center">
%s
      </div>
    </div>
  </section>
""" % (section_head("bi-stars", lst["free"], ov["title"], ov["sub"]), "\n".join(tiles))


def render_story(code, t, lst):
    """The three things that sell the app, each with its slide and full text."""
    rows = []
    for i, n in STORY:
        shot = lst["shots"][i]
        rows.append("""      <div class="row align-items-center g-4 g-lg-5 ml-row">
        <div class="col-lg-7 ml-row-img">
          <div class="ml-window">%s</div>
        </div>
        <div class="col-lg-5">
          <div class="ml-kicker"><i class="bi %s me-1" aria-hidden="true"></i>%s</div>
          <h3 class="ml-row-title">%s</h3>
          <p class="text-secondary mb-3">%s</p>
          <ul class="list-unstyled ml-check-list mb-0">
%s
          </ul>
        </div>
      </div>""" % (zoom_img(shot_url(code, SHOTS[i]), lst["captions"][i + 2]), SHOT_ICONS[i],
                   E(shot["kicker"]), E(shot["title"]), E(para(lst, n)),
                   check_items(shot["points"], "            ")))
    return """  <!-- What it shows -->
  <section class="py-5" id="features">
    <div class="container py-4">
%s
      <div>
%s
      </div>
    </div>
  </section>
""" % (section_head("bi-eye", t["story_eb"], t["story_h"], ""), "\n".join(rows))


def render_gallery(code, t, lst):
    cards = []
    for i in GALLERY:
        shot = lst["shots"][i]
        cards.append("""        <div class="col-md-6">
          <figure class="card card-glass ml-shot h-100%s">
            %s
            <figcaption>
              <div class="ml-kicker"><i class="bi %s me-1" aria-hidden="true"></i>%s</div>
              <h3 class="ml-shot-title">%s</h3>
              <ul class="list-unstyled ml-check-list mb-0">
%s
              </ul>
            </figcaption>
          </figure>
        </div>""" % (" ml-shot-pro" if shot["pro"] else "",
                     zoom_img(shot_url(code, SHOTS[i]), lst["captions"][i + 2]), SHOT_ICONS[i],
                     E(shot["kicker"]), E(shot["title"]),
                     check_items(shot["points"], "                ")))
    return """  <!-- Screenshots -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="screenshots">
    <div class="container py-4">
%s
      <div class="row g-4 justify-content-center">
%s
      </div>
%s    </div>
  </section>
""" % (section_head("bi-images", t["shots"], t["shots_h"], ""), "\n".join(cards), cta_strip(t, lst))


def render_tools(t, lst):
    """The twelve decision tools, in the app's own words and order."""
    shot = lst["shots"][5]
    cards = []
    for icon, (name, what) in zip(TOOL_ICONS, lst["tools"]):
        cards.append("""        <div class="col-xl-3 col-lg-4 col-md-6">
          <div class="card card-glass h-100 p-4 pillar-card border border-secondary-subtle">
            <span class="ml-icon-box ml-icon-box-sm mb-3"><i class="bi %s" aria-hidden="true"></i></span>
            <h3 class="h6 text-white fw-bold mb-2">%s</h3>
            <p class="text-secondary small mb-0">%s</p>
          </div>
        </div>""" % (icon, E(name), E(what)))
    terms = "\n".join('          <span class="ml-term"><i class="bi bi-search" aria-hidden="true"></i>%s</span>' % E(x)
                      for x in lst["terms"])
    return """  <!-- Decision tools -->
  <section class="py-5" id="decision-tools">
    <div class="container py-4">
%s
      <div class="row g-4">
%s
      </div>
      <h3 class="h5 text-white fw-bold text-center mt-5 mb-3">%s</h3>
      <div class="d-flex flex-wrap justify-content-center gap-2 mx-auto" style="max-width: 900px;">
%s
      </div>
    </div>
  </section>
""" % (section_head("bi-signpost-split", shot["kicker"], shot["title"], lst["overview"]["tiles"][5][2]),
       "\n".join(cards), E(t["terms_h"]), terms)


def render_compare(t, lst):
    head = "\n".join([
        '                <th scope="col">%s</th>' % E(t["cmp_feature"]),
        '                <th scope="col" class="ml-col">%s</th>' % E(APP),
        '                <th scope="col">%s</th>' % E(t["cmp_web"]),
        '                <th scope="col">%s</th>' % E(t["cmp_sheet"]),
    ])
    word = {"y": t["cmp_legend"][0], "p": t["cmp_legend"][1], "n": t["cmp_legend"][2]}
    rows = []
    for marks, label in zip(CMP_MARKS, t["cmp_rows"]):
        cells = ['                  <th scope="row" class="text-white">%s</th>' % E(label)]
        for i, m in enumerate(marks):
            cells.append('                  <td%s><i class="bi %s" aria-hidden="true"></i><span class="visually-hidden">%s</span></td>'
                         % (' class="ml-col"' if i == 0 else "", MARK_ICON[m], E(word[m])))
        rows.append("                <tr>\n%s\n                </tr>" % "\n".join(cells))
    legend = " ".join(
        '<span class="me-3"><i class="bi %s me-1" aria-hidden="true"></i>%s</span>' % (MARK_ICON[k], E(word[k]))
        for k in "ypn")
    return """  <!-- Comparison -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="compare">
    <div class="container py-4">
%s
      <div class="card card-glass p-2 p-md-3 border border-secondary-subtle shadow-lg mx-auto" style="max-width: 1040px;">
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
      <p class="small text-secondary text-center mt-3 mb-1">%s</p>
      <p class="extra-small text-secondary text-center mb-0">%s</p>
    </div>
  </section>
""" % (section_head("bi-layout-three-columns", t["cmp_eb"], t["cmp_h"], t["cmp_sub"]), head,
       "\n".join(rows), legend, E(t["cmp_note"]))


def render_who(t):
    cards = []
    for icon, c in zip(WHO_ICONS, t["who_cards"]):
        cards.append("""        <div class="col-lg-3 col-md-6">
          <div class="card card-glass h-100 p-4 pillar-card border border-secondary-subtle">
            <span class="ml-icon-box mb-3"><i class="bi %s" aria-hidden="true"></i></span>
            <h3 class="h6 text-white fw-bold mb-2">%s</h3>
            <p class="text-secondary small mb-0">%s</p>
          </div>
        </div>""" % (icon, E(c["t"]), E(c["d"])))
    return """  <!-- Who it is for -->
  <section class="py-5" id="who-it-is-for">
    <div class="container py-4">
%s
      <div class="row g-4">
%s
      </div>
    </div>
  </section>
""" % (section_head("bi-people", t["who_eb"], t["who_h"], ""), "\n".join(cards))


def render_steps(t, lst):
    steps = []
    for n, s in enumerate(t["steps"], 1):
        steps.append("""        <div class="col-md-4">
          <div class="card card-glass h-100 p-4">
            <div class="d-flex align-items-center gap-3 mb-2">
              <div class="ml-step">%d</div>
              <h3 class="h6 text-white fw-bold mb-0">%s</h3>
            </div>
            <p class="text-secondary small mb-0">%s</p>
          </div>
        </div>""" % (n, E(s["t"]), E(s["d"])))
    return """  <!-- How it works -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="how-it-works">
    <div class="container py-4">
%s
      <div class="row g-4">
%s
      </div>
%s    </div>
  </section>
""" % (section_head("bi-signpost-2", t["steps_eb"], t["steps_h"], ""), "\n".join(steps), cta_strip(t, lst))


def render_pricing(t, lst):
    """Everything you can calculate is free; Pro is for following a real loan.

    The two lists are the store description's own, so the page and the listing
    cannot disagree. No price: it varies by market, and the Store and the app
    show the live one.
    """
    return """  <!-- Pricing -->
  <section class="py-5" id="pricing">
    <div class="container py-4">
%s
      <div class="row justify-content-center g-4">
        <div class="col-md-6 col-lg-5">
          <div class="card card-glass h-100 p-4 p-lg-5 ml-plan ml-plan-free">
            <h3 class="h5 text-white fw-bold mb-1">%s</h3>
            <p class="ml-plan-price mb-3">%s</p>
            <p class="text-secondary small mb-3">%s</p>
            <ul class="list-unstyled ml-check-list mb-4">
%s
            </ul>
            <div class="mt-auto">%s</div>
          </div>
        </div>
        <div class="col-md-6 col-lg-5">
          <div class="card card-glass h-100 p-4 p-lg-5 ml-plan ml-plan-pro">
            <h3 class="h5 text-white fw-bold mb-1">%s <span class="badge rounded-pill ml-plan-opt align-middle ms-1">%s</span></h3>
            <p class="ml-plan-price-sm mb-3">%s</p>
            <p class="text-secondary small mb-3">%s</p>
            <ul class="list-unstyled ml-check-list mb-0">
%s
            </ul>
          </div>
        </div>
      </div>
      <p class="text-secondary small text-center mx-auto mt-4 mb-0 ml-narrow">%s</p>
    </div>
  </section>
""" % (section_head("bi-unlock-fill", t["price_eb"], t["price_h"], t["price_sub"]),
       E(t["free_title"]), E(t["free_price"]), E(intro(lst, 1)), check_items(bullets(lst, 1)),
       store_button(t), E(t["pro_title"]), E(t["pro_badge"]), E(t["pro_price"]), E(intro(lst, 7)),
       check_items(bullets(lst, 7)), E(t["price_fine"]))


def render_trust(code, t, lst):
    cards = []
    for icon, n in zip(TRUST_ICONS, (5, 8, 9)):
        link = ""
        if n == 8:
            link = ('<a class="small d-block mt-3" href="%s"><i class="bi bi-shield-check me-1" aria-hidden="true"></i>%s</a>'
                    % (PRIVACY, E(privacy_label(code))))
        cards.append("""        <div class="col-lg-4">
          <div class="card card-glass h-100 p-4 invariant-card">
            <div class="d-flex align-items-center gap-3 mb-3">
              <span class="ml-icon-box ml-icon-box-sm"><i class="bi %s" aria-hidden="true"></i></span>
              <h3 class="ml-para-h">%s</h3>
            </div>
            <p class="text-secondary small mb-0">%s</p>
            %s
          </div>
        </div>""" % (icon, E(heading(lst, n)), E(para(lst, n)), link))
    return """  <!-- Banks, privacy, countries -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="privacy">
    <div class="container py-4">
%s
      <div class="row g-4">
%s
      </div>
    </div>
  </section>
""" % (section_head("bi-shield-check", t["trust_eb"], t["trust_h"], ""), "\n".join(cards))


def render_features(t, lst):
    feats = lst["features"]
    half = (len(feats) + 1) // 2
    cols = []
    for chunk in (feats[:half], feats[half:]):
        cols.append("""          <div class="col-md-6">
            <ul class="list-unstyled ml-check-list mb-0">
%s
            </ul>
          </div>""" % check_items(chunk))
    return """  <!-- Every feature -->
  <section class="py-5" id="all-features">
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


def render_faq(t, faqs):
    items = []
    for i, (q, a) in enumerate(faqs, 1):
        first = i == 1
        items.append("""            <div class="accordion-item bg-transparent border-bottom border-secondary">
              <h3 class="accordion-header" id="faq%dHeading">
                <button class="accordion-button%s bg-transparent text-white fw-semibold py-4" type="button" data-bs-toggle="collapse" data-bs-target="#faq%d" aria-expanded="%s" aria-controls="faq%d">
                  %s
                </button>
              </h3>
              <div id="faq%d" class="accordion-collapse collapse%s" aria-labelledby="faq%dHeading" data-bs-parent="#mortgageFaqAccordion">
                <div class="accordion-body text-secondary small pb-4">
                  %s
                </div>
              </div>
            </div>""" % (i, "" if first else " collapsed", i, "true" if first else "false", i,
                         E(q), i, " show" if first else "", i, E(a)))
    return """  <!-- FAQ -->
  <section class="py-5 bg-dark border-top border-bottom border-secondary-subtle" id="faq">
    <div class="container py-4">
%s
      <div class="row justify-content-center">
        <div class="col-lg-9">
          <div class="accordion accordion-flush" id="mortgageFaqAccordion">
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
      <div class="card card-glass p-5 text-center border-0 position-relative overflow-hidden" style="background: linear-gradient(135deg, rgba(19,80,158,0.32) 0%%, rgba(34,197,94,0.1) 100%%);">
        <div class="ml-narrow mx-auto position-relative" style="z-index: 2;">
          <div class="mx-auto mb-3" style="width: 90px; height: 90px;">
            <img src="%s" alt="%s" class="w-100 h-100 object-fit-contain rounded-4" loading="lazy" decoding="async" width="256" height="256">
          </div>
          <h2 class="display-6 fw-bold text-white mb-3">%s</h2>
          <p class="text-secondary fs-5 mb-4">%s</p>
          <div class="d-flex justify-content-center">
            %s
          </div>
          %s
          <p class="extra-small text-secondary mt-4 mb-0">%s</p>
        </div>
      </div>
    </div>
  </section>
""" % (ICON_WEBP, E(APP + " icon"), E("%s %s" % (lst["line1"], lst["line2"])), E(lst["short"]),
       store_button(t), render_price(lst, True), E(lst["description"][10]))


def build(code):
    t = dict(S["en"])
    t.update(S.get(code, {}))
    lst = LISTING[code]
    _c, _label, direction, hl, og = BY_CODE[code]
    title = t["seo_title"]
    desc = lst["short"]
    nums = figures(code, lst)
    faqs = [(f["q"], f["a"].format(**nums)) for f in t["faqs"]]

    og_alts = "\n".join('  <meta property="og:locale:alternate" content="%s">' % o
                        for c2, _l, _d, _h, o in built_langs() if c2 != code)

    body = "\n".join([
        render_hero(code, t, lst),
        # Someone who searched for a calculator gets one first. Then what the
        # thing is and costs, stated plainly; what it does and looks like; why
        # choose it, and what Pro adds; then every remaining question.
        render_calc(code, t, lst),
        render_glance(t, lst),
        render_overview(lst),
        render_story(code, t, lst),
        render_gallery(code, t, lst),
        render_tools(t, lst),
        render_compare(t, lst),
        render_pricing(t, lst),
        render_trust(code, t, lst),
        render_who(t),
        render_steps(t, lst),
        render_features(t, lst),
        render_faq(t, faqs),
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
<!-- Navigation Bar (independent Mortgage Loan EMI Pro tree) -->
{navbar}
<main id="main">

{body}
</main>
{footer}
  <!-- Bootstrap 5.3 JS Bundle -->
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
  <script src="/assets/js/nav.js"></script>
  <script src="/assets/js/mortgage-calc.js"></script>

  <!-- BEGIN generated UX block -->
  <div class="install-bar" role="complementary" aria-label="{app}">
    <img src="{icon}" alt="" width="42" height="42" loading="lazy" decoding="async">
    <div class="install-bar-text">
      <div class="install-bar-title">{app}</div>
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
        schema=schema(code, t, lst, title, desc, faqs), hero_shot=shot_url(code, HERO),
        navbar=navbar(code, t), body=body, footer=FOOTER, icon=ICON_WEBP, app=E(APP),
        store=E(STORE_UTM), consent_banner=consent_banner_html(code))


def check(code, t, lst):
    """Fail loudly when the listing or strings no longer have the shape used above."""
    problems = []
    if len(lst["description"]) != 11:
        problems.append("description has %d paragraphs, expected 11" % len(lst["description"]))
    else:
        problems += ["description paragraph %d has no heading line" % n
                     for n in (1, 2, 3, 5, 6, 7, 8, 9) if "\n" not in lst["description"][n]]
        for n in (1, 7):
            if not bullets(lst, n) or not intro(lst, n):
                problems.append("description paragraph %d lost its intro or bullets" % n)
    for key, n in (("cmp_rows", len(CMP_MARKS)), ("steps", 3), ("who_cards", len(WHO_ICONS)),
                   ("cmp_legend", 3), ("glance", 9), ("faqs", 13)):
        if len(t[key]) != n:
            problems.append("%s has %d items, expected %d" % (key, len(t[key]), n))
    if len(lst["shots"]) != len(SHOTS) or len(lst["captions"]) != 10:
        problems.append("listing shots/captions do not match the eight gallery slides")
    if len(lst["tools"]) != len(TOOL_ICONS) or len(lst["overview"]["tiles"]) != 10:
        problems.append("listing tools/tiles changed shape")
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
        missing = [k for k in S["en"] if k not in S.get(code, {})]
        print("wrote %s%s" % (os.path.relpath(path, ROOT),
                              "  (English fallback: %d keys)" % len(missing) if code != "en" and missing else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
