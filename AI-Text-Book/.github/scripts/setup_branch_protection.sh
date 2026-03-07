#!/bin/bash

###############################################################################
# GitHub Branch Protection Setup Script
#
# This script configures branch protection rules for the AI-Text-Book repository.
# It sets up protection for the main branch with the following rules:
#
# - Require pull request reviews before merging
# - Require status checks to pass
# - Require conversation resolution
# - Prevent force pushes and deletions
# - Include administrators in restrictions
#
# Prerequisites:
# - GitHub CLI (gh) installed and authenticated
# - Repository must exist on GitHub
# - User must have admin access to the repository
#
# Usage:
#   ./setup_branch_protection.sh [--dry-run] [--branch BRANCH_NAME]
#
# Options:
#   --dry-run        Show what would be done without making changes
#   --branch NAME    Branch to protect (default: main)
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DRY_RUN=false
BRANCH_NAME="main"
REPO_OWNER=""
REPO_NAME=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --branch)
            BRANCH_NAME="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [--dry-run] [--branch BRANCH_NAME]"
            echo ""
            echo "Options:"
            echo "  --dry-run        Show what would be done without making changes"
            echo "  --branch NAME    Branch to protect (default: main)"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Function to print section headers
print_header() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  $1${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Function to check if GitHub CLI is installed
check_gh_cli() {
    if ! command -v gh &> /dev/null; then
        echo -e "${RED}❌ ERROR: GitHub CLI (gh) is not installed${NC}"
        echo ""
        echo "Install it from: https://cli.github.com/"
        echo ""
        echo "Installation commands:"
        echo "  macOS:    brew install gh"
        echo "  Windows:  winget install GitHub.cli"
        echo "  Linux:    See https://github.com/cli/cli/blob/trunk/docs/install_linux.md"
        exit 1
    fi
    echo -e "${GREEN}✅ GitHub CLI is installed${NC}"
}

# Function to check if user is authenticated
check_gh_auth() {
    if ! gh auth status &> /dev/null; then
        echo -e "${RED}❌ ERROR: Not authenticated with GitHub CLI${NC}"
        echo ""
        echo "Run: gh auth login"
        exit 1
    fi
    echo -e "${GREEN}✅ Authenticated with GitHub${NC}"
}

# Function to get repository information
get_repo_info() {
    # Try to get repo info from current directory
    if gh repo view &> /dev/null; then
        REPO_OWNER=$(gh repo view --json owner -q '.owner.login')
        REPO_NAME=$(gh repo view --json name -q '.name')
        echo -e "${GREEN}✅ Repository detected: ${REPO_OWNER}/${REPO_NAME}${NC}"
    else
        echo -e "${RED}❌ ERROR: Not in a GitHub repository directory${NC}"
        echo "Run this script from within your repository"
        exit 1
    fi
}

# Function to check if branch exists
check_branch_exists() {
    if ! gh api "repos/${REPO_OWNER}/${REPO_NAME}/branches/${BRANCH_NAME}" &> /dev/null; then
        echo -e "${RED}❌ ERROR: Branch '${BRANCH_NAME}' does not exist${NC}"
        echo ""
        echo "Create the branch first:"
        echo "  git checkout -b ${BRANCH_NAME}"
        echo "  git push -u origin ${BRANCH_NAME}"
        exit 1
    fi
    echo -e "${GREEN}✅ Branch '${BRANCH_NAME}' exists${NC}"
}

# Function to create branch protection rules
create_branch_protection() {
    local protection_config='{
        "required_status_checks": {
            "strict": true,
            "contexts": ["build", "test", "lint"]
        },
        "enforce_admins": true,
        "required_pull_request_reviews": {
            "dismiss_stale_reviews": true,
            "require_code_owner_reviews": false,
            "required_approving_review_count": 1,
            "require_last_push_approval": false
        },
        "restrictions": null,
        "required_linear_history": false,
        "allow_force_pushes": false,
        "allow_deletions": false,
        "block_creations": false,
        "required_conversation_resolution": true,
        "lock_branch": false,
        "allow_fork_syncing": true
    }'

    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}🔍 DRY RUN: Would apply the following protection rules to '${BRANCH_NAME}':${NC}"
        echo "$protection_config" | jq '.'
        echo ""
        echo -e "${YELLOW}No changes were made. Remove --dry-run to apply.${NC}"
        return 0
    fi

    echo -e "${BLUE}🔧 Applying branch protection rules to '${BRANCH_NAME}'...${NC}"

    if echo "$protection_config" | gh api \
        "repos/${REPO_OWNER}/${REPO_NAME}/branches/${BRANCH_NAME}/protection" \
        --method PUT \
        --input - > /dev/null 2>&1; then

        echo -e "${GREEN}✅ Branch protection rules applied successfully!${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed to apply branch protection rules${NC}"
        echo ""
        echo "Possible reasons:"
        echo "  - Insufficient permissions (need admin access)"
        echo "  - GitHub Actions workflows not yet created"
        echo "  - Repository settings conflict"
        return 1
    fi
}

# Function to verify protection rules
verify_protection() {
    echo -e "${BLUE}🔍 Verifying branch protection rules...${NC}"
    echo ""

    local protection_info=$(gh api "repos/${REPO_OWNER}/${REPO_NAME}/branches/${BRANCH_NAME}/protection" 2>&1)

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Branch protection is enabled${NC}"
        echo ""
        echo "Protection rules:"
        echo "$protection_info" | jq '{
            "required_status_checks": .required_status_checks.contexts,
            "required_approving_reviews": .required_pull_request_reviews.required_approving_review_count,
            "enforce_admins": .enforce_admins.enabled,
            "allow_force_pushes": .allow_force_pushes.enabled,
            "allow_deletions": .allow_deletions.enabled,
            "required_conversation_resolution": .required_conversation_resolution.enabled
        }'
    else
        echo -e "${YELLOW}⚠️  No branch protection rules currently set${NC}"
    fi
}

# Function to create status check workflows
create_status_check_workflows() {
    local workflows_dir=".github/workflows"

    echo -e "${BLUE}🔧 Creating GitHub Actions workflows for status checks...${NC}"

    mkdir -p "$workflows_dir"

    # Create CI workflow if it doesn't exist
    if [ ! -f "$workflows_dir/ci.yml" ]; then
        cat > "$workflows_dir/ci.yml" << 'EOF'
name: CI

on:
  push:
    branches: [main, develop, "**"]
  pull_request:
    branches: [main, develop]

jobs:
  build:
    name: Build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build application
        run: npm run build

  test:
    name: Test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install Python dependencies
        run: |
          pip install -r api/requirements.txt

      - name: Run Python tests
        run: |
          pytest api/tests/ --cov=api/src --cov-report=xml

  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run ESLint
        run: npm run lint
EOF

        echo -e "${GREEN}✅ Created .github/workflows/ci.yml${NC}"

        if [ "$DRY_RUN" = false ]; then
            echo -e "${YELLOW}⚠️  Remember to commit and push this workflow file:${NC}"
            echo "    git add .github/workflows/ci.yml"
            echo "    git commit -m 'ci: Add GitHub Actions workflow'"
            echo "    git push"
        fi
    else
        echo -e "${YELLOW}⚠️  CI workflow already exists${NC}"
    fi
}

# Main execution
main() {
    print_header "GitHub Branch Protection Setup"

    echo "Configuration:"
    echo "  Repository: Will be auto-detected"
    echo "  Branch: ${BRANCH_NAME}"
    echo "  Dry Run: ${DRY_RUN}"
    echo ""

    # Run checks
    print_header "Pre-flight Checks"
    check_gh_cli
    check_gh_auth
    get_repo_info
    check_branch_exists

    # Verify current protection
    print_header "Current Protection Status"
    verify_protection

    # Create workflows
    print_header "GitHub Actions Workflows"
    create_status_check_workflows

    # Apply protection rules
    print_header "Applying Branch Protection"
    if create_branch_protection; then
        echo ""
        print_header "Verification"
        verify_protection

        echo ""
        print_header "Success!"
        echo -e "${GREEN}✅ Branch protection setup complete!${NC}"
        echo ""
        echo "Next steps:"
        echo "  1. Review protection rules in GitHub web UI"
        echo "  2. Commit and push the CI workflow if created"
        echo "  3. Test by creating a pull request"
        echo ""
        echo "View rules: https://github.com/${REPO_OWNER}/${REPO_NAME}/settings/branches"
    else
        echo ""
        echo -e "${RED}❌ Setup failed. Please check the error messages above.${NC}"
        exit 1
    fi
}

# Run main function
main
