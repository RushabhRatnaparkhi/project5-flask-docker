from datetime import date, datetime
import csv
import io
import os
import sqlite3
from flask import Flask, jsonify, redirect, render_template, request, send_file, url_for

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "planner.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            notes TEXT DEFAULT '',
            due_date TEXT,
            priority TEXT NOT NULL DEFAULT 'medium',
            done INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def fetch_tasks(filter_mode="all"):
    conn = get_conn()
    query = "SELECT * FROM tasks"
    args = []

    if filter_mode == "open":
        query += " WHERE done = 0"
    elif filter_mode == "done":
        query += " WHERE done = 1"
    elif filter_mode == "overdue":
        query += " WHERE done = 0 AND due_date IS NOT NULL AND due_date < ?"
        args.append(date.today().isoformat())

    query += " ORDER BY done ASC, CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END, due_date IS NULL, due_date ASC, created_at DESC"
    rows = conn.execute(query, args).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def summary_from_tasks(tasks):
    today = date.today().isoformat()
    total = len(tasks)
    done = sum(1 for t in tasks if t["done"] == 1)
    open_items = total - done
    overdue = sum(1 for t in tasks if t["done"] == 0 and t["due_date"] and t["due_date"] < today)
    due_today = sum(1 for t in tasks if t["done"] == 0 and t["due_date"] == today)
    return {
        "total": total,
        "done": done,
        "open": open_items,
        "overdue": overdue,
        "due_today": due_today,
    }


@app.get("/")
def home():
    filter_mode = request.args.get("filter", "all")
    if filter_mode not in {"all", "open", "done", "overdue"}:
        filter_mode = "all"
    tasks = fetch_tasks(filter_mode)
    summary = summary_from_tasks(fetch_tasks("all"))
    return render_template(
        "index.html",
        tasks=tasks,
        summary=summary,
        filter_mode=filter_mode,
        today=date.today().isoformat(),
    )


@app.post("/tasks")
def add_task():
    title = request.form.get("title", "").strip()
    notes = request.form.get("notes", "").strip()
    due_date = request.form.get("due_date", "").strip() or None
    priority = request.form.get("priority", "medium").strip().lower()

    if not title:
        return redirect(url_for("home", error="title_required"))
    if priority not in {"low", "medium", "high"}:
        priority = "medium"

    now = datetime.now().isoformat()
    conn = get_conn()
    conn.execute(
        "INSERT INTO tasks(title, notes, due_date, priority, done, created_at, updated_at) VALUES (?, ?, ?, ?, 0, ?, ?)",
        (title, notes, due_date, priority, now, now),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("home"))


@app.post("/tasks/<int:task_id>/toggle")
def toggle_task(task_id):
    conn = get_conn()
    row = conn.execute("SELECT done FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row:
        new_done = 0 if row["done"] == 1 else 1
        conn.execute(
            "UPDATE tasks SET done = ?, updated_at = ? WHERE id = ?",
            (new_done, datetime.now().isoformat(), task_id),
        )
        conn.commit()
    conn.close()
    return redirect(url_for("home"))


@app.post("/tasks/<int:task_id>/delete")
def delete_task(task_id):
    conn = get_conn()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("home"))


@app.get("/api/summary")
def api_summary():
    tasks = fetch_tasks("all")
    return jsonify(summary_from_tasks(tasks)), 200


@app.get("/api/tasks")
def api_tasks():
    filter_mode = request.args.get("filter", "all")
    if filter_mode not in {"all", "open", "done", "overdue"}:
        filter_mode = "all"
    return jsonify({"filter": filter_mode, "tasks": fetch_tasks(filter_mode)}), 200


@app.get("/export.csv")
def export_csv():
    tasks = fetch_tasks("all")
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "title", "notes", "due_date", "priority", "done", "created_at", "updated_at"])
    for task in tasks:
        writer.writerow(
            [
                task["id"],
                task["title"],
                task["notes"],
                task["due_date"],
                task["priority"],
                task["done"],
                task["created_at"],
                task["updated_at"],
            ]
        )
    mem = io.BytesIO(output.getvalue().encode("utf-8"))
    output.close()
    return send_file(mem, mimetype="text/csv", as_attachment=True, download_name="tasks-export.csv")


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "task-planner"}), 200


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
