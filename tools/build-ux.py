#!/usr/bin/env python3
"""
Dhinovatech UX / accessibility / conversion builder.

For every page this adds, idempotently:
  * a translated skip link (first tab stop, WCAG 2.4.1)
  * a <main id="main"> landmark wrapping the page body
  * aria-hidden="true" on purely decorative Bootstrap icons, so screen
    readers stop announcing hundreds of meaningless glyphs
  * a translated back-to-top control
  * a sticky mobile install bar on app pages (the conversion CTA)
  * install-referrer / campaign tagging on every store link, so Play Console
    and Partner Center can attribute installs back to this site
  * the ux.js behaviour layer

Run:  python tools/build-ux.py
Idempotent: generated regions are delimited and replaced on each run.
"""
import os, re, sys, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BEGIN = "<!-- BEGIN generated UX block -->"
END = "<!-- END generated UX block -->"

# Apps -> store link + icon, used to build the sticky install bar.
APPS = {
 'glowcompare': dict(name="GlowCompare", icon="/assets/images/glowcompare-icon.png",
    store="https://play.google.com/store/apps/details?id=com.dhinova.glowcompare",
    kind='play'),
 'milk-monthly-expense-calendar': dict(name="Milk Monthly Expense Calendar",
    icon="/assets/images/milk-calendar-icon.png",
    store="https://play.google.com/store/apps/details?id=com.dhinova.milkmonthlyexpensecalendar",
    kind='play'),
 'notelock': dict(name="Notelock", icon="/assets/images/notelock-icon.png",
    store="https://apps.microsoft.com/detail/9NRQLDJ9ZFCM", kind='ms'),
 'slouch-guard': dict(name="Slouch Guard", icon="/assets/images/slouch-guard-icon.png",
    store="https://apps.microsoft.com/detail/9NJH1LC3PQ8N", kind='ms'),
 'mortgage-loan-emi-pro': dict(name="Mortgage Loan EMI Pro Insights",
    icon="/assets/images/mortgage-emi-icon.png",
    store="https://apps.microsoft.com/detail/9PFS2J56BJXR", kind='ms'),
 'glowcompare-windows': dict(name="GlowCompare",
    icon="/assets/images/glowcompare-icon.png",
    store="https://apps.microsoft.com/detail/9N4QM1FDQ1CB", kind='ms'),
 'stow': dict(name="Stow", icon="/assets/images/stow-icon.png",
    store="https://apps.microsoft.com/detail/9NHBR7SW2TZ0", kind='ms'),
 'nudge': dict(name="Nudge", icon="/assets/images/nudge-icon.png",
    store="https://apps.microsoft.com/detail/9MV92P7RLDGB", kind='ms'),
 'aes-vault': dict(name="AES Vault", icon="/assets/images/aes-vault-icon.png",
    store="https://apps.microsoft.com/detail/9N8XWF00VRNJ", kind='ms'),
}

# UI microcopy. Keys: skip link, back-to-top label, install button.
UI = {
 'en':  ("Skip to main content", "Back to top", "Install"),
 'es':  ("Saltar al contenido principal", "Volver arriba", "Instalar"),
 'fr':  ("Aller au contenu principal", "Retour en haut", "Installer"),
 'de':  ("Zum Hauptinhalt springen", "Nach oben", "Installieren"),
 'it':  ("Vai al contenuto principale", "Torna su", "Installa"),
 'nl':  ("Ga naar hoofdinhoud", "Terug naar boven", "Installeren"),
 'pl':  ("Przejdź do treści głównej", "Powrót na górę", "Zainstaluj"),
 'pt':  ("Ir para o conteúdo principal", "Voltar ao topo", "Instalar"),
 'ru':  ("Перейти к основному содержанию", "Наверх", "Установить"),
 'uk':  ("Перейти до основного вмісту", "Догори", "Встановити"),
 'ja':  ("メインコンテンツへスキップ", "トップへ戻る", "インストール"),
 'ko':  ("본문으로 건너뛰기", "맨 위로", "설치"),
 'zh':  ("跳到主要内容", "返回顶部", "安装"),
 'yue': ("跳去主要內容", "返去頂部", "安裝"),
 'wuu': ("跳到主要内容", "回到顶部", "安装"),
 'nan': ("跳去主要內容", "轉去頂懸", "安裝"),
 'tr':  ("Ana içeriğe geç", "Başa dön", "Yükle"),
 'vi':  ("Chuyển đến nội dung chính", "Lên đầu trang", "Cài đặt"),
 'id':  ("Lompat ke konten utama", "Kembali ke atas", "Pasang"),
 'jv':  ("Langsung menyang isi utama", "Bali menyang ndhuwur", "Pasang"),
 'tl':  ("Lumaktaw sa pangunahing nilalaman", "Bumalik sa itaas", "I-install"),
 'hi':  ("मुख्य सामग्री पर जाएँ", "ऊपर जाएँ", "इंस्टॉल करें"),
 'bho': ("मुख्य सामग्री पर जाईं", "ऊपर जाईं", "इंस्टॉल करीं"),
 'mr':  ("मुख्य मजकुरावर जा", "वर जा", "इंस्टॉल करा"),
 'bn':  ("মূল বিষয়বস্তুতে যান", "উপরে ফিরুন", "ইনস্টল করুন"),
 'gu':  ("મુખ્ય સામગ્રી પર જાઓ", "ઉપર જાઓ", "ઇન્સ્ટોલ કરો"),
 'pa':  ("ਮੁੱਖ ਸਮੱਗਰੀ ਤੇ ਜਾਓ", "ਉੱਪਰ ਜਾਓ", "ਇੰਸਟਾਲ ਕਰੋ"),
 'or':  ("ମୁଖ୍ୟ ବିଷୟବସ୍ତୁକୁ ଯାଆନ୍ତୁ", "ଉପରକୁ ଫେରନ୍ତୁ", "ଇନଷ୍ଟଲ୍ କରନ୍ତୁ"),
 'te':  ("ప్రధాన కంటెంట్‌కు వెళ్లండి", "పైకి వెళ్లండి", "ఇన్‌స్టాల్ చేయండి"),
 'ta':  ("முதன்மை உள்ளடக்கத்திற்குச் செல்க", "மேலே செல்க", "நிறுவு"),
 'kn':  ("ಮುಖ್ಯ ವಿಷಯಕ್ಕೆ ಹೋಗಿ", "ಮೇಲಕ್ಕೆ ಹೋಗಿ", "ಸ್ಥಾಪಿಸಿ"),
 'ml':  ("പ്രധാന ഉള്ളടക്കത്തിലേക്ക് പോകുക", "മുകളിലേക്ക്", "ഇൻസ്റ്റാൾ ചെയ്യുക"),
 'ar':  ("انتقل إلى المحتوى الرئيسي", "العودة إلى الأعلى", "تثبيت"),
 'arz': ("روح للمحتوى الرئيسى", "ارجع لفوق", "تثبيت"),
 'ur':  ("مرکزی مواد پر جائیں", "اوپر جائیں", "انسٹال کریں"),
 'pnb': ("مکھ مواد تے جاؤ", "اُتے جاؤ", "انسٹال کرو"),
 'fa':  ("پرش به محتوای اصلی", "بازگشت به بالا", "نصب"),
 'ps':  ("اصلي منځپانګې ته ورشئ", "بیرته پورته", "نصب کړئ"),
 'th':  ("ข้ามไปยังเนื้อหาหลัก", "กลับไปด้านบน", "ติดตั้ง"),
 'sw':  ("Rukia maudhui makuu", "Rudi juu", "Sakinisha"),
 'ha':  ("Tsallake zuwa babban abun ciki", "Koma sama", "Shigar"),
 'yo':  ("Fo si akoonu akọkọ", "Pada si oke", "Fi sori ẹrọ"),
 'am':  ("ወደ ዋናው ይዘት ዝለል", "ወደ ላይ ተመለስ", "ጫን"),
 'pcm': ("Jump go main content", "Go back to top", "Install"),
 'cs':  ("Přejít na hlavní obsah", "Zpět nahoru", "Instalovat"),
 'da':  ("Gå til hovedindhold", "Tilbage til toppen", "Installer"),
 'sv':  ("Hoppa till huvudinnehållet", "Till toppen", "Installera"),
 'nb':  ("Gå til hovedinnhold", "Til toppen", "Installer"),
 'fi':  ("Siirry pääsisältöön", "Takaisin ylös", "Asenna"),
 'hu':  ("Ugrás a fő tartalomra", "Vissza a tetejére", "Telepítés"),
 'he':  ("דלג לתוכן הראשי", "חזרה למעלה", "התקן"),
 'ro':  ("Treci la conținutul principal", "Înapoi sus", "Instalează"),
 'el':  ("Μετάβαση στο κύριο περιεχόμενο", "Επιστροφή στην κορυφή", "Εγκατάσταση"),
 'sk':  ("Prejsť na hlavný obsah", "Späť na začiatok", "Inštalovať"),
 'ca':  ("Salta al contingut principal", "Torna a dalt", "Instal·la"),
 'kk':  ("Негізгі мазмұнға өту", "Жоғарыға қайту", "Орнату"),
 'my':  ("ပင်မအကြောင်းအရာသို့ သွားရန်", "အပေါ်သို့ ပြန်သွားရန်", "ထည့်သွင်းပါ"),
 'ms':  ("Langkau ke kandungan utama", "Kembali ke atas", "Pasang"),
}

def ui(lang):
    """Microcopy for a page's <html lang>.

    Pages carry full BCP-47 tags (zh-Hans, pt-BR), while the table above is
    keyed by the base language, so fall back to the subtag before English -
    otherwise every Chinese page silently renders its skip link in English.
    """
    if lang in UI:
        return UI[lang]
    return UI.get(lang.split('-')[0], UI['en'])

def relpath(p):
    return os.path.relpath(p, ROOT).replace('\\', '/')

# Partner Center's acquisition report breaks installs down by `cid`, and it is
# one bucket for the whole site rather than one per app: the question it exists
# to answer is "how many installs came from dhinovatech.com at all", which the
# per-app `ocid` below already answers app by app.
STORE_CID = "FromDhinoWebsite"


def href_attr(url):
    """Escape a tagged URL for an href attribute.

    These are the only multi-parameter links on the site, and a bare `&` in an
    attribute is an HTML parse error - harmless in practice, but this pass is
    the one place that emits them, so it is the one place to get it right.

    Pairs with unhref(): the pass re-reads its own output on every run, so
    whatever this writes has to decode back to exactly what tag_store_url()
    produced, or the [?&]cid= test below stops matching (`&amp;cid=` has a
    semicolon before `cid`, not an ampersand) and a second cid is appended on
    every build.
    """
    return url.replace('&', '&amp;')


def unhref(url):
    return url.replace('&amp;', '&')


def tag_store_url(url, page_url, app_key):
    """Attach campaign attribution so installs can be traced back to the site.

    Google Play reads the `referrer` parameter (URL-encoded key=value pairs)
    and surfaces it in Play Console acquisition reports.

    Microsoft Store links carry two tags, because they are read by two
    different systems: `ocid` is Microsoft's originating-campaign parameter and
    is what assets/js/ux.js hands to the ms-windows-store:// protocol, and
    `cid` is the custom campaign ID Partner Center reports acquisitions
    against. Existing parameters are preserved.
    """
    campaign = app_key or 'site'
    if 'play.google.com' in url:
        if 'referrer=' in url:
            return url
        ref = ('utm_source%3Ddhinovatech.com'
               '%26utm_medium%3Dwebsite'
               f'%26utm_campaign%3D{campaign}')
        sep = '&' if '?' in url else '?'
        return f'{url}{sep}referrer={ref}'
    if 'apps.microsoft.com' in url:
        if re.search(r'[?&]ocid=', url):
            # normalise the existing share ocid to our own campaign tag
            url = re.sub(r'ocid=[^&]*', f'ocid=dhinovatech_{campaign}', url)
        else:
            url += ('&' if '?' in url else '?') + f'ocid=dhinovatech_{campaign}'
        # The boundary matters: 'cid=' is a substring of 'ocid=', so a plain
        # containment test would decide cid was already there every time and
        # this pass would never add it.
        if re.search(r'[?&]cid=', url):
            url = re.sub(r'([?&])cid=[^&]*', r'\1cid=' + STORE_CID, url)
        else:
            url += ('&' if '?' in url else '?') + 'cid=' + STORE_CID
        return url
    return url

def build_block(app_key, lang, is_rtl):
    """Back-to-top control + (on app pages) the sticky install bar."""
    skip, top, install = ui(lang)
    L = [BEGIN]
    if app_key:
        a = APPS[app_key]
        store = href_attr(tag_store_url(a['store'], None, app_key))
        icon = 'bi-google-play' if a['kind'] == 'play' else 'bi-microsoft'
        store_name = 'Google Play' if a['kind'] == 'play' else 'Microsoft Store'
        btn = 'btn-dhin-primary'
        L += [
          f'<div class="install-bar" role="complementary" aria-label="{html.escape(a["name"])}">',
          f'  <img src="{a["icon"]}" alt="" width="42" height="42" loading="lazy" decoding="async">',
          '  <div class="install-bar-text">',
          f'    <div class="install-bar-title">{html.escape(a["name"])}</div>',
          f'    <div class="install-bar-sub"><i class="bi {icon}" aria-hidden="true"></i> {store_name}</div>',
          '  </div>',
          f'  <a href="{store}" target="_blank" rel="noopener"',
          f'     class="btn {btn} btn-sm rounded-pill px-3">{html.escape(install)}</a>',
          '</div>',
        ]
    L += [
      f'<button type="button" class="to-top" aria-label="{html.escape(top)}" title="{html.escape(top)}">',
      '  <i class="bi bi-arrow-up" aria-hidden="true"></i>',
      '</button>',
      '<script src="/assets/js/ux.js"></script>',
      END,
    ]
    return '\n'.join(L)

BLOCK_RE = re.compile(re.escape(BEGIN) + r'.*?' + re.escape(END) + r'\n?', re.S)
SKIP_RE = re.compile(r'<a class="skip-link"[^>]*>.*?</a>\s*\n?', re.S)

# A Bootstrap icon is decorative when it sits next to its own label; these are
# the <i class="bi ..."></i> glyphs used throughout. Announcing them adds noise
# for screen-reader users, so they are hidden from the accessibility tree.
ICON_RE = re.compile(r'<i class="bi ([^"]*)"([^>]*)>')

def process(path):
    s = open(path, encoding='utf-8').read()
    rel = relpath(path)
    parts = rel.split('/')
    app_key = parts[0] if parts[0] in APPS and parts[-1] == 'index.html' else None
    lang = re.search(r'<html[^>]*\slang="([^"]+)"', s).group(1)
    is_rtl = 'dir="rtl"' in s
    skip, top, install = ui(lang)

    # ---- clean previous generation --------------------------------------
    s = BLOCK_RE.sub('', s)
    s = SKIP_RE.sub('', s)

    # ---- skip link as the first focusable element ------------------------
    link = (f'<a class="skip-link" href="#main">{html.escape(skip)}</a>')
    s = re.sub(r'(<body[^>]*>)', lambda m: m.group(1) + '\n' + link, s, count=1)

    # ---- <main> landmark --------------------------------------------------
    if '<main' not in s:
        s = s.replace('</nav>', '</nav>\n\n<main id="main">', 1)
        # close it immediately before the footer
        m = re.search(r'\n?\s*<footer\b', s)
        if m:
            s = s[:m.start()] + '\n\n</main>\n' + s[m.start():].lstrip('\n')
    else:
        # A hand-written <main> already exists; it still needs the id so the
        # skip link has something to target.
        mo = re.search(r'<main\b([^>]*)>', s)
        if mo and 'id=' not in mo.group(1):
            s = s[:mo.start()] + f'<main id="main"{mo.group(1)}>' + s[mo.end():]

    # ---- decorative icons -------------------------------------------------
    def icon(m):
        if 'aria-hidden' in m.group(0):
            return m.group(0)
        return f'<i class="bi {m.group(1)}"{m.group(2)} aria-hidden="true">'
    s = ICON_RE.sub(icon, s)

    # ---- store link attribution ------------------------------------------
    def store(m):
        url = tag_store_url(unhref(m.group(1)), rel, app_key or 'site')
        return 'href="' + href_attr(url) + '"'
    s = re.sub(r'href="(https://(?:play\.google\.com|apps\.microsoft\.com)/[^"]*)"',
               store, s)

    # ---- UX block before </body> -----------------------------------------
    s = s.replace('</body>', build_block(app_key, lang, is_rtl) + '\n</body>', 1)

    for attempt in range(5):
        try:
            with open(path, 'w', encoding='utf-8', newline='') as fh:
                fh.write(s)
            break
        except OSError:
            if attempt == 4:
                raise
            import time
            time.sleep(0.15)
    return app_key is not None

def main():
    pages = []
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [x for x in dn if x not in ('.git', 'tools')]
        for f in fn:
            if f.endswith('.html'):
                pages.append(os.path.join(dp, f))
    bars = 0
    missing = set()
    for p in sorted(pages):
        s = open(p, encoding='utf-8').read()
        lang = re.search(r'<html[^>]*\slang="([^"]+)"', s).group(1)
        # Mirror ui()'s subtag fallback, so a page that does resolve (zh-Hans
        # -> zh) is not reported as untranslated.
        if lang not in UI and lang.split('-')[0] not in UI:
            missing.add(lang)
        if process(p):
            bars += 1
    print(f"pages processed   : {len(pages)}")
    print(f"install bars added: {bars}")
    if missing:
        print(f"!! no UI translation, fell back to English: {sorted(missing)}")
    else:
        print("UI microcopy      : translated for every language present")

if __name__ == '__main__':
    sys.exit(main())
