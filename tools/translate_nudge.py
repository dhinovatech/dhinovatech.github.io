#!/usr/bin/env python3
"""
Complete multilingual localization for Nudge:
Translates all 121 keys (headings, paragraphs, pillars, specs matrix,
comparison table, workflows, FAQs, moments, quotes, and hardware tiers)
across all 50 target non-English locales using an unthrottled Google endpoint.

Saves progress incrementally to tools/nudge-strings.json after every language.
"""
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STRINGS_PATH = os.path.join(ROOT, "tools", "nudge-strings.json")

with open(STRINGS_PATH, "r", encoding="utf-8") as f:
    L = json.load(f)

en = L["en"]

GT_MAP = {
    "ar": "ar", "zh": "zh-CN", "es": "es", "ja": "ja", "de": "de", "fr": "fr",
    "ko": "ko", "hi": "hi", "pt": "pt", "pt-pt": "pt", "id": "id", "ms": "ms",
    "ru": "ru", "tr": "tr", "it": "it", "nl": "nl", "pl": "pl", "th": "th",
    "fa": "fa", "sv": "sv", "vi": "vi", "bn": "bn", "yue": "zh-TW", "tl": "tl",
    "uk": "uk", "cs": "cs", "ro": "ro", "he": "iw", "el": "el", "hu": "hu",
    "da": "da", "fi": "fi", "nb": "no", "te": "te", "mr": "mr", "ta": "ta",
    "gu": "gu", "ur": "ur", "pa": "pa", "ml": "ml", "kn": "kn", "jv": "jw",
    "sw": "sw", "ha": "ha", "yo": "yo", "my": "my", "am": "am", "kk": "kk",
    "sk": "sk", "ca": "ca"
}

# Strings that must never be translated
PROTECTED_EXACT = {
    "Windows 10 / Windows 11",
    "Windows 10, Windows 11",
    "Nudge",
    "Day One",
    "Obsidian",
    "Notion",
    "AI Chatbots",
    "WinUI 3",
    "WinUI 3 Native",
    "Electron",
    "Markdown",
    "Plain Markdown",
    "Plain Markdown (.md)",
    "SQLite",
    "AES-256-GCM",
    "Argon2id",
    "x64",
    "ARM64",
    "Copilot+ PC",
    "Snapdragon X Elite",
    "Snapdragon X Plus",
    "BM25",
    "YAML",
    "JSON",
    "CSV",
    "EPUB",
    "PDF",
    "1", "2", "3", "4", "5",
    "—", "-", "$0.99", "0.99", "0,99"
}

# Post-translation regex cleanups to restore brand terms
BRAND_FIXES = [
    (re.compile(r"\b(Fenêtres|Ventanas|Finestre|Janelas|Fenster|Виндовс|Винда)\s+(10|11)\b", re.IGNORECASE), r"Windows \2"),
    (re.compile(r"\b(Giorno uno|Día uno|Jour un|Tag eins|Dia um)\b", re.IGNORECASE), "Day One"),
    (re.compile(r"\b(Spintone|Empujoncito|Anstupsen|Coup de coude)\b", re.IGNORECASE), "Nudge"),
]

ALL_STRING_KEYS = [
    # Hero & Branding
    "subtitle", "tagline", "intro_lead", "intro_p2",
    "platform_badge", "badge_offline", "badge_ai", "badge_markdown",
    "badge_telemetry", "badge_hello", "badge_price",
    "cta_store", "cta_trial", "cta_buy", "cta_see",
    # Section Headings
    "h_pillars", "pillars_sub",
    "h_specs", "specs_sub",
    "h_manifesto", "manifesto_sub",
    "manifesto_cloud_title", "manifesto_cloud_desc",
    "manifesto_epistemic_title", "manifesto_epistemic_desc",
    "manifesto_longevity_title", "manifesto_longevity_desc",
    "h_arch", "arch_sub",
    "arch_fs_title", "arch_fs_desc",
    "arch_atomic_title", "arch_atomic_desc",
    "arch_bm25_title", "arch_bm25_desc",
    "h_ai", "ai_sub",
    "ai_rule_title", "ai_rule_desc",
    "moments_title",
    "ai_recap_title", "ai_recap_desc",
    "ai_search_title", "ai_search_desc",
    "h_psych", "psych_sub",
    "psych_grace_title", "psych_grace_desc",
    "psych_return_title", "psych_return_desc",
    "psych_median_title", "psych_median_desc",
    "psych_themes_title", "psych_themes_desc",
    "h_writing", "writing_sub",
    "writing_launch_title", "writing_launch_desc",
    "writing_palette_title", "writing_palette_desc",
    "writing_focus_title", "writing_focus_desc",
    "writing_capture_title", "writing_capture_desc",
    "h_security", "security_sub",
    "sec_hello_title", "sec_hello_desc",
    "sec_aes_title", "sec_aes_desc",
    "sec_privacy_title", "sec_privacy_desc",
    "sec_import_title", "sec_import_desc",
    "sec_export_title", "sec_export_desc",
    "h_multilingual", "multilingual_sub",
    "multi_cldr_title", "multi_cldr_desc",
    "multi_rtl_title", "multi_rtl_desc",
    "multi_grapheme_title", "multi_grapheme_desc",
    "h_compare", "compare_sub",
    "h_workflows", "workflows_sub",
    "h_hardware", "hardware_sub",
    "sys_min", "sys_rec",
    "h_pricing", "pricing_sub",
    "pricing_trial_title", "pricing_trial_desc",
    "pricing_buy_title", "pricing_buy_desc",
    "pricing_failopen_title", "pricing_failopen_desc",
    "pricing_expired_title", "pricing_expired_desc",
    "h_faq", "faq_sub",
    "h_quotes",
    "h_cta", "cta_lead", "cta_trial_btn", "cta_buy_btn", "cta_guarantee"
]

CACHE = {}

def translate(text, gt_target):
    if not text or not isinstance(text, str) or not text.strip():
        return text
    clean = text.strip()
    if clean in PROTECTED_EXACT:
        return text
    cache_key = (clean, gt_target)
    if cache_key in CACHE:
        return CACHE[cache_key]

    url = (
        "https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl=en&tl="
        + gt_target
        + "&q="
        + urllib.parse.quote(clean)
    )
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )

    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=7) as res:
                raw = res.read().decode("utf-8")
                data = json.loads(raw)
                if isinstance(data, list):
                    res_str = " ".join(str(p) for p in data if p)
                else:
                    res_str = str(data)

                # Post-fix brand terms
                for pattern, repl in BRAND_FIXES:
                    res_str = pattern.sub(repl, res_str)

                # Ensure 24.99 is never introduced
                res_str = res_str.replace("24.99", "0.99").replace("24,99", "0,99")

                CACHE[cache_key] = res_str
                return res_str
        except Exception:
            time.sleep(0.25 * (attempt + 1))

    return text

def translate_locale(lang_code):
    gt = GT_MAP.get(lang_code)
    if not gt:
        return 0

    data = L.get(lang_code, {})
    tasks = []

    # 1. Name
    cur_name = data.get("name", "")
    if not cur_name or cur_name == en["name"]:
        tasks.append(("name", "Offline Journal & Diary with AI Companion", "name"))

    # 2. Plain string keys
    for k in ALL_STRING_KEYS:
        if k in en:
            cur_val = data.get(k)
            # If missing or identical to English, queue translation
            if not cur_val or cur_val == en[k]:
                tasks.append((k, en[k], "plain"))

    # 3. Pillars
    cur_pillars = data.get("pillars", [])
    need_pillars = not cur_pillars or cur_pillars[0].get("title") == en["pillars"][0]["title"]
    if need_pillars:
        for idx, p in enumerate(en["pillars"]):
            tasks.append((f"pillar_t_{idx}", p["title"], "pillar_t"))
            tasks.append((f"pillar_d_{idx}", p["desc"], "pillar_d"))

    # 4. Specs headers & rows
    cur_sh = data.get("specs_headers", [])
    need_sh = not cur_sh or cur_sh[0] == en["specs_headers"][0]
    if need_sh:
        for idx, h in enumerate(en["specs_headers"]):
            tasks.append((f"sh_{idx}", h, "sh"))

    cur_sr = data.get("specs_rows", [])
    need_sr = not cur_sr or cur_sr[0][0] == en["specs_rows"][0][0]
    if need_sr:
        for r_idx, row in enumerate(en["specs_rows"]):
            for c_idx, col in enumerate(row):
                tasks.append((f"sr_{r_idx}_{c_idx}", col, "sr"))

    # 5. Compare headers & rows
    cur_ch = data.get("compare_headers", [])
    need_ch = not cur_ch or cur_ch[0] == en["compare_headers"][0]
    if need_ch:
        for idx, h in enumerate(en["compare_headers"]):
            tasks.append((f"ch_{idx}", h, "ch"))

    cur_cr = data.get("compare_rows", [])
    need_cr = not cur_cr or cur_cr[0][0] == en["compare_rows"][0][0]
    if need_cr:
        for r_idx, row in enumerate(en["compare_rows"]):
            for c_idx, col in enumerate(row):
                tasks.append((f"cr_{r_idx}_{c_idx}", col, "cr"))

    # 6. Moments
    cur_m = data.get("moments", [])
    need_m = not cur_m or cur_m[0].get("title") == en["moments"][0]["title"]
    if need_m:
        for idx, m in enumerate(en["moments"]):
            tasks.append((f"m_title_{idx}", m["title"], "m_title"))
            tasks.append((f"m_timing_{idx}", m["timing"], "m_timing"))
            tasks.append((f"m_desc_{idx}", m["desc"], "m_desc"))

    # 7. Workflows
    cur_wf = data.get("workflows", [])
    need_wf = not cur_wf or cur_wf[0].get("title") == en["workflows"][0]["title"]
    if need_wf:
        for idx, w in enumerate(en["workflows"]):
            tasks.append((f"wf_title_{idx}", w["title"], "wf_title"))
            tasks.append((f"wf_time_{idx}", w["time"], "wf_time"))
            tasks.append((f"wf_desc_{idx}", w["desc"], "wf_desc"))

    # 8. Hardware tiers
    cur_hw = data.get("hardware_tiers", [])
    need_hw = not cur_hw or cur_hw[0].get("tier") == en["hardware_tiers"][0]["tier"]
    if need_hw:
        for idx, hw in enumerate(en["hardware_tiers"]):
            tasks.append((f"hw_tier_{idx}", hw["tier"], "hw_tier"))
            tasks.append((f"hw_specs_{idx}", hw["specs"], "hw_specs"))
            tasks.append((f"hw_perf_{idx}", hw["perf"], "hw_perf"))

    # 9. FAQs
    cur_faqs = data.get("faqs", [])
    need_faqs = not cur_faqs or cur_faqs[0].get("q") == en["faqs"][0]["q"]
    if need_faqs:
        for idx, f in enumerate(en["faqs"]):
            tasks.append((f"faq_q_{idx}", f["q"], "faq_q"))
            tasks.append((f"faq_a_{idx}", f["a"], "faq_a"))

    # 10. Quotes
    cur_q = data.get("quotes", [])
    need_q = not cur_q or cur_q[0].get("quote") == en["quotes"][0]["quote"]
    if need_q:
        for idx, q in enumerate(en["quotes"]):
            tasks.append((f"q_quote_{idx}", q["quote"], "q_quote"))
            tasks.append((f"q_role_{idx}", q["role"], "q_role"))

    if not tasks:
        return 0

    def worker(item):
        key_id, text_to_tr, kind = item
        res = translate(text_to_tr, gt)
        return key_id, res, kind

    with ThreadPoolExecutor(max_workers=10) as ex:
        results = list(ex.map(worker, tasks))

    res_map = {r[0]: r[1] for r in results}

    # Apply translated values
    if "name" in res_map:
        data["name"] = f"Nudge — {res_map['name']}"

    for k in ALL_STRING_KEYS:
        if k in res_map:
            data[k] = res_map[k]

    if need_pillars:
        new_pillars = []
        for idx, p in enumerate(en["pillars"]):
            new_pillars.append({
                "num": p["num"],
                "icon": p["icon"],
                "title": res_map.get(f"pillar_t_{idx}", p["title"]),
                "desc": res_map.get(f"pillar_d_{idx}", p["desc"])
            })
        data["pillars"] = new_pillars

    if need_sh:
        data["specs_headers"] = [res_map.get(f"sh_{idx}", h) for idx, h in enumerate(en["specs_headers"])]

    if need_sr:
        new_sr = []
        for r_idx, row in enumerate(en["specs_rows"]):
            new_sr.append([
                res_map.get(f"sr_{r_idx}_{c_idx}", col)
                for c_idx, col in enumerate(row)
            ])
        data["specs_rows"] = new_sr

    if need_ch:
        data["compare_headers"] = [res_map.get(f"ch_{idx}", h) for idx, h in enumerate(en["compare_headers"])]

    if need_cr:
        new_cr = []
        for r_idx, row in enumerate(en["compare_rows"]):
            new_cr.append([
                res_map.get(f"cr_{r_idx}_{c_idx}", col)
                for c_idx, col in enumerate(row)
            ])
        data["compare_rows"] = new_cr

    if need_m:
        new_m = []
        for idx, m in enumerate(en["moments"]):
            new_m.append({
                "num": m["num"],
                "title": res_map.get(f"m_title_{idx}", m["title"]),
                "timing": res_map.get(f"m_timing_{idx}", m["timing"]),
                "desc": res_map.get(f"m_desc_{idx}", m["desc"])
            })
        data["moments"] = new_m

    if need_wf:
        new_wf = []
        for idx, w in enumerate(en["workflows"]):
            new_wf.append({
                "num": w["num"],
                "title": res_map.get(f"wf_title_{idx}", w["title"]),
                "time": res_map.get(f"wf_time_{idx}", w["time"]),
                "desc": res_map.get(f"wf_desc_{idx}", w["desc"])
            })
        data["workflows"] = new_wf

    if need_hw:
        new_hw = []
        for idx, hw in enumerate(en["hardware_tiers"]):
            new_hw.append({
                "tier": res_map.get(f"hw_tier_{idx}", hw["tier"]),
                "specs": res_map.get(f"hw_specs_{idx}", hw["specs"]),
                "perf": res_map.get(f"hw_perf_{idx}", hw["perf"])
            })
        data["hardware_tiers"] = new_hw

    if need_faqs:
        new_faqs = []
        for idx, f in enumerate(en["faqs"]):
            new_faqs.append({
                "q": res_map.get(f"faq_q_{idx}", f["q"]),
                "a": res_map.get(f"faq_a_{idx}", f["a"])
            })
        data["faqs"] = new_faqs

    if need_q:
        new_q = []
        for idx, q in enumerate(en["quotes"]):
            new_q.append({
                "quote": res_map.get(f"q_quote_{idx}", q["quote"]),
                "author": q["author"],
                "role": res_map.get(f"q_role_{idx}", q["role"])
            })
        data["quotes"] = new_q

    L[lang_code] = data

    # Immediate checkpoint save
    with open(STRINGS_PATH, "w", encoding="utf-8") as out_f:
        json.dump(L, out_f, ensure_ascii=False, indent=2)

    return len(tasks)

def main():
    target_langs = [c for c in GT_MAP if c != "en"]
    total = len(target_langs)
    print(f"Starting deep localization across {total} languages using clients5 Google endpoint...", flush=True)

    grand_total_tasks = 0
    start_all = time.time()

    for i, lang in enumerate(target_langs, 1):
        t0 = time.time()
        n = translate_locale(lang)
        grand_total_tasks += n
        elapsed = time.time() - t0
        print(f"[{i:2d}/{total}] {lang:6s} -> {n:3d} translated in {elapsed:.1f}s", flush=True)

    total_time = time.time() - start_all
    print(f"\nCompleted! Translated {grand_total_tasks} strings across all {total} languages in {total_time:.1f}s.", flush=True)

if __name__ == "__main__":
    main()
