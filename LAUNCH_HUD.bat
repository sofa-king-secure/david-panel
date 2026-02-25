@echo off
:: ============================================================
::  MIR // TACTICAL HUD — 1-Click Launcher
::  Targets: 1920x440 secondary bar display
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
set "WIN_POS=1920,0"
set "WIN_SIZE=1920,440"

:: Convert backslashes to forward slashes for file:/// URL
set "HTML_URL=%HTML_FILE:\=/%"

:: ── METHOD 1: Chrome (check common locations) ─────────────────────────────
set "BROWSER_EXE="

if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
  set "BROWSER_EXE=C:\Program Files\Google\Chrome\Application\chrome.exe"
  goto :LAUNCH
)
if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
  set "BROWSER_EXE=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
  goto :LAUNCH
)
if exist "%LocalAppData%\Google\Chrome\Application\chrome.exe" (
  set "BROWSER_EXE=%LocalAppData%\Google\Chrome\Application\chrome.exe"
  goto :LAUNCH
)
if exist "D:\Program Files\Google\Chrome\Application\chrome.exe" (
  set "BROWSER_EXE=D:\Program Files\Google\Chrome\Application\chrome.exe"
  goto :LAUNCH
)

:: ── METHOD 2: Edge (check common locations) ───────────────────────────────
if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
  set "BROWSER_EXE=C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
  goto :LAUNCH
)
if exist "C:\Program Files\Microsoft\Edge\Application\msedge.exe" (
  set "BROWSER_EXE=C:\Program Files\Microsoft\Edge\Application\msedge.exe"
  goto :LAUNCH
)
if exist "%LocalAppData%\Microsoft\Edge\Application\msedge.exe" (
  set "BROWSER_EXE=%LocalAppData%\Microsoft\Edge\Application\msedge.exe"
  goto :LAUNCH
)

:: ── METHOD 3: Fallback ────────────────────────────────────────────────────
echo  [WARN] Chrome and Edge not found. Opening in default browser.
start "" "%HTML_FILE%"
goto :DONE

:LAUNCH
echo  [OK] Browser: %BROWSER_EXE%
start "" "%BROWSER_EXE%" "--app=file:///%HTML_URL%" "--window-size=%WIN_SIZE%" "--window-position=%WIN_POS%" "--start-fullscreen" "--no-default-browser-check" "--allow-file-access-from-files" "--disable-extensions"

:DONE
echo  [OK] MIR Tactical HUD launched!
echo.
echo  If window is in wrong position, edit WIN_POS in this file.
echo.
timeout /t 3 >nul
exit /b 0
