"use strict";

"use strict";

/* =========================
   NAV ELEMENTS
========================= */
const toggle = document.querySelector('.nav__toggle');
const nav = document.querySelector('.nav__list');
const links = document.querySelectorAll('.nav__link');
const header = document.querySelector('.header');


if (toggle && nav) {
  /* =========================
    MOBILE MENU TOGGLE
  ========================= */
  toggle.addEventListener('click', () => {
    nav.classList.toggle('active');
  });


  // Close menu when clicking a link
  links.forEach(link => {
    link.addEventListener('click', () => {
      nav.classList.remove('active');
    });
  });

  document.addEventListener('click', (e) => {
    if (!nav.contains(e.target) && !toggle.contains(e.target)) {
      nav.classList.remove('active');
    }
  });
}

// Close menu when clicking outside
document.addEventListener('click', (e) => {
  if (!nav.contains(e.target) && !toggle.contains(e.target)) {
    nav.classList.remove('active');
  }
});

/* =========================
   HEADER SCROLL EFFECT
========================= */

window.addEventListener('scroll', () => {
  if (header) {
    if (window.scrollY > 50) {
      header.classList.add('header--scrolled');
    } else {
      header.classList.remove('header--scrolled');
    }
  }
});

/* =========================
   ACTIVE LINK DETECTION
========================= */
const currentPage = window.location.pathname.split("/").pop();

links.forEach(link => {
  const linkPage = link.getAttribute("href");

  if (linkPage === currentPage) {
    link.classList.add("active");
  }

  if (currentPage === "") {
    document.querySelector('a[href="index.html"]').classList.add("active");
  }
});

/* =========================
   CONTACT FORM VALIDATION
========================= */
const form = document.getElementById('contactForm');

if (form) {
  const nameInput = document.getElementById('name');
  const emailInput = document.getElementById('email');
  const messageInput = document.getElementById('message');

  form.addEventListener('submit', function (e) {
    e.preventDefault();

    let isValid = true;

    // RESET
    clearError(nameInput);
    clearError(emailInput);
    clearError(messageInput);

    // NAME
    if (nameInput.value.trim() === '') {
      showError(nameInput, 'Nama wajib diisi');
      isValid = false;
    } else {
      showSuccess(nameInput);
    }

    // EMAIL
    // EMAIL (OPTIONAL)
    if (emailInput.value.trim() !== '') {
      if (!isEmailValid(emailInput.value)) {
        showError(emailInput, 'Format email tidak valid');
        isValid = false;
      } else {
        showSuccess(emailInput);
      }
    }

    // MESSAGE
    if (messageInput.value.trim() === '') {
      showError(messageInput, 'Pesan tidak boleh kosong');
      isValid = false;
    } else {
      showSuccess(messageInput);
    }

    // SUCCESS SEND TO WHATSAPP
    if (isValid) {
      /* SEND TO WHATSAPP */
if (isValid) {

  const phoneNumber = "6281315452107";

  const emailText = emailInput.value 
  ? `📧 Email: ${emailInput.value}` 
  : `📧 Email: (tidak diisi)`;

  const message = 
  `Assalamu'alaikum, saya ingin bertanya:

  👤 Nama: ${nameInput.value}
  ${emailText}
  📝 Pesan: ${messageInput.value}`;

    const encodedMessage = encodeURIComponent(message);

    const url = `https://wa.me/${phoneNumber}?text=${encodedMessage}`;

    window.open(url, "_blank");

    form.reset();

    [nameInput, emailInput, messageInput].forEach(input => {
      input.classList.remove('success');
    });
  }
    }
  });

  function showError(input, message) {
    input.classList.add('error');
    const error = input.nextElementSibling;
    error.textContent = message;
  }

  function showSuccess(input) {
    input.classList.add('success');
  }

  function clearError(input) {
    input.classList.remove('error');
    const error = input.nextElementSibling;
    error.textContent = '';
  }

  function isEmailValid(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }
}




/* =========================
   SCROLL REVEAL ANIMATION
========================= */
const reveals = document.querySelectorAll('.reveal');

function revealOnScroll() {
  const windowHeight = window.innerHeight;

  reveals.forEach(el => {
    const elementTop = el.getBoundingClientRect().top;

    if (elementTop < windowHeight - 100) {
      el.classList.add('active');
    }
  });
}

window.addEventListener('scroll', revealOnScroll);

// run once on load
revealOnScroll();