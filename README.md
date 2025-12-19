# Stravit Companion

Small CLI that tracks a Stravit challenge leaderboard, stores snapshots in SQLite, and sends Pushover alerts when your position or nearby gaps change.

## Table of contents

- Features
- Requirements
- Quick start (local)
- Usage
- Configuration
- Docker
- Development
- Project structure
- Troubleshooting
- License

## Features

- Log in to Stravit and fetch leaderboard CSV
- Store snapshots in SQLite
- Compare the latest snapshots and detect changes around your position
- Send alerts via Pushover

## Requirements

- Python 3.12
- A Stravit account and CSV export link
- A Pushover account (token + user)

## Quick start (local)

1. Install dependencies with uv:

```bash
uv sync --frozen --no-dev
```

2. Create your environment file:

```bash
cp .env.example .env
```

3. Update `.env` with your credentials and challenge link.

4. Run once to fetch data and persist a snapshot:

```bash
uv run python -m stravit_companion.runner --refresh
```

5. On the next run, compare snapshots and send alerts:

```bash
uv run python -m stravit_companion.runner
```

## Usage

```bash
uv run python -m stravit_companion.runner [OPTIONS]
```

Options:

- `--refresh` Fetch fresh data from Stravit before comparing snapshots
- `--dry-run` Detect alerts but do not send
- `--debug` Enable debug logging
- `--offset` Snapshot offset used for comparison (default: 0)

## Configuration

All settings are read from `.env` (see `.env.example`).

| Variable | Description | Example |
| --- | --- | --- |
| `DB_PATH` | SQLite database path | `/data/stravit.db` |
| `STRAVIT_BASE_URL` | Stravit base URL | `https://stravit.app` |
| `STRAVIT_EMAIL` | Stravit login email | `you@example.com` |
| `STRAVIT_PASSWORD` | Stravit login password | `secret` |
| `STRAVIT_CSV_LINK` | CSV export path (relative) | `challenge/xxx/export/leaderboard/csv` |
| `MY_NAME` | Your name as shown on the leaderboard | `Jan Kowalski` |
| `PUSHOVER_USER` | Pushover user key | `u123...` |
| `PUSHOVER_TOKEN` | Pushover app token | `a123...` |
| `PUSHOVER_TITLE` | Alert title | `Stravit Companion` |
| `PUSHOVER_PRIORITY` | Pushover priority (-2..2) | `0` |

## Docker

Build and run using docker compose:

```bash
docker compose up --build
```

Data is persisted in `./data/stravit.db` by default.

## Development

Install dev dependencies:

```bash
uv sync --frozen
```

Run lint/format:

```bash
ruff check --fix .
ruff format .
black .
```

## Project structure

```text
stravit_companion/
  alerts/        alert detection and Pushover sender
  client/        Stravit session and CSV fetch
  db/            SQLAlchemy models and session
  parsing/       CSV parsing
  snapshots/     snapshot persistence and comparison
  runner.py      CLI entry point
```

## Troubleshooting

- If login fails, verify `STRAVIT_BASE_URL` and that the CSV link is correct.
- If alerts look wrong, confirm your `MY_NAME` matches the leaderboard exactly.
- If the database is empty, run once with `--refresh` to create a snapshot.

## License

No license specified.
