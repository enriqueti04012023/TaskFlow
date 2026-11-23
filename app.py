
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = "database.db"


# Connect to the database
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Create database and tasks table
def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT DEFAULT 'Medium',
            status TEXT DEFAULT 'To Do',
            due_date TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# Main dashboard
@app.route("/")
def index():
    conn = get_db_connection()

    tasks = conn.execute(
        "SELECT * FROM tasks ORDER BY id DESC"
    ).fetchall()

    total = conn.execute(
        "SELECT COUNT(*) FROM tasks"
    ).fetchone()[0]

    completed = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE status = 'Completed'"
    ).fetchone()[0]

    in_progress = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE status = 'In Progress'"
    ).fetchone()[0]

    pending = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE status = 'To Do'"
    ).fetchone()[0]

    completion_rate = round(
        (completed / total) * 100
    ) if total > 0 else 0

    conn.close()

    return render_template(
        "index.html",
        tasks=tasks,
        total=total,
        completed=completed,
        pending=pending,
        in_progress=in_progress,
        completion_rate=completion_rate
    )



# Add a new task
@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    priority = request.form.get("priority", "Medium")
    due_date = request.form.get("due_date", "")

    if not title:
        return "Error: Task title cannot be empty.", 400

    if len(title) > 120:
        return "Error: Task title is too long.", 400

    if len(description) > 1000:
        return "Error: Description is too long.", 400

    if priority not in ["Low", "Medium", "High"]:
        return "Error: Invalid priority.", 400

    conn = get_db_connection()

    conn.execute("""
        INSERT INTO tasks
        (title, description, priority, status, due_date, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        title,
        description,
        priority,
        "To Do",
        due_date,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("index"))



# Update task status
@app.route("/update/<int:task_id>", methods=["POST"])
def update_task(task_id):
    status = request.form.get("status")

    if status not in ["To Do", "In Progress", "Completed"]:
        return redirect(url_for("index"))

    conn = get_db_connection()

    conn.execute(
        "UPDATE tasks SET status = ? WHERE id = ?",
        (status, task_id)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("index"))


# Delete a task
@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    conn = get_db_connection()

    cursor = conn.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    conn.commit()
    deleted = cursor.rowcount

    conn.close()

    if deleted == 0:
        return "Error: Task not found.", 404

    return redirect(url_for("index"))



# Edit an existing task
@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    conn = get_db_connection()

    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    if task is None:
        conn.close()
        return "Task not found", 404

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        priority = request.form.get("priority", "Medium")
        due_date = request.form.get("due_date", "")

        if not title:
            conn.close()
            return "Task title is required", 400

        if priority not in ["Low", "Medium", "High"]:
            priority = "Medium"

        conn.execute("""
            UPDATE tasks
            SET title = ?, description = ?, priority = ?, due_date = ?
            WHERE id = ?
        """, (title, description, priority, due_date, task_id))

        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    conn.close()
    return render_template("edit_task.html", task=task)


@app.errorhandler(404)
def page_not_found(error):
    return render_template(
        "error.html",
        message="Page not found."
    ), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template(
        "error.html",
        message="Internal server error."
    ), 500


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
