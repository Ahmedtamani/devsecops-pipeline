import sqlite3
import subprocess

from flask import Flask, jsonify, request

app = Flask(__name__)
app.config["DATABASE"] = "users.db"

# INTENTIONALLY VULNERABLE (VULN-03): hardcoded secret.
# The admin token is written in the source code and committed to Git.
# Kept on purpose for this learning project.
ADMIN_TOKEN = "9f2c4e7a1b8d3f6e0a5c2b9d4e7f1a3c"

SEED_USERS = [
    ("alice", "admin"),
    ("bob", "developer"),
    ("carol", "viewer"),
]


def get_db():
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    try:
        with conn:
            conn.execute("DROP TABLE IF EXISTS users")
            conn.execute(
                "CREATE TABLE users ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "name TEXT NOT NULL, "
                "role TEXT NOT NULL)"
            )
            conn.executemany(
                "INSERT INTO users (name, role) VALUES (?, ?)", SEED_USERS
            )
    finally:
        conn.close()


@app.get("/health")
def health():
    return jsonify(status="ok"), 200


@app.get("/users")
def list_users():
    name = request.args.get("name")
    conn = get_db()
    try:
        if name:
            rows = conn.execute(
                "SELECT id, name, role FROM users WHERE name = ?", (name,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT id, name, role FROM users").fetchall()
    finally:
        conn.close()
    return jsonify([dict(row) for row in rows])


@app.get("/users/<int:user_id>")
def get_user(user_id):
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT id, name, role FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        return jsonify(error="not found"), 404
    return jsonify(dict(row))


@app.get("/search")
def search_users():
    # INTENTIONALLY VULNERABLE (VULN-01): SQL injection.
    # The search term is inserted into the query with an f-string.
    # Kept on purpose for this learning project. Compare with /users.
    q = request.args.get("q", "")
    conn = get_db()
    try:
        rows = conn.execute(
            f"SELECT id, name, role FROM users WHERE name LIKE '%{q}%'"
        ).fetchall()
    finally:
        conn.close()
    return jsonify([dict(row) for row in rows])


@app.get("/ping")
def ping():
    # INTENTIONALLY VULNERABLE (VULN-02): OS command injection.
    # The host parameter is passed to a shell (shell=True) without validation.
    # Kept on purpose for this learning project.
    host = request.args.get("host", "127.0.0.1")
    result = subprocess.run(
        f"ping -c 1 {host}", shell=True, capture_output=True, text=True, timeout=5
    )
    return jsonify(returncode=result.returncode, output=result.stdout)


@app.delete("/admin/users/<int:user_id>")
def delete_user(user_id):
    if request.headers.get("X-Admin-Token") != ADMIN_TOKEN:
        return jsonify(error="unauthorized"), 401
    conn = get_db()
    try:
        with conn:
            cursor = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    finally:
        conn.close()
    if cursor.rowcount == 0:
        return jsonify(error="not found"), 404
    return jsonify(deleted=user_id)


init_db()
