@echo off
title MIR // TACTICAL HUD LAUNCHER

set "SCRIPT_DIR=%~dp0"
set "HTML_FILE=%SCRIPT_DIR%hud_controller.html"

if not exist "%HTML_FILE%" (
  echo [ERROR] hud_controller.html not found
  pause
  exit /b 1
)

set "HTML_URL=%HTML_FILE:\=/%"

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
if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
  set "BROWSER_EXE=C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
  goto :LAUNCH
)
if exist "C:\Program Files\Microsoft\Edge\Application\msedge.exe" (
  set "BROWSER_EXE=C:\Program Files\Microsoft\Edge\Application\msedge.exe"
  goto :LAUNCH
)

echo [WARN] Browser not found, opening default
start "" "%HTML_FILE%"
goto :DONE

:LAUNCH
start "" "%BROWSER_EXE%" "--app=file:///%HTML_URL%" "--allow-file-access-from-files"

:DONE
timeout /t 2 >nul
exit /b 0
