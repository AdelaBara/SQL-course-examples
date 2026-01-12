# SQL Streamlit Lab

Run prepared SQL examples and ad-hoc queries against an Oracle schema in a
Streamlit app.

## Prerequisites

- Python 3.10+
- Oracle DB reachable from the machine running the app

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## Configure Oracle credentials

Use Streamlit secrets (recommended). Create `.streamlit/secrets.toml`:

```toml
[oracle]
user = "..."
password = "..."
dsn = "host:1521/service_name"
```

For local development, you can also set environment variables:

- `ORACLE_USER`
- `ORACLE_PASSWORD`
- `ORACLE_DSN`

## Run locally

```bash
streamlit run SQL_Lab.py
```

## Deploy to Streamlit Cloud

1. Push this repo to GitHub.
2. In Streamlit Cloud, create a new app:
   - Repository: your GitHub repo
   - Branch: main
   - Main file path: `SQL_Lab.py`
3. Add the same `[oracle]` secrets in Streamlit Cloud settings.

## Notes

- Query examples live in `SQL examples/`.
