#!/usr/bin/env python3
"""
Build the Steptell imagery and listing text the landing pages need.

The Steptell application repository keeps a complete Microsoft Store listing
kit per store language (StoreScreenshotsV2/<store locale>): ten 3840x2160
slides whose headline is already written in that language over a real capture
of the app in that language, the upload CSV, and - under
_source/tools/strings - the words on every slide and the listing text as
structured JSON. This script:

  * converts the slides the page shows to WebP at the width it renders them
    at and writes them to assets/images/steptell/<site locale>/<slug>.webp;
  * copies the text the page reuses into tools/steptell-listing.json: the
    title, short description, description, feature bullets and slide captions
    from the upload CSV (what the Store actually shows), and the hero lines,
    hero chips, the ten overview tiles of slide 2 and the eight slide
    headlines with their bullets from the strings file;
  * copies the app icon to assets/images/_src/steptell-icon.png and draws the
    1200x630 social card assets/images/_src/steptell-og.png; build-images.py
    compresses both like any other source image.

Every picture is the app itself running on a seeded demo library (six guides
in fictional Contoso apps, every image drawn), so all of them are safe to show.

The source repository is not a dependency of this site: if it is not checked
out, this script says so and exits 0, and build-steptell.py renders from what
is already committed.

Run:  python tools/build-steptell-shots.py
Idempotent: every output is re-derived from source on each run.
"""
import csv
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "images", "steptell")
LISTING = os.path.join(ROOT, "tools", "steptell-listing.json")
SRC_IMG = os.path.join(ROOT, "assets", "images", "_src")

# The application repository. Override with STEPTELL_REPO.
APP = os.environ.get("STEPTELL_REPO",
                     os.path.join("C:\\", "Drive", "git", "StepTell", "StepTell"))
STORE = os.path.join(APP, "StoreScreenshotsV2")
STRINGS = os.path.join(STORE, "_source", "tools", "strings")
ICON_SRC = os.path.join(APP, "launch", "brand", "icon-1024.png")

# Site locale -> store listing locale directory (the column names Partner
# Center uses). Portuguese is the Brazilian listing.
LOCALES = {
    "en": "en-us", "ar": "ar-sa", "cs": "cs-cz", "da": "da-dk", "de": "de-de",
    "es": "es-es", "fi": "fi-fi", "fr": "fr-fr", "he": "he-il", "id": "id-id",
    "it": "it-it", "ja": "ja-jp", "ko": "ko-kr", "nb": "nb-no", "nl": "nl-nl",
    "pl": "pl-pl", "pt": "pt-br", "ro": "ro-ro", "sv": "sv-se", "th": "th-th",
    "tr": "tr-tr", "uk": "uk-ua", "vi": "vi-vn", "zh": "zh-cn", "zh-tw": "zh-tw",
}

# slug -> store slide number. Slide 1 is the hero and slides 3-10 the gallery,
# in the kit's SHOT_ORDER (home, label, privacy, export, document, report,
# consent, settings). Slide 2 is ten text tiles on a plain background; the
# page sets the same tiles as real text, so the picture is not shipped.
SLIDES = [("hero", 1), ("record", 3), ("edit", 4), ("privacy", 5),
          ("export", 6), ("guide", 7), ("report", 8), ("private", 9),
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
        src = json.load(fh)
    return {
        "title": val["Title"],
        "kind": src["appKind"],
        "short": val["ShortDescription"],
        "line1": src["heroLine1"],
        "line2": src["heroLine2"],
        "chips": [c["label"] for c in src["heroChips"]],
        "free": src["footerFree"],
        "free_sub": src["freeSub"],
        "overview": {"title": src["overviewTitle"], "sub": src["overviewSub"],
                     "tiles": [[f["icon"], f["label"], f["desc"]] for f in src["features"]]},
        "shots": [{"kicker": s["kicker"], "title": s["title"], "points": s["points"]}
                  for s in src["shots"]],
        "description": [p.strip() for p in val["Description"].split("\n\n") if p.strip()],
        "features": [val["Feature%d" % i] for i in range(1, 21) if val.get("Feature%d" % i)],
        "captions": [val["DesktopScreenshotCaption%d" % i] for i in range(1, 11)],
    }


# ---------------------------------------------------------------- social card

CARD = (1200, 630)
INK = "#f4f7ff"
MUTED = "#b4c3ea"
AMBER = (255, 194, 61)      # "ALL FEATURES FREE" on slide 1
BG_TOP = (26, 70, 193)      # the slides' royal blue
BG_BOTTOM = (16, 18, 40)


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
        # The icon already has its own rounded corners on a transparent canvas.
        icon = Image.open(ICON_SRC).convert("RGBA").resize((side, side), Image.LANCZOS)
        card.paste(icon, (80, (CARD[1] - side) // 2), icon)

    x = 80 + 250 + 60
    draw.text((x, 150), "Steptell", font=font("segoeuib.ttf", 84), fill=INK)
    draw.text((x, 256), "Steps recorder & how-to guide maker for Windows",
              font=font("segoeui.ttf", 30), fill=MUTED)
    claims = "Replaces Steps Recorder  ·  Blurs passwords  ·  100% offline"
    for size in range(30, 17, -1):
        f = font("segoeuib.ttf", size)
        if draw.textlength(claims, font=f) <= CARD[0] - x - 60:
            break
    draw.text((x, 314), claims, font=f, fill=AMBER)

    draw.rounded_rectangle([x, 392, x + 330, 450], radius=29, fill=AMBER)
    draw.text((x + 28, 407), "All features free", font=font("segoeuib.ttf", 28), fill=(16, 18, 40))
    draw.text((x + 354, 409), "Microsoft Store", font=font("segoeui.ttf", 27), fill=MUTED)

    out = os.path.join(SRC_IMG, "steptell-og.png")
    card.save(out, "PNG", optimize=True)
    print("  social card -> %s" % os.path.relpath(out, ROOT))


def copy_icon():
    if not os.path.exists(ICON_SRC):
        return
    out = os.path.join(SRC_IMG, "steptell-icon.png")
    Image.open(ICON_SRC).convert("RGBA").resize((512, 512), Image.LANCZOS).save(out, "PNG", optimize=True)
    print("  icon -> %s" % os.path.relpath(out, ROOT))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if not os.path.isdir(STORE):
        print("  Steptell repo not found at:\n    %s" % os.path.abspath(APP))
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
