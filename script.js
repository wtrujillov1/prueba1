"use strict";

// Without JavaScript the navigation and every project remain visible.
const menuButton = document.querySelector(".menu-toggle");
const navigation = document.querySelector("#navegacion");
const desktop = window.matchMedia("(min-width: 1024px)");

function setMenu(open) {
  menuButton.setAttribute("aria-expanded", String(open));
  navigation.hidden = !open;
}

function syncMenu() {
  menuButton.hidden = desktop.matches;
  setMenu(desktop.matches);
}

menuButton.addEventListener("click", () => {
  setMenu(menuButton.getAttribute("aria-expanded") !== "true");
});

navigation.addEventListener("click", (event) => {
  const link = event.target.closest("a");
  if (!link || desktop.matches) return;
  event.preventDefault();
  setMenu(false);
  const section = document.querySelector(link.getAttribute("href"));
  const heading = section?.querySelector("h1, h2");
  if (heading) {
    heading.setAttribute("tabindex", "-1");
    heading.focus({ preventScroll: true });
  }
  if (window.location.hash !== link.hash)
    history.pushState(null, "", link.hash);
  section?.scrollIntoView({ block: "start" });
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !desktop.matches && !navigation.hidden) {
    setMenu(false);
    menuButton.focus();
  }
});

desktop.addEventListener("change", syncMenu);
syncMenu();

const filters = document.querySelector(".filters");
const filterButtons = [...filters.querySelectorAll("button")];
const projects = [...document.querySelectorAll(".project-card")];
const count = document.querySelector("#project-count");
filters.hidden = false;

filters.addEventListener("click", (event) => {
  const selected = event.target.closest("[data-filter]");
  if (!selected) return;
  filterButtons.forEach((button) => {
    button.setAttribute("aria-pressed", String(button === selected));
  });
  let visible = 0;
  projects.forEach((project) => {
    project.hidden =
      selected.dataset.filter !== "todos" &&
      project.dataset.category !== selected.dataset.filter;
    if (!project.hidden) visible += 1;
  });
  count.textContent = `${visible} ${visible === 1 ? "proyecto" : "proyectos"} para descubrir`;
});

const form = document.querySelector("#registration-form");
const formFields = document.querySelector("#registration-fields");
const feedback = document.querySelector("#form-feedback");
const fields = [
  {
    input: document.querySelector("#full-name"),
    error: document.querySelector("#name-error"),
  },
  {
    input: document.querySelector("#email"),
    error: document.querySelector("#email-error"),
  },
  {
    input: document.querySelector("#role"),
    error: document.querySelector("#role-error"),
  },
  {
    input: document.querySelector("#consent"),
    error: document.querySelector("#consent-error"),
  },
];
formFields.disabled = false;
form.noValidate = true;

function validationMessage(input) {
  if (input.id === "full-name" && input.value.trim().length < 3)
    return "Escribe tu nombre con al menos 3 caracteres.";
  if (input.id === "email" && !input.value.trim())
    return "Escribe tu correo electrónico.";
  if (input.id === "email" && !input.validity.valid)
    return "Escribe un correo válido, como nombre@ejemplo.com.";
  if (input.id === "role" && !input.value)
    return "Selecciona cómo quieres participar.";
  if (input.id === "consent" && !input.checked)
    return "Confirma que entiendes el alcance de esta demostración.";
  return "";
}

function validateField(field) {
  const message = validationMessage(field.input);
  field.error.textContent = message;
  field.error.hidden = !message;
  if (message) field.input.setAttribute("aria-invalid", "true");
  else field.input.removeAttribute("aria-invalid");
  return !message;
}

fields.forEach((field) => {
  field.input.addEventListener("input", () => {
    if (field.input.hasAttribute("aria-invalid")) validateField(field);
    feedback.textContent = "";
  });
  field.input.addEventListener("change", () => {
    if (field.input.hasAttribute("aria-invalid")) validateField(field);
    feedback.textContent = "";
  });
});

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const invalid = fields.filter((field) => !validateField(field));
  feedback.classList.toggle("is-error", invalid.length > 0);
  if (invalid.length) {
    feedback.textContent = `Revisa ${invalid.length} ${invalid.length === 1 ? "campo indicado" : "campos indicados"} para continuar.`;
    invalid[0].input.focus();
    return;
  }
  feedback.textContent =
    "¡Todo listo! Tus datos son válidos. Esta demostración no envía datos ni confirma una inscripción real.";
  form.reset();
});
