# daily-contribution-digest

A small automation that runs daily via GitHub Actions, searches the GitHub
Search API for freshly-opened `good first issue` tickets (filtered by
language), and appends them to [OPPORTUNITIES.md](OPPORTUNITIES.md).

## How it works

- [.github/workflows/daily.yml](.github/workflows/daily.yml) runs on a daily
  cron schedule (06:00 UTC) and can also be triggered manually via
  `workflow_dispatch`.
- [scripts/daily_update.py](scripts/daily_update.py) queries the GitHub
  Search API for open issues labeled `good first issue`, created in the last
  day, across a configurable list of languages.
- New issues (not already listed) are appended to `OPPORTUNITIES.md` under a
  dated section. The workflow commits and pushes the update automatically.
- Auth uses the built-in `GITHUB_TOKEN` provided by GitHub Actions — no extra
  secrets required.

## Configuration

Edit the `LANGUAGES` env var in `.github/workflows/daily.yml` (comma-separated,
e.g. `python,javascript,typescript,go`) to change which languages are searched.

## Running locally

```bash
export GITHUB_TOKEN=your_personal_access_token
export LANGUAGES=python,go
python scripts/daily_update.py
```
