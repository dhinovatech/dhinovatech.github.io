/* Dhinovatech cookie-consent banner.

   Google Consent Mode v2 does the actual enforcing, and it is armed in the
   <head> before gtag.js runs. The default there is region-scoped: denied in
   the EEA, UK and Switzerland, granted everywhere else. This file only draws
   the banner and records the answer.

   That ordering still matters. In the EEA, if this script fails to load, is
   blocked, or JavaScript is off entirely, the banner never appears AND consent
   is never granted - the failure mode is "no tracking", not "tracking without
   consent". The banner ships with the `hidden` attribute set for the same
   reason.

   Outside those regions the head block has already granted analytics, so the
   banner is an opt-out: Decline has to actively revoke rather than merely
   withhold. Both answers therefore issue a consent update, and both are
   stored, so the head block can re-apply either one on the next visit. */
(function () {
  'use strict';

  var KEY = 'dhin-consent';          // 'granted' | 'denied'

  /* Section 10 of /privacy.html promises that if what we collect changes, the
     notice is shown again. Storing only the answer could not keep that
     promise: everyone who had already answered would go on never seeing it.

     So the version of the notice a reader answered is stored alongside their
     answer, and the banner reappears when this constant moves ahead of it.
     Bump NOTICE whenever the notice's wording changes what it discloses -
     not for a typo.

     Deliberately NOT done by clearing the answer: the head block re-applies
     the stored answer on every page, so a reader who declined stays declined
     while the new notice sits in front of them. Outside the EEA, where the
     default is granted, resetting the answer instead of keeping it would
     quietly re-enable analytics for somebody who had turned it off. */
  var SEEN = 'dhin-consent-notice';  // notice version last answered
  var NOTICE = '2026-09-09';         // advertising tags disclosed

  function read(key) {
    try { return localStorage.getItem(key); } catch (e) { return null; }
  }

  function remember(value) {
    try {
      localStorage.setItem(KEY, value);
      localStorage.setItem(SEEN, NOTICE);
    } catch (e) { /* private mode */ }
  }

  document.addEventListener('DOMContentLoaded', function () {
    var bar = document.getElementById('consentBar');
    if (!bar) return;

    // Already answered this version of the notice on a previous visit - the
    // head block has re-applied that answer, so there is nothing to ask.
    // An answer stored against an older version still applies, and still
    // gets re-applied, but the reader is asked again.
    if (read(KEY) && read(SEEN) === NOTICE) return;

    bar.hidden = false;

    function answer(granted) {
      var value = granted ? 'granted' : 'denied';
      remember(value);
      if (typeof window.gtag === 'function') {
        window.gtag('consent', 'update', {
          analytics_storage: value
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
    // choosing must not leave analytics running. Outside the EEA that is now
    // a real revocation rather than a no-op, since the default was granted.
    bar.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') answer(false);
    });
  });
})();
