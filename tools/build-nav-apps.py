#!/usr/bin/env python3
"""
Put Smart Photos at the top of the "Our Apps" menu on every page.

The navbar is written separately by each generator and by hand on the older
pages, so there is no single template to add a new app to. This pass inserts
one entry as the first item of every `aria-labelledby="appsDropdown"` menu that
does not already link /smart-photos/. The Smart Photos tree writes its own
menu (with its language submenu) and is left alone.

Run it after the page generators - build-all.py does - or a regenerated page
loses the entry until the next run.

Run:  python tools/build-nav-apps.py
Idempotent: a menu that already links /smart-photos/ is not touched.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", "tools", "_src", "smart-photos"}

MENU = re.compile(r'(<ul[^>]*aria-labelledby="appsDropdown"[^>]*>)(.*?)(\n[ \t]*</ul>\s*</li>)', re.S)
ENTRY = ('\n              <li><a class="dropdown-item py-2" href="/smart-photos/">'
         '<img src="/assets/images/smart-photos-icon.webp" alt="Smart Photos Icon" '
         'style="width: 20px; height: 20px; border-radius: 5px; object-fit: contain;" '
         'class="me-2" decoding="async" width="256" height="256">Smart Photos</a></li>')


def html_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in sorted(filenames):
            if fn.endswith(".html"):
                yield os.path.join(dirpath, fn)


def main():
    changed = 0
    for path in html_files():
        with open(path, encoding="utf-8") as fh:
            doc = fh.read()
        m = MENU.search(doc)
        if not m or 'href="/smart-photos/"' in m.group(2):
            continue
        doc = doc[:m.end(1)] + ENTRY + doc[m.end(1):]
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(doc)
        changed += 1
    print("Smart Photos added to the Our Apps menu on %d pages" % changed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
