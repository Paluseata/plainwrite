// Plainwrite-K service worker: everything is cached on first visit, then served from the device.
const CACHE = 'plainwrite-k-ko-v01';
const CORE = ['./', './index.html', './manifest.json', './icon-192.png', './icon-512.png', './dict-ko.txt'];
self.addEventListener('install', e => {
  e.waitUntil((async () => {
    const c = await caches.open(CACHE);
    await c.addAll(CORE);
    await c.addAll(['./bedstead.otf', './bedstead-condensed.otf', './plain-sans.ttf', './home-computer.ttf', './home-computer-thin.ttf', './jost.ttf', './vt323.ttf', './press-start-2p.ttf', './tiny5.ttf', './ibm-plex-mono-medium.ttf', './courier-prime-bold.ttf', './share-tech-mono.ttf', './pixel-gothic.ttf', './hanja-fallback.woff', './logo-k.woff', './ui-ko-400.woff', './ui-ko-500.woff', './ui-ko-700.woff', './neodgm.woff', './jeongeum.woff']).catch(() => {});
  })());
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    // Only clear this edition's own old caches: the other editions on the same site keep theirs.
    const mine = CACHE.replace(/-v[\d.]+(-\d+)?$/, '-v');
    await Promise.all(keys.filter(k => k !== CACHE && k.startsWith(mine)).map(k => caches.delete(k)));
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
    const net = fetch(req).then(res => {
      if (res && (res.ok || res.type === 'opaque')) { const copy = res.clone(); cache.put(key, copy); }
      return res;
    }).catch(() => hit || (isNav ? cache.match('./') : Response.error()));
    if (hit) { e.waitUntil(net.catch(() => {})); return hit; }
    return net;
  })());
});
