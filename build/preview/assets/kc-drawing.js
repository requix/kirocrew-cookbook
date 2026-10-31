// The drawn KiroCrew dashboard, shared by the "Where is…?" finder and the Dashboard map.
// A simplified copy of the real layout (from screenshots in the KiroCrew repo), labelled from
// KiroCrew's own UI index. Every drawn control carries data-loc: a UI-index id, or an x.* id for
// parts the index does not list. Pages drive it with render(state, opts); it never fetches anything.

export const W = 960, H = 580
const MIN_SCALE = 0.62   // below this the frame zooms in and follows the pointer instead

// 16px line icons, drawn in currentColor.
const ICON = {
  chat: '<path d="M2.5 3.5h11v7.5h-6.5l-3 2.5v-2.5h-1.5z"/>',
  users: '<circle cx="6" cy="6" r="2.2"/><path d="M2.5 13a3.5 3.5 0 0 1 7 0M10.5 4a2 2 0 0 1 0 4M13.5 13a3 3 0 0 0-2-2.8"/>',
  calendar: '<rect x="2.5" y="3.5" width="11" height="10" rx="1.5"/><path d="M2.5 6.5h11M5.5 2v3M10.5 2v3"/>',
  artifacts: '<path d="M8 1.8l2.2 2.2L8 6.2 5.8 4zM4 5.8L6.2 8 4 10.2 1.8 8zM12 5.8L14.2 8 12 10.2 9.8 8zM8 9.8l2.2 2.2L8 14.2 5.8 12z"/>',
  compass: '<circle cx="8" cy="8" r="5.5"/><path d="M10.2 5.8L9 9 5.8 10.2 7 7z"/>',
  grid: '<rect x="2.5" y="2.5" width="4.5" height="4.5" rx="1"/><rect x="9" y="2.5" width="4.5" height="4.5" rx="1"/><rect x="2.5" y="9" width="4.5" height="4.5" rx="1"/><rect x="9" y="9" width="4.5" height="4.5" rx="1"/>',
  rocket: '<path d="M9.5 2.5c2.2 0 4 1.8 4 4L8.2 11.8 4.2 7.8zM4.2 7.8 2.5 8.5l1 2.5M8.2 11.8l-.7 1.7-2.5-1"/>',
  terminal: '<rect x="2" y="3" width="12" height="10" rx="1.5"/><path d="M4.5 6l2 2-2 2M8.5 10h3"/>',
  ghost: '<path d="M4 13.5V7a4 4 0 0 1 8 0v6.5l-2-1.2-2 1.2-2-1.2z"/>',
  gear: '<circle cx="8" cy="8" r="2.2"/><path d="M8 1.8v2M8 12.2v2M1.8 8h2M12.2 8h2M3.6 3.6l1.4 1.4M11 11l1.4 1.4M3.6 12.4 5 11M11 5l1.4-1.4"/>',
  bell: '<path d="M4 11V7.5a4 4 0 0 1 8 0V11l1 1.5H3zM6.5 14h3"/>',
  back: '<path d="M10 3.5 5.5 8 10 12.5"/>', fwd: '<path d="M6 3.5 10.5 8 6 12.5"/>',
  shot: '<path d="M2.5 5.5v-3h3M10.5 2.5h3v3M13.5 10.5v3h-3M5.5 13.5h-3v-3"/>',
  bulb: '<path d="M6 12.5h4M6.5 14.5h3M5 9.5a4 4 0 1 1 6 0c-.7.7-1 1.4-1 2H6c0-.6-.3-1.3-1-2z"/>',
  collapse: '<path d="M3 2.5v11M13 8H6M9 5 6 8l3 3"/>',
  panel: '<rect x="2.5" y="2.5" width="11" height="11" rx="1.5"/><path d="M6 2.5v11"/>',
  panelR: '<rect x="2.5" y="2.5" width="11" height="11" rx="1.5"/><path d="M10 2.5v11"/>',
  dots: '<circle cx="8" cy="3.5" r=".8"/><circle cx="8" cy="8" r=".8"/><circle cx="8" cy="12.5" r=".8"/>',
  hdots: '<circle cx="3.5" cy="8" r=".8"/><circle cx="8" cy="8" r=".8"/><circle cx="12.5" cy="8" r=".8"/>',
  plus: '<path d="M8 3v10M3 8h10"/>', x: '<path d="M4 4l8 8M12 4l-8 8"/>',
  fork: '<circle cx="4.5" cy="3.5" r="1.5"/><circle cx="11.5" cy="3.5" r="1.5"/><circle cx="8" cy="12.5" r="1.5"/><path d="M4.5 5c0 3 3.5 2.5 3.5 6M11.5 5c0 3-3.5 2.5-3.5 6"/>',
  search: '<circle cx="7" cy="7" r="4.5"/><path d="m10.5 10.5 3 3"/>',
  filter: '<path d="M2.5 4h11M4.5 8h7M6.5 12h3"/>',
  down: '<path d="M4 6l4 4 4-4"/>', right: '<path d="M6 4l4 4-4 4"/>',
  target: '<circle cx="8" cy="8" r="5.5"/><circle cx="8" cy="8" r="2.5"/>',
  shield: '<path d="M8 2l5 2v4c0 3-2.3 5.2-5 6-2.7-.8-5-3-5-6V4z"/><path d="M5.8 8l1.6 1.6 3-3"/>',
  mic: '<rect x="6" y="2" width="4" height="7.5" rx="2"/><path d="M3.5 8a4.5 4.5 0 0 0 9 0M8 12.5V14"/>',
  sparkle: '<path d="M7 2.5l1.2 3.3 3.3 1.2-3.3 1.2L7 11.5 5.8 8.2 2.5 7l3.3-1.2zM12 10l.6 1.4 1.4.6-1.4.6L12 14l-.6-1.4L10 12l1.4-.6z"/>',
  up: '<path d="M8 12.5V3.5M4.5 7 8 3.5 11.5 7"/>',
  bot: '<rect x="3" y="5" width="10" height="8" rx="2"/><path d="M8 2.5V5M6 9h.1M10 9h.1"/>',
  folder: '<path d="M2 4.5h4.5l1.5 1.5h6v7H2z"/>',
  external: '<path d="M9 2.5h4.5V7M13.5 2.5 7.5 8.5M11.5 9.5v4h-9v-9h4"/>',
  history: '<circle cx="8" cy="8" r="5.5"/><path d="M8 5v3l2 1.5"/>',
  doc: '<path d="M4 1.5h5l3 3V14.5H4z"/><path d="M9 1.5v3h3"/>',
  summary: '<path d="M2.5 4h11M2.5 8h7M2.5 12h9"/>',
  git: '<circle cx="4.5" cy="4" r="1.5"/><circle cx="4.5" cy="12" r="1.5"/><circle cx="11.5" cy="6" r="1.5"/><path d="M4.5 5.5v5M11.5 7.5c0 2.5-4 2-6 3.5"/>',
}
const RAIL_ICON = {
  'page.chat': 'chat', 'page.members': 'users', 'page.schedule': 'calendar', 'page.artifacts': 'artifacts',
  'page.apps': 'compass', 'page.apps-library': 'grid', 'page.projects': 'rocket', 'shell.terminal': 'terminal',
  'page.capabilities': 'ghost', 'page.settings': 'gear',
}
// Settings tabs carry a colored tile in the real dashboard.
const TILE = {
  overview: 'gray', imports: 'blue', agent: 'teal', chat: 'green', display: 'indigo', voice: 'pink', notifications: 'red',
  shortcuts: 'purple', skills: 'orange', channels: 'teal', browser: 'blue', 'computer-use': 'indigo', webhooks: 'orange',
  instances: 'gray', privacy: 'blue', security: 'red', connections: 'green', secrets: 'gray', developer: 'gray',
  releases: 'purple', about: 'gray',
}
// Schedule controls that live in an open job's panel, and ones that exist only before the first job.
const JOB_ACTIONS = new Set(['schedule.run-now', 'schedule.pause', 'schedule.delete', 'schedule.cancel-run', 'schedule.secret-approve', 'schedule.edit-when'])
const EMPTY_SCHEDULE = new Set(['schedule.create-first', 'schedule.templates'])
// Clicks that open a menu in the drawing.
export const MENU_OPENERS = new Set(['composer.add-menu', 'sessions.create-menu', 'sessions.list-menu', 'sessions.row-menu',
  'chat.side-panel.add', 'composer.automation', 'x.project-pill', 'x.agent-selector'])

export const HOME = Object.freeze({ screen: 'page.chat', sidetab: null, subnav: null, ctab: null, menu: null, panel: false, job: false })

export function h(tag, attrs = {}, ...kids) {
  const el = document.createElement(tag)
  for (const [k, v] of Object.entries(attrs)) {
    if (v == null || v === false) continue
    if (k === 'class') el.className = v
    else if (k === 'loc') el.dataset.loc = v
    else if (k.startsWith('on')) el.addEventListener(k.slice(2), v)
    else el.setAttribute(k, v === true ? '' : v)
  }
  for (const kid of kids.flat()) if (kid != null && kid !== false) el.append(kid.nodeType ? kid : document.createTextNode(kid))
  return el
}

// After a pick, make sure the reader can see the drawing. On phones it sits below the list, so a pick
// would change something off screen. Best case: the whole box (answer + drawing) just under the site
// header. If that box is taller than the screen, the drawing's bottom goes to the screen's bottom instead.
export function showDrawing(frame, box, reduce) {
  const nav = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--vc-nav-height')) || 48
  const f = frame.getBoundingClientRect(), b = box.getBoundingClientRect()
  if (f.top >= nav && f.bottom <= innerHeight) return
  let dy = b.top - nav - 8
  if (f.bottom - dy > innerHeight) dy = f.bottom - innerHeight + 8
  window.scrollBy({ top: dy, behavior: reduce ? 'auto' : 'smooth' })
}

function ico(name, cls = '') {
  const s = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
  s.setAttribute('viewBox', '0 0 16 16'); s.setAttribute('class', `d-i ${cls}`); s.setAttribute('aria-hidden', 'true')
  s.innerHTML = ICON[name] || ''
  return s
}

export function createDrawing({ canvas, frame, D }) {
  let scale = 1, follow = false
  const pointer = h('div', { class: 'wi-pointer' }, h('span', { class: 'wi-pointer__ring' }))
  const arrow = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
  arrow.setAttribute('viewBox', '0 0 16 16'); arrow.setAttribute('class', 'wi-pointer__arrow')
  arrow.innerHTML = '<path d="M3 2l12 6.5-5.2 1.3L7.4 15z"/>'
  pointer.append(arrow)
  pointer.hidden = true
  const $head = h('div', { class: 'd-head' })
  const $rail = h('nav', { class: 'd-rail d-card' })
  const $main = h('div', { class: 'd-main' })
  const $layer = h('div', { class: 'd-layer' })   // menus and number badges float here
  canvas.append($head, h('div', { class: 'd-body' }, $rail, $main), $layer, pointer)
  let height = H   // fitHeight makes it taller when a page's column runs past H
  canvas.style.width = `${W}px`; canvas.style.height = `${H}px`

  const label = loc => D.labels[loc] || D.pages[loc] || tabLabel(loc) || loc
  function tabLabel(loc) {
    for (const g of [...D.customize, ...D.settings]) for (const t of g.tabs) if (t.loc === loc) return t.label
    return null
  }

  $head.append(
    h('span', { class: 'd-head__nav', loc: 'x.history-nav' }, ico('back'), ico('fwd', 'is-off')),
    h('span', { class: 'd-head__center' },
      h('span', { class: 'd-search', loc: 'shell.search' }, '⌘K — Search for anything…'),
      h('span', { class: 'd-iconbtn' }, ico('shot'))),
    h('span', { class: 'd-head__end' },
      h('span', { class: 'd-capsule', loc: 'x.status' }, h('span', { class: 'd-dot' }), h('span', { class: 'd-capsule__bar' }), h('span', { class: 'd-capsule__bar' })),
      h('span', { class: 'd-pill', loc: 'x.feedback' }, ico('bulb'), 'Request a Feature'),
      h('span', { class: 'd-iconbtn', loc: 'shell.notifications' }, ico('bell'))))

  function drawRail(mates) {
    const item = it => h('span', { class: 'd-nav', loc: it.loc }, ico(RAIL_ICON[it.loc] || 'doc'), h('span', {}, it.label))
    // The Mates page is a preview: it is only in the rail once its switch is on.
    const main = D.rail.main.filter(it => it.loc !== 'page.members' || mates)
    $rail.replaceChildren(
      h('div', { class: 'd-logo' }, h('span', { class: 'd-logo__ghost' }, ico('ghost')),
        h('span', { class: 'd-logo__word' }, 'KIRO ', h('b', {}, 'CREW')), h('span', { class: 'd-spacer' }), ico('collapse', 'd-muted')),
      ...main.map(item),
      h('span', { class: 'd-nav__label', loc: 'x.apps-group' }, 'Apps'),
      ...D.rail.apps.map(item),
      h('span', { class: 'd-spacer' }),
      ...D.rail.bottom.map(item),
      h('div', { class: 'd-rail__foot' }, 'Star us · Report issue'))
  }

  // ------------------------------------------------------------ render one state of the dashboard
  // state: { screen, sidetab, subnav, ctab, menu, panel, job }
  // opts:  { want: locs that must be drawn, empty: chat before its first message, mates: Mates preview on, next }
  function render(s, opts = {}) {
    const o = { want: [], empty: false, mates: false, next: null, ...opts }
    drawRail(o.mates || s.screen === 'page.members')
    $main.replaceChildren(...(s.screen === 'page.chat' ? chatScreen(s, o) : pageScreen(s, o.want)))
    $layer.replaceChildren()
    for (const el of $head.querySelectorAll('.is-hot, .is-visited, .is-hover')) el.classList.remove('is-hot', 'is-visited', 'is-hover')
    const railSel = $rail.querySelector(`[data-loc="${s.screen}"]`)
    if (railSel) railSel.classList.add('is-selected')
    if (s.menu) openMenu(s.menu)
    // A control this drawing does not draw on its own still gets a plain box, so the next step has a target.
    if (o.next && !find(o.next) && !o.next.startsWith('page.') && !o.next.startsWith('x.')) placeGeneric(o.next)
    fitHeight()
  }

  // Settings has more tabs than H is tall: grow the drawing until every tab shows; other screens stay at H.
  function fitHeight() {
    const was = height
    height = H; canvas.style.height = `${H}px`
    let over = 0
    for (const el of $main.querySelectorAll('.d-col [data-loc]')) {
      const r = rectIn(el)
      over = Math.max(over, r.y + r.h - (H - 18))
    }
    if (over > 0) { height = H + Math.ceil(over); canvas.style.height = `${height}px` }
    if (height !== was) fit()
  }

  function chatScreen(s, o) {
    const empty = o.empty
    const row = (agent, title, sub, active) => h('span', { class: `d-srow${active ? ' is-active' : ''}`, loc: active ? 'x.session-row' : null },
      h('span', { class: 'd-srow__agent' }, agent), h('span', { class: 'd-srow__title' }, title),
      sub ? h('span', { class: 'd-srow__sub' }, sub) : null,
      active ? h('span', { class: 'd-srow__acts' },
        h('span', { class: 'd-mini', loc: 'sessions.row-menu' }, ico('dots')),
        h('span', { class: 'd-mini', loc: 'sessions.row-duplicate' }, ico('fork')),
        h('span', { class: 'd-mini', loc: 'sessions.row-close' }, ico('x'))) : null)
    const sessions = h('div', { class: 'd-sessions d-card' },
      h('div', { class: 'd-sessions__head' },
        h('span', { class: 'd-muted' }, ico('panel')), h('b', {}, 'Sessions'),
        h('span', { class: 'd-iconbtn d-iconbtn--box', loc: 'sessions.list-menu' }, ico('dots')),
        h('span', { class: 'd-split' },
          h('span', { class: 'd-split__main', loc: 'chat.new-session' }, ico('plus'), 'New'),
          h('span', { class: 'd-split__more', loc: 'sessions.create-menu' }, ico('down')))),
      h('span', { class: 'd-field', loc: 'sessions.list' }, ico('search'), 'Search sessions…', h('span', { class: 'd-spacer' }), ico('filter')),
      empty ? row('kirocrew', 'New session', null, true) : row('kirocrew', 'Fix the login test', 'Test passes on CI now.', true),
      row('kirocrew', 'Release notes', 'Draft is ready for review.'),
      row('kirocrew', 'Terraform plan review', null),
      h('span', { class: 'd-older-link' }, 'Show all older sessions'),
      h('span', { class: 'd-spacer' }),
      h('span', { class: 'd-sessions__foot', loc: 'chat.older-sessions' }, ico('history'), h('b', {}, 'Older Sessions'), h('span', { class: 'd-spacer' }), ico('right')))

    const convo = h('div', { class: 'd-convo' },
      h('div', { class: 'd-convo__head' }, ico('down', 'd-muted'),
        h('b', { loc: 'chat.session-title' }, empty ? 'New session' : 'Fix the login test'),
        h('span', { class: 'd-spacer' }), h('span', { class: 'd-muted' }, ico('external')),
        s.panel ? null : h('span', { class: 'd-iconbtn', loc: 'chat.side-panel-open' }, ico('panelR'))),
      empty
        ? h('div', { class: 'd-welcome' }, h('span', { class: 'd-welcome__ghost' }, ico('ghost')), h('span', { class: 'd-welcome__line' }, 'Ready when you are.'),
            h('div', { class: 'd-welcome__cards' }, h('span', { class: 'd-sugg' }), h('span', { class: 'd-sugg' }), h('span', { class: 'd-sugg' })))
        : h('div', { class: 'd-transcript', loc: 'x.transcript' },
            h('span', { class: 'd-bubble' }, 'The login test fails on CI. Can you find out why?'),
            h('span', { class: 'd-reply' }), h('span', { class: 'd-reply d-reply--short' })),
      empty ? h('span', { class: 'd-memchip', loc: 'chat.memory-mode' }, ico('history'), 'Persistent', ico('down')) : null,
      h('div', { class: 'd-composer', loc: 'x.message-box' },
        h('span', { class: 'd-composer__text' }, 'Message Kiro… (/command · @file · $skill · ! shell command)'),
        h('div', { class: 'd-composer__row' },
          h('span', { class: 'd-cbtn', loc: 'composer.add-menu' }, ico('plus')),
          h('span', { class: 'd-cbtn', loc: 'composer.automation' }, ico('target')),
          h('span', { class: 'd-cbtn d-cbtn--text', loc: 'composer.approval-mode' }, ico('shield'), 'Normal'),
          h('span', { class: 'd-spacer' }),
          h('span', { class: 'd-cbtn', loc: 'composer.voice' }, ico('mic')),
          h('span', { class: 'd-cbtn', loc: 'x.optimize' }, ico('sparkle')),
          h('span', { class: 'd-send', loc: 'composer.send' }, ico('up')))),
      h('div', { class: 'd-under' },
        h('span', { class: 'd-under__item', loc: 'x.agent-selector' }, ico('bot'), 'kirocrew'),
        h('span', { class: 'd-under__item', loc: 'x.project-pill' }, ico('folder'), 'my-repo'),
        h('span', { class: 'd-spacer' }),
        empty ? null : h('span', { class: 'd-ctx', loc: 'composer.context-usage' }, h('span', {})),
        h('span', { class: 'd-under__item', loc: 'chat.model-picker' }, 'auto')))

    const panel = s.panel ? h('div', { class: 'd-panel d-card', loc: 'x.side-panel' },
      h('div', { class: 'd-panel__tabs' },
        h('span', { class: 'd-ptab is-selected' }, ico('summary'), 'Summary'),
        h('span', { class: 'd-ptab' }, ico('git')), h('span', { class: 'd-ptab' }, ico('artifacts')),
        h('span', { class: 'd-iconbtn', loc: 'chat.side-panel.add' }, ico('plus')),
        h('span', { class: 'd-spacer' }), h('span', { class: 'd-muted' }, ico('hdots')),
        h('span', { class: 'd-iconbtn', loc: 'x.side-panel-close' }, ico('panelR'))),
      h('b', { class: 'd-panel__title' }, 'Summary'),
      h('span', { class: 'd-block' }), h('span', { class: 'd-block d-block--tall' })) : null
    return [sessions, convo, panel].filter(Boolean)
  }

  function pageScreen(s, want) {
    const page = s.screen
    if (page === 'page.members') {
      const mate = (name, line) => h('span', { class: 'd-mate' }, h('span', { class: 'd-mate__face' }, ico('ghost')),
        h('span', { class: 'd-mate__text' }, h('b', {}, name), h('span', {}, line)))
      return [h('div', { class: 'd-sessions d-card' },
        h('div', { class: 'd-sessions__head' }, h('b', {}, label(page)), h('span', { class: 'd-iconbtn d-iconbtn--box' }, ico('plus'))),
        h('div', { class: 'd-roster', loc: 'members.roster-list' }, mate('Ops Buddy', 'Watches the on-call queue'),
          mate('Terraform Pal', 'Reviews plans before apply'), mate('Docs Writer', 'Keeps the README honest'))),
        h('div', { class: 'd-convo' }, h('div', { class: 'd-welcome' }, h('span', { class: 'd-welcome__ghost' }, ico('users')),
          h('span', { class: 'd-pagebody__hint' }, 'Pick a mate to open its chat')))]
    }
    if (page === 'page.capabilities' || page === 'page.settings') {
      const isSettings = page === 'page.settings'
      const groups = isSettings ? D.settings : D.customize
      const col = h('div', { class: 'd-col' }, h('b', { class: 'd-col__title' }, label(page)),
        h('span', { class: 'd-field' }, ico('search'), isSettings ? 'Search settings…' : 'Search…'))
      for (const g of groups) {
        if (g.group) col.append(h('span', { class: 'd-col__group' }, g.group))
        for (const t of g.tabs) {
          if (t.preview && !want.includes(t.loc)) continue   // a preview tab exists only once its switch is on
          const key = t.loc.replace('settings.tab.', '')
          col.append(h('span', { class: `d-coltab${s.sidetab === t.loc ? ' is-selected' : ''}`, loc: t.loc },
            isSettings ? h('span', { class: `d-tile d-tile--${TILE[key] || 'gray'}` }) : ico('doc', 'd-muted'), t.label))
        }
      }
      return [col, h('div', { class: 'd-pagebody' }, ...content(s, want, true))]
    }
    return [h('div', { class: 'd-pagebody d-pagebody--full' },
      h('b', { class: 'd-pagebody__title' }, label(page)), h('span', { class: 'd-pagebody__desc' }), ...content(s, want, false))]
  }

  function content(s, want, split) {
    const out = []
    const container = s.sidetab || s.screen
    if (split) {
      if (!s.sidetab) return [h('span', { class: 'd-pagebody__hint' }, 'Pick a section'), h('span', { class: 'd-block' }), h('span', { class: 'd-block' })]
      out.push(h('b', { class: 'd-pagebody__title' }, label(s.sidetab)), h('span', { class: 'd-pagebody__desc' }))
    }
    const subs = s.sidetab && s.sidetab.startsWith('settings.tab.') ? (D.subnav[s.sidetab] || []) : []
    const deepest = s.ctab || s.subnav || container
    let kids = (D.children[deepest] || []).filter(c => !c.loc.startsWith('settings.sub.'))
    const emptySchedule = s.screen === 'page.schedule' && want.includes('schedule.create-first')
    if (s.screen === 'page.schedule') {
      kids = kids.filter(c => !JOB_ACTIONS.has(c.loc) && (emptySchedule ? EMPTY_SCHEDULE.has(c.loc) || c.kind === 'tab' : !EMPTY_SCHEDULE.has(c.loc)))
    }
    const isCtab = c => c.kind === 'tab' && !c.loc.startsWith('tab.') && !c.loc.startsWith('settings.')
    const ctabs = (D.children[container] || []).filter(isCtab)
    const pick = (list, n) => {
      const must = list.filter(c => want.includes(c.loc))
      return [...must, ...list.filter(c => !want.includes(c.loc))].slice(0, Math.max(n, must.length))
    }
    const body = h('div', { class: 'd-rows' })
    if (ctabs.length) body.append(h('div', { class: 'd-tabs' },
      ...ctabs.map(x => h('span', { class: `d-tab${s.ctab === x.loc ? ' is-selected' : ''}`, loc: x.loc }, x.label))))
    const buttons = pick(kids.filter(c => ['button', 'menu-item', 'link', 'toggle', 'field'].includes(c.kind)), 3)
    if (buttons.length) body.append(h('div', { class: 'd-toolbar' },
      ...buttons.map((b, i) => h('span', { class: `d-btn${i === 0 ? ' d-btn--primary' : ''}`, loc: b.loc }, b.label))))
    if (s.screen === 'page.schedule' && !emptySchedule) body.append(jobs(s, want))
    for (const l of kids.filter(c => c.kind === 'list' && c.loc !== 'schedule.job-list')) body.append(h('div', { class: 'd-tiles', loc: l.loc },
      h('span', { class: 'd-tiles__label' }, l.label), ...[1, 2, 3, 4, 5, 6].map(() => h('span', { class: 'd-tilecard' }))))
    const rows = pick(kids.filter(c => c.kind === 'setting'), 5)
    for (const r of rows) body.append(h('div', { class: 'd-setrow', loc: r.loc },
      h('span', { class: 'd-setrow__text' }, h('b', {}, r.label), h('span', { class: 'd-setrow__desc' })), h('span', { class: 'd-switch' })))
    const hasList = kids.some(c => c.kind === 'list') || (s.screen === 'page.schedule' && !emptySchedule)
    if (!rows.length && !hasList) body.append(h('span', { class: 'd-block' }), h('span', { class: 'd-block' }), h('span', { class: 'd-block d-block--short' }))
    if (subs.length) {
      out.push(h('div', { class: 'd-subsplit' },
        h('div', { class: 'd-subnav' }, ...subs.map(x => h('span', { class: `d-subtab${s.subnav === x.loc ? ' is-selected' : ''}`, loc: x.loc }, ico('doc', 'd-muted'), x.label))),
        body))
    } else out.push(body)
    return out
  }

  function jobs(s, want) {
    const list = h('div', { class: 'd-jobs' },
      h('span', { class: `d-job${s.job ? ' is-selected' : ''}`, loc: 'x.job-row' }, ico('calendar', 'd-muted'), h('b', {}, 'Weekday standup'), h('span', { class: 'd-spacer' }), h('span', { class: 'd-muted' }, '08:30')),
      h('span', { class: 'd-job' }, ico('calendar', 'd-muted'), h('b', {}, 'Nightly backup'), h('span', { class: 'd-spacer' }), h('span', { class: 'd-muted' }, '02:00')))
    if (!s.job) return list
    const acts = ['schedule.run-now', 'schedule.pause', ...(want.includes('schedule.secret-approve') ? ['schedule.secret-approve'] : [])]
    return h('div', { class: 'd-jobsplit' }, list, h('div', { class: 'd-jobpanel' }, h('b', {}, 'Weekday standup'),
      want.includes('schedule.secret-approve') ? h('span', { class: 'd-jobpanel__note' }, 'Asks to use a secret') : null,
      h('div', { class: 'd-toolbar d-jobpanel__acts' }, ...acts.map((a, i) => h('span', { class: `d-btn${i === 0 ? ' d-btn--primary' : ''}`, loc: a }, label(a))))))
  }

  function placeGeneric(loc) {
    const panelActs = $main.querySelector('.d-jobpanel__acts')
    const where = panelActs || $main.querySelector('.d-rows') || $main.querySelector('.d-convo') || $main
    const bar = panelActs || where.querySelector('.d-toolbar') || where.appendChild(h('div', { class: 'd-toolbar' }))
    bar.append(h('span', { class: 'd-btn', loc }, label(loc)))
  }

  // Menus open from their button; the project and agent pickers are drawn by hand (not in the index).
  function openMenu(loc) {
    const anchor = find(loc)
    if (!anchor) return
    let body
    if (loc === 'x.project-pill') {
      body = h('div', { class: 'd-menu__body', loc: 'x.project-picker' }, h('span', { class: 'd-menu__head' }, 'Project'),
        ...['~/work/my-repo', '~/work/website', '~/notes'].map((p, i) => h('span', { class: `d-menu__item${i ? '' : ' is-on'}` }, ico('folder'), p)),
        h('span', { class: 'd-menu__item d-menu__item--muted' }, 'Choose another folder…'))
    } else if (loc === 'x.agent-selector') {
      const agent = (name, desc, on) => h('span', { class: `d-agent${on ? ' is-on' : ''}` },
        h('span', { class: 'd-agent__name' }, name, h('span', { class: 'd-agent__tag' }, on ? 'default' : 'custom')), h('span', { class: 'd-agent__desc' }, desc))
      body = h('div', { class: 'd-menu__body d-menu__body--agents', loc: 'x.agent-list' }, h('span', { class: 'd-field' }, ico('search'), 'Search agents…'),
        agent('kirocrew', 'The default agent, with memory and tools.', true),
        agent('release-helper', 'Prepares release notes and tags the build.'),
        agent('standup-writer', 'Writes a daily standup from git history.'))
    } else {
      const kids = (D.children[loc] || []).slice(0, 7)
      body = h('div', { class: 'd-menu__body' }, ...kids.map(c => h('span', { class: 'd-menu__item', loc: c.loc }, ico('doc', 'd-muted'), c.label)),
        ...(kids.length < 4 ? [h('span', { class: 'd-menu__more' }), h('span', { class: 'd-menu__more' })] : []))
    }
    const menu = h('div', { class: 'd-menu' }, body)
    $layer.append(menu)
    const a = rectIn(anchor), up = a.y > H / 2
    menu.style.left = `${Math.max(8, Math.min(a.x, W - menu.offsetWidth - 8))}px`
    menu.style.top = `${up ? a.y - menu.offsetHeight - 6 : a.y + a.h + 6}px`
  }

  // ------------------------------------------------------------ geometry, pointer, marks
  function find(loc) { return canvas.querySelector(`[data-loc="${CSS.escape(loc)}"]`) }
  function rectIn(el) {
    const c = canvas.getBoundingClientRect(), r = el.getBoundingClientRect()
    return { x: (r.left - c.left) / scale, y: (r.top - c.top) / scale, w: r.width / scale, h: r.height / scale }
  }
  function aim(el) {
    const r = rectIn(el)
    return { x: r.x + Math.min(r.w / 2, r.w - 10), y: r.y + Math.min(r.h * 0.62, 24) }
  }
  function pointTo(el, animate) {
    const p = aim(el)
    pointer.classList.toggle('is-instant', !animate)
    pointer.style.transform = `translate(${p.x}px, ${p.y}px)`
    pointer.hidden = false
    if (follow) pan(p, animate, rectIn(el))
  }
  function click() { pointer.classList.remove('is-click'); void pointer.offsetWidth; pointer.classList.add('is-click') }
  function badge(el, n, now) {
    const r = rectIn(el)
    const b = h('span', { class: `d-badge${now ? ' is-now' : ''}` }, String(n))
    b.style.left = `${Math.max(2, r.x - 9)}px`; b.style.top = `${Math.max(2, r.y - 9)}px`
    $layer.append(b)
  }
  function focusOn(el, animate) { if (follow && el) pan(aim(el), animate, rectIn(el)) }

  // Fit the drawing to the frame; on narrow frames zoom in and follow the pointer instead.
  const onFit = []
  function fit() {
    const fitScale = frame.clientWidth / W
    follow = fitScale < MIN_SCALE
    scale = follow ? MIN_SCALE : fitScale
    frame.style.height = `${Math.round(height * scale)}px`
    canvas.style.transform = `scale(${scale})`
    for (const fn of onFit) fn()
  }
  function pan(p, animate, r) {
    const view = frame.clientWidth / scale
    // A part wider than the view (a full-width row on a phone) starts at its left edge, where its name is.
    const want = r && r.w > view - 16 ? r.x - 8 : p.x - view / 2
    const x = Math.max(0, Math.min(W - view, want))
    canvas.classList.toggle('is-instant', !animate)
    canvas.style.transform = `scale(${scale}) translateX(${-x}px)`
  }
  new ResizeObserver(fit).observe(frame)

  return {
    render, find, rectIn, pointTo, click, badge, focusOn, fit, label,
    hidePointer: () => { pointer.hidden = true },
    onFit: fn => onFit.push(fn),
  }
}
