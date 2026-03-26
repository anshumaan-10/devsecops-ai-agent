# Sim AI — DevSecOps AI Security Workflow Specification

## Goal

Build an automated AI workflow that performs security analysis on every GitHub Pull Request and posts a summarized report back as a PR comment.

---

## Workflow Steps

### 1. Setup Trigger

- Configure GitHub Pull Request trigger
- Events:
  - `opened`
  - `synchronize`
  - `reopened`
- Ensure webhook is registered with the repository

### 2. Extract PR Data

From webhook payload:
- Repository owner
- Repository name
- Pull Request number

### 3. Fetch Changed Files

- Use GitHub API:
  ```
  GET /repos/{owner}/{repo}/pulls/{pull_number}/files
  ```
- Authentication:
  - Retrieve GitHub PAT securely from workspace secrets
  - Example: `GITHUB_TOKEN`
- For each file:
  - Filename
  - Patch (diff)
  - Status (added/modified/removed)
- Skip:
  - Binary files
  - Files exceeding size threshold

### 4. AI Security Analysis

Analyze each changed file for:

- **Hardcoded secrets** (API keys, tokens, credentials)
- **Injection vulnerabilities** (SQL, command, etc.)
- **Unsafe deserialization**
- **Authentication/authorization flaws**
- **Sensitive data leaks**
- **OWASP Top 10 risks**

For each issue, produce:
- **Severity** (Low / Medium / High / Critical)
- **Description**
- **Affected snippet** (from diff)
- **Recommended fix**

### 5. Aggregate Results

- Total issues by severity
- File-wise breakdown
- Highlight critical/high issues

### 6. Generate PR Comment (Markdown)

```markdown
## 🔐 AI Security Scan Report

### Summary:
| Severity | Count |
|----------|-------|
| Critical | X     |
| High     | X     |
| Medium   | X     |
| Low      | X     |

### Findings:

**File:** `<filename>`
- **Issue:** <description>
- **Severity:** <level>
- **Recommendation:** <fix>

### Overall Recommendation:
- ✅ Approve
- ⚠️ Needs Fixes
- ❌ Block Merge
```

### 7. Post Comment to PR

- GitHub API:
  ```
  POST /repos/{owner}/{repo}/issues/{pull_number}/comments
  ```
- Authentication:
  - Use GitHub PAT from workspace secrets (`GITHUB_TOKEN`)
  - Do NOT hardcode or expose the token

---

## Constraints

- Never expose secrets in logs or outputs
- Ensure idempotency (avoid duplicate comments)
- Handle large PRs efficiently
- Respect API rate limits

---

## Expected Output

```
"Security scan completed and comment posted successfully."
```
