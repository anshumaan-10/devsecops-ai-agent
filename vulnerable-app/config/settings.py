"""
🔴 INTENTIONALLY VULNERABLE Configuration
==========================================
"""

import os

# 🔴 VULN: All secrets hardcoded (CWE-798)
class Config:
    SECRET_KEY = "flask-secret-key-never-use-in-production"
    DEBUG = True  # 🔴 Debug mode in production
    TESTING = False

    # 🔴 Database credentials hardcoded
    SQLALCHEMY_DATABASE_URI = "postgresql://admin:P@ssw0rd123@prod-db.company.internal:5432/maindb"
    REDIS_URL = "redis://:redis_password_2024@cache.company.internal:6379/0"

    # 🔴 Third-party service credentials
    SMTP_HOST = "smtp.gmail.com"
    SMTP_USER = "app-notifications@company.com"
    SMTP_PASSWORD = "Gmail_App_P@ssword_2024"

    # 🔴 AWS Configuration
    AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
    AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    S3_BUCKET = "company-production-data"

    # 🔴 Security headers disabled
    SESSION_COOKIE_SECURE = False       # 🔴 Should be True
    SESSION_COOKIE_HTTPONLY = False      # 🔴 Should be True
    SESSION_COOKIE_SAMESITE = None      # 🔴 Should be 'Lax' or 'Strict'

    # 🔴 CORS misconfiguration
    CORS_ORIGINS = "*"
    CORS_ALLOW_CREDENTIALS = True       # 🔴 Wildcard + credentials = vulnerability

    # 🔴 Rate limiting disabled
    RATELIMIT_ENABLED = False

    # 🔴 JWT configuration - weak
    JWT_SECRET = "jwt_secret_123"
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION = None               # 🔴 Tokens never expire
