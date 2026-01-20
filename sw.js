const CACHE_NAME = 'japan-life-cache-v3';

const urlsToCache = [
  './',
  './manifest.json',
  './icon.png',
  './icon-512.png'
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then(names =>
      Promise.all(
        names.map(name => {
          if (name !== CACHE_NAME) {
            return caches.delete(name);
          }
        })
      )
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const request = event.request;

  // GET 以外は触らない
  if (request.method !== 'GET') return;

  // http(s) 以外は触らない
  if (!request.url.startsWith('http')) return;

  // terms.json は常にネットワーク
  if (request.url.includes('terms.json')) {
    event.respondWith(fetch(request));
    return;
  }

  // それ以外は cache-first
  event.respondWith(
    caches.match(request).then(cached => {
      return cached || fetch(request);
    })
  );
});
