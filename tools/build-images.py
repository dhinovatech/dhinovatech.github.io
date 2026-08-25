#!/usr/bin/env python3
"""
Dhinovatech image pipeline.

Every content image on the site was shipping as an unoptimised export - the
512x512 GlowCompare icon alone was 723 KB and loads in the navbar of all 168
pages at 20 CSS px. This script fixes that in one pass:

  * downscales anything far larger than the biggest size it is ever rendered at
  * writes a WebP sibling for every content image (what the pages actually load)
  * re-compresses the original PNG/JPEG, because og:image is still read by
    social crawlers that do not all handle WebP
  * records intrinsic dimensions in tools/image-sizes.json, then rewrites every
    <img> on the site to point at the WebP and to carry width/height, which is
    what actually stops the layout shift

Only <img src> is rewritten. og:image, twitter:image and JSON-LD image/logo
keep pointing at the PNG/JPEG on purpose: link-preview scrapers are far behind
browsers on WebP, and a broken share card costs more than the bytes save.

Run:  python tools/build-images.py
Idempotent: it always re-derives from assets/images/_src/, which holds the
untouched originals, so running it twice cannot re-compress a compressed file.
"""
import json
import os
import re
import shutil
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "assets", "images")
SKIP_DIRS = {".git", "_src", "tools"}
SRC = os.path.join(IMG, "_src")
MANIFEST = os.path.join(ROOT, "tools", "image-sizes.json")

# max_dim: longest edge to keep. Derived from the largest CSS size each image is
# ever rendered at, times 3 for hi-DPI. None = keep native size.
# webp: emit a WebP sibling (skip for favicons and PWA manifest icons, which
# have to stay PNG).
# keep: the original PNG/JPEG survives alongside the WebP because something
# outside a browser still fetches it - og:image / twitter:image, a JSON-LD
# image or logo, or the webmanifest. Everything else is WebP-only; shipping an
# unread PNG fallback next to it just doubles the repo for nothing.
SPEC = {
    # brand - navbar caps the logo at 160x26 CSS px
    "LogoWithText.png":                   dict(max_dim=512,  webp=True,  q=90, keep=True),
    "BiggerLogo.png":                     dict(max_dim=900,  webp=True,  q=86, keep=False),
    "LogoOnlyImage.png":                  dict(max_dim=256,  webp=False),  # webmanifest
    "favicon.png":                        dict(max_dim=256,  webp=False),

    # app icons - largest render is the 90px app card, plus the 42px install bar
    "aes-vault-icon.png":                 dict(max_dim=256,  webp=True,  q=90, keep=True),
    "glowcompare-icon.png":               dict(max_dim=256,  webp=True,  q=90, keep=True),
    "milk-calendar-icon.png":             dict(max_dim=256,  webp=True,  q=90, keep=True),
    "mortgage-emi-icon.png":              dict(max_dim=256,  webp=True,  q=90, keep=True),
    "notelock-icon.png":                  dict(max_dim=256,  webp=True,  q=90, keep=True),
    "slouch-guard-icon.png":              dict(max_dim=256,  webp=True,  q=90, keep=True),

    # hero / preview art. og:image wants >=1200px on the long edge, so the
    # JPEG fallback is not downscaled below that.
    "dhinovatech-hero.jpg":               dict(max_dim=1376, webp=True,  q=82, webp_dim=1200, keep=True),
    "glowcompare-slider-before.jpg":      dict(max_dim=1200, webp=True,  q=82, keep=False),
    "glowcompare-slider-after.jpg":       dict(max_dim=1200, webp=True,  q=82, keep=True),
    "milk-monthly-calendar-banner.jpg":   dict(max_dim=1200, webp=True,  q=82, keep=False),
    "milk-monthly-calendar-ui-preview.jpg": dict(max_dim=1200, webp=True, q=82, keep=True),
    "slouch-guard-ui-preview.jpg":        dict(max_dim=1200, webp=True,  q=82, keep=True),

    # store screenshots render at roughly 300 CSS px wide
    "glowcompare-screenshot-1.png":       dict(max_dim=592,  webp=True,  q=86, keep=False),
    "glowcompare-screenshot-2.png":       dict(max_dim=592,  webp=True,  q=86, keep=False),
    "glowcompare-screenshot-3.png":       dict(max_dim=592,  webp=True,  q=86, keep=False),
    "glowcompare-screenshot-4.png":       dict(max_dim=592,  webp=True,  q=86, keep=False),
    "glowcompare-screenshot-5.png":       dict(max_dim=592,  webp=True,  q=86, keep=False),
    "glowcompare-screenshot-6.png":       dict(max_dim=592,  webp=True,  q=86, keep=False),
}

# Referenced by nothing in the site, or superseded by a WebP sibling.
OBSOLETE = [
    "LogoTextOnly.png",             # unreferenced
    "slouch-guard-edge-glow.jpg",   # unreferenced
    "slouch-guard-ui-preview.png",  # duplicate of the .jpg, now served as .webp
]


def seed_sources():
    """Copy pristine originals into _src/ the first time we run."""
    os.makedirs(SRC, exist_ok=True)
    for name in SPEC:
        s = os.path.join(SRC, name)
        cur = os.path.join(IMG, name)
        if not os.path.exists(s) and os.path.exists(cur):
            shutil.copy2(cur, s)


def html_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.endswith(".html"):
                yield os.path.join(dirpath, fn)


IMG_TAG = re.compile(r"<img\b[^>]*>", re.I)
SRC_ATTR = re.compile(r'(\bsrc=")(/assets/images/([^"]+))(")')


def rewrite_html(sizes):
    """Point every <img> at the WebP build and give it intrinsic dimensions."""
    # name.ext -> name.webp, for every image that got a WebP sibling.
    webp = {}
    for name in sizes:
        if name.endswith(".webp"):
            for ext in (".png", ".jpg", ".jpeg"):
                webp[os.path.splitext(name)[0] + ext] = name
    # These originals are gone entirely; anything still pointing at them 404s.
    for name in ("slouch-guard-ui-preview.png",):
        webp.setdefault(name, os.path.splitext(name)[0] + ".webp")

    touched = 0
    for path in html_files():
        with open(path, encoding="utf-8") as fh:
            doc = fh.read()

        def fix(tag):
            m = SRC_ATTR.search(tag.group(0))
            if not m:
                return tag.group(0)
            out, cur = tag.group(0), m.group(3)
            new = webp.get(cur, cur)
            if new != cur:
                out = out.replace(m.group(2), "/assets/images/" + new, 1)
            dim = sizes.get(new)
            if dim and " width=" not in out and " height=" not in out:
                out = out[:-1].rstrip() + ' width="%d" height="%d">' % (dim[0], dim[1])
            return out

        new_doc = IMG_TAG.sub(fix, doc)
        if new_doc != doc:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(new_doc)
            touched += 1
    return touched


def fit(im, max_dim):
    if max_dim and max(im.size) > max_dim:
        r = max_dim / float(max(im.size))
        return im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    return im


def main():
    seed_sources()
    sizes, saved = {}, 0

    for name, spec in sorted(SPEC.items()):
        src = os.path.join(SRC, name)
        if not os.path.exists(src):
            print("  skip (no source): %s" % name)
            continue

        before = os.path.getsize(os.path.join(IMG, name)) if os.path.exists(os.path.join(IMG, name)) else 0
        im = Image.open(src)
        # Some files carry a misleading extension (slouch-guard-icon.png is a
        # JPEG); trust Pillow's sniffed format, not the name.
        is_jpeg = im.format == "JPEG" or name.lower().endswith((".jpg", ".jpeg"))

        base = fit(im, spec["max_dim"])
        out = os.path.join(IMG, name)
        if is_jpeg:
            base.convert("RGB").save(out, "JPEG", quality=spec.get("q", 82),
                                     optimize=True, progressive=True)
        else:
            base.convert("RGBA").save(out, "PNG", optimize=True)
        after = os.path.getsize(out)

        sizes[name] = list(base.size)

        if spec.get("webp"):
            wim = fit(im, spec.get("webp_dim") or spec["max_dim"])
            wname = os.path.splitext(name)[0] + ".webp"
            wpath = os.path.join(IMG, wname)
            wim.save(wpath, "WEBP", quality=spec.get("q", 85), method=6)
            sizes[wname] = list(wim.size)
            after += os.path.getsize(wpath)
            if not spec.get("keep", True):
                after -= os.path.getsize(out)
                os.remove(out)
                sizes.pop(name, None)

        saved += before - after
        print("  %-40s %6d KB -> %6d KB" % (name, before // 1024, after // 1024))

    for name in OBSOLETE:
        p = os.path.join(IMG, name)
        if os.path.exists(p):
            saved += os.path.getsize(p)
            os.remove(p)
            print("  removed unused: %s" % name)

    # Favicons are copied, not generated; record their size for completeness.
    for extra in ("favicon.ico",):
        p = os.path.join(IMG, extra)
        if os.path.exists(p):
            try:
                sizes[extra] = list(Image.open(p).size)
            except Exception:
                pass

    with open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump(sizes, fh, indent=1, sort_keys=True)

    touched = rewrite_html(sizes)
    print("\n  rewrote <img> src + width/height in %d pages" % touched)
    print("  wrote %s (%d entries)" % (os.path.relpath(MANIFEST, ROOT), len(sizes)))
    print("  net saving: %.1f MB" % (saved / 1048576.0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
