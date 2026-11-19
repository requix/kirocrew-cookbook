import { mount, el, chips, pillSwitch, verdict } from "./widget-base.js";

mount("note-router", ({ body, data }) => {
  const L = data.labels;
  const s = { ...data.start };
  const opts = (labels) => labels.map((x, i) => ({ value: i, label: x }));
  const appIdx = data.apps.map((_, i) => i);

  // Priority chips are rebuilt when the kind changes, so they show that kind's usual priority.
  const prioSlot = el("div", {});
  const prioChips = () => chips(opts(data.priorities), { value: s.priority, label: L.priority, onchange: (v) => { s.priority = v; update(); } });

  const tile = (name) => {
    const sub = el("p", { class: "nr-sub" });
    const node = el("div", { class: "nr-tile" }, el("p", { class: "nr-name" }, name), sub);
    return { node, sub };
  };
  const card = tile(data.places.card);
  const dms = data.apps.map((a) => ({ id: a.id, ...tile(`${a.label} ${data.places.dm}`) }));
  const out = verdict();

  function update() {
    const c = data.cases[`${s.kind}:${s.priority}:${s.route}:${s.apps}:${s.preview ? 1 : 0}`];
    card.node.classList.toggle("is-on", c.card);
    dms.forEach((d, i) => {
      const on = c.dm.includes(d.id);
      d.node.classList.toggle("is-on", on);
      d.node.hidden = !(s.apps >> i & 1);
      d.sub.textContent = on ? (c.answers[d.id] || "") : "";
    });
    out.set(c.text, c.tone);
  }

  const row = (label, control) => el("div", { class: "nr-row" }, el("p", { class: "kw-label" }, label), control);
  prioSlot.append(prioChips());
  body.append(
    row(L.kind, chips(data.kinds.map((k, i) => ({ value: i, label: k.label })), { value: s.kind, label: L.kind, onchange: (v) => {
      s.kind = v; s.priority = data.kinds[v].priority; prioSlot.replaceChildren(prioChips()); update();
    } })),
    row(L.priority, prioSlot),
    row(L.route, chips(opts(data.routes), { value: s.route, label: L.route, onchange: (v) => { s.route = v; update(); } })),
    row(L.apps, chips(data.apps.map((a, i) => ({ value: i, label: a.label })), {
      value: appIdx.filter((i) => s.apps >> i & 1), multi: true, label: L.apps,
      onchange: (set) => { s.apps = [...set].reduce((m, i) => m | (1 << i), 0); update(); } })),
    pillSwitch(L.preview, s.preview, (v) => { s.preview = v; update(); }),
    el("div", { class: "nr-places" }, card.node, dms.map((d) => d.node)),
    out.node,
  );
  update();
});
