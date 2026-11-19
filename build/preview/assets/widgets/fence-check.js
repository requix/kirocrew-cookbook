import { mount, el, chips, pillSwitch, verdict } from "./widget-base.js";

mount("fence-check", ({ body, data }) => {
  const L = data.labels;
  const s = { ...data.start };
  const opts = (items) => items.map((x, i) => ({ value: i, label: x }));
  const bits = (mask, n) => Array.from({ length: n }, (_, i) => i).filter((i) => mask >> i & 1);
  const toMask = (set) => [...set].reduce((m, i) => m | (1 << i), 0);

  const out = verdict();
  const note = el("p", { class: "fc-note" });
  const update = () => {
    const c = data.cases[`${s.target}:${s.paths}:${s.exceptions}:${s.sandbox ? 1 : 0}`];
    out.set(c.text, c.tone);
    note.textContent = c.note;
    note.hidden = !c.note;
  };
  const row = (label, control) => el("div", { class: "fc-row" }, el("p", { class: "kw-label" }, label), control);

  body.append(
    row(L.folder, chips(opts(data.targets), { value: s.target, label: L.folder, onchange: (v) => { s.target = v; update(); } })),
    row(L.paths, chips(opts(data.paths), { value: bits(s.paths, data.paths.length), multi: true, label: L.paths, onchange: (v) => { s.paths = toMask(v); update(); } })),
    row(L.exceptions, chips(opts(data.exceptions), { value: bits(s.exceptions, data.exceptions.length), multi: true, label: L.exceptions, onchange: (v) => { s.exceptions = toMask(v); update(); } })),
    pillSwitch(L.sandbox, s.sandbox, (v) => { s.sandbox = v; update(); }),
    out.node,
    note,
  );
  update();
});
