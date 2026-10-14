#!/usr/bin/env python3
"""
Build the Nudge imagery and listing text the landing pages need.

The Nudge application repository keeps a complete Microsoft Store listing kit
per store language (StoreScreenshotsV2/<store locale>): ten 3840x2160 slides
whose headline is already written in that language over a real capture of the
app in that language, the upload CSV, and - under _source/strings - the words
on every slide as structured JSON. This script:

  * converts the slides the page shows to WebP at the width it renders them
    at and writes them to assets/images/nudge/<site locale>/<slug>.webp;
  * copies the text the page reuses into tools/nudge-listing.json: the title,
    short description, description, feature bullets and slide captions from
    the upload CSV (what the Store actually shows), and the hero lines, the
    eight overview tiles and the eight slide headlines with their bullets from
    the strings file. The page then says the same thing as the store listing,
    in the same words, in every language;
  * draws the 1200x630 social card assets/images/_src/nudge-og.png, which
    build-images.py compresses like any other source image.

Every picture is the app itself running a demo journal written for the
purpose, so all of them are safe to show.

The source repository is not a dependency of this site: if it is not checked
out, this script says so and exits 0, and build-nudge.py renders from what is
already committed.

Run:  python tools/build-nudge-shots.py
Idempotent: every output is re-derived from source on each run.
"""
import csv
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "images", "nudge")
LISTING = os.path.join(ROOT, "tools", "nudge-listing.json")
SRC_IMG = os.path.join(ROOT, "assets", "images", "_src")

# The application repository. Override with NUDGE_REPO.
APP = os.environ.get("NUDGE_REPO",
                     os.path.join("C:\\", "Drive", "git", "NudgeOfflineDiary",
                                  "NudgeOfflineJournal", "NudgeOfflineJournal"))
STORE = os.path.join(APP, "StoreScreenshotsV2")
STRINGS = os.path.join(STORE, "_source", "strings")

# Site locale -> store listing locale directory. The site's codes predate the
# store kit and are kept so no published URL moves: /nudge/pt/ has always been
# Brazilian Portuguese (store pt-br) and /nudge/pt-pt/ European (store pt).
LOCALES = {
    "en": "en-us", "ar": "ar", "zh": "zh", "es": "es", "ja": "ja", "de": "de",
    "fr": "fr", "ko": "ko", "hi": "hi", "pt": "pt-br", "pt-pt": "pt", "id": "id",
    "ru": "ru", "tr": "tr", "it": "it", "nl": "nl", "pl": "pl", "th": "th",
    "fa": "fa", "sv": "sv", "vi": "vi", "bn": "bn", "yue": "zh-hk", "tl": "fil",
    "uk": "uk", "cs": "cs", "ro": "ro", "he": "he", "el": "el", "hu": "hu",
    "da": "da", "fi": "fi", "nb": "no", "te": "te", "mr": "mr", "ta": "ta",
    "gu": "gu", "ur": "ur", "pa": "pa", "ml": "ml", "kn": "kn", "jv": "jv",
    "sw": "sw", "ha": "ha", "yo": "yo", "my": "my", "am": "am", "kk": "kk",
    "sk": "sk", "ca": "ca",
}

# slug -> store slide number. Slide 1 is the hero and slides 3-10 the gallery.
# Slide 2 is eight text tiles on a plain background; the page sets the same
# tiles as real text, so the picture is not shipped.
SLIDES = [("hero", 1), ("companion", 3), ("private", 4), ("ask", 5),
          ("timeline", 6), ("insights", 7), ("journeys", 8), ("files", 9),
          ("languages", 10)]

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
    with open(os.path.join(STRINGS, store_loc + ".json"), encoding="utf-8") as fh:
        slides = json.load(fh)["slides"]
    hero = slides["hero"]
    return {
        "title": val["Title"],
        "short": val["ShortDescription"],
        "tagline": hero["tagline"],
        "line1": hero["line1"],
        "line2": hero["line2"],
        "chips": hero["chips"],
        "trial": slides["footer"],
        "overview": slides["overview"],
        "shots": slides["shots"],
        "description": [p.strip() for p in val["Description"].split("\n\n") if p.strip()],
        "features": [val["Feature%d" % i] for i in range(1, 21) if val.get("Feature%d" % i)],
        "captions": [val["DesktopScreenshotCaption%d" % i] for i in range(1, 11)],
    }


# ---------------------------------------------------------------- social card

CARD = (1200, 630)
INK = "#fbf3e6"
MUTED = "#cdb597"
GOLD = "#ffc978"            # the trial badge on the store slides
BG_TOP = (104, 72, 38)
BG_BOTTOM = (16, 12, 9)


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

    icon_src = os.path.join(SRC_IMG, "nudge-icon.png")
    if os.path.exists(icon_src):
        side = 250
        icon = Image.open(icon_src).convert("RGB").resize((side, side), Image.LANCZOS)
        mask = Image.new("L", (side, side), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, side - 1, side - 1], radius=56, fill=255)
        card.paste(icon, (80, (CARD[1] - side) // 2), mask)

    x = 80 + 250 + 60
    draw.text((x, 150), "Nudge", font=font("segoeuib.ttf", 84), fill=INK)
    draw.text((x, 256), "Private journal and diary for Windows",
              font=font("segoeui.ttf", 32), fill=MUTED)
    claims = "Offline AI companion  ·  Windows Hello lock  ·  Markdown files"
    for size in range(30, 17, -1):
        f = font("segoeuib.ttf", size)
        if draw.textlength(claims, font=f) <= CARD[0] - x - 60:
            break
    draw.text((x, 314), claims, font=f, fill=GOLD)

    draw.rounded_rectangle([x, 392, x + 348, 450], radius=29, fill=(255, 201, 120))
    draw.text((x + 30, 407), "Microsoft Store", font=font("segoeuib.ttf", 28), fill=(42, 26, 8))
    draw.text((x + 372, 409), "Windows 10 & 11", font=font("segoeui.ttf", 27), fill=MUTED)

    out = os.path.join(SRC_IMG, "nudge-og.png")
    card.save(out, "PNG", optimize=True)
    print("  social card -> %s" % os.path.relpath(out, ROOT))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if not os.path.isdir(STORE):
        print("  Nudge repo not found at:\n    %s" % os.path.abspath(APP))
        print("  Leaving committed images and listing text as they are.")
        return 0

    os.makedirs(SRC_IMG, exist_ok=True)
    build_og()

    listing = {}
    total = 0
    dims = None
    for code, store_loc in LOCALES.items():
        listing[code] = read_listing(store_loc)
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
