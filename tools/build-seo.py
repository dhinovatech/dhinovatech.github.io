#!/usr/bin/env python3
"""
Dhinovatech site SEO builder.

Regenerates, for every page on the site:
  * <link rel="canonical">                     - one true URL per page
  * <link rel="alternate" hreflang=...>         - full reciprocal translation cluster
  * Open Graph + Twitter Card meta              - social/link-preview cards
  * JSON-LD structured data                     - Organization / WebSite /
                                                  SoftwareApplication / BreadcrumbList
  * resource hints, theme-color, manifest link
  * loading="lazy" on below-the-fold images
and writes sitemap.xml, robots.txt and site.webmanifest.

Run it after adding a page, an app, or a language:

    python tools/build-seo.py

It is idempotent - generated blocks are delimited by comment markers and are
replaced on each run, so running it twice changes nothing.

Adding a new app: add an entry to APPS below (the key is the directory name).
Adding a new language: just create <app>/<code>/index.html and re-run; the
hreflang cluster, sitemap and schema pick it up automatically.
"""
import os, re, sys, json, html, datetime
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://www.dhinovatech.com"
ORG  = SITE + "/#organization"

# Pages that must never be indexed, canonicalised or listed in the sitemap.
EXCLUDE = {"404.html"}

# Trees that build their own <head>. build-glowcompare-windows.py writes the
# canonical, the hreflang cluster and the offers schema for every page under
# /glowcompare-windows/, so injecting a second SEO block here would emit a
# duplicate, contradicting canonical. They are skipped from head processing
# only - write_sitemap() reads each page's own canonical, so they stay in
# sitemap.xml exactly as before.
SELF_MANAGED = ("glowcompare-windows",)

# Intrinsic dimensions of everything under assets/images, written by
# build-images.py. og:image:width/height have to match the file actually
# served or the card renders letterboxed, and hard-coding them here means they
# silently rot the next time an image is re-encoded.
with open(os.path.join(ROOT, "tools", "image-sizes.json"), encoding="utf-8") as _fh:
    IMG_SIZES = json.load(_fh)

def img_dims(path, fallback):
    return tuple(IMG_SIZES.get(os.path.basename(path), fallback))

SEO_BEGIN = "  <!-- BEGIN generated SEO block (canonical/hreflang/social/schema) -->"
SEO_END   = "  <!-- END generated SEO block -->"
HINT_BEGIN = "  <!-- BEGIN generated resource hints -->"
HINT_END   = "  <!-- END generated resource hints -->"

APPS = {
 'glowcompare': dict(
    name="GlowCompare", os="Android", cat="HealthApplication",
    store="https://play.google.com/store/apps/details?id=com.dhinova.glowcompare",
    icon="/assets/images/glowcompare-icon.png",
    og="/assets/images/glowcompare-slider-after.jpg", ogw=1200, ogh=896,
    ogalt="GlowCompare split-slider skincare progress comparison", large=True),
 'milk-monthly-expense-calendar': dict(
    name="Milk Monthly Expense Calendar", os="Android", cat="FinanceApplication",
    store="https://play.google.com/store/apps/details?id=com.dhinova.milkmonthlyexpensecalendar",
    icon="/assets/images/milk-calendar-icon.png",
    og="/assets/images/milk-monthly-calendar-ui-preview.jpg", ogw=1376, ogh=768,
    ogalt="Milk Monthly Expense Calendar monthly tracking interface", large=True),
 'notelock': dict(
    name="Notelock", os="Windows", cat="SecurityApplication",
    store="https://apps.microsoft.com/detail/9NRQLDJ9ZFCM",
    icon="/assets/images/notelock-icon.png",
    og="/assets/images/notelock-icon.png", ogw=300, ogh=300,
    ogalt="Notelock secure encrypted notepad icon", large=False),
 'slouch-guard': dict(
    name="Slouch Guard", os="Windows", cat="HealthApplication",
    store="https://apps.microsoft.com/detail/9NJH1LC3PQ8N",
    icon="/assets/images/slouch-guard-icon.png",
    og="/assets/images/slouch-guard-ui-preview.jpg", ogw=1376, ogh=768,
    ogalt="Slouch Guard real-time posture monitoring interface", large=True),
 'mortgage-loan-emi-pro': dict(
    name="Mortgage Loan EMI Pro Insights", os="Windows", cat="FinanceApplication",
    store="https://apps.microsoft.com/detail/9PFS2J56BJXR",
    icon="/assets/images/mortgage-emi-icon.png",
    og="/assets/images/mortgage-emi-icon.png", ogw=300, ogh=300,
    ogalt="Mortgage Loan EMI Pro Insights icon", large=False),
 'aes-vault': dict(
    name="AES Vault", os="Windows", cat="SecurityApplication",
    store="https://apps.microsoft.com/detail/9N8XWF00VRNJ",
    icon="/assets/images/aes-vault-icon.png",
    og="/assets/images/aes-vault-icon.png", ogw=300, ogh=300,
    ogalt="AES Vault file and folder encryption icon", large=False),
}

# Store screenshots, for SoftwareApplication.screenshot. Only listed where the
# images genuinely exist - an app with no screenshots gets no screenshot field
# rather than a placeholder.
SHOTS = {
 'glowcompare': ["/assets/images/glowcompare-screenshot-%d.webp" % i
                 for i in range(1, 7)],
}

# Directory code -> BCP-47 hreflang value (only where they differ).
#
# Google resolves hreflang against ISO 639-1 and ignores any value it cannot
# parse, so the ISO 639-3 codes this site uses as directory names would be
# dropped from the cluster entirely. Where a language has a faithful
# region-qualified equivalent it is mapped to one; that is valid BCP-47 and
# does not collide with the plain code (ar-EG alongside ar is a normal pair).
#
# wuu (Wu) and bho (Bhojpuri) are deliberately left unmapped: the only
# candidates would be zh-Hans and hi, which already belong to other pages in
# the same cluster, and emitting a duplicate hreflang is worse than emitting
# one Google skips. Those pages still index normally through their canonical.
HREF = {'zh': 'zh-Hans',
        'arz': 'ar-EG',   # Egyptian Arabic
        'pnb': 'pa-PK',   # Western Punjabi (Shahmukhi)
        'yue': 'zh-HK',   # Cantonese
        'nan': 'zh-TW',   # Min Nan / Taiwanese
        'pcm': 'en-NG'}   # Nigerian Pidgin
# BCP-47 -> og:locale. Only confident mappings; og:locale is optional, so a
# missing entry simply omits the tag rather than emitting something wrong.
OGLOC = {'en':'en_US','es':'es_ES','fr':'fr_FR','de':'de_DE','it':'it_IT','nl':'nl_NL',
 'pl':'pl_PL','pt':'pt_BR','ru':'ru_RU','ja':'ja_JP','ko':'ko_KR','zh-Hans':'zh_CN',
 'tr':'tr_TR','vi':'vi_VN','id':'id_ID','hi':'hi_IN','ar':'ar_AR','ur':'ur_PK',
 'fa':'fa_IR','bn':'bn_IN','mr':'mr_IN','te':'te_IN','ta':'ta_IN','uk':'uk_UA',
 'sw':'sw_KE','th':'th_TH','ml':'ml_IN','kn':'kn_IN','gu':'gu_IN','pa':'pa_IN',
 'or':'or_IN','tl':'tl_PH','ha':'ha_NG','yo':'yo_NG','am':'am_ET','ps':'ps_AF',
 'jv':'jv_ID','ar-EG':'ar_EG','pa-PK':'pa_PK','zh-HK':'zh_HK','zh-TW':'zh_TW',
 'en-NG':'en_NG'}

def hl(code):
    return HREF.get(code, code)

def relpath(p):
    return os.path.relpath(p, ROOT).replace('\\', '/')

def url_of(p):
    r = relpath(p)
    if r == 'index.html':
        return '/'
    if r.endswith('/index.html'):
        return '/' + r[:-len('index.html')]
    return '/' + r

def esc(s):
    return html.escape(s, quote=True)

# The FAQ accordions are hand-written per page and per language. Rather than
# keep a parallel copy of the copy in this script - which would drift the first
# time someone edits a page - the questions and answers are read back out of
# the rendered markup, so the schema can never disagree with what a reader
# sees. Bootstrap's accordion markup is uniform across the site.
FAQ_ITEM = re.compile(
    r'<button[^>]*class="[^"]*accordion-button[^"]*"[^>]*>(?P<q>.*?)</button>'
    r'.*?<div[^>]*class="[^"]*accordion-body[^"]*"[^>]*>(?P<a>.*?)</div>',
    re.S | re.I)

def _plain(fragment):
    t = re.sub(r'<[^>]+>', ' ', fragment)
    return re.sub(r'\s+', ' ', html.unescape(t)).strip()

def faq_entities(src):
    out = []
    for m in FAQ_ITEM.finditer(src):
        q, a = _plain(m.group('q')), _plain(m.group('a'))
        # Drop the "Q1:" / "Q2:" prefixes the visible copy uses; they are
        # numbering, not part of the question.
        q = re.sub(r'^Q\s*\d+\s*[:.\u2013-]\s*', '', q)
        if len(q) > 3 and len(a) > 10:
            out.append({"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a}})
    return out

# ---------------------------------------------------------------- discovery
def discover():
    pages = []
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [x for x in dn if x not in ('.git', 'tools')]
        for f in fn:
            if f.endswith('.html') and f not in EXCLUDE:
                pages.append(os.path.join(dp, f))
    return sorted(pages)

# Fraction of a page's visible copy that may be byte-identical to the English
# page before we stop calling it a translation. Tuned against the real site:
# the 24 unfinished GlowCompare locales sit at 87-95%, the partly-done ones at
# 58-59%, and genuine translations at 4-16%. 0.70 splits "not translated yet"
# from "translated, with some English left in it" without catching either of
# the latter two groups.
UNTRANSLATED_AT = 0.70

# Copy long enough to be a sentence rather than a product name, a number or a
# UI label. Brand names and store buttons are identical in every language and
# would drag the score up for pages that are perfectly well translated.
SEG_RE = re.compile(r'>([^<>]{25,})<')
GEN_RE = re.compile(r'<!-- BEGIN generated .*?<!-- END generated [a-z ]*-->', re.S)
TAG_RE = re.compile(r'<(script|style)\b.*?</\1>', re.S)


def segments(src):
    """The set of visible text runs in <main>, normalised for whitespace."""
    i, j = src.find('<main'), src.find('</main>')
    body = src[i:j] if i >= 0 else src
    # Generated regions are translated by their own builders and would skew the
    # comparison on pages whose hand-written copy is still English.
    body = TAG_RE.sub('', GEN_RE.sub('', body))
    return set(' '.join(m.group(1).split())
               for m in SEG_RE.finditer(body) if m.group(1).strip())


def untranslated(pages):
    """
    Locale pages whose copy is still overwhelmingly the English original.

    Serving those under hreflang="de" and friends is what Google reads as
    duplicate content, and it can suppress the whole cluster - including the
    English page that is doing nothing wrong. Rather than guess from character
    sets (which would misjudge every Latin-script language), each page is
    compared against its own app's English page: identical sentences are
    untranslated sentences, whatever the alphabet.

    These pages stay published and usable. They are only kept out of the
    index, out of the hreflang cluster and out of the sitemap until the copy
    catches up.
    """
    ref, out = {}, set()
    for p in pages:
        parts = relpath(p).split('/')
        if len(parts) == 2 and parts[0] in APPS and parts[1] == 'index.html':
            ref[parts[0]] = segments(open(p, encoding='utf-8').read())
    for p in pages:
        parts = relpath(p).split('/')
        if len(parts) != 3 or parts[0] not in APPS or parts[2] != 'index.html':
            continue
        en = ref.get(parts[0])
        if not en:
            continue
        seg = segments(open(p, encoding='utf-8').read())
        if seg and len(seg & en) / len(seg) > UNTRANSLATED_AT:
            out.add(relpath(p))
    return out


def locale_map(pages):
    loc = {a: [] for a in APPS}
    for p in pages:
        parts = relpath(p).split('/')
        if len(parts) == 3 and parts[0] in APPS and parts[2] == 'index.html':
            loc[parts[0]].append(parts[1])
    for a in loc:
        loc[a].sort()
    return loc

# ------------------------------------------------------------- SEO block
def seo_block(p, locales, skip=frozenset()):
    parts = relpath(p).split('/')
    app = parts[0] if parts[0] in APPS else None
    loc = parts[1] if (app and len(parts) == 3) else ('en' if app else None)
    is_app_page = app is not None and parts[-1] == 'index.html'

    src = open(p, encoding='utf-8').read()
    title = re.search(r'<title>(.*?)</title>', src, re.S).group(1).strip()
    desc = re.search(r'<meta\s+name="description"\s+content="(.*?)"', src, re.S | re.I).group(1).strip()
    lang = re.search(r'<html[^>]*\slang="([^"]+)"', src, re.I).group(1)
    url = SITE + url_of(p)

    me_untranslated = relpath(p) in skip

    L = [SEO_BEGIN, f'  <link rel="canonical" href="{url}">']
    if me_untranslated:
        # follow, not none: the page still passes link equity to the app pages
        # it points at, it just should not rank as a translation it is not.
        L.append('  <meta name="robots" content="noindex,follow">')
    else:
        L.append('  <meta name="robots" content="index,follow,'
                 'max-image-preview:large,max-snippet:-1,max-video-preview:-1">')

    # An untranslated page advertises no alternates, and no other page
    # advertises it: a cluster is a mutual claim, and half of this one is not
    # true yet.
    if is_app_page and not me_untranslated:
        base = f'{SITE}/{app}/'
        L.append(f'  <link rel="alternate" hreflang="x-default" href="{base}">')
        L.append(f'  <link rel="alternate" hreflang="en" href="{base}">')
        for c in locales[app]:
            if f'{app}/{c}/index.html' in skip:
                continue
            L.append(f'  <link rel="alternate" hreflang="{hl(c)}" href="{base}{c}/">')

    a = APPS.get(app)
    if a:
        ogimg, ogalt, large = a['og'], a['ogalt'], a['large']
        ogw, ogh = img_dims(ogimg, (a['ogw'], a['ogh']))
    else:
        ogimg, large = "/assets/images/dhinovatech-hero.jpg", True
        ogw, ogh = img_dims(ogimg, (1376, 768))
        ogalt = "Dhinovatech privacy-first apps for Android and Windows"

    L += ['  <meta property="og:type" content="website">',
          '  <meta property="og:site_name" content="Dhinovatech">',
          f'  <meta property="og:title" content="{esc(title)}">',
          f'  <meta property="og:description" content="{esc(desc)}">',
          f'  <meta property="og:url" content="{url}">',
          f'  <meta property="og:image" content="{SITE}{ogimg}">',
          f'  <meta property="og:image:width" content="{ogw}">',
          f'  <meta property="og:image:height" content="{ogh}">',
          f'  <meta property="og:image:alt" content="{esc(ogalt)}">']

    ogl = OGLOC.get(hl(loc) if loc else 'en')
    if ogl:
        L.append(f'  <meta property="og:locale" content="{ogl}">')
    if is_app_page:
        for c in ['en'] + locales[app]:
            o = OGLOC.get(hl(c))
            if o and o != ogl:
                L.append(f'  <meta property="og:locale:alternate" content="{o}">')

    L += [f'  <meta name="twitter:card" content="{"summary_large_image" if large else "summary"}">',
          f'  <meta name="twitter:title" content="{esc(title)}">',
          f'  <meta name="twitter:description" content="{esc(desc)}">',
          f'  <meta name="twitter:image" content="{SITE}{ogimg}">',
          f'  <meta name="twitter:image:alt" content="{esc(ogalt)}">']

    # ---- structured data -------------------------------------------------
    # `offers` states the one price fact that is verifiable from the store
    # listings themselves: every app is a free download (in-app credits, where
    # they exist, are priced in-app and are not the download price). This is
    # the same Offer the Microsoft Store build already publishes.
    #
    # NOTE: still no `aggregateRating`. A rating has to be a real, current
    # store figure; inventing one breaks Google's structured-data policy and
    # risks a manual action. Add it here only with genuine numbers, and only
    # with something that keeps them up to date.
    graph = []
    if url_of(p) == '/':
        graph.append({"@type": "Organization", "@id": ORG, "name": "Dhinovatech",
            "url": SITE + "/", "email": "dhinovatech@gmail.com",
            "logo": {"@type": "ImageObject",
                     "url": SITE + "/assets/images/LogoWithText.png",
                     "width": img_dims("LogoWithText.png", (1096, 176))[0],
                     "height": img_dims("LogoWithText.png", (1096, 176))[1]},
            "description": "Dhinovatech builds privacy-first, offline-capable "
                           "applications for Android and Windows."})
        graph.append({"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/",
                      "name": "Dhinovatech", "publisher": {"@id": ORG}, "inLanguage": "en"})
        graph.append({"@type": "ItemList", "name": "Dhinovatech Applications",
            "itemListElement": [{"@type": "ListItem", "position": i + 1,
                                 "name": v['name'], "url": f"{SITE}/{k}/"}
                                for i, (k, v) in enumerate(APPS.items())]})
    else:
        graph.append({"@type": "Organization", "@id": ORG,
                      "name": "Dhinovatech", "url": SITE + "/"})

    if is_app_page:
        soft = {"@type": "SoftwareApplication", "@id": f"{SITE}/{app}/#software",
            "name": a['name'], "operatingSystem": a['os'],
            "applicationCategory": a['cat'], "description": desc,
            "url": f"{SITE}/{app}/",
            "inLanguage": [hl(c) for c in ['en'] + locales[app]
                           if f'{app}/{c}/index.html' not in skip],
            "image": SITE + a['icon'], "downloadUrl": a['store'],
            "installUrl": a['store'],
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD",
                       "availability": "https://schema.org/InStock",
                       "url": a['store']},
            "publisher": {"@id": ORG}, "author": {"@id": ORG}}
        if app in SHOTS:
            soft["screenshot"] = [SITE + u for u in SHOTS[app]]
        graph.append(soft)
        faq = faq_entities(src)
        if faq:
            graph.append({"@type": "FAQPage", "@id": url + "#faq",
                          "inLanguage": hl(loc), "mainEntity": faq})
        crumbs = [{"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
                  {"@type": "ListItem", "position": 2, "name": a['name'],
                   "item": f"{SITE}/{app}/"}]
        if loc != 'en':
            crumbs.append({"@type": "ListItem", "position": 3,
                           "name": f"{a['name']} ({lang})", "item": url})
        graph.append({"@type": "BreadcrumbList", "itemListElement": crumbs})
    elif url_of(p) != '/':
        nm = title.split('|')[0].split('—')[0].strip()
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": nm, "item": url}]})

    L.append('  <script type="application/ld+json">')
    L.append(json.dumps({"@context": "https://schema.org", "@graph": graph},
                        ensure_ascii=False, separators=(',', ':')))
    L.append('  </script>')
    L.append(SEO_END)
    return '\n'.join(L)

HINTS = "\n".join([
  HINT_BEGIN,
  '  <link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>',
  '  <link rel="dns-prefetch" href="https://cdn.jsdelivr.net">',
  # Inter used to be pulled in by an @import at the top of custom.css, which
  # meant the browser could not even discover the font stylesheet until
  # custom.css had downloaded and parsed - a render-blocking request behind a
  # render-blocking request. Linking it here with a preconnect makes it a
  # first-wave fetch instead.
  '  <link rel="preconnect" href="https://fonts.googleapis.com">',
  '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
  '  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
  'family=Inter:wght@300;400;500;600;700;800&display=swap">',
  '  <link rel="preconnect" href="https://www.googletagmanager.com">',
  '  <link rel="dns-prefetch" href="https://www.googletagmanager.com">',
  '  <link rel="manifest" href="/site.webmanifest">',
  '  <meta name="theme-color" content="#080c14">',
  '  <meta name="color-scheme" content="dark light">',
  HINT_END,
])

SEO_RE  = re.compile(re.escape(SEO_BEGIN) + r'.*?' + re.escape(SEO_END) + r'\n?', re.S)
HINT_RE = re.compile(re.escape(HINT_BEGIN) + r'.*?' + re.escape(HINT_END) + r'\n?', re.S)

def process(pages, locales, skip=frozenset()):
    lazy = eager = skipped = 0
    for p in pages:
        rp = relpath(p)
        # Only the pages that builder actually writes - its index.html files.
        # The hand-written privacy policy in that tree is not one of them, and
        # skipping it left it with a canonical pointing at its own old URL.
        if rp.split('/')[0] in SELF_MANAGED and rp.endswith('/index.html'):
            skipped += 1
            continue
        s = open(p, encoding='utf-8').read()
        s = SEO_RE.sub('', s)
        s = HINT_RE.sub('', s)
        if '</head>' not in s:
            print(f"  ! no </head>, skipped: {relpath(p)}")
            continue
        s = s.replace('</head>', seo_block(p, locales, skip) + '\n' + HINTS + '\n</head>', 1)

        # Images up to and including the first one after </nav> stay eager -
        # that is the brand logo, the nav dropdown icons and the hero (the LCP
        # element). Everything below the fold is lazy-loaded.
        nav_end = s.find('</nav>')
        first_after_nav = s.find('<img', nav_end) if nav_end != -1 else -1
        cutoff = first_after_nav + 1 if first_after_nav != -1 else 0

        def img(m):
            nonlocal lazy, eager
            tag, pos = m.group(0), m.start()
            if 'loading=' in tag:
                return tag
            extra = ' decoding="async"' if 'decoding=' not in tag else ''
            if pos < cutoff:
                eager += 1
                if pos >= nav_end and 'fetchpriority=' not in tag:
                    extra += ' fetchpriority="high"'
                return tag[:-1].rstrip() + extra + '>'
            lazy += 1
            return tag[:-1].rstrip() + ' loading="lazy"' + extra + '>'

        s = re.sub(r'<img\b[^>]*>', img, s)
        open(p, 'w', encoding='utf-8', newline='').write(s)
    return lazy, eager, skipped

def write_sitemap(pages):
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
           '        xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    n_alt = n_skipped = 0
    for p in pages:
        s = open(p, encoding='utf-8').read()
        # A sitemap is a request to index. Listing a page we just told robots
        # not to index is a contradiction Search Console reports as an error.
        if 'content="noindex' in s:
            n_skipped += 1
            continue
        canon = re.search(r'rel="canonical" href="([^"]+)"', s).group(1)
        alts = [(m.group(1), m.group(2))
                for m in re.finditer(r'hreflang="([^"]+)" href="([^"]+)"', s)]
        lm = datetime.date.fromtimestamp(os.path.getmtime(p)).isoformat()
        r = relpath(p)
        depth = r.count('/')
        if r == 'index.html':                              pr, cf = '1.0', 'weekly'
        elif depth == 1 and r.endswith('index.html'):       pr, cf = '0.9', 'weekly'
        elif r in ('about.html', 'contact.html'):           pr, cf = '0.6', 'monthly'
        elif 'privacy' in r:                                pr, cf = '0.3', 'yearly'
        else:                                               pr, cf = '0.7', 'monthly'
        out += ['  <url>', f'    <loc>{escape(canon)}</loc>',
                f'    <lastmod>{lm}</lastmod>',
                f'    <changefreq>{cf}</changefreq>',
                f'    <priority>{pr}</priority>']
        for code, href in alts:
            out.append(f'    <xhtml:link rel="alternate" hreflang="{escape(code)}" '
                       f'href="{escape(href)}"/>')
            n_alt += 1
        out.append('  </url>')
    out.append('</urlset>')
    open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8',
         newline='\n').write('\n'.join(out) + '\n')
    return len(pages) - n_skipped, n_alt

ROBOTS = f"""# https://www.dhinovatech.com/robots.txt
User-agent: *
Allow: /

# Crawler traps / non-content assets
Disallow: /*.json$

Sitemap: {SITE}/sitemap.xml
"""

MANIFEST = """{
  "name": "Dhinovatech",
  "short_name": "Dhinovatech",
  "description": "Privacy-first, offline-capable applications for Android and Windows.",
  "start_url": "/",
  "scope": "/",
  "display": "standalone",
  "background_color": "#080c14",
  "theme_color": "#080c14",
  "icons": [
    { "src": "/assets/images/LogoOnlyImage.png", "sizes": "256x256", "type": "image/png", "purpose": "any" },
    { "src": "/favicon.png", "sizes": "256x256", "type": "image/png", "purpose": "maskable" }
  ]
}
"""

def main():
    pages = discover()
    locales = locale_map(pages)
    skip = untranslated(pages)
    lazy, eager, skipped = process(pages, locales, skip)
    n_urls, n_alt = write_sitemap(pages)
    open(os.path.join(ROOT, 'robots.txt'), 'w', encoding='utf-8', newline='\n').write(ROBOTS)
    open(os.path.join(ROOT, 'site.webmanifest'), 'w', encoding='utf-8', newline='\n').write(MANIFEST)

    print(f"pages processed : {len(pages)}")
    for a in sorted(locales):
        print(f"  {a:32s} {len(locales[a]) + 1:3d} languages")
    if skip:
        by_app = {}
        for r in sorted(skip):
            by_app.setdefault(r.split('/')[0], []).append(r.split('/')[1])
        print("noindexed       : %d locale pages still identical to English"
              % len(skip))
        for a in sorted(by_app):
            print(f"  {a:32s} {' '.join(by_app[a])}")
    print(f"images          : {lazy} lazy, {eager} eager")
    print(f"self-managed    : {skipped} pages skipped ({', '.join(SELF_MANAGED)})")
    print(f"sitemap.xml     : {n_urls} URLs, {n_alt} hreflang annotations")
    print("robots.txt, site.webmanifest written")

if __name__ == '__main__':
    sys.exit(main())
