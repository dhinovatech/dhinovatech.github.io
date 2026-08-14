#!/usr/bin/env python3
"""
Inject the GlowCompare "AI Skincare Expert chat" feature section into every
GlowCompare page, in that page's own language.

Copy lives in tools/ai-chat-strings.json (one block per locale). The section is
placed directly after the hero so the newest headline feature is visible without
scrolling, which is also where it does the most for install conversion.

Run:  python tools/build-ai-chat-section.py
Idempotent: the generated region is delimited and replaced on each run.
"""
import os, re, sys, json, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, 'glowcompare')
STRINGS = os.path.join(ROOT, 'tools', 'ai-chat-strings.json')

BEGIN = "<!-- BEGIN generated AI chat section -->"
END = "<!-- END generated AI chat section -->"
ANCHOR = '<section id="interactive-comparator"'

PLAY = ("https://play.google.com/store/apps/details?id=com.dhinova.glowcompare"
        "&referrer=utm_source%3Ddhinovatech.com%26utm_medium%3Dwebsite"
        "%26utm_campaign%3Dglowcompare_ai_chat")


def e(s):
    return html.escape(s, quote=True)


def section(t):
    """Build the localised section. `t` is the string block for one locale."""
    feats = [('bi-chat-heart', t['f1t'], t['f1d']),
             ('bi-exclamation-diamond', t['f2t'], t['f2d']),
             ('bi-list-check', t['f3t'], t['f3d']),
             ('bi-translate', t['f4t'], t['f4d'])]
    cards = []
    for icon, title, desc in feats:
        cards.append(f'''
          <div class="col-md-6">
            <div class="d-flex gap-3 h-100">
              <div class="feature-icon-box flex-shrink-0">
                <i class="bi {icon}" aria-hidden="true"></i>
              </div>
              <div>
                <h3 class="h6 fw-bold text-white mb-1">{e(title)}</h3>
                <p class="text-secondary small mb-0">{e(desc)}</p>
              </div>
            </div>
          </div>''')

    return f'''{BEGIN}
<section id="ai-expert-chat" class="py-5">
  <div class="container">
    <div class="row align-items-center gy-5">

      <div class="col-lg-6">
        <div class="d-inline-flex align-items-center gap-2 px-3 py-2 rounded-pill bg-rose-subtle-custom mb-3 fw-semibold small badge-glow-rose">
          <i class="bi bi-stars" aria-hidden="true"></i> {e(t['badge'])}
        </div>
        <h2 class="fw-bold mb-3">{e(t['title'])}</h2>
        <p class="lead text-secondary mb-4">{e(t['lead'])}</p>

        <div class="row g-4 mb-4">{''.join(cards)}
        </div>

        <a href="{PLAY}" target="_blank" rel="noopener"
           class="btn btn-dhin-rose btn-lg rounded-pill px-4 shadow">
          <i class="bi bi-google-play me-2" aria-hidden="true"></i> {e(t['cta'])}
        </a>
      </div>

      <div class="col-lg-6">
        <div class="ai-chat-panel p-4 p-lg-4">
          <div class="d-flex align-items-center gap-2 mb-4 pb-3 border-bottom border-secondary-subtle">
            <span class="feature-icon-box"><i class="bi bi-robot" aria-hidden="true"></i></span>
            <span class="fw-bold text-white">{e(t['title'])}</span>
          </div>

          <div class="d-flex flex-column gap-3">
            <div class="ai-chat-bubble ai-chat-bubble-user">{e(t['q1'])}</div>
            <div class="ai-chat-bubble ai-chat-bubble-ai">{e(t['a1'])}</div>
          </div>

          <p class="text-secondary extra-small mt-4 mb-0 pt-3 border-top border-secondary-subtle">
            <i class="bi bi-info-circle me-1" aria-hidden="true"></i> {e(t['disclaimer'])}
          </p>
        </div>
      </div>

    </div>
  </div>
</section>
{END}

'''


BLOCK_RE = re.compile(re.escape(BEGIN) + r'.*?' + re.escape(END) + r'\n*', re.S)


def main():
    data = json.load(open(STRINGS, encoding='utf-8'))
    pages = [(os.path.join(APP, 'index.html'), 'en')]
    for d in sorted(os.listdir(APP)):
        p = os.path.join(APP, d, 'index.html')
        if os.path.isfile(p):
            pages.append((p, d))

    done, skipped = 0, []
    for path, loc in pages:
        s = open(path, encoding='utf-8').read()
        s = BLOCK_RE.sub('', s)
        t = data.get(loc)
        if t is None:
            skipped.append((loc, 'no strings'))
            continue
        if ANCHOR not in s:
            skipped.append((loc, 'anchor not found'))
            continue
        s = s.replace(ANCHOR, section(t) + ANCHOR, 1)
        open(path, 'w', encoding='utf-8', newline='').write(s)
        done += 1

    print(f"AI chat section injected into {done}/{len(pages)} GlowCompare pages")
    if skipped:
        print("skipped:", skipped)


if __name__ == '__main__':
    sys.exit(main())
