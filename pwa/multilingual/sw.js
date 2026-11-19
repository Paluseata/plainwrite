// Plainwrite service worker: everything is cached on first visit, then served from the device.
const CACHE = 'plainwrite-all-v103';
const CORE = ['./', './index.html', './langs/all.json', './manifest.json', './icon-192.png', './icon-512.png'];
const FONT_CSS = 'https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap';

// Fetch the font stylesheet and every font file it points to, so all typefaces work offline.
async function cacheFonts(cache) {
  for (const url of [FONT_CSS]) await cacheFontCss(cache, url);
}
async function cacheFontCss(cache, FONT_CSS) {
  try {
    const res = await fetch(FONT_CSS, { mode: 'cors' });
    if (!res.ok) return;
    await cache.put(FONT_CSS, res.clone());
    const css = await res.text();
    const urls = [...css.matchAll(/url\((https:[^)]+)\)/g)].map(m => m[1].replace(/['"]/g, ''));
    await Promise.all(urls.map(u =>
      fetch(u, { mode: 'cors' }).then(r => r.ok && cache.put(u, r)).catch(() => {})));
  } catch (e) { /* offline during install: fonts will be cached the next time they load */ }
}

self.addEventListener('install', e => {
  e.waitUntil((async () => {
    const c = await caches.open(CACHE);
    await c.addAll(CORE);
    await c.addAll(['./bedstead.otf', './bedstead-condensed.otf', './plain-sans.ttf', './home-computer.ttf', './home-computer-thin.ttf', './pixel-gothic.ttf', './jost.ttf', './vt323.ttf', './press-start-2p.ttf', './tiny5.ttf', './ibm-plex-mono-medium.ttf', './courier-prime-bold.ttf']).catch(() => {});
    await cacheFonts(c);
  })());
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)));
    await self.clients.claim();
  })());
});

// Cache first, refresh in the background when online.
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  if (/dictionary-|wooorm\/dictionaries/.test(req.url)) return;   // spelling dictionaries are kept by the app itself
  const isNav = req.mode === 'navigate';
  const key = isNav ? './index.html' : req;
  e.respondWith((async () => {
    const cache = await caches.open(CACHE);
    const hit = await cache.match(key);
    if (hit && req.url.startsWith('https://fonts.gstatic.com/')) return hit; // font files never change
    const net = fetch(req).then(res => {
      if (res && (res.ok || res.type === 'opaque')) { const copy = res.clone(); cache.put(key, copy); }
      return res;
    }).catch(() => hit || (isNav ? cache.match('./') : Response.error()));
    if (hit) { e.waitUntil(net.catch(() => {})); return hit; }
    return net;
  })());
});
