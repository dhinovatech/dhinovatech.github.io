#!/usr/bin/env python3
"""
Run every site builder, in the only order that is safe.

The builders fall into three layers, and running them out of order silently
undoes work:

  1. Page generators  - write whole pages from a strings/facts file.
     Anything a later layer injects into these pages is destroyed if a
     generator runs afterwards, so they go first.
  2. Section injectors - replace one delimited region inside existing pages.
  3. Cross-cutting passes - touch every page: image tags, UX landmarks, the
     SEO head block, then analytics/consent.

build-consent.py runs last on purpose. It owns the very top of <head>, and it
is the one thing that must not be reordered behind anything that rewrites the
head, or analytics ends up ahead of its own consent defaults.

Run:  python tools/build-all.py
      python tools/build-all.py --check    (fail if anything changed - for CI)
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STEPS = [
    # 1. generators
    ("build-glowcompare-windows.py", "regenerate the Microsoft Store tree"),
    ("build-privacy.py",             "regenerate policy pages"),
    # 2. section injectors
    ("build-ai-chat-section.py",     "GlowCompare AI chat section"),
    ("build-footer.py",              "footer app + legal columns"),
    ("build-contact.py",             "contact form (off until an endpoint is set)"),
    # 3. cross-cutting
    ("build-images.py",              "optimise images, rewrite <img>"),
    ("build-ux.py",                  "skip links, landmarks, install bar"),
    ("build-seo.py",                 "canonical, hreflang, schema, sitemap"),
    ("build-consent.py",             "analytics behind Consent Mode v2"),
]


def dirty():
    out = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                         capture_output=True, text=True).stdout
    return [l for l in out.splitlines() if l.strip()]


def main():
    check = "--check" in sys.argv
    before = dirty() if check else None

    for script, why in STEPS:
        path = os.path.join(ROOT, "tools", script)
        if not os.path.exists(path):
            print("!! missing: tools/%s" % script)
            return 1
        print("\n=== %s  (%s)" % (script, why))
        r = subprocess.run([sys.executable, path], cwd=ROOT)
        if r.returncode != 0:
            print("!! %s failed with exit code %d" % (script, r.returncode))
            return r.returncode

    if check:
        after = dirty()
        if after != before:
            print("\n!! working tree changed - generated output is stale.")
            print("   Run tools/build-all.py and commit the result.")
            for line in sorted(set(after) - set(before))[:40]:
                print("   %s" % line)
            return 1
        print("\nAll generated output is up to date.")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
