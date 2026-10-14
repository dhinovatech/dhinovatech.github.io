#!/usr/bin/env python3
"""
Build the KeepOne imagery and listing text the landing pages need.

The KeepOne application repository keeps a complete Microsoft Store listing
kit per store language (StoreScreenshotsV2/<store locale>): ten 3840x2160
slides whose headline is already written in that language over a real capture
of the app in that language, the upload CSV, and - under _source/strings -
the words on every slide and the listing text as structured JSON. This script:

  * converts the slides the page shows to WebP at the width it renders them
    at and writes them to assets/images/keepone/<site locale>/<slug>.webp;
  * copies the text the page reuses into tools/keepone-listing.json: the short
    description, description, feature bullets and slide captions from the
    upload CSV (what the Store actually shows), the localized title written
    from each market's measured search queries (strings file, listing.title -
    the Store still shows the English one until the name is reserved, but a
    web page can use it now), and the hero lines, the eight overview tiles and
    the eight slide headlines with their bullets;
  * copies the app icon to assets/images/_src/keepone-icon.png and draws the
    1200x630 social card assets/images/_src/keepone-og.png; build-images.py
    compresses both like any other source image.

Every picture is the app itself running on a demo library of royalty-free
photos, with folder and file names written for the purpose, so all of them
are safe to show.

The source repository is not a dependency of this site: if it is not checked
out, this script says so and exits 0, and build-keepone.py renders from what
is already committed.

Run:  python tools/build-keepone-shots.py
Idempotent: every output is re-derived from source on each run.
"""
import csv
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "images", "keepone")
LISTING = os.path.join(ROOT, "tools", "keepone-listing.json")
SRC_IMG = os.path.join(ROOT, "assets", "images", "_src")

# The application repository. Override with KEEPONE_REPO.
APP = os.environ.get("KEEPONE_REPO",
                     os.path.join("C:\\", "Drive", "git", "KeepOne", "KeepOne", "KeepOne"))
STORE = os.path.join(APP, "StoreScreenshotsV2")
STRINGS = os.path.join(STORE, "_source", "strings")
ICON_SRC = os.path.join(APP, "tools", "make-assets", "KeepOne-icon.png")
LOC = os.path.join(APP, "loc")
# Site locale -> the app's own UI strings file, where the name differs.
LOC_FILE = {"en": "en-US", "zh": "zh-Hans"}
# The three similar-photo strictness levels, in the app's own words (Settings).
STRICTNESS = ["Settings_SensitivityVeryStrict", "Settings_SensitivityStrict",
              "Settings_SensitivityLoose"]

# Site locale -> store listing locale directory (the codes Partner Center
# exports). Norwegian is filed under "no" in the kit and served as nb here.
LOCALES = {
    "en": "en-us", "ar": "ar", "cs": "cs", "da": "da", "de": "de", "es": "es",
    "fi": "fi", "fr": "fr", "he": "he", "hu": "hu", "it": "it", "ja": "ja",
    "ko": "ko", "nl": "nl", "nb": "no", "pl": "pl", "pt": "pt", "ru": "ru",
    "sv": "sv", "th": "th", "tr": "tr", "uk": "uk", "zh": "zh",
}

# slug -> store slide number. Slide 1 is the hero and slides 3-10 the gallery.
# Slide 2 is eight text tiles on a plain background; the page sets the same
# tiles as real text, so the picture is not shipped.
SLIDES = [("hero", 1), ("similar", 3), ("exact", 4), ("folders", 5),
          ("videos", 6), ("confirm", 7), ("undo", 8), ("scan", 9),
          ("private", 10)]

WIDTH = 1200
QUALITY = 74


def convert(src, dst):
    im = Image.open(src).convert("RGB")
    if im.width > WIDTH:
        im = im.resize((WIDTH, round(im.height * WIDTH / float(im.width))), Image.LANCZOS)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im.save(dst, "WEBP", quality=QUALITY, method=6)
    return im.size, os.path.getsize(dst)


def read_ui(code):
    """The app's own UI text for `code`, as a key -> value dict."""
    out = {}
    path = os.path.join(LOC, LOC_FILE.get(code, code) + ".txt")
    with open(path, encoding="utf-8-sig") as fh:
        for line in fh:
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.rstrip("\n").split("=", 1)
                out[k.strip()] = v.strip()
    return out


def read_listing(store_loc):
    path = os.path.join(STORE, store_loc, "store-listings-export.csv")
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    col = rows[0].index(store_loc)
    val = dict((r[0], r[col].replace("\r\n", "\n")) for r in rows[1:] if len(r) > col)
    with open(os.path.join(STRINGS, store_loc + ".json"), encoding="utf-8") as fh:
        src = json.load(fh)
    slides = src["slides"]
    hero = slides["hero"]
    return {
        "title": src["listing"]["title"],
        "store_title": val["Title"],
        "short": val["ShortDescription"],
        "tagline": hero["tagline"],
        "line1": hero["line1"],
        "line2": hero["line2"],
        "chips": hero["chips"],
        "free": slides["footer"],
        "overview": slides["overview"],
        "shots": slides["shots"],
        "description": [p.strip() for p in val["Description"].split("\n\n") if p.strip()],
        "features": [val["Feature%d" % i] for i in range(1, 21) if val.get("Feature%d" % i)],
        "captions": [val["DesktopScreenshotCaption%d" % i] for i in range(1, 11)],
    }


# ---------------------------------------------------------------- social card

CARD = (1200, 630)
INK = "#f1f6ff"
MUTED = "#a9bde6"
CYAN = "#22d3ee"            # the glow on the store slides
SUN = (255, 209, 102)       # the FREE DOWNLOAD button on slide 1
BG_TOP = (30, 107, 255)
BG_BOTTOM = (6, 14, 52)


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

    if os.path.exists(ICON_SRC):
        side = 250
        icon = Image.open(ICON_SRC).convert("RGB").resize((side, side), Image.LANCZOS)
        mask = Image.new("L", (side, side), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, side - 1, side - 1], radius=56, fill=255)
        card.paste(icon, (80, (CARD[1] - side) // 2), mask)

    x = 80 + 250 + 60
    draw.text((x, 150), "KeepOne", font=font("segoeuib.ttf", 84), fill=INK)
    draw.text((x, 256), "Duplicate photo & file finder for Windows",
              font=font("segoeui.ttf", 32), fill=MUTED)
    claims = "Byte-for-byte check  ·  Recycle Bin  ·  Undo any cleanup"
    for size in range(30, 17, -1):
        f = font("segoeuib.ttf", size)
        if draw.textlength(claims, font=f) <= CARD[0] - x - 60:
            break
    draw.text((x, 314), claims, font=f, fill=CYAN)

    draw.rounded_rectangle([x, 392, x + 300, 450], radius=29, fill=SUN)
    draw.text((x + 30, 407), "Free download", font=font("segoeuib.ttf", 28), fill=(12, 20, 52))
    draw.text((x + 324, 409), "Microsoft Store", font=font("segoeui.ttf", 27), fill=MUTED)

    out = os.path.join(SRC_IMG, "keepone-og.png")
    card.save(out, "PNG", optimize=True)
    print("  social card -> %s" % os.path.relpath(out, ROOT))


def copy_icon():
    if not os.path.exists(ICON_SRC):
        return
    out = os.path.join(SRC_IMG, "keepone-icon.png")
    Image.open(ICON_SRC).convert("RGB").resize((512, 512), Image.LANCZOS).save(out, "PNG", optimize=True)
    print("  icon -> %s" % os.path.relpath(out, ROOT))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if not os.path.isdir(STORE):
        print("  KeepOne repo not found at:\n    %s" % os.path.abspath(APP))
        print("  Leaving committed images and listing text as they are.")
        return 0

    os.makedirs(SRC_IMG, exist_ok=True)
    copy_icon()
    build_og()

    listing = {}
    total = 0
    dims = None
    for code, store_loc in LOCALES.items():
        listing[code] = read_listing(store_loc)
        ui = read_ui(code)
        listing[code]["strictness"] = [ui[k] for k in STRICTNESS]
        for slug, n in SLIDES:
            src = os.path.join(STORE, store_loc, "Screenshots", "DesktopScreenshot%d.png" % n)
            if not os.path.exists(src):
                src = os.path.join(STORE, "en-us", "Screenshots", "DesktopScreenshot%d.png" % n)
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
