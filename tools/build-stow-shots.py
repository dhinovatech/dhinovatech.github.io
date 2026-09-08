#!/usr/bin/env python3
"""
Build the Stow imagery the landing pages need: the localised product
screenshots, and the social card.

The Stow application repository keeps one set of Microsoft Store screenshots
per store locale, captured from the real running app. Those are 1920x1080 PNGs
of 130-290 KB each, which is far too heavy to put on a page 23 times over, so
this script picks the seven that carry the marketing weight - one for the hero
and six for the gallery below it - converts them to WebP at the width the page
actually renders them at, and writes them to
assets/images/stow/<site locale>/<slug>.webp.

Only seven are used, and which seven is a deliberate choice, not a crop of the
first seven:

  * they are populated, not empty states - "No backup jobs configured yet" and
    "No debris or clutter found" prove nothing to somebody who has not
    installed the app yet;
  * none of them shows personal content. The store set also contains the
    folder browser (real paths from the developer's own machine) and the face
    grouping screen (photographs of the developer's family). Both are already
    public on the store listing, but a page behind paid advertising pushes them
    much harder than a store listing does, so they are left out here.

The source repository is not a dependency of this site: if it is not checked
out next to it, this script prints what it would have done and exits 0, and
build-stow.py falls back to rendering the gallery from whatever is already
committed under assets/images/stow/.

It also draws assets/images/_src/stow-og.png, the 1200x630 card link previews
use. That has to be a wide image with legible text in it: the app icon on its
own was being sent as a 512x512 square under summary_large_image, which every
scraper either letterboxes or rejects. build-images.py compresses it from _src
like any other source image.

Run:  python tools/build-stow-shots.py
Idempotent: every WebP and the card are re-derived from source on each run.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "images", "stow")

# The application repository, as checked out beside this one. Override with
# STOW_APP_REPO when it lives somewhere else.
APP = os.environ.get(
    "STOW_APP_REPO",
    os.path.join(os.path.dirname(ROOT), "..", "offlineAIFolderOrganizer",
                 "offlineAIFolderOrganizer"))

STORE = os.path.join(APP, "Storelistings", "Screenshots")
EXTRA = os.path.join(APP, "ExtraScreenshots")

# Site locale -> store listing locale directory. Only nb differs; the Microsoft
# Store files Norwegian under the bare "no" macrolanguage code while the site
# uses nb, which is what hreflang wants.
LOCALES = {
    "en": "en-us", "es": "es", "fr": "fr", "de": "de", "it": "it",
    "pt": "pt", "nl": "nl", "pl": "pl", "cs": "cs", "hu": "hu",
    "da": "da", "sv": "sv", "nb": "no", "fi": "fi", "ru": "ru",
    "uk": "uk", "tr": "tr", "ja": "ja", "ko": "ko", "zh": "zh",
    "th": "th", "ar": "ar", "he": "he",
}

# slug, source directory, source file. Order is the order the gallery shows.
SHOTS = [
    ("home",       STORE, "DesktopScreenshot2.png"),   # the hero
    ("find",       STORE, "DesktopScreenshot5.png"),
    ("space",      STORE, "DesktopScreenshot6.png"),
    ("duplicates", STORE, "DesktopScreenshot9.png"),
    ("undo",       STORE, "DesktopScreenshot8.png"),
    ("photos",     EXTRA, "DesktopScreenshot11.png"),
    ("privacy",    STORE, "DesktopScreenshot10.png"),
]

# The gallery renders at 560 CSS px in the two-column desktop grid and full
# width on a phone. 1100 covers both, including a 2x phone, in one file -
# shipping a second srcset width would double 161 files to save a few KB on a
# lazy-loaded image nobody has scrolled to yet.
WIDTH = 1100
QUALITY = 72


def convert(src, dst):
    im = Image.open(src).convert("RGB")
    if im.width > WIDTH:
        h = round(im.height * WIDTH / float(im.width))
        im = im.resize((WIDTH, h), Image.LANCZOS)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im.save(dst, "WEBP", quality=QUALITY, method=6)
    return im.size, os.path.getsize(dst)


# ---------------------------------------------------------------- social card

SRC_IMG = os.path.join(ROOT, "assets", "images", "_src")
CARD = (1200, 630)
INK = "#e8ecf4"
MUTED = "#94a3b8"
AMBER = "#ffb634"          # the accent the Stow application itself uses
BG_TOP = (10, 14, 24)
BG_BOTTOM = (18, 24, 40)


def font(name, size):
    for candidate in (name, os.path.join("C:\\Windows\\Fonts", name)):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def build_og():
    card = Image.new("RGB", CARD, BG_TOP)
    draw = ImageDraw.Draw(card)

    # Vertical wash, so the card is not a flat rectangle in a timeline.
    for y in range(CARD[1]):
        t = y / float(CARD[1] - 1)
        draw.line([(0, y), (CARD[0], y)],
                  fill=tuple(round(a + (b - a) * t) for a, b in zip(BG_TOP, BG_BOTTOM)))

    icon_src = os.path.join(SRC_IMG, "stow-icon.png")
    if os.path.exists(icon_src):
        side = 260
        icon = Image.open(icon_src).convert("RGBA").resize((side, side), Image.LANCZOS)
        # Round the corners the way Windows renders an app icon.
        mask = Image.new("L", (side * 4, side * 4), 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            [0, 0, side * 4 - 1, side * 4 - 1], radius=side * 4 // 5, fill=255)
        icon.putalpha(mask.resize((side, side), Image.LANCZOS))
        card.paste(icon, (86, (CARD[1] - side) // 2), icon)

    x = 86 + 260 + 64
    draw.text((x, 168), "Stow", font=font("segoeuib.ttf", 92), fill=INK)
    draw.text((x, 278), "Photo & file organizer for Windows",
              font=font("segoeui.ttf", 38), fill=MUTED)
    # Shrink the claim line until it clears the right edge rather than
    # trusting one hand-measured size: the fallback bitmap font, on a machine
    # without Segoe, meters completely differently.
    claims = "100% offline  ·  preview before it moves  ·  1-click undo"
    for size in range(30, 17, -1):
        f = font("segoeuib.ttf", size)
        if draw.textlength(claims, font=f) <= CARD[0] - x - 86:
            break
    draw.text((x, 336), claims, font=f, fill=AMBER)

    # Microsoft Store strip along the bottom of the text column.
    pill = font("segoeui.ttf", 27)
    draw.rounded_rectangle([x, 404, x + 348, 462], radius=29,
                           fill=(255, 182, 52, 255))
    draw.text((x + 30, 419), "Microsoft Store", font=font("segoeuib.ttf", 28),
              fill=(24, 18, 6))
    draw.text((x + 372, 421), "Windows 10 & 11", font=pill, fill=MUTED)

    out = os.path.join(SRC_IMG, "stow-og.png")
    os.makedirs(SRC_IMG, exist_ok=True)
    card.save(out, "PNG", optimize=True)
    print("  social card -> %s (%dx%d)"
          % (os.path.relpath(out, ROOT), CARD[0], CARD[1]))


def main():
    build_og()
    if not os.path.isdir(STORE):
        print("  Stow application repo not found at:\n    %s" % os.path.abspath(APP))
        print("  Leaving assets/images/stow/ as committed. Set STOW_APP_REPO to rebuild.")
        return 0

    total = missing = 0
    dims = None
    for code, store_loc in LOCALES.items():
        for slug, base, fname in SHOTS:
            src = os.path.join(base, store_loc, fname)
            if not os.path.exists(src):
                # Fall back to the store's own "default" locale, then English.
                for alt in (os.path.join(base, "default", fname),
                            os.path.join(base, "en-us", fname)):
                    if os.path.exists(alt):
                        src = alt
                        break
                else:
                    print("  !! missing: %s/%s" % (store_loc, fname))
                    missing += 1
                    continue
            dst = os.path.join(OUT, code, slug + ".webp")
            dims, size = convert(src, dst)
            total += size

    print("  %d locales x %d shots -> %s" % (len(LOCALES), len(SHOTS),
                                             os.path.relpath(OUT, ROOT)))
    print("  intrinsic size %dx%d, %.1f MB total%s"
          % (dims[0], dims[1], total / 1048576.0,
             "" if not missing else ", %d missing" % missing))
    return 0


if __name__ == "__main__":
    sys.exit(main())
