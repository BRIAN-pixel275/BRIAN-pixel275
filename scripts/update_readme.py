"""
Fetches the user's public repos from the GitHub API and rewrites the
PROJECTS section of README.md between the marker comments.

Run manually with:  python scripts/update_readme.py
Runs automatically via .github/workflows/update-readme.yml
"""

import os
import re
import sys
from datetime import datetime, timezone

import requests

# ---- Configuration ----------------------------------------------------
USERNAME = os.environ.get("GITHUB_REPOSITORY_OWNER", "BRIAN-pixel275")
README_PATH = os.path.join(os.path.dirname(__file__), "..", "README.md")
MAX_PROJECTS = 8          # how many repos to show
EXCLUDE_REPOS = {USERNAME.lower()}   # skip the profile repo itself, add more names to hide any repo
EXCLUDE_FORKS = True
# ------------------------------------------------------------------------

API_URL = f"https://api.github.com/users/{USERNAME}/repos"


def fetch_repos():
    repos = []
    page = 1
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    while True:
        resp = requests.get(
            API_URL,
            params={"sort": "created", "direction": "desc", "per_page": 100, "page": page},
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        repos.extend(batch)
        page += 1

    return repos


def build_table(repos):
    rows = []
    for repo in repos:
        if repo["name"].lower() in EXCLUDE_REPOS:
            continue
        if EXCLUDE_FORKS and repo.get("fork"):
            continue
        if repo.get("archived"):
            continue

        name = repo["name"]
        url = repo["html_url"]
        description = (repo.get("description") or "").replace("|", "-").strip()
        language = repo.get("language") or "—"
        stars = repo.get("stargazers_count", 0)

        rows.append((name, url, description, language, stars))

        if len(rows) >= MAX_PROJECTS:
            break

    if not rows:
        return "_No public repositories found yet._"

    lines = ["| Project | Description | Language | ⭐ |", "|---|---|---|---|"]
    for name, url, description, language, stars in rows:
        lines.append(f"| [**{name}**]({url}) | {description or '—'} | {language} | {stars} |")

    return "\n".join(lines)


def update_readme(table_md):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    content = re.sub(
        r"(<!-- PROJECTS:START -->\n<!-- This section is updated automatically.*?-->\n)(.*?)(\n<!-- PROJECTS:END -->)",
        lambda m: m.group(1) + table_md + m.group(3),
        content,
        flags=re.DOTALL,
    )

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    content = re.sub(
        r"(<!-- LAST_UPDATED:START -->)(.*?)(<!-- LAST_UPDATED:END -->)",
        lambda m: m.group(1) + timestamp + m.group(3),
        content,
    )

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    try:
        repos = fetch_repos()
    except requests.RequestException as exc:
        print(f"Failed to fetch repos: {exc}", file=sys.stderr)
        sys.exit(1)

    table_md = build_table(repos)
    update_readme(table_md)
    print("README.md updated.")


if __name__ == "__main__":
    main()
