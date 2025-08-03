#!/bin/bash

# =================================================================
# Unified Gateway Starter - Enhanced Linux/Mac
# =================================================================

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"

echo -e "${BLUE}=====================================================${NC}"
echo -e "${BLUE}  Unified Gateway Backend - Enhanced${NC}"
echo -e "${BLUE}=====================================================${NC}"

echo "📁 Project Directory: $PROJECT_DIR"
echo -e "${BLUE}🌐 Starting Unified Gateway Backend...${NC}"
echo

# Change to project directory
cd "$PROJECT_DIR"

# === Load .env from root project directory ===
if [ -f "$PROJECT_DIR/.env" ]; then
    echo -e "${GREEN}🔄 Loading environment variables from .env...${NC}"
    set -a
    source "$PROJECT_DIR/.env"
    set +a
else
    echo -e "${NC}⚠️  .env file not found in $PROJECT_DIR${NC}"
fi

# Check virtual environment
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo -e "${RED}❌ Virtual environment not found${NC}"
    echo "Please run setup_enhanced.sh first"
    exit 1
fi

# Check gateway source file
if [ ! -f "src/biometric_flow/backend/unified_gateway.py" ]; then
    echo -e "${RED}❌ Gateway source file not found: src/biometric_flow/backend/unified_gateway.py${NC}"
    exit 1
fi

# Check backends config file
if [ ! -f "config/unified_backends_config.json" ]; then
    echo -e "${RED}❌ Configuration file not found: config/unified_backends_config.json${NC}"
    exit 1
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Set additional environment variables for Unified Gateway
export GATEWAY_PORT="9000"
export FRONTEND_BACKEND_PORT="9001"
export ALLOWED_ORIGINS="http://localhost:8501,http://localhost:9001"
export PYTHONPATH="$PROJECT_DIR/src"

echo -e "${GREEN}⚙️  Configuration:${NC}"
echo "   Gateway Port: $GATEWAY_PORT"
echo "   Frontend Backend Port: $FRONTEND_BACKEND_PORT"
echo "   Allowed Origins: $ALLOWED_ORIGINS"
echo "   Python Path: $PYTHONPATH"
echo

echo -e "${GREEN}🚀 Starting unified gateway service...${NC}"
python -m biometric_flow.backend.unified_gateway

echo
echo -e "${RED}❌ Gateway service stopped${NC}"
