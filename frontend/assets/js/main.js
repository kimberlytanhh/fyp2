// =========================
// UI / ANIMATION HELPERS
// =========================
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) entry.target.classList.add("visible");
  });
}, { threshold: 0.12 });

document.querySelectorAll(".reveal").forEach((el) => observer.observe(el));

// === Mobile nav toggle ===
(function () {
  const toggle = document.querySelector(".nav-toggle");
  const menu = document.querySelector("#menu");
  if (!toggle || !menu) return;
  toggle.addEventListener("click", () => {
    const expanded = toggle.getAttribute("aria-expanded") === "true";
    toggle.setAttribute("aria-expanded", String(!expanded));
    menu.classList.toggle("show");
  });
})();

// =========================
// TOAST / MODAL HELPERS
// =========================
window.showToast = function (message) {
  const toast = document.querySelector(".toast");
  if (!toast) { alert(message); return; }
  const titleEl = toast.querySelector("strong");
  const bodyP = toast.querySelector("p") || document.createElement("p");
  if (!bodyP.parentNode) toast.querySelector(".toast-inner").appendChild(bodyP);
  if (titleEl) titleEl.textContent = "Notice";
  bodyP.textContent = message;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2600);
};

(function () {
  const btn = document.querySelector(".close-toast");
  const toast = document.querySelector(".toast");
  if (btn && toast) btn.addEventListener("click", () => toast.classList.remove("show"));
})();

// =========================
// FLASH MESSAGE (AFTER REDIRECT)
// =========================
document.addEventListener("DOMContentLoaded", () => {
  try {
    const msg = sessionStorage.getItem("flash");
    if (msg) {
      sessionStorage.removeItem("flash");
      showToast(msg);
    }
  } catch {}
});

// =========================
// AUTH (JWT-BASED)
// =========================
function isAuthenticated() {
  return !!localStorage.getItem("access_token");
}

function requireAuth() {
  if (!isAuthenticated()) {
    sessionStorage.setItem("flash", "Please log in to continue.");
    window.location.href = "login.html";
    return false;
  }
  return true;
}

function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("token_type");
  sessionStorage.setItem("flash", "Signed out.");
  window.location.href = "index.html";
}

window.getToken = function () {
  return localStorage.getItem("access_token");
};

window.isAuthenticated = isAuthenticated;
window.requireAuth = requireAuth;
window.logout = logout;

// =========================
// NAVBAR AUTH STATE
// =========================
function updateNavAuth() {
  const menu = document.querySelector("#menu");
  if (!menu) return;

  // remove old injected auth links
  menu.querySelectorAll("[data-auth]").forEach(el => el.remove());

  if (isAuthenticated()) {
    const liProfile = document.createElement("li");
    liProfile.setAttribute("data-auth", "1");
    liProfile.innerHTML = '<a href="profile.html">Profile</a>';

    const liLogout = document.createElement("li");
    liLogout.setAttribute("data-auth", "1");
    const a = document.createElement("a");
    a.href = "#";
    a.textContent = "Logout";
    a.addEventListener("click", (e) => {
      e.preventDefault();
      logout();
    });
    liLogout.appendChild(a);

    menu.appendChild(liProfile);
    menu.appendChild(liLogout);
  } else {
    const liLogin = document.createElement("li");
    liLogin.setAttribute("data-auth", "1");
    liLogin.innerHTML = '<a href="login.html">Login</a>';
    menu.appendChild(liLogin);
  }
}

document.addEventListener("DOMContentLoaded", updateNavAuth);

// =========================
// PROTECT CREATE REPORT LINK
// =========================
document.addEventListener("click", (e) => {
  const a = e.target.closest('a[href$="createreport.html"]');
  if (!a) return;
  if (!isAuthenticated()) {
    e.preventDefault();
    sessionStorage.setItem("flash", "Please log in to create a report.");
    window.location.href = "login.html";
  }
});

// =========================
// FOOTER YEAR
// =========================
(function () {
  const y = document.getElementById("year");
  if (y) y.textContent = new Date().getFullYear();
})();
