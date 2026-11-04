/* The landing page's calculator and screenshot zoom (/mortgage-loan-emi-pro/).
   tools/build-mortgage.py writes the first result into the HTML with the same
   arithmetic, so the numbers are there before this runs. Interest and the
   payment round to cents each month, as the app does, so the page's "interest
   saved" matches the figure on the store slide beside it. */
(function () {
  'use strict';

  function payoff(amount, r, n, emi, extra) {
    var bal = amount, interest = 0, months = 0;
    while (bal > 0.005 && months < 1200) {
      var it = Math.round(bal * r * 100) / 100;
      months += 1;
      // Without an extra payment the last one clears whatever rounding left.
      var pay = (months === n && !extra) ? bal + it : Math.min(emi + extra, bal + it);
      // A payment that cannot cover the interest never ends; the cap above stops it.
      interest += it;
      bal = Math.round((bal - (pay - it)) * 100) / 100;
    }
    return { interest: interest, months: months };
  }

  // The CLDR rules for whole numbers, as in the app's TermText.PluralCategory.
  function plural(n, lang) {
    var two = n % 100, last = n % 10;
    var few = last >= 2 && last <= 4 && !(two >= 12 && two <= 14);
    switch (lang) {
      case 'ar':
        if (n <= 2) return ['Zero', 'One', 'Two'][n];
        return two >= 3 && two <= 10 ? 'Few' : two >= 11 ? 'Many' : 'Other';
      case 'ru': return last === 1 && two !== 11 ? 'One' : few ? 'Few' : 'Many';
      case 'pl': return n === 1 ? 'One' : few ? 'Few' : 'Many';
      case 'cs': return n === 1 ? 'One' : n >= 2 && n <= 4 ? 'Few' : 'Other';
      case 'fr': return n <= 1 ? 'One' : 'Other';
      default: return 'Other';
    }
  }

  function setupCalculator(root) {
    var fields = {};
    root.querySelectorAll('[data-calc]').forEach(function (el) {
      fields[el.getAttribute('data-calc')] = el;
    });
    var ranges = {};
    root.querySelectorAll('[data-calc-range]').forEach(function (el) {
      ranges[el.getAttribute('data-calc-range')] = el;
    });
    var out = {};
    root.querySelectorAll('[data-out]').forEach(function (el) {
      out[el.getAttribute('data-out')] = el;
    });

    var money = new Intl.NumberFormat(root.getAttribute('data-locale'), {
      style: 'currency', currency: root.getAttribute('data-currency'), maximumFractionDigits: 0
    });
    var timeFormat = root.getAttribute('data-time');
    var term = JSON.parse(root.getAttribute('data-term') || '{}');
    var lang = document.documentElement.lang;

    function fill(format, a, b) {
      return format.replace('{0}', a).replace('{1}', b);
    }

    function counted(forms, n) {
      return fill(forms[plural(n, lang)] || forms.Other, n);
    }

    function timeText(months) {
      var y = Math.floor(months / 12), m = months % 12;
      if (!term.years || !term.years.Other && !term.years.Many || !term.months || !term.months.Other) {
        return fill(timeFormat, y, m);
      }
      if (!y) return counted(term.months, m);
      if (!m) return counted(term.years, y);
      return fill(term.join, counted(term.years, y), counted(term.months, m));
    }

    function read(key) {
      var v = parseFloat(fields[key].value);
      return isFinite(v) && v >= 0 ? v : 0;
    }

    function render() {
      var amount = read('amount'), rate = read('rate'), extra = read('extra');
      var n = Math.round(read('years') * 12);
      if (!amount || !n) return;
      var r = rate / 1200;
      var emi = r ? amount * r / (1 - Math.pow(1 + r, -n)) : amount / n;
      emi = Math.round(emi * 100) / 100;
      var base = payoff(amount, r, n, emi, 0);
      var withExtra = payoff(amount, r, n, emi, extra);
      var cut = Math.max(0, n - withExtra.months);
      out.payment.textContent = money.format(emi);
      out.interest.textContent = money.format(base.interest);
      out.saved.textContent = money.format(Math.floor(Math.max(0, base.interest - withExtra.interest) + 0.005));
      out.time.textContent = timeText(cut);
    }

    Object.keys(fields).forEach(function (key) {
      fields[key].addEventListener('input', function () {
        if (ranges[key]) ranges[key].value = fields[key].value;
        render();
      });
      if (ranges[key]) {
        ranges[key].addEventListener('input', function () {
          fields[key].value = ranges[key].value;
          render();
        });
      }
    });
    render();
  }

  document.querySelectorAll('[data-mortgage-calc]').forEach(setupCalculator);

  // Screenshot zoom. Each picture is a plain link to its file, so without a
  // <dialog> (or without this script) a click simply opens the image.
  if (typeof HTMLDialogElement !== 'function') return;
  var dialog = document.createElement('dialog');
  dialog.className = 'ml-lightbox';
  dialog.innerHTML = '<img alt=""><button type="button" aria-label="Close"><i class="bi bi-x-lg" aria-hidden="true"></i></button>';
  document.body.appendChild(dialog);
  var image = dialog.querySelector('img');

  dialog.addEventListener('click', function () { dialog.close(); });
  document.querySelectorAll('a.ml-zoom').forEach(function (link) {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      var thumb = link.querySelector('img');
      image.src = link.href;
      image.alt = thumb ? thumb.alt : '';
      dialog.showModal();
    });
  });
})();
