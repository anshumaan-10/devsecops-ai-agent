"""
GitHub API Client
==================
Handles all GitHub API interactions: fetching PR data, changed files,
and posting security report comments.
"""

import os
import sys
import json
import argparse
import logging
import hashlib
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"


class GitHubClient:
    """GitHub API client for PR security scanning."""

    def __init__(self, token: str = None):
        self.token = token or os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GitHub token is required (GH_TOKEN or GITHUB_TOKEN env var)")

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_pr_files(self, owner: str, repo: str, pr_number: int) -> list[dict]:
        """Fetch changed files for a pull request."""
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        all_files = []
        page = 1

        while True:
            response = self.session.get(url, params={"per_page": 100, "page": page})
            response.raise_for_status()
            files = response.json()

            if not files:
                break

            all_files.extend(files)
            page += 1

            # Check for rate limiting
            remaining = int(response.headers.get("X-RateLimit-Remaining", 100))
            if remaining < 10:
                logger.warning(f"GitHub API rate limit low: {remaining} remaining")

        logger.info(f"Fetched {len(all_files)} changed files from PR #{pr_number}")
        return all_files

    def post_pr_comment(self, owner: str, repo: str, pr_number: int, body: str) -> dict:
        """Post a comment on a pull request. Handles idempotency by checking for existing comments."""
        # Check for existing security scan comments to avoid duplicates
        comment_marker = "<!-- ai-security-scan-report -->"
        existing = self._find_existing_comment(owner, repo, pr_number, comment_marker)

        body_with_marker = f"{comment_marker}\n{body}"

        if existing:
            # Update existing comment instead of creating duplicate
            url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues/comments/{existing['id']}"
            response = self.session.patch(url, json={"body": body_with_marker})
            response.raise_for_status()
            logger.info(f"Updated existing security comment (ID: {existing['id']})")
        else:
            # Create new comment
            url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues/{pr_number}/comments"
            response = self.session.post(url, json={"body": body_with_marker})
            response.raise_for_status()
            logger.info(f"Posted new security comment on PR #{pr_number}")

        return response.json()

    def _find_existing_comment(self, owner: str, repo: str, pr_number: int, marker: str) -> dict | None:
        """Find an existing comment with the given marker."""
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues/{pr_number}/comments"
        response = self.session.get(url, params={"per_page": 100})
        response.raise_for_status()

        for comment in response.json():
            if marker in comment.get("body", ""):
                return comment

        return None

    def get_pr_info(self, owner: str, repo: str, pr_number: int) -> dict:
        """Fetch PR metadata."""
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()


def main():
    parser = argparse.ArgumentParser(description="GitHub API Client for Security Agent")
    parser.add_argument("--action", required=True, choices=["get-files", "post-comment", "get-pr-info"])
    parser.add_argument("--owner", required=True, help="Repository owner")
    parser.add_argument("--repo", required=True, help="Repository name")
    parser.add_argument("--pr-number", required=True, type=int, help="Pull request number")
    parser.add_argument("--comment-file", help="Path to markdown file for comment body")
    parser.add_argument("--output", help="Output file path")
    args = parser.parse_args()

    client = GitHubClient()

    if args.action == "get-files":
        files = client.get_pr_files(args.owner, args.repo, args.pr_number)
        if args.output:
            with open(args.output, "w") as f:
                json.dump(files, f, indent=2)
        else:
            print(json.dumps(files, indent=2))

    elif args.action == "post-comment":
        if not args.comment_file:
            logger.error("--comment-file is required for post-comment action")
            sys.exit(1)

        with open(args.comment_file, "r") as f:
            body = f.read()

        result = client.post_pr_comment(args.owner, args.repo, args.pr_number, body)
        logger.info(f"Comment posted: {result.get('html_url', 'N/A')}")

    elif args.action == "get-pr-info":
        info = client.get_pr_info(args.owner, args.repo, args.pr_number)
        print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
