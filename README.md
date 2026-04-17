# Project 5 - Daily Task Planner (Flask + Docker)

This is a practical Flask web app you can actually use every day: a **task planner** with priorities, due dates, status tracking, filtering, and CSV export.

## Useful features

- Create tasks with title, notes, due date, and priority
- Mark tasks complete/reopen
- Delete tasks
- Filter tasks by `all`, `open`, `done`, `overdue`
- Dashboard counters: total, open, done, overdue, due today
- Export all tasks as CSV (`/export.csv`)
- JSON APIs for integration:
  - `GET /api/summary`
  - `GET /api/tasks?filter=all|open|done|overdue`

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000`.

Data is stored in a local SQLite database at `data/planner.db`.

## Dockerize (Requirement A)

```bash
docker build -t project5-flask-docker:latest .
docker run --rm -p 5000:5000 project5-flask-docker:latest
```

## Push image to registry (Requirement B)

Example with GitHub Container Registry:

```bash
docker tag project5-flask-docker:latest ghcr.io/<github-username>/project5-flask-docker:latest
echo <github-token> | docker login ghcr.io -u <github-username> --password-stdin
docker push ghcr.io/<github-username>/project5-flask-docker:latest
```

## API quick checks

```bash
curl http://localhost:5000/health
curl http://localhost:5000/api/summary
curl "http://localhost:5000/api/tasks?filter=open"
```
