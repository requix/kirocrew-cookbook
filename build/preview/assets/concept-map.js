// "How the pieces fit": a diagram that builds up as you read the numbered steps beside it.
// The step text is the page's own "### N." sections (moved into the left column here), so the page
// reads the same without JavaScript. Boxes are real buttons: clicking one jumps to the step that adds it.

const SVG = 'http://www.w3.org/2000/svg'
const root = document.querySelector('[data-concept-map]')
if (root) init(root)

function init(root) {
  const data = JSON.parse(root.querySelector('[data-cm-data]').textContent)
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)')
  let steps = root.nextElementSibling
  while (steps && (steps.tagName === 'LINK' || steps.tagName === 'SCRIPT')) steps = steps.nextElementSibling
  if (!steps?.classList.contains('vc-steps-group')) return   // no numbered steps after the widget: leave the page as written
  root.querySelector('[data-cm-text]').append(steps)
  const sections = [...steps.querySelectorAll('.vc-step')]
  const titles = sections.map(s => {
    const head = s.querySelector('h3').cloneNode(true)
    head.querySelectorAll('.vc-step-num, .vc-sr').forEach(x => x.remove())
    return head.textContent.trim()
  })

  const el = (tag, attrs = {}, ...kids) => {
    const n = document.createElement(tag)
    for (const [k, v] of Object.entries(attrs)) {
      if (v == null || v === false) continue
      if (k === 'class') n.className = v
      else if (k.startsWith('on')) n.addEventListener(k.slice(2), v)
      else n.setAttribute(k, v === true ? '' : v)
    }
    n.append(...kids.filter(k => k != null))
    return n
  }
  const svgEl = (tag, attrs = {}) => {
    const n = document.createElementNS(SVG, tag)
    for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v)
    return n
  }

  // ------------------------------------------------------------ the diagram
  const $frame = root.querySelector('.cm-frame')
  const $canvas = root.querySelector('.cm-canvas')
  $canvas.style.width = `${data.w}px`; $canvas.style.height = `${data.h}px`
  const byId = Object.fromEntries(data.nodes.map(n => [n.id, n]))

  const c = data.container
  const [cx, cy, cw, ch] = c.box
  const $container = el('div', { class: 'cm-container', style: `left:${cx}px;top:${cy}px;width:${cw}px;height:${ch}px` })
  const $containerLabel = el('div', { class: 'cm-container__label', style: `left:${cx}px;top:${cy - 24}px` },
    el('span', { class: 'cm-badge' }, String(c.step)), el('b', {}, c.name), el('span', {}, ` · ${c.sub}`))

  const svg = svgEl('svg', { class: 'cm-links', viewBox: `0 0 ${data.w} ${data.h}`, width: data.w, height: data.h, 'aria-hidden': 'true' })
  const defs = svgEl('defs')
  for (const [id, cls] of [['cm-arrow', 'cm-arrowhead'], ['cm-arrow-now', 'cm-arrowhead is-now']]) {
    const m = svgEl('marker', { id, viewBox: '0 0 8 8', refX: '7', refY: '4', markerWidth: '7', markerHeight: '7', orient: 'auto-start-reverse' })
    m.append(svgEl('path', { d: 'M0,0 L8,4 L0,8 z', class: cls }))
    defs.append(m)
  }
  svg.append(defs)

  const centre = n => ({ x: n.x + n.w / 2, y: n.y + n.h / 2 })
  // Where the line from a box's centre towards a point leaves the box.
  function clip(n, toward) {
    const p = centre(n), dx = toward.x - p.x, dy = toward.y - p.y
    const tx = dx ? (n.w / 2 + 4) / Math.abs(dx) : Infinity, ty = dy ? (n.h / 2 + 4) / Math.abs(dy) : Infinity
    const t = Math.min(tx, ty)
    return { x: p.x + dx * t, y: p.y + dy * t }
  }
  const links = data.links.map(l => {
    const a = byId[l.from], b = byId[l.to]
    const p1 = clip(a, centre(b)), p2 = clip(b, centre(a))
    const line = svgEl('line', { x1: p1.x, y1: p1.y, x2: p2.x, y2: p2.y, class: 'cm-link' })
    svg.append(line)
    const label = el('span', { class: 'cm-link__label', style: `left:${(p1.x + p2.x) / 2}px;top:${(p1.y + p2.y) / 2}px` }, l.label)
    return { ...l, line, label, len: Math.hypot(p2.x - p1.x, p2.y - p1.y) }
  })

  const nodes = data.nodes.map(n => {
    const b = el('button', { type: 'button', class: `cm-node${n.w < 120 ? ' cm-node--small' : ''}`,
      style: `left:${n.x}px;top:${n.y}px;width:${n.w}px;height:${n.h}px`,
      'aria-label': `${n.name}${n.sub ? `: ${n.sub}` : ''}. Step ${n.step}: ${titles[n.step - 1]}`,
      onclick: () => goTo(n.step, true) },
      el('span', { class: 'cm-badge', 'aria-hidden': 'true' }, String(n.step)),
      el('b', {}, n.name), n.sub ? el('span', { class: 'cm-node__sub' }, n.sub) : null)
    return { ...n, btn: b }
  })
  $canvas.append($container, $containerLabel, svg, ...links.map(l => l.label), ...nodes.map(n => n.btn))

  // ------------------------------------------------------------ numbered chips
  const $chips = root.querySelector('.cm-chips')
  const chips = titles.map((t, i) => {
    const b = el('button', { type: 'button', class: 'cm-chip', onclick: () => goTo(i + 1, true) },
      el('span', { class: 'cm-chip__n', 'aria-hidden': 'true' }, String(i + 1).padStart(2, '0')), el('span', { class: 'cm-chip__t' }, t))
    $chips.append(el('li', {}, b))
    return b
  })

  // ------------------------------------------------------------ state
  let current = 1, all = false
  const $all = root.querySelector('[data-cm-all]')
  function paint() {
    const k = all ? Infinity : current
    const marks = all ? [] : data.steps[current - 1].mark
    const cls = s => (s < k ? 'is-shown' : s === k ? 'is-now' : 'is-ghost')
    $container.className = `cm-container ${cls(c.step)}`
    $containerLabel.className = `cm-container__label ${cls(c.step)}`
    for (const n of nodes) {
      n.btn.className = `cm-node ${n.w < 120 ? 'cm-node--small ' : ''}${cls(n.step)}${marks.includes(n.id) ? ' is-marked' : ''}`
    }
    for (const l of links) {
      const state = cls(l.step)
      l.line.setAttribute('class', `cm-link ${state}`)
      l.line.setAttribute('marker-end', state === 'is-ghost' ? '' : state === 'is-now' ? 'url(#cm-arrow-now)' : 'url(#cm-arrow)')
      l.label.className = `cm-link__label ${state}`
      if (state === 'is-now' && !reduce.matches) {
        l.line.style.strokeDasharray = `${l.len}`
        l.line.style.strokeDashoffset = `${l.len}`
        requestAnimationFrame(() => requestAnimationFrame(() => { l.line.style.strokeDashoffset = '0' }))
      } else { l.line.style.strokeDasharray = ''; l.line.style.strokeDashoffset = '' }
    }
    chips.forEach((b, i) => {
      b.classList.toggle('is-now', !all && i + 1 === current)
      b.classList.toggle('is-done', all || i + 1 < current)
      if (!all && i + 1 === current) b.setAttribute('aria-current', 'step'); else b.removeAttribute('aria-current')
    })
    sections.forEach((s, i) => s.classList.toggle('cm-current', !all && i + 1 === current))
    $all.setAttribute('aria-pressed', String(all))
    $all.textContent = all ? 'Back to the steps' : 'Show the whole picture'
  }
  function set(k) { if (k !== current || all) { current = k; all = false; paint(); fit() } }

  // The current step is the last one whose top has passed the reading line. On wide screens the line
  // sits a third of the way down. On narrow screens the diagram sticks to the top, so the line sits a
  // little below the diagram: a step hidden behind the diagram is never the current one.
  const $side = root.querySelector('.cm-side')
  const navH = () => parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--vc-nav-height')) || 48
  const wide = window.matchMedia('(min-width: 1056px)')
  function readingLine(stuck) {
    if (wide.matches) return innerHeight * 0.35
    const bottom = stuck ? navH() + $side.offsetHeight : $side.getBoundingClientRect().bottom
    return bottom + (innerHeight - bottom) * 0.25
  }
  function onScroll() {
    if (all) return
    const line = readingLine(false)
    let k = 1
    sections.forEach((s, i) => { if (s.getBoundingClientRect().top <= line) k = i + 1 })
    set(k)
  }
  let ticking = false
  window.addEventListener('scroll', () => {
    if (ticking) return
    ticking = true
    requestAnimationFrame(() => { ticking = false; onScroll() })
  }, { passive: true })

  function goTo(k, scroll) {
    set(k)
    if (!scroll) return
    // Put the step's top just above the reading line, so it is the current step once the scroll ends.
    const top = window.scrollY + sections[k - 1].getBoundingClientRect().top - (readingLine(true) - 24)
    window.scrollTo({ top, behavior: reduce.matches ? 'auto' : 'smooth' })
  }
  $all.addEventListener('click', () => { all = !all; paint(); fit() })

  // ------------------------------------------------------------ scale to the column
  // Wide enough: the whole diagram fits. On a phone the whole diagram would shrink its text to about
  // 5px, so the frame works like a camera instead: it zooms to the boxes the current step adds, as large
  // as fits (never past MAX), and moves when the step changes. "Show the whole picture" zooms out to fit.
  const READABLE = 0.75, MAX = 0.9, PAD = 16
  let zoom = false
  function fit() {
    const fitS = Math.min(1, $frame.clientWidth / data.w)
    zoom = fitS < READABLE && !all
    root.classList.toggle('cm--zoom', zoom)
    // A fixed frame height on phones, so the sticky diagram never changes size while you read.
    $frame.style.height = `${Math.round(zoom ? Math.min(data.h * fitS * 1.6, innerHeight * 0.38) : data.h * fitS)}px`
    if (!zoom) { $canvas.style.transform = `scale(${fitS})`; return }
    const b = focusBox(), fw = $frame.clientWidth, fh = $frame.clientHeight
    const s = Math.max(fitS, Math.min(MAX, fw / (b.w + 2 * PAD), fh / (b.h + 2 * PAD)))
    const vw = fw / s, vh = fh / s
    const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v))
    const x = clamp(b.x + b.w / 2 - vw / 2, 0, Math.max(0, data.w - vw)), y = clamp(b.y + b.h / 2 - vh / 2, -24, Math.max(0, data.h - vh))
    $canvas.style.transform = `scale(${s}) translate(${-x}px, ${-y}px)`
  }
  // The boxes the current step adds, plus both ends of the arrows it adds (and the gateway, on its step).
  function focusBox() {
    const ids = new Set(nodes.filter(n => n.step === current).map(n => n.id))
    for (const l of links) if (l.step === current) { ids.add(l.from); ids.add(l.to) }
    const rs = nodes.filter(n => ids.has(n.id)).map(n => ({ x: n.x, y: n.y, w: n.w, h: n.h }))
    // On the gateway's own step, frame its label (the outline carries on past the frame's edge).
    if (c.step === current) rs.push({ x: cx, y: cy - 24, w: 260, h: 24 })
    if (!rs.length) rs.push({ x: cx, y: cy - 24, w: cw, h: ch + 24 })
    const x = Math.min(...rs.map(r => r.x)), y = Math.min(...rs.map(r => r.y))
    return { x, y, w: Math.max(...rs.map(r => r.x + r.w)) - x, h: Math.max(...rs.map(r => r.y + r.h)) - y }
  }
  new ResizeObserver(fit).observe($frame)
  root.classList.add('is-ready')
  fit()
  paint()
  onScroll()
}
