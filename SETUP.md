# Setup — Self-Updating README

## How it works

A GitHub Actions workflow runs on a schedule (every 6 hours) and whenever you
manually trigger it. It calls the GitHub API for your public repos, builds a
table of your most recent projects, and rewrites the section of `README.md`
between these two comments:

```
<!-- PROJECTS:START -->
...
<!-- PROJECTS:END -->
```

If anything changed, it commits and pushes automatically — no `git commit`
needed on your end for the projects list.

## Install into your profile repo (`BRIAN-pixel275/BRIAN-pixel275`)

1. Copy these into your profile repo, keeping the folder structure:
   ```
   README.md
   .github/workflows/update-readme.yml
   scripts/update_readme.py
   ```
2. Commit and push to `main`.
3. Go to your repo's **Actions** tab → select **"Update README with latest
   projects"** → click **"Run workflow"** to trigger it the first time.
4. Check README.md — the projects table should now be filled in, and the
   "Last synced" line at the bottom should show a real timestamp.

From then on, it re-runs automatically every 6 hours, so a new public repo
you create will show up within that window without you touching the README.

## Notes / things you can tweak

- **Update frequency:** change the `cron` line in the workflow if you want it
  more/less often (e.g. `0 0 * * *` for once a day). GitHub doesn't support
  true "instant" triggers across repos without a GitHub App or a webhook, so
  a schedule is the standard approach these self-updating profiles use.
- **How many projects show:** `MAX_PROJECTS` in `scripts/update_readme.py`.
- **Hide a specific repo:** add its name (lowercase) to `EXCLUDE_REPOS` in
  the same script.
- **Include forks:** set `EXCLUDE_FORKS = False` if you want forked repos
  listed too.
- **Private repos:** the default `GITHUB_TOKEN` can only see public repos
  here. If you want private repos included, you'd need a personal access
  token with repo scope, stored as a secret, and reference it in the
  workflow instead of `secrets.GITHUB_TOKEN`.

## Testing locally (optional)

```bash
pip install requests
GITHUB_REPOSITORY_OWNER=BRIAN-pixel275 python scripts/update_readme.py
```

This rewrites your local `README.md` the same way the Action does, so you
can preview it before pushing.
