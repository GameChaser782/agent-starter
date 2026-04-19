const buttons = Array.from(document.querySelectorAll(".tab-button"));
const panels = Array.from(document.querySelectorAll(".tab-panel"));
const toggle = document.querySelector(".theme-toggle");
const themeStorageKey = "agent-starter-docs-theme";

function applyTheme(theme) {
  document.body.classList.toggle("dark", theme === "dark");
}

function getPreferredTheme() {
  const saved = window.localStorage.getItem(themeStorageKey);
  if (saved === "light" || saved === "dark") {
    return saved;
  }

  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function animateThemeSwitch(nextTheme) {
  document.body.classList.add("theme-animating");
  document.body.style.setProperty("--wave-scale", "0");
  const viewportWidth = window.innerWidth;
  const viewportHeight = window.innerHeight;
  const originX = viewportWidth - 42;
  const originY = 42;
  const farthestX = Math.max(originX, viewportWidth - originX);
  const farthestY = Math.max(originY, viewportHeight - originY);
  const radius = Math.hypot(farthestX, farthestY);
  const baseRadius = 24;
  const scale = Math.ceil(radius / baseRadius) + 2;
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      document.body.style.setProperty("--wave-scale", String(scale));
    });
  });

  window.setTimeout(() => applyTheme(nextTheme), 220);
  window.setTimeout(() => {
    document.body.classList.remove("theme-animating");
    document.body.style.removeProperty("--wave-scale");
  }, 560);
}

function activateTab(target) {
  buttons.forEach((button) => {
    const active = button.dataset.tab === target;
    button.classList.toggle("active", active);
    button.setAttribute("aria-selected", String(active));
  });

  panels.forEach((panel) => {
    const active = panel.dataset.panel === target;
    panel.classList.toggle("active", active);
    panel.hidden = !active;
  });

  const url = new URL(window.location.href);
  url.hash = target;
  window.history.replaceState({}, "", url);
}

buttons.forEach((button) => {
  button.addEventListener("click", () => activateTab(button.dataset.tab));
});

const initial = window.location.hash.replace("#", "");
if (initial && buttons.some((button) => button.dataset.tab === initial)) {
  activateTab(initial);
}

applyTheme(getPreferredTheme());

window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (event) => {
  const saved = window.localStorage.getItem(themeStorageKey);
  if (!saved) {
    applyTheme(event.matches ? "dark" : "light");
  }
});

toggle?.addEventListener("click", () => {
  const nextTheme = document.body.classList.contains("dark") ? "light" : "dark";
  window.localStorage.setItem(themeStorageKey, nextTheme);
  animateThemeSwitch(nextTheme);
});
