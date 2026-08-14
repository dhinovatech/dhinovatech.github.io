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

# Directory code -> BCP-47 hreflang value (only where they differ).
HREF = {'zh': 'zh-Hans'}
# BCP-47 -> og:locale. Only confident mappings; og:locale is optional, so a
# missing entry simply omits the tag rather than emitting something wrong.
OGLOC = {'en':'en_US','es':'es_ES','fr':'fr_FR','de':'de_DE','it':'it_IT','nl':'nl_NL',
 'pl':'pl_PL','pt':'pt_BR','ru':'ru_RU','ja':'ja_JP','ko':'ko_KR','zh-Hans':'zh_CN',
 'tr':'tr_TR','vi':'vi_VN','id':'id_ID','hi':'hi_IN','ar':'ar_AR','ur':'ur_PK',
 'fa':'fa_IR','bn':'bn_IN','mr':'mr_IN','te':'te_IN','ta':'ta_IN','uk':'uk_UA',
 'sw':'sw_KE','th':'th_TH','ml':'ml_IN','kn':'kn_IN','gu':'gu_IN','pa':'pa_IN',
 'or':'or_IN','tl':'tl_PH','ha':'ha_NG','yo':'yo_NG','am':'am_ET','ps':'ps_AF',
 'jv':'jv_ID'}

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

# ---------------------------------------------------------------- discovery
def discover():
    pages = []
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [x for x in dn if x not in ('.git', 'tools')]
        for f in fn:
            if f.endswith('.html') and f not in EXCLUDE:
                pages.append(os.path.join(dp, f))
    return sorted(pages)

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
def seo_block(p, locales):
    parts = relpath(p).split('/')
    app = parts[0] if parts[0] in APPS else None
    loc = parts[1] if (app and len(parts) == 3) else ('en' if app else None)
    is_app_page = app is not None and parts[-1] == 'index.html'

    src = open(p, encoding='utf-8').read()
    title = re.search(r'<title>(.*?)</title>', src, re.S).group(1).strip()
    desc = re.search(r'<meta\s+name="description"\s+content="(.*?)"', src, re.S | re.I).group(1).strip()
    lang = re.search(r'<html[^>]*\slang="([^"]+)"', src, re.I).group(1)
    url = SITE + url_of(p)

    L = [SEO_BEGIN,
         f'  <link rel="canonical" href="{url}">',
         '  <meta name="robots" content="index,follow,max-image-preview:large,'
         'max-snippet:-1,max-video-preview:-1">']

    if is_app_page:
        base = f'{SITE}/{app}/'
        L.append(f'  <link rel="alternate" hreflang="x-default" href="{base}">')
        L.append(f'  <link rel="alternate" hreflang="en" href="{base}">')
        for c in locales[app]:
            L.append(f'  <link rel="alternate" hreflang="{hl(c)}" href="{base}{c}/">')

    a = APPS.get(app)
    if a:
        ogimg, ogw, ogh, ogalt, large = a['og'], a['ogw'], a['ogh'], a['ogalt'], a['large']
    else:
        ogimg, ogw, ogh, large = "/assets/images/dhinovatech-hero.jpg", 1376, 768, True
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
    # NOTE: no `offers`/price and no `aggregateRating` are emitted. Those must
    # reflect reality; publishing invented ratings or prices breaks Google's
    # structured-data policy and risks a manual action. Add them here only with
    # real store figures, and keep them updated.
    graph = []
    if url_of(p) == '/':
        graph.append({"@type": "Organization", "@id": ORG, "name": "Dhinovatech",
            "url": SITE + "/", "email": "dhinovatech@gmail.com",
            "logo": {"@type": "ImageObject",
                     "url": SITE + "/assets/images/LogoWithText.png",
                     "width": 1096, "height": 176},
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
        graph.append({"@type": "SoftwareApplication", "@id": f"{SITE}/{app}/#software",
            "name": a['name'], "operatingSystem": a['os'],
            "applicationCategory": a['cat'], "description": desc,
            "url": f"{SITE}/{app}/",
            "inLanguage": [hl(c) for c in ['en'] + locales[app]],
            "image": SITE + a['icon'], "downloadUrl": a['store'],
            "installUrl": a['store'], "publisher": {"@id": ORG}, "author": {"@id": ORG}})
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
  '  <link rel="preconnect" href="https://www.googletagmanager.com">',
  '  <link rel="dns-prefetch" href="https://www.googletagmanager.com">',
  '  <link rel="manifest" href="/site.webmanifest">',
  '  <meta name="theme-color" content="#080c14">',
  '  <meta name="color-scheme" content="dark light">',
  HINT_END,
])

SEO_RE  = re.compile(re.escape(SEO_BEGIN) + r'.*?' + re.escape(SEO_END) + r'\n?', re.S)
HINT_RE = re.compile(re.escape(HINT_BEGIN) + r'.*?' + re.escape(HINT_END) + r'\n?', re.S)

def process(pages, locales):
    lazy = eager = 0
    for p in pages:
        s = open(p, encoding='utf-8').read()
        s = SEO_RE.sub('', s)
        s = HINT_RE.sub('', s)
        if '</head>' not in s:
            print(f"  ! no </head>, skipped: {relpath(p)}")
            continue
        s = s.replace('</head>', seo_block(p, locales) + '\n' + HINTS + '\n</head>', 1)

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
    return lazy, eager

def write_sitemap(pages):
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
           '        xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    n_alt = 0
    for p in pages:
        s = open(p, encoding='utf-8').read()
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
    return len(pages), n_alt

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
    lazy, eager = process(pages, locales)
    n_urls, n_alt = write_sitemap(pages)
    open(os.path.join(ROOT, 'robots.txt'), 'w', encoding='utf-8', newline='\n').write(ROBOTS)
    open(os.path.join(ROOT, 'site.webmanifest'), 'w', encoding='utf-8', newline='\n').write(MANIFEST)

    print(f"pages processed : {len(pages)}")
    for a in sorted(locales):
        print(f"  {a:32s} {len(locales[a]) + 1:3d} languages")
    print(f"images          : {lazy} lazy, {eager} eager")
    print(f"sitemap.xml     : {n_urls} URLs, {n_alt} hreflang annotations")
    print("robots.txt, site.webmanifest written")

if __name__ == '__main__':
    sys.exit(main())
