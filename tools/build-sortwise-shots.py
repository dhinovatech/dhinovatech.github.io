#!/usr/bin/env python3
"""
Build the Sortwise imagery and listing text the landing pages need.

Sortwise is built from the same repository as Stow
(C:/Drive/git/offlineAIFolderOrganizer/.../offlineAIFolderOrganizer), and its
Microsoft Store release kit lives in SortwiseStore/:

  * upload/<store tag>/store-listings-export.csv - what the Store shows, per
    language: title, short description, description (19 paragraphs), the 20
    feature bullets and the 9 screenshot captions;
  * upload/<store tag>/Screenshots/DesktopScreenshot1-9.png - the 3840x2160
    slides, headline already written in that language over a real capture of
    the app in that language, on a demo library (C:\\Demo\\Sortwise);
  * listing/slides/<store tag>.json - the words on the slides: hero lines,
    hero chips, the eight overview tiles of slide 2, and the kicker, title and
    bullets of slides 3-9.

This script:

  * converts the slides the page shows to WebP at the width it renders them
    at, under English keyword file names, into
    assets/images/sortwise/<site locale>/<slug>.webp;
  * copies the text the page reuses into tools/sortwise-listing.json;
  * copies the app icon to assets/images/_src/sortwise-icon.png and draws the
    1200x630 social card assets/images/_src/sortwise-og.png; build-images.py
    compresses both like any other source image.

The source repository is not a dependency of this site: if it is not checked
out, this script says so and exits 0, and build-sortwise.py renders from what
is already committed.

Run:  python tools/build-sortwise-shots.py            (slides, text, icon, card)
      python tools/build-sortwise-shots.py --text-only
Idempotent: every output is re-derived from source on each run.
"""
import csv
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "images", "sortwise")
LISTING = os.path.join(ROOT, "tools", "sortwise-listing.json")
SRC_IMG = os.path.join(ROOT, "assets", "images", "_src")

# The application repository. Override with SORTWISE_REPO.
APP = os.environ.get("SORTWISE_REPO", os.path.join(
    "C:\\", "Drive", "git", "offlineAIFolderOrganizer", "offlineAIFolderOrganizer",
    "offlineAIFolderOrganizer"))
KIT = os.path.join(APP, "SortwiseStore")
UPLOAD = os.path.join(KIT, "upload")
SLIDE_TEXT = os.path.join(KIT, "listing", "slides")
ICON_SRC = os.path.join(APP, "SwPkg", "Images", "Square44x44Logo.altform-unplated_targetsize-256.png")

# Site locale -> store tag (the kit's folder and column names).
LOCALES = {
    "en": "en-us", "de": "de", "fr": "fr", "es": "es", "it": "it", "pt": "pt",
    "nl": "nl", "sv": "sv", "da": "da", "nb": "nb", "fi": "fi", "hu": "hu",
    "pl": "pl", "cs": "cs", "ru": "ru", "uk": "uk", "tr": "tr", "ja": "ja",
    "ko": "ko", "zh": "zh-hans", "th": "th", "ar": "ar", "he": "he",
}

# slug -> store slide number. Slide 2 is eight text tiles on a plain
# background; the page sets the same tiles as real text, so it is not shipped.
# The slugs are English keyword phrases in every locale: image search reads
# the file name, and one name per picture keeps the paths predictable.
SLIDES = [("ai-photo-file-organizer", 1), ("ai-photo-search", 3),
          ("sort-files-by-type-or-date", 4), ("preview-every-move", 5),
          ("duplicate-file-finder", 6), ("find-files", 7),
          ("tidy-downloads-folder", 8), ("undo-timeline", 9)]

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
    csv.field_size_limit(10 ** 8)
    path = os.path.join(UPLOAD, tag, "store-listings-export.csv")
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    col = rows[0].index(tag)
    val = dict((r[0], r[col].replace("\r\n", "\n")) for r in rows[1:] if len(r) > col)
    with open(os.path.join(SLIDE_TEXT, tag + ".json"), encoding="utf-8") as fh:
        src = json.load(fh)
    # "All features free · Unlimited scans · 1,000 file changes a month"
    footer = [p.strip() for p in src["footer"].split("·")]
    return {
        "title": val["Title"],
        "kind": src["hero"]["tagline"],
        "short": val["ShortDescription"],
        "headline": src["hero"]["headline"],
        "subline": src["hero"]["subline"],
        "chips": src["hero"]["chips"],
        "free": footer[0],
        "scans": footer[1],
        "changes": footer[2],
        "overview": {"kicker": src["overview"]["kicker"], "title": src["overview"]["title"],
                     "tiles": src["overview"]["tiles"]},
        "shots": [{"kicker": s["kicker"], "title": s["title"], "points": s["bullets"]}
                  for s in src["shots"]],
        "description": [p.strip() for p in val["Description"].split("\n\n") if p.strip()],
        "features": [val["Feature%d" % i] for i in range(1, 21) if val.get("Feature%d" % i)],
        "captions": [val["DesktopScreenshotCaption%d" % i] for i in range(1, 10)],
    }


# ---------------------------------------------------------------- social card

CARD = (1200, 630)
INK = "#f4fff9"
MUTED = "#b9e6d3"
AMBER = (255, 211, 102)     # "ALL FEATURES FREE" on slide 1
BG_TOP = (14, 139, 99)      # the slides' green
BG_BOTTOM = (3, 44, 31)


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
        # The unplated icon already has its own rounded corners.
        icon = Image.open(ICON_SRC).convert("RGBA").resize((side, side), Image.LANCZOS)
        card.paste(icon, (80, (CARD[1] - side) // 2), icon)

    x = 80 + 250 + 60
    draw.text((x, 150), "Sortwise", font=font("segoeuib.ttf", 84), fill=INK)
    draw.text((x, 256), "AI photo & file organizer for Windows",
              font=font("segoeui.ttf", 32), fill=MUTED)
    claims = "Tidy Downloads  ·  Find duplicates  ·  Undo anything"
    for size in range(30, 17, -1):
        f = font("segoeuib.ttf", size)
        if draw.textlength(claims, font=f) <= CARD[0] - x - 60:
            break
    draw.text((x, 314), claims, font=f, fill=AMBER)

    draw.rounded_rectangle([x, 392, x + 330, 450], radius=29, fill=AMBER)
    draw.text((x + 28, 407), "All features free", font=font("segoeuib.ttf", 28), fill=(3, 44, 31))
    draw.text((x + 354, 409), "Microsoft Store", font=font("segoeui.ttf", 27), fill=MUTED)

    out = os.path.join(SRC_IMG, "sortwise-og.png")
    card.save(out, "PNG", optimize=True)
    print("  social card -> %s" % os.path.relpath(out, ROOT))


def copy_icon():
    if not os.path.exists(ICON_SRC):
        return
    out = os.path.join(SRC_IMG, "sortwise-icon.png")
    Image.open(ICON_SRC).convert("RGBA").save(out, "PNG", optimize=True)
    print("  icon -> %s" % os.path.relpath(out, ROOT))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if not os.path.isdir(UPLOAD):
        print("  Sortwise release kit not found at:\n    %s" % os.path.abspath(KIT))
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
            src = os.path.join(UPLOAD, tag, "Screenshots", "DesktopScreenshot%d.png" % n)
            if not os.path.exists(src):
                src = os.path.join(UPLOAD, "en-us", "Screenshots", "DesktopScreenshot%d.png" % n)
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
