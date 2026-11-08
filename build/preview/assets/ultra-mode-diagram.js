// Ultra Mode conductor/worker diagram.
// Shows how requests flow from you → conductor → workers → back.
// Steps can be navigated manually or auto-played.

const SVG = 'http://www.w3.org/2000/svg'
const root = document.querySelector('[data-ultra-mode]')
if (root) init(root)

function init(root) {
  const data = JSON.parse(root.querySelector('[data-um-data]').textContent)
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)')

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
  const $frame = root.querySelector('.um-frame')
  const $canvas = root.querySelector('.um-canvas')
  $canvas.style.width = `${data.w}px`
  $canvas.style.height = `${data.h}px`
  const byId = Object.fromEntries(data.nodes.map(n => [n.id, n]))

  // SVG for arrows
  const svg = svgEl('svg', {
    class: 'um-links',
    viewBox: `0 0 ${data.w} ${data.h}`,
    width: data.w,
    height: data.h,
    'aria-hidden': 'true'
  })
  const defs = svgEl('defs')
  for (const [id, cls] of [['um-arrow', 'um-arrowhead'], ['um-arrow-now', 'um-arrowhead is-now']]) {
    const m = svgEl('marker', {
      id,
      viewBox: '0 0 8 8',
      refX: '7',
      refY: '4',
      markerWidth: '7',
      markerHeight: '7',
      orient: 'auto-start-reverse'
    })
    m.append(svgEl('path', { d: 'M0,0 L8,4 L0,8 z', class: cls }))
    defs.append(m)
  }
  svg.append(defs)

  const centre = n => ({ x: n.x + n.w / 2, y: n.y + n.h / 2 })

  function clip(n, toward) {
    const p = centre(n), dx = toward.x - p.x, dy = toward.y - p.y
    const tx = dx ? (n.w / 2 + 4) / Math.abs(dx) : Infinity
    const ty = dy ? (n.h / 2 + 4) / Math.abs(dy) : Infinity
    const t = Math.min(tx, ty)
    return { x: p.x + dx * t, y: p.y + dy * t }
  }

  const links = data.links.map(l => {
    const a = byId[l.from], b = byId[l.to]
    const p1 = clip(a, centre(b)), p2 = clip(b, centre(a))
    const line = svgEl('line', {
      x1: p1.x, y1: p1.y, x2: p2.x, y2: p2.y,
      class: 'um-link'
    })
    svg.append(line)
    const label = l.label
      ? el('span', {
          class: 'um-link__label',
          style: `left:${(p1.x + p2.x) / 2}px;top:${(p1.y + p2.y) / 2}px`
        }, l.label)
      : null
    return { ...l, line, label, len: Math.hypot(p2.x - p1.x, p2.y - p1.y) }
  })

  const nodes = data.nodes.map(n => {
    const styleClass = n.style ? ` um-node--${n.style}` : ''
    const small = n.w < 100 || n.h < 40
    const box = el('div', {
      class: `um-node${styleClass}${small ? ' um-node--small' : ''}`,
      style: `left:${n.x}px;top:${n.y}px;width:${n.w}px;height:${n.h}px`,
      'aria-label': `${n.name}${n.sub ? `: ${n.sub}` : ''}`
    },
      el('b', {}, n.name),
      n.sub ? el('span', { class: 'um-node__sub' }, n.sub) : null
    )
    return { ...n, box }
  })

  $canvas.append(svg, ...links.filter(l => l.label).map(l => l.label), ...nodes.map(n => n.box))

  // ------------------------------------------------------------ step controls
  const $steps = [...root.querySelectorAll('.um-step')]
  const $prev = root.querySelector('.um-prev')
  const $next = root.querySelector('.um-next')
  const $play = root.querySelector('.um-play')

  let current = 0  // 0 = nothing shown, 1..N = step shown
  let playing = false
  let playTimer = null

  function paint() {
    const k = current

    for (const n of nodes) {
      const shown = n.step <= k
      n.box.classList.toggle('is-shown', shown && n.step < k)
      n.box.classList.toggle('is-now', n.step === k)
      n.box.classList.toggle('is-ghost', !shown)
    }

    for (const l of links) {
      const shown = l.step <= k
      const state = !shown ? 'is-ghost' : l.step === k ? 'is-now' : 'is-shown'
      l.line.setAttribute('class', `um-link ${state}`)
      l.line.setAttribute('marker-end',
        state === 'is-ghost' ? '' : state === 'is-now' ? 'url(#um-arrow-now)' : 'url(#um-arrow)')
      if (l.label) l.label.className = `um-link__label ${state}`

      // Animate the arrow drawing
      if (state === 'is-now' && !reduce.matches) {
        l.line.style.strokeDasharray = `${l.len}`
        l.line.style.strokeDashoffset = `${l.len}`
        requestAnimationFrame(() => requestAnimationFrame(() => {
          l.line.style.strokeDashoffset = '0'
        }))
      } else {
        l.line.style.strokeDasharray = ''
        l.line.style.strokeDashoffset = ''
      }
    }

    $steps.forEach((s, i) => {
      s.classList.toggle('is-current', i + 1 === k)
      s.classList.toggle('is-done', i + 1 < k)
    })

    $prev.disabled = k <= 1
    $next.disabled = k >= data.steps.length
  }

  function goTo(step) {
    current = Math.max(0, Math.min(data.steps.length, step))
    paint()
  }

  function nextStep() {
    if (current < data.steps.length) {
      goTo(current + 1)
    } else if (playing) {
      stopPlay()
    }
  }

  function prevStep() {
    if (current > 1) goTo(current - 1)
  }

  function startPlay() {
    playing = true
    $play.dataset.playing = 'true'
    $play.textContent = '⏸ Pause'
    if (current >= data.steps.length) goTo(0)
    playTimer = setInterval(() => {
      if (current < data.steps.length) {
        nextStep()
      } else {
        stopPlay()
      }
    }, 2000)
    nextStep()  // Start immediately
  }

  function stopPlay() {
    playing = false
    $play.dataset.playing = 'false'
    $play.textContent = '▶ Play'
    if (playTimer) {
      clearInterval(playTimer)
      playTimer = null
    }
  }

  $prev.addEventListener('click', () => { stopPlay(); prevStep() })
  $next.addEventListener('click', () => { stopPlay(); nextStep() })
  $play.addEventListener('click', () => playing ? stopPlay() : startPlay())
  $steps.forEach((s, i) => {
    s.querySelector('button').addEventListener('click', () => { stopPlay(); goTo(i + 1) })
  })

  // Keyboard navigation
  root.addEventListener('keydown', e => {
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') { stopPlay(); nextStep(); e.preventDefault() }
    if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') { stopPlay(); prevStep(); e.preventDefault() }
    if (e.key === ' ') { playing ? stopPlay() : startPlay(); e.preventDefault() }
  })

  // ------------------------------------------------------------ scale to fit
  function fit() {
    const fitS = Math.min(1, $frame.clientWidth / data.w, 320 / data.h)
    $canvas.style.transform = `scale(${fitS})`
    $frame.style.height = `${Math.round(data.h * fitS)}px`
  }
  new ResizeObserver(fit).observe($frame)

  // Initialize
  root.classList.add('is-ready')
  fit()
  goTo(1)  // Show first step on load
}
