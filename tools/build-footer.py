#!/usr/bin/env python3
"""
Keep the footer "Applications" column complete on every page.

The column was written by hand before GlowCompare existed and never picked it
up, so on 107 of 169 pages the two newest and most heavily promoted apps -
GlowCompare for Android and GlowCompare for Windows - were the only ones with
no footer link anywhere on the site. That is a self-inflicted internal-linking
hole on the pages that need the link equity most.

The list is rebuilt in place: the entries are matched by href, so a page that
already links an app keeps its own (possibly translated) link text and only the
missing entries are inserted, in APP_ORDER.

The "Company" column gets the same treatment for the legal pages. Those are
only appended if absent - that column's third entry is an anchor into whichever
page you are on, so it is never rebuilt wholesale.

Run:  python tools/build-footer.py
Idempotent: re-running finds nothing missing and rewrites nothing.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", "tools", "_src"}

# href -> default link text, in the order the column should read.
APP_ORDER = [
    ("/glowcompare/",                     "GlowCompare"),
    ("/glowcompare-windows/",             "GlowCompare for Windows"),
    ("/milk-monthly-expense-calendar/",   "Milk Calendar"),
    ("/slouch-guard/",                    "Slouch Guard AI"),
    ("/notelock/",                        "Notelock"),
    ("/mortgage-loan-emi-pro/",           "Mortgage EMI Pro"),
    ("/aes-vault/",                       "AES Vault"),
]

LI = '<li><a href="%s" class="footer-link">%s</a></li>'

# Appended to the Company column when missing. Store review and GDPR both
# expect these reachable from every page, not just the home page.
LEGAL = [("/privacy.html", "Privacy"), ("/terms.html", "Terms")]
# The app column is the only <ul> in the footer that links the app directories.
UL = re.compile(r"(<ul[^>]*>)(.*?)(</ul>)", re.S | re.I)
LI_HREF = re.compile(r'<li>.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?</li>', re.S | re.I)


def html_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in sorted(filenames):
            if fn.endswith(".html"):
                yield os.path.join(dirpath, fn)


def add_legal(block, indent):
    """Append the legal links to the Company column if they are not there."""
    have = set(h for h, _ in LI_HREF.findall(block))
    if "/about.html" not in have:
        return None                      # not the Company column
    missing = [(h, t) for h, t in LEGAL if h not in have]
    if not missing:
        return None
    joined = (chr(10) + indent).join(LI % (h, t) for h, t in missing)
    return block.rstrip() + chr(10) + indent + joined + chr(10) + indent[:-2]


def rebuild(block, indent):
    """Return the <li> list for one app column, or None if nothing is missing."""
    existing = dict((h, t) for h, t in LI_HREF.findall(block))
    wanted = [h for h, _ in APP_ORDER]
    if not any(h in existing for h in wanted):
        return None                      # not the app column
    if all(h in existing for h in wanted):
        return None                      # already complete
    # Keep whatever text the page already uses; only fill the gaps.
    out = [LI % (h, existing.get(h, default).strip())
           for h, default in APP_ORDER]
    sep = "\n" + indent
    return sep + sep.join(out) + "\n" + indent[:-2]


def main():
    changed = 0
    for path in html_files():
        with open(path, encoding="utf-8") as fh:
            doc = fh.read()
        start = doc.find("<footer")
        if start < 0:
            continue
        head, foot = doc[:start], doc[start:]

        def fix(m):
            inner = m.group(2)
            found = re.search(r"\n([ \t]*)<li", inner)
            indent = found.group(1) if found else "            "
            new = rebuild(inner, indent) or add_legal(inner, indent)
            return m.group(1) + new + m.group(3) if new else m.group(0)

        new_foot = UL.sub(fix, foot)
        if new_foot != foot:
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(head + new_foot)
            changed += 1

    print("footer columns completed on %d pages" % changed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
