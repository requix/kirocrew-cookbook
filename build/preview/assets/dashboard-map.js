// Dashboard map — pick a part of the KiroCrew dashboard from the list, and the drawing shows where it is.
// The drawing is a picture, not a simulator: it takes no clicks and no hovers. Selection happens only
// in the list beside it (or the numbered tour), and the drawing highlights the selected part.
// Three screen buttons show the other main pages. The drawing (kc-drawing.js) is aria-hidden;
// the list is the keyboard and screen-reader way in.
import { createDrawing, h, HOME, showDrawing } from './kc-drawing.js'

const TOUR_MS = 3800
const SCREENS = [['page.chat', 'Sessions'], ['page.capabilities', 'Customize'], ['page.settings', 'Settings']]

const root = document.querySelector('[data-dash-map]')
if (root) init(root)

function init(root) {
  const data = JSON.parse(root.querySelector('#dm-data').textContent)
  const zones = Object.fromEntries(data.groups.flatMap(g => g.zones.map(z => [z.at, { ...z, group: g.group }])))
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)')
  const base = new URL('../', import.meta.url).href
  const canvas = root.querySelector('#dm-canvas')
  const $list = root.querySelector('#dm-list')
  const $info = root.querySelector('#dm-info')
  const $tourBtn = root.querySelector('#dm-tour')
  const $screens = root.querySelector('#dm-screens')
  const dr = createDrawing({ canvas, frame: root.querySelector('.wi-frame'), D: data.drawing })

  let state = { ...HOME }, selected = null
  let tour = -1, touring = false, run = 0
  const wait = ms => new Promise(r => setTimeout(r, ms))

  // ------------------------------------------------------------ list and screen buttons
  const buttons = {}
  for (const g of data.groups) {
    $list.append(h('p', { class: 'wi-group' }, g.group))
    for (const z of g.zones) {
      const b = h('button', { type: 'button', class: 'wi-item', 'aria-pressed': 'false', onclick: () => { stopTour(); select(z.at, { pan: true }) } },
        h('span', { class: 'wi-item__task' }, z.name),
        z.text ? h('span', { class: 'wi-item__path' }, z.text) : null)
      buttons[z.at] = b
      $list.append(b)
    }
  }
  const screenBtns = SCREENS.map(([loc, name]) => h('button', { type: 'button', class: 'dm-screen', 'aria-pressed': 'false',
    onclick: () => { stopTour(); state = { ...HOME, screen: loc }; selected = null; markList(); redraw(); hint(name) } }, name))
  $screens.append(h('span', { class: 'dm-screens__label' }, 'Show:'), ...screenBtns,
    h('span', { class: 'dm-screens__hint' }, 'Pick a part from the list. The drawing shows where it is.'))

  // ------------------------------------------------------------ drawing
  function redraw() {
    dr.render(state, { want: selected ? [selected] : [] })
    paint()
    SCREENS.forEach(([loc], i) => screenBtns[i].setAttribute('aria-pressed', String(state.screen === loc)))
  }
  function paint() {
    for (const el of canvas.querySelectorAll('.is-hot, .is-visited')) el.classList.remove('is-hot', 'is-visited')
    for (const b of canvas.querySelectorAll('.d-layer .d-badge')) b.remove()
    if (tour >= 0) {
      // Number every tour stop on this screen; the current one is filled.
      data.tour.forEach((at, i) => {
        const el = dr.find(at)
        if (!el) return
        if (i !== tour) el.classList.add('is-visited')
        dr.badge(el, i + 1, i === tour)
      })
    }
    if (selected) dr.find(selected)?.classList.add('is-hot')
  }

  // Bring the drawing to the page and state a zone needs, then highlight it.
  function reveal(z) {
    let next = { ...(z.screen && z.screen !== state.screen ? { ...HOME, screen: z.screen } : state), menu: null, ...z.state }
    if (z.at === 'chat.side-panel-open') next.panel = false
    if (!z.state?.panel && z.screen === 'page.chat' && z.at !== 'x.side-panel') next.panel = next.panel && state.panel
    state = next
    selected = z.at
    redraw()
    if (!dr.find(z.at)) { state = { ...HOME, screen: z.screen || 'page.chat', ...z.state }; redraw() }
  }

  function markList() {
    for (const [k, b] of Object.entries(buttons)) b.setAttribute('aria-pressed', String(k === selected))
  }

  function select(at, { pan = false, point = false } = {}) {
    const z = zones[at]
    if (!z) return
    reveal(z)
    markList()
    if (pan) buttons[at].scrollIntoView({ block: 'nearest' })
    const el = dr.find(at)
    if (el) { if (point) dr.pointTo(el, !reduce.matches); else dr.focusOn(el, !reduce.matches) }
    info(z)
    history.replaceState(null, '', `#zone=${at}`)
    if (pan) showDrawing(root.querySelector('.wi-frame'), root.querySelector('.wi-stage'), reduce.matches)
  }

  function hint(screenName) {
    $info.replaceChildren(h('p', { class: 'wi-hint' }, `${screenName}: pick a part from the list. The drawing shows where it is.`))
  }

  function info(z) {
    const links = h('p', { class: 'wi-see' },
      z.task ? h('a', { href: `${base}find/where-is.html#task=${z.task}` }, 'Show me how to use it') : null,
      z.task && z.see ? ' · ' : null,
      z.see ? h('a', { href: `${base}${z.see.slug}.html${z.see.hash ? `#${z.see.hash}` : ''}` }, `Read: ${z.see.title}`) : null)
    const parts = [
      h('p', { class: 'wi-answer__meta' }, h('span', { class: 'vc-label' }, z.group)),
      h('h3', { class: 'wi-answer__task' }, z.name),
      z.text ? h('p', { class: 'dm-text' }, z.text) : null,
      z.path ? h('p', { class: 'wi-detail' }, `Where: ${z.path}`) : null,
      z.task || z.see ? links : null,
    ]
    root.classList.remove('is-empty')   // the info box appears, and from now on keeps one height
    $info.replaceChildren(...parts.filter(Boolean))
  }

  // ------------------------------------------------------------ numbered tour
  const $stops = h('ol', { class: 'wi-steps dm-stops', hidden: true }, ...data.tour.map((at, i) =>
    h('li', { 'data-i': i }, h('button', { type: 'button', class: 'dm-stop', onclick: () => { run++; touring = false; showStop(i) } },
      h('span', { class: 'wi-steps__n', 'aria-hidden': 'true' }, String(i + 1).padStart(2, '0')), zones[at].name))))
  const ctl = (lbl, fn, extra = {}) => h('button', { type: 'button', class: 'vc-btn vc-btn--ghost vc-btn--sm', onclick: fn, ...extra }, lbl)
  const $play = ctl('Pause', () => (touring ? pauseTour() : playTour(tour + 1 >= data.tour.length ? 0 : tour + 1)))
  const $tourCtl = h('div', { class: 'wi-controls dm-tourctl', hidden: true },
    $play,
    ctl('← Back', () => stepTour(-1), { 'aria-label': 'Previous stop' }),
    ctl('Next →', () => stepTour(1), { 'aria-label': 'Next stop' }),
    ctl('End tour', stopTour))
  root.querySelector('.dm-tourbox').append($stops, $tourCtl)

  function syncTourUI() {
    const on = tour >= 0
    $stops.hidden = !on; $tourCtl.hidden = !on
    $play.textContent = touring ? 'Pause' : 'Play'
    for (const li of $stops.children) {
      const n = Number(li.dataset.i)
      li.classList.toggle('is-done', on && n < tour)
      li.classList.toggle('is-now', on && n === tour)
    }
  }
  function showStop(i) {
    tour = i
    select(data.tour[i], { point: true })
    paint()
    syncTourUI()
    const live = root.querySelector('#dm-live')
    if (live) live.textContent = `Stop ${i + 1} of ${data.tour.length}: ${zones[data.tour[i]].name}`
  }
  async function playTour(from = 0) {
    const mine = ++run
    touring = true
    $tourBtn.textContent = 'Restart the tour'
    for (let i = from; i < data.tour.length; i++) {
      showStop(i)
      await wait(TOUR_MS)
      if (mine !== run) return
    }
    touring = false
    syncTourUI()
  }
  function pauseTour() { run++; touring = false; syncTourUI() }
  function stepTour(d) { run++; touring = false; showStop(Math.max(0, Math.min(data.tour.length - 1, tour + d))) }
  function stopTour() {
    if (tour < 0 && !touring) return
    run++; touring = false; tour = -1
    dr.hidePointer()
    $tourBtn.textContent = 'Take the 1-minute tour'
    paint()
    syncTourUI()
  }
  $tourBtn.addEventListener('click', () => {
    if (reduce.matches) { run++; touring = false; showStop(0) }   // no autoplay: step with Next
    else playTour(0)
    showDrawing(root.querySelector('.wi-frame'), root.querySelector('.wi-stage'), reduce.matches)
  })
  root.append(h('p', { class: 'vc-sr', 'aria-live': 'polite', id: 'dm-live' }))

  // ------------------------------------------------------------ links: #zone=<id>, #tour
  // Both paths bring the drawing on screen themselves.
  function fromHash() {
    const m = location.hash.match(/^#zone=([\w.:-]+)$/)
    if (m && zones[m[1]]) { stopTour(); select(m[1], { pan: true }) }
    else if (location.hash === '#tour') $tourBtn.click()
  }
  window.addEventListener('hashchange', () => fromHash())
  dr.onFit(() => { if (selected && tour >= 0) { const el = dr.find(selected); if (el) dr.pointTo(el, false) } })

  redraw()
  dr.fit()
  fromHash()
}
