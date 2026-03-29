from flask import Flask, render_template, request, redirect, url_for, session
import re
from datetime import date
import sqlite3

# ---------------- PHISHING CHECK FUNCTION ----------------
def check_phishing(url):
    if not url.startswith("https://"):
        return "❌ Unsafe Link"

    pattern = re.compile(
        r'^(https://)'
        r'([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'
    )

    if not pattern.match(url):
        return "❌ Invalid URL"

    shorteners = ["bit.ly", "tinyurl", "t.co", "goo.gl"]
    for s in shorteners:
        if s in url:
            return "⚠️ Warning: Shortened URL – Possible phishing"

    return "✅ Safe Link"

# ---------------- APP SETUP ----------------
app = Flask(__name__)
app.secret_key = "cyber_secret_key"

# ---------------- DATABASE INIT ----------------
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ---------------- HOME / AUTH ----------------
@app.route("/")
def index():
    return render_template("auth.html")

# ---------------- SIGNUP ----------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    msg = None
    error = None

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            error = "❌ Username already exists"
        else:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            conn.commit()
            msg = "✅ Sign up successfully"

        conn.close()

    return render_template('auth.html', msg=msg, error=error)



# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()

        session["passed"] = False
        conn.close()

        if user:
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('auth.html', error="Invalid username or password")

    return render_template('auth.html')

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template("dashboard.html")

# ---------------- PHISHING LINK CHECK ----------------
@app.route("/phishing-check", methods=["GET", "POST"])
def phishing_check():
    if 'user' not in session:
        return redirect(url_for('index'))

    result = None

    if request.method == "POST":
        url = request.form.get("url")
        result = check_phishing(url)

    return render_template("phishing.html", result=result)

# ---------------- QUIZ ----------------
@app.route("/quiz")
def quiz():
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template("quiz.html")

# ---------------- QUIZ SUBMIT ----------------
@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():

    if 'user' not in session:
        return redirect(url_for('index'))

    correct_answers = {
        "q1": "phishing",
        "q2": "strong",
        "q3": "no",
        "q4": "ignore",
        "q5": "update",
        "q6": "protect",
        "q7": "mix",
        "q8": "unsafe",
        "q9": "secure",
        "q10": "fraud"
    }

    score = 0

    for q, correct in correct_answers.items():
        if request.form.get(q) == correct:
            score += 1

    session["score"] = score
    session["passed"] = score >= 3

    return redirect(url_for("result"))

# ---------------- RESULT ----------------
@app.route("/result")
def result():
    if 'user' not in session:
        return redirect(url_for('index'))

    score = session.get("score", 0)
    total = 10
    percentage = int((score / total) * 100)

    return render_template(
        "result.html",
        score=score,
        total=total,
        percentage=percentage,
        passed=session.get("passed", False)
    )

# ---------------- CERTIFICATE ----------------
@app.route("/certificate")
def certificate():
    if 'user' not in session:
        return redirect(url_for('index'))

    # 🔥 STRICT CHECK
    if session.get("passed") != True:
        return render_template(
            "dashboard.html",
            error="First pass the quiz to unlock certificate"
        )

    # ✅ Only if passed
    student_name = session.get("user")
    today = date.today().strftime("%d-%m-%Y")

    return render_template(
        "certificate.html",
        student_name=student_name,
        today=today
    )

# ---------------- PASSWORD STRENGTH ----------------
@app.route("/password-strength")
def password_strength():
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template("password_strength.html")

# ---------------- AWARENESS ----------------
@app.route('/awareness')
def awareness():
    return render_template('awareness.html')

# ---------------- RUN ----------------
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)