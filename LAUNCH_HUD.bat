@echo off
:: ============================================================
::  DTMB-MCS TACTICAL HUD — 1-Click USB Launcher
::  Targets: 1920x440 secondary monitor
::  Usage: Place this .bat in the same folder as dashboard.html
:: ============================================================
title DTMB-MCS HUD LAUNCHER

echo.
echo  ██╗  ██╗██╗   ██╗██████╗     ██╗      █████╗ ██╗   ██╗███╗   ██╗ ██████╗██╗  ██╗
echo  ██║  ██║██║   ██║██╔══██╗    ██║     ██╔══██╗██║   ██║████╗  ██║██╔════╝██║  ██║
echo  ███████║██║   ██║██║  ██║    ██║     ███████║██║   ██║██╔██╗ ██║██║     ███████║
echo  ██╔══██║██║   ██║██║  ██║    ██║     ██╔══██║██║   ██║██║╚██╗██║██║     ██╔══██║
echo  ██║  ██║╚██████╔╝██████╔╝    ███████╗██║  ██║╚██████╔╝██║ ╚████║╚██████╗██║  ██║
echo  ╚═╝  ╚═╝ ╚═════╝ ╚═════╝     ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝╚═╝  ╚═╝
echo.
echo  [*] Initializing DTMB-MCS Tactical HUD...
echo  [*] Target Display: 1920x440
echo  [*] Dashboard: %~dp0dashboard.html
echo.

:: Get the directory this bat file lives in
set "SCRIPT_DIR=%~dp0"
set "HTML_FILE=%SCRIPT_DIR%dashboard.html"

if not exist "%HTML_FILE%" (
  echo  [ERROR] dashboard.html not found at: %HTML_FILE%
  echo  [ERROR] Ensure dashboard.html is in the same folder as this .bat file.
  pause
  exit /b 1
)

:: ── METHOD 1: Chrome (preferred — best rendering + kiosk mode) ──────────────
:: Try common Chrome paths. Adjust if your Chrome is elsewhere.
set "CHROME_PATHS[0]=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
set "CHROME_PATHS[1]=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
set "CHROME_PATHS[2]=%LocalAppData%\Google\Chrome\Application\chrome.exe"

set "CHROME_EXE="
for %%P in (
  "%ProgramFiles%\Google\Chrome\Application\chrome.exe"
  "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
  "%LocalAppData%\Google\Chrome\Application\chrome.exe"
) do (
  if exist %%P (
    if not defined CHROME_EXE set "CHROME_EXE=%%~P"
  )
)

if defined CHROME_EXE (
  echo  [OK] Chrome found: %CHROME_EXE%
  echo  [*]  Launching in app/kiosk mode at 1920x440...
  echo.
  echo  IMPORTANT: After Chrome opens, drag the window to your 1920x440 display
  echo  and press F11 for fullscreen. Or use --window-position below if you know
  echo  your secondary monitor offset (see README note).
  echo.
  :: --window-size=1920,440 opens at correct size
  :: --window-position=X,Y  — set X,Y to your secondary monitor's top-left pixel offset
  ::   Example: if your bar display is to the right of a 1920x1080 primary, use 1920,0
  ::   Example: if it sits below a 1080p display, use 0,1080
  ::   EDIT THE LINE BELOW to match your setup:
  set "WIN_POS=1920,0"
  start "" "%CHROME_EXE%" --app="file:///%HTML_FILE:\=/%"^
    --window-size=1920,440^
    --window-position=%WIN_POS%^
    --no-default-browser-check^
    --disable-extensions^
    --disable-background-networking^
    --disable-sync^
    --disable-translate^
    --disable-web-security^
    --allow-file-access-from-files^
    --start-maximized
  goto :LAUNCHED
)

:: ── METHOD 2: Edge (fallback) ────────────────────────────────────────────────
set "EDGE_EXE=%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
if not exist "%EDGE_EXE%" set "EDGE_EXE=%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"

if exist "%EDGE_EXE%" (
  echo  [OK] Edge found (Chrome not available). Using Edge.
  start "" "%EDGE_EXE%" --app="file:///%HTML_FILE:\=/%"^
    --window-size=1920,440^
    --window-position=1920,0^
    --disable-extensions^
    --allow-file-access-from-files
  goto :LAUNCHED
)

:: ── METHOD 3: Default browser fallback ───────────────────────────────────────
echo  [WARN] Chrome/Edge not found. Opening with default browser.
echo  [WARN] For best results, install Chrome or Chromium.
start "" "%HTML_FILE%"

:LAUNCHED
echo  [OK] HUD launched successfully.
echo.
echo  ┌─────────────────────────────────────────────────────────────┐
echo  │  TIPS:                                                      │
echo  │  • Press F11 in the browser window for true fullscreen      │
echo  │  • Edit WIN_POS in this .bat to auto-snap to your display   │
echo  │  • Right-click Desktop → Display Settings to find your      │
echo  │    secondary monitor's pixel offset (e.g. 1920,0 or 0,1080)│
echo  └─────────────────────────────────────────────────────────────┘
echo.
timeout /t 5 >nul
exit /b 0
