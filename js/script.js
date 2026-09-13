"use strict";

(() => {
  const root = document.documentElement;
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const mobile = window.matchMedia('(max-width: 760px)');
  const toggle = document.querySelector('.nav__toggle');
  const nav = document.getElementById('primary-navigation');
  const header = document.querySelector('.header');

  // The approved mobile navigation remains an in-flow disclosure, not a modal.
  if (toggle && nav && header) {
    let closeTimer;
    const isOpen = () => toggle.getAttribute('aria-expanded') === 'true';
    const finishClose = () => nav.classList.remove('active', 'is-closing');
    const setOpen = (open, returnFocus = false, immediate = false) => {
      clearTimeout(closeTimer);
      nav.classList.remove('is-closing');
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Tutup navigasi' : 'Buka navigasi');
      nav.inert = mobile.matches && !open;
      if (open) nav.classList.add('active');
      else if (!immediate && !reduced.matches && nav.classList.contains('active')) {
        nav.classList.add('is-closing');
        closeTimer = setTimeout(finishClose, parseFloat(getComputedStyle(nav).getPropertyValue('--motion-instant')) || 120);
      } else finishClose();
      if (returnFocus) toggle.focus({ preventScroll: true });
    };
    [...nav.children].forEach((item, index) => item.style.setProperty('--menu-step', index));
    toggle.addEventListener('click', () => setOpen(!isOpen()));
    nav.addEventListener('click', event => {
      const link = event.target.closest('a');
      if (!link || !isOpen()) return;
      // Collapse geometry before the browser performs native anchor navigation.
      setOpen(false, false, true);
      if (link.hash && link.pathname === window.location.pathname) {
        const target = document.getElementById(decodeURIComponent(link.hash.slice(1)));
        if (target) {
          if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
          target.focus({ preventScroll: true });
        }
      }
    });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && isOpen()) {
        event.preventDefault();
        setOpen(false, true);
      }
    });
    document.addEventListener('click', event => {
      if (isOpen() && !header.contains(event.target)) setOpen(false, nav.contains(document.activeElement));
    });
    header.addEventListener('focusout', event => {
      if (isOpen() && event.relatedTarget && !header.contains(event.relatedTarget)) setOpen(false);
    });
    window.addEventListener('resize', () => {
      const needsFocus = mobile.matches && nav.contains(document.activeElement);
      setOpen(false, needsFocus, true);
    });
    reduced.addEventListener('change', () => { if (!isOpen()) setOpen(false, false, true); });
    setOpen(false, false, true);
    root.classList.add('navigation-enhanced');
  }

  if (document.body.classList.contains('home')) {
    const sections = [...document.querySelectorAll('main > section')];
    const links = [...document.querySelectorAll('.nav__link[href^="#"]')];
    // All seven sections are tracked without expanding the frozen six-link IA.
    const destinations = { hero: 'beranda', 'quran-teknologi': 'program', 'capaian-tahfizh': 'program' };
    const syncSection = () => {
      const line = innerHeight * 0.3;
      const current = sections.filter(section => section.getBoundingClientRect().top <= line).pop() || sections[0];
      header.dataset.activeSection = current.id;
      links.forEach(link => {
        if (link.hash === '#' + (destinations[current.id] || current.id)) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    };
    syncSection();
    if ('IntersectionObserver' in window) {
      const sentinel = document.createElement('span');
      sentinel.className = 'nav-sentinel';
      sentinel.setAttribute('aria-hidden', 'true');
      document.body.prepend(sentinel);
      const topObserver = new IntersectionObserver(([entry]) => {
        header.classList.toggle('is-scrolled', !entry.isIntersecting && entry.boundingClientRect.top < 0);
      });
      topObserver.observe(sentinel);
      let sectionObserver;
      const observeSections = () => {
        if (sectionObserver) sectionObserver.disconnect();
        const line = Math.round(innerHeight * 0.3);
        sectionObserver = new IntersectionObserver(syncSection, {
          rootMargin: `-${line}px 0px -${Math.max(0, innerHeight - line - 2)}px 0px`, threshold: 0
        });
        sections.forEach(section => sectionObserver.observe(section));
        syncSection();
      };
      observeSections();
      window.addEventListener('resize', observeSections);
      window.addEventListener('pageshow', () => {
        header.classList.toggle('is-scrolled', sentinel.getBoundingClientRect().bottom < 0);
        syncSection();
      });
    }
    window.addEventListener('hashchange', syncSection);

    const targets = [...document.querySelectorAll('[data-reveal]')];
    let revealObserver;
    const reveal = (element, immediate = false) => {
      if (immediate && (element.classList.contains('is-pending') || element.classList.contains('is-entering'))) {
        element.classList.add('reveal-immediate');
      }
      element.classList.remove('is-pending');
      if (revealObserver) revealObserver.unobserve(element);
    };
    const revealAll = () => {
      targets.forEach(element => {
        reveal(element, true);
        element.classList.remove('is-entering');
      });
      if (revealObserver) revealObserver.disconnect();
    };
    // Install the observer before arming anything. Failed initialization fails open.
    if ('IntersectionObserver' in window && !reduced.matches) {
      try {
        revealObserver = new IntersectionObserver(entries => {
          entries.forEach(entry => { if (entry.isIntersecting) reveal(entry.target); });
        }, { rootMargin: '0px 0px 140px 0px', threshold: 0 });
        targets.forEach(element => {
          element.style.setProperty('--reveal-step', element.dataset.step || 0);
          if (element.dataset.mobileStep) element.style.setProperty('--reveal-mobile-step', element.dataset.mobileStep);
          const bounds = element.getBoundingClientRect();
          if (bounds.top >= innerHeight && bounds.height) {
            revealObserver.observe(element);
            element.classList.add('is-pending');
          } else if (element.dataset.hero && bounds.bottom > 0 && scrollY < 20 && performance.now() < 1500) {
            // Finite CSS entrance only; already-painted late loads stay visible.
            element.classList.add('is-entering');
            element.addEventListener('animationend', () => element.classList.remove('is-entering'), { once: true });
          }
        });
        root.classList.add('motion-ready');
      } catch {
        root.classList.remove('motion-ready');
        revealAll();
      }
    }
    // Focusing a destination or control never leaves the reader waiting for motion.
    document.addEventListener('focusin', event => {
      targets.forEach(element => {
        if (element.contains(event.target) || event.target.contains(element)) reveal(element, true);
      });
    });
    reduced.addEventListener('change', () => { if (reduced.matches) revealAll(); });
    window.addEventListener('pageshow', event => { if (event.persisted) revealAll(); });
    window.addEventListener('beforeprint', revealAll);

    // One native modal, installed only for explicitly eligible photography.
    // The image remains an ordinary image; a separate semantic button overlays it.
    if ('HTMLDialogElement' in window && typeof HTMLDialogElement.prototype.showModal === 'function') {
      const dialog = document.createElement('dialog');
      dialog.id = 'photography-lightbox';
      dialog.className = 'photo-lightbox';
      dialog.setAttribute('aria-label', 'Foto diperbesar');
      const closeButton = document.createElement('button');
      closeButton.type = 'button';
      closeButton.className = 'photo-lightbox__close';
      closeButton.setAttribute('aria-label', 'Tutup foto');
      closeButton.textContent = '×';
      const enlarged = document.createElement('img');
      enlarged.className = 'photo-lightbox__image';
      dialog.append(closeButton, enlarged);
      document.body.append(dialog);
      let trigger;
      let savedScroll;
      let bodyStyle;
      let closeTimer;
      let backdropStart = false;
      const unlock = () => {
        if (!savedScroll) return;
        root.classList.add('is-restoring-scroll');
        root.classList.remove('is-scroll-locked');
        if (bodyStyle === null) document.body.removeAttribute('style');
        else document.body.setAttribute('style', bodyStyle);
        window.scrollTo(savedScroll.x, savedScroll.y);
        savedScroll = null;
        if (trigger && trigger.isConnected) trigger.focus({ preventScroll: true });
        root.classList.remove('is-restoring-scroll');
      };
      const finishClose = () => {
        clearTimeout(closeTimer);
        dialog.classList.remove('is-open');
        if (dialog.open) dialog.close();
        unlock();
      };
      const close = () => {
        if (!dialog.open) return;
        if (reduced.matches || !dialog.classList.contains('is-open')) {
          finishClose();
          return;
        }
        dialog.classList.remove('is-open');
        // A bounded exit; never depend on transitionend to release focus/scroll.
        closeTimer = setTimeout(finishClose, parseFloat(getComputedStyle(dialog).getPropertyValue('--motion-instant')) || 120);
      };
      const open = (button, photo) => {
        if (dialog.open) return;
        clearTimeout(closeTimer);
        trigger = button;
        enlarged.alt = photo.alt;
        enlarged.width = Number(photo.getAttribute('width'));
        enlarged.height = Number(photo.getAttribute('height'));
        enlarged.style.setProperty('--photo-max-width', enlarged.width + 'px');
        enlarged.sizes = '(max-width: 760px) calc(100vw - 32px), (max-width: 1200px) calc(100vw - 96px), 1080px';
        enlarged.srcset = photo.srcset;
        enlarged.src = photo.currentSrc || photo.src;
        savedScroll = { x: scrollX, y: scrollY };
        bodyStyle = document.body.getAttribute('style');
        const gutter = innerWidth - root.clientWidth;
        const padding = parseFloat(getComputedStyle(document.body).paddingRight);
        Object.assign(document.body.style, {
          position: 'fixed', top: `-${savedScroll.y}px`, left: '0', right: '0',
          paddingRight: `${padding + gutter}px`
        });
        root.classList.add('is-scroll-locked');
        try {
          dialog.showModal();
          closeButton.focus({ preventScroll: true });
          // One style resolution on activation establishes the opacity transition.
          // No scroll/pointer loop and no animation-frame scheduling.
          getComputedStyle(dialog).opacity;
          dialog.classList.add('is-open');
        } catch {
          finishClose();
        }
      };
      closeButton.addEventListener('click', close);
      dialog.addEventListener('cancel', event => { event.preventDefault(); close(); });
      dialog.addEventListener('close', () => { if (!dialog.open) unlock(); });
      dialog.addEventListener('pointerdown', event => { backdropStart = event.target === dialog; });
      dialog.addEventListener('click', event => {
        if (event.target === dialog && backdropStart) close();
        backdropStart = false;
      });
      // With one control, both Tab directions stay on that control. Native modal
      // inertness also excludes the underlying document and its accessibility tree.
      dialog.addEventListener('keydown', event => {
        if (event.key === 'Tab') {
          event.preventDefault();
          closeButton.focus({ preventScroll: true });
        }
      });
      reduced.addEventListener('change', () => {
        if (reduced.matches && dialog.open && !dialog.classList.contains('is-open')) finishClose();
      });
      window.addEventListener('pagehide', finishClose);
      document.querySelectorAll('[data-photo]').forEach(frame => {
        const photo = frame.querySelector('img');
        if (!photo) return;
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'photo-trigger';
        button.setAttribute('aria-label', 'Perbesar foto: ' + photo.alt);
        button.setAttribute('aria-haspopup', 'dialog');
        button.setAttribute('aria-controls', dialog.id);
        button.addEventListener('click', () => open(button, photo));
        frame.append(button);
      });
    }
  }
})();

// Existing contact-page behavior remains independent of homepage enhancement.
(() => {
  const form = document.getElementById('contactForm');
  if (!form) return;

  const fields = ['name', 'email', 'message'].map(id => ({
    input: document.getElementById(id),
    error: document.getElementById(id + 'Error')
  }));
  const status = document.getElementById('formStatus');
  const destination = document.getElementById('contact-whatsapp');
  if (!status || !destination || fields.some(field => !field.input || !field.error)) return;

  const [nameField, emailField, messageField] = fields;
  const clearError = field => {
    field.input.classList.remove('error', 'success');
    field.input.removeAttribute('aria-invalid');
    field.error.textContent = '';
  };
  const showError = (field, message) => {
    field.input.classList.add('error');
    field.input.setAttribute('aria-invalid', 'true');
    field.error.textContent = message;
  };

  form.addEventListener('submit', event => {
    event.preventDefault();
    fields.forEach(clearError);
    status.textContent = '';

    const name = nameField.input.value.trim();
    const email = emailField.input.value.trim();
    const message = messageField.input.value.trim();

    if (!name) showError(nameField, 'Nama wajib diisi');
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      showError(emailField, 'Format email tidak valid');
    }
    if (!message) showError(messageField, 'Pesan tidak boleh kosong');

    const invalid = fields.find(field => field.input.getAttribute('aria-invalid') === 'true');
    if (invalid) {
      invalid.input.focus();
      return;
    }

    const content = [
      "Assalamu'alaikum, saya ingin bertanya:",
      '',
      '👤 Nama: ' + name,
      '📧 Email: ' + (email || '(tidak diisi)'),
      '📝 Pesan: ' + message
    ].join('\n');
    // Read the authoritative destination from the existing direct contact link.
    const url = new URL(destination.href);
    url.searchParams.set('text', content);
    // A blank same-origin window allows popup detection and opener isolation.
    const popup = window.open('about:blank', '_blank');
    if (!popup) {
      status.textContent = 'WhatsApp belum terbuka. Izinkan jendela baru, lalu kirim kembali. Pesan Anda tetap tersimpan di formulir.';
      return;
    }
    popup.opener = null;
    popup.location.replace(url.href);
    form.reset();
    fields.forEach(clearError);
    status.textContent = 'WhatsApp telah dibuka. Silakan lanjutkan pengiriman pesan di WhatsApp.';
  });

  fields.forEach(field => {
    field.input.addEventListener('input', () => {
      if (field.input.hasAttribute('aria-invalid')) clearError(field);
      status.textContent = '';
    });
  });
  form.noValidate = true;
  form.hidden = false;
})();
