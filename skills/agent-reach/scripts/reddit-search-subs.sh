#!/usr/bin/env bash
# rdt-cli search across multiple subreddits + parse results
# Usage: bash scripts/reddit-search-subs.sh "query" [subreddit1 subreddit2 ...]
# Default subreddits cover CS/CE/EE career discussions.

set -euo pipefail

QUERY="${1:-computer engineering}"
shift || true

SUBREDDITS=("$@")
if [ ${#SUBREDDITS[@]} -eq 0 ]; then
    SUBREDDITS=(
        cscareerquestions
        cscareerquestionsEU
        Engineering
        EngineeringStudents
        AskEngineers
        ComputerEngineering
        learnprogramming
        csmajors
    )
fi

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
PARSE_SCRIPT="${SCRIPT_DIR%/scripts}/scripts/reddit-parse-subs.py"

if [ ! -f "$PARSE_SCRIPT" ]; then
    echo "ERROR: parse script not found at $PARSE_SCRIPT"
    echo "Place reddit-parse-subs.py next to this script."
    exit 1
fi

# Search each subreddit
for sub in "${SUBREDDITS[@]}"; do
    outfile="/tmp/reddit_sub_${sub}.txt"
    echo "[*] Searching r/${sub} for \"${QUERY}\" ..."
    rdt search "$QUERY" --subreddit "$sub" --sort relevance --limit 5 --time year 2>/dev/null > "$outfile"
done

# Parse all results
echo ""
echo "====== REDDIT RESULTS for \"${QUERY}\" ======"
echo ""
python3 "$PARSE_SCRIPT" "${SUBREDDITS[@]}"