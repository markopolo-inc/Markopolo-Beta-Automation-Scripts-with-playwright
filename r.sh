#!/usr/bin/env bash
# Cross-platform runner for macOS/Linux
# Usage: ./r.sh [stg|prod] [chromium|firefox|webkit] [headed]

set -euo pipefail

# pick python
pick_python() {
  if command -v py >/dev/null 2>&1; then
    if py -3.13 -c "import sys;print(sys.version)" >/dev/null 2>&1; then
      echo "py -3.13"
      return
    fi
  fi
  if command -v python3 >/dev/null 2>&1; then
    echo "python3"
    return
  fi
  if command -v python >/dev/null 2>&1; then
    echo "python"
    return
  fi
  echo "Error: Python not found" >&2
  exit 1
}

PY_CMD=$(pick_python)
PIP_CMD="$PY_CMD -m pip"
PW_CMD="$PY_CMD -m playwright"
PYTEST_CMD="$PY_CMD -m pytest"

# defaults from args
ENV_CHOICE="${1:-stg}"
BROWSER="${2:-chromium}"
HEADFLAG=""
if [ "${3:-}" = "headed" ]; then HEADFLAG="--headed"; fi

printf "\n==================================================\n"
echo "Markopolo Playwright Test Runner (macOS/Linux)"
printf "==================================================\n\n"

# 1) install deps
echo "[1/3] Installing/updating Python dependencies..."
$PIP_CMD install -r requirements.txt >/dev/null || { echo "Dependencies failed. Retrying with output:"; $PIP_CMD install -r requirements.txt; }

# 2) playwright browsers
echo "\n[2/3] Ensuring Playwright browsers are installed..."
$PW_CMD install >/dev/null || { echo "Playwright install failed. Retrying with output:"; $PW_CMD install; }

# 3) choose environment (arg as default)
echo "\n[3/3] Select environment to test:"
echo "  1. Staging (https://beta-stg.markopolo.ai)"
echo "  2. Production (https://beta.markopolo.ai)"
DEFAULT_ENV=1
if [ "$ENV_CHOICE" = "prod" ]; then DEFAULT_ENV=2; fi
read -rp "Enter choice [1/2] (default $DEFAULT_ENV): " ENV_PICK || true
ENV_PICK=${ENV_PICK:-$DEFAULT_ENV}
if [ "$ENV_PICK" = "2" ]; then
  export BASE_URL="https://beta.markopolo.ai"
  ENV_CHOICE="prod"
else
  export BASE_URL="https://beta-stg.markopolo.ai"
  ENV_CHOICE="stg"
fi

# credentials (optional)
echo
echo "Enter login credentials (press Enter to skip):"
read -rp "Email: " MANUAL_EMAIL || true
read -rp "Password: " MANUAL_PASSWORD || true

# if creds provided and no headed flag, enable headed
if [ -z "$HEADFLAG" ] && [ -n "${MANUAL_EMAIL:-}" ]; then
  HEADFLAG="--headed"
fi

# summary
echo
echo "============== Test Configuration =============="
echo "Environment : $ENV_CHOICE  (BASE_URL=$BASE_URL)"
echo "Browser     : $BROWSER"
echo "Headed      : $HEADFLAG"
if [ -n "${MANUAL_EMAIL:-}" ]; then echo "Email       : [provided]"; else echo "Email       : [not provided]"; fi
printf "===============================================\n\n"

# export creds if provided
if [ -n "${MANUAL_EMAIL:-}" ]; then export MANUAL_EMAIL; fi
if [ -n "${MANUAL_PASSWORD:-}" ]; then export MANUAL_PASSWORD; fi

# run pytest
exec $PYTEST_CMD -v $HEADFLAG --browser="$BROWSER"
