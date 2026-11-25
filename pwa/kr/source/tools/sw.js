// Plainwrite-K service worker: everything is cached on first visit, then served from the device.
const CACHE = 'plainwrite-k-v01';
const CORE = ['./', './index.html', './manifest.json', './icon-192.png', './icon-512.png', './dict-ko.txt'];
self.addEventListener('install', e => {
  e.waitUntil((async () => {
    const c = await caches.open(CACHE);
    await c.addAll(CORE);
    await c.addAll([%FONTS%]).catch(() => {});
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
    const net = fetch(req).then(res => {
      if (res && (res.ok || res.type === 'opaque')) { const copy = res.clone(); cache.put(key, copy); }
      return res;
    }).catch(() => hit || (isNav ? cache.match('./') : Response.error()));
    if (hit) { e.waitUntil(net.catch(() => {})); return hit; }
    return net;
  })());
});
