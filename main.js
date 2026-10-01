/* Pro Gen Plumbing — site scripts (no dependencies) */
(function () {
  'use strict';

  /* Sticky header: solid background after scrolling past the top */
  var header = document.querySelector('.site-header');
  function onScroll() {
    if (!header) return;
    header.classList.toggle('is-scrolled', window.scrollY > 24);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* Mobile nav */
  var toggle = document.querySelector('.nav-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var open = document.body.classList.toggle('nav-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.querySelectorAll('.nav-wrap a').forEach(function (a) {
      a.addEventListener('click', function () {
        document.body.classList.remove('nav-open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && document.body.classList.contains('nav-open')) {
        document.body.classList.remove('nav-open');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.focus();
      }
    });
  }

  /* FAQ accordion — one open at a time per group */
  document.querySelectorAll('.faq').forEach(function (group) {
    var items = group.querySelectorAll('.faq__item');
    items.forEach(function (item) {
      var btn = item.querySelector('.faq__q');
      btn.addEventListener('click', function () {
        var isOpen = item.classList.contains('is-open');
        items.forEach(function (i) {
          i.classList.remove('is-open');
          i.querySelector('.faq__q').setAttribute('aria-expanded', 'false');
        });
        if (!isOpen) {
          item.classList.add('is-open');
          btn.setAttribute('aria-expanded', 'true');
        }
      });
    });
  });

  /* Scroll reveal + counters */
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add('is-visible');
        if (e.target.hasAttribute('data-count')) animateCount(e.target);
        io.unobserve(e.target);
      });
    }, { threshold: 0.15 });
    document.querySelectorAll('[data-count]').forEach(function (el) { el.textContent = (0).toFixed((el.getAttribute('data-count').split('.')[1] || '').length); });
    document.querySelectorAll('.reveal, [data-count]').forEach(function (el) { io.observe(el); });
  } else {
    document.querySelectorAll('.reveal').forEach(function (el) { el.classList.add('is-visible'); });
  }

  function animateCount(el) {
    var target = parseFloat(el.getAttribute('data-count'));
    var decimals = (el.getAttribute('data-count').split('.')[1] || '').length;
    var duration = 1400, start = null;
    function step(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / duration, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = (target * eased).toFixed(decimals);
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = target.toFixed(decimals);
    }
    requestAnimationFrame(step);
  }

  /* Simple fade slider (testimonials) */
  document.querySelectorAll('.slider').forEach(function (slider) {
    var slides = slider.querySelectorAll('.slider__slide');
    if (slides.length < 2) return;
    var dotsWrap = slider.querySelector('.slider__dots');
    var idx = 0, timer;
    slides.forEach(function (_, i) {
      var b = document.createElement('button');
      b.type = 'button';
      b.setAttribute('aria-label', 'Show testimonial ' + (i + 1));
      b.addEventListener('click', function () { go(i); restart(); });
      dotsWrap.appendChild(b);
    });
    var dots = dotsWrap.querySelectorAll('button');
    function go(i) {
      slides[idx].classList.remove('is-active'); dots[idx].classList.remove('is-active');
      idx = (i + slides.length) % slides.length;
      slides[idx].classList.add('is-active'); dots[idx].classList.add('is-active');
    }
    var paused = false;
    function restart() { clearInterval(timer); if (!reduce && !paused) timer = setInterval(function () { go(idx + 1); }, 6000); }
    var prev = slider.querySelector('.slider__arrow--prev'), next = slider.querySelector('.slider__arrow--next');
    if (prev) prev.addEventListener('click', function () { go(idx - 1); restart(); });
    if (next) next.addEventListener('click', function () { go(idx + 1); restart(); });
    /* pause auto-rotate while someone is reading (hover) or using the keyboard inside it */
    function pause() { paused = true; clearInterval(timer); }
    function resume() { paused = false; restart(); }
    slider.addEventListener('mouseenter', pause);
    slider.addEventListener('mouseleave', resume);
    slider.addEventListener('focusin', pause);
    slider.addEventListener('focusout', function (e) { if (!slider.contains(e.relatedTarget)) resume(); });
    go(0); restart();
  });

  /* Instagram reels: load Instagram's (heavy) embed script only when a reel is about to scroll into view */
  var reels = document.querySelectorAll('.instagram-media');
  if (reels.length) {
    var igLoaded = false;
    var loadIG = function () {
      if (igLoaded) return; igLoaded = true;
      var s = document.createElement('script');
      s.async = true; s.src = 'https://www.instagram.com/embed.js';
      document.body.appendChild(s);
    };
    if ('IntersectionObserver' in window) {
      var igIO = new IntersectionObserver(function (entries) {
        if (entries.some(function (en) { return en.isIntersecting; })) { loadIG(); igIO.disconnect(); }
      }, { rootMargin: '600px 0px' });
      reels.forEach(function (r) { igIO.observe(r); });
    } else { loadIG(); }
  }

  /* Contact forms: validate, send in the background (Formspree), show a thank-you message inline.
     If the form isn't connected yet (action still has YOUR_FORM_ID), fall back to opening an email. */
  document.querySelectorAll('form[data-validate]').forEach(function (form) {
    var status = form.querySelector('.form__status');
    var button = form.querySelector('button[type="submit"]');
    function show(msg, isError) {
      if (!status) return;
      status.hidden = false;
      status.textContent = msg;
      status.classList.toggle('is-error', !!isError);
    }
    form.addEventListener('submit', function (e) {
      var phone = form.querySelector('input[name="phone"]');
      if (phone && phone.value.replace(/\D/g, '').length < 10) {
        e.preventDefault();
        phone.focus();
        phone.setCustomValidity('Please enter a valid phone number.');
        phone.reportValidity();
        phone.addEventListener('input', function () { phone.setCustomValidity(''); }, { once: true });
        return;
      }
      var hp = form.querySelector('input[name="_gotcha"]');
      if (hp && hp.value) { e.preventDefault(); return; } /* bot */

      var action = form.getAttribute('action') || '';
      var data = new FormData(form);
      if (action.indexOf('YOUR_FORM_ID') !== -1) {
        /* Not connected yet: open the visitor's email app with everything filled in */
        e.preventDefault();
        var body = ['Name: ' + (data.get('name') || ''), 'Phone: ' + (data.get('phone') || ''), 'Email: ' + (data.get('email') || ''),
                    'Service: ' + (data.get('service') || ''), 'Preferred time: ' + (data.get('preferred_time') || ''), '', (data.get('message') || '')].join('\n');
        window.location.href = 'mailto:' + (form.getAttribute('data-email') || '') +
          '?subject=' + encodeURIComponent('Service request from the website') + '&body=' + encodeURIComponent(body);
        show('Your email app should open with your request filled in — just hit send. Or call/text (647) 804-3744.');
        return;
      }
      if (!window.fetch) return; /* very old browser: normal form post */
      e.preventDefault();
      if (button) button.disabled = true;
      show('Sending…');
      fetch(action, { method: 'POST', body: data, headers: { 'Accept': 'application/json' } })
        .then(function (r) {
          if (!r.ok) throw new Error('bad status');
          form.reset();
          show('Thanks — your request was sent. We’ll call or text you back shortly. For anything urgent, call (647) 804-3744.');
        })
        .catch(function () {
          show('Sorry, that didn’t go through. Please call or text (647) 804-3744 instead.', true);
        })
        .then(function () { if (button) button.disabled = false; });
    });
  });

  /* Footer year */
  var y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();
})();
