"use strict";

(() => {
  const toggle = document.querySelector('.nav__toggle');
  const nav = document.getElementById('primary-navigation');
  const header = document.querySelector('.header');

  if (toggle && nav && header) {
    const mobile = window.matchMedia('(max-width: 760px)');
    const isOpen = () => toggle.getAttribute('aria-expanded') === 'true';
    const setOpen = (open, returnFocus = false) => {
      nav.classList.toggle('active', open);
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Tutup navigasi' : 'Buka navigasi');
      if (returnFocus) toggle.focus();
    };

    toggle.addEventListener('click', () => setOpen(!isOpen()));
    nav.addEventListener('click', event => {
      const link = event.target.closest('a');
      if (!link || !isOpen()) return;
      setOpen(false);
      // Move keyboard focus to the destination before collapsing its source link.
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
      if (isOpen() && !header.contains(event.target)) {
        setOpen(false, nav.contains(document.activeElement));
      }
    });
    header.addEventListener('focusout', event => {
      if (isOpen() && event.relatedTarget && !header.contains(event.relatedTarget)) setOpen(false);
    });
    mobile.addEventListener('change', () => setOpen(false));
    // Enhance only after the disclosure handlers are installed.
    document.documentElement.classList.add('navigation-enhanced');
  }

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
  // No reveal or scroll listeners: content is visible, including reduced-motion users.
})();
