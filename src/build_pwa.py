"""index.html(Claude 아티팩트용 원본) → app/ 폴더(독립 웹앱, PWA)로 빌드.
사용: python3 build_pwa.py
"""
import json, os, re, shutil, zipfile, hashlib
from PIL import Image, ImageDraw

SRC = os.path.join(os.path.dirname(__file__), 'claude-artifact.html')
OUT = os.path.join(os.path.dirname(__file__), '..')
os.makedirs(os.path.join(OUT, 'icons'), exist_ok=True)

# ---------- 아이콘 ----------
PAL = ['#e8590c', '#2f9e44', '#1971c2', '#ae3ec9', '#f08c00', '#0c8599']
def icon(size, maskable=False):
    S = 4 * size                       # 4배로 그린 뒤 축소(부드러운 가장자리)
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    bg = (31, 30, 28, 255)
    if maskable: d.rectangle([0, 0, S, S], fill=bg)
    else: d.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.22), fill=bg)
    k = 0.72 if maskable else 1.0      # maskable은 안전 영역 안으로
    c = S / 2
    def P(x, y): return (c + (x - 0.5) * S * k, c + (y - 0.5) * S * k)
    ends = [(0.17, 0.25), (0.83, 0.25), (0.13, 0.62), (0.87, 0.62), (0.32, 0.86), (0.68, 0.86)]
    w = int(S * 0.035 * k)
    for (x, y), col in zip(ends, PAL):
        d.line([P(0.5, 0.52), P(x, y)], fill=col, width=w)
    for (x, y), col in zip(ends, PAL):
        r = S * 0.07 * k; px, py = P(x, y)
        d.ellipse([px - r, py - r, px + r, py + r], fill=col)
    r = S * 0.15 * k; px, py = P(0.5, 0.52)
    d.ellipse([px - r, py - r, px + r, py + r], fill=(246, 245, 242, 255))
    return im.resize((size, size), Image.LANCZOS)

icon(192).save(f'{OUT}/icons/icon-192.png')
icon(512).save(f'{OUT}/icons/icon-512.png')
icon(512, True).save(f'{OUT}/icons/maskable-512.png')
icon(180, True).convert('RGB').save(f'{OUT}/icons/apple-touch-icon.png')
icon(48).save(f'{OUT}/icons/favicon.png')

# ---------- manifest ----------
manifest = {
    "name": "마인드맵", "short_name": "마인드맵",
    "description": "생각을 펼치는 개인용 마인드맵 · 템플릿 · 단어장",
    "lang": "ko", "start_url": "./", "scope": "./", "display": "standalone",
    "background_color": "#f6f5f2", "theme_color": "#f6f5f2",
    "icons": [
        {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
        {"src": "icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}
json.dump(manifest, open(f'{OUT}/manifest.webmanifest', 'w'), ensure_ascii=False, indent=2)

# ---------- index.html ----------
html = open(SRC, encoding='utf-8').read()
head = """<link rel="manifest" href="manifest.webmanifest">
<meta name="theme-color" content="#f6f5f2" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#151515" media="(prefers-color-scheme: dark)">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="마인드맵">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<link rel="icon" type="image/png" href="icons/favicon.png">
</head>"""
assert html.count('</head>') == 1
html = html.replace('</head>', head)

tail = """<div id="installBar" class="pill" style="display:none;position:fixed;left:50%;top:62px;transform:translateX(-50%);z-index:15;padding:6px 6px 6px 14px;gap:8px;font-size:13px;white-space:nowrap">
  <span>앱으로 설치하면 홈 화면에서 바로 열 수 있어요</span>
  <button class="btn primary" id="installYes" style="padding:6px 12px">설치</button>
  <button class="ib" id="installNo" style="width:32px;height:32px" title="닫기">✕</button>
</div>
<script>
/* ===== 독립 웹앱(PWA) 전용 ===== */
if ('serviceWorker' in navigator) {
  addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {}));
}
// 브라우저가 데이터를 함부로 지우지 않도록 요청
if (navigator.storage && navigator.storage.persist) navigator.storage.persist().catch(() => {});
// 설치 안내 (안드로이드 크롬 등)
let deferredInstall = null;
addEventListener('beforeinstallprompt', e => {
  e.preventDefault(); deferredInstall = e;
  try { if (localStorage.getItem('mindmap.installDismissed')) return; } catch {}
  document.getElementById('installBar').style.display = 'flex';
});
document.getElementById('installYes').onclick = async () => {
  document.getElementById('installBar').style.display = 'none';
  if (deferredInstall) { deferredInstall.prompt(); deferredInstall = null; }
};
document.getElementById('installNo').onclick = () => {
  document.getElementById('installBar').style.display = 'none';
  try { localStorage.setItem('mindmap.installDismissed', '1'); } catch {}
};
addEventListener('appinstalled', () => { document.getElementById('installBar').style.display = 'none'; try { toast('설치됐어요'); } catch {} });
</script>
</body>"""
assert html.count('</body>') == 1
html = html.replace('</body>', tail)
open(f'{OUT}/index.html', 'w', encoding='utf-8').write(html)

# ---------- service worker (오프라인) ----------
files = ['./', 'index.html', 'manifest.webmanifest', 'icons/icon-192.png', 'icons/icon-512.png',
         'icons/maskable-512.png', 'icons/apple-touch-icon.png', 'icons/favicon.png']
ver = hashlib.sha1(html.encode()).hexdigest()[:10]
sw = f"""// 오프라인 캐시 — 버전 {ver}
const CACHE = 'mindmap-{ver}';
const SHELL = {json.dumps(files)};
self.addEventListener('install', e => {{
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
}});
self.addEventListener('activate', e => {{
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('mindmap-') && k !== CACHE && k !== 'mindmap-fonts').map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
}});
self.addEventListener('fetch', e => {{
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  // 글꼴: 한 번 받으면 캐시에서
  if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {{
    e.respondWith(caches.open('mindmap-fonts').then(async c => {{
      const hit = await c.match(req); if (hit) return hit;
      try {{ const res = await fetch(req); if (res.ok || res.type === 'opaque') c.put(req, res.clone()); return res; }}
      catch {{ return new Response('', {{ status: 504 }}); }}
    }}));
    return;
  }}
  if (url.origin !== location.origin) return;
  // 앱 화면: 네트워크 우선(최신 버전), 안 되면 캐시
  if (req.mode === 'navigate') {{
    e.respondWith(fetch(req).then(res => {{ caches.open(CACHE).then(c => c.put('index.html', res.clone())); return res; }})
      .catch(() => caches.match('index.html')));
    return;
  }}
  e.respondWith(caches.match(req).then(hit => hit || fetch(req)));
}});
"""
open(f'{OUT}/sw.js', 'w', encoding='utf-8').write(sw)

# ---------- 안내 ----------
readme = """# mapnote — 마인드맵 웹앱

주소: https://umlongsilver.github.io/mapnote/

Claude 로그인 없이 쓰는 독립 웹앱(PWA)입니다. 인터넷이 없어도 열리고, 홈 화면에 앱처럼 설치할 수 있어요.

## 올리는 법 (GitHub Pages, 무료)
1. github.com 에서 새 저장소(Repository)를 만듭니다. 예: mapnote
2. 이 폴더 안의 파일을 모두 그대로 올립니다. (Add file → Upload files → index.html, manifest.webmanifest, sw.js, icons 폴더)
3. 저장소 Settings → Pages → Branch를 main / (root)로 고르고 Save
4. 1~2분 뒤 https://<내아이디>.github.io/mapnote/ 에서 열립니다.

## 설치
- 안드로이드(크롬): 주소를 열면 위쪽에 “설치” 안내가 떠요. 안 뜨면 ⋮ 메뉴 → “앱 설치” 또는 “홈 화면에 추가”.
- 아이폰(사파리): 공유 버튼 → “홈 화면에 추가”.
- PC(크롬·엣지): 주소창 오른쪽 설치 아이콘.

## 데이터
- 데이터는 그 기기의 브라우저 안에만 저장돼요. (기기끼리 자동 동기화 없음)
- 왼쪽 위 목록 메뉴 → “전체 백업”으로 파일을 저장해 두고, 다른 기기에서 “파일 가져오기”로 불러오세요.
- 브라우저의 “사이트 데이터 삭제”를 하면 지워지니 가끔 백업해 두세요.

## 수정
- 루트의 index.html은 빌드 결과물입니다. 원본은 src/claude-artifact.html이고, `python3 src/build_pwa.py`로 다시 만듭니다.
"""
open(f'{OUT}/README.md', 'w', encoding='utf-8').write(readme)

# ---------- zip ----------
zp = None
print('built', os.path.abspath(OUT), 'version', ver)
