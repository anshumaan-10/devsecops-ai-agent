"""
🔴 INTENTIONALLY VULNERABLE Flask Application
================================================
This application contains REAL security vulnerabilities for testing
the AI Security Agent. NEVER deploy this in production.

Vulnerabilities included:
- SQL Injection (CWE-89)
- Command Injection (CWE-78)
- Cross-Site Scripting / XSS (CWE-79)
- Insecure Deserialization (CWE-502)
- Sensitive Data Exposure (CWE-200)
- Security Misconfiguration (CWE-16)
- Broken Access Control (CWE-284)
"""

import os
import pickle
import base64
import sqlite3
import subprocess
import logging
from flask import Flask, request, jsonify, render_template_string, session, redirect

# 🔴 VULN: Debug mode enabled in production (CWE-16 - Security Misconfiguration)
app = Flask(__name__)
app.debug = True

# 🔴 VULN: Hardcoded secret key (CWE-798)
app.secret_key = "super_secret_key_12345_do_not_share"

# 🔴 VULN: CORS wildcard allows any origin (CWE-942)
from flask_cors import CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# 🔴 VULN: Logging sensitive data (CWE-532)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_db():
    """Get database connection - uses vulnerable query building."""
    db = sqlite3.connect("app.db")
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            email TEXT,
            role TEXT,
            ssn TEXT
        )
    """)
    return db


# ============================================================
# 🔴 SQL INJECTION ENDPOINTS (CWE-89)
# ============================================================

@app.route("/api/users/search", methods=["GET"])
def search_users():
    """🔴 VULN: Direct string interpolation in SQL query."""
    username = request.args.get("username", "")
    db = get_db()

    # 🔴 SQL Injection - user input directly concatenated into query
    query = f"SELECT * FROM users WHERE username = '{username}'"
    logger.info(f"Executing query: {query}")  # 🔴 Logging the query with user input

    cursor = db.execute(query)
    users = cursor.fetchall()
    return jsonify({"users": users})


@app.route("/api/users/<user_id>", methods=["GET"])
def get_user(user_id):
    """🔴 VULN: Another SQL injection point."""
    db = get_db()

    # 🔴 SQL Injection via path parameter
    query = "SELECT id, username, email, role FROM users WHERE id = " + user_id
    cursor = db.execute(query)
    user = cursor.fetchone()

    if user:
        return jsonify({"id": user[0], "username": user[1], "email": user[2], "role": user[3]})
    return jsonify({"error": "User not found"}), 404


# ============================================================
# 🔴 COMMAND INJECTION ENDPOINTS (CWE-78)
# ============================================================

@app.route("/api/tools/ping", methods=["POST"])
def ping_host():
    """🔴 VULN: Command injection via os.system()."""
    data = request.get_json()
    host = data.get("host", "")

    # 🔴 Command Injection - user input passed directly to shell
    result = os.popen(f"ping -c 3 {host}").read()
    return jsonify({"result": result})


@app.route("/api/tools/lookup", methods=["POST"])
def dns_lookup():
    """🔴 VULN: Command injection via subprocess with shell=True."""
    domain = request.json.get("domain", "")

    # 🔴 Command Injection - shell=True with user input
    result = subprocess.check_output(
        f"nslookup {domain}",
        shell=True,
        stderr=subprocess.STDOUT
    )
    return jsonify({"result": result.decode()})


# ============================================================
# 🔴 XSS VULNERABILITY (CWE-79)
# ============================================================

@app.route("/profile")
def profile():
    """🔴 VULN: Reflected XSS via unescaped user input."""
    name = request.args.get("name", "Guest")

    # 🔴 XSS - rendering user input directly into HTML without escaping
    template = f"""
    <html>
    <head><title>Profile</title></head>
    <body>
        <h1>Welcome, {name}!</h1>
        <p>Your profile page.</p>
    </body>
    </html>
    """
    return render_template_string(template)


# ============================================================
# 🔴 INSECURE DESERIALIZATION (CWE-502)
# ============================================================

@app.route("/api/import", methods=["POST"])
def import_data():
    """🔴 VULN: Unsafe pickle deserialization from user input."""
    data = request.json.get("data", "")

    try:
        # 🔴 Insecure Deserialization - pickle.loads on user-supplied data
        decoded = base64.b64decode(data)
        obj = pickle.loads(decoded)
        return jsonify({"imported": str(obj)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ============================================================
# 🔴 BROKEN AUTHENTICATION (CWE-287)
# ============================================================

@app.route("/api/auth/login", methods=["POST"])
def login():
    """🔴 VULN: Multiple auth vulnerabilities."""
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")

    db = get_db()

    # 🔴 SQL Injection in login (auth bypass)
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor = db.execute(query)
    user = cursor.fetchone()

    if user:
        # 🔴 Storing sensitive data in session without encryption
        session["user_id"] = user[0]
        session["role"] = user[4]
        session["ssn"] = user[5]  # 🔴 PII in session

        # 🔴 Logging credentials (CWE-532)
        logger.info(f"User logged in: {username} with password: {password}")

        return jsonify({"message": "Login successful", "role": user[4]})

    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/api/auth/register", methods=["POST"])
def register():
    """🔴 VULN: Plaintext password storage."""
    data = request.get_json()
    db = get_db()

    # 🔴 Storing password in plaintext (CWE-256)
    db.execute(
        "INSERT INTO users (username, password, email, role, ssn) VALUES (?, ?, ?, ?, ?)",
        (data["username"], data["password"], data["email"], "user", data.get("ssn", ""))
    )
    db.commit()

    # 🔴 Returning password in response
    return jsonify({
        "message": "User registered",
        "username": data["username"],
        "password": data["password"]  # 🔴 Exposing password in API response
    })


# ============================================================
# 🔴 BROKEN ACCESS CONTROL (CWE-284)
# ============================================================

@app.route("/api/admin/users", methods=["GET"])
def admin_get_all_users():
    """🔴 VULN: No authorization check for admin endpoint."""
    # 🔴 No authentication or authorization check
    db = get_db()
    cursor = db.execute("SELECT id, username, email, role, ssn FROM users")
    users = cursor.fetchall()

    return jsonify({"users": [
        {"id": u[0], "username": u[1], "email": u[2], "role": u[3], "ssn": u[4]}
        for u in users
    ]})


@app.route("/api/admin/delete/<user_id>", methods=["DELETE"])
def admin_delete_user(user_id):
    """🔴 VULN: IDOR - no ownership validation."""
    db = get_db()
    # 🔴 No check if requester is authorized to delete this user
    db.execute(f"DELETE FROM users WHERE id = {user_id}")  # 🔴 Also SQL Injection
    db.commit()
    return jsonify({"message": f"User {user_id} deleted"})


# ============================================================
# 🔴 FILE UPLOAD VULNERABILITY (CWE-434)
# ============================================================

@app.route("/api/upload", methods=["POST"])
def upload_file():
    """🔴 VULN: Unrestricted file upload."""
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400

    file = request.files["file"]

    # 🔴 No file type validation, no size limit, path traversal possible
    filepath = os.path.join("/tmp/uploads", file.filename)
    file.save(filepath)

    # 🔴 Execute uploaded file
    if filepath.endswith(".py"):
        result = os.popen(f"python {filepath}").read()
        return jsonify({"result": result})

    return jsonify({"message": f"File saved to {filepath}"})


# ============================================================
# 🔴 SERVER-SIDE REQUEST FORGERY (CWE-918)
# ============================================================

@app.route("/api/fetch", methods=["POST"])
def fetch_url():
    """🔴 VULN: SSRF - fetching arbitrary URLs."""
    import requests as req
    url = request.json.get("url", "")

    # 🔴 SSRF - No URL validation, can access internal services
    response = req.get(url)
    return jsonify({"status": response.status_code, "body": response.text[:1000]})


if __name__ == "__main__":
    # 🔴 VULN: Binding to all interfaces, debug mode on
    app.run(host="0.0.0.0", port=5000, debug=True)
