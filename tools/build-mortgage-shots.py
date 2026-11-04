#!/usr/bin/env python3
"""
Build the Mortgage Loan EMI Pro Insights imagery and listing text the landing
pages need.

The application repository keeps a complete Microsoft Store listing kit per
store language (StoreScreenshotsV2/<store>): ten 3840x2160 slides whose words
are in that language over a real capture of the app in that language, with
that market's money and rates, plus the upload CSV. Under _source/tools it
keeps the structured words (strings/<store>.json) and the demo loan of each
market (make_demo.py). This script:

  * converts the slides the page shows to WebP and writes them to
    assets/images/mortgage/<site locale>/<slug>.webp;
  * copies the text the page reuses into tools/mortgage-listing.json: title,
    short description, description, features, captions and search terms from
    the upload CSV (what the Store actually shows), the slide words from the
    strings file, the twelve decision tools and the calculator labels from the
    app's own AppResources, and the market's demo loan;
  * copies the app icon to assets/images/_src/mortgage-emi-icon.png and draws
    the 1200x630 social card assets/images/_src/mortgage-emi-og.png;
    build-images.py compresses both like any other source image.

Every figure in the slides was worked out by the app on an invented demo loan,
so all of them are safe to show.

The source repository is not a dependency of this site: if it is not checked
out, this script says so and exits 0, and build-mortgage.py renders from what
is already committed.

Run:  python tools/build-mortgage-shots.py
Idempotent: every output is re-derived from source on each run.
"""
import csv
import importlib.util
import json
import os
import sys
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "images", "mortgage")
LISTING = os.path.join(ROOT, "tools", "mortgage-listing.json")
SRC_IMG = os.path.join(ROOT, "assets", "images", "_src")

# The application repository. Override with MORTGAGE_REPO.
APP = os.environ.get("MORTGAGE_REPO",
                     os.path.join("C:\\", "Drive", "git", "MortgageLoanEMIInsights",
                                  "MortgageLoanEMIProInsights"))
STORE = os.path.join(APP, "StoreScreenshotsV2")
KIT = os.path.join(STORE, "_source", "tools")
STRINGS = os.path.join(KIT, "strings")
ICON_SRC = os.path.join(STORE, "_source", "icon-master.png")
RESX = os.path.join(APP, "MortgageLoanEMIProInsights.WinUI", "Resources", "Strings")

# Site locale -> store folder (the column Partner Center uses) and resx suffix.
LOCALES = {
    "en": ("en-us", ""), "ar": ("ar", ".ar"), "cs": ("cs", ".cs"), "da": ("da", ".da"),
    "de": ("de", ".de"), "es": ("es", ".es"), "fr": ("fr", ".fr"), "hi": ("hi", ".hi"),
    "id": ("id", ".id"), "it": ("it", ".it"), "ja": ("ja", ".ja"), "ko": ("ko", ".ko"),
    "nb": ("nb", ".nb"), "nl": ("nl", ".nl"), "pl": ("pl", ".pl"), "pt": ("pt", ".pt"),
    "ru": ("ru", ".ru"), "sv": ("sv", ".sv"), "th": ("th", ".th"), "tr": ("tr", ".tr"),
    "vi": ("vi", ".vi"), "zh": ("zh-hans", ".zh"), "zh-tw": ("zh-hant", ".zh-Hant"),
}

# slug -> store slide number. Slide 2 is ten text tiles on a plain background;
# the page sets the same tiles as real text, so the picture is not shipped.
# Slugs are English on purpose: the file name is part of what image search reads.
SLIDES = [("mortgage-emi-calculator", 1), ("loan-calculator", 3), ("extra-payment-calculator", 4),
          ("loan-charts", 5), ("amortization-schedule", 6), ("compare-loans", 7),
          ("loan-decision-tools", 8), ("inflation-adjusted-loan-cost", 9), ("my-loans-tracking", 10)]

# Keys from the app's AppResources: the twelve decision tools, in the order of
# the Tools page, and the words on the page's calculator.
TOOLS = ["MaxLoan", "Tenure", "Rate", "Goal", "Afford", "Stress", "Refi", "Prepay", "Rent",
         "Down", "Sale", "Frequency"]
LABELS = {"amount": "LoanAmountLabel", "rate": "InterestRateLabel", "years": "TenureYearsLabel",
          "extra": "ExtraMonthlyPayment", "payment": "MonthlyEMILabel", "interest": "TotalInterestLabel",
          "saved": "InterestSavedLabel", "time": "TimeSavedLabel", "time_fmt": "TermYearsMonthsFormat"}

WIDTH = 1200
QUALITY = 74


def convert(src, dst):
    im = Image.open(src).convert("RGB")
    if im.width > WIDTH:
        im = im.resize((WIDTH, round(im.height * WIDTH / float(im.width))), Image.LANCZOS)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im.save(dst, "WEBP", quality=QUALITY, method=6)
    return im.size, os.path.getsize(dst)


def load_resx(suffix):
    root = ET.parse(os.path.join(RESX, "AppResources%s.resx" % suffix)).getroot()
    return {d.get("name"): (d.find("value").text or "") for d in root.findall("data")}


def load_demo():
    """The market table from the kit's make_demo.py, without running its main."""
    spec = importlib.util.spec_from_file_location("make_demo", os.path.join(KIT, "make_demo.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True
    spec.loader.exec_module(mod)
    return mod.MARKETS


def read_listing(code, store_loc, suffix, markets, en_res):
    path = os.path.join(STORE, store_loc, "store-listings-export.csv")
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    col = rows[0].index(store_loc)
    val = dict((r[0], r[col].replace("\r\n", "\n")) for r in rows[1:] if len(r) > col)
    with open(os.path.join(STRINGS, store_loc + ".json"), encoding="utf-8") as fh:
        src = json.load(fh)
    res = load_resx(suffix)

    def word(key):
        return res.get(key) or en_res[key]

    _lang, region, currency, _grouping, price, down, rate, years = markets[store_loc]
    amount = price - down
    r, n = rate / 1200.0, years * 12
    payment = amount * r / (1 - (1 + r) ** -n)
    # The kit's own rule for the demo's extra payment, so the page's calculator
    # opens on the same loan, and the same saving, as this language's slide 1.
    step = 10 ** (len(str(int(payment * 0.2))) - 1)
    extra = int(round(payment * 0.2 / step) * step) or step
    return {
        "title": val["Title"],
        "kind": src["appKind"],
        "short": val["ShortDescription"],
        "line1": src["heroLine1"],
        "line2": src["heroLine2"],
        "chips": [c["label"] for c in src["heroChips"]],
        "free": src["footerFree"],
        "free_sub": src["freeSub"],
        "pro_line": src["footerPro"],
        "chip_free": src["chipFree"],
        "overview": {"title": src["overviewTitle"], "sub": src["overviewSub"],
                     "tiles": [[f["icon"], f["label"], f["desc"], f["pro"]] for f in src["features"]]},
        "shots": [{"kicker": s["kicker"], "title": s["title"], "points": s["points"], "pro": s["pro"]}
                  for s in src["shots"]],
        "description": [p.strip() for p in val["Description"].split("\n\n") if p.strip()],
        "features": [val["Feature%d" % i] for i in range(1, 21) if val.get("Feature%d" % i)],
        "captions": [val["DesktopScreenshotCaption%d" % i] for i in range(1, 11)],
        "terms": [val["SearchTerm%d" % i] for i in range(1, 8) if val.get("SearchTerm%d" % i)],
        "tools": [[word("Tool%sTitle" % t), word("Tool%sHelp" % t)] for t in TOOLS],
        "labels": {k: word(v) for k, v in LABELS.items()},
        # Plural forms, for the languages whose word changes with the number
        # (the app's TermText). Empty where one format string is right.
        "term": {"years": {k[9:]: v for k, v in res.items()
                           if k.startswith("TermYears") and k != "TermYearsMonthsFormat"},
                 "months": {k[10:]: v for k, v in res.items() if k.startswith("TermMonths")},
                 "join": res.get("TermJoinFormat", "{0} {1}")},
        "demo": {"region": region, "currency": currency, "amount": amount,
                 "rate": rate, "years": years, "extra": extra},
    }


# ---------------------------------------------------------------- social card

CARD = (1200, 630)
INK = "#f4f7ff"
MUTED = "#b7c6e4"
GREEN = (34, 197, 94)       # "CORE CALCULATOR ALWAYS FREE" on slide 1
AMBER = (251, 191, 36)      # "Pay it off years sooner." on slide 1
BG_TOP = (14, 56, 120)      # the slides' navy
BG_BOTTOM = (8, 40, 56)


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
        side = 240
        icon = Image.open(ICON_SRC).convert("RGBA").resize((side, side), Image.LANCZOS)
        card.paste(icon, (70, (CARD[1] - side) // 2), icon)

    x = 70 + 240 + 50
    draw.text((x, 112), "Mortgage Loan EMI", font=font("segoeuib.ttf", 62), fill=INK)
    draw.text((x, 184), "Pro Insights", font=font("segoeuib.ttf", 62), fill=INK)
    draw.text((x, 272), "Free mortgage, EMI & loan calculator for Windows",
              font=font("segoeui.ttf", 31), fill=MUTED)
    draw.text((x, 326), "Pay it off years sooner.", font=font("segoeuib.ttf", 36), fill=AMBER)

    draw.rounded_rectangle([x, 402, x + 452, 468], radius=18, fill=GREEN)
    draw.text((x + 26, 416), "Core calculator always free", font=font("segoeuib.ttf", 28), fill=(6, 30, 18))
    draw.text((x + 474, 420), "Microsoft Store", font=font("segoeui.ttf", 27), fill=MUTED)

    out = os.path.join(SRC_IMG, "mortgage-emi-og.png")
    card.save(out, "PNG", optimize=True)
    print("  social card -> %s" % os.path.relpath(out, ROOT))


def copy_icon():
    if not os.path.exists(ICON_SRC):
        return
    out = os.path.join(SRC_IMG, "mortgage-emi-icon.png")
    Image.open(ICON_SRC).convert("RGBA").save(out, "PNG", optimize=True)
    print("  icon -> %s" % os.path.relpath(out, ROOT))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if not os.path.isdir(STORE):
        print("  Mortgage repo not found at:\n    %s" % os.path.abspath(APP))
        print("  Leaving committed images and listing text as they are.")
        return 0

    os.makedirs(SRC_IMG, exist_ok=True)
    copy_icon()
    build_og()

    markets = load_demo()
    en_res = load_resx("")
    listing = {}
    total = 0
    dims = None
    text_only = "--text-only" in sys.argv
    for code, (store_loc, suffix) in LOCALES.items():
        listing[code] = read_listing(code, store_loc, suffix, markets, en_res)
        if text_only:
            continue
        for slug, n in SLIDES:
            src = os.path.join(STORE, store_loc, "Screenshots", "DesktopScreenshot%d.png" % n)
            dims, size = convert(src, os.path.join(OUT, code, slug + ".webp"))
            total += size
        print("  %s done" % code, flush=True)

    with open(LISTING, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(listing, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    if dims:
        print("  %d locales x %d slides -> %s (%dx%d, %.1f MB)"
              % (len(LOCALES), len(SLIDES), os.path.relpath(OUT, ROOT),
                 dims[0], dims[1], total / 1048576.0))
    print("  listing text -> %s" % os.path.relpath(LISTING, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
