#!/usr/bin/env python3
"""
Generate the policy pages this site was missing.

Google Play and the Microsoft Store both require a reachable privacy policy per
listing. Before this, exactly one existed - and it was the Windows GlowCompare
policy filed under /glowcompare/, the Android app's URL. Notelock, AES Vault,
Slouch Guard, Milk Calendar and Mortgage EMI Pro had none at all, and neither
did the website itself, which now sets analytics cookies and therefore owes
readers a notice explaining them.

This writes, from tools/privacy-facts.json:
  <app>/privacy.html   one per app in the facts file
  /privacy.html        the website's own policy (analytics, hosting, consent)
  /terms.html          site terms

The long hand-written GlowCompare for Windows policy at
glowcompare-windows/privacy.html is left alone; it says more than a generated
page can and it is already correct for the tree it now sits in.

Run:  python tools/build-privacy.py
      python tools/build-seo.py     # afterwards, to pick up the new pages

Every page is rewritten from the facts file on each run, so edit the JSON
rather than the HTML.
"""
import html
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACTS = os.path.join(ROOT, "tools", "privacy-facts.json")

SITE = "https://www.dhinovatech.com"
EMAIL = "dhinovatech@gmail.com"
COMPANY = "Dhinova Tech"
EFFECTIVE = "August 19, 2026"

with io.open(FACTS, encoding="utf-8") as _fh:
    F = json.load(_fh)


def e(s):
    return html.escape(s, quote=False)


def shell(title, desc, body, path_depth=0):
    """The page chrome shared by every policy page."""
    return """<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>%s</title>
  <meta name="description" content="%s">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">
  <link rel="stylesheet" href="/assets/css/legal.css">
  <link rel="icon" type="image/x-icon" href="/favicon.ico">
  <link rel="icon" type="image/png" href="/favicon.png">
  <link rel="apple-touch-icon" href="/favicon.png">
</head>
<body>
<a class="skip-link" href="#main">Skip to main content</a>
%s
</body>
</html>
""" % (e(title), e(desc), body)


def toc(items):
    lis = "\n".join('        <li><a href="#%s">%s</a></li>' % (i, e(t))
                    for i, t in items)
    return """    <nav class="toc" aria-label="Table of contents">
      <p class="toc-title">Contents</p>
      <ol>
%s
      </ol>
    </nav>
""" % lis


def tag_for(storage):
    """Colour the storage column by where the data actually ends up."""
    s = storage.lower()
    if "never stored" in s or "discarded" in s or "memory only" in s or "in memory" in s:
        return "transient", "Transient"
    if "sent to" in s or "held by" in s:
        return "external", "Leaves device"
    return "local", "Local"


def table(rows):
    body = ""
    for data, purpose, storage in rows:
        cls, label = tag_for(storage)
        body += """            <tr>
              <td>%s</td>
              <td>%s</td>
              <td>%s<br><span class="tag %s">%s</span></td>
            </tr>
""" % (e(data), e(purpose), e(storage), cls, label)
    return """      <div class="data-table-wrapper">
        <table class="data-table">
          <thead>
            <tr><th>Data</th><th>Purpose</th><th>Where it lives</th></tr>
          </thead>
          <tbody>
%s          </tbody>
        </table>
      </div>
""" % body


def section(n, sid, heading, inner):
    return """    <section class="section" id="%s">
      <h2>%s. %s</h2>
%s    </section>

""" % (sid, n, e(heading), inner)


def p(text):
    return "      <p>%s</p>\n" % e(text)


def footer():
    return """    <footer class="footer">
      <p>&copy; 2026 %s. All rights reserved.</p>
      <p>
        <a href="/">Home</a> &middot;
        <a href="/privacy.html">Website privacy</a> &middot;
        <a href="/terms.html">Terms</a> &middot;
        <a href="mailto:%s">Contact</a>
      </p>
    </footer>

  </main>
""" % (COMPANY, EMAIL)


def app_page(key, f):
    secs, items, n = "", [], 1

    def add(sid, heading, inner):
        nonlocal secs, n
        items.append((sid, heading))
        secs += section(n, sid, heading, inner)
        n += 1

    add("overview", "Overview",
        p('%s ("the App") is published by %s ("we", "us", "our"). %s'
          % (f["name"], COMPANY, f["intro"]))
        + p("The App is built to keep your data on your own device. We do not "
            "operate user accounts for it, and we cannot see what you store in it."))

    add("data-we-collect", "What the App handles",
        p("This table covers every category of data the App processes, what it "
          "is for, and where it ends up.")
        + table(f["data"]))

    add("storage", "Where your data is stored",
        p("Everything marked Local above stays in the App's own storage on your "
          "device. We run no user database and no cloud sync for it, so there is "
          "no copy of your data on our side to lose, sell, or be compelled to "
          "hand over.")
        + p(f["uninstall"]))

    perms = "".join(
        "        <li><strong>%s</strong> &mdash; %s</li>\n" % (e(a), e(b))
        for a, b in f["permissions"])
    inner = (p("The App asks for the following, and nothing else:")
             + "      <ul>\n" + perms + "      </ul>\n"
             + p("You can review or revoke these at any time in %s."
                 % f["settings_path"]))
    if f.get("camera_note"):
        inner += '      <div class="callout highlight">\n        <p>%s</p>\n      </div>\n' % e(f["camera_note"])
    add("permissions", "Permissions", inner)

    if f.get("third_parties"):
        inner = p("These are the only third parties the App can send anything to, "
                  "and each one is listed with what triggers it.")
        for name, what, url in f["third_parties"]:
            inner += ('      <p><strong>%s</strong> &mdash; %s '
                      '<a href="%s" target="_blank" rel="noopener">Their privacy policy</a>.</p>\n'
                      % (e(name), e(what), e(url)))
        add("third-parties", "Third-party services", inner)
    else:
        add("third-parties", "Third-party services",
            p("None. The App contains no third-party SDKs, no advertising "
              "libraries, and no analytics. It does not need a network "
              "connection to do its job."))

    if f.get("iap"):
        add("purchases", "Purchases", p(f["iap_note"]))

    add("no-tracking", "Analytics, ads and tracking",
        p("The App itself contains no analytics, no advertising and no tracking "
          "of any kind. We do not build a profile of you, and we have nothing "
          "to sell to anyone else.")
        + p("This is separate from the website you are reading now, which does "
            "use analytics with your consent. That is described in the "
            "website privacy policy."))

    add("children", "Children's privacy",
        p("The App is not directed at children under 13, and we do not "
          "knowingly collect personal information from them. Because the App "
          "holds no accounts and transmits no personal data to us, there is no "
          "record on our side to delete."))

    rights = p("Because your data never reaches us, you exercise your rights "
               "directly and immediately, without asking us first:")
    rights += ("      <ul>\n"
               "        <li><strong>Access and portability</strong> &mdash; your data is in the App on your device; export or copy it whenever you like.</li>\n"
               "        <li><strong>Erasure</strong> &mdash; delete entries in the App, or uninstall it, and it is gone.</li>\n"
               "        <li><strong>Objection and restriction</strong> &mdash; revoke a permission in your system settings and the corresponding feature stops.</li>\n"
               "      </ul>\n")
    rights += p("If you are in the EU/EEA or UK and want to raise something "
                "under the GDPR, write to us at %s and we will answer." % EMAIL)
    add("your-rights", "Your rights", rights)

    inner = p("The App is distributed only through %s, which signs and verifies "
              "every build. Install it from anywhere else and we cannot vouch "
              "for what you are running." % f["store"])
    if f.get("security_note"):
        inner += '      <div class="callout">\n        <p>%s</p>\n      </div>\n' % e(f["security_note"])
    if f.get("financial_note"):
        inner += '      <div class="callout">\n        <p>%s</p>\n      </div>\n' % e(f["financial_note"])
    add("security", "Security", inner)

    add("changes", "Changes to this policy",
        p("If we change how the App handles data, this page changes with it and "
          "the effective date above moves. Material changes will also be noted "
          "in the App's store listing release notes."))

    add("contact", "Contact",
        p("Questions about this policy, or about anything the App does with "
          "your data: %s. We read everything sent there." % EMAIL))

    body = """<main id="main" class="page">

    <header class="header">
      <a href="/%s/">&larr; %s</a>
      <h1>Privacy Policy</h1>
      <p class="subtitle">%s</p>
      <span class="effective-date">Effective date: %s</span>
    </header>

%s
%s%s""" % (key, e(f["name"]), e(f["subtitle"]), EFFECTIVE, toc(items), secs, footer())

    return shell("Privacy Policy | %s" % f["name"],
                 "How %s handles your data: what stays on your device, what it "
                 "never collects, and the permissions it asks for."
                 % f["name"], body)


def site_privacy_page():
    items, secs, n = [], "", 1

    def add(sid, heading, inner):
        nonlocal secs, n
        items.append((sid, heading))
        secs += section(n, sid, heading, inner)
        n += 1

    add("scope", "What this covers",
        p("This policy is about the website at www.dhinovatech.com &mdash; the "
          "pages you are reading right now. Each app we publish has its own "
          "policy covering what that app does on your device; this page does "
          "not replace them.")
        + p("The site is a set of static pages. There are no accounts, no "
            "logins, and no forms that submit anywhere."))

    add("analytics", "Analytics and cookies",
        p("We use Google Analytics 4 to see which pages people read and which "
          "languages get used. That is the only reason we measure anything.")
        + p("Analytics storage starts denied on every page load. Nothing is "
            "stored and no analytics cookie is set unless you press Accept on "
            "the consent notice. If you press Decline, or ignore the notice, or "
            "have JavaScript turned off, no analytics data is collected and the "
            "site works exactly the same.")
        + p("Your choice is remembered in your browser's local storage under "
            "the key dhin-consent so we do not ask again. Clearing your browser "
            "storage for this site resets it and the notice returns.")
        + '      <div class="callout">\n        <p>To change your mind later: clear this '
          'site\'s local storage in your browser settings, then reload. The notice will '
          'appear again and you can answer differently.</p>\n      </div>\n')

    add("what-we-see", "What analytics receives",
        p("When you have consented, Google Analytics receives the usual page "
          "measurement data: the page URL, referrer, approximate location "
          "derived from your IP address, device and browser type, and how long "
          "you stayed. We use it in aggregate.")
        + p("We do not collect your name, email address or any other detail "
            "that identifies you personally, because the site never asks you "
            "for one. IP addresses are handled by Google Analytics 4, which "
            "does not log or store them in full.")
        + '      <p>Google acts as our processor for this data. See '
          '<a href="https://policies.google.com/privacy" target="_blank" rel="noopener">'
          'Google\'s privacy policy</a> and '
          '<a href="https://support.google.com/analytics/answer/6004245" target="_blank" rel="noopener">'
          'how Google Analytics handles data</a>.</p>\n')

    add("hosting", "Hosting",
        p("The site is served as static files by GitHub Pages. Like any web "
          "host, GitHub processes request logs, including IP addresses, to "
          "deliver pages and defend against abuse. That happens whether or not "
          "you consent to analytics, because it is how the page reaches you at "
          "all.")
        + '      <p>See <a href="https://docs.github.com/site-policy/privacy-policies/github-privacy-statement" '
          'target="_blank" rel="noopener">GitHub\'s privacy statement</a>.</p>\n')

    add("third-party", "Other third parties",
        p("Page styling and icons are loaded from the jsDelivr CDN, and the "
          "Inter typeface from Google Fonts. Requesting a file from those "
          "services exposes your IP address to them, as it does for any file "
          "your browser fetches. Neither is used to track you, and no other "
          "external service is contacted.")
        + p("Links to Google Play, the Microsoft Store and other sites take you "
            "to services with their own policies, which we do not control."))

    add("contact-email", "If you email us",
        p("Writing to %s means we hold your message and address for as long as "
          "it takes to answer you and keep a record of the conversation. We do "
          "not add you to a mailing list &mdash; we do not have one." % EMAIL))

    add("rights", "Your rights",
        p("If you are in the EU/EEA or UK, the GDPR gives you rights of access, "
          "rectification, erasure, restriction, objection and portability over "
          "personal data we hold. In practice the only personal data we ever "
          "hold is an email you chose to send us, plus consented analytics that "
          "is not tied to your identity.")
        + p("Our lawful basis for analytics is your consent, which you can "
            "withdraw at any time by the method in section 2. Our basis for "
            "answering your email is our legitimate interest in replying to "
            "you.")
        + p("To exercise any of these rights, write to %s. You also have the "
            "right to complain to your local data protection authority."
            % EMAIL))

    links = p("Each app has its own policy covering what it does on your "
              "device. Nothing on this page overrides them:")
    rows = []
    for k, f in F.items():
        if k.startswith("_"):
            continue
        rows.append('        <li><a href="/%s/privacy.html">%s</a> &mdash; %s</li>'
                    % (k, e(f["name"]), e(f["platform"])))
    # Not generated from the facts file, but it is a policy page and belongs
    # in the index a reader uses to find one.
    rows.append('        <li><a href="/glowcompare-windows/privacy.html">'
                'GlowCompare Skincare Tracker</a> &mdash; Windows</li>')
    links += ("      <ul>\n" + "\n".join(rows)
              + "\n      </ul>\n")
    add("app-policies", "Policies for the apps", links)

    add("policy-changes", "Changes",
        p("When this policy changes, the effective date above changes with it. "
          "If a change affects what is collected or on what basis, the consent "
          "notice will be shown again."))

    add("reach-us", "Contact",
        p("%s &mdash; %s. That address reaches a person, not a ticket queue."
          % (COMPANY, EMAIL)))

    body = """<main id="main" class="page">

    <header class="header">
      <a href="/">&larr; dhinovatech.com</a>
      <h1>Website Privacy Policy</h1>
      <p class="subtitle">www.dhinovatech.com</p>
      <span class="effective-date">Effective date: %s</span>
    </header>

%s
%s%s""" % (EFFECTIVE, toc(items), secs, footer())

    return shell("Website Privacy Policy | Dhinovatech",
                 "How www.dhinovatech.com handles analytics, cookies and "
                 "consent. Analytics is denied by default and only runs if you "
                 "accept.", body)


def terms_page():
    items, secs, n = [], "", 1

    def add(sid, heading, inner):
        nonlocal secs, n
        items.append((sid, heading))
        secs += section(n, sid, heading, inner)
        n += 1

    add("about", "These terms",
        p("These terms cover your use of www.dhinovatech.com. Using the site "
          "means you accept them. Our apps are licensed separately, under the "
          "terms of the store you install them from &mdash; Google Play or the "
          "Microsoft Store &mdash; not under these."))

    add("use", "Using the site",
        p("The site is informational. You may read it, link to it, and quote "
          "reasonable extracts with attribution. Please do not scrape it at a "
          "rate that degrades it for others, mirror it as your own, or use it "
          "to distribute anything harmful."))

    add("ip", "Content and trademarks",
        p("The text, design, app names, logos and screenshots on this site "
          "belong to %s unless stated otherwise. Google Play and the Google "
          "Play logo are trademarks of Google LLC; Microsoft, Windows and the "
          "Microsoft Store are trademarks of Microsoft Corporation. We are not "
          "affiliated with or endorsed by either company beyond publishing "
          "apps on their stores." % COMPANY))

    add("apps", "About the apps described here",
        p("App descriptions on this site are marketing summaries of what the "
          "current release does. Features change between versions, and the "
          "store listing plus the app's own privacy policy are authoritative "
          "if the two ever disagree.")
        + p("Mortgage Loan EMI Pro Insights performs calculations on figures "
            "you supply. Nothing on this site or in that app is financial "
            "advice; check any projection against your lender before acting on "
            "it."))

    add("warranty", "No warranty",
        p("The site is provided as is. We work to keep it accurate and "
          "available, but we do not warrant that it is free of errors or that "
          "it will be uninterrupted."))

    add("liability", "Liability",
        p("To the extent the law allows, we are not liable for indirect or "
          "consequential loss arising from use of this site. Nothing here "
          "limits liability that cannot lawfully be limited, and if you are a "
          "consumer, your statutory rights are unaffected."))

    add("links", "Links out",
        p("We link to store listings and to third-party policies. We do not "
          "control those sites and are not responsible for their content."))

    add("law", "Governing law",
        p("These terms are governed by the laws of India, and the courts of "
          "India have jurisdiction. If you are a consumer elsewhere, this does "
          "not deprive you of the protection of your own local law."))

    add("updates", "Changes",
        p("We may update these terms; the effective date above will change "
          "when we do. Continuing to use the site after that means you accept "
          "the update."))

    add("terms-contact", "Contact",
        p("Questions about these terms: %s." % EMAIL))

    body = """<main id="main" class="page">

    <header class="header">
      <a href="/">&larr; dhinovatech.com</a>
      <h1>Terms of Use</h1>
      <p class="subtitle">www.dhinovatech.com</p>
      <span class="effective-date">Effective date: %s</span>
    </header>

%s
%s%s""" % (EFFECTIVE, toc(items), secs, footer())

    return shell("Terms of Use | Dhinovatech",
                 "Terms of use for www.dhinovatech.com, including content "
                 "ownership, disclaimers and governing law.", body)


def main():
    written = []
    for key, f in F.items():
        if key.startswith("_"):
            continue
        out = os.path.join(ROOT, key, "privacy.html")
        if not os.path.isdir(os.path.dirname(out)):
            print("  ! no such app directory, skipped: %s" % key)
            continue
        io.open(out, "w", encoding="utf-8", newline="\n").write(app_page(key, f))
        written.append("%s/privacy.html" % key)

    io.open(os.path.join(ROOT, "privacy.html"), "w",
            encoding="utf-8", newline="\n").write(site_privacy_page())
    written.append("privacy.html")
    io.open(os.path.join(ROOT, "terms.html"), "w",
            encoding="utf-8", newline="\n").write(terms_page())
    written.append("terms.html")

    for w in written:
        print("  wrote %s" % w)
    print("\n%d policy pages written." % len(written))
    print("glowcompare-windows/privacy.html left as hand-written.")

    todo = [(k, v["_verify"]) for k, v in F.items()
            if not k.startswith("_") and v.get("_verify")]
    if todo:
        print("\nBefore publishing, confirm these against the shipped builds:")
        for k, lines in todo:
            print("  %s" % k)
            for line in lines:
                print("    - %s" % line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
