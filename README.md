# mapnote — 마인드맵 웹앱

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
