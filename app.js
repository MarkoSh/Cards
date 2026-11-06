// Cards: masonry gallery of the 1000 most frequent nouns/verbs per language.
// State: base language (what you know) -> decks of the other two; pos = n|v.
const LANGS = ['ru', 'en', 'th'];
const NAMES = { ru: 'RU', en: 'EN', th: 'TH' };
const FIELD = { ru: 'r', en: 'e', th: 't' };
const POS = [['n', 'nouns'], ['v', 'verbs']];
const I18N = {
  ru: {
    nouns: 'Существительные', verbs: 'Глаголы', search: 'Поиск…', empty: 'Ничего не найдено',
    title: 'Cards — слова в карточках',
    description: '1000 частотных существительных и 1000 глаголов английского, русского и тайского в карточках с иконками, транскрипцией и переводом.',
    footer: 'Иконки: <a class="underline" href="https://openmoji.org" rel="noopener" target="_blank">OpenMoji</a> (CC BY-SA 4.0). Частотность: wordfreq (en/ru), Thai National Corpus (th). Переводы подобраны вручную.',
    projects: 'Другие проекты:'
  },
  en: {
    nouns: 'Nouns', verbs: 'Verbs', search: 'Search…', empty: 'Nothing found',
    title: 'Cards — vocabulary in cards',
    description: '1000 frequent nouns and 1000 verbs in English, Russian and Thai, with icons, transcriptions and translations.',
    footer: 'Icons: <a class="underline" href="https://openmoji.org" rel="noopener" target="_blank">OpenMoji</a> (CC BY-SA 4.0). Frequency: wordfreq (en/ru), Thai National Corpus (th). Translations curated by hand.',
    projects: 'Other projects:'
  },
  th: {
    nouns: 'คำนาม', verbs: 'คำกริยา', search: 'ค้นหา…', empty: 'ไม่พบคำที่ค้นหา',
    title: 'Cards — เรียนคำศัพท์ด้วยบัตรคำ',
    description: 'คำนามและคำกริยาที่พบบ่อยภาษาละ 1,000 คำ ในภาษาอังกฤษ รัสเซีย และไทย พร้อมไอคอน การถอดเสียง และคำแปล',
    footer: 'ไอคอน: <a class="underline" href="https://openmoji.org" rel="noopener" target="_blank">OpenMoji</a> (CC BY-SA 4.0) · ความถี่คำ: wordfreq (en/ru), Thai National Corpus (th) · คำแปลคัดสรรด้วยตนเอง',
    projects: 'โครงการอื่น:'
  }
};

let state = { base: 'ru', target: 'en', pos: 'n' };
try {
  const saved = JSON.parse(localStorage.getItem('cards') || '{}');
  if (LANGS.includes(saved.base)) state.base = saved.base;
  if (LANGS.includes(saved.target) && saved.target !== state.base) state.target = saved.target;
  if (['n', 'v'].includes(saved.pos)) state.pos = saved.pos;
} catch (e) {}
if (state.target === state.base) state.target = LANGS.find(l => l !== state.base);

const $ = id => document.getElementById(id);
const esc = s => s.replace(/[&<>"]/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[m]));
const hash = s => [...s].reduce((h, c) => (h * 31 + c.charCodeAt(0)) >>> 0, 7);

function save() { localStorage.setItem('cards', JSON.stringify(state)); }

function chips(el, items, current, cb) {
  el.innerHTML = items.map(([val, label]) =>
    `<button data-v="${val}" aria-pressed="${val === current}" class="px-3 py-1 rounded-lg cursor-pointer ${val === current ? 'bg-amber-400 text-zinc-950 font-semibold' : 'text-zinc-400 hover:text-zinc-100'}">${label}</button>`).join('');
  el.querySelectorAll('button').forEach(b => b.onclick = () => cb(b.dataset.v));
}

function deck() {
  // frequency rank first, then authored order to fill up to 1000 cards
  return CONCEPTS
    .map((c, i) => [(c.k && c.k[state.target]) || 9999, i, c])
    .filter(x => x[2].p === state.pos)
    .sort((a, b) => a[0] - b[0] || a[1] - b[1])
    .map(x => x[2])
    .filter((c, i, all) => all.findIndex(d => d[FIELD[state.target]] === c[FIELD[state.target]]) === i)  // synonyms share a translation: one card per word
    .slice(0, 1000);
}

function transcription(c) {
  if (state.target === 'en') return c.i || '';
  if (state.target === 'th') return c.x || '';
  return '';
}

// no pictogram for abstract words: first letter of the deck word in a ring
function badge(c) {
  const w = c[FIELD[state.target]];
  const ch = (state.target === 'th' ? w.match(/[\u0E01-\u0E2E]/) : null)?.[0] || [...w][0];
  return `<span class="w-20 h-20 rounded-full border-2 border-amber-400/50 flex items-center justify-center text-3xl font-semibold ${state.target === 'th' ? 'pb-1' : ''}">${esc(ch)}</span>`;
}

const COPY_ICON = '<svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="8" y="8" rx="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>';
const CHECK_ICON = '<svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>';
const HEIGHTS = [208, 224, 240];   // px of h-52 / h-56 / h-60

// how common the word is: rank in the frequency list of the deck language (1 = most common)
function freq(c) {
  const r = c.k && c.k[state.target];
  const lit = !r ? 0 : r <= 50 ? 5 : r <= 200 ? 4 : r <= 500 ? 3 : r <= 1000 ? 2 : 1;
  const bars = [0, 1, 2, 3, 4].map(i => `<span class="w-0.5 rounded-full ${i < lit ? 'bg-amber-400' : 'bg-zinc-700'}" style="height:${4 + i * 2}px"></span>`).join('');
  return `<span class="absolute top-2 left-2 flex items-end gap-px" title="${r ? '#' + r : ''}">${bars}</span>`;
}

function columns() {
  const w = window.innerWidth;
  return w < 640 ? 2 : w < 1024 ? 3 : w < 1440 ? 4 : w < 1900 ? 5 : 6;
}

function cardHTML(c, h) {
  const size = ['w-16 h-16', 'w-20 h-20', 'w-24 h-24'][h];
  const height = ['h-52', 'h-56', 'h-60'][h];
  const word = c[FIELD[state.target]];
  return `<article class="card ${height} relative overflow-hidden bg-zinc-900 p-4 flex flex-col items-center justify-center text-center cursor-pointer select-none" data-e="${esc(c.e)}">
      ${freq(c)}
      <button type="button" class="copy absolute top-1.5 right-1.5 flex items-center justify-center w-6 h-6 rounded-full border border-zinc-700 text-zinc-500 hover:text-amber-400 hover:border-amber-400 cursor-pointer" aria-label="Copy" data-w="${esc(word)}">${COPY_ICON}</button>
      <div class="text-amber-400 flex justify-center shrink-0">${c.g ? `<svg class="${size}"><use href="#i-${c.g}"/></svg>` : badge(c)}</div>
      <div class="mt-2 font-semibold ${state.target === 'th' ? 'text-xl' : 'text-lg'} leading-snug">${esc(word)}</div>
      <div class="h-4 text-xs text-zinc-500 mt-0.5">${esc(transcription(c))}</div>
      <div class="translation h-10 mt-2 pt-2 border-t border-zinc-800 text-sm text-zinc-400">${esc(c[FIELD[state.base]])}</div>
    </article>`;
}

function copyText(text) {
  if (navigator.clipboard && navigator.clipboard.writeText) return navigator.clipboard.writeText(text);
  return new Promise((ok, no) => {
    const t = document.createElement('textarea');
    t.value = text; document.body.appendChild(t); t.select();
    try { document.execCommand('copy') ? ok() : no(); } catch (e) { no(e); } finally { t.remove(); }
  });
}

function render() {
  const q = $('q').value.trim().toLowerCase();
  const items = deck().filter(c => !q ||
    ['e', 'r', 't'].some(f => c[f].toLowerCase().includes(q)));
  // masonry that keeps the order: every next card goes to the shortest column,
  // so the rank grows left to right, then down
  const n = columns(), cols = Array.from({ length: n }, () => ({ h: 0, html: '' }));
  items.forEach(c => {
    const h = hash(c.e) % 3, col = cols.reduce((m, x) => x.h < m.h ? x : m);
    col.html += cardHTML(c, h);
    col.h += HEIGHTS[h] + 1;
  });
  $('grid').innerHTML = cols.map(c => `<div class="flex-1 min-w-0 flex flex-col gap-px">${c.html}</div>`).join('');
  $('grid').querySelectorAll('.card').forEach(el => el.onclick = () => el.classList.toggle('open'));
  $('grid').querySelectorAll('.copy').forEach(b => b.onclick = e => {
    e.stopPropagation();
    copyText(b.dataset.w).then(() => {
      b.innerHTML = CHECK_ICON; b.classList.add('text-amber-400', 'border-amber-400');
      setTimeout(() => { b.innerHTML = COPY_ICON; b.classList.remove('text-amber-400', 'border-amber-400'); }, 1000);
    }).catch(() => {});
  });
  $('empty').classList.toggle('hidden', items.length > 0);
}

function renderControls() {
  chips($('base'), LANGS.map(l => [l, NAMES[l]]), state.base, v => {
    state.base = v;
    if (state.target === v) state.target = LANGS.find(l => l !== v);
    save(); renderAll();
  });
  const text = I18N[state.base];
  chips($('pos'), POS.map(([value, key]) => [value, text[key]]), state.pos,
    v => { state.pos = v; save(); renderControls(); render(); });
  const others = LANGS.filter(l => l !== state.base);
  chips($('targets'), others.map(l => [l, NAMES[l]]), state.target, v => { state.target = v; save(); renderAll(); });
}

function renderAll() {
  const text = I18N[state.base];
  document.documentElement.lang = state.base;
  document.title = text.title;
  document.querySelector('meta[name="description"]').content = text.description;
  $('q').placeholder = text.search;
  $('empty').textContent = text.empty;
  $('footer-note').innerHTML = text.footer;
  $('projects-label').textContent = text.projects;
  renderControls();
  render();
}

$('sprite').innerHTML = SPRITE;
renderAll();
$('q').oninput = render;
let cols = columns();
window.addEventListener('resize', () => { if (columns() !== cols) { cols = columns(); render(); } });
if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').catch(() => {});
