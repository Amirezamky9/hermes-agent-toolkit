#!/usr/bin/env python3
"""Parse rdt-cli search results saved to /tmp/reddit_sub_<name>.txt files.

Usage:
  python3 reddit-parse-subs.py [subreddit1 subreddit2 ...]

Finds files at /tmp/reddit_sub_<name>.txt (created by reddit-search-subs.sh
or manually via: rdt search <query> --subreddit <sub> --limit 5 > /tmp/reddit_sub_<sub>.txt)

Handles rdt-cli's custom YAML tags (!!bool, !!int, !!null, !!float) via regex.
"""
import re
import os
import sys


def parse_subreddit_block(block):
    """Extract one post from a split block of rdt-cli YAML output."""
    title_m = re.search(r'"title": "((?:[^"\\]|\\.)*)"', block)
    if not title_m:
        return None
    title = re.sub(r'\\[nt"]', ' ', title_m.group(1)).strip()

    score_m = re.search(r'"ups": !!int "(\d+)"', block)
    comments_m = re.search(r'"num_comments": !!int "(\d+)"', block)
    pid_m = re.search(r'"id": "((?:[^"\\]|\\.)*)"', block)
    sub_m = re.search(r'"subreddit": "((?:[^"\\]|\\.)*)"', block)
    selftext_m = re.search(r'"selftext": "((?:[^"\\]|\\.)*)"', block)
    ratio_m = re.search(r'"upvote_ratio": ([0-9.]+)', block)

    text = ""
    if selftext_m:
        text = re.sub(r'\\[nt"]', ' ', selftext_m.group(1)).strip()

    return {
        'title': title,
        'score': int(score_m.group(1)) if score_m else 0,
        'comments': int(comments_m.group(1)) if comments_m else 0,
        'id': pid_m.group(1) if pid_m else "",
        'subreddit': sub_m.group(1) if sub_m else "",
        'text': text,
        'ratio': float(ratio_m.group(1)) if ratio_m else 0.0,
    }


def display_post(p, index):
    """Format a single post for terminal output."""
    print(f"  [{p['score']:>5} pts] {p['title'][:90]}")
    print(f"      ID: {p['id']} | {p['ratio']*100:.0f}% | {p['comments']} comments")
    if p['text'] and len(p['text']) > 10:
        print(f"      -> {p['text'][:200]}")
    print()


def main():
    subreddits = sys.argv[1:] if len(sys.argv) > 1 else [
        "cscareerquestions", "Engineering", "AskEngineers",
        "ComputerEngineering", "learnprogramming", "csmajors"
    ]

    for sub in subreddits:
        fname = f"/tmp/reddit_sub_{sub}.txt"
        if not os.path.exists(fname):
            continue

        data = open(fname).read()
        blocks = re.split(r'\s+- \"kind\": \"t3\"', data)

        posts = []
        for block in blocks[1:]:
            p = parse_subreddit_block(block)
            if p:
                posts.append(p)

        print(f"====== r/{sub} ({len(posts)} posts) ======")
        for i, p in enumerate(posts[:5], 1):
            display_post(p, i)

        if not posts:
            print("  (no posts found)")
        print()


if __name__ == "__main__":
    main()