#!/bin/bash

# =================================================================
# Place 2 Backend Starter - Enhanced Linux/Mac
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
echo -e "${BLUE}  Place 2 Backend (Show Room) - Enhanced${NC}"
echo -e "${BLUE}=====================================================${NC}"

echo "📁 Project Directory: $PROJECT_DIR"
echo -e "${BLUE}🏬 Starting Place 2 Backend (Show Room)...${NC}"
echo

# Change to project directory
cd "$PROJECT_DIR"

# Check virtual environment
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo -e "${RED}❌ Virtual environment not found${NC}"
    echo "Please run setup_enhanced.sh first"
    exit 1
fi

# Check backend source file
if [ ! -f "src/biometric_flow/backend/place_backend.py" ]; then
    echo -e "${RED}❌ Backend source file not found: src/biometric_flow/backend/place_backend.py${NC}"
    exit 1
fi

# Check config file
if [ ! -f "config/devices_config_place2.json" ]; then
    echo -e "${RED}❌ Configuration file not found: config/devices_config_place2.json${NC}"
    exit 1
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Set environment variables for Place 2
export BACKEND_NAME="Place_2_ShowRoom"
export BACKEND_PORT="8001"
export BACKEND_LOCATION="Show Room Complex"
export DEVICES_CONFIG_FILE="config/devices_config_place2.json"
export PYTHONPATH="$PROJECT_DIR/src"

echo -e "${GREEN}⚙️  Configuration:${NC}"
echo "   Backend Name: $BACKEND_NAME"
echo "   Port: $BACKEND_PORT"
echo "   Location: $BACKEND_LOCATION"
echo "   Config File: $DEVICES_CONFIG_FILE"
echo "   Python Path: $PYTHONPATH"
echo

echo -e "${GREEN}🚀 Starting backend service...${NC}"
python -m biometric_flow.backend.place_backend

echo
echo -e "${RED}❌ Backend service stopped${NC}"
