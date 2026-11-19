// Shared helpers for interactive widgets. Import from a widget's own module:
//   import { mount, el, chips, pillSwitch, dots, verdict, iconButton, reducedMotion } from "./widget-base.js";

export const reducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/** el("div", {class: "x", onclick: fn}, child, "text") */
export function el(tag, attrs = {}, ...kids) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null || v === false) continue;
    if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
    else if (k === "class") n.className = v;
    else n.setAttribute(k, v === true ? "" : v);
  }
  for (const k of kids.flat()) if (k != null && k !== false) n.append(k.nodeType ? k : document.createTextNode(String(k)));
  return n;
}

const ICONS = {
  play: '<path d="M7 5l12 7-12 7z"/>',
  pause: '<path d="M8 5v14M16 5v14"/>',
  replay: '<path d="M4 12a8 8 0 1 0 2.3-5.6M4 4v4h4"/>',
};

/** An icon-only button with an accessible label. */
export function iconButton(icon, label, onclick) {
  const b = el("button", { type: "button", class: "kw-icon", "aria-label": label, title: label, onclick });
  b.innerHTML = `<svg viewBox="0 0 24 24" aria-hidden="true">${ICONS[icon]}</svg>`;
  b.setIcon = (name, lab) => { b.innerHTML = `<svg viewBox="0 0 24 24" aria-hidden="true">${ICONS[name]}</svg>`; b.setAttribute("aria-label", lab); b.title = lab; };
  return b;
}

/** Chips. multi=false: pick one (radiogroup). multi=true: toggle many. onchange(valueOrSet). */
export function chips(options, { value, multi = false, label, onchange }) {
  const sel = multi ? new Set(value || []) : value;
  const list = el("div", { class: "kw-chips", role: multi ? "group" : "radiogroup", "aria-label": label });
  const btns = options.map((o) => {
    const b = el("button", { type: "button", class: "kw-chip", "data-value": o.value }, o.label);
    if (multi) b.setAttribute("aria-pressed", String(sel.has(o.value)));
    else { b.setAttribute("role", "radio"); b.setAttribute("aria-checked", String(o.value === sel)); }
    b.addEventListener("click", () => {
      if (multi) { sel.has(o.value) ? sel.delete(o.value) : sel.add(o.value); b.setAttribute("aria-pressed", String(sel.has(o.value))); onchange(new Set(sel)); }
      else { btns.forEach((x) => x.setAttribute("aria-checked", String(x === b))); onchange(o.value); }
    });
    list.append(b);
    return b;
  });
  return list;
}

/** A small labelled on/off switch. */
export function pillSwitch(label, on, onchange) {
  const b = el("button", { type: "button", class: "kw-switch", role: "switch", "aria-checked": String(!!on) },
    el("span", { class: "kw-switch__track", "aria-hidden": "true" }), el("span", {}, label));
  b.addEventListener("click", () => { const v = b.getAttribute("aria-checked") !== "true"; b.setAttribute("aria-checked", String(v)); onchange(v); });
  return b;
}

/** A dot track. Returns {node, set(i)} where i is the current index (-1 for none). */
export function dots(n, label) {
  const node = el("ol", { class: "kw-dots", "aria-label": label });
  const items = Array.from({ length: n }, () => node.appendChild(el("li", { class: "kw-dot" })));
  return { node, set(i) { items.forEach((d, k) => { d.classList.toggle("is-done", k < i); d.classList.toggle("is-current", k === i); }); } };
}

/** The one-line verdict. tone: ok | stop | info. Announced politely to screen readers. */
export function verdict() {
  const node = el("p", { class: "kw-verdict", "aria-live": "polite" });
  return { node, set(text, tone = "info") { node.textContent = text; node.dataset.tone = tone; } };
}

/** Find every mount for this widget, parse its data, build the card shell, call render. */
export function mount(name, render) {
  for (const root of document.querySelectorAll(`[data-widget="${name}"]`)) {
    const data = JSON.parse(root.querySelector("script[data-widget-data]").textContent);
    const head = el("div", { class: "kw-head" }, el("p", { class: "kw-title" }, data.title || ""));
    const body = el("div", { class: "kw-body" });
    root.querySelector("noscript")?.remove();
    root.append(head, body);
    render({ root, head, body, data });
    root.classList.add("is-ready");
  }
}
