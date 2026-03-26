# 🛡️ Security Rules & OWASP Mapping

## Overview

This document maps the AI Security Agent's detection capabilities to the OWASP Top 10 (2021) and CWE framework.

---

## OWASP Top 10 (2021) Coverage

### A01:2021 — Broken Access Control

| Check | CWE | Example |
|-------|-----|---------|
| Missing authorization on endpoints | CWE-284 | Admin endpoint without auth check |
| Insecure Direct Object Reference (IDOR) | CWE-639 | `/api/users/{id}` without ownership check |
| Privilege escalation | CWE-269 | Role manipulation in JWT payload |
| CORS misconfiguration | CWE-942 | `Access-Control-Allow-Origin: *` with credentials |

### A02:2021 — Cryptographic Failures

| Check | CWE | Example |
|-------|-----|---------|
| Hardcoded secrets | CWE-798 | `API_KEY = "sk-..."` in source code |
| Weak hashing (MD5/SHA1) | CWE-327 | `hashlib.md5(password)` |
| Plaintext password storage | CWE-256 | Storing passwords without hashing |
| Missing encryption | CWE-311 | Sensitive data transmitted in cleartext |

### A03:2021 — Injection

| Check | CWE | Example |
|-------|-----|---------|
| SQL injection | CWE-89 | `f"SELECT * FROM users WHERE id = '{input}'"` |
| Command injection | CWE-78 | `os.system(f"ping {user_input}")` |
| XSS | CWE-79 | `render_template_string(f"<h1>{name}</h1>")` |
| LDAP injection | CWE-90 | Unsanitized input in LDAP queries |

### A04:2021 — Insecure Design

| Check | CWE | Example |
|-------|-----|---------|
| Missing rate limiting | CWE-770 | Login endpoint without throttling |
| Missing input validation | CWE-20 | No validation on API parameters |

### A05:2021 — Security Misconfiguration

| Check | CWE | Example |
|-------|-----|---------|
| Debug mode in production | CWE-489 | `app.debug = True` |
| Default credentials | CWE-1392 | Using well-known default passwords |
| Missing security headers | CWE-693 | No CSP, HSTS, X-Frame-Options |
| Verbose error messages | CWE-209 | Stack traces exposed to users |

### A06:2021 — Vulnerable and Outdated Components

| Check | CWE | Example |
|-------|-----|---------|
| Known CVEs in dependencies | CWE-1035 | Using `requests==2.20.0` with known vuln |
| Unpinned dependencies | CWE-829 | `Flask>=2.0` without upper bound |

### A07:2021 — Identification and Authentication Failures

| Check | CWE | Example |
|-------|-----|---------|
| Broken authentication | CWE-287 | SQL injection in login query |
| Weak session management | CWE-613 | JWT tokens that never expire |
| Missing MFA | CWE-308 | No multi-factor authentication |
| Timing attacks | CWE-208 | Non-constant-time password comparison |

### A08:2021 — Software and Data Integrity Failures

| Check | CWE | Example |
|-------|-----|---------|
| Insecure deserialization | CWE-502 | `pickle.loads(user_data)` |
| Unsigned data | CWE-345 | Accepting unsigned JWTs (`"none"` algorithm) |

### A09:2021 — Security Logging and Monitoring Failures

| Check | CWE | Example |
|-------|-----|---------|
| Sensitive data in logs | CWE-532 | `logger.info(f"password: {pwd}")` |
| Missing audit trail | CWE-778 | No logging of auth events |

### A10:2021 — Server-Side Request Forgery (SSRF)

| Check | CWE | Example |
|-------|-----|---------|
| Unvalidated URL fetching | CWE-918 | `requests.get(user_url)` without validation |
| Internal service access | CWE-441 | Fetching `http://169.254.169.254/` (AWS metadata) |

---

## Severity Classification

### Critical (CVSS 9.0-10.0)
- Hardcoded production credentials (AWS keys, DB passwords)
- SQL injection in authentication flow
- Remote Code Execution (command injection, deserialization)

### High (CVSS 7.0-8.9)
- SQL injection in non-auth endpoints
- SSRF with internal network access
- Broken access control on admin endpoints
- Unsafe file upload allowing code execution

### Medium (CVSS 4.0-6.9)
- Cross-Site Scripting (XSS)
- Weak cryptography (MD5/SHA1)
- Missing security headers
- CORS misconfiguration

### Low (CVSS 0.1-3.9)
- Debug mode enabled
- Verbose error messages
- Missing rate limiting
- Informational findings
