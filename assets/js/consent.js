/* Dhinovatech cookie-consent banner.

   Google Consent Mode v2 does the actual enforcing, and it is armed in the
   <head> before gtag.js runs - analytics_storage starts at 'denied' on every
   page load. This file only draws the banner and records the answer.

   That ordering is deliberate: if this script fails to load, is blocked, or
   JavaScript is off entirely, the banner never appears AND consent is never
   granted. The failure mode is "no tracking", not "tracking without consent".
   The banner ships with the `hidden` attribute set for the same reason. */
(function () {
  'use strict';

  var KEY = 'dhin-consent';   // 'granted' | 'denied'

  function stored() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }

  function remember(value) {
    try { localStorage.setItem(KEY, value); } catch (e) { /* private mode */ }
  }

  document.addEventListener('DOMContentLoaded', function () {
    var bar = document.getElementById('consentBar');
    if (!bar) return;

    // Already answered on a previous visit - the head block has re-applied
    // that answer, so there is nothing to ask.
    if (stored()) return;

    bar.hidden = false;

    function answer(granted) {
      remember(granted ? 'granted' : 'denied');
      if (granted && typeof window.gtag === 'function') {
        window.gtag('consent', 'update', {
          analytics_storage: 'granted'
        });
      }
      bar.hidden = true;
      // Hand focus somewhere sensible instead of letting it fall to the top
      // of the document when the banner disappears under the keyboard.
      var main = document.getElementById('main');
      if (main) { main.setAttribute('tabindex', '-1'); main.focus({ preventScroll: true }); }
    }

    bar.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-consent]');
      if (!btn) return;
      e.preventDefault();
      answer(btn.getAttribute('data-consent') === 'allow');
    });

    // Escape is a refusal, not a dismissal: closing the banner without
    // choosing must not leave analytics in a granted state, and it does not -
    // 'denied' is what we store.
    bar.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') answer(false);
    });
  });
})();
