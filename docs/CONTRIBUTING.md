# Contributing to DevSecOps AI Security Agent

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/devsecops-ai-agent.git`
3. Create a feature branch: `git checkout -b feature/your-feature`
4. Make your changes
5. Run tests: `python -m pytest tests/`
6. Commit with conventional commits: `git commit -m "feat: add new security check"`
7. Push and create a Pull Request

## Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r security-agent/requirements.txt
pip install -r dev-requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-key"
export GITHUB_TOKEN="your-token"
```

## Code Standards

- **Python**: Follow PEP 8, use type hints, docstrings for all public functions
- **YAML**: Use 2-space indentation
- **Commits**: Follow [Conventional Commits](https://www.conventionalcommits.org/)

## Adding New Security Rules

1. Add the detection pattern to `security-agent/src/agent.py` → `SECURITY_CATEGORIES`
2. Update the AI prompt in `security-agent/prompts/security_analysis.txt`
3. Add test cases in the `vulnerable-app/` directory
4. Update `docs/SECURITY_RULES.md` with the new rule and OWASP/CWE mapping

## Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Docstrings added/updated
- [ ] Security rules documented
- [ ] No hardcoded secrets (even test ones should be clearly marked)

## Reporting Security Issues

If you find a real security vulnerability in the security agent itself (not the intentionally vulnerable test app), please report it responsibly via GitHub Security Advisories.
