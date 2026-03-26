#!/bin/bash
# ============================================================
# DevSecOps AI Security Agent — One-Click Setup Script
# ============================================================

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🔐 DevSecOps AI Security Agent — Setup${NC}"
echo "============================================="
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

command -v python3 >/dev/null 2>&1 || { echo -e "${RED}❌ Python 3 is required but not installed.${NC}"; exit 1; }
command -v pip >/dev/null 2>&1 || command -v pip3 >/dev/null 2>&1 || { echo -e "${RED}❌ pip is required but not installed.${NC}"; exit 1; }
command -v gh >/dev/null 2>&1 || echo -e "${YELLOW}⚠️  GitHub CLI (gh) not found. You'll need to set secrets manually.${NC}"

echo -e "${GREEN}✅ Prerequisites met${NC}"
echo ""

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install -r security-agent/requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Check for required secrets
echo -e "${YELLOW}Checking environment variables...${NC}"

if [ -z "${OPENAI_API_KEY:-}" ]; then
    echo -e "${YELLOW}⚠️  OPENAI_API_KEY not set in environment${NC}"
    echo "   Set it with: export OPENAI_API_KEY='your-key'"
    echo "   Or add it as a GitHub Actions secret"
else
    echo -e "${GREEN}✅ OPENAI_API_KEY is set${NC}"
fi

if [ -z "${GITHUB_TOKEN:-}" ] && [ -z "${GH_PAT:-}" ]; then
    echo -e "${YELLOW}⚠️  GITHUB_TOKEN/GH_PAT not set in environment${NC}"
    echo "   GitHub Actions provides GITHUB_TOKEN automatically"
    echo "   For enhanced permissions, add GH_PAT as a secret"
else
    echo -e "${GREEN}✅ GitHub token is set${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Add OPENAI_API_KEY to GitHub repo secrets"
echo "  2. Add GH_PAT to GitHub repo secrets (optional, for enhanced permissions)"
echo "  3. Push a branch and open a PR to trigger the security scan"
echo ""
echo "  For detailed docs, see: docs/WORKFLOW.md"
