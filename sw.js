const CACHE_NAME = 'japan-life-cache-v6';

const urlsToCache = [
  './manifest.json',
  './icon.png',
  './icon-512.png'
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
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

  // GET以外は無視
  if (request.method !== 'GET') return;

  // 自分のサイト以外は無視（超重要）
  if (new URL(request.url).origin !== self.location.origin) {
    return;
  }

  // HTMLは常に最新取得
  if (request.headers.get('accept')?.includes('text/html')) {
    event.respondWith(fetch(request));
    return;
  }

  // それ以外はキャッシュ優先
  event.respondWith(
    caches.match(request).then(cachedResponse => {
      return cachedResponse || fetch(request).then(response => {
        const responseClone = response.clone();
        caches.open(CACHE_NAME).then(cache => {
          cache.put(request, responseClone);
        });
        return response;
      });
    })
  );
});