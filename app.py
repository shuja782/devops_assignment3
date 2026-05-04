from flask import Flask, render_template, request, redirect, url_for, jsonify
import mysql.connector
import os

app = Flask(__name__)

def get_db():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", "root"),
        database=os.environ.get("DB_NAME", "tododb")
    )

@app.route("/")
def index():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM todos ORDER BY id DESC")
    todos = cursor.fetchall()
    db.close()
    return render_template("index.html", todos=todos)

@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title", "").strip()
    if title:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO todos (title, done) VALUES (%s, %s)", (title, False))
        db.commit()
        db.close()
    return redirect(url_for("index"))

@app.route("/toggle/<int:todo_id>")
def toggle(todo_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT done FROM todos WHERE id = %s", (todo_id,))
    todo = cursor.fetchone()
    if todo:
        cursor.execute("UPDATE todos SET done = %s WHERE id = %s", (not todo["done"], todo_id))
        db.commit()
    db.close()
    return redirect(url_for("index"))

@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
    db.commit()
    db.close()
    return redirect(url_for("index"))

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)