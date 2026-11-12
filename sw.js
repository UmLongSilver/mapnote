// 오프라인 캐시 — 버전 ebe884fe7e
const CACHE = 'mindmap-ebe884fe7e';
const SHELL = ["./", "index.html", "manifest.webmanifest", "icons/icon-192.png", "icons/icon-512.png", "icons/maskable-512.png", "icons/apple-touch-icon.png", "icons/favicon.png"];
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('mindmap-') && k !== CACHE && k !== 'mindmap-fonts').map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  // 글꼴: 한 번 받으면 캐시에서
  if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {
    e.respondWith(caches.open('mindmap-fonts').then(async c => {
      const hit = await c.match(req); if (hit) return hit;
      try { const res = await fetch(req); if (res.ok || res.type === 'opaque') c.put(req, res.clone()); return res; }
      catch { return new Response('', { status: 504 }); }
    }));
    return;
  }
  if (url.origin !== location.origin) return;
  // 앱 화면: 네트워크 우선(최신 버전), 안 되면 캐시
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).then(res => { caches.open(CACHE).then(c => c.put('index.html', res.clone())); return res; })
      .catch(() => caches.match('index.html')));
    return;
  }
  e.respondWith(caches.match(req).then(hit => hit || fetch(req)));
});
