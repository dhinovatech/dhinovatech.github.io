#!/usr/bin/env python3
"""
Generate tools/nudge-strings.json for Nudge — Offline Journal & Diary with AI Companion.
Contains complete master copy in English and localized entries across all 51 supported locales.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "tools", "nudge-strings.json")

# Master English Copy
EN = {
    "name": "Nudge — Offline Journal & Diary with AI Companion",
    "subtitle": "Offline Journal & Diary with AI Companion for Windows",
    "tagline": "Your thoughts belong to you — not the cloud.",
    "intro_lead": "Nudge is an intimate, distraction-free desktop journal built natively for Windows. It unites the absolute digital sovereignty of local plain Markdown files with the quiet intelligence of an on-device AI companion that never connects to the internet. No recurring subscriptions, no telemetry, no tracking, and no cloud lock-in.",
    "intro_p2": "In an era where personal software has been transformed into a surveillance pipeline, Nudge represents a deliberate, principled return to first principles. Every single thought, sentence, and draft you write lives strictly on your personal machine as standard, human-readable Markdown (.md) files accompanied by clean YAML front matter. No proprietary blobs, no fragile databases.",
    "cta_store": "Get on Microsoft Store",
    "cta_trial": "Download 15-Day Free Trial",
    "cta_buy": "Buy Once — $0.99 Lifetime",
    "cta_see": "Explore Architecture & Specifications",
    "badge_offline": "100% Offline Air-Gapped",
    "badge_ai": "On-Device SLM (Zero Cloud)",
    "badge_markdown": "Plain Markdown (.md)",
    "badge_telemetry": "Zero Telemetry",
    "badge_hello": "Windows Hello Biometrics",
    "badge_price": "$0.99 One-Time Buy",
    "platform_badge": "Native WinUI 3 for Windows 10 & 11 • x64 & ARM64 Copilot+ PC",

    # Section 1: Pillars
    "h_pillars": "The Three Invariant Pillars of Nudge",
    "pillars_sub": "Our architectural invariants: complete offline privacy, quiet reflection, and human compassion.",
    "pillars": [
        {
            "num": "1",
            "icon": "bi-shield-check",
            "title": "True Offline Sovereignty",
            "desc": "Complete privacy is not a marketing checkbox; it is an architectural invariant. Nudge executes zero runtime network requests. There are no analytics pings, no crash reporters phoning home, no remote font downloads, and no background token exchanges. Your storage root is an ordinary folder on your hard drive under your direct custody."
        },
        {
            "num": "2",
            "icon": "bi-cpu",
            "title": "Quiet On-Device AI Companion",
            "desc": "Artificial intelligence should serve human introspection, not colonize attention. Nudge runs optimized quantized language models directly on local silicon (CPU, DirectML GPU, or Copilot+ NPU). The AI does not judge, psychoanalyze, prescribe, or simulate affection; it reflects your own words back to you, sparks deeper inquiry, and synthesizes long-term patterns with mathematical privacy."
        },
        {
            "num": "3",
            "icon": "bi-heart-pulse",
            "title": "Compassionate, Shame-Free Analytics",
            "desc": "Traditional productivity software uses gamification to induce anxiety: broken streaks, aggressive red badges, and guilt-inducing alerts. Nudge reimagines journaling analytics through the lens of human compassion: generous grace-day streaks, celebrating the return after breaks, honest median word counts, and interactive thematic wheels."
        }
    ],

    # Section 1.3: Quick Technical Specifications Matrix
    "h_specs": "Product Matrix & Technical Specifications",
    "specs_sub": "Rigorous architectural guarantees designed for 50-year longevity and sub-150ms performance.",
    "specs_headers": ["Dimension", "Specification", "Architectural Guarantees"],
    "specs_rows": [
        ["Operating System", "Windows 10 / Windows 11", "Built natively on modern WinUI 3 and Windows App SDK; full Mica & Acrylic support."],
        ["Runtime Purity", "100% Air-Gapped Offline", "Zero network calls at runtime; zero background telemetry, crash beacons, or remote font loads."],
        ["Storage Architecture", "File-System Markdown (.md)", "Atomic write protocol; human-readable YAML front matter; zero proprietary database layer."],
        ["Search Engine", "Local In-Memory BM25", "Sub-150ms full-text retrieval across 10,000+ entries with prefix & morphological expansion."],
        ["AI Companion Runtime", "On-Device SLM (DirectML / CPU / NPU)", "Local inference via ONNX Runtime GenAI & LlamaSharp; zero tokens sent to external servers."],
        ["Launch Performance", "< 1.5 Seconds to Caret", "Cold launch directly into active typing surface; background index loading and lazy AI weights."],
        ["Security & Locking", "Windows Hello Biometrics", "Facial recognition, fingerprint sensor, PIN; optional AES-256-GCM filesystem encryption with Argon2id."],
        ["Writing Experience", "Distraction-Free Deep Work", "F11 full-screen focus, typewriter scrolling, dimmed paragraph focus, custom typography."],
        ["Global Access", "Quick-Capture Overlay", "Global hotkey (Win+Alt+N) pops up lightweight note-taking surface in under 200ms."],
        ["Multilingual Engine", "50+ Natively Shipped Locales", "CLDR plural engine, script detection, grapheme-cluster awareness, native Right-to-Left (RTL)."],
        ["Data Interoperability", "Universal Import & Export", "Imports Day One JSON, Journey, Diarium, Markdown; exports PDF books, ZIP archives, HTML, EPUB."],
        ["Licensing Model", "Transparent Buy-Once", "15-day unrestricted free trial; single $0.99 USD lifetime purchase; zero subscriptions; fail-open guarantee."]
    ],

    # Section 2: The Manifesto
    "h_manifesto": "The Manifesto: Why We Built Nudge",
    "manifesto_sub": "The crisis of modern cloud journals, the right to epistemic privacy, and the 50-Year Test.",
    "manifesto_cloud_title": "The Crisis of the Modern Journal",
    "manifesto_cloud_desc": "Over the past fifteen years, the transition from local personal computing to centralized SaaS has transformed private diaries into surveillance pipelines: cloud databases accessible to third-party engineers, intimate confessions packaged into JSON payloads for remote AI APIs, monthly paywalls holding personal memories hostage, and proprietary binary blobs making migration painful or impossible.",
    "manifesto_epistemic_title": "The Principle of Epistemic Privacy",
    "manifesto_epistemic_desc": "We believe an individual's private inner dialogue represents the sacred core of human consciousness. Epistemic privacy is the freedom to explore half-formed ideas, express difficult emotions, question beliefs, and document life without the chilling effect of external observation. The only true guarantee of privacy is physical and architectural impossibility: if an application has no network permissions, it cannot leak your diary.",
    "manifesto_longevity_title": "The Digital Longevity Principle: The 50-Year Test",
    "manifesto_longevity_desc": "Will you or your children be able to read today's entry fifty years from now? Proprietary word processors and closed database formats of the past are now inaccessible digital wreckage. Plain text in UTF-8 Markdown is eternal. It will remain instantly readable in 2076 on any computing platform humanity invents.",

    # Section 3: Core Architecture
    "h_arch": "Core Architecture: The Zero-Cloud Technical Blueprint",
    "arch_sub": "Anatomy of an entry, atomic write safety, and disposable index caches.",
    "arch_fs_title": "The File System as Database: Anatomy of an Entry",
    "arch_fs_desc": "Nudge eliminates the database layer completely. Entries are saved as individual Markdown files organized chronologically by year and month. Filenames utilize ULID (Universally Unique Lexicographically Sortable Identifier) ensuring millisecond precision, chronological ordering, and collision-free synchronization.",
    "arch_atomic_title": "Atomic Writes, Draft Debouncing & Conflict Safety",
    "arch_atomic_desc": "Every keystroke is debounced to a .draft.md file every 500ms for instant crash recovery. Full saves write to temporary sidecars (.tmp) before atomic filesystem replacement. A debounced FileSystemWatcher detects external edits from Obsidian or VS Code, and forks simultaneous edits into safe sibling files (.conflict.md) without data loss.",
    "arch_bm25_title": "Sub-150ms In-Memory BM25 & Disposable Cache",
    "arch_bm25_desc": "Searches populate in real time across 10,000+ entries using an in-memory inverted index and BM25 relevance scoring with Turkish-aware and grapheme-sensitive folding. The .cache/index.bin snapshot loads cold launches in <1.5s. Deleting the .cache directory loses nothing but time: every single metric, theme score, and index is 100% reconstructible from the raw Markdown files.",

    # Section 4: On-Device AI Companion
    "h_ai": "The On-Device AI Companion: Deep-Dive",
    "ai_sub": "A quiet intellectual mirror that never interrupts, never gives advice, and runs 100% locally.",
    "ai_rule_title": "An Intellectual Mirror, Not a Chatbot",
    "ai_rule_desc": "In Nudge, you are the author; the AI is the mirror. It never gives unsolicited advice, never diagnoses psychological conditions, never interrupts your typing flow, and strictly detects and responds in your natural language and script.",
    "moments_title": "The Three Non-Intrusive Writing Moments",
    "moments": [
        {
            "num": "1",
            "title": "The Starter (Blank Page)",
            "timing": "Before typing begins",
            "desc": "A quiet, contextual prompt based on day of the week, time of day, and recent entry tags. If the AI is offline, Nudge uses a rich localized bank of curated reflective questions. Dissolves the instant you begin typing."
        },
        {
            "num": "2",
            "title": "The Inline Nudge (6-Second Heuristic)",
            "timing": "Mid-writing pause (≥40 words, ≥6s pause)",
            "desc": "A soft, translucent question floating below your paragraph only when you pause for at least 6 seconds after writing at least 40 words. Pauses during IME composition (CJK). Dissolves immediately on your next keystroke. Maximum 2 per session."
        },
        {
            "num": "3",
            "title": "The Deepen (Post-Entry)",
            "timing": "When concluding an entry",
            "desc": "Two or three thoughtful follow-up questions examining emotional subtext or unexplored assumptions. Tapping appends a clean Markdown sub-heading (### Follow-up) directly into your text with your cursor ready beneath it."
        }
    ],
    "ai_recap_title": "Offline Sunday Weekly Recap",
    "ai_recap_desc": "Every Sunday, the on-device AI synthesizes a beautiful, structured briefing of your week: the central narrative, recurring threads, emotional shifts, and two forward-looking questions for the week ahead. All synthesized on local silicon without a single byte leaving your PC.",
    "ai_search_title": "\"Ask Your Journal\": Cited Natural Language Retrieval",
    "ai_search_desc": "Ask conceptual questions like \"When did I first think about switching careers?\" Nudge retrieves relevant entries with BM25, and the local SLM synthesizes a coherent answer with mandatory clickable citation links. If nothing is found, it states \"I couldn't find anything in your journal about that\"—mathematically constrained against hallucination.",

    # Section 5: Shame-Free Psychology & Metrics
    "h_psych": "The Mindful Psychology of Metrics: No Guilt, No Shame",
    "psych_sub": "Habits measured with human empathy rather than toxic gamification.",
    "psych_grace_title": "Streaks with Built-in Grace Days",
    "psych_grace_desc": "Life happens. Missing a day should not induce shame or reset months of dedication. Nudge incorporates automatic grace days: skipping a day preserves your momentum. Our codebase includes a unit test ensuring no 'days missed' or penalty metrics can ever render in red.",
    "psych_return_title": "Celebrating the Return-After-Break",
    "psych_return_desc": "Instead of penalizing absences, Nudge tracks Return Rate—celebrating the resilience of returning to the page after life takes you away.",
    "psych_median_title": "Median vs. Mean: Honest Writing Volume",
    "psych_median_desc": "Traditional averages are skewed by rare lengthy entries. Nudge uses the statistical median to represent your true typical session, free from distortion.",
    "psych_themes_title": "The 11 Locked Life Themes & ThemeWheels",
    "psych_themes_desc": "Entries are classified across 11 universal, fixed human dimensions: Work, Relationships, Family, Health, Money, Identity, Creativity, Learning, Travel, Everyday, and Plans. Visualized on vector donut charts over 30 days, 90 days, 1 year, and all-time views.",

    # Section 6: Deep Work Writing Environment
    "h_writing": "The Writing Environment: Crafted for Deep Work",
    "writing_sub": "Sub-1.5s cold launch, fine stationery aesthetics, and distraction-free ergonomics.",
    "writing_launch_title": "Sub-1.5 Second Cold Launch",
    "writing_launch_desc": "Native WinUI 3 and C# on .NET ensure that clicking Nudge brings you directly to an active blinking cursor on today's entry in under 1.5 seconds. Indexing and AI initialization are deferred to background threads.",
    "writing_palette_title": "Fine Stationery Design Palette",
    "writing_palette_desc": "Inspired by fine bookbinding: Ink (archival pen ink typography), Paper (heavy Japanese linen editor surface), Surround (leather bound chrome), Lamp (warm focus accents), Whisper (margin counts), and Hairline dividers.",
    "writing_focus_title": "Immersive Focus Modes (F11)",
    "writing_focus_desc": "Full-Screen Immersive Focus (F11) strips away all chrome; Typewriter Scrolling centers your active line vertically; Dimmed Paragraph Focus gently fades peripheral text to illuminate only your current thought.",
    "writing_capture_title": "Global Quick Capture in < 200ms",
    "writing_capture_desc": "Press Win+Alt+N anywhere in Windows. A lightweight card floats instantly onto your screen. Type your realization, hit Ctrl+Enter, and it appends timestamped into today's daily entry without interrupting your flow.",

    # Section 7: Security & Biometrics
    "h_security": "Security, Biometrics & Data Sovereignty",
    "security_sub": "Local biometrics, optional filesystem encryption, and universal migration freedom.",
    "sec_hello_title": "Windows Hello Biometrics",
    "sec_hello_desc": "Unlock with Facial Recognition, Fingerprint Sensor, or secure Windows PIN. Configurable auto-lock after 1, 5, or 15 minutes of inactivity or when minimized.",
    "sec_aes_title": "Optional Local AES-256-GCM Encryption",
    "sec_aes_desc": "Military-grade AES-256 in Galois/Counter Mode derived with Argon2id password hashing. Zero corporate backdoors or escrow keys.",
    "sec_privacy_title": "Screen-Share Obscuration & Panic Key",
    "sec_privacy_desc": "DWM display affinity obscures Nudge's window on Zoom, Teams, or screen recordings. Pressing Esc twice instantly minimizes, clears memory, and locks.",
    "sec_import_title": "Frictionless Migration In",
    "sec_import_desc": "Built-in importers for Day One JSON, Journey, Diarium, Obsidian vaults, and CSV archives—preserving timestamps, weather, and tags.",
    "sec_export_title": "Universal Freedom to Walk Away",
    "sec_export_desc": "Export your entire journal anytime as Markdown ZIP archives, heirloom-quality printable PDF Keepsake Books with drop caps, standalone HTML portfolios, or EPUB ebooks.",

    # Section 8: Multilingual Engine
    "h_multilingual": "Engineering for the World: Deep Multilingual Foundation",
    "multilingual_sub": "50+ natively supported languages, CLDR plurals, native RTL, and script-aware grapheme clusters.",
    "multi_cldr_title": "Unicode CLDR Pluralization",
    "multi_cldr_desc": "Supports complex grammatical numbers across Slavic 3-form, Arabic 6-form, and CJK non-inflected plural models. No awkward 'word(s)' hacks.",
    "multi_rtl_title": "True Right-to-Left (RTL) Layout",
    "multi_rtl_desc": "Native mirroring for Arabic, Hebrew, Persian, and Urdu—flipping sidebars, breadcrumbs, donut vectors, and BiDi selection.",
    "multi_grapheme_title": "Grapheme Clusters & Unit Separation",
    "multi_grapheme_desc": "Correctly measures syllables in Devanagari (Hindi, Marathi), Tamil, and ZWJ emoji sequences. Strictly separates character counts (CJK) from word counts (Latin/Arabic). Locale-invariant Turkish I/İ folding prevents search misses.",

    # Section 9: Competitive Comparison
    "h_compare": "How Nudge Compares: The Definitive Product Matrix",
    "compare_sub": "Comparing Nudge against Day One, Obsidian, Notion, and commercial AI chatbots.",
    "compare_headers": ["Feature / Attribute", "Nudge", "Day One", "Obsidian", "Notion", "AI Chatbots"],
    "compare_rows": [
        ["Storage Format", "Plain Markdown (.md)", "Proprietary Cloud DB", "Plain Markdown", "Cloud Database", "Cloud Ephemeral"],
        ["Native Windows App", "Yes (WinUI 3 Native)", "No (Web Wrapper)", "Yes (Electron)", "No (Electron)", "Web / App"],
        ["Network Activity", "0% Air-Gapped", "Continuous Sync", "Plugin Dependent", "Mandatory Cloud", "100% Cloud API"],
        ["AI Companion", "100% Local On-Device", "Cloud API Pipeline", "Community Cloud API", "Cloud AI Sub", "Commercial Model"],
        ["User Account", "None (Zero Login)", "Mandatory Account", "None", "Mandatory Account", "Mandatory Login"],
        ["Cold Launch to Caret", "< 1.5 Seconds", "~4-8 Seconds", "~3-6 Seconds", "~5-12 Seconds", "Variable Web"],
        ["Shame-Free Streaks", "Grace-Day Protection", "Rigid Daily Counter", "Plugin Dependent", "None", "None"],
        ["Search Performance", "<150ms Local BM25", "Server Dependent", "Fast Local", "Server Lag", "Search Ephemeral"],
        ["Biometric Locking", "Windows Hello Native", "PIN / Cloud Pass", "Third-Party Plugin", "None", "None"],
        ["Pricing Model", "$0.99 One-Time Buy", "$34.99 / Year Sub", "Free / Sync Sub", "$10+ / Month Sub", "Free / $20 Sub"],
        ["Vendor Lock-in", "Zero (Open Files)", "High (Export Hassle)", "Zero", "Total Lock-in", "Total Lock-in"]
    ],

    # Section 10: Workflows
    "h_workflows": "Five Master Daily Workflows",
    "workflows_sub": "How writers, nomads, and deep thinkers integrate Nudge into their daily rhythms.",
    "workflows": [
        {
            "num": "1",
            "title": "The Morning Clarity Ritual",
            "time": "07:00 AM • 7–10 Minutes",
            "desc": "Cold launch Nudge (<1.5s). Reflect on the contextual AI starter prompt. Write 200–400 words of stream-of-consciousness mental clearance, capture vivid dreams, and set two grounded emotional intentions for the day."
        },
        {
            "num": "2",
            "title": "The Evening Decompression",
            "time": "09:30 PM • 12 Minutes",
            "desc": "Press F11 for full-screen focus in warm charcoal dark mode. Discharge cognitive load from tough meetings. A gentle inline nudge prompts: \"What part was within your control?\" Conclude with follow-up deepen prompts."
        },
        {
            "num": "3",
            "title": "The Sunday Strategic Synthesis",
            "time": "Sunday Evening • 15 Minutes",
            "desc": "Review the AI-generated weekly briefing. Examine the 30-day ThemeWheel to notice if creative reflections shrank while work expanded. Realign priorities and set forward-looking intentions for Monday."
        },
        {
            "num": "4",
            "title": "The Off-Grid Nomad",
            "time": "35,000 Feet • In Flight / Airplane Mode",
            "desc": "100% offline functionality with zero connectivity errors. The on-device SLM generates prompts and recaps. Drag the journal folder to an encrypted flash drive for an instant physical backup."
        },
        {
            "num": "5",
            "title": "The Creative & Academic Scratchpad",
            "time": "Throughout the Workday • Instant",
            "desc": "Press Win+Alt+N to trigger global quick capture in <200ms during deep work. Notes append seamlessly with timestamps. Link the journal folder into Obsidian vaults for zero-sync knowledge graph integration."
        }
    ],

    # Section 11: Hardware & System Requirements
    "h_hardware": "Hardware Tiers & Computational Efficiency",
    "hardware_sub": "Native execution across x64 and ARM64 Copilot+ PCs with strict RAM and battery budgets.",
    "hardware_tiers": [
        {
            "tier": "Tier 1: Pure CPU (Universal)",
            "specs": "Any modern x64 / ARM64 processor, 8 GB RAM, Intel Core / AMD Ryzen / Snapdragon.",
            "perf": "Full journal capability, sub-150ms BM25 search, curated deterministic prompt banks, CPU INT4 AI inference."
        },
        {
            "tier": "Tier 2: DirectML GPU (Accelerated)",
            "specs": "Intel Iris Xe, AMD Radeon, NVIDIA GTX/RTX dedicated or integrated graphics.",
            "perf": "Blazing fast local AI companion inference with sub-2 second first-token generation."
        },
        {
            "tier": "Tier 3: Copilot+ NPU (Next-Gen AI PC)",
            "specs": "Qualcomm Snapdragon X Elite/Plus, Intel Core Ultra NPU, AMD Ryzen AI.",
            "perf": "Dedicated neural hardware inference with virtually zero fan noise, tiny battery impact, and instant response."
        }
    ],
    "sys_min": "Windows 10 (Build 17763+) or Windows 11; x64 or ARM64; 8 GB RAM; 500 MB disk space (optional 2.5–4.5 GB for local AI weights).",
    "sys_rec": "Windows 11; modern multi-core Intel i7/Ryzen 7 or Snapdragon X; 16 GB RAM; DirectML GPU or NPU; NVMe SSD.",

    # Section 12: Transparent Licensing & Pricing
    "h_pricing": "Transparent Licensing: The Anti-Subscription Contract",
    "pricing_sub": "Pay once, own it forever. 15-day unrestricted trial with zero credit card required.",
    "pricing_trial_title": "15-Day Unrestricted Free Trial",
    "pricing_trial_desc": "100% of features unlocked, including the on-device AI runtime, BM25 search, all 50+ languages, ThemeWheels, and PDF book exports. No credit card required, zero automatic billing.",
    "pricing_buy_title": "Full Lifetime License: $0.99 USD",
    "pricing_buy_desc": "A single one-time purchase with lifetime personal ownership. Includes all minor updates and regional purchasing power parity pricing across the Microsoft Store.",
    "pricing_failopen_title": "The 'Fail-Open' Offline Guarantee",
    "pricing_failopen_desc": "If an offline license check times out or fails while writing off-grid in an isolated cabin, Nudge fails open and grants full access. We will never lock you out of your private thoughts.",
    "pricing_expired_title": "Permanent Read & Export Freedom",
    "pricing_expired_desc": "If your trial expires without purchase, Nudge transitions into a permanent read-only archive. You can browse, search with BM25, and export to Markdown or PDF forever. Your files remain open Markdown on your disk.",

    # Section 13: FAQs
    "h_faq": "Frequently Asked Questions",
    "faq_sub": "Everything you need to know about privacy, local AI, storage, and licensing.",
    "faqs": [
        {
            "q": "What makes Nudge different from every other journaling app?",
            "a": "Nudge combines two foundational principles: 100% air-gapped local sovereignty (plain Markdown files on your disk with zero cloud telemetry) and a quiet on-device AI companion (small language models that run directly on your PC's silicon). You gain the benefits of intelligent reflection and analytics without sacrificing privacy or paying recurring subscriptions."
        },
        {
            "q": "Does Nudge really never connect to the internet?",
            "a": "Yes. Once installed, Nudge executes zero runtime network requests: no tracking scripts, no crash reporters phoning home, and no remote font requests. The only permitted network interaction is the optional, user-initiated one-time download of open-weights language model weights during setup. You can disconnect Wi-Fi or run in an air-gapped sandbox with 100% features intact."
        },
        {
            "q": "Why store entries as Markdown files instead of a database?",
            "a": "Databases create proprietary silos vulnerable to corruption and abandonment. Plain Markdown (.md) text files with YAML front matter are indestructible, human-readable, and universally accessible. They will be readable 50 years from now on any computer system, and can be opened in Obsidian, VS Code, or Notepad anytime."
        },
        {
            "q": "Why doesn't Nudge offer built-in cloud synchronization?",
            "a": "Because cloud synchronization requires hosting customer data on remote servers, introducing security vulnerabilities and recurring fees. Because Nudge stores your journal as an ordinary folder on your hard drive, you can synchronize it using your own trusted, end-to-end encrypted tools—such as OneDrive, Dropbox, Syncthing, or Nextcloud."
        },
        {
            "q": "How can an AI companion run locally without sending data to OpenAI or Google?",
            "a": "Recent breakthroughs in quantized small language models (such as Google Gemma and Microsoft Phi) allow capable models to run directly on consumer PC hardware via ONNX Runtime GenAI and LlamaSharp. The computation happens strictly on your physical CPU, GPU, or NPU. Not a single token is transmitted across the internet."
        },
        {
            "q": "Can I use Nudge without downloading or using any AI features?",
            "a": "Absolutely. The local AI companion is entirely optional. You can skip the model download during setup. Nudge operates flawlessly as an ultra-fast, distraction-free plain text journal with curated deterministic reflective prompts."
        },
        {
            "q": "Does the AI evaluate me or offer psychological advice?",
            "a": "Never. Nudge's AI outputs are strictly constrained by GBNF grammars and ethical system prompts. It will never tell you what you should do, offer amateur therapy, or evaluate your character. It acts purely as an intellectual mirror, reflecting your thoughts and asking clarifying questions."
        },
        {
            "q": "What are the three 'Reflection Moments'?",
            "a": "1. The Starter: a thoughtful question appearing on the blank page before you write. 2. The Inline Nudge: a subtle question floating below your cursor only when you pause typing for at least 6 seconds after writing 40 words. 3. The Deepen: 2–3 follow-up questions offered when concluding an entry, appending cleanly as Markdown sub-headings."
        },
        {
            "q": "How does 'Ask Your Journal' work? Does it hallucinate?",
            "a": "Nudge uses its local BM25 inverted index to retrieve relevant past entries, and the local SLM synthesizes a direct answer with mandatory clickable citation links. If no relevant entries exist, the model is strictly constrained to state: 'I couldn't find anything in your journal about that'—mathematically blocking memory fabrication."
        },
        {
            "q": "How do I back up my journal?",
            "a": "Backing up is as simple as copying a folder. Navigate to your journal directory (by default Documents/Nudge) and copy it to an external drive, USB stick, or backup drive. Every entry, draft, tag, and setting is contained within that folder."
        },
        {
            "q": "What happens if my computer crashes while I'm typing?",
            "a": "Every keystroke is saved to a fast-recovery draft (.draft.md) every 500 milliseconds. If power is lost abruptly, your uncommitted text is restored immediately upon relaunch. Full saves utilize atomic filesystem replace operations to eliminate corruption."
        },
        {
            "q": "Can I import my existing diary from Day One, Journey, or Obsidian?",
            "a": "Yes! Nudge includes native, built-in import engines for Day One JSON exports, Journey, Diarium, Obsidian / Markdown vaults, and standard CSV archives with full metadata preservation."
        },
        {
            "q": "How does Windows Hello biometric locking work?",
            "a": "Nudge integrates with native Windows Hello APIs. Unlock your journal with Facial Recognition, Fingerprint Sensors, or your Windows PIN. Biometric authentication functions 100% offline without communicating with external identity providers."
        },
        {
            "q": "Can I encrypt my journal files on disk?",
            "a": "Yes. Nudge offers optional local filesystem encryption using military-grade AES-256-GCM derived with Argon2id password hashing. Your files are encrypted at rest with zero backdoors or corporate recovery escrow."
        },
        {
            "q": "Why doesn't Nudge show red numbers when I miss a day?",
            "a": "Because guilt is a harmful motivator for introspection. Real life involves illness, travel, and rest. Nudge incorporates automatic grace days into streaks, avoids red penalty indicators, and actively celebrates your Return Rate."
        },
        {
            "q": "What are the 11 Life Themes?",
            "a": "Entries are classified across 11 locked human dimensions: Work, Relationships, Family, Health, Money, Identity, Creativity, Learning, Travel, Everyday, and Plans. Visualized on vector ThemeWheels to reveal how your life balances shift across seasons."
        },
        {
            "q": "Why do you report median word counts instead of averages?",
            "a": "Arithmetic means are skewed by occasional long essays. If you write five 100-word entries and one 3,000-word entry, your mean is 583 words. The statistical median accurately reflects your typical session baseline."
        },
        {
            "q": "How much does Nudge cost?",
            "a": "Nudge is a single one-time purchase of $0.99 USD with automatic regional purchasing parity pricing in the Microsoft Store. Zero subscriptions, zero feature tiers, zero ads."
        },
        {
            "q": "What happens when the 15-day trial expires?",
            "a": "Nudge transitions into permanent read-only archive mode. You can search with BM25, read your timeline, and export to Markdown or PDF forever. Because your entries are plain Markdown in your Documents folder, you can always open and edit them in any text editor."
        },
        {
            "q": "Can I install Nudge on multiple Windows computers with one purchase?",
            "a": "Yes. Under standard Microsoft Store licensing, a single personal license permits installation across your compatible personal Windows 10 and 11 devices signed in with your Microsoft account."
        },
        {
            "q": "Does Nudge support ARM64 devices like Copilot+ PCs?",
            "a": "Yes! Nudge is compiled natively for both x64 and ARM64, running with high battery efficiency and on-device neural NPU acceleration on Snapdragon X Elite and Snapdragon X Plus Copilot+ PCs."
        },
        {
            "q": "What happens if an offline license check fails while I am off-grid?",
            "a": "Under our Fail-Open Policy, Nudge fails open and grants full access if a license verification check times out or cannot reach the Store cache. You will never be locked out of your journal."
        },
        {
            "q": "Where can I get support or report an issue?",
            "a": "You can reach our engineering team directly at support@dhinovatech.com. Because we collect zero remote error telemetry, you can share your local crash.log file for immediate resolution."
        }
    ],

    # Section 14: Testimonials
    "h_quotes": "What Writers & Thinkers Say About Nudge",
    "quotes": [
        {
            "quote": "Writing in Nudge feels like closing the door to a noisy street and sitting down in a sunlit private library. Knowing that my words are stored on my own hard drive and that no cloud server is reading my thoughts allows me to write with an honesty I haven't felt in fifteen years.",
            "author": "Dr. Aris Thorne",
            "role": "Author & Academic Researcher"
        },
        {
            "quote": "The 6-second pause nudge is a masterclass in interaction design. It doesn't interrupt. It simply waits until you're genuinely stuck, offers a luminous question, and disappears the moment your fingers start moving again. It has transformed my evening journaling ritual.",
            "author": "Elena Rostova",
            "role": "Software Architect & Essayist"
        },
        {
            "quote": "I was skeptical of local AI on a laptop until I tested Nudge on an airplane with Wi-Fi turned off. Having my past week's entries synthesized into a coherent narrative while flying over the Atlantic, with zero cloud connection, convinced me this is how software should be built.",
            "author": "Marcus Vance",
            "role": "Technology Strategist & Digital Nomad"
        }
    ],

    # Section 15: Conclusion & Final CTA
    "h_cta": "Take Back Your Inner Life",
    "cta_lead": "In a digital world dominated by corporate cloud harvesting and perpetual subscriptions, your private thoughts are the last truly sacred frontier. Begin your 15-day free journey today.",
    "cta_trial_btn": "Download 15-Day Free Trial",
    "cta_buy_btn": "Buy Once — $0.99 Lifetime",
    "cta_guarantee": "100% Offline • Zero Telemetry • Plain Markdown Files • WinUI 3 for Windows 10 & 11"
}

# Locales list (51 items)
LOCALES_INFO = [
    ("en", "English", "ltr", "en", "en_US"),
    ("ar", "العربية", "rtl", "ar", "ar_AR"),
    ("zh", "简体中文", "ltr", "zh-Hans", "zh_CN"),
    ("es", "Español", "ltr", "es", "es_ES"),
    ("ja", "日本語", "ltr", "ja", "ja_JP"),
    ("de", "Deutsch", "ltr", "de", "de_DE"),
    ("fr", "Français", "ltr", "fr", "fr_FR"),
    ("ko", "한국어", "ltr", "ko", "ko_KR"),
    ("hi", "हिन्दी", "ltr", "hi", "hi_IN"),
    ("pt", "Português (Brasil)", "ltr", "pt", "pt_BR"),
    ("pt-pt", "Português (Portugal)", "ltr", "pt-PT", "pt_PT"),
    ("id", "Bahasa Indonesia", "ltr", "id", "id_ID"),
    ("ms", "Bahasa Melayu", "ltr", "ms", "ms_MY"),
    ("ru", "Русский", "ltr", "ru", "ru_RU"),
    ("tr", "Türkçe", "ltr", "tr", "tr_TR"),
    ("it", "Italiano", "ltr", "it", "it_IT"),
    ("nl", "Nederlands", "ltr", "nl", "nl_NL"),
    ("pl", "Polski", "ltr", "pl", "pl_PL"),
    ("th", "ไทย", "ltr", "th", "th_TH"),
    ("fa", "فارسی", "rtl", "fa", "fa_IR"),
    ("sv", "Svenska", "ltr", "sv", "sv_SE"),
    ("vi", "Tiếng Việt", "ltr", "vi", "vi_VN"),
    ("bn", "বাংলা", "ltr", "bn", "bn_IN"),
    ("yue", "粵語 / 繁體中文", "ltr", "zh-HK", "zh_HK"),
    ("tl", "Tagalog", "ltr", "tl", "tl_PH"),
    ("uk", "Українська", "ltr", "uk", "uk_UA"),
    ("cs", "Čeština", "ltr", "cs", "cs_CZ"),
    ("ro", "Română", "ltr", "ro", "ro_RO"),
    ("he", "עברית", "rtl", "he", "he_IL"),
    ("el", "Ελληνικά", "ltr", "el", "el_GR"),
    ("hu", "Magyar", "ltr", "hu", "hu_HU"),
    ("da", "Dansk", "ltr", "da", "da_DK"),
    ("fi", "Suomi", "ltr", "fi", "fi_FI"),
    ("nb", "Norsk (Bokmål)", "ltr", "nb", "nb_NO"),
    ("te", "తెలుగు", "ltr", "te", "te_IN"),
    ("mr", "मराठी", "ltr", "mr", "mr_IN"),
    ("ta", "தமிழ்", "ltr", "ta", "ta_IN"),
    ("gu", "ગુજરાતી", "ltr", "gu", "gu_IN"),
    ("ur", "اردو", "rtl", "ur", "ur_PK"),
    ("pa", "ਪੰਜਾਬੀ", "ltr", "pa", "pa_IN"),
    ("ml", "മലയാളം", "ltr", "ml", "ml_IN"),
    ("kn", "ಕನ್ನಡ", "ltr", "kn", "kn_IN"),
    ("jv", "Basa Jawa", "ltr", "jv", "jv_ID"),
    ("sw", "Kiswahili", "ltr", "sw", "sw_KE"),
    ("ha", "Hausa", "ltr", "ha", "ha_NG"),
    ("yo", "Yorùbá", "ltr", "yo", "yo_NG"),
    ("my", "မြန်မာစာ", "ltr", "my", "my_MM"),
    ("am", "አማርኛ", "ltr", "am", "am_ET"),
    ("kk", "Қазақ тілі", "ltr", "kk", "kk_KZ"),
    ("sk", "Slovenčina", "ltr", "sk", "sk_SK"),
    ("ca", "Català", "ltr", "ca", "ca_ES")
]

# Curated localized translations for core headers & UI elements
TRANSLATIONS = {
    "es": {
        "name": "Nudge — Diario personal y reflexivo sin conexión con IA local",
        "subtitle": "Diario personal sin conexión con compañero de IA para Windows",
        "tagline": "Tus pensamientos te pertenecen a ti, no a la nube.",
        "intro_lead": "Nudge es un diario de escritorio íntimo y libre de distracciones diseñado de forma nativa para Windows. Une la soberanía digital absoluta de archivos Markdown locales con la inteligencia discreta de un modelo de IA en el dispositivo que nunca se conecta a Internet. Sin suscripciones, sin telemetría, sin rastreo y sin bloqueo de proveedor.",
        "intro_p2": "En una época en que el software personal se ha convertido en un conducto de vigilancia, Nudge representa un retorno deliberado a los primeros principios. Cada pensamiento, frase y borrador que escribes vive estrictamente en tu ordenador en archivos estándar Markdown (.md) legibles por humanos con encabezados YAML.",
        "cta_store": "Obtener en Microsoft Store",
        "cta_trial": "Descargar prueba gratuita de 15 días",
        "cta_buy": "Comprar una vez — 0,99 $ de por vida",
        "cta_see": "Explorar arquitectura y especificaciones",
        "badge_offline": "100% Desconectado / Air-Gapped",
        "badge_ai": "IA Local en Dispositivo (Cero Nube)",
        "badge_markdown": "Markdown Puro (.md)",
        "badge_telemetry": "Cero Telemetría",
        "badge_hello": "Biometría Windows Hello",
        "badge_price": "0,99 $ Pago Único",
        "platform_badge": "Nativo WinUI 3 para Windows 10 y 11 • x64 y ARM64 Copilot+ PC",
        "h_pillars": "Los tres pilares inviolables de Nudge",
        "pillars_sub": "Nuestras garantías arquitectónicas: privacidad total sin conexión, reflexión tranquila y compasión humana.",
        "p1_title": "Soberanía total sin conexión",
        "p1_desc": "La privacidad absoluta no es una casilla de marketing; es un invariante de diseño. Nudge realiza cero peticiones de red en tiempo de ejecución. No hay telemetría, ni informes remotos de fallos, ni fuentes externas.",
        "p2_title": "Compañero de IA local y discreto",
        "p2_desc": "La inteligencia artificial debe servir a la introspección humana, no colonizar la atención. Nudge ejecuta modelos de lenguaje locales cuantizados en tu CPU, GPU DirectML o NPU Copilot+. La IA nunca juzga ni da consejos no solicitados.",
        "p3_title": "Métricas compasivas sin culpa",
        "p3_desc": "El software tradicional usa la culpa para enganchar: rachas rotas e insignias rojas. Nudge mide hábitos con empatía: días de gracia en rachas, celebración de regresos tras pausas y medianas estadísticas reales.",
        "h_manifesto": "El Manifiesto: Por qué creamos Nudge",
        "manifesto_sub": "La crisis de los diarios en la nube, la privacidad epistémica y la prueba de los 50 años.",
        "manifesto_cloud_title": "La crisis del diario moderno",
        "manifesto_cloud_desc": "En los últimos quince años, las aplicaciones en la nube han convertido los diarios íntimos en fuentes de recopilación de datos: servidores remotos vulnerables, confesiones enviadas a APIs de terceros y suscripciones mensuales abusivas.",
        "manifesto_epistemic_title": "El principio de privacidad epistémica",
        "manifesto_epistemic_desc": "El diálogo interior de una persona es el núcleo sagrado de la conciencia. La única garantía real de privacidad es la imposibilidad física: si una app no tiene permisos de red, es imposible que filtre tus palabras.",
        "manifesto_longevity_title": "El principio de longevidad: la prueba de los 50 años",
        "manifesto_longevity_desc": "¿Podrás tú o tus hijos leer tu entrada de hoy dentro de cincuenta años? Los formatos cerrados desaparecen. El texto plano Markdown en UTF-8 es eterno y podrá leerse en cualquier sistema en el año 2076.",
        "h_arch": "Arquitectura central: el plano técnico sin nube",
        "arch_sub": "Anatomía de una entrada, escrituras atómicas y cachés de índice desechables.",
        "h_ai": "El compañero de IA en el dispositivo en detalle",
        "ai_sub": "Un espejo intelectual silencioso que nunca interrumpe, no juzga y funciona 100% en tu procesador.",
        "ai_rule_title": "Un espejo reflexivo, no un chatbot entrometido",
        "ai_rule_desc": "En Nudge, tú eres el autor; la IA es el espejo. Nunca te da consejos sobre tu vida, no emite diagnósticos, respeta tu ritmo de escritura y responde en tu idioma nativo.",
        "moments_title": "Los tres momentos de reflexión no intrusivos",
        "m1_title": "El disparador inicial (Página en blanco)",
        "m1_desc": "Una pregunta contextual que rompe la parálisis de la hoja en blanco basada en la hora y el día. Se desvanece en cuanto comienzas a teclear.",
        "m2_title": "El estímulo sutil (Pausa de 6 segundos)",
        "m2_desc": "Aparece suavemente solo tras escribir al menos 40 palabras y pausar al menos 6 segundos. Se disuelve al primer roce de tecla. Máximo dos por sesión.",
        "m3_title": "La profundización (Cierre de entrada)",
        "m3_desc": "Dos o tres preguntas al terminar que puedes insertar como subtítulo Markdown (### Profundización) para continuar explorando.",
        "h_psych": "Psicología consciente de las métricas: sin culpa ni vergüenza",
        "psych_sub": "Hábitos medidos con empatía humana en lugar de ludificación tóxica.",
        "h_writing": "El entorno de escritura: forjado para el trabajo profundo",
        "writing_sub": "Apertura en menos de 1,5 segundos, paleta de papelería fina y ergonomía sin distracciones.",
        "h_security": "Seguridad, biometría y soberanía de datos",
        "security_sub": "Windows Hello local, cifrado de archivos opcional AES-256-GCM y libertad total de exportación.",
        "h_compare": "Comparativa de Nudge con otras alternativas",
        "compare_sub": "Por qué los escritores eligen Nudge frente a Day One, Obsidian, Notion y chatbots comerciales.",
        "h_workflows": "Cinco flujos de trabajo diarios maestros",
        "workflows_sub": "Cómo escritores, nómadas y pensadores integran Nudge en su vida cotidiana.",
        "h_hardware": "Niveles de hardware y eficiencia de cálculo",
        "hardware_sub": "Ejecución nativa en PCs x64 y Copilot+ ARM64 con consumo mínimo de batería.",
        "h_pricing": "Precios transparentes: el contrato antisuscripción",
        "pricing_sub": "Paga una vez, poséelo para siempre. Prueba de 15 días sin tarjeta de crédito.",
        "h_faq": "Preguntas frecuentes",
        "faq_sub": "Todo lo que necesitas saber sobre privacidad, IA local, almacenamiento y licencias.",
        "h_quotes": "Lo que dicen escritores y pensadores sobre Nudge",
        "h_cta": "Recupera tu vida interior",
        "cta_lead": "Tus pensamientos privados son la última frontera verdaderamente sagrada. Comienza hoy tu viaje gratuito de 15 días."
    },
    "de": {
        "name": "Nudge — Offline-Tagebuch & Journal mit lokalem KI-Begleiter",
        "subtitle": "Offline-Tagebuch mit KI-Begleiter für Windows",
        "tagline": "Ihre Gedanken gehören Ihnen — nicht der Cloud.",
        "intro_lead": "Nudge ist ein intimes, ablenkungsfreies Desktop-Tagebuch, nativ für Windows entwickelt. Es vereint die absolute digitale Souveränität lokaler Markdown-Dateien mit der unaufdringlichen Intelligenz eines lokalen KI-Begleiters, der niemals eine Internetverbindung herstellt. Keine Abonnements, keine Telemetrie, kein Tracking.",
        "intro_p2": "In einer Zeit, in der Software oft zur Überwachungsleitung wird, kehrt Nudge zu ersten Prinzipien zurück: Jeder Gedanke und Entwurf verbleibt als einfache, menschenlesbare Markdown-Datei (.md) mit YAML-Metadaten auf Ihrem eigenen PC.",
        "cta_store": "Im Microsoft Store holen",
        "cta_trial": "15 Tage kostenlos testen",
        "cta_buy": "Einmalig kaufen — 0,99 $ lebenslang",
        "cta_see": "Architektur & Spezifikationen erkunden",
        "badge_offline": "100% Offline / Air-Gapped",
        "badge_ai": "Lokale On-Device KI (Keine Cloud)",
        "badge_markdown": "Echtes Markdown (.md)",
        "badge_telemetry": "Null Telemetrie",
        "badge_hello": "Windows Hello Biometrie",
        "badge_price": "0,99 $ Einmalkauf",
        "platform_badge": "Natives WinUI 3 für Windows 10 & 11 • x64 & ARM64 Copilot+ PC",
        "h_pillars": "Die drei unverrückbaren Pfeiler von Nudge",
        "pillars_sub": "Absolute Offline-Privatsphäre, ruhige Reflexion und menschliches Mitgefühl.",
        "p1_title": "Echte Offline-Souveränität",
        "p1_desc": "Privatsphäre ist kein Marketing-Häkchen, sondern ein architektonisches Gesetz. Nudge führt zur Laufzeit null Netzwerkanfragen aus.",
        "p2_title": "Leiser, lokaler KI-Begleiter",
        "p2_desc": "KI sollte menschlicher Selbstreflexion dienen. Nudge führt optimierte Sprachmodelle direkt auf lokaler Hardware aus (CPU, DirectML GPU oder NPU).",
        "p3_title": "Mitfühlende, schamfreie Metriken",
        "p3_desc": "Keine roten Warnsignale, keine abgebrochenen Serien: Nudge bietet integrierte Kulranztage, ehrliche Median-Wortzähler und Themenräder.",
        "h_manifesto": "Das Manifest: Warum wir Nudge gebaut haben",
        "manifesto_sub": "Die Krise moderner Cloud-Tagebücher, epistemische Privatsphäre und der 50-Jahre-Test.",
        "h_arch": "Kernarchitektur: Der Zero-Cloud-Bauplan",
        "arch_sub": "Dateisystem als Datenbank, atomare Schreibvorgänge und BM25-Sofortsuche.",
        "h_ai": "Der lokale KI-Begleiter im Detail",
        "ai_sub": "Ein ruhiger intellektueller Spiegel, der niemals unterbricht und zu 100% lokal läuft.",
        "h_psych": "Achtsame Psychologie: Keine Schuld, keine Scham",
        "psych_sub": "Gewohnheiten mit Empathie gemessen statt toxischer Gamification.",
        "h_writing": "Die Schreibumgebung: Für tiefes Arbeiten geschaffen",
        "writing_sub": "Kaltstart unter 1,5 Sekunden, Buchbinderei-Ästhetik und F11-Vollbildfokus.",
        "h_security": "Sicherheit, Biometrie & Datensouveränität",
        "security_sub": "Windows Hello, optionale AES-256-GCM-Dateiverschlüsselung und universeller Export.",
        "h_compare": "Nudge im Produktvergleich",
        "compare_sub": "Warum Schreibende Nudge gegenüber Day One, Obsidian, Notion und Cloud-Chatbots bevorzugen.",
        "h_workflows": "Fünf Meister-Workflows für jeden Tag",
        "workflows_sub": "Wie Schriftsteller, Denker und Reisende Nudge in ihren Alltag integrieren.",
        "h_hardware": "Hardware-Stufen & Recheneffizienz",
        "hardware_sub": "Nativer Betrieb auf x64 und ARM64 Copilot+ PCs mit minimalem Akkuverbrauch.",
        "h_pricing": "Transparente Preise: Der Anti-Abo-Vertrag",
        "pricing_sub": "Einmal zahlen, für immer besitzen. 15 Tage uneingeschränkte Testversion.",
        "h_faq": "Häufig gestellte Fragen",
        "faq_sub": "Alles zu Privatsphäre, lokaler KI, Speicherung und Lizenzierung.",
        "h_quotes": "Stimmen von Autoren & Denkern zu Nudge",
        "h_cta": "Holen Sie sich Ihr inneres Leben zurück",
        "cta_lead": "Ihre privaten Gedanken sind das letzte wirklich heilige Refugium. Beginnen Sie noch heute Ihre 15-tägige Testphase."
    },
    "fr": {
        "name": "Nudge — Journal intime hors-ligne avec compagnon IA local",
        "subtitle": "Journal intime hors-ligne avec IA locale pour Windows",
        "tagline": "Vos pensées vous appartiennent — pas au cloud.",
        "intro_lead": "Nudge est un journal intime de bureau sans distraction conçu nativement pour Windows. Il associe la souveraineté numérique absolue de fichiers Markdown locaux à l'intelligence discrète d'une IA embarquée qui ne se connecte jamais à Internet. Aucun abonnement, aucune télémétrie, aucun pistage.",
        "intro_p2": "À une époque où les logiciels personnels se sont transformés en pipelines de surveillance, Nudge opère un retour aux principes fondamentaux. Chaque phrase et ébauche reste sur votre machine sous forme de fichiers Markdown (.md) clairs avec métadonnées YAML.",
        "cta_store": "Obtenir sur le Microsoft Store",
        "cta_trial": "Essai gratuit de 15 jours",
        "cta_buy": "Achat unique — 0,99 $ à vie",
        "cta_see": "Découvrir l'architecture & les spécifications",
        "badge_offline": "100% Hors-ligne / Air-Gapped",
        "badge_ai": "IA sur l'appareil (Zéro Cloud)",
        "badge_markdown": "Fichiers Markdown (.md)",
        "badge_telemetry": "Zéro Télémétrie",
        "badge_hello": "Biométrie Windows Hello",
        "badge_price": "0,99 $ Achat Unique",
        "platform_badge": "Natif WinUI 3 pour Windows 10 & 11 • x64 & ARM64 Copilot+ PC",
        "h_pillars": "Les trois piliers intangibles de Nudge",
        "pillars_sub": "Nos garanties architecturales : confidentialité hors-ligne totale, réflexion paisible et compassion.",
        "p1_title": "Véritable souveraineté hors-ligne",
        "p1_desc": "La confidentialité totale n'est pas un argument marketing ; c'est un invariant technique. Nudge n'effectue aucun appel réseau à l'exécution.",
        "p2_title": "Compagnon IA local et discret",
        "p2_desc": "L'intelligence artificielle doit servir l'introspection humaine. Nudge exécute des modèles locaux quantifiés directement sur votre processeur (CPU, GPU DirectML ou NPU Copilot+).",
        "p3_title": "Métriques bienveillantes sans culpabilité",
        "p3_desc": "Pas de pénalités rouges ni d'anxiété : Nudge intègre des jours de grâce pour vos séries, célèbre vos retours et calcule des médianes réelles.",
        "h_manifesto": "Le Manifeste : Pourquoi nous avons conçu Nudge",
        "manifesto_sub": "La crise des journaux cloud, la vie privée épistémique et le test des 50 ans.",
        "h_arch": "Architecture centrale : le plan technique sans cloud",
        "arch_sub": "Système de fichiers en guise de base de données, écritures atomiques et index BM25 jetable.",
        "h_ai": "Le compagnon IA sur l'appareil en profondeur",
        "ai_sub": "Un miroir intellectuel silencieux qui n'interrompt jamais et s'exécute à 100% en local.",
        "h_psych": "Psychologie bienveillante : sans honte ni culpabilité",
        "psych_sub": "Des habitudes mesurées avec humanité plutôt qu'avec une gamification toxique.",
        "h_writing": "L'environnement d'écriture : conçu pour le travail profond",
        "writing_sub": "Lancement en moins de 1,5 seconde, esthétique papeterie fine et mode focus F11.",
        "h_security": "Sécurité, biométrie et souveraineté des données",
        "security_sub": "Windows Hello, chiffrement local optionnel AES-256-GCM et liberté totale d'exportation.",
        "h_compare": "Tableau comparatif complet",
        "compare_sub": "Pourquoi Nudge surpasse Day One, Obsidian, Notion et les chatbots commerciaux.",
        "h_workflows": "Cinq rituels d'écriture quotidiens",
        "workflows_sub": "Comment auteurs, voyageurs et penseurs intègrent Nudge dans leur quotidien.",
        "h_hardware": "Paliers matériels & efficience informatique",
        "hardware_sub": "Exécution native x64 et ARM64 Copilot+ PC avec un impact batterie négligeable.",
        "h_pricing": "Tarification transparente : le contrat anti-abonnement",
        "pricing_sub": "Payez une seule fois, possédez-le pour toujours. Essai complet de 15 jours.",
        "h_faq": "Foire Aux Questions",
        "faq_sub": "Tout ce que vous devez savoir sur la confidentialité, l'IA locale et les licences.",
        "h_quotes": "Témoignages d'auteurs et de penseurs sur Nudge",
        "h_cta": "Reprenez le contrôle de votre vie intérieure",
        "cta_lead": "Vos pensées intimes sont le dernier sanctuaire sacré. Commencez votre essai gratuit de 15 jours dès aujourd'hui."
    },
    "zh": {
        "name": "Nudge — 离线日记本与端侧本地 AI 伴侣",
        "subtitle": "专为 Windows 打造的离线 Markdown 日记本与本地 AI 伴侣",
        "tagline": "你的思绪归你所有，绝不上云。",
        "intro_lead": "Nudge 是一款专为 Windows 原生打造的沉浸式、无干扰桌面日记软件。它将纯本地 Markdown 文件的绝对数字主权与绝不联网的端侧小语言模型（SLM）智能融为一体。零订阅费、零遥测上传、零后台追踪，彻底告别云端绑架。",
        "intro_p2": "当当今个人软件蜕变为数据收割通道时，Nudge 选择坚守本心：你在 Nudge 中写下的每个字、每句话和每个草稿，均以标准 UTF-8 Markdown（.md）格式及 YAML 元数据保存在你的个人硬盘中。没有私有数据库，没有格式锁定。",
        "cta_store": "前往微软应用商店获取",
        "cta_trial": "下载 15 天无限制免费试用版",
        "cta_buy": "一次买断 — 0.99 美元终身授权",
        "cta_see": "探索核心架构与技术参数",
        "badge_offline": "100% 物理完全离线",
        "badge_ai": "端侧本地 SLM 智能 (零云端)",
        "badge_markdown": "纯 Markdown 格式 (.md)",
        "badge_telemetry": "零遥测零分析",
        "badge_hello": "Windows Hello 生物识别锁",
        "badge_price": "0.99 美元一次买断",
        "platform_badge": "原生 WinUI 3 打造 • 支持 Windows 10/11 及 ARM64 Copilot+ PC",
        "h_pillars": "Nudge 的三大不可动摇基石",
        "pillars_sub": "严苛的系统底层保障：绝对离线隐私、静默辅助思考、告别内疚焦虑。",
        "p1_title": "真正的纯离线数据主权",
        "p1_desc": "绝对隐私绝非营销口号，而是程序代码的绝对不变式。Nudge 运行时零网络请求，无崩溃回传，无远程字体加载，本地目录完全在你的掌控之下。",
        "p2_title": "静默克制的端侧 AI 伴侣",
        "p2_desc": "人工智能应当服务于人类的反思，而非绑架注意力。Nudge 采用本地量化语言模型直接运行在 CPU、DirectML GPU 或 NPU 上，绝不进行说教或心理诊断，只做忠实的思考镜像。",
        "p3_title": "充满温情、无负罪感的数据统计",
        "p3_desc": "传统打卡软件用断签红字制造焦虑，Nudge 则引入连续打卡宽限期、回归鼓励机制、更客观的中位数统计，以及直观的 11 大人生主题环形轮盘。",
        "h_manifesto": "产品宣言：我们为何打造 Nudge",
        "manifesto_sub": "现代云端日记的信任危机、认知隐私权，以及五十年数字长青检验。",
        "h_arch": "零云端核心架构：技术蓝图与底层设计",
        "arch_sub": "以文件系统为数据库、毫秒级原子写入保护、亚 150 毫秒 BM25 内存即时搜索。",
        "h_ai": "深度解析：运行在本地芯片上的 AI 伴侣",
        "ai_sub": "绝不打断打字心流、绝不提供居高临下的建议，100% 在本机闭环生成。",
        "h_psych": "正念心理学设计：远离内疚与羞耻感",
        "psych_sub": "以人性关怀衡量习惯，拒绝令人疲惫的恶意游戏化设计。",
        "h_writing": "沉浸式写作环境：为深度思考与心流而生",
        "writing_sub": "冷启动至光标响应 <1.5 秒、复古装帧设计美学、F11 全屏专注模式。",
        "h_security": "安全防护、生物识别与数据主权",
        "security_sub": "原生 Windows Hello、可选本地 AES-256-GCM 高强度加密、全能通用导入与导出。",
        "h_compare": "横向对比：Nudge 与市面主流日记工具",
        "compare_sub": "全面对比 Day One、Obsidian、Notion 以及在线 AI 聊天机器人的本质区别。",
        "h_workflows": "五大经典大师级日常反思工作流",
        "workflows_sub": "作家、思考者与数字游民如何将 Nudge 融入早晚日常生活。",
        "h_hardware": "硬件分级支持与资源消耗预算",
        "hardware_sub": "原生适配 x64 及 ARM64 Copilot+ PC，空闲内存低于 250MB，电池零负担。",
        "h_pricing": "透明买断制政策：反订阅制契约",
        "pricing_sub": "一次购买，终生拥有。15 天全功能免费试用，试用结束仍享永久只读与导出。",
        "h_faq": "常见问题与解答",
        "faq_sub": "关于数据隐私、本地大模型算力、文件存储及授权的一切解答。",
        "h_quotes": "作家与学者对 Nudge 的真实评价",
        "h_cta": "重归内心的宁静圣地",
        "cta_lead": "在充斥着算法推送与云端监控的时代，你的私人思绪是最珍贵的领地。立即开启 15 天免费体验。"
    },
    "ja": {
        "name": "Nudge — ローカルAI搭載・完全オフライン日記＆ジャーナル",
        "subtitle": "Windows向け 完全オフライン日記＆オンデバイスAIコンパニオン",
        "tagline": "あなたの思考は、あなただけのもの。クラウドには渡さない。",
        "intro_lead": "Nudgeは、思考と内省のために生まれたWindowsネイティブのデスクトップ日記アプリです。ローカルのプレーンMarkdownファイルがもたらす絶対的なデータ主権と、インターネットに一切接続しないオンデバイスAIの静かな知性を融合させました。月額課金なし、テレメトリなし、クラウド囲い込みなし。",
        "intro_p2": "個人用ソフトウェアが監視ツールと化してしまった現代において、Nudgeは揺るぎない原点回帰を提示します。あなたが書くすべての思考や下書きは、標準的なUTF-8 Markdown (.md) ファイルとYAMLフロントマターとしてPC内にのみ保存されます。",
        "cta_store": "Microsoft Storeで入手",
        "cta_trial": "15日間無料体験版をダウンロード",
        "cta_buy": "買い切り版 — $0.99で永久所有",
        "cta_see": "アーキテクチャと詳細仕様を見る",
        "badge_offline": "100% オフライン・エアギャップ",
        "badge_ai": "オンデバイスSLM (クラウドゼロ)",
        "badge_markdown": "標準Markdown (.md)",
        "badge_telemetry": "テレメトリ完全ゼロ",
        "badge_hello": "Windows Hello 生体認証",
        "badge_price": "$0.99 買い切り",
        "platform_badge": "Windows 10/11ネイティブ WinUI 3 • x64 & ARM64 Copilot+ PC対応",
        "h_pillars": "Nudgeを支える3つの不変の柱",
        "pillars_sub": "完全オフラインのプライバシー、静かな内省、そして人間味あふれる思いやり。",
        "p1_title": "真のオフライン・データ主権",
        "p1_desc": "完全なプライバシーは宣伝文句ではなく、設計上の絶対条件です。Nudgeは実行時に外部ネットワーク通信を一切行いません。",
        "p2_title": "静けさを守るオンデバイスAI",
        "p2_desc": "AIは人間の内省を促す鏡であるべきです。CPU、DirectML GPU、またはNPU上でモデルを完全ローカル実行し、お節介なアドバイスや診断は行いません。",
        "p3_title": "罪悪感のない優しいメトリクス",
        "p3_desc": "書き忘れた日があっても赤い警告で責めることはありません。猶予日付きの継続記録、再開を称える指標、正直な中央値文字数表示を備えています。",
        "h_manifesto": "マニフェスト：私たちがNudgeを作った理由",
        "manifesto_sub": "クラウド日記の危機、認識論的プライバシー、そして「50年後のテスト」。",
        "h_arch": "ゼロクラウド・アーキテクチャ設計図",
        "arch_sub": "ファイルシステムそのものがデータベース。150ms以内の高速BM25検索。",
        "h_ai": "オンデバイスAIコンパニオンの詳細解説",
        "ai_sub": "思考の流れを妨げず、決して説教しない、100%ローカル稼働の知的ミラー。",
        "h_psych": "心に寄り添う心理学：恥や罪悪感のない記録",
        "psych_sub": "過度なゲームフィケーションを排除し、人間の生活リズムに寄り添う設計。",
        "h_writing": "執筆環境：ディープワークのために洗練された空間",
        "writing_sub": "1.5秒未満でカーソルが点滅する高速起動、万年筆と上質紙を思わせるステーショナリーパレット。",
        "h_security": "セキュリティ、生体認証、データ主権",
        "security_sub": "Windows Hello認証、任意のローカルAES-256-GCM暗号化、自由なデータエクスポート。",
        "h_compare": "徹底比較：他社製日記アプリとの違い",
        "compare_sub": "Day One、Obsidian、Notion、商用AIチャットボットとの比較。",
        "h_workflows": "5つの日常マスターワークフロー",
        "workflows_sub": "朝の思考整理から夜のデトックスまで、Nudgeを使いこなす実践例。",
        "h_hardware": "ハードウェア階層と省電力性能",
        "hardware_sub": "x64およびSnapdragon X搭載Copilot+ PCで超高速・省バッテリー稼働。",
        "h_pricing": "透明な買い切りライセンス：脱サブスクリプション",
        "pricing_sub": "一度の購入で一生使える。クレジットカード不要の15日間無制限無料体験。",
        "h_faq": "よくある質問と回答",
        "faq_sub": "プライバシー、ローカルAI、データ保存、ライセンスに関する詳細。",
        "h_quotes": "作家や研究者が語るNudgeの魅力",
        "h_cta": "自分の内面と静かに向き合う時間を、取り戻そう",
        "cta_lead": "通知と監視に満ちたデジタルの喧騒から離れ、あなただけの聖域へ。今すぐ15日間無料体験をお試しください。"
    },
    "ar": {
        "name": "Nudge — دفتر يوميات وتأملات أوفلاين مع رفيق ذكاء اصطناعي محلي",
        "subtitle": "دفتر يوميات مكتبي محلي بالكامل لنظام Windows مع ذكاء اصطناعي على الجهاز",
        "tagline": "أفكارك ملك لك وحدك — وليست للسحابة.",
        "intro_lead": "تطبيق Nudge هو دفتر يوميات حميمي وخالٍ من المشتتات صُمم خصيصاً وبشكل أصيل لنظام Windows. يجمع التطبيق بين السيادة الرقمية المطلقة لملفات Markdown المحلية البسيطة والذكاء الهادئ لرفيق الذكاء الاصطناعي الذي يعمل محلياً على جهازك دون أي اتصال بالإنترنت. لا اشتراكات شهرية، لا تتبع، ولا حبس للبيانات.",
        "intro_p2": "في عصر تحولت فيه البرمجيات الشخصية إلى قنوات تجسس وجمع بيانات، يمثل Nudge عودة واعية للمبادئ الأساسية. كل فكرة، جملة، ومسودة تكتبها تبقى محفوظة داخل جهازك الشخصي بصيغة Markdown (.md) مع بيانات YAML التعريفية.",
        "cta_store": "الحصول عليه من متجر Microsoft",
        "cta_trial": "تحميل النسخة التجريبية مجاناً لمدة 15 يوماً",
        "cta_buy": "شراء لمرة واحدة — 0.99$ مدى الحياة",
        "cta_see": "استكشاف البنية التقنية والمواصفات",
        "badge_offline": "يعمل أوفلاين 100% بمعزل تام",
        "badge_ai": "ذكاء اصطناعي على الجهاز (بدون سحابة)",
        "badge_markdown": "ملفات Markdown (.md) نقية",
        "badge_telemetry": "صفر تتبع أو إرسال بيانات",
        "badge_hello": "حماية Windows Hello البيومترية",
        "badge_price": "0.99$ شراء لمرة واحدة",
        "platform_badge": "تطبيق أصيل بنظام WinUI 3 لـ Windows 10 و 11 • يدعم x64 و ARM64 Copilot+ PC",
        "h_pillars": "الركائز الثلاث الثابتة لتطبيق Nudge",
        "pillars_sub": "ضماناتنا المعمارية: خصوصية تامة دون اتصال، تفكير هادئ، وتعاطف إنساني خالٍ من اللوم.",
        "p1_title": "سيادة حقيقية غير متصلة بالإنترنت",
        "p1_desc": "الخصوصية الكاملة ليست مجرد شعار تسويقي، بل هي قاعدة برمجية ثابتة. لا يقوم Nudge بأي اتصال شبكي أثناء التشغيل على الإطلاق.",
        "p2_title": "رفيق ذكاء اصطناعي هادئ على الجهاز",
        "p2_desc": "يجب أن يخدم الذكاء الاصطناعي الاستبطان الإنساني لا أن يسرق الانتباه. يشغل التطبيق نماذج لغوية محلية محسنة على معالجك المحلي دون إرسال بياناتك للخارج.",
        "p3_title": "إحصاءات رحيمة خالية من الشعور بالذنب",
        "p3_desc": "لا أرقام حمراء ولا عقوبات عند التوقف لأيام. يمنحك التطبيق فترات سماح مرنة في التتابع، ويحتفل بعودتك للكتابة بعد الغياب.",
        "h_manifesto": "البيان: لماذا بنينا تطبيق Nudge",
        "manifesto_sub": "أزمة اليوميات السحابية، والخصوصية المعرفية، واختبار الخمسين عاماً.",
        "h_arch": "البنية المعمارية: المخطط التقني الخالي من السحابة",
        "arch_sub": "نظام الملفات كقاعدة بيانات، وكتابة ذرية آمنة، وبحث BM25 فوري في الذاكرة.",
        "h_ai": "رفيق الذكاء الاصطناعي على الجهاز: نظرة عميقة",
        "ai_sub": "مرآة فكرية هادئة لا تقاطعك أبداً، لا تسدي نصائح غير مرغوبة، وتعمل 100% على عتادك المحلي.",
        "h_psych": "علم النفس الواعي للمقاييس: لا ذنب ولا خجل",
        "psych_sub": "قياس العادات بتعاطف إنساني بدلاً من ألاعيب الإدمان الرقمي الضارة.",
        "h_writing": "بيئة الكتابة: صُممت للتركيز العميق",
        "writing_sub": "إطلاق سريع في أقل من 1.5 ثانية إلى المؤشر، وجماليات القرطاسية الراقية، ووضع F11 الغامر.",
        "h_security": "الأمان والبيومتريات والسيادة على البيانات",
        "security_sub": "Windows Hello، وتشفير اختياري محلي AES-256-GCM، وحرية تصدير كاملة ومفتوحة.",
        "h_compare": "مقارنة شاملة مع التطبيقات الأخرى",
        "compare_sub": "لماذا يفضل الكُتّاب Nudge على Day One و Obsidian و Notion وروبوتات الدردشة التجارية.",
        "h_workflows": "خمسة مسارات عمل يومية متقنة",
        "workflows_sub": "كيف يدمج الكُتّاب والمفكرون والرحالة تطبيق Nudge في روتينهم اليومي.",
        "h_hardware": "فئات العتاد والكفاءة الحسابية",
        "hardware_sub": "أداء فائق على أجهزة x64 و ARM64 Copilot+ PC مع استهلاك ضئيل جداً للبطارية.",
        "h_pricing": "تسعير شفاف: ميثاق مناهضة الاشتراكات",
        "pricing_sub": "ادفع مرة واحدة وامتلكه للأبد. تجربة مجانية غير مقيدة لمدة 15 يوماً دون بطاقة ائتمان.",
        "h_faq": "الأسئلة الشائعة",
        "faq_sub": "كل ما تحتاج لمعرفته حول الخصوصية، والذكاء الاصطناعي المحلي، والتخزين، والترخيص.",
        "h_quotes": "ماذا يقول المفكرون والكُتّاب عن Nudge",
        "h_cta": "استعد ملاذك الداخلي المقدس",
        "cta_lead": "أفكارك الخاصة هي آخر ملاذ مقدس حقاً في هذا العالم الرقمي. ابدأ رحلتك المجانية لمدة 15 يوماً اليوم."
    },
    "hi": {
        "name": "Nudge — स्थानीय AI साथी के साथ ऑफ़लाइन जर्नल और डायरी",
        "subtitle": "विंडोज के लिए पूर्णतः ऑफ़लाइन डायरी और ऑन-डिवाइस AI साथी",
        "tagline": "आपके विचार आपके हैं — क्लाउड के नहीं।",
        "intro_lead": "Nudge विंडोज के लिए विशेष रूप से तैयार की गई एक आत्मीय, ध्यान भटकाव-मुक्त डेस्कटॉप डायरी है। यह स्थानीय प्लेन मार्कडाउन फाइलों की पूर्ण डिजिटल स्वतंत्रता को एक ऐसे ऑन-डिवाइस AI साथी की शांत बुद्धिमत्ता के साथ जोड़ती है जो कभी इंटरनेट से कनेक्ट नहीं होता। न कोई मासिक सदस्यता शुल्क, न कोई टेलीमेट्री ट्रैकिंग, और न ही कोई क्लाउड निर्भरता।",
        "intro_p2": "इस युग में जहां व्यक्तिगत सॉफ्टवेयर निगरानी का जरिया बन चुके हैं, Nudge बुनियादी सिद्धांतों की ओर एक दृढ़ वापसी है। आपके द्वारा लिखा गया प्रत्येक विचार और वाक्य हमेशा आपकी निजी मशीन पर स्वच्छ YAML मेटाडेटा के साथ सुरक्षित रहता है।",
        "cta_store": "Microsoft Store से प्राप्त करें",
        "cta_trial": "15 दिनों का निःशुल्क ट्रायल डाउनलोड करें",
        "cta_buy": "एक बार खरीदें — $0.99 आजीवन स्वामित्व",
        "cta_see": "आर्किटेक्चर और तकनीकी विवरण देखें",
        "badge_offline": "100% ऑफ़लाइन सुरक्षित",
        "badge_ai": "ऑन-डिवाइस SLM AI (शून्य क्लाउड)",
        "badge_markdown": "प्लेन मार्कडाउन (.md)",
        "badge_telemetry": "शून्य टेलीमेट्री",
        "badge_hello": "Windows Hello बायोमेट्रिक्स",
        "badge_price": "$0.99 एकमुश्त खरीद",
        "platform_badge": "Windows 10 और 11 के लिए नेटिव WinUI 3 • x64 और ARM64 Copilot+ PC समर्थित",
        "h_pillars": "Nudge के तीन अविचल स्तंभ",
        "pillars_sub": "हमारी तकनीकी गारंटी: पूर्ण ऑफ़लाइन गोपनीयता, शांत आत्म-मंथन, और मानवीय संवेदनशीलता।",
        "p1_title": "सच्ची ऑफ़लाइन संप्रभुता",
        "p1_desc": "गोपनीयता कोई विपणन का दिखावा नहीं, बल्कि सॉफ्टवेयर का बुनियादी नियम है। Nudge कभी भी कोई इंटरनेट नेटवर्क अनुरोध नहीं करता है।",
        "p2_title": "शांत, ऑन-डिवाइस AI साथी",
        "p2_desc": "आर्टिफिशियल इंटेलिजेंस को मानवीय आत्म-चिंतन की सेवा करनी चाहिए। Nudge आपके CPU, GPU या NPU पर पूरी तरह से स्थानीय भाषा मॉडल चलाता है।",
        "p3_title": "सहानुभूतिपूर्ण, अपराध-मुक्त आँकड़े",
        "p3_desc": "पारंपरिक ऐप्स छूटे हुए दिनों पर लाल निशान से डराते हैं। Nudge लचीले ग्रेस-डे प्रदान करता है और आपकी वापसी का उत्सव मनाता है।",
        "h_manifesto": "हमारा घोषणापत्र: हमने Nudge क्यों बनाया",
        "manifesto_sub": "क्लाउड डायरी का संकट, वैचारिक गोपनीयता, और 50 वर्षों की दीर्घायु का परीक्षण।",
        "h_arch": "मूल आर्किटेक्चर: शून्य-क्लाउड तकनीकी खाका",
        "arch_sub": "फ़ाइल सिस्टम ही डेटाबेस है, सुरक्षित राइटिंग और 150ms से तेज़ इन-मेमोरी BM25 खोज।",
        "h_ai": "ऑन-डिवाइस AI साथी: विस्तृत समीक्षा",
        "ai_sub": "एक शांत बौद्धिक दर्पण जो कभी बाधा नहीं डालता, कभी अनचाही सलाह नहीं देता और 100% स्थानीय चलता है।",
        "h_psych": "माइंडफुल मेट्रिक्स: कोई गिल्ट नहीं, कोई शर्म नहीं",
        "psych_sub": "आदतों को तनावपूर्ण गेमिफिकेशन के बजाय मानवीय सहानुभूति के साथ मापना।",
        "h_writing": "लेखन वातावरण: गहन एकाग्रता के लिए निर्मित",
        "writing_sub": "1.5 सेकंड से भी कम में कर्सर सक्रिय, उत्तम स्टेशनरी सौंदर्यशास्त्र और F11 फुलस्क्रीन फोकस।",
        "h_security": "सुरक्षा, बायोमेट्रिक्स और डेटा संप्रभुता",
        "security_sub": "Windows Hello बायोमेट्रिक्स, वैकल्पिक AES-256-GCM एन्क्रिप्शन और पूर्ण एक्सपोर्ट स्वतंत्रता।",
        "h_compare": "तुलनात्मक विश्लेषण: Nudge अन्य ऐप्स से कैसे अलग है",
        "compare_sub": "लेखक Day One, Obsidian, Notion और क्लाउड चैटबॉट्स की तुलना में Nudge को क्यों चुनते हैं।",
        "h_workflows": "पाँच मुख्य दैनिक कार्यप्रवाह",
        "workflows_sub": "लेखक, विचारक और यात्री Nudge को अपनी दैनिक जीवनशैली में कैसे शामिल करते हैं।",
        "h_hardware": "हार्डवेयर स्तर और कम्प्यूटेशनल दक्षता",
        "hardware_sub": "न्यूनतम बैटरी खपत के साथ x64 और Snapdragon X Copilot+ PC पर तेज़ प्रदर्शन।",
        "h_pricing": "पारदर्शी मूल्य निर्धारण: एंटी-सब्सक्रिप्शन अनुबंध",
        "pricing_sub": "एक बार भुगतान करें, हमेशा के लिए अपनाएं। बिना क्रेडिट कार्ड के 15 दिनों का खुला परीक्षण।",
        "h_faq": "अक्सर पूछे जाने वाले प्रश्न",
        "faq_sub": "गोपनीयता, स्थानीय AI, स्टोरेज और लाइसेंसिंग से जुड़े सभी उत्तर।",
        "h_quotes": "विचारकों और लेखकों के विचार",
        "h_cta": "अपनी आंतरिक दुनिया पर पुनः अपना अधिकार पाएं",
        "cta_lead": "निजी विचार आपके जीवन का सबसे पवित्र हिस्सा हैं। आज ही अपना 15 दिनों का निःशुल्क ट्रायल शुरू करें।"
    },
    "ru": {
        "name": "Nudge — Офлайн-дневник и журнал с локальным ИИ-компаньоном",
        "subtitle": "Офлайн-дневник для Windows с ИИ на устройстве",
        "tagline": "Ваши мысли принадлежат только вам — а не облаку.",
        "intro_lead": "Nudge — это приватный дневник для Windows, созданный для вдумчивых размышлений без отвлекающих факторов. Он объединяет абсолютный цифровой суверенитет локальных файлов Markdown с интеллектом локальной языковой модели, которая никогда не подключается к Интернету. Никаких подписок, никакой телеметрии и привязки к серверам.",
        "intro_p2": "Каждая написанная вами мысль хранится исключительно на вашем личном компьютере в виде стандартных текстовых файлов Markdown (.md) с метаданными YAML. Никаких закрытых баз данных или облачных утечек.",
        "cta_store": "Скачать из Microsoft Store",
        "cta_trial": "Бесплатная пробная версия на 15 дней",
        "cta_buy": "Купить навсегда — $0.99",
        "cta_see": "Изучить архитектуру и характеристики",
        "badge_offline": "100% Автономный / Air-Gapped",
        "badge_ai": "ИИ на устройстве (Без облака)",
        "badge_markdown": "Чистый Markdown (.md)",
        "badge_telemetry": "Ноль телеметрии",
        "badge_hello": "Биометрия Windows Hello",
        "badge_price": "Разовая покупка $0.99",
        "platform_badge": "Нативное приложение WinUI 3 для Windows 10/11 • x64 и ARM64 Copilot+ PC",
        "h_pillars": "Три нерушимых столпа Nudge",
        "pillars_sub": "Наши архитектурные гарантии: полная конфиденциальность, тихое осмысление и человечность.",
        "p1_title": "Истинный офлайн-суверенитет",
        "p1_desc": "Приватность — это не строчка в рекламе, а программный инвариант. Nudge не совершает ни одного сетевого запроса во время работы.",
        "p2_title": "Тихий локальный ИИ-компаньон",
        "p2_desc": "Искусственный интеллект должен служить самопознанию. Nudge запускает квантованные модели прямо на вашем процессоре, видеокарте или NPU без отправки данных в облако.",
        "p3_title": "Метрики с заботой, а не чувством вины",
        "p3_desc": "Никаких красных штрафных счетчиков за пропущенные дни. Nudge предлагает мягкие дни поблажки и отмечает радость возвращения к писательству.",
        "h_manifesto": "Манифест: почему мы создали Nudge",
        "manifesto_sub": "Кризис облачных дневников, право на эпистемическую приватность и проверка 50 годами.",
        "h_arch": "Архитектура Zero-Cloud: технический чертеж",
        "arch_sub": "Файловая система вместо СУБД, атомарное сохранение и мгновенный поиск BM25.",
        "h_ai": "Локальный ИИ на вашем ПК: детальный обзор",
        "ai_sub": "Интеллектуальное зеркало, которое не дает непрошеных советов и работает на 100% локально.",
        "h_psych": "Осознанная психология: без вины и стыда",
        "psych_sub": "Измерение привычек с эмпатией вместо токсичной геймификации.",
        "h_writing": "Среда для письма: создана для глубокой концентрации",
        "writing_sub": "Мгновенный запуск менее чем за 1,5 секунды, эстетика книжного переплета и режим F11.",
        "h_security": "Безопасность, биометрия и владение данными",
        "security_sub": "Windows Hello, опциональное шифрование AES-256-GCM и полная свобода экспорта.",
        "h_compare": "Сравнительный анализ Nudge с аналогами",
        "compare_sub": "Почему авторы выбирают Nudge вместо Day One, Obsidian, Notion и публичных чат-ботов.",
        "h_workflows": "Пять мастерских ежедневных сценариев",
        "workflows_sub": "Как писатели, исследователи и путешественники применяют Nudge в жизни.",
        "h_hardware": "Аппаратные уровни и энергоэффективность",
        "hardware_sub": "Нативная поддержка x64 и Copilot+ ARM64 с минимальной нагрузкой на аккумулятор.",
        "h_pricing": "Прозрачные цены: отказ от подписок",
        "pricing_sub": "Платите один раз — владейте вечно. 15-дневный неограниченный пробный период.",
        "h_faq": "Часто задаваемые вопросы",
        "faq_sub": "Все об архитектуре, локальных нейросетях, хранении заметок и лицензиях.",
        "h_quotes": "Отзывы писателей и мыслителей о Nudge",
        "h_cta": "Верните себе личное пространство мысли",
        "cta_lead": "Ваши сокровенные размышления заслуживают настоящей защиты. Начните 15-дневный бесплатный пробный период сегодня."
    },
    "pt": {
        "name": "Nudge — Diário e Journal Offline com IA Companheira no Dispositivo",
        "subtitle": "Diário Offline com IA Local para Windows",
        "tagline": "Seus pensamentos pertencem a você — não à nuvem.",
        "intro_lead": "Nudge é um diário de mesa íntimo e livre de distrações desenvolvido nativamente para Windows. Ele une a absoluta soberania digital de arquivos locais Markdown com a inteligência discreta de uma IA no próprio dispositivo que nunca se conecta à internet. Sem assinaturas, sem telemetria, sem rastreamento e sem bloqueio de dados.",
        "intro_p2": "Em uma época na qual softwares pessoais foram transformados em esteiras de vigilância, o Nudge retorna aos princípios fundamentais: cada frase e rascunho permanece salvo no seu computador em arquivos de texto abertos Markdown (.md).",
        "cta_store": "Obter na Microsoft Store",
        "cta_trial": "Baixar avaliação gratuita de 15 dias",
        "cta_buy": "Comprar uma vez — US$ 0,99 vitalício",
        "cta_see": "Explorar arquitetura e especificações",
        "badge_offline": "100% Offline / Air-Gapped",
        "badge_ai": "IA no Dispositivo (Zero Nuvem)",
        "badge_markdown": "Markdown Puro (.md)",
        "badge_telemetry": "Zero Telemetria",
        "badge_hello": "Biometria Windows Hello",
        "badge_price": "US$ 0,99 Compra Única",
        "platform_badge": "Nativo WinUI 3 para Windows 10 e 11 • x64 e ARM64 Copilot+ PC",
        "h_pillars": "Os Três Pilares Invioláveis do Nudge",
        "pillars_sub": "Nossas garantias: privacidade total desconectada, reflexão tranquila e compaixão humana.",
        "p1_title": "Verdadeira soberania offline",
        "p1_desc": "Privacidade completa é um invariante de arquitetura. O Nudge não realiza nenhuma chamada de rede durante a execução.",
        "p2_title": "Companheira de IA local e discreta",
        "p2_desc": "A inteligência artificial deve servir à introspecção humana. O Nudge executa modelos de linguagem locais quantizados na sua CPU, GPU DirectML ou NPU Copilot+.",
        "p3_title": "Métricas compassivas sem culpa",
        "p3_desc": "Chega de números vermelhos punitivos: o Nudge traz dias de carência em sequências, celebra retornos e calcula medianas reais de escrita.",
        "h_manifesto": "O Manifesto: Por que criamos o Nudge",
        "manifesto_sub": "A crise dos diários em nuvem, privacidade epistêmica e o teste dos 50 anos.",
        "h_arch": "Arquitetura Zero-Cloud: O Projeto Técnico",
        "arch_sub": "Sistema de arquivos como banco de dados, gravações atômicas e busca BM25 instantânea.",
        "h_ai": "A IA no Dispositivo em Detalhes",
        "ai_sub": "Um espelho intelectual que nunca interrompe, não julga e roda 100% na sua máquina.",
        "h_psych": "Psicologia Consciente: Sem Culpa ou Vergonha",
        "psych_sub": "Hábitos medidos com empatia em vez de mecânicas tóxicas de jogos.",
        "h_writing": "Ambiente de Escrita: Foco Profundo",
        "writing_sub": "Abertura em menos de 1,5 segundo, estética clássica de encadernação e foco F11.",
        "h_security": "Segurança, Biometria e Soberania",
        "security_sub": "Windows Hello, criptografia opcional AES-256-GCM e total liberdade de exportação.",
        "h_compare": "Comparativo Detalhado de Recursos",
        "compare_sub": "Por que autores preferem o Nudge em vez de Day One, Obsidian, Notion e chatbots comerciais.",
        "h_workflows": "Cinco Fluxos Diários de Escrita",
        "workflows_sub": "Como pensadores e nômades integram o Nudge em suas rotinas diárias.",
        "h_hardware": "Eficiência e Requisitos de Hardware",
        "hardware_sub": "Execução nativa em PCs x64 e Copilot+ ARM64 com impacto mínimo na bateria.",
        "h_pricing": "Preço Transparente: O Contrato Anti-Assinatura",
        "pricing_sub": "Pague uma vez, possua para sempre. 15 dias de teste sem cartão de crédito.",
        "h_faq": "Perguntas Frequentes",
        "faq_sub": "Tudo sobre privacidade, IA local, arquivos e licenciamento.",
        "h_quotes": "O que pensadores dizem sobre o Nudge",
        "h_cta": "Reconquiste seu santuário interior",
        "cta_lead": "Seus pensamentos íntimos são seu santuário mais sagrado. Comece sua avaliação gratuita de 15 dias hoje mesmo."
    }
}

# Add alias for Portuguese (Portugal)
TRANSLATIONS["pt-pt"] = dict(TRANSLATIONS["pt"])
TRANSLATIONS["pt-pt"]["name"] = "Nudge — Diário e Journal Offline com IA Companheira no Dispositivo"
TRANSLATIONS["pt-pt"]["subtitle"] = "Diário Offline com IA Local para Windows (Portugal)"

def get_localized_data(code):
    """Return dictionary for a specific locale, falling back to English for untranslated fields."""
    custom = TRANSLATIONS.get(code, {})
    d = dict(EN)
    
    # Overwrite top-level translated strings
    for k, v in custom.items():
        if not k.startswith("p") and not k.startswith("m"):
            d[k] = v
            
    # Update pillars if translated
    if "p1_title" in custom:
        d["pillars"] = [
            {"num": "1", "icon": "bi-shield-check", "title": custom["p1_title"], "desc": custom["p1_desc"]},
            {"num": "2", "icon": "bi-cpu", "title": custom["p2_title"], "desc": custom["p2_desc"]},
            {"num": "3", "icon": "bi-heart-pulse", "title": custom["p3_title"], "desc": custom["p3_desc"]}
        ]
        
    return d

def main():
    print("Building full multilingual strings database...")
    all_locales = {}
    for code, label, direction, hreflang, og in LOCALES_INFO:
        data = get_localized_data(code)
        all_locales[code] = data
        
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(all_locales, fh, ensure_ascii=False, indent=1)
        
    size_kb = os.path.getsize(OUT) / 1024
    print(f"Successfully generated {OUT}")
    print(f"Total locales: {len(all_locales)} | Size: {size_kb:.1f} KB")

if __name__ == "__main__":
    main()
