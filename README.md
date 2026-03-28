<p align="center">
  <img src="https://img.shields.io/badge/DevSecOps-Security%20Agent-blue?style=for-the-badge&logo=github-actions" alt="DevSecOps Security Agent"/>
</p>

<h1 align="center">DevSecOps AI Security Agent</h1>

<p align="center">
  <strong>Enterprise-Grade Automated Security Analysis for Every Pull Request</strong>
</p>

<p align="center">
  <a href="https://github.com/anshumaan-10/devsecops-ai-agent/actions"><img src="https://img.shields.io/github/actions/workflow/status/anshumaan-10/devsecops-ai-agent/ai-security-scan.yml?style=flat-square&label=Security%20Scan" alt="Security Scan"/></a>
  <a href="https://github.com/anshumaan-10/devsecops-ai-agent/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License"/></a>
  <a href="#"><img src="https://img.shields.io/badge/OWASP-Top%2010-red?style=flat-square" alt="OWASP"/></a>
  <a href="#"><img src="https://img.shields.io/badge/python-3.11-blue?style=flat-square&logo=python" alt="Python 3.11"/></a>
</p>

---

## Overview

The **DevSecOps AI Security Agent** is a fully automated security analysis pipeline that integrates directly into your GitHub workflow. It uses GPT-4 to perform deep security analysis on every Pull Request — detecting vulnerabilities, hardcoded secrets, injection flaws, and OWASP Top 10 risks — and posts a detailed, actionable security report as a PR comment.

### Why This Exists

Traditional SAST tools generate hundreds of false positives and require manual triage. This agent takes a different approach:

- **Contextual analysis** — understands code intent, not just patterns
- **Automated PR integration** — zero manual intervention required
- **Enterprise security standards** — OWASP Top 10, CWE mapping, CVSS scoring
- **Actionable remediation** — specific fix recommendations, not just warnings

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub Pull Request                          │
│                  (opened / synchronize / reopened)              │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                 GitHub Actions Workflow                           │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────────────┐ │
│  │ PR Trigger  │→│ Extract PR   │→│ Fetch Changed Files       │ │
│  │ (webhook)   │  │ Metadata     │  │ (GitHub API + diff)      │ │
│  └────────────┘  └──────────────┘  └──────────┬───────────────┘ │
│                                                │                 │
│                                                ▼                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              AI Security Analysis Engine                     │ │
│  │  ┌─────────────┐ ┌──────────────┐ ┌─────────────────────┐  │ │
│  │  │ Secrets      │ │ Injection    │ │ Auth/AuthZ          │  │ │
│  │  │ Detection    │ │ Analysis     │ │ Flaw Detection      │  │ │
│  │  └─────────────┘ └──────────────┘ └─────────────────────┘  │ │
│  │  ┌─────────────┐ ┌──────────────┐ ┌─────────────────────┐  │ │
│  │  │ Unsafe       │ │ Data Leak    │ │ OWASP Top 10        │  │ │
│  │  │ Deserialize  │ │ Analysis     │ │ Coverage            │  │ │
│  │  └─────────────┘ └──────────────┘ └─────────────────────┘  │ │
│  └────────────────────────────┬────────────────────────────────┘ │
│                               │                                  │
│                               ▼                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │            Report Generation & PR Comment                    │ │
│  │  • Severity aggregation (Critical/High/Medium/Low)           │ │
│  │  • File-wise breakdown with code snippets                    │ │
│  │  • CWE/CVE mapping                                           │ │
│  │  • Remediation recommendations                               │ │
│  │  • Approval decision (Approve / Needs Fixes / Block Merge) │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites

- GitHub repository with Actions enabled
- OpenAI API key (GPT-4 recommended) or compatible LLM endpoint
- GitHub Personal Access Token (PAT) with `repo` scope

### Setup (3 Minutes)

**1. Fork or clone this repository:**
```bash
git clone https://github.com/anshumaan-10/devsecops-ai-agent.git
cd devsecops-ai-agent
```

**2. Add GitHub Secrets:**

Navigate to your repo → Settings → Secrets and variables → Actions, and add:

| Secret Name | Description |
|---|---|
| `OPENAI_API_KEY` | Your OpenAI API key |
| `GH_PAT` | GitHub PAT with `repo` scope |

**3. Enable the workflow:**

The AI Security Agent automatically runs on every PR. Push a branch and open a PR to test:

```bash
git checkout -b test/security-scan
# Make changes to the vulnerable-app
git push origin test/security-scan
# Open a PR on GitHub
```

---

## Project Structure

```
devsecops-ai-agent/
├── .github/
│   └── workflows/
│       ├── ai-security-scan.yml        # Main AI security scan workflow
│       ├── dependency-scan.yml          # Dependency vulnerability scanning
│       └── secret-scan.yml             # Dedicated secret scanning workflow
├── security-agent/
│   ├── src/
│   │   ├── agent.py                    # Core AI security analysis engine
│   │   ├── github_client.py            # GitHub API integration
│   │   ├── report_generator.py         # Markdown report builder
│   │   └── file_analyzer.py            # File diff parser and filter
│   ├── prompts/
│   │   └── security_analysis.txt       # AI prompt templates
│   └── requirements.txt                # Python dependencies
├── vulnerable-app/
│   ├── src/
│   │   ├── app.py                      # Intentionally vulnerable Flask app
│   │   ├── auth.py                     # Broken authentication module
│   │   ├── database.py                 # SQL injection vulnerable queries
│   │   └── utils.py                    # Hardcoded secrets and unsafe code
│   ├── config/
│   │   └── settings.py                 # Exposed configuration secrets
│   ├── requirements.txt                # App dependencies
│   └── Dockerfile                      # Container with vulnerabilities
├── docs/
│   ├── WORKFLOW.md                     # Detailed workflow documentation
│   ├── SECURITY_RULES.md              # Security rules & OWASP mapping
│   └── CONTRIBUTING.md                 # Contribution guidelines
├── scripts/
│   └── setup.sh                        # One-click setup script
├── Sim_DevSecOps_AI_Workflow.md        # Original Sim AI workflow spec
├── .gitignore
├── LICENSE
└── README.md
```

---

## Security Checks Performed

| Category | Checks | OWASP Mapping |
|---|---|---|
| **Secrets Detection** | API keys, tokens, passwords, private keys, connection strings | A02:2021 |
| **Injection Flaws** | SQL injection, command injection, XSS, LDAP injection | A03:2021 |
| **Auth/AuthZ** | Broken authentication, missing authorization, session flaws | A01:2021, A07:2021 |
| **Unsafe Deserialization** | Pickle, YAML, JSON deserialization attacks | A08:2021 |
| **Data Exposure** | PII leaks, sensitive data in logs, unencrypted storage | A02:2021 |
| **Security Misconfig** | Debug mode, CORS misconfig, missing headers | A05:2021 |
| **Dependency Vulns** | Known CVEs in dependencies via safety/pip-audit | A06:2021 |
| **Cryptographic Failures** | Weak algorithms, hardcoded keys, missing encryption | A02:2021 |

---

## Sample PR Security Report

When the agent runs, it posts a comment like this on your PR:

```markdown
## Security Scan Report

**Scan ID:** scan-abc123 | **Date:** 2026-03-26 | **Duration:** 12.3s

### Summary
| Severity | Count |
|----------|-------|
| Critical | 2 |
| High | 3 |
| Medium | 5 |
| Low | 1 |

### Findings

#### CRITICAL — Hardcoded AWS Secret Key
- **File:** `vulnerable-app/src/utils.py` (Line 15)
- **CWE:** CWE-798 (Use of Hard-coded Credentials)
- **Snippet:**
  ```python
  AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
  ```
- **Recommendation:** Use AWS Secrets Manager or environment variables.

#### CRITICAL — SQL Injection
- **File:** `vulnerable-app/src/database.py` (Line 23)
- **CWE:** CWE-89 (SQL Injection)
- **Snippet:**
  ```python
  query = f"SELECT * FROM users WHERE id = '{user_id}'"
  ```
- **Recommendation:** Use parameterized queries with SQLAlchemy ORM.

### Overall Recommendation
**Block Merge** — 2 critical vulnerabilities found. Fix before merging.
```

---

## The Vulnerable App (For Testing)

The `vulnerable-app/` directory contains an **intentionally vulnerable** Flask application designed to trigger the AI Security Agent. It includes:

- **Hardcoded credentials** (AWS keys, API tokens, database passwords)
- **SQL injection** endpoints
- **Command injection** via `os.system()`
- **Broken authentication** (plaintext passwords, no rate limiting)
- **Insecure deserialization** (pickle loads from user input)
- **XSS vulnerabilities** (unescaped user input in templates)
- **Sensitive data exposure** (PII in logs)
- **Security misconfiguration** (debug mode, CORS wildcard)

> **WARNING:** This application is intentionally vulnerable. Do not deploy it in production under any circumstances.

---

## Configuration

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | Yes | OpenAI API key for GPT-4 analysis |
| `GITHUB_TOKEN` | Yes | GitHub token (auto-provided in Actions) |
| `GH_PAT` | Yes | GitHub PAT for PR comments |
| `AI_MODEL` | No | Model to use (default: `gpt-4`) |
| `SEVERITY_THRESHOLD` | No | Minimum severity to report (default: `low`) |
| `MAX_FILE_SIZE` | No | Maximum file size to analyze in KB (default: `500`) |

---

## Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <strong>Built for the DevSecOps community</strong><br/>
  <em>Securing code, one pull request at a time.</em>
</p>

## Getting Started

1. Clone this repository.
2. Install dependencies as documented in the project files.
3. Run/build using the project-specific commands.

## Repository Structure

Key source code, configuration, and documentation are organized by folders at the repository root.

## Contribution Guidelines

Please open an issue for major changes and submit focused pull requests with clear descriptions.
