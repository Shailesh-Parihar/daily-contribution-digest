#!/usr/bin/env python3
"""Fetch freshly-opened 'good first issue' tickets from GitHub Search API
and append new ones to OPPORTUNITIES.md, skipping anything already listed."""

import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

API_URL = "https://api.github.com/search/issues"
OPPORTUNITIES_FILE = os.path.join(os.path.dirname(__file__), "..", "OPPORTUNITIES.md")
DEFAULT_LANGUAGES = "python,javascript,typescript,go"
PER_PAGE = 20


def get_languages():
    raw = os.environ.get("LANGUAGES", DEFAULT_LANGUAGES)
    return [lang.strip() for lang in raw.split(",") if lang.strip()]


def get_token():
    return os.environ.get("GITHUB_TOKEN", "")


def build_query(language, since):
    parts = [
        'label:"good first issue"',
        "state:open",
        "is:issue",
        f"language:{language}",
        f"created:>={since}",
    ]
    return " ".join(parts)


def fetch_issues(language, since, token):
    query = build_query(language, since)
    url = f"{API_URL}?{urllib.parse.urlencode({'q': query, 'sort': 'created', 'order': 'desc', 'per_page': PER_PAGE})}"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "daily-contribution-digest")
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"Warning: search failed for language={language}: {e}", file=sys.stderr)
        return []

    return data.get("items", [])


def load_existing_urls():
    if not os.path.exists(OPPORTUNITIES_FILE):
        return set()
    with open(OPPORTUNITIES_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    return set(re.findall(r"\((https://github\.com/[^)]+)\)", content))


def format_entry(issue, language):
    repo_url = issue["repository_url"].replace("https://api.github.com/repos/", "https://github.com/")
    repo_name = repo_url.replace("https://github.com/", "")
    title = issue["title"].strip()
    html_url = issue["html_url"]
    return f"- **[{title}]({html_url})** — `{repo_name}` ({language})"


def main():
    token = get_token()
    languages = get_languages()
    since = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    existing_urls = load_existing_urls()

    new_entries = []
    seen_urls = set()
    for language in languages:
        for issue in fetch_issues(language, since, token):
            url = issue["html_url"]
            if url in existing_urls or url in seen_urls:
                continue
            seen_urls.add(url)
            new_entries.append(format_entry(issue, language))

    if not new_entries:
        print("No new opportunities found.")
        return

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    section = f"\n## {today}\n\n" + "\n".join(new_entries) + "\n"

    if not os.path.exists(OPPORTUNITIES_FILE):
        header = "# Opportunities\n\nFreshly-opened \"good first issue\" tickets, updated daily.\n"
        with open(OPPORTUNITIES_FILE, "w", encoding="utf-8") as f:
            f.write(header + section)
    else:
        with open(OPPORTUNITIES_FILE, "a", encoding="utf-8") as f:
            f.write(section)

    print(f"Added {len(new_entries)} new opportunities.")


if __name__ == "__main__":
    main()
