# storyboard-spec

> A reusable [Claude Code](https://claude.ai/code) **Skill** that generates side-by-side **storyboard-style screen design documents** (스토리보드식 화면설계서) — the kind 기획자/PM hand to both non-developers and API developers.

한 화면 = 한 페이지. **왼쪽은 실제 화면을 픽셀까지 재현 + 번호 콜아웃**, **오른쪽은 요소별 설명표(동작·데이터·예외)**. 그리고 썸네일 미리보기 **보드(index)** 가 각 화면으로 링크됩니다. 도메인에 종속되지 않아 어떤 앱/기획에도 재사용할 수 있습니다.

![demo](examples/demo/thumbs/sb-01-login.png)

## 무엇을 만드나 / What it produces

- **LEFT — 실제 화면**: 대상 앱의 진짜 CSS를 그대로 링크해 화면을 재현하고, 그 위에 번호 콜아웃(①②③…)을 얹습니다.
- **RIGHT — 화면 설명**: 콜아웃 1:1 대응 설명표 — 요소/DOM id, 동작·이벤트, 데이터 계약(필드·엔드포인트·공식), 상태, 예외.
- **BOARD — index.html**: 화면 미리보기 썸네일 카드 → 클릭하면 해당 스토리보드가 별도 화면으로 열림.

비개발자용 개요와 API 개발용 계약을 한 문서에 같이 담는 게 핵심입니다.

## 설치 / Install

**Claude Code** 와 **Codex** 둘 다, **macOS · Linux · Windows** 모두 지원합니다 (같은 `SKILL.md`).

```bash
# macOS / Linux / Windows(Git Bash·WSL)
git clone https://github.com/cskwork/storyboard-spec.git
cd storyboard-spec
./install.sh           # 설치된 런타임 모두 (~/.claude/skills, ~/.codex/skills)
./install.sh claude    # Claude Code 만   ·   ./install.sh codex   # Codex 만
```

```powershell
# Windows (네이티브 PowerShell)
git clone https://github.com/cskwork/storyboard-spec.git
cd storyboard-spec
.\install.ps1          # 양쪽   ·   .\install.ps1 claude   ·   .\install.ps1 codex
```

스킬 디렉토리에 바로 클론해도 됩니다:
`git clone … ~/.claude/skills/storyboard-spec` 또는 `… ~/.codex/skills/storyboard-spec`.

> 스크린샷 검증은 헤드리스 Chrome/Edge 가 필요합니다. macOS/Linux/Git Bash/WSL → `scripts/shoot.sh`, 네이티브 Windows → `scripts/shoot.ps1`. 둘 다 Chrome→Edge 순으로 자동 탐지하며 `CHROME` 환경변수로 직접 지정 가능합니다.

## 사용 / Usage

Claude Code / Codex 에서 그냥 요청하면 스킬이 발동합니다:

- "이 앱 화면들 **화면설계서**(스토리보드) 만들어줘"
- "`<app>/design-specs/` 에 로그인·결제 화면 스토리보드 만들어"
- 또는 슬래시: `/storyboard-spec`

Claude 가 화면을 추출 → 실제 CSS를 재사용해 왼쪽 화면을 재현 → 콜아웃 + 설명표 작성 → 보드 생성 → 헤드리스 크롬으로 스크린샷 검증까지 수행합니다.

## 구조 / Layout

```
storyboard-spec/
├── SKILL.md                     # 스킬 진입점 (Claude 가 읽음)
├── templates/
│   ├── storyboard.css           # chrome (콜아웃·설명표). :root 변수로 테마
│   ├── storyboard-page.html     # 화면 1장 스켈레톤 ({{placeholder}})
│   └── board-index.html         # 썸네일 보드 스켈레톤
├── scripts/
│   └── shoot.sh                 # 헤드리스 크롬 썸네일/검증 샷
├── reference/
│   └── playbook.md              # 전체 프로세스 · 함정 · 도메인 이식 가이드
└── examples/demo/               # 최소 동작 예제(로그인 화면) = 스모크 테스트
```

## 핵심 함정 (실전에서 깨졌던 것) / Gotchas

이 스킬이 값진 이유는 실제로 겪은 함정을 코드에 박아뒀기 때문입니다:

1. **콜아웃이 대상 앱 규칙에 덮어써짐** — 대상 CSS의 `.field span{display:block}`, `.meter span{background}` 같은 규칙이 콜아웃 `<span>`을 사각형/왼쪽정렬로 깨뜨립니다. → `storyboard.css`의 `.sb-cue`가 `!important`로 방어 (지우지 말 것).
2. **`<table>` 직속 `<span>` 금지** — 브라우저가 테이블 밖으로 밀어냅니다(foster parenting). → `<table>`을 `<div class="sb-mark">`로 감싸고 콜아웃을 그 div에.
3. **CSS 링크 순서** — 대상 앱 CSS 먼저, `storyboard.css` 나중.
4. **스크린샷으로 검증** 후 완료 선언.

자세한 내용은 [`reference/playbook.md`](reference/playbook.md).

## 도메인 이식 / Cross-domain

웹뿐 아니라 모바일/네이티브(스크린샷 위에 절대좌표 콜아웃), 프레임워크 앱(정적 렌더 후 CSS 링크), Figma 목업(와이어프레임/export)으로 확장 가능. `storyboard.css`의 `:root --sb-*` 변수만 바꾸면 브랜드 색에 맞출 수 있고, 템플릿의 한국어 라벨을 치환하면 영어 문서도 됩니다.

## License

MIT — see [LICENSE](LICENSE).
