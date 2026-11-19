import { mount, el, iconButton, verdict, reducedMotion } from "./widget-base.js";

const STEP_MS = 2600;

mount("conductor-run", ({ head, body, data }) => {
  const L = data.labels;
  const steps = data.steps;
  let index = 0;
  let timer = null;

  // Conductor and workers
  const cSub = el("p", { class: "cr-sub" });
  const conductor = el("div", { class: "cr-node cr-conductor" }, el("p", { class: "cr-name" }, data.conductor.name), cSub);
  const workerNodes = steps[0].workers.map((w) => {
    const sub = el("p", { class: "cr-sub" });
    const node = el("div", { class: "cr-node cr-worker" }, el("p", { class: "cr-name" }, w.name), sub);
    return { id: w.id, node, sub };
  });
  const workers = el("div", { class: "cr-workers" }, workerNodes.map((w) => w.node));

  // Board
  const paused = el("span", { class: "cr-tag" }, L.paused);
  const pauseTag = el("span", { class: "cr-tag" }, L.pause_all);
  const resumeTag = el("span", { class: "cr-tag" }, L.resume_all);
  const recapText = el("p", { class: "cr-text" });
  const needsBox = el("div", {});
  const msCount = el("span", {});
  const msBox = el("div", {});
  const sec = (title, extra, content) => el("div", { class: "cr-sec" },
    el("p", { class: "kw-label" }, el("span", {}, title), extra), content);
  const board = el("div", { class: "cr-board" },
    el("div", { class: "cr-board-head" }, el("p", { class: "kw-label" }, L.board), paused, pauseTag, resumeTag),
    el("div", { class: "cr-sections" },
      sec(L.recap, null, recapText),
      sec(L.needs_you, null, needsBox),
      sec(L.milestones, msCount, msBox)));

  const stage = el("div", { class: "cr-stage" }, conductor, el("div", { class: "cr-link", "aria-hidden": "true" }), workers, board);

  // Dot track: real buttons so each step is reachable by keyboard
  const dotBtns = steps.map((s, i) => el("button", { type: "button", class: "kw-dot", "aria-label": `Step ${i + 1} of ${steps.length}`, onclick: () => { stop(); show(i); } }));
  const track = el("ol", { class: "kw-dots", "aria-label": "Steps" }, dotBtns.map((b) => el("li", {}, b)));
  const caption = verdict();

  const play = iconButton("play", "Play the run", () => {
    if (timer) { stop(); return; }
    if (index >= steps.length - 1) show(0);
    start();
  });
  head.append(play);

  function list(items, empty) {
    return items.length ? el("ul", { class: "cr-rows" }, items.map((t) => el("li", {}, ...t))) : el("p", { class: "cr-text" }, empty);
  }

  function show(i) {
    index = i;
    const s = steps[i];
    conductor.classList.toggle("is-active", s.conductor.state !== "idle");
    cSub.textContent = s.conductor.label;
    s.workers.forEach((w, k) => {
      workerNodes[k].node.dataset.state = w.state;
      workerNodes[k].sub.textContent = w.state === "absent" ? "" : (w.label || w.task);
    });
    paused.hidden = !s.paused;
    pauseTag.classList.toggle("is-on", s.control === L.pause_all);
    resumeTag.classList.toggle("is-on", s.control === L.resume_all);
    recapText.textContent = s.recap;
    needsBox.replaceChildren(list(s.needs_you.map((n) => [el("span", {}, n)]), L.needs_you_none));
    msCount.textContent = s.milestones;
    msBox.replaceChildren(list(s.workers.filter((w) => w.board).map((w) => [el("span", {}, w.name), el("span", {}, w.board)]), L.milestones_none));
    dotBtns.forEach((b, k) => {
      b.classList.toggle("is-done", k < i);
      b.classList.toggle("is-current", k === i);
      if (k === i) b.setAttribute("aria-current", "step"); else b.removeAttribute("aria-current");
    });
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
    play.setIcon(index >= steps.length - 1 ? "replay" : "play", index >= steps.length - 1 ? "Play the run again" : "Play the run");
  }

  body.append(stage, track, caption.node);
  show(0);
});
