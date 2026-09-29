#!/usr/bin/env python3
"""
Put Smart Photos, with its language submenu, at the top of the "Our Apps"
menu on every page.

The navbar is written separately by each generator and by hand on the older
pages, so there is no single template to add a new app to. This pass inserts
one entry as the first item of every `aria-labelledby="appsDropdown"` menu:
the same "N Languages" submenu Stow and Nudge carry, listing every Smart
Photos locale from tools/build-smart-photos.py, so the list cannot drift
from the pages that actually exist. The Smart Photos tree writes its own
menu and is left alone.

The entry sits between BEGIN/END markers and is replaced wholesale on each
run, so adding a locale to the Smart Photos builder updates every menu.

Run it after the page generators - build-all.py does - or a regenerated page
loses the entry until the next run.

Run:  python tools/build-nav-apps.py
Idempotent: a menu that already carries the current entry is not rewritten.
"""
import html
import importlib.util
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", "tools", "_src", "smart-photos"}

_spec = importlib.util.spec_from_file_location(
    "build_smart_photos", os.path.join(ROOT, "tools", "build-smart-photos.py"))
SP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(SP)

BEGIN = "<!-- BEGIN Smart Photos menu -->"
END = "<!-- END Smart Photos menu -->"

MENU_OPEN = re.compile(r'<ul[^>]*aria-labelledby="appsDropdown"[^>]*>')
BLOCK = re.compile(r'\n?[ \t]*' + re.escape(BEGIN) + r'.*?' + re.escape(END), re.S)
# The plain one-line entry earlier versions of this script inserted.
LEGACY = re.compile(r'\n?[ \t]*<li><a class="dropdown-item py-2" href="/smart-photos/">.*?</a></li>')


def entry():
    langs = SP.built_langs()
    items = "\n".join(
        '                  <li><a class="dropdown-item py-1 small" href="%s">'
        '<i class="bi bi-globe text-success me-2" aria-hidden="true"></i>%s</a></li>'
        % (SP.url_for(code), html.escape(label))
        for code, label, _d, _hl, _og in langs)
    return """
              %s
              <li class="dropdown-submenu position-relative">
                <a class="dropdown-item py-2 d-flex align-items-center justify-content-between" href="/smart-photos/">
                  <span><img src="/assets/images/smart-photos-icon.webp" alt="Smart Photos Icon" style="width: 20px; height: 20px; border-radius: 5px; object-fit: contain;" class="me-2" decoding="async" width="256" height="256">Smart Photos</span>
                  <span class="badge bg-success-subtle text-success border border-success-subtle rounded-pill ms-2 extra-small submenu-toggle-btn" role="button" title="View %d Languages">%d Languages <i class="bi bi-chevron-down ms-1" aria-hidden="true"></i></span>
                </a>
                <ul class="dropdown-menu dropdown-menu-dark border-secondary shadow-lg scrollable-menu" style="max-height: 360px; overflow-y: auto;">
%s
                </ul>
              </li>
              %s""" % (BEGIN, len(langs), len(langs), items, END)


def html_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in sorted(filenames):
            if fn.endswith(".html"):
                yield os.path.join(dirpath, fn)


def main():
    new_entry = entry()
    changed = 0
    for path in html_files():
        with open(path, encoding="utf-8") as fh:
            doc = fh.read()
        m = MENU_OPEN.search(doc)
        if not m:
            continue
        head, rest = doc[:m.end()], doc[m.end():]
        rest = BLOCK.sub("", rest, count=1)
        rest = LEGACY.sub("", rest, count=1)
        out = head + new_entry + rest
        if out != doc:
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(out)
            changed += 1
    print("Smart Photos menu written on %d pages" % changed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
