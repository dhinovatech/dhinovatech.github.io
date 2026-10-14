#!/usr/bin/env python3
"""
Put Smart Photos and KeepOne, each with its language submenu, at the top of
the "Our Apps" menu on every page.

The navbar is written separately by each generator and by hand on the older
pages, so there is no single template to add a new app to. This pass inserts
one entry as the first item of every `aria-labelledby="appsDropdown"` menu:
the same "N Languages" submenu Stow and Nudge carry, listing every Smart
Photos locale from tools/build-smart-photos.py, so the list cannot drift
from the pages that actually exist. The Smart Photos tree writes its own
menu and is left alone.

KeepOne gets the same treatment, listed right after Smart Photos, from
tools/build-keepone.py; its own tree writes its own entry and is left alone.

Each entry sits between BEGIN/END markers and is replaced wholesale on each
run, so adding a locale to either builder updates every menu.

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
SKIP_DIRS = {".git", "tools", "_src"}


def _module(name, script):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "tools", script))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SP = _module("build_smart_photos", "build-smart-photos.py")
KO = _module("build_keepone", "build-keepone.py")

BEGIN = "<!-- BEGIN Smart Photos menu -->"
END = "<!-- END Smart Photos menu -->"
KO_BEGIN = "<!-- BEGIN KeepOne menu -->"
KO_END = "<!-- END KeepOne menu -->"

MENU_OPEN = re.compile(r'<ul[^>]*aria-labelledby="appsDropdown"[^>]*>')
BLOCK = re.compile(r'\n?[ \t]*' + re.escape(BEGIN) + r'.*?' + re.escape(END), re.S)
KO_BLOCK = re.compile(r'\n?[ \t]*' + re.escape(KO_BEGIN) + r'.*?' + re.escape(KO_END), re.S)
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


def keepone_entry():
    langs = KO.built_langs()
    items = "\n".join(
        '                  <li><a class="dropdown-item py-1 small" href="%s">'
        '<i class="bi bi-globe text-info me-2" aria-hidden="true"></i>%s</a></li>'
        % (KO.url_for(code), html.escape(label))
        for code, label, _d, _hl, _og in langs)
    return """
              %s
              <li class="dropdown-submenu position-relative">
                <a class="dropdown-item py-2 d-flex align-items-center justify-content-between" href="/KeepOne/">
                  <span><img src="/assets/images/keepone-icon.webp" alt="KeepOne Icon" style="width: 20px; height: 20px; border-radius: 5px; object-fit: cover;" class="me-2" decoding="async" width="256" height="256">KeepOne Duplicate Finder</span>
                  <span class="badge bg-info-subtle text-info border border-info-subtle rounded-pill ms-2 extra-small submenu-toggle-btn" role="button" title="View %d Languages">%d Languages <i class="bi bi-chevron-down ms-1" aria-hidden="true"></i></span>
                </a>
                <ul class="dropdown-menu dropdown-menu-dark border-secondary shadow-lg scrollable-menu" style="max-height: 360px; overflow-y: auto;">
%s
                </ul>
              </li>
              %s""" % (KO_BEGIN, len(langs), len(langs), items, KO_END)


def html_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in sorted(filenames):
            if fn.endswith(".html"):
                yield os.path.join(dirpath, fn)


def main():
    sp_entry, ko_entry = entry(), keepone_entry()
    changed = 0
    for path in html_files():
        top = os.path.relpath(path, ROOT).replace(os.sep, "/").split("/")[0]
        with open(path, encoding="utf-8") as fh:
            doc = fh.read()
        m = MENU_OPEN.search(doc)
        if not m:
            continue
        head, rest = doc[:m.end()], doc[m.end():]
        rest = BLOCK.sub("", rest, count=1)
        rest = KO_BLOCK.sub("", rest, count=1)
        rest = LEGACY.sub("", rest, count=1)
        # Each tree writes its own entry, with its own language submenu.
        new_entry = (("" if top == "smart-photos" else sp_entry) +
                     ("" if top == "KeepOne" else ko_entry))
        out = head + new_entry + rest
        if out != doc:
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(out)
            changed += 1
    print("Smart Photos and KeepOne menus written on %d pages" % changed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
