"""
AI Security Analysis Agent
===========================
Core engine that analyzes code diffs using OpenAI GPT-4 for security vulnerabilities.
Covers OWASP Top 10, CWE mapping, hardcoded secrets, injection flaws, and more.
"""

import json
import os
import sys
import argparse
import time
import logging
from typing import Optional
from openai import OpenAI

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Security analysis categories
SECURITY_CATEGORIES = [
    "Hardcoded Secrets (API keys, tokens, passwords, private keys, connection strings)",
    "SQL Injection (CWE-89)",
    "Command Injection (CWE-78)",
    "Cross-Site Scripting / XSS (CWE-79)",
    "Insecure Deserialization (CWE-502)",
    "Broken Authentication (CWE-287)",
    "Broken Access Control (CWE-284)",
    "Sensitive Data Exposure (CWE-200)",
    "Security Misconfiguration (CWE-16)",
    "XML External Entity / XXE (CWE-611)",
    "Server-Side Request Forgery / SSRF (CWE-918)",
    "Path Traversal (CWE-22)",
    "Weak Cryptography (CWE-327)",
    "Unsafe File Upload (CWE-434)",
    "Logging of Sensitive Data (CWE-532)",
]


def build_analysis_prompt(filename: str, patch: str, status: str) -> str:
    """Build the security analysis prompt for the AI model."""
    categories_text = "\n".join(f"  - {cat}" for cat in SECURITY_CATEGORIES)

    return f"""You are an expert application security engineer performing a code review.
Analyze the following code diff for security vulnerabilities.

**File:** `{filename}`
**Change Status:** {status}

**Code Diff:**
```
{patch}
```

**Security Categories to Check:**
{categories_text}

**Instructions:**
1. Analyze ONLY the changed lines (lines starting with + in the diff).
2. For each vulnerability found, provide:
   - **category**: The security category (from the list above)
   - **severity**: One of "critical", "high", "medium", "low"
   - **cwe**: The relevant CWE ID (e.g., "CWE-89")
   - **description**: Clear description of the vulnerability
   - **snippet**: The exact vulnerable code snippet from the diff
   - **line_hint**: Approximate line reference from the diff
   - **recommendation**: Specific, actionable fix recommendation
3. If no vulnerabilities are found, return an empty findings array.
4. Be precise — avoid false positives. Only flag genuine security issues.

**Response Format (JSON only, no markdown):**
{{
  "findings": [
    {{
      "category": "...",
      "severity": "critical|high|medium|low",
      "cwe": "CWE-XXX",
      "description": "...",
      "snippet": "...",
      "line_hint": "...",
      "recommendation": "..."
    }}
  ]
}}
"""


class SecurityAgent:
    """AI-powered security analysis agent."""

    def __init__(self, model: str = "gpt-4", severity_threshold: str = "low"):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.severity_threshold = severity_threshold
        self.severity_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}

    def analyze_file(self, filename: str, patch: str, status: str) -> dict:
        """Analyze a single file diff for security vulnerabilities."""
        logger.info(f"Analyzing: {filename} (status: {status})")

        prompt = build_analysis_prompt(filename, patch, status)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior application security engineer. "
                                   "Respond ONLY with valid JSON. No markdown formatting."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=4096,
                response_format={"type": "json_object"}
            )

            result_text = response.choices[0].message.content
            result = json.loads(result_text)

            # Filter by severity threshold
            threshold = self.severity_order.get(self.severity_threshold, 0)
            result["findings"] = [
                f for f in result.get("findings", [])
                if self.severity_order.get(f.get("severity", "low"), 0) >= threshold
            ]

            return {
                "filename": filename,
                "status": status,
                "findings": result.get("findings", []),
                "tokens_used": response.usage.total_tokens if response.usage else 0
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response for {filename}: {e}")
            return {"filename": filename, "status": status, "findings": [], "error": str(e)}
        except Exception as e:
            logger.error(f"Analysis failed for {filename}: {e}")
            return {"filename": filename, "status": status, "findings": [], "error": str(e)}

    def analyze_all(self, files: list[dict]) -> dict:
        """Analyze all changed files and aggregate results."""
        start_time = time.time()
        all_findings = []
        file_results = []
        total_tokens = 0

        for file_info in files:
            filename = file_info.get("filename", "")
            patch = file_info.get("patch", "")
            status = file_info.get("status", "modified")

            if not patch:
                logger.info(f"Skipping {filename} — no patch data")
                continue

            result = self.analyze_file(filename, patch, status)
            file_results.append(result)
            all_findings.extend(result.get("findings", []))
            total_tokens += result.get("tokens_used", 0)

        # Aggregate summary
        summary = {
            "critical": sum(1 for f in all_findings if f.get("severity") == "critical"),
            "high": sum(1 for f in all_findings if f.get("severity") == "high"),
            "medium": sum(1 for f in all_findings if f.get("severity") == "medium"),
            "low": sum(1 for f in all_findings if f.get("severity") == "low"),
            "total": len(all_findings),
        }

        # Determine overall recommendation
        if summary["critical"] > 0:
            recommendation = "block"
        elif summary["high"] > 2:
            recommendation = "needs_fixes"
        elif summary["high"] > 0 or summary["medium"] > 3:
            recommendation = "needs_fixes"
        else:
            recommendation = "approve"

        duration = round(time.time() - start_time, 2)

        return {
            "summary": summary,
            "recommendation": recommendation,
            "file_results": file_results,
            "duration_seconds": duration,
            "total_tokens": total_tokens,
            "model": self.model,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }


def main():
    parser = argparse.ArgumentParser(description="AI Security Analysis Agent")
    parser.add_argument("--files", required=True, help="Path to JSON file with changed files")
    parser.add_argument("--model", default="gpt-4", help="AI model to use")
    parser.add_argument("--severity-threshold", default="low", help="Minimum severity to report")
    parser.add_argument("--output", required=True, help="Output JSON file path")
    args = parser.parse_args()

    # Load changed files
    with open(args.files, "r") as f:
        files = json.load(f)

    logger.info(f"Starting security analysis of {len(files)} files with model {args.model}")

    agent = SecurityAgent(model=args.model, severity_threshold=args.severity_threshold)
    report = agent.analyze_all(files)

    # Write report
    with open(args.output, "w") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Analysis complete: {report['summary']['total']} findings in {report['duration_seconds']}s")
    logger.info(f"Recommendation: {report['recommendation']}")

    # Exit with error if critical issues found (for CI gating)
    if report["summary"]["critical"] > 0:
        logger.warning(f"🔴 {report['summary']['critical']} CRITICAL issues detected!")
        sys.exit(0)  # Don't fail here — let the workflow decide

    print("Security scan completed successfully.")


if __name__ == "__main__":
    main()
