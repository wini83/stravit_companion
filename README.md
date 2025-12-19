# Stravit Companion

[![Build & Push Docker image (release)](https://github.com/wini83/stravit_companion/actions/workflows/docker-ghcr.yml/badge.svg)](https://github.com/wini83/stravit_companion/actions/workflows/docker-ghcr.yml)

**Stravit Companion** is a lightweight **batch runner** (CLI) that periodically:

- fetches a Stravit challenge leaderboard (CSV),
- stores snapshots in SQLite,
- compares changes around your position,
- sends alerts via Pushover.

🚫 This is **not** an HTTP server  
✅ This is a **job** you run on a schedule (cron / timer)

The project is **designed to run in Docker**  
→ perfect for **Raspberry Pi / always-on hosts**

---

## TL;DR — how to use it

The user:

1. downloads `docker-compose.yml`
2. creates `.env`
3. creates a `data/` directory
4. runs `docker compose run`
5. (optionally) adds a cron job

That’s it.

---

## Requirements

- Docker + Docker Compose
- Stravit account + leaderboard CSV link
- Pushover account (token + user)
- Linux / Raspberry Pi (ARM64 supported)

---

## 🐳 Running with Docker (RECOMMENDED)

### 1️⃣ Prepare the directory

On the host (e.g. Raspberry Pi):

```bash
mkdir -p ~/stravit-companion
cd ~/stravit-companion
mkdir data
```

Target structure:

```text
stravit-companion/
├── docker-compose.yml
├── .env
└── data/
```

---

### 2️⃣ docker-compose.yml

```yaml
services:
  stravit:
    image: ghcr.io/wini83/stravit_companion:latest
    env_file:
      - .env
    volumes:
      - ./data:/data
    restart: "no"
```

---

### 3️⃣ .env configuration

```bash
cp .env.example .env
```

| Variable | Description | Example |
| --------- | ------------- | --------- |
| DB_PATH | SQLite database path | /data/stravit.db |
| STRAVIT_BASE_URL | Stravit base URL | `https://stravit.app` |
| STRAVIT_EMAIL | Login email | `you@example.com` |
| STRAVIT_PASSWORD | Password | `secret` |
| STRAVIT_CSV_LINK | CSV export path | challenge/xxx/export/leaderboard/csv |
| MY_NAME | Your name on the leaderboard | John Doe |
| PUSHOVER_USER | Pushover user key | u123... |
| PUSHOVER_TOKEN | Pushover app token | a123... |

---

### 4️⃣ First run (initialization)

```bash
docker compose run --rm stravit --refresh
```

Database will be created at:

```text
./data/stravit.db
```

---

### 5️⃣ Subsequent runs

```bash
docker compose run --rm stravit
```

---

## ⏱ Scheduled execution (cron)

```cron
0 * * * * cd /home/osmc/stravit && docker compose run --rm stravit --refresh >> stravit.log 2>&1
```

---

## Development (local)

```bash
uv sync --frozen
cp .env.example .env
uv run python -m stravit_companion.runner --refresh
```

---

## Disclaimer

Stravit Companion is an independent, open-source project and is **not affiliated with, endorsed by, or officially connected to Stravit.app**.

The name “Stravit” is used **solely for identification purposes** to describe compatibility with the Stravit platform.
All trademarks, service marks, and brand names are the property of their respective owners.

---

## License

No license specified.
