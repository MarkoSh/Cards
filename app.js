// Cards: your own Instagram of the most frequent nouns and verbs in Russian, English and Thai.
// You pick the language you know (base) and the deck you study (target). A post is a photo and the deck word;
// a tap opens the translation, transcription, example and voice. The heart means "I know it" and fades after 30 days.
// Data: CONCEPTS (data.js), EXAMPLES (examples.js), PHOTOS (photos.js), SPRITE (icons/sprite.js); built by tools/.

const LANGS = ['ru', 'en', 'th'];
const CODE = { ru: 'RU', en: 'EN', th: 'TH' };
const FIELD = { ru: 'r', en: 'e', th: 't' };   // concept field holding the word of each language
const DECK_SIZE = 1000;
const NO_RANK = 1e9;      // words missing from a frequency list go to the end of the deck
const STORAGE_KEY = 'cards';

const TEXT = {
  ru: {
    title: 'Cards — слова как в инстаграме', search: 'Поиск…', empty: 'Ничего не найдено',
    n: 'Существительные', v: 'Глаголы', p: 'Местоимения', all: 'Все', copy: 'Копировать', example: 'Пример', copied: 'Скопировано', translate: 'Google Переводчик',
    share: 'Поделиться карточкой', like: 'Выучил', recall: 'Забыл? Вспомнил — нажмите ещё раз', listen: 'Послушать', known: 'выучено', recallN: 'пора вспомнить',
    description: 'До 1000 частотных существительных и глаголов английского, русского и тайского в карточках с иконками, транскрипцией и переводом.',
    credits: 'Иконки: {openmoji} (CC BY-SA 4.0). Частотность: wordfreq (en/ru), Thai National Corpus (th). Переводы подобраны вручную.',
    projects: 'Другие проекты:',
  },
  en: {
    title: 'Cards — vocabulary in cards', search: 'Search…', empty: 'Nothing found',
    n: 'Nouns', v: 'Verbs', p: 'Pronouns', all: 'All', copy: 'Copy', example: 'Example', copied: 'Copied', translate: 'Google Translate',
    share: 'Share this card', like: 'I know it', recall: 'Forgot? Recalled it — tap again', listen: 'Listen', known: 'learned', recallN: 'to recall',
    description: 'Up to 1000 frequent nouns and verbs in English, Russian and Thai, with icons, transcriptions and translations.',
    credits: 'Icons: {openmoji} (CC BY-SA 4.0). Frequency: wordfreq (en/ru), Thai National Corpus (th). Translations curated by hand.',
    projects: 'Other projects:',
  },
  th: {
    title: 'Cards — เรียนคำศัพท์ด้วยบัตรคำ', search: 'ค้นหา…', empty: 'ไม่พบคำที่ค้นหา',
    n: 'คำนาม', v: 'คำกริยา', p: 'สรรพนาม', all: 'ทั้งหมด', copy: 'คัดลอก', example: 'ตัวอย่าง', copied: 'คัดลอกแล้ว', translate: 'Google แปลภาษา',
    share: 'แชร์การ์ดนี้', like: 'จำได้แล้ว', recall: 'ลืมแล้ว? นึกออกแล้วกดอีกครั้ง', listen: 'ฟัง', known: 'จำได้', recallN: 'ควรทบทวน',
    description: 'คำนามและคำกริยาที่พบบ่อยสูงสุดภาษาละ 1,000 คำ ในภาษาอังกฤษ รัสเซีย และไทย พร้อมไอคอน การถอดเสียง และคำแปล',
    credits: 'ไอคอน: {openmoji} (CC BY-SA 4.0) · ความถี่คำ: wordfreq (en/ru), Thai National Corpus (th) · คำแปลคัดสรรด้วยตนเอง',
    projects: 'โครงการอื่น:',
  },
};

const ICON = {   // lucide, 24x24
  quote: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/><path d="M8 9h8"/><path d="M8 13h5"/>',
  share: '<path d="M14.536 21.686a.5.5 0 0 0 .937-.024l6.5-19a.496.496 0 0 0-.635-.635l-19 6.5a.5.5 0 0 0-.024.937l7.93 3.18a2 2 0 0 1 1.112 1.11z"/><path d="m21.854 2.147-10.94 10.939"/>',
  copy: '<rect width="14" height="14" x="8" y="8" rx="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>',
  check: '<path d="M20 6 9 17l-5-5"/>',
  heart: '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>',
  volume: '<path d="M11 4.702a.705.705 0 0 0-1.203-.498L6.413 7.587A1.4 1.4 0 0 1 5.416 8H3a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h2.416a1.4 1.4 0 0 1 .997.413l3.383 3.384A.705.705 0 0 0 11 19.298z"/><path d="M16 9a5 5 0 0 1 0 6"/><path d="M19.364 18.364a9 9 0 0 0 0-12.728"/>',
  translate: '<path d="m5 8 6 6"/><path d="m4 14 6-6 2-3"/><path d="M2 5h12"/><path d="M7 2h1"/><path d="m22 22-5-10-5 10"/><path d="M14 18h6"/>',
};
const icon = (name, size = 'size-5') => `<svg class="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICON[name]}</svg>`;

const $ = id => document.getElementById(id);
const esc = s => s.replace(/[&<>"]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch]));
const norm = s => s.toLowerCase().replace(/ё/g, 'е');
const otherLangs = lang => LANGS.filter(l => l !== lang);

// ---- state -------------------------------------------------------------------------------

const state = { base: 'ru', target: 'en', pos: 'n' };

function loadState() {
  let saved = {};
  try { saved = JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}; } catch (e) {}
  if (LANGS.includes(saved.base)) state.base = saved.base;
  if (otherLangs(state.base).includes(saved.target)) state.target = saved.target;
  else state.target = otherLangs(state.base)[0];
  if (['n', 'v', 'p', 'a'].includes(saved.pos)) state.pos = saved.pos;
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
  if (!decks.has(key)) decks.set(key, state.pos === 'a' ? [...deckOf('p'), ...mix(['n', 'v'].map(deckOf))] : deckOf(state.pos));
  return decks.get(key);
}

function deckOf(pos) {
  const field = FIELD[state.target], seen = new Set();
  return CONCEPTS
    .map((c, i) => ({ c, i, rank: c.k?.[state.target] ?? NO_RANK, en: c.k?.en ?? NO_RANK }))
    .filter(x => x.c.p === pos)
    // synonyms share a rank when they share a translation: the commonest English sense goes first
    .sort((a, b) => a.rank - b.rank || a.en - b.en || a.i - b.i)
    .map(x => x.c)
    // one card per deck word
    .filter(c => !seen.has(c[field]) && seen.add(c[field]))
    .slice(0, DECK_SIZE);
}

// lists shuffled together (pronouns, the most frequent words, open the 'All' deck); each list keeps its own frequency order (fixed seed: the same wall every time)
function mix(lists) {
  let seed = 7;
  const random = () => { seed = (seed + 0x6D2B79F5) | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  const at = lists.map(() => 0), out = [];
  for (let left = lists.reduce((n, l) => n + l.length, 0); left; left--) {
    // the next card comes from a list with probability proportional to what it has left
    let pick = random() * left;
    const i = lists.findIndex((l, j) => (pick -= l.length - at[j]) < 0);
    out.push(lists[i][at[i]++]);
  }
  return out;
}

// ---- likes: "I know this word"; a like is red for 30 days, then fades to grey (known once, time to recall) --------

const LIKE_KEY = 'cards-likes', LIKE_DAYS = 30;
let likes = {};
try { likes = JSON.parse(localStorage.getItem(LIKE_KEY)) || {}; } catch (e) {}
const likeKey = c => `${state.target}:${c.p}:${c.e}`;
const likeState = c => { const at = likes[likeKey(c)]; return !at ? '' : Date.now() - at < LIKE_DAYS * 864e5 ? 'on' : 'old'; };
function setLike(c, on) {
  if (on) likes[likeKey(c)] = Date.now(); else delete likes[likeKey(c)];
  try { localStorage.setItem(LIKE_KEY, JSON.stringify(likes)); } catch (e) {}
}

// ---- voice: audio/<lang>/<fnv1a(word)>.mp3, else the browser voice -------------------------

const fnv = str => { let h = 0x811c9dc5; for (const b of new TextEncoder().encode(str)) { h ^= b; h = Math.imul(h, 0x01000193) >>> 0; } return h.toString(16).padStart(8, '0'); };
const player = new Audio();
function speak(text, lang) {
  player.onerror = () => {
    if (!('speechSynthesis' in window)) return;
    speechSynthesis.cancel();
    speechSynthesis.speak(Object.assign(new SpeechSynthesisUtterance(text.replace(/\[|\]/g, '')), { lang: { ru: 'ru-RU', en: 'en-US', th: 'th-TH' }[lang], rate: .9 }));
  };
  player.src = `audio/${lang}/${fnv(text)}.mp3`;
  player.play().catch(() => {});
}

// ---- cards -------------------------------------------------------------------------------

const photoOf = c => PHOTOS.has(c.p + c.e) ? `photos/${c.p}-${c.e.replace(/\W+/g, '-')}.webp` : '';

// until a photo exists the post shows the old pictogram (or the first letter) on a dark square
function media(c) {
  const photo = photoOf(c);
  if (photo) return `<img class="size-full object-cover" src="${photo}" alt="" loading="lazy" decoding="async">`;
  if (c.g) return `<svg class="size-1/3 text-amber-400" aria-hidden="true"><use href="#i-${c.g}"/></svg>`;
  const word = c[FIELD[state.target]];
  const letter = (state.target === 'th' && word.match(/[ก-ฮ]/)?.[0]) || [...word][0];
  return `<span class="flex size-1/3 items-center justify-center rounded-full border-2 border-amber-400/50 text-5xl font-semibold text-amber-400 font-word" aria-hidden="true">${esc(letter)}</span>`;
}

// five bars: how common the word is (rank in the frequency list of the deck language)
function frequency(c) {
  const rank = c.k?.[state.target];
  const lit = !rank ? 0 : rank <= 50 ? 5 : rank <= 200 ? 4 : rank <= 500 ? 3 : rank <= 1000 ? 2 : 1;
  const bars = [0, 1, 2, 3, 4].map(i =>
    `<span class="w-0.5 rounded-full ${i < lit ? 'bg-amber-400' : 'bg-zinc-700'}" style="height:${4 + i * 2}px"></span>`).join('');
  return `<span class="flex items-end gap-px" ${rank ? `title="#${rank}"` : ''} aria-hidden="true">${bars}</span>`;
}

const transcription = c => (state.target === 'en' ? c.i : state.target === 'th' ? c.x : '') || '';

// [verb] in a sample sentence -> highlighted verb
const mark = text => esc(text).replace(/\[(.+?)\]/, '<b class="text-amber-400">$1</b>');

// a short sentence with the word, like the first comment under the photo
function example(c) {
  const ex = EXAMPLES[c.p === 'v' ? c.e : c.p + ':' + c.e];
  if (!ex) return '';
  const [en, ru, th, roman] = ex, sentence = { en, ru, th };
  return `<div class="mt-2 border-t border-zinc-800 pt-2">
    <p class="flex items-start gap-2"><b class="shrink-0 text-zinc-500">${CODE[state.target].toLowerCase()}</b><span class="font-word">${mark(sentence[state.target])}</span>
      <button type="button" class="speak-ex ml-auto shrink-0 text-zinc-500 hover:text-amber-400" data-text="${esc(sentence[state.target])}" aria-label="${TEXT[state.base].listen}">${icon('volume')}</button></p>
    ${state.target === 'th' ? `<p class="pl-6 text-xs text-zinc-500">${esc(roman)}</p>` : ''}
    <p class="mt-1 flex gap-2 text-zinc-400"><b class="shrink-0 text-zinc-600">${CODE[state.base].toLowerCase()}</b><span>${mark(sentence[state.base])}</span></p>
  </div>`;
}

function heart(c) {
  const st = likeState(c), t = TEXT[state.base];
  return `<button type="button" class="like action ${st ? 'like-' + st : ''}" aria-pressed="${st === 'on'}" title="${st === 'old' ? t.recall : t.like}" aria-label="${t.like}">${icon('heart', 'size-6')}</button>`;
}

function card(c) {
  const t = TEXT[state.base], word = c[FIELD[state.target]], tr = transcription(c);
  const url = `https://translate.google.com/?sl=${state.target}&tl=${state.base}&text=${encodeURIComponent(word)}&op=translate`;
  return `<article class="post overflow-hidden border border-zinc-800 bg-zinc-900 sm:rounded-lg" data-id="${c.p}:${c.e}">
  <header class="flex items-center gap-2 px-3 py-2 text-xs text-zinc-400">
    <span class="flex size-7 items-center justify-center rounded-full bg-amber-400 text-[10px] font-bold text-zinc-950">${CODE[state.target]}</span>
    <span class="font-semibold text-zinc-200">${t[c.p]}</span>
    <span class="ml-auto flex items-center gap-2">${c.k?.[state.target] ? `#${c.k[state.target]}` : ''}${frequency(c)}</span>
  </header>
  <button type="button" class="reveal media relative flex aspect-square w-full select-none items-center justify-center overflow-hidden bg-gradient-to-br from-zinc-900 to-zinc-800" aria-expanded="false" aria-label="${esc(word)}">
    ${media(c)}
    <span class="burst pointer-events-none absolute inset-0 flex items-center justify-center text-red-500">${icon('heart', 'size-24 fill-current')}</span>
  </button>
  <div class="flex items-center gap-3 px-3 pt-2.5">
    ${heart(c)}
    <button type="button" class="speak action" data-text="${esc(word)}" title="${t.listen}" aria-label="${t.listen}">${icon('volume', 'size-6')}</button>
    <a class="action" href="${url}" target="_blank" rel="noopener" title="${t.translate}" aria-label="${t.translate}">${icon('translate', 'size-6')}</a>
    <button type="button" class="share action" title="${t.share}" aria-label="${t.share}">${icon('share', 'size-6')}</button>
    <button type="button" class="copy action ml-auto" data-word="${esc(word)}" title="${t.copy}" aria-label="${t.copy}">${icon('copy', 'size-6')}</button>
  </div>
  <div class="px-3 pb-3 pt-1.5">
    <button type="button" class="reveal caption block w-full text-left" aria-expanded="false">
      <span class="font-word ${state.target === 'th' ? 'text-2xl' : 'text-xl'} font-semibold leading-snug">${esc(word)}</span>
      ${tr ? `<span class="ml-2 text-sm text-zinc-500">${esc(tr)}</span>` : ''}
    </button>
    <div class="more"><div class="overflow-hidden text-sm"><p class="mt-1 text-base text-zinc-300">${esc(c[FIELD[state.base]])}</p>${example(c)}</div></div>
  </div>
</article>`;
}

// ---- feed: one column like Instagram on a phone, three on a big screen ---------------------

const byId = new Map(CONCEPTS.map(c => [c.p + ':' + c.e, c]));

function paintStats(items) {
  const known = items.filter(c => likeState(c) === 'on').length, old = items.filter(c => likeState(c) === 'old').length, t = TEXT[state.base];
  const label = `${known} / ${items.length} ${t.known}${old ? ` · ${old} ${t.recallN}` : ''}`;
  $('stats').title = label;
  $('stats').setAttribute('aria-label', label);
  $('stats').innerHTML = `<span class="text-red-500">${icon('heart', 'size-4 fill-current')}</span><b>${known}</b><span class="text-zinc-500">/ ${items.length}</span>
    <span class="h-1 w-14 overflow-hidden rounded-full bg-zinc-800"><span class="block h-full bg-red-500" style="width:${known / items.length * 100}%"></span></span>${old ? `<span class="text-zinc-500">${icon('heart', 'size-4 fill-current')}</span><span class="text-zinc-500">${old}</span>` : ''}`;
}

function paintGrid() {
  const q = norm($('q').value.trim());
  const items = deck().filter(c => !q || c.s.includes(q));
  $('grid').innerHTML = items.map(card).join('');
  $('empty').classList.toggle('hidden', items.length > 0);
  paintStats(deck());
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
  segment($('pos'), [['a', t.all], ['n', t.n], ['v', t.v], ['p', t.p]], state.pos);
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

// the button shows a check mark for a second
function flash(btn) {
  const html = btn.innerHTML, label = btn.title;
  btn.innerHTML = icon('check', 'size-6');
  btn.dataset.done = '';
  setLabel(btn, TEXT[state.base].copied);
  setTimeout(() => { btn.innerHTML = html; delete btn.dataset.done; setLabel(btn, label); }, 1000);
}

// ---- share link: #<base>-<deck>-<n|v>-<english word> opens that deck, scrolls to the card and lights it ----

const shareUrl = c => `${location.origin === 'null' ? 'file://' : location.origin}${location.pathname}#${state.base}-${state.target}-${c.p}-${encodeURIComponent(c.e)}`;

function applyHash() {
  let m;
  try { m = decodeURIComponent(location.hash.slice(1)).match(/^(ru|en|th)-(ru|en|th)-([nvp])-(.+)$/); } catch (e) {}
  if (!m || m[1] === m[2] || !byId.has(m[3] + ':' + m[4])) return false;
  $('q').value = '';
  Object.assign(state, { base: m[1], target: m[2], pos: m[3] });
  paintChrome();
  paintGrid();
  const post = $('grid').querySelector(`[data-id="${CSS.escape(m[3] + ':' + m[4])}"]`);
  if (!post) return true;
  post.classList.add('shared');
  // posts below the screen are not rendered yet (content-visibility), so aim again once the layout settles
  post.scrollIntoView({ block: 'center' });
  setTimeout(() => post.scrollIntoView({ block: 'center' }), 250);
  return true;
}
window.addEventListener('hashchange', applyHash);

$('grid').addEventListener('click', e => {
  const post = e.target.closest('.post');
  if (!post) return;
  const c = byId.get(post.dataset.id), lang = state.target;
  const copy = e.target.closest('.copy'), share = e.target.closest('.share');
  if (copy) {
    copyText(copy.dataset.word).then(() => flash(copy)).catch(() => {});
  } else if (share) {
    const url = shareUrl(c), word = c[FIELD[state.target]];
    (navigator.share ? navigator.share({ title: word, url }) : copyText(url).then(() => flash(share)))
      .catch(err => { if (err?.name !== 'AbortError') copyText(url).then(() => flash(share)).catch(() => {}); });
  } else if (e.target.closest('.speak, .speak-ex')) {
    const b = e.target.closest('.speak, .speak-ex');
    speak(b.dataset.text, lang);
  } else if (e.target.closest('.like')) {
    setLike(c, likeState(c) !== 'on');
    paintLike(post, c);
  } else if (e.target.closest('.reveal')) {
    const open = post.classList.toggle('open');
    post.querySelectorAll('.reveal').forEach(b => b.setAttribute('aria-expanded', open));
  }
});

// double tap on the photo likes it (never un-likes), with the heart burst
$('grid').addEventListener('dblclick', e => {
  const media = e.target.closest('.media');
  if (!media) return;
  const post = media.closest('.post'), c = byId.get(post.dataset.id);
  setLike(c, true);
  paintLike(post, c);
  media.classList.remove('burst-on');
  void media.offsetWidth;
  media.classList.add('burst-on');
});

function paintLike(post, c) {
  post.querySelector('.like').outerHTML = heart(c);
  paintStats(deck());
}

$('base').addEventListener('click', e => { const b = e.target.closest('button'); if (b) setState({ base: b.dataset.value }); });
$('target').addEventListener('click', e => { const b = e.target.closest('button'); if (b) setState({ target: b.dataset.value }); });
$('pos').addEventListener('click', e => { const b = e.target.closest('button'); if (b) setState({ pos: b.dataset.value }); });

let searchFrame = 0;
$('q').addEventListener('input', () => {
  cancelAnimationFrame(searchFrame);
  searchFrame = requestAnimationFrame(paintGrid);
});

// ---- start -------------------------------------------------------------------------------

$('sprite').innerHTML = SPRITE;
loadState();
if (!applyHash()) { paintChrome(); paintGrid(); }
if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').catch(() => {});
