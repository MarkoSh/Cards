// Cards: a gallery of the most frequent nouns and verbs in Russian, English and Thai.
// You pick the language you know (base) and the deck you study (target); the card shows the
// deck word and reveals the base-language translation on click.
// Data: CONCEPTS (data.js), SPRITE (icons/sprite.js). Both are built by tools/build_data.py.

const LANGS = ['ru', 'en', 'th'];
const CODE = { ru: 'RU', en: 'EN', th: 'TH' };
const FIELD = { ru: 'r', en: 'e', th: 't' };   // concept field holding the word of each language
const DECK_SIZE = 1000;
const NO_RANK = 1e9;      // words missing from a frequency list go to the end of the deck
const STORAGE_KEY = 'cards';

const TEXT = {
  ru: {
    title: 'Cards — слова в карточках', search: 'Поиск…', empty: 'Ничего не найдено',
    n: 'Существительные', v: 'Глаголы', copy: 'Копировать', copied: 'Скопировано', translate: 'Google Переводчик',
    description: 'До 1000 частотных существительных и глаголов английского, русского и тайского в карточках с иконками, транскрипцией и переводом.',
    credits: 'Иконки: {openmoji} (CC BY-SA 4.0). Частотность: wordfreq (en/ru), Thai National Corpus (th). Переводы подобраны вручную.',
    projects: 'Другие проекты:',
  },
  en: {
    title: 'Cards — vocabulary in cards', search: 'Search…', empty: 'Nothing found',
    n: 'Nouns', v: 'Verbs', copy: 'Copy', copied: 'Copied', translate: 'Google Translate',
    description: 'Up to 1000 frequent nouns and verbs in English, Russian and Thai, with icons, transcriptions and translations.',
    credits: 'Icons: {openmoji} (CC BY-SA 4.0). Frequency: wordfreq (en/ru), Thai National Corpus (th). Translations curated by hand.',
    projects: 'Other projects:',
  },
  th: {
    title: 'Cards — เรียนคำศัพท์ด้วยบัตรคำ', search: 'ค้นหา…', empty: 'ไม่พบคำที่ค้นหา',
    n: 'คำนาม', v: 'คำกริยา', copy: 'คัดลอก', copied: 'คัดลอกแล้ว', translate: 'Google แปลภาษา',
    description: 'คำนามและคำกริยาที่พบบ่อยสูงสุดภาษาละ 1,000 คำ ในภาษาอังกฤษ รัสเซีย และไทย พร้อมไอคอน การถอดเสียง และคำแปล',
    credits: 'ไอคอน: {openmoji} (CC BY-SA 4.0) · ความถี่คำ: wordfreq (en/ru), Thai National Corpus (th) · คำแปลคัดสรรด้วยตนเอง',
    projects: 'โครงการอื่น:',
  },
};

const ICON = {   // lucide, 24x24
  copy: '<rect width="14" height="14" x="8" y="8" rx="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>',
  check: '<path d="M20 6 9 17l-5-5"/>',
  translate: '<path d="m5 8 6 6"/><path d="m4 14 6-6 2-3"/><path d="M2 5h12"/><path d="M7 2h1"/><path d="m22 22-5-10-5 10"/><path d="M14 18h6"/>',
};
const icon = name => `<svg class="size-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICON[name]}</svg>`;

// card heights vary a little so the wall does not look like a table (px must match the classes)
const LOOKS = [
  { height: 'h-52', px: 208, glyph: 'size-16' },
  { height: 'h-56', px: 224, glyph: 'size-20' },
  { height: 'h-60', px: 240, glyph: 'size-24' },
];

const $ = id => document.getElementById(id);
const esc = s => s.replace(/[&<>"]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch]));
const norm = s => s.toLowerCase().replace(/ё/g, 'е');
const lookOf = c => LOOKS[[...c.e].reduce((h, ch) => (h * 31 + ch.charCodeAt(0)) >>> 0, 7) % LOOKS.length];
const otherLangs = lang => LANGS.filter(l => l !== lang);

// ---- state -------------------------------------------------------------------------------

const state = { base: 'ru', target: 'en', pos: 'n' };

function loadState() {
  let saved = {};
  try { saved = JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}; } catch (e) {}
  if (LANGS.includes(saved.base)) state.base = saved.base;
  if (otherLangs(state.base).includes(saved.target)) state.target = saved.target;
  else state.target = otherLangs(state.base)[0];
  if (saved.pos === 'n' || saved.pos === 'v') state.pos = saved.pos;
}

function setState(patch) {
  Object.assign(state, patch);
  if (state.target === state.base) state.target = otherLangs(state.base)[0];
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch (e) {}
  paintChrome();
  paintGrid();
}

// ---- deck: most frequent first, then the authored order --------------------------------

CONCEPTS.forEach(c => { c.s = norm([c.e, c.r, c.t, c.x].join(' ')); });   // search text

const decks = new Map();
function deck() {
  const key = state.target + state.pos;
  if (!decks.has(key)) {
    const field = FIELD[state.target], seen = new Set();
    decks.set(key, CONCEPTS
      .map((c, i) => ({ c, i, rank: c.k?.[state.target] ?? NO_RANK, en: c.k?.en ?? NO_RANK }))
      .filter(x => x.c.p === state.pos)
      // synonyms share a rank when they share a translation: the commonest English sense goes first
      .sort((a, b) => a.rank - b.rank || a.en - b.en || a.i - b.i)
      .map(x => x.c)
      // one card per deck word
      .filter(c => !seen.has(c[field]) && seen.add(c[field]))
      .slice(0, DECK_SIZE));
  }
  return decks.get(key);
}

// ---- cards -------------------------------------------------------------------------------

function glyph(c, look) {
  if (c.g) return `<svg class="${look.glyph} text-amber-400" aria-hidden="true"><use href="#i-${c.g}"/></svg>`;
  // abstract word, no pictogram: its first letter in a ring
  const word = c[FIELD[state.target]];
  const letter = (state.target === 'th' && word.match(/[ก-ฮ]/)?.[0]) || [...word][0];
  return `<span class="flex size-20 items-center justify-center rounded-full border-2 border-amber-400/50 text-3xl text-amber-400 font-semibold font-word ${state.target === 'th' ? 'pb-1' : ''}" aria-hidden="true">${esc(letter)}</span>`;
}

// five bars: how common the word is (rank in the frequency list of the deck language)
function frequency(c) {
  const rank = c.k?.[state.target];
  const lit = !rank ? 0 : rank <= 50 ? 5 : rank <= 200 ? 4 : rank <= 500 ? 3 : rank <= 1000 ? 2 : 1;
  const bars = [0, 1, 2, 3, 4].map(i =>
    `<span class="w-0.5 rounded-full ${i < lit ? 'bg-amber-400' : 'bg-zinc-700'}" style="height:${4 + i * 2}px"></span>`).join('');
  return `<span class="absolute left-2 top-2 flex items-end gap-px" ${rank ? `title="#${rank}"` : ''} aria-hidden="true">${bars}</span>`;
}

function transcription(c) {
  return (state.target === 'en' ? c.i : state.target === 'th' ? c.x : '') || '';
}

function card(c) {
  const t = TEXT[state.base], look = lookOf(c), word = c[FIELD[state.target]];
  const url = `https://translate.google.com/?sl=${state.target}&tl=${state.base}&text=${encodeURIComponent(word)}&op=translate`;
  return `<article class="card ${look.height} relative bg-zinc-900">
  <button type="button" class="reveal absolute inset-0 flex select-none flex-col items-center justify-center p-4 text-center" aria-expanded="false">
    ${glyph(c, look)}
    <span class="font-word mt-2 block font-semibold leading-snug ${state.target === 'th' ? 'text-xl' : 'text-lg'}">${esc(word)}</span>
    <span class="mt-0.5 block h-4 text-xs text-zinc-500">${esc(transcription(c))}</span>
    <span class="translation mt-2 block h-10 w-full border-t border-zinc-800 pt-2 text-sm text-zinc-400" aria-hidden="true">${esc(c[FIELD[state.base]])}</span>
  </button>
  ${frequency(c)}
  <a class="corner right-9" href="${url}" target="_blank" rel="noopener" title="${t.translate}" aria-label="${t.translate}">${icon('translate')}</a>
  <button type="button" class="corner copy right-1.5" data-word="${esc(word)}" title="${t.copy}" aria-label="${t.copy}">${icon('copy')}</button>
</article>`;
}

// ---- grid: columns filled in reading order (every card goes to the shortest column) ------

const BREAKPOINTS = [[1900, 6], [1440, 5], [1024, 4], [640, 3]].map(([w, n]) => [matchMedia(`(min-width:${w}px)`), n]);
const columnCount = () => BREAKPOINTS.find(([mq]) => mq.matches)?.[1] ?? 2;

function paintGrid() {
  const q = norm($('q').value.trim());
  const items = deck().filter(c => !q || c.s.includes(q));
  const cols = Array.from({ length: columnCount() }, () => ({ height: 0, html: '' }));
  for (const c of items) {
    const col = cols.reduce((a, b) => b.height < a.height ? b : a);
    col.html += card(c);
    col.height += lookOf(c).px + 1;
  }
  $('grid').innerHTML = cols.map(col => `<div class="flex min-w-0 flex-1 flex-col gap-px">${col.html}</div>`).join('');
  $('empty').classList.toggle('hidden', items.length > 0);
}

// ---- page chrome: switches, texts --------------------------------------------------------

function segment(el, items, current, label) {
  el.innerHTML = items.map(([value, text]) =>
    `<button type="button" data-value="${value}" aria-pressed="${value === current}" ${label ? `title="${label(value)}"` : ''}>${text}</button>`).join('');
}

function paintChrome() {
  const t = TEXT[state.base];
  const names = new Intl.DisplayNames([state.base], { type: 'language' });
  const langName = l => names.of(l);
  document.documentElement.lang = state.base;
  document.title = t.title;
  document.querySelector('meta[name="description"]').content = t.description;
  $('q').placeholder = t.search;
  $('q').setAttribute('aria-label', t.search);
  $('empty').textContent = t.empty;
  $('credits').innerHTML = t.credits.replace('{openmoji}', '<a class="underline" href="https://openmoji.org" target="_blank" rel="noopener">OpenMoji</a>');
  $('projects').textContent = t.projects;
  segment($('base'), LANGS.map(l => [l, CODE[l]]), state.base, langName);
  segment($('target'), otherLangs(state.base).map(l => [l, CODE[l]]), state.target, langName);
  segment($('pos'), [['n', t.n], ['v', t.v]], state.pos);
}

// ---- events (one listener per area; the grid is re-created on every repaint) -------------

const setLabel = (el, text) => { el.title = text; el.setAttribute('aria-label', text); };

function copyText(text) {
  if (navigator.clipboard?.writeText) return navigator.clipboard.writeText(text);
  return new Promise((resolve, reject) => {
    const box = Object.assign(document.createElement('textarea'), { value: text });
    document.body.append(box);
    box.select();
    try { document.execCommand('copy') ? resolve() : reject(); } catch (e) { reject(e); } finally { box.remove(); }
  });
}

$('grid').addEventListener('click', e => {
  const copy = e.target.closest('.copy');
  if (copy) {
    copyText(copy.dataset.word).then(() => {
      const label = copy.title;
      copy.innerHTML = icon('check');
      copy.dataset.done = '';
      setLabel(copy, TEXT[state.base].copied);
      setTimeout(() => {
        copy.innerHTML = icon('copy');
        delete copy.dataset.done;
        setLabel(copy, label);
      }, 1000);
    }).catch(() => {});
    return;
  }
  const reveal = e.target.closest('.reveal');
  if (reveal) {
    const open = reveal.parentElement.classList.toggle('open');
    reveal.setAttribute('aria-expanded', open);
    reveal.querySelector('.translation').setAttribute('aria-hidden', !open);
  }
});

$('base').addEventListener('click', e => { const b = e.target.closest('button'); if (b) setState({ base: b.dataset.value }); });
$('target').addEventListener('click', e => { const b = e.target.closest('button'); if (b) setState({ target: b.dataset.value }); });
$('pos').addEventListener('click', e => { const b = e.target.closest('button'); if (b) setState({ pos: b.dataset.value }); });

let searchFrame = 0;
$('q').addEventListener('input', () => {
  cancelAnimationFrame(searchFrame);
  searchFrame = requestAnimationFrame(paintGrid);
});

let columns = columnCount();
for (const [mq] of BREAKPOINTS) {
  mq.addEventListener('change', () => { if (columnCount() !== columns) { columns = columnCount(); paintGrid(); } });
}

// ---- start -------------------------------------------------------------------------------

$('sprite').innerHTML = SPRITE;
loadState();
paintChrome();
paintGrid();
if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').catch(() => {});
