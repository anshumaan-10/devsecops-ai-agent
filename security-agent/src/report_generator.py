"""
Security Report Generator
===========================
Converts raw JSON analysis results into formatted Markdown PR comments.
"""

import json
import sys
import argparse
import logging
import time
import uuid

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SEVERITY_ICONS = {
    "critical": "🔴",
    "high": "🟠",
    "medium": "🟡",
    "low": "🔵",
}

RECOMMENDATION_MAP = {
    "approve": ("✅", "Approve", "No critical or high-severity issues found. Code is safe to merge."),
    "needs_fixes": ("⚠️", "Needs Fixes", "Security issues detected that should be addressed before merging."),
    "block": ("❌", "Block Merge", "Critical vulnerabilities found. Do NOT merge until resolved."),
}


def generate_markdown_report(report: dict) -> str:
    """Generate a formatted Markdown security report for a PR comment."""
    summary = report.get("summary", {})
    recommendation_key = report.get("recommendation", "approve")
    rec_icon, rec_label, rec_desc = RECOMMENDATION_MAP.get(
        recommendation_key, RECOMMENDATION_MAP["approve"]
    )

    scan_id = f"scan-{uuid.uuid4().hex[:8]}"
    timestamp = report.get("timestamp", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    duration = report.get("duration_seconds", 0)
    model = report.get("model", "gpt-4")

    lines = []

    # Header
    lines.append("## 🔐 AI Security Scan Report")
    lines.append("")
    lines.append(f"**Scan ID:** `{scan_id}` | **Date:** {timestamp} | **Duration:** {duration}s | **Model:** {model}")
    lines.append("")

    # Summary Table
    lines.append("### 📊 Summary")
    lines.append("")
    lines.append("| Severity | Count |")
    lines.append("|----------|-------|")
    lines.append(f"| {SEVERITY_ICONS['critical']} Critical | {summary.get('critical', 0)} |")
    lines.append(f"| {SEVERITY_ICONS['high']} High | {summary.get('high', 0)} |")
    lines.append(f"| {SEVERITY_ICONS['medium']} Medium | {summary.get('medium', 0)} |")
    lines.append(f"| {SEVERITY_ICONS['low']} Low | {summary.get('low', 0)} |")
    lines.append(f"| **Total** | **{summary.get('total', 0)}** |")
    lines.append("")

    # Findings by file
    file_results = report.get("file_results", [])
    has_findings = any(fr.get("findings") for fr in file_results)

    if has_findings:
        lines.append("---")
        lines.append("")
        lines.append("### 🔎 Findings")
        lines.append("")

        finding_num = 0
        for file_result in file_results:
            findings = file_result.get("findings", [])
            if not findings:
                continue

            filename = file_result.get("filename", "unknown")

            # Sort findings by severity (critical first)
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            findings.sort(key=lambda f: severity_order.get(f.get("severity", "low"), 4))

            for finding in findings:
                finding_num += 1
                severity = finding.get("severity", "low")
                icon = SEVERITY_ICONS.get(severity, "⚪")
                category = finding.get("category", "Unknown")
                cwe = finding.get("cwe", "N/A")
                description = finding.get("description", "No description")
                snippet = finding.get("snippet", "")
                line_hint = finding.get("line_hint", "")
                recommendation = finding.get("recommendation", "No recommendation")

                lines.append(f"#### {icon} {severity.upper()} — {category}")
                lines.append(f"- **File:** `{filename}`{f' (Line {line_hint})' if line_hint else ''}")
                lines.append(f"- **CWE:** {cwe}")
                lines.append(f"- **Description:** {description}")

                if snippet:
                    lines.append(f"- **Vulnerable Code:**")
                    lines.append(f"  ```")
                    lines.append(f"  {snippet}")
                    lines.append(f"  ```")

                lines.append(f"- **Recommendation:** {recommendation}")
                lines.append("")

    else:
        lines.append("### ✅ No Security Issues Found")
        lines.append("")
        lines.append("The AI analysis did not detect any security vulnerabilities in the changed files.")
        lines.append("")

    # Overall Recommendation
    lines.append("---")
    lines.append("")
    lines.append("### 🏁 Overall Recommendation")
    lines.append("")
    lines.append(f"{rec_icon} **{rec_label}** — {rec_desc}")
    lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append(
        "<sub>🤖 Powered by <b>DevSecOps AI Security Agent</b> | "
        f"Model: {model} | "
        f"Tokens used: {report.get('total_tokens', 'N/A')} | "
        f"<a href='https://github.com/anshumaan-10/devsecops-ai-agent'>View Source</a></sub>"
    )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Security Report Generator")
    parser.add_argument("--input", required=True, help="Input JSON report file")
    parser.add_argument("--format", default="markdown", choices=["markdown", "json"])
    parser.add_argument("--output", required=True, help="Output file path")
    args = parser.parse_args()

    with open(args.input, "r") as f:
        report = json.load(f)

    if args.format == "markdown":
        output = generate_markdown_report(report)
    else:
        output = json.dumps(report, indent=2)

    with open(args.output, "w") as f:
        f.write(output)

    logger.info(f"Report generated: {args.output}")
    logger.info(f"Total findings: {report.get('summary', {}).get('total', 0)}")


if __name__ == "__main__":
    main()
