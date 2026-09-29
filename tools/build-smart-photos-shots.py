#!/usr/bin/env python3
"""
Build the Smart Photos imagery and listing text the landing pages need.

The Smart Photos application repository keeps one set of Microsoft Store
slides per store locale (StoreScreenshotsV2/<store locale>/Screenshots), each
a 3840x2160 PNG of 1-5 MB with the headline already translated into that
language, plus a Partner Center export of the listing text next to it. This
script:

  * converts the ten slides to WebP at the width the page renders them at and
    writes them to assets/images/smart-photos/<site locale>/<slug>.webp;
  * copies the listing text the page reuses (title, short description, the
    description paragraphs, the twenty feature bullets and the ten slide
    captions) into tools/smart-photos-listing.json, so the page speaks with
    the same, already-translated voice as the store listing;
  * copies the app icon into assets/images/_src/smart-photos-icon.png and draws
    the 1200x630 social card assets/images/_src/smart-photos-og.png, which
    build-images.py then compresses like any other source image.

The slides are marketing composites built from stock photography, not captures
of anyone's own library, so all ten are safe to show.

The source repository is not a dependency of this site: if it is not checked
out, this script says so and exits 0, and build-smart-photos.py renders from
what is already committed.

Run:  python tools/build-smart-photos-shots.py
Idempotent: every output is re-derived from source on each run.
"""
import csv
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "images", "smart-photos")
LISTING = os.path.join(ROOT, "tools", "smart-photos-listing.json")
SRC_IMG = os.path.join(ROOT, "assets", "images", "_src")

# The application repository. Override with SMART_PHOTOS_REPO.
APP = os.environ.get("SMART_PHOTOS_REPO",
                     os.path.join("C:\\", "Drive", "git", "SmartPhotos", "SmartPhotos"))
STORE = os.path.join(APP, "StoreScreenshotsV2")
ICON_SRC = os.path.join(APP, "src", "SmartPhotos.App", "Assets", "BrandMark.png")

# Site locale -> store listing locale directory.
LOCALES = {
    "en": "en-us", "es": "es-es", "fr": "fr-fr", "de": "de-de", "it": "it-it",
    "pt": "pt-br", "nl": "nl-nl", "pl": "pl-pl", "cs": "cs-cz", "da": "da-dk",
    "sv": "sv-se", "nb": "nb-no", "fi": "fi-fi", "tr": "tr-tr", "ja": "ja-jp",
    "ko": "ko-kr", "zh": "zh-cn", "zh-tw": "zh-tw", "th": "th-th", "vi": "vi-vn",
    "id": "id-id", "hi": "hi-in", "ta": "ta-in", "ar": "ar-sa", "he": "he-il",
}

# slug per store slide number. Slide 1 is the hero; the rest form the gallery.
SLIDES = ["hero", "search", "people", "switch", "map", "memories",
          "explore", "albums", "cleanup", "privacy"]

WIDTH = 1200
QUALITY = 74


def convert(src, dst):
    im = Image.open(src).convert("RGB")
    if im.width > WIDTH:
        im = im.resize((WIDTH, round(im.height * WIDTH / float(im.width))), Image.LANCZOS)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im.save(dst, "WEBP", quality=QUALITY, method=6)
    return im.size, os.path.getsize(dst)


def read_listing(store_loc):
    path = os.path.join(STORE, store_loc, "store-listings-export.csv")
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    col = rows[0].index(store_loc)
    val = dict((r[0], r[col].replace("\r\n", "\n")) for r in rows[1:] if len(r) > col)
    return {
        "title": val["Title"],
        "short": val["ShortDescription"],
        "description": [p.strip() for p in val["Description"].split("\n\n") if p.strip()],
        "features": [val["Feature%d" % i] for i in range(1, 21) if val.get("Feature%d" % i)],
        "captions": [val["DesktopScreenshotCaption%d" % i] for i in range(1, 11)],
    }


# ---------------------------------------------------------------- social card

CARD = (1200, 630)
INK = "#eef6f2"
MUTED = "#a7c4b8"
MINT = "#5fd3ae"
BG_TOP = (9, 44, 40)
BG_BOTTOM = (10, 18, 30)


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
    for y in range(CARD[1]):
        t = y / float(CARD[1] - 1)
        draw.line([(0, y), (CARD[0], y)],
                  fill=tuple(round(a + (b - a) * t) for a, b in zip(BG_TOP, BG_BOTTOM)))

    icon_src = os.path.join(SRC_IMG, "smart-photos-icon.png")
    if os.path.exists(icon_src):
        side = 250
        icon = Image.open(icon_src).convert("RGBA").resize((side, side), Image.LANCZOS)
        card.paste(icon, (80, (CARD[1] - side) // 2), icon)

    x = 80 + 250 + 60
    draw.text((x, 150), "Smart Photos", font=font("segoeuib.ttf", 84), fill=INK)
    draw.text((x, 256), "Private Google Photos alternative for Windows",
              font=font("segoeui.ttf", 32), fill=MUTED)
    claims = "AI search  ·  faces & places  ·  100% on your PC"
    for size in range(30, 17, -1):
        f = font("segoeuib.ttf", size)
        if draw.textlength(claims, font=f) <= CARD[0] - x - 60:
            break
    draw.text((x, 314), claims, font=f, fill=MINT)

    draw.rounded_rectangle([x, 392, x + 348, 450], radius=29, fill=(95, 211, 174))
    draw.text((x + 30, 407), "Microsoft Store", font=font("segoeuib.ttf", 28), fill=(6, 30, 24))
    draw.text((x + 372, 409), "Windows 10 & 11", font=font("segoeui.ttf", 27), fill=MUTED)

    out = os.path.join(SRC_IMG, "smart-photos-og.png")
    card.save(out, "PNG", optimize=True)
    print("  social card -> %s" % os.path.relpath(out, ROOT))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if not os.path.isdir(STORE):
        print("  Smart Photos repo not found at:\n    %s" % os.path.abspath(APP))
        print("  Leaving committed images and listing text as they are.")
        return 0

    os.makedirs(SRC_IMG, exist_ok=True)
    if os.path.exists(ICON_SRC):
        Image.open(ICON_SRC).save(os.path.join(SRC_IMG, "smart-photos-icon.png"))
    build_og()

    listing = {}
    total = 0
    dims = None
    for code, store_loc in LOCALES.items():
        listing[code] = read_listing(store_loc)
        for i, slug in enumerate(SLIDES, 1):
            src = os.path.join(STORE, store_loc, "Screenshots", "DesktopScreenshot%d.png" % i)
            if not os.path.exists(src):
                src = os.path.join(STORE, "en-us", "Screenshots", "DesktopScreenshot%d.png" % i)
            dims, size = convert(src, os.path.join(OUT, code, slug + ".webp"))
            total += size

    with open(LISTING, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(listing, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    print("  %d locales x %d slides -> %s (%dx%d, %.1f MB)"
          % (len(LOCALES), len(SLIDES), os.path.relpath(OUT, ROOT),
             dims[0], dims[1], total / 1048576.0))
    print("  listing text -> %s" % os.path.relpath(LISTING, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
