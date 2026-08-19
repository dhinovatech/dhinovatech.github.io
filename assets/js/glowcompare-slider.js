/* GlowCompare before/after split-slider.
   Extracted from the inline script on /glowcompare/ so the Windows edition
   pages can share it. Progressive enhancement: without this script the two
   photos still render, the divider simply does not move. */
document.addEventListener('DOMContentLoaded', function () {
  var container = document.getElementById('webSplitSlider');
  var overlay = document.getElementById('sliderOverlay');
  var overlayImg = document.getElementById('sliderOverlayImg');
  var handle = document.getElementById('sliderHandle');

  if (!container || !overlay || !handle) return;

  var isDragging = false;

  // The overlay is width-clipped, so its image has to keep the container's
  // full width or the "before" photo would squash as the divider moves.
  function syncOverlayImgWidth() {
    if (overlayImg) {
      overlayImg.style.width = container.offsetWidth + 'px';
    }
  }

  syncOverlayImgWidth();
  window.addEventListener('resize', syncOverlayImgWidth);

  function updateSliderPos(clientX) {
    var rect = container.getBoundingClientRect();
    var x = clientX - rect.left;
    if (x < 0) x = 0;
    if (x > rect.width) x = rect.width;

    var percentage = (x / rect.width) * 100;
    overlay.style.width = percentage + '%';
    handle.style.left = percentage + '%';
  }

  function onMove(e) {
    if (!isDragging) return;
    updateSliderPos(e.touches ? e.touches[0].clientX : e.clientX);
  }

  function startDragging(e) {
    isDragging = true;
    updateSliderPos(e.touches ? e.touches[0].clientX : e.clientX);
  }

  function stopDragging() {
    isDragging = false;
  }

  container.addEventListener('mousedown', startDragging);
  container.addEventListener('touchstart', startDragging, { passive: true });

  window.addEventListener('mousemove', onMove);
  window.addEventListener('touchmove', onMove, { passive: true });

  window.addEventListener('mouseup', stopDragging);
  window.addEventListener('touchend', stopDragging);
});
