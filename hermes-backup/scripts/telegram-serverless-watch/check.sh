#!/usr/bin/env bash
# ============================================================
# Telegram Serverless — Daily Status Checker
# چک میکنه ببینم سرویس Serverless پیشرفتی داشته یا نه
# ============================================================

set -euo pipefail

OUTPUT=""
CHANGES=0

# === 1. چک نسخه npm ===
echo "📦 Checking npm packages..." >&2

CLI_VER=$(npm view @tgcloud/cli version 2>/dev/null || echo "unknown")
BOT_VER=$(npm view @tgcloud/create-bot version 2>/dev/null || echo "unknown")

CLI_TIME=$(npm view @tgcloud/cli time --json 2>/dev/null | python3 -c "
import json,sys;d=json.loads(sys.stdin.read());v=sorted(d.keys())[-1];print(f'{v}: {d[v][:10]}')
" 2>/dev/null || echo "unknown")

OUTPUT+="📦 @tgcloud/cli: $CLI_VER (آخرین آپدیت: $CLI_TIME)\n"
OUTPUT+="📦 @tgcloud/create-bot: $BOT_VER\n"

# === 2. چک سایت رسمی (متن page برای کلمه "beta" یا "available") ===
echo "🌐 Checking official docs..." >&2

DOCS_HTML=$(curl -s --max-time 15 "https://core.telegram.org/bots/serverless" 2>/dev/null || echo "")

if echo "$DOCS_HTML" | grep -qi "beta\|experimental\|early access\|waitlist\|coming soon"; then
    OUTPUT+="\n⚠️  Docs mention beta/experimental status!\n"
    CHANGES=1
fi

# چک تاریخ آخرین تغییر — مقایسه با تاریخ فایل ذخیره شده
DOCS_HASH=$(echo "$DOCS_HTML" | md5sum | cut -d' ' -f1)
STORED_HASH=$(cat /tmp/telegram-serverless-docs-hash.txt 2>/dev/null || echo "")

if [ "$STORED_HASH" = "" ]; then
    echo "$DOCS_HASH" > /tmp/telegram-serverless-docs-hash.txt
    OUTPUT+="📄 Docs hash recorded for first time.\n"
elif [ "$DOCS_HASH" != "$STORED_HASH" ]; then
    echo "$DOCS_HASH" > /tmp/telegram-serverless-docs-hash.txt
    OUTPUT+="🔔 Docs CHANGED since last check!\n"
    CHANGES=1
else
    OUTPUT+="✅ Docs unchanged since last check.\n"
fi

# === 3. جستجوی Reddit ===
echo "🔍 Searching Reddit..." >&2

REDDIT_POSTS=$(curl -s --max-time 15 \
    -H "User-Agent: Mozilla/5.0" \
    "https://www.reddit.com/r/Telegram/search.json?q=serverless+bot+OR+tgcloud&sort=new&t=week&limit=5" \
    2>/dev/null | python3 -c "
import json,sys
try:
    d=json.loads(sys.stdin.read())
    children=d.get('data',{}).get('children',[])
    for c in children:
        p=c['data']
        print(f\"  📌 r/{p['subreddit']}: {p['title'][:80]}\")
except: pass
" 2>/dev/null || echo "")

if [ -n "$REDDIT_POSTS" ]; then
    OUTPUT+="\n🔴 New Reddit posts found:\n$REDDIT_POSTS\n"
    CHANGES=1
else
    OUTPUT+="✅ No new Reddit discussions.\n"
fi

# === 4. جستجوی GitHub ===
echo "🐙 Searching GitHub..." >&2

GH_RESULTS=$(curl -s --max-time 15 \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/search/repositories?q=tgcloud+telegram+serverless&sort=updated&per_page=5" \
    2>/dev/null | python3 -c "
import json,sys
try:
    d=json.loads(sys.stdin.read())
    for item in d.get('items',[])[:5]:
        print(f\"  📦 {item['full_name']} — ⭐{item['stargazers_count']}\")
except: pass
" 2>/dev/null || echo "")

if [ -n "$GH_RESULTS" ]; then
    OUTPUT+="\n🐙 New GitHub repos:\n$GH_RESULTS\n"
    CHANGES=1
else
    OUTPUT+="✅ No new GitHub activity.\n"
fi

# === 5. چک Hacker News ===
echo "📰 Checking HN..." >&2

HN_RESULTS=$(curl -s --max-time 15 \
    "https://hn.algolia.com/api/v1/search?query=telegram+serverless&tags=story&hitsPerPage=5&numericFilters=created_at_i%3E$(date -d '7 days ago' +%s)" \
    2>/dev/null | python3 -c "
import json,sys
try:
    d=json.loads(sys.stdin.read())
    for h in d.get('hits',[]):
        print(f\"  📰 {h['title'][:80]}\")
except: pass
" 2>/dev/null || echo "")

if [ -n "$HN_RESULTS" ]; then
    OUTPUT+="\n📰 HN discussions:\n$HN_RESULTS\n"
    CHANGES=1
else
    OUTPUT+="✅ No HN activity.\n"
fi

# === خروجی ===
if [ "$CHANGES" -eq 1 ]; then
    echo -e "🔔 **Telegram Serverless Update** — تغییر جدید شناسایی شد!\n\n$OUTPUT"
else
    echo ""
    # سایلنت — فقط وقتی تغییری باشه خبر میده
fi
