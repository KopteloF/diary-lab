from flask import Flask, jsonify, request
import os
import psycopg2

app = Flask(__name__)

def get_db_conn():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        )
@app.route("/health")
def health():
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        cur.close()
        conn.close()
        return jsonify(status="ok", db="ok")
    except Exception as e:
        return jsonify(status="ok", db="error", detail=str(e)), 503

@app.route("/entries", methods=["GET"])
def list_entries():
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, created_at, title, details, minutes, commands, stack FROM entries ORDER BY id;") 
        rows = cur.fetchall()
        entries = []
        for row in rows:
            entries.append({
                "id": row[0],
                "created_at": str(row[1]),
                "title": row[2],
                "details": row[3],
                "minutes": row[4],
                "commands": row[5],
                "stack": row[6]
            })
        cur.close()
        conn.close()
        return jsonify(entries)
    except Exception as e:
        return jsonify(status="ok", db="error", detail=str(e)), 503

@app.route("/entries", methods=["POST"])
def create_entry():
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        data = request.get_json()
        if not data or not data.get("title"):
            return jsonify(error="title required"), 400
        cur.execute(
    "INSERT INTO entries (title, details, minutes, commands, stack) "
    "VALUES (%s, %s, %s, %s, %s) "
    "RETURNING id, created_at, title, details, minutes, commands, stack",
    (
        data.get("title"),
        data.get("details"),
        data.get("minutes"),
        data.get("commands"),
        data.get("stack"),
    ),
)
        row = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({
            "id": row[0],
            "created_at": str(row[1]),
            "title": row[2],
            "details": row[3],
            "minutes": row[4],
            "commands": row[5],
            "stack": row[6],
        }), 201
    except Exception as e:
        return jsonify(status="ok", db="error", detail=str(e)), 503

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

