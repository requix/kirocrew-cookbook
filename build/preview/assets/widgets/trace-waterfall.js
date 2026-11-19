import { mount, el, verdict } from "./widget-base.js";

mount("trace-waterfall", ({ body, data }) => {
  const detailName = el("p", { class: "tw-dname" });
  const detailAbout = el("p", { class: "tw-about" });
  const detailAttrs = el("dl", { class: "tw-attrs" });
  const never = verdict();
  never.set(data.never, "stop");

  const rows = data.spans.map((s, i) => {
    const bar = el("span", { class: "tw-bar" + (s.slow ? " is-slow" : ""), style: `left:${s.left}%;width:max(${s.width}%,3px)` });
    const btn = el("button", { type: "button", class: "tw-row", "aria-pressed": "false", onclick: () => pick(i) },
      el("span", { class: "tw-name", style: `padding-left:${s.depth * 12}px` }, s.name),
      el("span", { class: "tw-lane" }, bar),
      el("span", { class: "tw-secs" }, `${s.secs}s`));
    return btn;
  });

  function pick(i) {
    const s = data.spans[i];
    rows.forEach((r, k) => r.setAttribute("aria-pressed", String(k === i)));
    detailName.textContent = s.name;
    detailAbout.textContent = s.about;
    detailAttrs.replaceChildren(...s.attrs.flatMap(([k, v]) => [el("dt", {}, k), el("dd", {}, v)]));
  }

  body.append(
    el("div", { class: "tw-chart", role: "group", "aria-label": "Spans, click one for details" }, rows),
    el("div", { class: "tw-detail", "aria-live": "polite" }, detailName, detailAbout, detailAttrs),
    never.node,
  );
  pick(data.start);
});
