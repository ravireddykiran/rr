// Minimal service worker: makes the player installable as an app and keeps
// the shell (not the video) available offline. Streams always go to the network.
const CACHE = 'free-tv-shell-v1';
const SHELL = ['./', './index.html', './hls.min.js', './manifest.webmanifest', './icon.svg'];
self.addEventListener('install', (e) => { e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener('activate', (e) => { e.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  if (url.origin !== location.origin) return; // never touch stream traffic
  e.respondWith(fetch(e.request).then((res) => { if (res.ok && e.request.method === 'GET') caches.open(CACHE).then((c) => c.put(e.request, res.clone())); return res; }).catch(() => caches.match(e.request)));
});
