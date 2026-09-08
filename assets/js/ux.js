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
