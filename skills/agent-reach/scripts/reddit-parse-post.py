#!/usr/bin/env python3
"""Parse rdt-cli post read output — extract title, selftext, and top comments.

Usage:
  rdt read <POST_ID> -n 20 --compact > /tmp/reddit_post_<id>.txt
  python3 reddit-parse-post.py <POST_ID>

Handles rdt-cli custom YAML tags (!!bool, !!int, !!null, !!float) via regex.
"""
import re
import sys


def parse_post(post_id):
    fname = f"/tmp/reddit_post_{post_id}.txt"
    try:
        data = open(fname).read()
    except FileNotFoundError:
        print(f"File {fname} not found. Run: rdt read {post_id} -n 20 --compact > {fname}")
        return

    # Title
    title_m = re.search(r'"title": "((?:[^"\\]|\\.)*)"', data)
    title = re.sub(r'\\[nt"]', ' ', title_m.group(1)).strip() if title_m else "?"
    print(f"TITLE: {title}")

    # Selftext
    selftext_m = re.search(r'"selftext": "((?:[^"\\]|\\.)*)"', data)
    if selftext_m:
        text = re.sub(r'\\[nt"]', ' ', selftext_m.group(1)).strip()
        if text:
            print(f"POST: {text[:500]}")
    print()

    # Comments
    comments = re.findall(r'"body": "((?:[^"\\]|\\.)*)"', data)
    print(f"--- COMMENTS ({len(comments)}) ---")
    for i, c in enumerate(comments[:15], 1):
        body = re.sub(r'\\[nt"]', ' ', c).strip()[:250]
        print(f"{i}. {body}")
        print()

    # Scores
    scores = re.findall(r'"score": !!int "(\d+)"', data)
    if scores:
        top_scores = [int(x) for x in scores[:10]]
        print(f"Top scores: {top_scores}")
    
    # Authors
    authors = re.findall(r'"author": "((?:[^"\\]|\\.)*)"', data)
    if authors:
        unique = list(dict.fromkeys(authors))
        print(f"Unique authors: {len(unique)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 reddit-parse-post.py <POST_ID>")
        sys.exit(1)
    parse_post(sys.argv[1])