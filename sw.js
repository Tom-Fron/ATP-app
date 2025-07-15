const CACHE_NAME = 'japan-life-cache'; // 今後は名前を固定にしてOK
const urlsToCache = [
  './',
  './index.html',
  './manifest.json',
  './icon.png',
  './icon-512.png',
  // './tts_audio/〜 なども必要に応じて追加
];

// 即時有効化：インストール後すぐ新バージョンが反映される
self.addEventListener('install', (event) => {
  self.skipWaiting();  // 🔸これが重要
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(urlsToCache))
  );
});

// 古いキャッシュを即時削除し、制御を新SWに移行
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) =>
      Promise.all(
        cacheNames.map((name) => {
          if (name !== CACHE_NAME) {
            return caches.delete(name);
          }
        })
      )
    )
  );
  return self.clients.claim();  // 🔸すぐコントロールするために必要
});

// ネット優先：ネットで取得しつつキャッシュにも保存、失敗時はキャッシュ
self.addEventListener('fetch', (event) => {
  event.respondWith(
    fetch(event.request).then((networkResponse) => {
      return caches.open(CACHE_NAME).then((cache) => {
        cache.put(event.request, networkResponse.clone());
        return networkResponse;
      });
    }).catch(() => {
      return caches.match(event.request);
    })
  );
});
