#!/usr/bin/env python3
"""
Put a real contact form on contact.html.

The page only ever offered a mailto: link, which loses everyone who reads mail
in a browser tab rather than a desktop client - the click either opens nothing
or opens an app they do not use.

GitHub Pages cannot process a form itself, so this needs a third-party
endpoint (Formspree, Web3Forms, Basin - any of them take a plain POST). Put
yours in ENDPOINT below and re-run.

Until then ENDPOINT stays empty and NO form is rendered: the page keeps the
mailto card exactly as it is today. A form posting to a dead URL would look
like it worked and quietly drop every message, which is worse than not having
one - so this deliberately refuses to ship one until it can actually deliver.

Run:  python tools/build-contact.py
Idempotent: the generated region is delimited and replaced on each run.
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, "contact.html")

# ---------------------------------------------------------------------------
# Paste your form endpoint here, e.g.
#   ENDPOINT = "https://formspree.io/f/xkndqwer"
#   ENDPOINT = "https://api.web3forms.com/submit"   (plus ACCESS_KEY below)
ENDPOINT = ""
# Web3Forms needs its access key as a hidden field; Formspree does not. Leave
# blank for anything that authenticates through the URL alone.
ACCESS_KEY = ""
# ---------------------------------------------------------------------------

BEGIN = "  <!-- BEGIN generated contact form -->"
END = "  <!-- END generated contact form -->"
BLOCK_RE = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", re.S)

# Anchored above the existing "Mail Us Directly" card, so the form is the first
# thing offered and the email address stays as the fallback underneath it.
ANCHOR = "          <!-- Main Email Card -->"


def form_html():
    key = ('\n            <input type="hidden" name="access_key" value="%s">'
           % ACCESS_KEY) if ACCESS_KEY else ""
    return """%s
          <div class="card card-glass p-4 p-md-5 border border-info-subtle shadow-lg mb-4">
            <h2 class="text-white fw-bold mb-2">Send us a message</h2>
            <p class="text-secondary mb-4">
              Fill this in and we will reply to the address you give us. Prefer
              your own mail client? The address is just below.
            </p>
            <form action="%s" method="POST" class="text-start">%s
              <input type="hidden" name="_subject" value="Message from dhinovatech.com">
              <!-- Honeypot: a real person never sees this field, so anything
                   that fills it in is a bot. Hidden from screen readers too. -->
              <p class="d-none" aria-hidden="true">
                <label>Leave this empty <input type="text" name="_gotcha" tabindex="-1" autocomplete="off"></label>
              </p>

              <div class="row g-3">
                <div class="col-md-6">
                  <label for="cf-name" class="form-label text-secondary small">Your name</label>
                  <input type="text" class="form-control form-control-dhin" id="cf-name"
                         name="name" autocomplete="name" required>
                </div>
                <div class="col-md-6">
                  <label for="cf-email" class="form-label text-secondary small">Your email</label>
                  <input type="email" class="form-control form-control-dhin" id="cf-email"
                         name="email" autocomplete="email" required>
                </div>
                <div class="col-12">
                  <label for="cf-topic" class="form-label text-secondary small">What is this about?</label>
                  <select class="form-select form-control-dhin" id="cf-topic" name="topic">
                    <option>App support</option>
                    <option>Bug report</option>
                    <option>Feature request</option>
                    <option>Business enquiry</option>
                    <option>Something else</option>
                  </select>
                </div>
                <div class="col-12">
                  <label for="cf-message" class="form-label text-secondary small">Message</label>
                  <textarea class="form-control form-control-dhin" id="cf-message"
                            name="message" rows="6" required></textarea>
                </div>
                <div class="col-12">
                  <div class="form-check">
                    <input class="form-check-input" type="checkbox" value="yes"
                           id="cf-consent" name="consent" required>
                    <label class="form-check-label text-secondary small" for="cf-consent">
                      I agree that Dhinovatech may store this message and my email
                      address in order to reply to me, as described in the
                      <a href="/privacy.html" class="text-info">privacy policy</a>.
                    </label>
                  </div>
                </div>
                <div class="col-12">
                  <button type="submit" class="btn btn-dhin-primary btn-lg rounded-pill px-5 fw-bold">
                    <i class="bi bi-send-fill me-2" aria-hidden="true"></i>Send message
                  </button>
                </div>
              </div>
            </form>
          </div>

%s""" % (BEGIN, ENDPOINT, key, END)


def main():
    if not os.path.exists(PAGE):
        print("!! contact.html not found")
        return 1

    doc = io.open(PAGE, encoding="utf-8").read()
    before = doc
    doc = BLOCK_RE.sub("", doc)

    if not ENDPOINT:
        if doc != before:
            io.open(PAGE, "w", encoding="utf-8", newline="").write(doc)
            print("contact form removed (ENDPOINT is empty)")
        else:
            print("no contact form rendered: set ENDPOINT in tools/build-contact.py")
            print("  (any of Formspree / Web3Forms / Basin; the form markup is")
            print("   already written and turns on the moment you paste a URL)")
        return 0

    if ANCHOR not in doc:
        print("!! anchor comment not found in contact.html; nothing changed")
        return 1
    doc = doc.replace(ANCHOR, form_html() + ANCHOR, 1)
    io.open(PAGE, "w", encoding="utf-8", newline="").write(doc)
    print("contact form rendered, posting to %s" % ENDPOINT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
