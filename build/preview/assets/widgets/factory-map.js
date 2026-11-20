import { mount, el, verdict } from "./widget-base.js";

mount("factory-map", ({ body, data }) => {
  const tiles = [];
  const name = el("p", { class: "fm-name" });
  const feats = el("ul", { class: "kw-chips fm-feats", "aria-label": "Kiro Crew parts" });
  const says = verdict();
  const more = el("a", { class: "fm-more" }, "Read this part");

  const zones = data.zones.map((z) => el("div", { class: "fm-zone" },
    el("p", { class: "kw-label" }, z.label),
    el("div", { class: "fm-tiles" }, z.stations.map((i) => {
      const b = el("button", { type: "button", class: "fm-tile", "aria-pressed": "false", onclick: () => pick(i) },
        el("span", { class: "fm-num" }, String(i + 1)), el("span", {}, data.stations[i].name));
      tiles[i] = b;
      return b;
    }))));

  function pick(i) {
    const s = data.stations[i];
    tiles.forEach((t, k) => t.setAttribute("aria-pressed", String(k === i)));
    name.textContent = s.name;
    feats.replaceChildren(...s.features.map((f) => el("li", { class: "kw-chip fm-feat" }, f)));
    says.set(s.says, "info");
    more.href = `#${s.anchor}`;
  }

  body.append(
    el("div", { class: "fm-zones" }, zones),
    el("div", { class: "fm-detail", "aria-live": "polite" }, el("div", { class: "fm-detail-head" }, name, more), feats),
    says.node,
  );
  pick(data.start);
});
