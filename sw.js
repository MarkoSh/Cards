// *Fast offline cache. The whole site — page, audio, icons, Tailwind, lucide, Google fonts — keeps working
// without internet. When online, offline.json (every file with a content hash, written by tools/offline.py)
// is compared with the saved copy and only changed files are downloaded again.
// The same file is copied into every *Fast site by tools/offline.py: edit it in ThaiFast/tools.
const CACHE = 'fast-offline';
const scope = new URL(self.registration.scope);
const abs = p => new URL(p, scope).href;
const PAGE = abs('index.html');
const META = abs('offline.json');
const SKIP = /googletagmanager\.com|google-analytics\.com/;   // analytics stay online-only

self.addEventListener('install', e => { self.skipWaiting(); e.waitUntil(sync({ full: false })) });
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));
self.addEventListener('message', e => { if (e.data && e.data.type === 'sync') e.waitUntil(sync(e.data)) });

self.addEventListener('fetch', e => {
  const req = e.request, url = new URL(req.url);
  if (req.method !== 'GET' || SKIP.test(url.hostname) || !/^https?:$/.test(url.protocol)) return;
  if (req.mode === 'navigate' && req.url.startsWith(scope.href)) return e.respondWith(page(req));
  e.respondWith(asset(req));
});

// the page: network first (so a new version shows up at once), the saved copy when offline or slow
async function page(req) {
  const cache = await caches.open(CACHE), path = new URL(req.url).pathname;
  const own = path === scope.pathname || path === new URL(PAGE).pathname;
  try {
    const res = await Promise.race([fetch(req, { cache: 'no-cache' }), new Promise((_, no) => setTimeout(no, 6000))]);
    if (res.ok && own) cache.put(PAGE, res.clone());
    return res;
  } catch (e) {
    return (await cache.match(PAGE)) || Response.error();
  }
}

// everything else: cache first, then the network (and keep what came)
async function asset(req) {
  const cache = await caches.open(CACHE);
  const hit = await cache.match(req.url);
  if (hit) return hit;
  try {
    const res = await fetch(req);
    if ((res.ok && res.status === 200) || res.type === 'opaque') cache.put(req.url, res.clone());
    return res;
  } catch (e) {
    return Response.error();
  }
}

async function report(msg) {
  for (const c of await self.clients.matchAll({ includeUncontrolled: true })) c.postMessage({ type: 'offline', ...msg });
}

let running = null;
function sync(opts) { return running || (running = run(opts || {}).catch(() => report({ offline: true })).finally(() => { running = null })) }

// download what changed (or everything, when full) and drop what was removed
async function run({ full }) {
  const cache = await caches.open(CACHE);
  const res = await fetch(META, { cache: 'no-store' });
  if (!res.ok) throw new Error('no manifest');
  const man = await res.clone().json();
  const old = await cache.match(META).then(r => (r ? r.json() : null)).catch(() => null) || { files: {} };
  const have = new Set((await cache.keys()).map(r => r.url));

  for (const p of Object.keys(old.files || {})) if (!(p in man.files)) await cache.delete(abs(p));

  const jobs = [];
  for (const [p, hash] of Object.entries(man.files)) {
    const u = abs(p), cached = have.has(u);
    if (man.core.includes(p) || (full && !cached) || (cached && old.files[p] !== hash)) jobs.push([u, 'same']);
  }
  for (const u of man.external) if (!have.has(u) || old.version !== man.version) jobs.push([u, 'ext']);

  let done = 0;
  const total = jobs.length;
  await report({ done, total });
  const get = async ([u, kind]) => {
    try {
      let r;
      if (kind === 'same') r = await fetch(u, { cache: 'reload' });
      else { try { r = await fetch(u, { mode: 'cors', cache: 'reload' }) } catch (e) { r = await fetch(u, { mode: 'no-cors' }) } }
      if (r.ok || r.type === 'opaque') {
        await cache.put(u, r.clone());
        // Google Fonts CSS points at the font files: keep them too
        if (/fonts\.googleapis\.com/.test(u) && r.ok) {
          for (const f of new Set((await r.text()).match(/https:\/\/fonts\.gstatic\.com\/[^)'"\s]+/g) || [])) {
            if (!have.has(f)) { const fr = await fetch(f, { mode: 'cors' }); if (fr.ok) await cache.put(f, fr) }
          }
        }
      }
    } catch (e) { /* stays missing; the next sync tries again */ }
    if (++done % 25 === 0 || done === total) report({ done, total });
  };
  const queue = jobs.slice();
  await Promise.all(Array.from({ length: 6 }, async () => { while (queue.length) await get(queue.shift()) }));
  await cache.put(META, res);
  await report({ done: total, total, version: man.version });
}
