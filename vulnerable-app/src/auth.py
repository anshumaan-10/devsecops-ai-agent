"""
🔴 INTENTIONALLY VULNERABLE Authentication Module
===================================================
Contains broken authentication patterns for security testing.
"""

import hashlib
import time
import jwt

# 🔴 VULN: Hardcoded JWT secret (CWE-798)
JWT_SECRET = "my_jwt_secret_key_never_change_this"

# 🔴 VULN: Weak hashing algorithm (CWE-328)
def hash_password(password: str) -> str:
    """Hash password using MD5 - INSECURE."""
    return hashlib.md5(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password - no timing-safe comparison."""
    # 🔴 VULN: Timing attack possible (CWE-208)
    return hash_password(password) == hashed


def create_token(user_id: int, role: str) -> str:
    """Create JWT token with vulnerabilities."""
    payload = {
        "user_id": user_id,
        "role": role,
        "iat": time.time(),
        # 🔴 VULN: Token never expires (CWE-613)
    }
    # 🔴 VULN: Using HS256 with weak secret
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def verify_token(token: str) -> dict:
    """Verify JWT token."""
    try:
        # 🔴 VULN: algorithms not restricted, allows 'none' algorithm attack
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256", "none"])
    except jwt.InvalidTokenError:
        return None


def check_admin(token: str) -> bool:
    """Check if user is admin - vulnerable to token manipulation."""
    payload = verify_token(token)
    if payload:
        # 🔴 VULN: Role from JWT payload, can be tampered
        return payload.get("role") == "admin"
    return False


# 🔴 VULN: No rate limiting on auth attempts
# 🔴 VULN: No account lockout mechanism
# 🔴 VULN: No password complexity requirements
def authenticate(username: str, password: str, db) -> dict:
    """Authenticate user with multiple vulnerabilities."""
    cursor = db.execute(
        f"SELECT * FROM users WHERE username = '{username}'"  # 🔴 SQL Injection
    )
    user = cursor.fetchone()

    if user and user[2] == password:  # 🔴 VULN: Comparing plaintext password
        token = create_token(user[0], user[4])
        return {"success": True, "token": token, "password": password}  # 🔴 Leaking password

    return {"success": False, "error": "Invalid credentials"}
