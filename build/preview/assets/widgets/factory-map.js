import { mount, el } from "./widget-base.js";

mount("factory-map", ({ body, data }) => {
  const n = data.stations.length;
  const stops = [];
  const zones = data.zones.map((z) => el("li", { class: "fm-zone", style: `grid-column: span ${z.stations.length}` },
    el("span", {}, z.label)));

  const track = el("ol", { class: "fm-track", role: "tablist", "aria-label": data.title, style: `--n:${n}` },
    data.stations.map((s, i) => {
      const b = el("button", { type: "button", class: "fm-stop", role: "tab", "aria-selected": "false", tabindex: "-1",
        onclick: () => pick(i), onkeydown: (e) => key(e, i) },
        el("span", { class: "fm-dot" }, String(i + 1)), el("span", { class: "fm-label" }, s.name));
      stops[i] = b;
      return el("li", {}, b);
    }));

  const name = el("p", { class: "fm-name" });
  const more = el("a", { class: "fm-more" }, "Read section");
  const says = el("p", { class: "fm-says" });
  const feats = el("ul", { class: "fm-feats", "aria-label": "Kiro Crew parts" });
  const papers = el("span", {});
  const testTag = el("span", { class: "fm-tag" });
  const testNote = el("span", {});
  const meta = el("dl", { class: "fm-meta" },
    el("dt", {}, "Papers"), el("dd", {}, papers),
    el("dt", {}, "Lab"), el("dd", {}, testTag, testNote));
  const detail = el("div", { class: "fm-detail", role: "tabpanel", "aria-live": "polite" },
    el("div", { class: "fm-detail-head" }, name, more), says, feats, meta);

  function key(e, i) {
    const to = { ArrowRight: i + 1, ArrowLeft: i - 1, Home: 0, End: n - 1 }[e.key];
    if (to == null) return;
    e.preventDefault();
    const j = (to + n) % n;
    pick(j);
    stops[j].focus();
  }

  function pick(i) {
    const s = data.stations[i];
    stops.forEach((b, k) => {
      b.setAttribute("aria-selected", String(k === i));
      b.tabIndex = k === i ? 0 : -1;
      b.classList.toggle("is-passed", k < i);
    });
    name.textContent = `${i + 1}. ${s.name}`;
    says.textContent = s.says;
    feats.replaceChildren(...s.features.map((f) => el("li", {}, f)));
    more.href = `#${s.anchor}`;
    papers.textContent = s.papers.join(", ");
    testTag.textContent = s.tested.label;
    testTag.dataset.status = s.tested.status;
    testNote.textContent = s.tested.note;
  }

  body.append(el("div", { class: "fm-scroll" }, el("ol", { class: "fm-zones", style: `--n:${n}` }, zones), track), detail);
  pick(data.start);
});
