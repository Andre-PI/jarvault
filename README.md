# JarVault API

FastAPI REST API to manage JAR files: upload, list, get, update, delete, and download. Files are stored on local disk under `mods/`, metadata is stored in SQLite.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload
```

- API docs: http://localhost:8000/docs

## Notes
- Stateless REST API
- SHA-256 hash is computed for each JAR; used to distinguish files
- SQLite file `jarvault.db` is created in project root
- Files stored under `mods/` are named by their SHA-256 hash
