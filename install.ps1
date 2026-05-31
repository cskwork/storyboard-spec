#!/usr/bin/env pwsh
# install.ps1 — 이 레포를 Claude Code / Codex 스킬 디렉토리로 설치 (Windows 네이티브).
# 사용:
#   .\install.ps1            # 설치된 런타임 모두 (~\.claude\skills, ~\.codex\skills)
#   .\install.ps1 claude     # Claude Code 만
#   .\install.ps1 codex      # Codex 만
#   .\install.ps1 <path>     # 임의 경로
param([string]$Target = "both")
$ErrorActionPreference = "Stop"

$src  = Split-Path -Parent $MyInvocation.MyCommand.Path
$name = "storyboard-spec"

function Copy-Skill($dest) {
  if ($src -eq $dest) { Write-Host "건너뜀 (이미 그 위치에서 실행 중): $dest"; return }
  New-Item -ItemType Directory -Force -Path $dest | Out-Null
  & robocopy $src $dest /E /XD .git | Out-Null     # /XD .git : .git 디렉토리 제외
  if ($LASTEXITCODE -ge 8) { Write-Error "robocopy 실패 (exit $LASTEXITCODE)"; exit 1 }
  $global:LASTEXITCODE = 0                          # robocopy 0~7 은 정상 → 초기화
  Write-Host "설치 완료 -> $dest"
}

$claude = Join-Path $env:USERPROFILE ".claude\skills\$name"
$codex  = Join-Path $env:USERPROFILE ".codex\skills\$name"

switch ($Target) {
  "claude" { Copy-Skill $claude }
  "codex"  { Copy-Skill $codex }
  "both" {
    $any = $false
    if (Test-Path (Join-Path $env:USERPROFILE ".claude")) { Copy-Skill $claude; $any = $true }
    if (Test-Path (Join-Path $env:USERPROFILE ".codex"))  { Copy-Skill $codex;  $any = $true }
    if (-not $any) { Write-Error "Claude/Codex 디렉토리 못 찾음. .\install.ps1 <path>"; exit 1 }
  }
  default { Copy-Skill $Target }
}
Write-Host "사용: '화면설계서 만들어줘' / '스토리보드' 라고 요청하거나 /storyboard-spec"
