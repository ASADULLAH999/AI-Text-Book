#!/bin/bash

###############################################################################
# Infrastructure Verification Script
#
# This script verifies that all infrastructure components are properly
# configured and accessible:
# - T004: Qdrant Cloud collection
# - T005: Neon Serverless Postgres database
# - T008: GitHub branch protection rules
#
# Usage:
#   ./scripts/verify_infrastructure.sh
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Function to print section headers
print_header() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    printf "${BLUE}║  %-60s  ║${NC}\n" "$1"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Function to run a check
run_check() {
    local name=$1
    local command=$2
    local required=${3:-true}

    echo -n "Checking $name... "

    if eval "$command" &> /dev/null; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((PASSED++))
        return 0
    else
        if [ "$required" = true ]; then
            echo -e "${RED}❌ FAIL${NC}"
            ((FAILED++))
        else
            echo -e "${YELLOW}⚠️  WARN${NC}"
            ((WARNINGS++))
        fi
        return 1
    fi
}

# Function to check environment variables
check_env_vars() {
    local all_set=true

    echo "Checking environment variables:"

    # Qdrant variables
    if [ -z "$QDRANT_URL" ]; then
        echo -e "  ${RED}❌ QDRANT_URL not set${NC}"
        all_set=false
    else
        echo -e "  ${GREEN}✅ QDRANT_URL: ${QDRANT_URL:0:30}...${NC}"
    fi

    if [ -z "$QDRANT_API_KEY" ]; then
        echo -e "  ${RED}❌ QDRANT_API_KEY not set${NC}"
        all_set=false
    else
        echo -e "  ${GREEN}✅ QDRANT_API_KEY: ${QDRANT_API_KEY:0:10}...${NC}"
    fi

    # Neon/Postgres variables
    if [ -z "$DATABASE_URL" ]; then
        echo -e "  ${RED}❌ DATABASE_URL not set${NC}"
        all_set=false
    else
        echo -e "  ${GREEN}✅ DATABASE_URL: ${DATABASE_URL:0:30}...${NC}"
    fi

    # OpenAI variables (bonus check)
    if [ -z "$OPENAI_API_KEY" ]; then
        echo -e "  ${YELLOW}⚠️  OPENAI_API_KEY not set (optional for infrastructure setup)${NC}"
    else
        echo -e "  ${GREEN}✅ OPENAI_API_KEY: ${OPENAI_API_KEY:0:10}...${NC}"
    fi

    if [ "$all_set" = true ]; then
        ((PASSED++))
    else
        ((FAILED++))
        echo ""
        echo -e "${YELLOW}💡 Copy .env.template to .env and fill in your credentials${NC}"
    fi

    return $([ "$all_set" = true ] && echo 0 || echo 1)
}

# Main verification
main() {
    print_header "Infrastructure Verification - Tasks T004, T005, T008"

    # Load environment variables if .env exists
    if [ -f .env ]; then
        echo -e "${GREEN}Loading environment from .env file...${NC}"
        set -a
        source .env
        set +a
    else
        echo -e "${YELLOW}⚠️  No .env file found. Environment variables must be set manually.${NC}"
        echo ""
    fi

    # Section 1: Environment Variables
    print_header "1. Environment Variables"
    check_env_vars

    # Section 2: Python Dependencies
    print_header "2. Python Dependencies"
    run_check "Python 3.11+" "python3 --version | grep -E 'Python 3\.(11|12|13)'"
    run_check "pip installed" "pip --version"
    run_check "qdrant-client" "python3 -c 'import qdrant_client'" false
    run_check "psycopg2" "python3 -c 'import psycopg2'" false

    if [ $FAILED -gt 0 ]; then
        echo ""
        echo -e "${YELLOW}💡 Install dependencies: pip install -r api/requirements.txt${NC}"
    fi

    # Section 3: Qdrant Cloud (T004)
    print_header "3. T004 - Qdrant Cloud Collection"

    if [ -n "$QDRANT_URL" ] && [ -n "$QDRANT_API_KEY" ]; then
        echo "Testing Qdrant connection..."
        if python3 api/scripts/provision_qdrant.py --check 2>/dev/null; then
            echo -e "${GREEN}✅ Qdrant collection 'textbook_chunks' exists and is accessible${NC}"
            ((PASSED++))

            # Get collection info
            echo ""
            python3 api/scripts/provision_qdrant.py --info 2>/dev/null || true
        else
            echo -e "${RED}❌ Qdrant collection not found or not accessible${NC}"
            ((FAILED++))
            echo ""
            echo -e "${YELLOW}💡 To create the collection:${NC}"
            echo "    python3 api/scripts/provision_qdrant.py --create"
        fi
    else
        echo -e "${RED}❌ Qdrant credentials not configured${NC}"
        ((FAILED++))
        echo ""
        echo -e "${YELLOW}💡 See docs/INFRASTRUCTURE_SETUP.md for Qdrant setup instructions${NC}"
    fi

    # Section 4: Neon Postgres (T005)
    print_header "4. T005 - Neon Serverless Postgres"

    if [ -n "$DATABASE_URL" ]; then
        echo "Testing Neon database connection..."
        if python3 api/scripts/provision_neon.py --check 2>/dev/null; then
            echo -e "${GREEN}✅ Neon database is accessible${NC}"
            ((PASSED++))

            # Get database status
            echo ""
            python3 api/scripts/provision_neon.py --status 2>/dev/null || true
        else
            echo -e "${RED}❌ Neon database not accessible${NC}"
            ((FAILED++))
            echo ""
            echo -e "${YELLOW}💡 To initialize the database:${NC}"
            echo "    python3 api/scripts/provision_neon.py --init"
        fi
    else
        echo -e "${RED}❌ Database credentials not configured${NC}"
        ((FAILED++))
        echo ""
        echo -e "${YELLOW}💡 See docs/INFRASTRUCTURE_SETUP.md for Neon setup instructions${NC}"
    fi

    # Section 5: GitHub Branch Protection (T008)
    print_header "5. T008 - GitHub Branch Protection"

    if command -v gh &> /dev/null; then
        if gh auth status &> /dev/null 2>&1; then
            echo "Checking branch protection for 'main' branch..."

            # Get repository info
            if REPO_INFO=$(gh repo view --json nameWithOwner -q '.nameWithOwner' 2>/dev/null); then
                echo "Repository: $REPO_INFO"

                # Check branch protection
                if gh api "repos/$REPO_INFO/branches/main/protection" &> /dev/null; then
                    echo -e "${GREEN}✅ Branch protection is enabled on 'main' branch${NC}"
                    ((PASSED++))

                    echo ""
                    echo "Protection rules:"
                    gh api "repos/$REPO_INFO/branches/main/protection" 2>/dev/null | jq '{
                        "required_status_checks": .required_status_checks.contexts,
                        "required_approving_reviews": .required_pull_request_reviews.required_approving_review_count,
                        "enforce_admins": .enforce_admins.enabled,
                        "allow_force_pushes": .allow_force_pushes.enabled
                    }' 2>/dev/null || echo "  (Unable to parse protection details)"
                else
                    echo -e "${YELLOW}⚠️  Branch protection is not configured${NC}"
                    ((WARNINGS++))
                    echo ""
                    echo -e "${YELLOW}💡 To set up branch protection:${NC}"
                    echo "    .github/scripts/setup_branch_protection.sh"
                fi
            else
                echo -e "${YELLOW}⚠️  Not in a GitHub repository directory${NC}"
                ((WARNINGS++))
            fi
        else
            echo -e "${YELLOW}⚠️  GitHub CLI not authenticated${NC}"
            ((WARNINGS++))
            echo ""
            echo -e "${YELLOW}💡 Authenticate with: gh auth login${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  GitHub CLI (gh) not installed${NC}"
        ((WARNINGS++))
        echo ""
        echo -e "${YELLOW}💡 Install from: https://cli.github.com/${NC}"
    fi

    # Summary
    print_header "Verification Summary"

    echo "Results:"
    echo -e "  ${GREEN}✅ Passed:   $PASSED${NC}"
    echo -e "  ${RED}❌ Failed:   $FAILED${NC}"
    echo -e "  ${YELLOW}⚠️  Warnings: $WARNINGS${NC}"
    echo ""

    if [ $FAILED -eq 0 ]; then
        echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║  ✅ ALL CRITICAL INFRASTRUCTURE CHECKS PASSED!                 ║${NC}"
        echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo "Your infrastructure is ready for development! 🎉"
        echo ""
        echo "Next steps:"
        echo "  - Process textbook content (T024)"
        echo "  - Validate ingestion pipeline (T025)"
        echo "  - Begin User Story 1 implementation (T026+)"
        exit 0
    else
        echo -e "${RED}╔════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${RED}║  ❌ SOME INFRASTRUCTURE CHECKS FAILED                          ║${NC}"
        echo -e "${RED}╚════════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo "Please resolve the failures above before proceeding."
        echo ""
        echo "For detailed setup instructions:"
        echo "  - Read: docs/INFRASTRUCTURE_SETUP.md"
        exit 1
    fi
}

# Run main function
main
