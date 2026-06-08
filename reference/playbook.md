# Storyboard 화면설계서 — Playbook (deep reference)

SKILL.md 의 단계별 상세판. "side-by-side 스토리보드식 화면설계서"를 **어떤 도메인에서도** 재현하는 방법.

산출물 한 줄 정의: 화면 1개 = 페이지 1개. **왼쪽 = 화면 이미지(스크린샷/Figma export/렌더 캡처) + 번호 콜아웃**, **오른쪽 = 요소별 설명표(동작·데이터·예외)를 진짜 HTML 텍스트로**. 그리고 썸네일 카드 **보드(index)** 가 각 페이지로 링크. (스토리보드 본래 형태: 좌 = 화면 그림, 우 = 텍스트 설명.)

**두 가지 모드 (동등 지원) — UI가 이미 있는지로 정한다:**
- **모드 B — 기획**: 화면이 아직 없음 → `sb-` 박스로 **와이어프레임**을 그려 설계한다. 문서가 곧 설계 산출물. 요소는 기획 의도에서 정의.
- **모드 A — 문서화**: 구현된/Figma 화면이 있음 → 실제 마크업·CSS(또는 Figma export)로 **픽셀 재현**. 요소는 코드/디자인에서 추출.

이 스킬은 **화면설계 산출물 생성기**이지 Figma 임포터가 아니다. Figma 소스는 모드 A의 한 입력일 뿐이며, MCP가 없으면 `figma-cli`로 끌어온다 (§8).

---

## 0. 스코프 확정 (먼저)

비개발자(기획·QA)와 API 개발자가 같이 보는 문서다. 만들기 전에 정한다:
- **화면 세트**: 어떤 화면/상태를 페이지로 만들지. 단일 페이지 앱이면 "상태"가 곧 화면이다 (예: READY / RECORDING / RESULT / ERROR). 화면 흐름(선행→후행) 순서로 나열.
- **모드 결정**: 화면이 이미 있는가? 없으면 **모드 B**(와이어프레임 = 기획), 있으면 **모드 A**(실제 CSS 재사용, 또는 Figma 소스 → §8).
- **출력 위치**: 보통 대상 앱 폴더 하위에 `design-specs/` (대상 CSS를 `../`로 상대링크하기 좋음).
- 분기(범위/포맷/상세명세 동반 여부)가 갈리면 **AskUserQuestion 으로 확정** 후 진행.

---

## 1. 요소 추출 (화면마다)

화면의 **상호작용 요소**를 빠짐없이 뽑는다 — 모드 A는 코드/디자인을 읽어 추출, 모드 B는 기획 의도에서 정의. 요소 하나당:
- **요소명 / DOM id(또는 selector·컴포넌트명)** — 개발자가 짚을 수 있게.
- **동작/이벤트** — 클릭/입력 시 무엇이 호출되나 (함수·API·상태전이).
- **데이터 계약** — 입력/출력 필드, 타입, 페이로드 (API 개발에 직접 쓰임).
- **상태** — 이 요소가 가지는 상태값(enabled/disabled, 상태라벨 등).
- **예외/폴백** — 실패·권한거부·빈값·오프라인 처리.

코드베이스가 크면 서브에이전트로 서브시스템별 사실 추출을 병렬화한다(파일 덤프 말고 distilled fact sheet 회수).

---

## 2. 화면 만들기 (왼쪽 pane)

§0에서 정한 모드로 고른다 — 둘은 우열이 아니라 용도가 다르다(B=설계, A=문서화).

### 모드 A — 문서화 (픽셀 일치)
**본래 형태**: 왼쪽 `.sb-screen` 에 화면을 **이미지(`<img>`)로** 깐다 — 스크린샷 또는 Figma export. 그 위에 `absolutePositioning`/좌표대로 `.sb-cue` 를 절대배치한다(부모 `position:relative`). Figma 소스면 §8 의 `figma-cli` 로 export 이미지/스펙을 먼저 확보한다.

**옵션(라이브 재현)**: 픽셀 정합을 코드로 보장하고 싶으면 대상 앱의 **진짜 마크업/클래스를 그대로** `.sb-screen` 안에 붙이고 **진짜 CSS를 상대경로로 링크**한다. 그러면 왼쪽이 실제 화면과 똑같이 렌더된다. (어느 쪽이든 좌측은 "화면 그림", 우측은 진짜 HTML 텍스트 표.)

```html
<link rel="stylesheet" href="../styles.css" />   <!-- 대상 앱 진짜 CSS 먼저 -->
<link rel="stylesheet" href="./storyboard.css" /> <!-- chrome 나중 -->
```
- 동적 상태(점수 채워짐, 미터 활성 등)는 대표값으로 하드코딩해 그 상태를 보여준다.
- 진행바 등 폭은 인라인 `style="width:80%"` 로 고정.

### 모드 B — 와이어프레임 (기획 · 화면 설계)
화면이 아직 없으니 storyboard.css 의 sb- 클래스로 박스/버튼/필드를 직접 만들어 화면을 **설계**한다. 기획 단계 산출물로 충분하다 — 어떤 요소가 어디 있고 무엇을 하는지 전달하면 그대로 구현 명세가 된다.

### 콜아웃(번호 마커) 달기
주석 달 요소마다:
1. 그 요소에 `class="... sb-mark"` 추가 (position:relative 가 됨)
2. 그 자식으로 `<span class="sb-cue">N</span>` 삽입 — 왼쪽 위 모서리에 빨강 원으로 붙음
3. 오른쪽 위에 붙이려면 `class="sb-cue r"`

---

## 3. 설명표 (오른쪽 pane)

오른쪽 pane 은 **진짜 HTML 텍스트**여야 한다 — 캡처 이미지로 굽지 말 것(검색·복사·접근성·diff 가능해야 한다). 좌측 화면 이미지와 대비되는, 스토리보드의 텍스트 절반이다.

`table.sb-notes` 5열: **No / 구역 / 요소·ID / 설명·동작·데이터·예외**. cue 번호와 1:1 대응.
마지막 열에서 태그로 종류 구분:
- `tag ev` 이벤트/동작 · `tag dt` 데이터/계약 · `tag ex` 예외 · `tag st` 상태

비개발자용 한 줄 설명 + 개발자용 계약(필드/엔드포인트/공식)을 한 칸에 같이 담되, 계약은 태그로 묶어 시각 분리.

---

## 4. 보드(index) + 썸네일

`board-index.html` 복제. 화면마다 `.sb-card` (썸네일 img + 상태배지 + 제목 + 한줄 + "스토리보드 열기"). 흐름 순서대로 배치.
썸네일은 `scripts/shoot.sh <dir>` 로 `thumbs/`에 생성(좁은 폭 → 1열 → 화면 위주 미리보기).
(옵션) 두 번째 그룹에 API "상세 명세" 카드를 둘 수 있음 — 6절 참고.

---

## 5. ⚠ 함정 (반드시 지킬 것 — 실전에서 깨졌던 것들)

1. **콜아웃 <span>이 대상 앱 규칙에 덮어써짐.** 대상 CSS에 `.field span{display:block}`, `.meter span{background;border-radius}` 같은 규칙이 있으면 cue 가 사각형/왼쪽정렬로 깨진다. → `storyboard.css`의 `.sb-cue`는 `display/width/height/background/border-radius/color/font` 에 **`!important`**를 건다. 이 블록을 지우거나 약화하지 말 것.
2. **`<table>` 직속 자식 `<span>` 금지.** `<table><span class=sb-cue>` 는 브라우저가 테이블 밖으로 밀어내(foster parenting) 위치가 깨진다. → `<table>`을 `<div class="sb-mark">`로 감싸고 cue 를 그 div 의 자식으로.
3. **CSS 링크 순서**: 대상 앱 CSS → storyboard.css 순. (chrome이 나중에 와야 cue 가 이김)
4. **콜아웃이 모서리에서 잘림**: `.sb-screen` 의 padding(기본 22/20px)이 마커 여유. 패딩을 0으로 만들지 말 것.
5. **상대경로**: 대상 CSS·썸네일 경로가 출력 폴더 기준으로 맞는지(`../styles.css`, `./thumbs/...`).

---

## 6. (옵션) 상세 명세 동반

스토리보드는 "화면+요소"가 중심이라, API 계약을 더 깊게 적고 싶으면 별도 **상세 명세 문서**를 곁들이고 보드 ②그룹에서 링크한다. 형식은 자유(섹션형 HTML/MD). 스토리보드의 각 cue 설명에서 해당 명세로 링크하면 비개발↔개발이 자연스럽게 이어진다.

---

## 7. 검증 루프 (claim 전에)

```bash
# macOS / Linux / Git Bash / WSL
scripts/shoot.sh <design-specs-dir>            # 썸네일 생성(=검증샷)
scripts/shoot.sh <dir> sb-01-xxx.html          # 한 장 전체폭

# Windows 네이티브 PowerShell
scripts\shoot.ps1 <design-specs-dir>
scripts\shoot.ps1 <dir> sb-01-xxx.html
```
두 스크립트 모두 Chrome→Edge 순 자동 탐지(`CHROME` 환경변수로 지정 가능). Git Bash/WSL 에서는 경로를 Windows 형식으로 자동 변환한다.
생성된 PNG를 **Read 로 열어 눈으로 확인**:
- [ ] 콜아웃이 흰 테두리 빨강 원 + 숫자 중앙정렬인가
- [ ] 왼쪽 화면이 실제 앱과 같은가 (모드 A일 때)
- [ ] 좌우 pane 정렬, 잘림 없음
- [ ] 보드 카드 썸네일/링크 정상

추가 정적 점검: 모든 `href`/`img src` 파일 존재, 이모지 없음(요청 시), `<section>` 등 태그 균형.

---

## 8. 다른 도메인으로 이식

- **모바일/네이티브**: 모드 A가 어려우면 스크린샷을 `.sb-screen` 배경/`<img>`로 깔고 그 위에 절대좌표로 `.sb-cue`를 얹는다(이땐 cue 부모를 `position:relative`로). 오른쪽 표는 동일.
- **프레임워크 앱(React/Vue 등)**: 컴포넌트를 정적 HTML로 한 번 렌더(또는 빌드 산출물 HTML)해 재현하고 그 CSS를 링크.
- **Figma 소스 (모드 A)** — 우선순위 ① **Figma MCP**가 붙어 있으면 그걸로 노드 조회·이미지 export → ② 없으면 **`figma-cli`** (Figma Desktop 로컬 연결, API 키 불필요):
  ```bash
  git clone https://github.com/cskwork/figma-cli && cd figma-cli && npm install
  figma-cli connect                  # Figma Desktop 연결 (앱이 실행 중이어야 함; --safe = 플러그인 방식, 무패칭)
  figma-cli inspect <node-id> --json   # 노드 spec(JSON, absolutePositioning 포함) → 요소표 + 콜아웃 절대좌표
  figma-cli export png <node-id>       # 화면 이미지 → 왼쪽 pane <img> (정확한 플래그는 `figma-cli export png --help` 또는 REFERENCE.md)
  ```
  - PATH에 바이너리가 없으면 `node src/index.js <명령>`으로 대체한다.
  - **node-id 표기**: Figma URL의 `node-id=73-2`(하이픈)를 `73:2`(콜론)로 바꿔 쓴다.
  - export 이미지를 `.sb-screen` 안 `<img>`로 깔고, inspect의 `absolutePositioning` 좌표대로 `.sb-cue`를 절대배치(부모 `position:relative`). = 위 모바일/네이티브 방식과 동일.
  - **REST API 변형** (figma-cli 대신 토큰만 있을 때): `X-Figma-Token` 헤더로 `GET /v1/files/{key}/nodes?ids=73:2`(스펙) + `GET /v1/images/{key}?ids=73:2&format=png`(이미지). 토큰은 환경변수/`.env`로만 두고 **절대 커밋하지 않는다**(`.gitignore`에 `.env`).
- **그 외 목업(이미지만)**: 모드 B 와이어프레임 또는 export 이미지 + 절대좌표 cue.
- **테마**: `storyboard.css` 의 `:root --sb-*` 변수만 바꿔 대상 브랜드 색에 맞춘다.
- 라벨을 영어로 바꾸려면 템플릿의 한국어 문구(화면/설명/구역/No 등)만 치환.
