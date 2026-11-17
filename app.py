from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
from datetime import datetime
from io import BytesIO

app = Flask(__name__)
app.secret_key = "chronohub-student-project-key"
DB_NAME = "chronohub.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS records(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        record_type TEXT,
        record_date TEXT,
        details TEXT,
        created_at TEXT
    )""")
    columns = [row[1] for row in conn.execute("PRAGMA table_info(records)").fetchall()]

    if "record_date" not in columns:
        conn.execute("ALTER TABLE records ADD COLUMN record_date TEXT")
    if not conn.execute("SELECT id FROM users WHERE email=?", ("admin@chronohub.com",)).fetchone():
        conn.execute("INSERT INTO users(name,email,password,is_admin) VALUES(?,?,?,1)",
                     ("Administrator", "admin@chronohub.com", "admin123"))
    conn.commit()
    conn.close()

@app.route("/")
def home():
    return render_template("index.html", user=session.get("name"))

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        conn = get_db()
        try:
            conn.execute("INSERT INTO users(name,email,password) VALUES(?,?,?)",
                         (name, email, password))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return render_template("register.html", error="Email already registered.")
        conn.close()
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email=? AND password=?",
                            (email, password)).fetchone()
        conn.close()
        if user:
            session.update(user_id=user["id"], name=user["name"], is_admin=user["is_admin"])
            return redirect("/dashboard")
        return render_template("login.html", error="Invalid email or password.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    conn = get_db()
    records = conn.execute("SELECT * FROM records WHERE user_id=? ORDER BY id DESC",
                           (session["user_id"],)).fetchall()
    conn.close()
    return render_template("dashboard.html", records=records, user=session["name"])

@app.route("/save", methods=["POST"])
def save():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()

    record_date = request.form.get("record_date")

    if not record_date:
        record_date = datetime.now().strftime("%Y-%m-%d")

    conn.execute("""
        INSERT INTO records
        (user_id, title, record_type, record_date, details, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        session["user_id"],
        request.form["title"],
        request.form["record_type"],
        record_date,
        request.form["details"],
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))

    conn.commit()
    print("RECORD SAVED", session["user_id"], record_date)
    conn.close()

    return redirect("/dashboard")
@app.route("/delete/<int:record_id>")
def delete_record(record_id):
    if "user_id" not in session:
        return redirect("/login")
    conn = get_db()
    conn.execute("DELETE FROM records WHERE id=? AND user_id=?",
                 (record_id, session["user_id"]))
    conn.commit()
    conn.close()
    return redirect("/dashboard")

@app.route("/admin")
def admin():
    if not session.get("is_admin"):
        return redirect("/login")
    conn = get_db()
    users = conn.execute("SELECT id,name,email,is_admin FROM users ORDER BY id").fetchall()
    records = conn.execute("""SELECT records.*, users.name AS user_name
                              FROM records LEFT JOIN users ON records.user_id=users.id
                              ORDER BY records.id DESC""").fetchall()
    conn.close()
    return render_template("admin.html", users=users, records=records)

@app.route("/report")
def report():
    if "user_id" not in session:
        return redirect("/login")
    conn = get_db()
    records = conn.execute("SELECT * FROM records WHERE user_id=? ORDER BY id DESC",
                           (session["user_id"],)).fetchall()
    conn.close()
    lines = ["ChronoHub - LifeSync Report", "============================",
             f"User: {session['name']}", ""]
    for r in records:
        lines += [f"{r['title']} ({r['record_type']})", r["details"],
                  f"Saved: {r['created_at']}", ""]
    return send_file(BytesIO("\n".join(lines).encode()),
                     as_attachment=True, download_name="chronohub_report.txt",
                     mimetype="text/plain")

@app.context_processor
def inject_admin():
    return {"is_admin": session.get("is_admin", 0)}

init_db()

if __name__ == "__main__":
    app.run(debug=True)
