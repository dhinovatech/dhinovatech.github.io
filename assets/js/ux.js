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
