// "Where is…?" — search a task, then watch a pointer click through a drawn KiroCrew dashboard.
// Data comes from the page (#wi-data), built from KiroCrew's own UI index. No framework, no network.
// The drawing (kc-drawing.js) is decorative and aria-hidden; the numbered step list carries the answer.
import { createDrawing, h, HOME, showDrawing } from './kc-drawing.js'

const MOVE_MS = 650, PAUSE_MS = 1100

const root = document.querySelector('[data-where-is]')
if (root) init(root)

function init(root) {
  const data = JSON.parse(root.querySelector('#wi-data').textContent)
  const tasks = data.tasks
  const byId = Object.fromEntries(tasks.map(t => [t.id, t]))
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)')
  const base = new URL('../', import.meta.url).href   // site root: this file lives in assets/

  const $q = root.querySelector('#wi-q')
  const $list = root.querySelector('#wi-list')
  const $count = root.querySelector('#wi-count')
  const $answer = root.querySelector('#wi-answer')
  const dr = createDrawing({ canvas: root.querySelector('#wi-canvas'), frame: root.querySelector('.wi-frame'), D: data.drawing })

  let current = null, stepIdx = -1, playing = false, run = 0
  const wait = ms => new Promise(r => setTimeout(r, ms))
  const has = (task, loc) => task.steps.some(s => s.loc === loc)

  // ------------------------------------------------------------ finder list
  const items = []
  let lastGroup = null
  for (const t of tasks) {
    if (t.group !== lastGroup) { $list.append(h('p', { class: 'wi-group' }, t.group)); lastGroup = t.group }
    const btn = h('button', { type: 'button', class: 'wi-item', 'aria-pressed': 'false', onclick: () => select(t.id, true) },
      h('span', { class: 'wi-item__task' }, t.task),
      h('span', { class: 'wi-item__path' }, t.steps.map(s => s.label).join(' → ')))
    btn.dataset.id = t.id
    const hay = [t.task, t.group, t.why, ...t.terms, ...t.steps.map(s => s.label)].join(' ').toLowerCase()
    items.push({ t, btn, hay })
    $list.append(btn)
  }
  function filter() {
    const words = $q.value.toLowerCase().split(/\s+/).filter(Boolean)
    let shown = 0
    for (const it of items) {
      const ok = words.every(w => it.hay.includes(w))
      it.btn.hidden = !ok
      if (ok) shown++
    }
    for (const g of $list.querySelectorAll('.wi-group')) {
      let n = g.nextElementSibling, any = false
      while (n && !n.classList.contains('wi-group')) { if (!n.hidden) any = true; n = n.nextElementSibling }
      g.hidden = !any
    }
    $count.textContent = words.length === 0 ? `${tasks.length} hard-to-find things`
      : shown ? `${shown} match${shown === 1 ? '' : 'es'}`
      : 'No match. Check the table below, or ask your agent where it is.'
  }
  $q.addEventListener('input', filter)
  $q.addEventListener('keydown', e => {
    const first = items.find(it => !it.btn.hidden)
    if (e.key === 'Enter' && first) { e.preventDefault(); select(first.t.id, true) }
    if (e.key === 'ArrowDown' && first) { e.preventDefault(); first.btn.focus() }
  })
  $list.addEventListener('keydown', e => {
    if (!['ArrowDown', 'ArrowUp'].includes(e.key)) return
    const vis = items.filter(it => !it.btn.hidden).map(it => it.btn)
    const i = vis.indexOf(document.activeElement)
    if (i < 0) return
    e.preventDefault()
    if (e.key === 'ArrowUp' && i === 0) { $q.focus(); return }
    vis[Math.max(0, Math.min(vis.length - 1, i + (e.key === 'ArrowDown' ? 1 : -1)))].focus()
  })
  filter()

  // ------------------------------------------------------------ drawing state after the first k clicks
  function stateAt(task, k) {
    const s = { ...HOME }
    for (const step of task.steps.slice(0, k)) {
      if (step.loc.startsWith('page.')) Object.assign(s, { screen: step.loc, sidetab: null, subnav: null, ctab: null, menu: null })
      else if (step.area === 'sidetab') Object.assign(s, { sidetab: step.loc, subnav: null, ctab: null })
      else if (step.area === 'subnav') s.subnav = step.loc
      else if (step.area === 'contenttab') s.ctab = step.loc
      else if (step.loc === 'chat.side-panel-open') s.panel = true
      else if (step.loc === 'x.job-row') s.job = true
      else if (step.area === 'menubutton' || step.loc === 'x.project-pill' || step.loc === 'x.agent-selector') s.menu = step.loc
    }
    return s
  }
  function draw(task, k) {
    const want = task.steps.map(st => st.loc)
    dr.render(stateAt(task, k), { want, empty: has(task, 'chat.memory-mode'), mates: has(task, 'page.members'), next: want[k] })
  }
  function mark(task, upto) {
    task.steps.forEach((st, i) => {
      if (i > upto) return
      const el = dr.find(st.loc)
      if (!el) return
      el.classList.add(i === upto ? 'is-hot' : 'is-visited')
      dr.badge(el, i + 1, i === upto)
    })
  }
  dr.onFit(() => { if (current && stepIdx >= 0) { const el = dr.find(current.steps[stepIdx].loc); if (el) dr.pointTo(el, false) } })

  // ------------------------------------------------------------ answer panel and playback
  function select(id, play) {
    const t = byId[id]
    if (!t) return
    current = t
    for (const it of items) it.btn.setAttribute('aria-pressed', String(it.t === t))
    history.replaceState(null, '', `#task=${id}`)
    drawAnswer(t)
    showDrawing(root.querySelector('.wi-frame'), root.querySelector('.wi-stage'), reduce.matches)
    if (reduce.matches || !play) showAll(t)
    else start(0)
  }

  function drawAnswer(t) {
    const steps = h('ol', { class: 'wi-steps' }, ...t.steps.map((s, i) =>
      h('li', { 'data-i': i }, h('span', { class: 'wi-steps__n', 'aria-hidden': 'true' }, String(i + 1).padStart(2, '0')), s.label)))
    const needs = t.needs.length ? h('ul', { class: 'wi-needs' }, ...t.needs.map(n => h('li', {}, n.text,
      n.task && n.task !== t.id ? h('button', { type: 'button', class: 'wi-link', onclick: () => select(n.task, true) }, 'Show me that first') : null))) : null
    const ctl = (lbl, fn, extra = {}) => h('button', { type: 'button', class: 'vc-btn vc-btn--ghost vc-btn--sm', onclick: fn, ...extra }, lbl)
    const ask = `Where is "${t.task.toLowerCase()}"? Point at it in my dashboard.`
    const copy = h('button', { type: 'button', class: 'vc-btn vc-btn--ghost vc-btn--sm', onclick: async e => {
      const b = e.currentTarget
      try { await navigator.clipboard.writeText(ask); b.textContent = 'Copied' } catch { b.textContent = 'Copy failed' }
    } }, 'Copy')
    $answer.replaceChildren(...[
      h('p', { class: 'wi-answer__meta' }, h('span', { class: 'vc-label' }, t.group), h('span', { class: 'wi-why' }, t.why)),
      h('h3', { class: 'wi-answer__task' }, t.task),
      steps,
      needs,
      t.note ? h('p', { class: 'wi-note' }, t.note) : null,
      t.detail ? h('p', { class: 'wi-detail' }, t.detail) : null,
      t.see ? h('p', { class: 'wi-see' }, h('a', { href: `${base}${t.see.slug}.html` }, `Read: ${t.see.title}`)) : null,
      h('div', { class: 'wi-controls' },
        ctl('Pause', togglePlay, { 'data-play': true }),
        ctl('← Back', () => step(-1), { 'aria-label': 'Previous step' }),
        ctl('Next →', () => step(1), { 'aria-label': 'Next step' }),
        ctl('Replay', () => start(0))),
      h('div', { class: 'wi-ask' }, h('span', { class: 'wi-ask__label' }, 'Or ask your agent to point at it in your own dashboard:'),
        h('code', {}, ask), copy),
      h('p', { class: 'vc-sr', 'aria-live': 'polite', id: 'wi-live' })].filter(Boolean))
  }

  function setStepUI(i, all = false) {
    for (const li of $answer.querySelectorAll('.wi-steps li')) {
      const n = Number(li.dataset.i)
      li.classList.toggle('is-done', all ? true : n < i)
      li.classList.toggle('is-now', !all && n === i)
    }
    const live = $answer.querySelector('#wi-live')
    if (live && current && !all) live.textContent = `Step ${i + 1} of ${current.steps.length}: ${current.steps[i].label}`
    const btn = $answer.querySelector('[data-play]')
    if (btn) btn.textContent = playing ? 'Pause' : 'Play'
  }

  async function showStep(i, animate) {
    stepIdx = i
    draw(current, i)
    const el = dr.find(current.steps[i].loc)
    mark(current, i)
    setStepUI(i)
    if (!el) return
    dr.pointTo(el, animate)
    if (animate) { await wait(MOVE_MS); dr.click() }
  }

  async function start(from) {
    const mine = ++run
    playing = true
    for (let i = from; i < current.steps.length; i++) {
      await showStep(i, true)
      if (mine !== run) return
      if (i < current.steps.length - 1) { await wait(PAUSE_MS); if (mine !== run) return }
    }
    playing = false
    setStepUI(stepIdx)
  }

  function showAll(t) {
    run++; playing = false
    stepIdx = t.steps.length - 1
    draw(t, stepIdx)
    mark(t, stepIdx)
    dr.hidePointer()
    setStepUI(stepIdx, true)
    dr.focusOn(dr.find(t.steps[stepIdx].loc), false)
  }

  function togglePlay() {
    if (!current) return
    if (playing) { run++; playing = false; setStepUI(stepIdx) }
    else if (reduce.matches) step(1)
    else start(stepIdx >= current.steps.length - 1 ? 0 : stepIdx + 1)
  }
  function step(d) {
    if (!current) return
    run++; playing = false
    const i = Math.max(0, Math.min(current.steps.length - 1, stepIdx + d))
    showStep(i, !reduce.matches)
  }

  // ------------------------------------------------------------ links: #task=<id>
  function fromHash() {
    const m = location.hash.match(/^#task=([\w-]+)$/)
    if (m && byId[m[1]]) select(m[1], true)   // select brings the drawing on screen
  }
  window.addEventListener('hashchange', () => fromHash())

  dr.render(HOME)
  dr.fit()
  fromHash()
}
