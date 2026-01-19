const CACHE_NAME = 'japan-life-cache-v1';

const urlsToCache = [
  './',
  './index.html',
  './manifest.json',
  './icon.png',
  './icon-512.png'
];

// インストール時：基本ファイルのみキャッシュ
self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(urlsToCache);
    })
  );
});

// アクティベート時：古いキャッシュ削除
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((name) => {
          if (name !== CACHE_NAME) {
            return caches.delete(name);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// フェッチ処理
self.addEventListener('fetch', (event) => {

  // 利用規約（terms.json）は必ずネットワークから取得
  if (event.request.url.includes('terms.json')) {
    return;
  }

  // GET 以外は処理しない
  if (event.request.method !== 'GET') {
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      return cachedResponse || fetch(event.request);
    })
  );
});
