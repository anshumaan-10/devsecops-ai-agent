# 📘 DevSecOps AI Security Workflow — Detailed Documentation

## Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Workflow Stages](#workflow-stages)
- [AI Analysis Deep Dive](#ai-analysis-deep-dive)
- [Security Gate Logic](#security-gate-logic)
- [Idempotency & Deduplication](#idempotency--deduplication)
- [Rate Limiting & Error Handling](#rate-limiting--error-handling)
- [Customization](#customization)

---

## Overview

The DevSecOps AI Security Agent is triggered automatically on every Pull Request event (`opened`, `synchronize`, `reopened`). It fetches the changed files, sends each diff to an AI model for security analysis, aggregates the findings, generates a Markdown report, and posts it as a PR comment.

The entire process is designed to be:
- **Fully automated** — zero human intervention for scanning
- **Idempotent** — updates existing comments instead of creating duplicates
- **Rate-limit aware** — respects GitHub API limits
- **Enterprise-ready** — supports custom models, severity thresholds, and file filters

---

## How It Works

```
PR Event → GitHub Actions → File Extraction → AI Analysis → Report Generation → PR Comment
```

### Step-by-Step Flow

1. **Developer opens/updates a PR** on `main` or `develop`
2. **GitHub webhook** triggers the `ai-security-scan.yml` workflow
3. **Workflow extracts** PR metadata (owner, repo, PR number)
4. **File Analyzer** fetches changed files via GitHub API
   - Filters out binary files, lock files, oversized files
   - Extracts filename, patch (diff), and status for each file
5. **AI Security Agent** sends each file's diff to GPT-4 with a security-focused prompt
   - Checks for OWASP Top 10, CWE-mapped vulnerabilities
   - Returns structured JSON findings with severity, description, snippet, and fix
6. **Report Generator** converts JSON findings into a formatted Markdown report
7. **GitHub Client** posts (or updates) the report as a PR comment
8. **Security Gate** blocks the PR if critical issues are found

---

## Workflow Stages

### Stage 1: PR Trigger

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]
    branches: [main, develop]
```

Triggers on:
- `opened` — new PR created
- `synchronize` — new commits pushed to existing PR
- `reopened` — closed PR reopened

### Stage 2: File Extraction

The file analyzer:
1. Calls `GET /repos/{owner}/{repo}/pulls/{pr_number}/files`
2. Paginates through all results (handles PRs with 100+ files)
3. Filters files based on:
   - **Extension whitelist** — `.py`, `.js`, `.ts`, `.java`, `.go`, etc.
   - **Size threshold** — configurable, default 500KB
   - **Binary detection** — skips images, fonts, archives
   - **Lock files** — skips `package-lock.json`, `yarn.lock`, etc.

### Stage 3: AI Security Analysis

Each file's diff is sent to the AI model with a carefully crafted prompt:
- Includes the full diff patch
- Lists all 14 security categories to check
- Requires structured JSON output
- Uses `temperature=0.1` for consistent results
- Uses `response_format=json_object` to enforce valid JSON

### Stage 4: Report Generation

Findings are aggregated into a single Markdown report:
- Summary table with severity counts
- File-by-file breakdown
- Each finding includes: severity, CWE, description, code snippet, recommendation
- Overall recommendation: Approve / Needs Fixes / Block Merge

### Stage 5: PR Comment

The GitHub client:
1. Checks for existing security scan comments (using an HTML comment marker)
2. Updates the existing comment (idempotent) or creates a new one
3. Uses the `GITHUB_TOKEN` or `GH_PAT` for authentication

### Stage 6: Security Gate

```bash
if [ "$CRITICAL" -gt 0 ]; then exit 1; fi
if [ "$HIGH" -gt 2 ]; then exit 1; fi
```

The workflow fails (blocks merge) if:
- Any **critical** issues are found
- More than 2 **high** severity issues are found

---

## AI Analysis Deep Dive

### Prompt Engineering

The AI prompt is designed to:
1. **Minimize false positives** — instructs the model to only flag genuine issues
2. **Maximize coverage** — covers 14 security categories with CWE mapping
3. **Provide actionable fixes** — each finding includes a specific recommendation
4. **Focus on diffs only** — analyzes only changed lines, not the entire file

### Model Selection

| Model | Speed | Accuracy | Cost |
|-------|-------|----------|------|
| GPT-4 | Slower | Highest | Higher |
| GPT-4 Turbo | Fast | High | Medium |
| GPT-3.5 Turbo | Fastest | Medium | Lowest |

Configure via the `AI_MODEL` environment variable.

---

## Security Gate Logic

| Condition | Action |
|-----------|--------|
| 0 critical, ≤2 high | ✅ Approve merge |
| 0 critical, >2 high | ⚠️ Require review |
| ≥1 critical | ❌ Block merge |

---

## Idempotency & Deduplication

- Each PR comment includes an HTML marker: `<!-- ai-security-scan-report -->`
- On subsequent pushes to the same PR, the existing comment is **updated** instead of duplicated
- This ensures a clean PR comment thread

---

## Rate Limiting & Error Handling

- GitHub API rate limits are monitored via `X-RateLimit-Remaining` header
- If remaining < 10, a warning is logged
- OpenAI API errors are caught and reported (not silently swallowed)
- File analysis failures don't block other files from being analyzed

---

## Customization

### Change Severity Threshold

```yaml
env:
  SEVERITY_THRESHOLD: "medium"  # Only report medium and above
```

### Change AI Model

```yaml
env:
  AI_MODEL: "gpt-4-turbo"
```

### Change Max File Size

```yaml
env:
  MAX_FILE_SIZE_KB: 1000  # Analyze files up to 1MB
```

### Add Custom File Extensions

Edit `security-agent/src/file_analyzer.py` → `ANALYZABLE_EXTENSIONS` set.
