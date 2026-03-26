"""
File Analyzer
==============
Fetches and filters changed files from a GitHub Pull Request.
Handles binary file detection, size filtering, and diff extraction.
"""

import json
import os
import sys
import argparse
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# File extensions to analyze
ANALYZABLE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rb", ".php",
    ".cs", ".cpp", ".c", ".h", ".rs", ".swift", ".kt", ".scala",
    ".yaml", ".yml", ".json", ".xml", ".toml", ".ini", ".cfg", ".conf",
    ".env", ".sh", ".bash", ".zsh", ".ps1", ".bat", ".cmd",
    ".sql", ".graphql", ".proto",
    ".html", ".htm", ".css", ".scss",
    ".tf", ".hcl",  # Terraform / HCL
    "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
}

# Files to always skip
SKIP_PATTERNS = {
    "package-lock.json", "yarn.lock", "poetry.lock", "Pipfile.lock",
    "go.sum", "Cargo.lock", "composer.lock",
    ".min.js", ".min.css", ".map",
}

# Binary file extensions to skip
BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".bmp", ".webp",
    ".woff", ".woff2", ".ttf", ".eot",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".zip", ".tar", ".gz", ".rar", ".7z",
    ".exe", ".dll", ".so", ".dylib",
    ".pyc", ".pyo", ".class", ".o",
}


def should_analyze(filename: str, file_size_kb: float, max_size_kb: int) -> tuple[bool, str]:
    """Determine if a file should be analyzed."""
    # Check binary extensions
    for ext in BINARY_EXTENSIONS:
        if filename.lower().endswith(ext):
            return False, "binary file"

    # Check skip patterns
    for pattern in SKIP_PATTERNS:
        if pattern in filename:
            return False, "lock/minified file"

    # Check file size
    if file_size_kb > max_size_kb:
        return False, f"exceeds size limit ({file_size_kb}KB > {max_size_kb}KB)"

    # Check analyzable extensions
    has_valid_ext = False
    for ext in ANALYZABLE_EXTENSIONS:
        if filename.lower().endswith(ext) or filename.endswith(ext):
            has_valid_ext = True
            break

    # Also analyze files without extensions (like Dockerfile)
    basename = os.path.basename(filename)
    if basename in ANALYZABLE_EXTENSIONS:
        has_valid_ext = True

    if not has_valid_ext:
        # Still analyze if it looks like a config/code file
        if "." not in basename:
            return True, "no extension — analyzing as potential config"
        return False, "unsupported file type"

    return True, "analyzable"


def filter_pr_files(files: list[dict], max_file_size_kb: int = 500) -> list[dict]:
    """Filter PR files to only include analyzable ones."""
    filtered = []
    skipped = []

    for file_info in files:
        filename = file_info.get("filename", "")
        patch = file_info.get("patch", "")
        status = file_info.get("status", "modified")
        changes = file_info.get("changes", 0)

        # Estimate file size from patch
        patch_size_kb = len(patch.encode("utf-8")) / 1024 if patch else 0

        should, reason = should_analyze(filename, patch_size_kb, max_file_size_kb)

        if should and patch:
            filtered.append({
                "filename": filename,
                "patch": patch,
                "status": status,
                "changes": changes,
            })
            logger.info(f"✅ Analyzing: {filename} ({status}, {changes} changes)")
        else:
            skip_reason = reason if not should else "no patch data"
            skipped.append({"filename": filename, "reason": skip_reason})
            logger.info(f"⏭️  Skipping: {filename} — {skip_reason}")

    logger.info(f"📊 Files: {len(filtered)} to analyze, {len(skipped)} skipped")
    return filtered


def main():
    """Fetch and filter changed files from a GitHub PR."""
    parser = argparse.ArgumentParser(description="PR File Analyzer")
    parser.add_argument("--owner", required=True, help="Repository owner")
    parser.add_argument("--repo", required=True, help="Repository name")
    parser.add_argument("--pr-number", required=True, type=int, help="PR number")
    parser.add_argument("--max-file-size", type=int, default=500, help="Max file size in KB")
    parser.add_argument("--output", required=True, help="Output JSON file path")
    args = parser.parse_args()

    # Import here to avoid circular dependencies
    from github_client import GitHubClient

    client = GitHubClient()
    raw_files = client.get_pr_files(args.owner, args.repo, args.pr_number)
    filtered_files = filter_pr_files(raw_files, args.max_file_size)

    with open(args.output, "w") as f:
        json.dump(filtered_files, f, indent=2)

    logger.info(f"Wrote {len(filtered_files)} files to {args.output}")


if __name__ == "__main__":
    main()
