@echo off
setlocal ENABLEDELAYEDEXPANSION
REM Usage: r [stg|prod] [chromium|firefox|webkit] [headed]

REM Defaults from args
set ENV=%1
if "%ENV%"=="" set ENV=stg
set BROWSER=%2
if "%BROWSER%"=="" set BROWSER=chromium
set HEADFLAG=
if /I "%3"=="headed" set HEADFLAG=--headed

echo ==================================================
echo Markopolo Playwright Test Runner
echo ==================================================

REM Ensure requirements are installed for Python 3.13
echo.
echo [1/3] Installing/updating Python dependencies...
py -3.13 -m pip install -r requirements.txt >nul
if errorlevel 1 (
  echo Failed to install Python dependencies. Showing output:
  py -3.13 -m pip install -r requirements.txt
  goto :eof
)

REM Ensure Playwright browsers are installed
echo.
echo [2/3] Ensuring Playwright browsers are installed...
py -3.13 -m playwright install >nul
if errorlevel 1 (
  echo Playwright install failed. Showing output:
  py -3.13 -m playwright install
  goto :eof
)

REM Ask user which environment to test (use arg as default)
echo.
echo [3/3] Select environment to test:
echo   1. Staging (https://beta-stg.markopolo.ai)
echo   2. Production (https://beta.markopolo.ai)
set DEFAULT_ENV=1
if /I "%ENV%"=="prod" set DEFAULT_ENV=2
set /p ENV_CHOICE=Enter choice [1/2] (default !DEFAULT_ENV!): 
if "%ENV_CHOICE%"=="" set ENV_CHOICE=!DEFAULT_ENV!
if "%ENV_CHOICE%"=="2" (
  set BASE_URL=https://beta.markopolo.ai
  set ENV=prod
) else (
  set BASE_URL=https://beta-stg.markopolo.ai
  set ENV=stg
)

echo.
echo ============== Test Configuration ==============
echo Environment : !ENV!  (BASE_URL=!BASE_URL!)
echo Browser     : !BROWSER!
echo Headed      : !HEADFLAG!
if not "!MANUAL_EMAIL!"=="" echo Email       : [provided via env]
if "!MANUAL_EMAIL!"=="" echo Email       : [not set - use MANUAL_EMAIL env var]
echo ==================================================
echo.
echo Note: Set MANUAL_EMAIL and MANUAL_PASSWORD environment variables before running
echo Example: set MANUAL_EMAIL=your@email.com
echo          set MANUAL_PASSWORD=yourpassword
echo.

REM Export environment variables for this session
set BASE_URL=!BASE_URL!

REM Run pytest (generic discovery)
py -3.13 -m pytest -v !HEADFLAG! --browser=!BROWSER!

endlocal
