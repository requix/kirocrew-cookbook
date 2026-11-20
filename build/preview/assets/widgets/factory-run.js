import { mount, el, iconButton, verdict, reducedMotion } from "./widget-base.js";

const STEP_MS = 2400;

mount("factory-run", ({ head, body, data }) => {
  const steps = data.steps;
  let index = 0;
  let timer = null;

  const cells = data.phases.map((p, k) => el("li", { class: "fr-cell" + (data.fence.includes(k) ? " is-fenced" : "") },
    el("span", { class: "fr-phase" }, p), el("span", { class: "fr-mark", "aria-hidden": "true" })));
  const lane = el("ol", { class: "fr-lane", "aria-label": "Phases" }, cells);
  const first = Math.min(...data.fence), last = Math.max(...data.fence);
  const fence = el("p", { class: "fr-fence", style: `--from:${first};--to:${last + 1};--n:${data.phases.length}` }, data.fence_label);

  const who = el("span", { class: "fr-who" });
  const pr = el("span", { class: "fr-pr" });
  const card = el("div", { class: "fr-card" }, el("span", { class: "kw-label" }, "Issue #142"), pr, who);

  const dotBtns = steps.map((_, i) => el("button", { type: "button", class: "kw-dot", "aria-label": `Step ${i + 1} of ${steps.length}`, onclick: () => { stop(); show(i); } }));
  const track = el("ol", { class: "kw-dots", "aria-label": "Steps" }, dotBtns.map((b) => el("li", {}, b)));
  const caption = verdict();

  const play = iconButton("play", "Play the run", () => {
    if (timer) { stop(); return; }
    if (index >= steps.length - 1) show(0);
    start();
  });
  head.append(play);

  function show(i) {
    index = i;
    const s = steps[i];
    cells.forEach((c, k) => {
      c.classList.toggle("is-visited", s.visited[k]);
      c.classList.toggle("is-reentered", s.reentered[k]);
      c.classList.toggle("is-current", k === s.phase);
      if (k === s.phase) c.setAttribute("aria-current", "step"); else c.removeAttribute("aria-current");
    });
    who.textContent = s.who;
    pr.textContent = s.pr;
    pr.hidden = !s.pr;
    dotBtns.forEach((b, k) => { b.classList.toggle("is-done", k < i); b.classList.toggle("is-current", k === i); });
    caption.set(s.caption, i === steps.length - 1 ? "ok" : "info");
  }

  function start() {
    play.setIcon("pause", "Pause the run");
    timer = setInterval(() => {
      if (index >= steps.length - 1) { stop(); return; }
      show(index + 1);
      if (index >= steps.length - 1) stop();
    }, reducedMotion() ? 1800 : STEP_MS);
  }

  function stop() {
    clearInterval(timer);
    timer = null;
    const end = index >= steps.length - 1;
    play.setIcon(end ? "replay" : "play", end ? "Play the run again" : "Play the run");
  }

  body.append(el("div", { class: "fr-stage" }, card, el("div", { class: "fr-scroll" }, lane, fence)), track, caption.node);
  show(0);
});
