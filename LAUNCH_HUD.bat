@echo off
:: ============================================================
::  MIR // TACTICAL HUD — 1-Click Launcher
::  Targets: 1920x440 secondary bar display
::  --app mode = no browser chrome, dedicated window
:: ============================================================
title MIR // TACTICAL HUD LAUNCHER

echo.
echo  [MIR] TACTICAL HUD -- Initializing...
echo  [*] Target: 1920x440 bar display
echo  [*] Mode: App window, no browser chrome
echo.

:: ── Locate dashboard.html (same folder as this .bat) ──────────────────────
set "SCRIPT_DIR=%~dp0"
set "HTML_FILE=%SCRIPT_DIR%dashboard.html"

if not exist "%HTML_FILE%" (
  echo  [ERROR] dashboard.html not found at: %HTML_FILE%
  echo  Place this .bat in the same folder as dashboard.html
  pause
  exit /b 1
)

:: ── EDIT THIS: Set X,Y to your bar display top-left pixel offset ──────────
::   Right of 1920x1080 primary  ->  1920,0
::   Right of 2560x1440 primary  ->  2560,0
::   Below a 1920x1080 primary   ->  0,1080
::   Find yours: Settings > System > Display > scroll down for offset numbers
set "WIN_POS=1920,0"
set "WIN_SIZE=1920,440"

:: ── METHOD 1: Chrome ──────────────────────────────────────────────────────
set "CHROME_EXE="
for %%P in (
  "%ProgramFiles%\Google\Chrome\Application\chrome.exe"
  "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
  "%LocalAppData%\Google\Chrome\Application\chrome.exe"
  "D:\Program Files\Google\Chrome\Application\chrome.exe"
) do (
  if exist %%P (
    if not defined CHROME_EXE set "CHROME_EXE=%%~P"
  )
)

if defined CHROME_EXE (
  echo  [OK] Chrome found: %CHROME_EXE%
  start "" "%CHROME_EXE%" --app="file:///%HTML_FILE:\=/%" --window-size=%WIN_SIZE% --window-position=%WIN_POS% --start-fullscreen --no-default-browser-check --disable-extensions --allow-file-access-from-files
  goto :LAUNCHED
)

:: ── METHOD 2: Edge ────────────────────────────────────────────────────────
set "EDGE_EXE="
for %%P in (
  "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
  "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
  "%LocalAppData%\Microsoft\Edge\Application\msedge.exe"
) do (
  if exist %%P (
    if not defined EDGE_EXE set "EDGE_EXE=%%~P"
  )
)

if defined EDGE_EXE (
  echo  [OK] Edge found: %EDGE_EXE%
  start "" "%EDGE_EXE%" --app="file:///%HTML_FILE:\=/%" --window-size=%WIN_SIZE% --window-position=%WIN_POS% --start-fullscreen --no-default-browser-check --disable-extensions --allow-file-access-from-files
  goto :LAUNCHED
)

:: ── METHOD 3: Default browser fallback ────────────────────────────────────
echo  [WARN] Chrome and Edge not found. Opening in default browser.
start "" "%HTML_FILE%"

:LAUNCHED
echo  [OK] MIR Tactical HUD launched!
echo.
echo  If window is in wrong position, edit WIN_POS in this file.
echo  Settings ^> System ^> Display to find your monitor offset.
echo.
timeout /t 3 >nul
exit /b 0
