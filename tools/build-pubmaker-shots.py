#!/usr/bin/env python3
"""
Build the PubMaker imagery and listing text the landing pages need.

PubMaker's Microsoft Store release kit lives in the app repository
(C:/Drive/git/PubMaker/pubmaker), under PubMakerScreenshotsV2/:

  * _source/strings/<store tag>.json - every word on the slides and the whole
    listing for that language: localized title, short description, the 10
    description paragraphs, the 20 feature bullets, the 10 screenshot captions,
    and the hero lines, chips, overview tiles and slide kickers/titles/bullets;
  * <store tag>/Screenshots/DesktopScreenshot1-10.png - the 3840x2160 slides,
    headline already written in that language over the real app in that
    language, with designs rendered from that language's template text.

This script:

  * converts the slides the page shows to WebP at the width it renders them
    at, under English keyword file names, into
    assets/images/pubmaker/<site locale>/<slug>.webp;
  * copies the text the page reuses into tools/pubmaker-listing.json;
  * copies the app icon to assets/images/_src/pubmaker-icon.png and draws the
    1200x630 social card assets/images/_src/pubmaker-og.png; build-images.py
    compresses both like any other source image.

The source repository is not a dependency of this site: if it is not checked
out, this script says so and exits 0, and build-pubmaker.py renders from what
is already committed.

Run:  python tools/build-pubmaker-shots.py            (slides, text, icon, card)
      python tools/build-pubmaker-shots.py --text-only
Idempotent: every output is re-derived from source on each run.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "images", "pubmaker")
LISTING = os.path.join(ROOT, "tools", "pubmaker-listing.json")
SRC_IMG = os.path.join(ROOT, "assets", "images", "_src")

# The application repository. Override with PUBMAKER_REPO.
APP = os.environ.get("PUBMAKER_REPO", os.path.join("C:\\", "Drive", "git", "PubMaker", "pubmaker"))
KIT = os.path.join(APP, "PubMakerScreenshotsV2")
STRINGS = os.path.join(KIT, "_source", "strings")
ICON_SRC = os.path.join(APP, "src", "PubMaker.App", "Assets",
                        "Square44x44Logo.targetsize-256_altform-unplated.png")

# Site locale -> store tag (the kit's folder names). Portuguese is the
# Brazilian listing; zh is Simplified, zh-tw Traditional.
LOCALES = {
    "en": "en-us", "de": "de-de", "fr": "fr-fr", "es": "es-es", "pt": "pt-br",
    "it": "it-it", "nl": "nl-nl", "pl": "pl-pl", "sv": "sv-se", "da": "da-dk",
    "nb": "nb-no", "fi": "fi-fi", "cs": "cs-cz", "ro": "ro-ro", "uk": "uk-ua",
    "tr": "tr-tr", "ja": "ja-jp", "ko": "ko-kr", "zh": "zh-cn", "zh-tw": "zh-tw",
    "id": "id-id", "vi": "vi-vn", "th": "th-th", "ar": "ar-sa", "he": "he-il",
}

# slug -> store slide number. Slide 2 is eight text tiles on a plain
# background; the page sets the same tiles as real text, so it is not shipped.
# The slugs are English keyword phrases in every locale: image search reads
# the file name, and one name per picture keeps the paths predictable.
SLIDES = [("pub-file-editor-desktop-publishing", 1), ("free-publishing-templates", 3),
          ("open-pub-files", 4), ("desktop-publishing-software", 5),
          ("color-and-font-schemes", 6), ("mail-merge-labels", 7),
          ("print-business-cards-booklets-posters", 8), ("export-pub-to-pdf", 9),
          ("offline-in-25-languages", 10)]

WIDTH = 1200
QUALITY = 74


def convert(src, dst):
    im = Image.open(src).convert("RGB")
    if im.width > WIDTH:
        im = im.resize((WIDTH, round(im.height * WIDTH / float(im.width))), Image.LANCZOS)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im.save(dst, "WEBP", quality=QUALITY, method=6)
    return im.size, os.path.getsize(dst)


def read_listing(tag):
    with open(os.path.join(STRINGS, tag + ".json"), encoding="utf-8") as fh:
        src = json.load(fh)
    sl, li = src["slides"], src["listing"]
    hero = sl["hero"]
    return {
        "title": li["title"],
        "kind": hero["tagline"],
        "short": li["shortDescription"],
        "line1": hero["line1"],
        "line2": hero["line2"],
        "chips": hero["chips"],
        "badge": hero["badge"],
        "free": sl["footer"],
        "overview": {"kicker": sl["overview"]["kicker"], "title": sl["overview"]["title"],
                     "tiles": sl["overview"]["tiles"]},
        "wall": {"kicker": sl["wall"]["kicker"], "title": sl["wall"]["title"]},
        "shots": [{"kicker": s["kicker"], "title": s["title"], "points": s["bullets"]}
                  for s in sl["shots"]],
        "description": [p.strip() for p in li["description"] if p.strip()],
        "features": [f for f in li["features"] if f],
        "captions": li["captions"],
    }


# ---------------------------------------------------------------- social card

CARD = (1200, 630)
INK = "#f4fffc"
MUTED = "#b7e3e0"
MINT = (110, 224, 188)      # line 2 of slide 1
GOLD = (255, 207, 90)       # "100% FREE · EVERY FEATURE"
BG_TOP = (21, 84, 96)       # the slides' teal
BG_BOTTOM = (8, 33, 41)


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

    side = 250
    if os.path.exists(ICON_SRC):
        icon = Image.open(ICON_SRC).convert("RGBA").resize((side, side), Image.LANCZOS)
        card.paste(icon, (70, (CARD[1] - side) // 2), icon)

    x = 70 + side + 50
    draw.text((x, 140), "PubMaker", font=font("segoeuib.ttf", 84), fill=INK)
    draw.text((x, 246), "Pub file editor & desktop publishing",
              font=font("segoeui.ttf", 32), fill=MUTED)
    claims = "Open .pub files  ·  200+ templates  ·  Mail merge"
    for size in range(30, 17, -1):
        f = font("segoeuib.ttf", size)
        if draw.textlength(claims, font=f) <= CARD[0] - x - 50:
            break
    draw.text((x, 304), claims, font=f, fill=MINT)

    draw.rounded_rectangle([x, 384, x + 330, 442], radius=29, fill=GOLD)
    draw.text((x + 26, 399), "Every feature free", font=font("segoeuib.ttf", 28), fill=(8, 33, 41))
    draw.text((x + 354, 401), "Microsoft Store", font=font("segoeui.ttf", 27), fill=MUTED)

    out = os.path.join(SRC_IMG, "pubmaker-og.png")
    card.save(out, "PNG", optimize=True)
    print("  social card -> %s" % os.path.relpath(out, ROOT))


def copy_icon():
    if not os.path.exists(ICON_SRC):
        return
    out = os.path.join(SRC_IMG, "pubmaker-icon.png")
    Image.open(ICON_SRC).convert("RGBA").save(out, "PNG", optimize=True)
    print("  icon -> %s" % os.path.relpath(out, ROOT))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if not os.path.isdir(STRINGS):
        print("  PubMaker release kit not found at:\n    %s" % os.path.abspath(KIT))
        print("  Leaving committed images and listing text as they are.")
        return 0
    text_only = "--text-only" in sys.argv

    listing = {}
    total, dims = 0, None
    if not text_only:
        os.makedirs(SRC_IMG, exist_ok=True)
        copy_icon()
        build_og()
    for code, tag in LOCALES.items():
        listing[code] = read_listing(tag)
        if text_only:
            continue
        for slug, n in SLIDES:
            src = os.path.join(KIT, tag, "Screenshots", "DesktopScreenshot%d.png" % n)
            if not os.path.exists(src):
                src = os.path.join(KIT, "en-us", "Screenshots", "DesktopScreenshot%d.png" % n)
            dims, size = convert(src, os.path.join(OUT, code, slug + ".webp"))
            total += size

    with open(LISTING, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(listing, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    if not text_only:
        print("  %d locales x %d slides -> %s (%dx%d, %.1f MB)"
              % (len(LOCALES), len(SLIDES), os.path.relpath(OUT, ROOT),
                 dims[0], dims[1], total / 1048576.0))
    print("  listing text -> %s" % os.path.relpath(LISTING, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
