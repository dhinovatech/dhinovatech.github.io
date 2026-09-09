/* Dhinovatech UX layer: scroll reveal, back-to-top, sticky install bar.
   Progressive enhancement - every element it touches is fully usable if this
   script never runs. */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  document.addEventListener('DOMContentLoaded', function () {

    /* ---- reveal sections on scroll --------------------------------------
       The reveal class is applied here rather than in the markup on purpose:
       it starts at opacity:0, so if this script fails to load the content must
       still be visible to readers and crawlers. No JS, no hiding. */
    var revealables = [];
    if (!reduceMotion && 'IntersectionObserver' in window) {
      var sections = document.querySelectorAll('main > section');
      // Skip the hero - it is above the fold and would flash on load.
      for (var i = 1; i < sections.length; i++) {
        sections[i].classList.add('reveal-dhin');
        revealables.push(sections[i]);
      }
    }
    if (revealables.length) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            io.unobserve(entry.target);
          }
        });
      }, { rootMargin: '0px 0px -10% 0px', threshold: 0.05 });
      revealables.forEach(function (el) { io.observe(el); });
    }

    /* ---- Microsoft Store deep links ------------------------------------
       Store CTAs ship as https://apps.microsoft.com/detail/<id> so that they
       work on every platform and stay crawlable (the JSON-LD downloadUrl
       points at the same web URL). On Windows we upgrade them in place to the
       ms-windows-store:// protocol, which hands the user straight to the Store
       app instead of a browser tab that then has to redirect.

       Non-Windows visitors are left completely untouched: the protocol is not
       registered there, so rewriting would turn a working link into a dead one. */
    var isWindows = (function () {
      var uad = navigator.userAgentData;
      if (uad && uad.platform) return uad.platform === 'Windows';
      // Windows Phone also matches "Windows" but has no desktop Store handler.
      return /Windows NT/.test(navigator.userAgent) &&
             !/Windows Phone/.test(navigator.userAgent);
    })();

    if (isWindows) {
      var STORE_RE = /^https:\/\/apps\.microsoft\.com\/detail\/([A-Za-z0-9]+)/;
      var links = document.querySelectorAll('a[href*="apps.microsoft.com/detail/"]');

      Array.prototype.forEach.call(links, function (a) {
        var web = a.getAttribute('href');
        var m = STORE_RE.exec(web);
        if (!m) return;

        // Carry the campaign tags across so Partner Center still attributes
        // the install to this site. Both have to come along: Windows visitors
        // are the only ones who can actually install, so a tag that survives
        // only on the web URL is a tag that is never counted.
        //
        // The cid pattern needs the [?&] boundary - 'cid=' also matches inside
        // 'ocid=', and without it every link would deep-link ocid's value as
        // its cid.
        var ocid = /[?&]ocid=([^&#]+)/.exec(web);
        var cid = /[?&]cid=([^&#]+)/.exec(web);
        var deep = 'ms-windows-store://pdp/?productid=' + m[1] +
                   (ocid ? '&ocid=' + ocid[1] : '') +
                   (cid ? '&cid=' + cid[1] : '');

        a.setAttribute('href', deep);
        // A protocol handler never renders a document, so a new tab would just
        // be left blank. Keep the navigation in this tab.
        a.removeAttribute('target');
        a.removeAttribute('rel');
        a.setAttribute('data-store-web', web);
      });

      /* Fallback for Windows installs with no Store app (LTSC, Server, some
         managed images): the protocol navigation is silently dropped there.
         If we are still here and still focused a moment later, nothing opened,
         so fall back to the web listing. */
      document.addEventListener('click', function (e) {
        var a = e.target.closest ? e.target.closest('a[data-store-web]') : null;
        if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey) return;

        var web = a.getAttribute('data-store-web');
        var opened = false;
        function markOpened() { opened = true; }
        document.addEventListener('visibilitychange', markOpened, { once: true });
        window.addEventListener('blur', markOpened, { once: true });

        window.setTimeout(function () {
          document.removeEventListener('visibilitychange', markOpened);
          window.removeEventListener('blur', markOpened);
          if (!opened && document.visibilityState === 'visible') {
            window.open(web, '_blank', 'noopener');
          }
        }, 1200);
      });
    }

    /* ---- store click conversions ---------------------------------------
       An install cannot be measured from this site - it happens inside the
       Store, on the other side of a link we do not control - so the click
       through to the listing is the conversion, for both ad platforms.

       This runs on every platform, and reads data-store-web before href
       precisely because the block above rewrites Windows visitors' links to
       ms-windows-store://. Matching on the href alone would report a
       conversion for everyone except the people who can actually install.

       No event_callback and no preventDefault: on Windows the link opens a
       protocol handler and on every other platform it opens a new tab, so in
       neither case is this document unloaded and in neither case is there a
       race to lose the beacon to. transport_type is set anyway, because it
       costs nothing and the day someone drops target="_blank" from a store
       button is not the day anyone will remember this comment. */
    var STORE_LINK = 'a[data-store-web],' +
                     'a[href*="apps.microsoft.com/detail/"],' +
                     'a[href*="play.google.com/store/apps"]';

    // One Google Ads conversion action per advertised app, keyed by the store
    // id the click was for. Keyed, rather than a single shared label, because
    // Google gives an action no way to be conditioned on an event parameter -
    // the way a UET goal can be conditioned on a label - so an app that is not
    // being advertised has to be filtered out here or not at all. Share one
    // label across every store button and a click on GlowCompare reports a
    // conversion against Stow's action, which does not just misreport: it
    // teaches automated bidding that GlowCompare traffic converts.
    //
    // A label is minted by the account that owns the action and is not
    // derivable from the AW- id. Sending a wrong one reports against a
    // different action rather than failing visibly, so re-copy it from the
    // tag if an action is ever deleted and recreated. An app with no entry
    // here reports nothing to Google, which is the safe default.
    var ADS_ID = 'AW-18122344867';
    var ADS_LABELS = {
      '9NHBR7SW2TZ0': 'Fp3TeZmwQMK8Cbc7'   // Stow
    };

    // Microsoft matches its goal on the event action alone, so this string is
    // the whole contract between this file and the goal in the Microsoft
    // Advertising UI. It has to be character-for-character what that goal
    // says: a mismatch does not error anywhere, it just silently counts
    // nothing, which is exactly how it read before this was corrected from
    // "store_click" to the action Microsoft's own snippet reports.
    var UET_ACTION = 'StoreVisit';

    function storeOf(url) {
      var m = /apps\.microsoft\.com\/detail\/([A-Za-z0-9]+)/.exec(url);
      if (m) return { store: 'microsoft', id: m[1] };
      m = /play\.google\.com\/store\/apps\/details\?id=([\w.]+)/.exec(url);
      if (m) return { store: 'google_play', id: m[1] };
      return null;
    }

    document.addEventListener('click', function (e) {
      if (e.defaultPrevented || e.button !== 0) return;
      var a = e.target.closest ? e.target.closest(STORE_LINK) : null;
      if (!a) return;

      var what = storeOf(a.getAttribute('data-store-web') || a.getAttribute('href') || '');
      if (!what) return;

      if (typeof window.gtag === 'function') {
        // GA4, for reading in reports. Consent Mode drops this by itself
        // wherever analytics storage is denied.
        window.gtag('event', 'store_click', {
          store: what.store,
          product_id: what.id,
          transport_type: 'beacon'
        });
        var label = ADS_LABELS[what.id];
        if (label) {
          window.gtag('event', 'conversion', {
            send_to: ADS_ID + '/' + label,
            transport_type: 'beacon'
          });
        }
      }

      // Microsoft's generated snippet sends this with an empty payload. The
      // category and label are added on top because the goal ignores
      // conditions it does not specify, so they cost nothing today and are
      // what a label condition would need if the goal is ever narrowed to one
      // app - as it stands, a click on any app's store button counts.
      window.uetq = window.uetq || [];
      window.uetq.push('event', UET_ACTION, {
        event_category: 'store',
        event_label: what.store + ':' + what.id
      });
    });

    /* ---- back to top ---------------------------------------------------- */
    var toTop = document.querySelector('.to-top');
    var installBar = document.querySelector('.install-bar');
    if (installBar) document.body.classList.add('has-install-bar');

    function onScroll() {
      var y = window.pageYOffset || document.documentElement.scrollTop;
      if (toTop) toTop.classList.toggle('is-visible', y > 600);
      // Reveal the install bar once the hero CTA has scrolled out of reach.
      if (installBar) installBar.classList.toggle('is-visible', y > 480);
    }

    // Called directly rather than batched through requestAnimationFrame: the
    // handler is two no-op-if-unchanged classList toggles, so batching buys
    // nothing, and an rAF that never fires (background tab, non-compositing
    // renderer) would latch the throttle flag and kill scrolling behaviour.
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll, { passive: true });
    onScroll();

    if (toTop) {
      toTop.addEventListener('click', function (e) {
        e.preventDefault();
        window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
        // Send focus back to the top of the document for keyboard users.
        var main = document.getElementById('main');
        if (main) { main.setAttribute('tabindex', '-1'); main.focus({ preventScroll: true }); }
      });
    }
  });
})();
