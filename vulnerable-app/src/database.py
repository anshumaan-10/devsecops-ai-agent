"""
🔴 INTENTIONALLY VULNERABLE Database Module
=============================================
Contains SQL injection and insecure database patterns.
"""

import sqlite3
import logging

logger = logging.getLogger(__name__)

# 🔴 VULN: Hardcoded database credentials (CWE-798)
DB_HOST = "production-db.internal.company.com"
DB_USER = "admin"
DB_PASSWORD = "P@ssw0rd!2024"
DB_NAME = "production_app"
DB_PORT = 5432

# 🔴 VULN: Connection string with embedded credentials
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


class DatabaseManager:
    """Database manager with intentional SQL injection vulnerabilities."""

    def __init__(self, db_path="app.db"):
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    # 🔴 VULN: SQL Injection via string formatting (CWE-89)
    def find_user_by_name(self, username: str):
        """Find user by username - VULNERABLE."""
        conn = self.get_connection()
        query = f"SELECT * FROM users WHERE username = '{username}'"
        logger.debug(f"Running query: {query}")  # 🔴 Logging query
        return conn.execute(query).fetchone()

    # 🔴 VULN: SQL Injection via string concatenation
    def find_users_by_role(self, role: str):
        """Find users by role - VULNERABLE."""
        conn = self.get_connection()
        query = "SELECT * FROM users WHERE role = '" + role + "'"
        return conn.execute(query).fetchall()

    # 🔴 VULN: SQL Injection via % formatting
    def search_users(self, search_term: str):
        """Search users - VULNERABLE."""
        conn = self.get_connection()
        query = "SELECT * FROM users WHERE username LIKE '%%%s%%' OR email LIKE '%%%s%%'" % (
            search_term, search_term
        )
        return conn.execute(query).fetchall()

    # 🔴 VULN: Bulk delete without authorization check
    def delete_users_by_condition(self, condition: str):
        """Delete users by condition - VULNERABLE to SQL injection and access control."""
        conn = self.get_connection()
        query = f"DELETE FROM users WHERE {condition}"
        conn.execute(query)
        conn.commit()
        logger.info(f"Deleted users matching: {condition}")

    # 🔴 VULN: Updating sensitive fields without validation
    def update_user_role(self, user_id: str, new_role: str):
        """Update user role - No authorization check."""
        conn = self.get_connection()
        # 🔴 SQL Injection + no authz check
        query = f"UPDATE users SET role = '{new_role}' WHERE id = {user_id}"
        conn.execute(query)
        conn.commit()

    def export_all_data(self):
        """🔴 VULN: Export all data including PII without access control."""
        conn = self.get_connection()
        # 🔴 Exposing SSN and passwords
        cursor = conn.execute("SELECT id, username, password, email, ssn, role FROM users")
        data = []
        for row in cursor.fetchall():
            data.append({
                "id": row[0],
                "username": row[1],
                "password": row[2],  # 🔴 Including plaintext password
                "email": row[3],
                "ssn": row[4],       # 🔴 Including SSN (PII)
                "role": row[5]
            })
        return data
