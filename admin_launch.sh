#!/bin/bash
# Admin Mode Launcher for Research Discovery Hub
# 
# TODO: DELETE THIS FILE BEFORE PRODUCTION DEPLOYMENT
# This script is for development/testing only
#
# This script allows developers to bypass the API key configuration screen
# by loading keys directly from environment variables or a backup .env file.
#
# Usage:
#   ./admin_launch.sh              - Launch with existing .env backup
#   ./admin_launch.sh restore      - Restore .env from latest backup
#   ./admin_launch.sh clean        - Remove .env and launch with API config screen

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║        🔧 ADMIN MODE - Research Discovery Hub 🔧         ║"
echo "║                                                           ║"
echo "║  ⚠️  FOR DEVELOPMENT/TESTING ONLY - NOT FOR PRODUCTION  ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Handle command arguments
COMMAND="${1:-launch}"

case "$COMMAND" in
    restore)
        echo -e "${YELLOW}🔄 Restoring .env from backup...${NC}"
        
        # Find the most recent backup
        LATEST_BACKUP=$(ls -t .env.backup* 2>/dev/null | head -1)
        
        if [ -z "$LATEST_BACKUP" ]; then
            echo -e "${RED}❌ No backup .env files found${NC}"
            echo "   Available backups:"
            ls -la .env* 2>/dev/null || echo "   (none)"
            exit 1
        fi
        
        echo "   Found backup: $LATEST_BACKUP"
        cp "$LATEST_BACKUP" .env
        echo -e "${GREEN}✅ Restored .env from $LATEST_BACKUP${NC}"
        echo ""
        echo "Now you can run: python main.py"
        exit 0
        ;;
        
    clean)
        echo -e "${YELLOW}🧹 Cleaning .env file...${NC}"
        
        if [ -f .env ]; then
            TIMESTAMP=$(date +%s)
            mv .env ".env.backup.$TIMESTAMP"
            echo -e "${GREEN}✅ Backed up .env to .env.backup.$TIMESTAMP${NC}"
        else
            echo "   No .env file to clean"
        fi
        
        echo ""
        echo "Now you can run: python main.py (will show API config screen)"
        exit 0
        ;;
        
    launch)
        # Continue with admin launch
        ;;
        
    *)
        echo -e "${RED}❌ Unknown command: $COMMAND${NC}"
        echo ""
        echo "Usage:"
        echo "  ./admin_launch.sh              - Launch with admin mode"
        echo "  ./admin_launch.sh restore      - Restore .env from backup"
        echo "  ./admin_launch.sh clean        - Remove .env (show API config screen)"
        exit 1
        ;;
esac

# Check if .env file exists
if [ -f .env ]; then
    echo -e "${GREEN}✓ Found .env file${NC}"
    echo "  Will use existing API keys"
    echo ""
    echo "Starting application..."
    python main.py
    exit 0
fi

# No .env file - check for backups
echo -e "${YELLOW}⚠️  No .env file found${NC}"
echo ""

# Find the most recent backup
LATEST_BACKUP=$(ls -t .env.backup* 2>/dev/null | head -1)

if [ -n "$LATEST_BACKUP" ]; then
    echo -e "${BLUE}Found backup: $LATEST_BACKUP${NC}"
    echo ""
    read -p "Restore from backup? (y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp "$LATEST_BACKUP" .env
        echo -e "${GREEN}✅ Restored .env from backup${NC}"
        echo ""
        echo "Starting application..."
        python main.py
        exit 0
    fi
fi

# No backup or user declined - try to use environment variables
echo ""
echo -e "${YELLOW}Checking for API keys in environment variables...${NC}"

if [ -n "$GEMINI_API_KEY" ] && [ -n "$SERPAPI_KEY" ]; then
    echo -e "${GREEN}✓ Found API keys in environment${NC}"
    echo "  GEMINI_API_KEY: ${GEMINI_API_KEY:0:10}..."
    echo "  SERPAPI_KEY: ${SERPAPI_KEY:0:10}..."
    echo ""
    echo "Starting application in ADMIN MODE..."
    echo ""
    export ADMIN_MODE=true
    python main.py
else
    echo -e "${RED}❌ No API keys found in environment variables${NC}"
    echo ""
    echo "Options:"
    echo "  1. Set environment variables:"
    echo "     export GEMINI_API_KEY='your-key'"
    echo "     export SERPAPI_KEY='your-key'"
    echo "     export ADMIN_MODE=true"
    echo "     python main.py"
    echo ""
    echo "  2. Restore from backup:"
    echo "     ./admin_launch.sh restore"
    echo ""
    echo "  3. Launch normally (will show API config screen):"
    echo "     python main.py"
    exit 1
fi
