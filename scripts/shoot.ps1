#!/usr/bin/env pwsh
# shoot.ps1 — 스토리보드 페이지를 헤드리스 크롬으로 캡처 (Windows 네이티브 PowerShell).
#   1) thumbs\<name>.png  : 보드 카드용 화면 위주 썸네일
#   2) (옵션) 전체폭 검증샷 : 콜아웃/레이아웃 확인용 ($env:TEMP)
#
# 사용:
#   scripts\shoot.ps1 <design-specs-dir>                 # 폴더 내 sb-*.html 전부 썸네일
#   scripts\shoot.ps1 <design-specs-dir> <one-file.html> # 한 파일 전체폭 검증샷
#   $env:CHROME = "C:\path\chrome.exe"; scripts\shoot.ps1 ...
#
# (Git Bash / WSL 사용자는 scripts/shoot.sh 를 쓰면 된다.)

param(
  [Parameter(Mandatory = $true)][string]$Dir,
  [string]$One
)
$ErrorActionPreference = "Stop"

$ThumbW = if ($env:THUMB_W) { [int]$env:THUMB_W } else { 1000 }
$ThumbH = if ($env:THUMB_H) { [int]$env:THUMB_H } else { 820 }
$FullW  = if ($env:FULL_W)  { [int]$env:FULL_W }  else { 1500 }
$FullH  = if ($env:FULL_H)  { [int]$env:FULL_H }  else { 1500 }

$Dir = (Resolve-Path $Dir).Path

# 크롬/엣지 탐지
$candidates = @(
  $env:CHROME,
  "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
  "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
  "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe",
  "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
  "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
)
$chrome = $candidates | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
if (-not $chrome) { Write-Error "Chrome/Edge not found. Set `$env:CHROME"; exit 1 }

function Invoke-Shot($out, $w, $h, $file) {
  $abs = (Resolve-Path $file).Path
  $url = ([uri]$abs).AbsoluteUri                 # file:///C:/...
  $a = @('--headless=new', '--disable-gpu', '--hide-scrollbars',
         "--window-size=$w,$h", "--screenshot=$out", $url)
  & $chrome @a | Out-Null
}

if ($One) {
  $f = Join-Path $Dir (Split-Path $One -Leaf)
  if (-not (Test-Path $f)) { $f = (Resolve-Path $One).Path }
  $out = Join-Path $env:TEMP ("sb-verify-" + [IO.Path]::GetFileNameWithoutExtension($One) + ".png")
  Invoke-Shot $out $FullW $FullH $f
  Write-Host "verify shot: $out"
  exit 0
}

$thumbs = Join-Path $Dir "thumbs"
New-Item -ItemType Directory -Force -Path $thumbs | Out-Null
$count = 0
Get-ChildItem -Path $Dir -Filter "sb-*.html" -File | ForEach-Object {
  $out = Join-Path $thumbs ($_.BaseName + ".png")
  Invoke-Shot $out $ThumbW $ThumbH $_.FullName
  Write-Host "thumb: thumbs/$($_.BaseName).png"
  $count++
}
if ($count -eq 0) { Write-Warning "no sb-*.html found in $Dir" }
Write-Host "done ($count thumbnails)"
