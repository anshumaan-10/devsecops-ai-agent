"""
🔴 INTENTIONALLY VULNERABLE Utility Module
============================================
Contains hardcoded secrets and unsafe operations.
"""

import os
import yaml
import xml.etree.ElementTree as ET
import tempfile
import pickle

# ============================================================
# 🔴 HARDCODED SECRETS (CWE-798)
# ============================================================

# 🔴 AWS Credentials
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
AWS_REGION = "us-east-1"

# 🔴 Database Credentials
MYSQL_ROOT_PASSWORD = "r00t_p@ssw0rd_2024!"
POSTGRES_PASSWORD = "sup3r_s3cr3t_pg_pass"

# 🔴 API Keys
STRIPE_SECRET_KEY = "sk_live_EXAMPLE_FAKE_KEY_NOT_REAL_12345678"  # noqa: E501
SENDGRID_API_KEY = "SG.EXAMPLE_FAKE_SENDGRID_KEY_NOT_REAL"  # noqa: E501
SLACK_WEBHOOK_URL = "https://hooks.example.com/services/TXXXXXX/BXXXXXX/FAKE_WEBHOOK_NOT_REAL"  # noqa: E501
OPENAI_API_KEY = "sk-EXAMPLE-FAKE-OPENAI-KEY-NOT-REAL-1234567890"  # noqa: E501

# 🔴 OAuth Secrets
GITHUB_CLIENT_SECRET = "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdef12"
GOOGLE_CLIENT_SECRET = "GOCSPX-abcdefghijklmnopqrstuvwxyz"

# 🔴 JWT / Encryption Keys
ENCRYPTION_KEY = "aes-256-key-must-be-32-bytes!!"
RSA_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA0Z3VS5JJcds3xfn/ygWyF8PbnGy0AHB7MhgHcTz6sE2I2yPB
aNDUTEEGOyMEAFBCOxGJHSiZGCYsTKiHPMAFBCOxyzGCYsTKiHPMqVwDiqaCFGHJK
EXAMPLE_NOT_REAL_KEY_FOR_DEMO_ONLY
-----END RSA PRIVATE KEY-----"""


# ============================================================
# 🔴 UNSAFE DESERIALIZATION (CWE-502)
# ============================================================

def load_config_from_yaml(yaml_string: str) -> dict:
    """🔴 VULN: Unsafe YAML loading allows arbitrary code execution."""
    # 🔴 yaml.load without SafeLoader
    return yaml.load(yaml_string, Loader=yaml.FullLoader)


def load_user_object(serialized_data: bytes) -> object:
    """🔴 VULN: Deserializing untrusted pickle data."""
    return pickle.loads(serialized_data)


# ============================================================
# 🔴 XML EXTERNAL ENTITY (XXE) (CWE-611)
# ============================================================

def parse_user_xml(xml_string: str) -> dict:
    """🔴 VULN: XXE injection possible."""
    # 🔴 No defusedxml, allows external entity resolution
    root = ET.fromstring(xml_string)
    return {child.tag: child.text for child in root}


# ============================================================
# 🔴 PATH TRAVERSAL (CWE-22)
# ============================================================

def read_user_file(filename: str) -> str:
    """🔴 VULN: Path traversal - no sanitization of filename."""
    # 🔴 User can pass ../../../etc/passwd
    filepath = os.path.join("/app/uploads", filename)
    with open(filepath, "r") as f:
        return f.read()


def write_log(user_id: str, message: str):
    """🔴 VULN: Path traversal in log writing."""
    # 🔴 user_id not sanitized, allows directory traversal
    log_path = f"/var/log/app/{user_id}/activity.log"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a") as f:
        f.write(f"{message}\n")


# ============================================================
# 🔴 COMMAND INJECTION HELPERS (CWE-78)
# ============================================================

def compress_file(filename: str) -> str:
    """🔴 VULN: Command injection via filename."""
    output = f"/tmp/{filename}.tar.gz"
    # 🔴 Command injection through filename
    os.system(f"tar -czf {output} {filename}")
    return output


def get_file_info(filepath: str) -> str:
    """🔴 VULN: Command injection via filepath."""
    # 🔴 Unsanitized input passed to shell
    return os.popen(f"file {filepath}").read()


# ============================================================
# 🔴 WEAK CRYPTOGRAPHY (CWE-327)
# ============================================================

import hashlib

def hash_sensitive_data(data: str) -> str:
    """🔴 VULN: Using MD5 for hashing sensitive data."""
    return hashlib.md5(data.encode()).hexdigest()


def encrypt_data(data: str) -> str:
    """🔴 VULN: 'Encryption' using base64 (not actual encryption)."""
    import base64
    return base64.b64encode(data.encode()).decode()


def decrypt_data(data: str) -> str:
    """🔴 VULN: 'Decryption' using base64."""
    import base64
    return base64.b64decode(data.encode()).decode()
