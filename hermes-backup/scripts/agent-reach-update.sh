#!/usr/bin/env bash
# agent-reach-update.sh — آپدیت خودکار agent-reach و CLIها از GitHub
# اجرا: bash ~/.hermes/scripts/agent-reach-update.sh

set -euo pipefail
export PATH="$HOME/.local/bin:$HOME/.local/node/bin:$PATH"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}✅ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
err() { echo -e "${RED}❌ $1${NC}"; }

echo "========================================="
echo "  Agent Reach Update Script"
echo "========================================="
echo ""

UPDATED=0
FAILED=0

# 1. agent-reach (pipx)
echo "--- agent-reach ---"
if command -v agent-reach &>/dev/null; then
    OLD_VER=$(agent-reach --version 2>/dev/null | grep -oP 'v[\d.]+' || echo "unknown")
    if agent-reach check-update 2>&1 | grep -q "已是最新"; then
        log "agent-reach $OLD_VER — آخرین نسخه"
    else
        warn "agent-reach $OLD_VER — آپدیت موجود..."
        pipx upgrade agent-reach 2>/dev/null && { log "agent-reach آپدیت شد"; UPDATED=$((UPDATED+1)); } || { err "آپدیت agent-reach ناموفق"; FAILED=$((FAILED+1)); }
    fi
else
    warn "agent-reach نصب نیست — نصب می‌شه..."
    pipx install agent-reach 2>/dev/null && { log "agent-reach نصب شد"; UPDATED=$((UPDATED+1)); } || { err "نصب agent-reach ناموفق"; FAILED=$((FAILED+1)); }
fi

# 2. yt-dlp
echo ""
echo "--- yt-dlp ---"
if command -v yt-dlp &>/dev/null; then
    OLD_VER=$(yt-dlp --version 2>/dev/null)
    yt-dlp -U 2>&1 | grep -q "already up to date" && {
        log "yt-dlp $OLD_VER — آخرین نسخه"
    } || {
        NEW_VER=$(yt-dlp --version 2>/dev/null)
        log "yt-dlp $OLD_VER → $NEW_VER"
        UPDATED=$((UPDATED+1))
    }
else
    warn "yt-dlp نصب نیست..."
    pipx install yt-dlp 2>/dev/null && { log "yt-dlp نصب شد"; UPDATED=$((UPDATED+1)); } || { err "نصب yt-dlp ناموفق"; FAILED=$((FAILED+1)); }
fi

# 3. gh CLI
echo ""
echo "--- gh CLI ---"
if command -v gh &>/dev/null; then
    OLD_VER=$(gh --version 2>/dev/null | head -1 | grep -oP '[\d.]+' | head -1)
    gh update 2>&1 | grep -q "already up to date" && {
        log "gh $OLD_VER — آخرین نسخه"
    } || {
        log "gh آپدیت شد"
        UPDATED=$((UPDATED+1))
    }
else
    warn "gh نصب نیست..."
    GH_VER=$(curl -s https://api.github.com/repos/cli/cli/releases/latest | python3 -c "import json,sys; print(json.load(sys.stdin)['tag_name'].lstrip('v'))" 2>/dev/null || echo "2.70.0")
    curl -sL "https://github.com/cli/cli/releases/download/v${GH_VER}/gh_${GH_VER}_linux_amd64.tar.gz" | tar xz -C /tmp
    cp /tmp/gh_${GH_VER}_linux_amd64/bin/gh ~/.local/bin/gh
    chmod +x ~/.local/bin/gh
    log "gh $GH_VER نصب شد"
    UPDATED=$((UPDATED+1))
fi

# 4. twitter-cli
echo ""
echo "--- twitter-cli ---"
if command -v twitter &>/dev/null; then
    OLD_VER=$(twitter --version 2>/dev/null | grep -oP '[\d.]+' || echo "unknown")
    pipx upgrade twitter-cli 2>/dev/null && {
        NEW_VER=$(twitter --version 2>/dev/null | grep -oP '[\d.]+' || echo "unknown")
        if [ "$OLD_VER" != "$NEW_VER" ]; then
            log "twitter-cli $OLD_VER → $NEW_VER"
            UPDATED=$((UPDATED+1))
        else
            log "twitter-cli $OLD_VER — آخرین نسخه"
        fi
    } || warn "twitter-cli آپدیت نشد"
else
    warn "twitter-cli نصب نیست..."
    pipx install twitter-cli 2>/dev/null && { log "twitter-cli نصب شد"; UPDATED=$((UPDATED+1)); } || { err "نصب twitter-cli ناموفق"; FAILED=$((FAILED+1)); }
fi

# 5. rdt-cli
echo ""
echo "--- rdt-cli ---"
if command -v rdt &>/dev/null; then
    OLD_VER=$(rdt --version 2>/dev/null | grep -oP '[\d.]+' || echo "unknown")
    pipx upgrade rdt-cli 2>/dev/null && {
        NEW_VER=$(rdt --version 2>/dev/null | grep -oP '[\d.]+' || echo "unknown")
        if [ "$OLD_VER" != "$NEW_VER" ]; then
            log "rdt-cli $OLD_VER → $NEW_VER"
            UPDATED=$((UPDATED+1))
        else
            log "rdt-cli $OLD_VER — آخرین نسخه"
        fi
    } || warn "rdt-cli آپدیت نشد"
else
    warn "rdt-cli نصب نیست..."
    pipx install rdt-cli 2>/dev/null && { log "rdt-cli نصب شد"; UPDATED=$((UPDATED+1)); } || { err "نصب rdt-cli ناموفق"; FAILED=$((FAILED+1)); }
fi

# 6. bili-cli
echo ""
echo "--- bili-cli ---"
if command -v bili &>/dev/null; then
    OLD_VER=$(bili --version 2>/dev/null | grep -oP '[\d.]+' || echo "unknown")
    pipx upgrade bili-cli 2>/dev/null && {
        NEW_VER=$(bili --version 2>/dev/null | grep -oP '[\d.]+' || echo "unknown")
        if [ "$OLD_VER" != "$NEW_VER" ]; then
            log "bili-cli $OLD_VER → $NEW_VER"
            UPDATED=$((UPDATED+1))
        else
            log "bili-cli $OLD_VER — آخرین نسخه"
        fi
    } || warn "bili-cli آپدیت نشد"
else
    warn "bili-cli نصب نیست..."
    pipx install bili-cli 2>/dev/null && { log "bili-cli نصب شد"; UPDATED=$((UPDATED+1)); } || { err "نصب bili-cli ناموفق"; FAILED=$((FAILED+1)); }
fi

# 7. بررسی کوکی‌ها
echo ""
echo "--- بررسی کوکی‌ها ---"
COOKIE_DIR="$HOME/.agent-reach/cookies"
if [ -d "$COOKIE_DIR" ]; then
    for f in "$COOKIE_DIR"/*.json "$COOKIE_DIR"/*.txt "$COOKIE_DIR"/*.env; do
        [ -f "$f" ] || continue
        AGE=$(( ($(date +%s) - $(stat -c %Y "$f" 2>/dev/null || stat -f %m "$f" 2>/dev/null)) / 86400 ))
        if [ "$AGE" -gt 7 ]; then
            warn "$(basename $f) — $AGE روز پیش آپدیت شده"
        else
            log "$(basename $f) — $AGE روز پیش"
        fi
    done
else
    warn "پوشه کوکی وجود نداره"
fi

# 8. doctor
echo ""
echo "--- agent-reach doctor ---"
agent-reach doctor 2>&1 | tail -5

# خلاصه
echo ""
echo "========================================="
echo "  خلاصه: $UPDATED آپدیت, $FAILED خطا"
echo "========================================="
