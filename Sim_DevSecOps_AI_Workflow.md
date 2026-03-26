# Building an Automated DevSecOps Security Agent That Reviews Every Pull Request

**How I built a fully automated security analysis pipeline that scans every GitHub Pull Request for vulnerabilities, hardcoded secrets, injection flaws, and OWASP Top 10 risks — then posts a detailed report directly on the PR.**

---

## The Problem

Most development teams treat security as a gate at the end of the pipeline. A dedicated security team reviews code weeks after it was written, files tickets, and developers context-switch back to fix issues they barely remember writing.

The result: slow releases, frustrated developers, and vulnerabilities that slip through anyway.

Static Application Security Testing (SAST) tools help, but they generate hundreds of false positives. Teams start ignoring the alerts. The tool becomes noise.

I wanted something different — a security reviewer that actually understands code context, runs on every single pull request, and gives developers clear, actionable feedback before the code ever reaches the main branch.

---

## The Solution: An AI-Powered Security Agent on GitHub Actions

The approach is straightforward. Every time a developer opens, updates, or reopens a pull request, a GitHub Actions workflow triggers automatically. That workflow:

1. Extracts the PR metadata from the webhook payload
2. Fetches every changed file and its diff using the GitHub API
3. Sends each diff to a large language model (GPT-4) with a security-focused prompt
4. Aggregates the findings by severity and file
5. Generates a structured Markdown report
6. Posts the report as a PR comment

The developer sees the security feedback before any reviewer even opens the PR. Critical issues block the merge. The entire loop takes under 30 seconds for a typical PR.

---

## How It Works, Step by Step

### Step 1 — Configure the Pull Request Trigger

The workflow listens for three pull request events on the `main` and `develop` branches:

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]
    branches: [main, develop]
```

- **opened** — a new pull request is created
- **synchronize** — new commits are pushed to an existing pull request
- **reopened** — a previously closed pull request is reopened

GitHub registers the webhook automatically when the workflow file exists in the repository. No manual configuration is required.

### Step 2 — Extract PR Metadata

The workflow reads the webhook payload to determine three values:

| Field | Source |
|-------|--------|
| Repository owner | `github.repository_owner` |
| Repository name | `github.event.repository.name` |
| Pull request number | `github.event.pull_request.number` |

These values are passed downstream to the file fetcher and the comment poster.

### Step 3 — Fetch the Changed Files

The file analyzer calls the GitHub Pull Request Files API:

```
GET /repos/{owner}/{repo}/pulls/{pull_number}/files
```

Authentication uses a GitHub Personal Access Token stored as a repository secret (`GITHUB_TOKEN` or `GH_PAT`). The token is never hardcoded and never printed to logs.

For each file in the response, the analyzer extracts:

- **Filename** — full path within the repository
- **Patch** — the unified diff showing exactly which lines changed
- **Status** — whether the file was added, modified, or removed

The analyzer applies intelligent filtering before sending files to the AI model:

| Rule | Reason |
|------|--------|
| Skip binary files (images, fonts, archives) | No security-relevant code to analyze |
| Skip lock files (`package-lock.json`, `yarn.lock`, `poetry.lock`) | Auto-generated, extremely large, low signal |
| Skip files exceeding the size threshold (default: 500 KB) | Prevents token limits and ensures fast response times |
| Only analyze known code extensions (`.py`, `.js`, `.ts`, `.java`, `.go`, `.yaml`, etc.) | Focuses analysis on files that contain logic |

This filtering step is critical for keeping the analysis fast and cost-efficient on large pull requests.

### Step 4 — Run the AI Security Analysis

Each file's diff is sent to GPT-4 with a carefully engineered prompt. The prompt instructs the model to analyze only the changed lines (lines prefixed with `+` in the diff) and check for these categories:

| Category | What It Catches |
|----------|-----------------|
| Hardcoded Secrets | API keys, tokens, passwords, private keys, connection strings |
| SQL Injection | String interpolation or concatenation in database queries |
| Command Injection | User input passed to `os.system()`, `subprocess`, or shell commands |
| Cross-Site Scripting (XSS) | Unescaped user input rendered in HTML templates |
| Insecure Deserialization | `pickle.loads()`, `yaml.load()`, or similar on untrusted data |
| Broken Authentication | Plaintext password storage, weak hashing, missing rate limiting |
| Broken Access Control | Missing authorization checks, insecure direct object references |
| Sensitive Data Exposure | Personally identifiable information logged or returned in API responses |
| Security Misconfiguration | Debug mode enabled, CORS wildcard with credentials, missing security headers |
| Server-Side Request Forgery | Unvalidated URL fetching that could access internal services |
| Path Traversal | Unsanitized file paths that allow reading arbitrary files |
| Weak Cryptography | MD5 or SHA1 for password hashing, hardcoded encryption keys |

For every issue found, the model returns a structured JSON object containing:

```json
{
  "category": "SQL Injection",
  "severity": "critical",
  "cwe": "CWE-89",
  "description": "User input is interpolated directly into a SQL query without parameterization.",
  "snippet": "query = f\"SELECT * FROM users WHERE id = '{user_id}'\"",
  "line_hint": "23",
  "recommendation": "Use parameterized queries. Replace with: cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))"
}
```

The model uses a temperature of 0.1 for consistency and is instructed to minimize false positives. It only flags genuine, exploitable issues.

### Step 5 — Aggregate the Results

After all files are analyzed, the agent aggregates findings into a summary:

- Total count by severity level (Critical, High, Medium, Low)
- File-by-file breakdown showing which files have the most issues
- Critical and high-severity findings are highlighted at the top

The agent then determines an overall recommendation:

| Condition | Recommendation |
|-----------|----------------|
| Any critical-severity findings | **Block Merge** — do not merge until resolved |
| More than 2 high-severity findings | **Needs Fixes** — address issues before approval |
| Only medium and low findings | **Approve** — safe to merge with optional improvements |

### Step 6 — Generate the PR Comment

The report generator converts the JSON findings into a clean Markdown comment. Here is the structure:

```
## AI Security Scan Report

Scan ID: scan-a1b2c3 | Date: 2026-03-26 | Duration: 14.2s

### Summary
| Severity | Count |
|----------|-------|
| Critical | 2     |
| High     | 3     |
| Medium   | 5     |
| Low      | 1     |

### Findings

#### CRITICAL — Hardcoded AWS Secret Key
- File: vulnerable-app/src/utils.py (Line 15)
- CWE: CWE-798 (Use of Hard-coded Credentials)
- Vulnerable Code:
  AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
- Recommendation: Store credentials in AWS Secrets Manager or inject them via environment variables at runtime.

#### CRITICAL — SQL Injection in Login Endpoint
- File: vulnerable-app/src/database.py (Line 23)
- CWE: CWE-89 (Improper Neutralization of Special Elements in SQL)
- Vulnerable Code:
  query = f"SELECT * FROM users WHERE id = '{user_id}'"
- Recommendation: Use parameterized queries with your ORM or database driver.

### Overall Recommendation
Block Merge — 2 critical vulnerabilities must be resolved before this PR can be merged.
```

The report includes every detail a developer needs to understand and fix the issue without leaving the pull request page.

### Step 7 — Post the Comment to the Pull Request

The GitHub client posts the Markdown report using the Issues Comments API:

```
POST /repos/{owner}/{repo}/issues/{pull_number}/comments
```

To prevent duplicate comments when a developer pushes additional commits, the client implements idempotency. Each comment includes a hidden HTML marker:

```html
<!-- ai-security-scan-report -->
```

Before posting, the client checks whether a comment with this marker already exists on the PR. If it does, the client updates the existing comment instead of creating a new one. This keeps the PR comment thread clean.

Authentication uses the same GitHub PAT retrieved from repository secrets. The token is never exposed in logs, outputs, or error messages.

---

## The Security Gate

The workflow includes a final gating step that determines whether the PR pipeline passes or fails:

```bash
if [ "$CRITICAL" -gt 0 ]; then
    echo "BLOCKED: Critical vulnerabilities found."
    exit 1
fi

if [ "$HIGH" -gt 2 ]; then
    echo "WARNING: Multiple high-severity issues found. Review required."
    exit 1
fi

echo "Security scan passed."
```

When combined with GitHub branch protection rules requiring this check to pass, critical vulnerabilities physically cannot reach the main branch.

---

## Design Constraints

Several constraints ensure this system is production-ready:

| Constraint | Implementation |
|------------|----------------|
| Secrets must never appear in logs or outputs | All tokens are loaded from GitHub Secrets. Logging is sanitized. |
| Comments must be idempotent | HTML marker-based deduplication prevents duplicate PR comments. |
| Large PRs must not break the workflow | File size filtering and pagination handle PRs with hundreds of files. |
| GitHub API rate limits must be respected | Rate limit headers are monitored. Warnings are logged when limits are low. |
| Analysis failures must not block unrelated files | Each file is analyzed independently. A failure on one file does not affect others. |

---

## The Test Application

To validate the agent, the repository includes an intentionally vulnerable Flask application. This application contains real vulnerability patterns across every OWASP Top 10 category:

| Vulnerability | Location | CWE |
|---------------|----------|-----|
| Hardcoded AWS credentials | `vulnerable-app/src/utils.py` | CWE-798 |
| SQL injection via string interpolation | `vulnerable-app/src/database.py` | CWE-89 |
| Command injection via `os.system()` | `vulnerable-app/src/app.py` | CWE-78 |
| Reflected XSS via `render_template_string()` | `vulnerable-app/src/app.py` | CWE-79 |
| Insecure deserialization via `pickle.loads()` | `vulnerable-app/src/app.py` | CWE-502 |
| Plaintext password storage | `vulnerable-app/src/auth.py` | CWE-256 |
| Missing authorization on admin endpoints | `vulnerable-app/src/app.py` | CWE-284 |
| Sensitive data in log output | `vulnerable-app/src/app.py` | CWE-532 |
| Debug mode and CORS wildcard in production config | `vulnerable-app/config/settings.py` | CWE-16 |
| Server-side request forgery | `vulnerable-app/src/app.py` | CWE-918 |

When a developer opens a pull request that modifies any of these files, the AI agent detects every vulnerability, maps it to the correct CWE, and recommends a specific fix.

---

## Project Structure

```
devsecops-ai-agent/
├── .github/workflows/
│   ├── ai-security-scan.yml          Main AI security analysis workflow
│   ├── dependency-scan.yml            Dependency vulnerability scanning
│   └── secret-scan.yml               Dedicated hardcoded secret detection
├── security-agent/src/
│   ├── agent.py                       Core analysis engine (GPT-4 integration)
│   ├── github_client.py               GitHub API client (files, comments)
│   ├── report_generator.py            Markdown report builder
│   └── file_analyzer.py               File diff parser and filter
├── security-agent/prompts/
│   └── security_analysis.txt          AI prompt template
├── vulnerable-app/src/
│   ├── app.py                         Intentionally vulnerable Flask application
│   ├── auth.py                        Broken authentication module
│   ├── database.py                    SQL injection vulnerable queries
│   └── utils.py                       Hardcoded secrets and unsafe operations
├── vulnerable-app/config/
│   └── settings.py                    Exposed configuration with credentials
├── docs/
│   ├── WORKFLOW.md                    Detailed workflow documentation
│   ├── SECURITY_RULES.md             OWASP Top 10 and CWE mapping reference
│   └── CONTRIBUTING.md                Contribution guidelines
└── scripts/
    └── setup.sh                       One-command setup script
```

---

## Setup Instructions

The entire setup takes under three minutes.

**1. Clone the repository**

```bash
git clone https://github.com/anshumaan-10/devsecops-ai-agent.git
cd devsecops-ai-agent
```

**2. Configure repository secrets**

In your GitHub repository, navigate to Settings, then Secrets and variables, then Actions. Add two secrets:

| Secret | Purpose |
|--------|---------|
| `OPENAI_API_KEY` | Authentication for the GPT-4 API |
| `GH_PAT` | GitHub Personal Access Token with `repo` scope for posting PR comments |

**3. Open a pull request to trigger the scan**

```bash
git checkout -b feature/test-security-scan
git push origin feature/test-security-scan
```

Open a pull request on GitHub. The AI security scan runs automatically within seconds.

---

## What I Learned Building This

**Prompt engineering matters more than model selection.** A well-structured prompt with clear output format requirements, severity definitions, and false-positive reduction instructions dramatically improves result quality. Switching from a generic "find security issues" prompt to a category-specific, JSON-structured prompt reduced false positives by roughly 80%.

**Idempotency is not optional.** In a CI/CD environment, the same workflow runs multiple times per PR. Without deduplication logic, a single PR can accumulate dozens of identical security comments. The HTML marker approach solves this cleanly.

**File filtering is a performance multiplier.** Analyzing lock files and auto-generated code wastes tokens and time. Filtering down to only relevant source files cut average scan time from 45 seconds to under 15 seconds.

**The security gate changes developer behavior.** When the scan is advisory-only, developers ignore it. When it blocks the merge pipeline, developers fix issues before requesting review. The gate is the most impactful part of the entire system.

---

## Repository

The full source code, including the AI agent, GitHub Actions workflows, and the intentionally vulnerable test application, is available here:

**[github.com/anshumaan-10/devsecops-ai-agent](https://github.com/anshumaan-10/devsecops-ai-agent)**

---

*Shifting security left is not about adding more tools to the pipeline. It is about making security feedback as fast and as specific as a linter warning. When a developer sees the exact vulnerable line, the exact CWE, and the exact fix — all before a human reviewer even opens the PR — the security posture of the entire codebase improves with every single commit.*
