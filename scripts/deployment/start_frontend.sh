#!/bin/bash

# =================================================================
# Frontend Starter - Enhanced Linux/Mac
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
echo -e "${BLUE}  Streamlit Frontend - Enhanced${NC}"
echo -e "${BLUE}=====================================================${NC}"

echo "📁 Project Directory: $PROJECT_DIR"
echo -e "${BLUE}🖥️  Starting Streamlit Frontend...${NC}"
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

# Check frontend source file
if [ ! -f "src/biometric_flow/frontend/app.py" ]; then
    echo -e "${RED}❌ Frontend source file not found: src/biometric_flow/frontend/app.py${NC}"
    exit 1
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo -e "${RED}❌ Streamlit not found in virtual environment${NC}"
    echo "Please run setup_enhanced.sh first"
    exit 1
fi

# Set additional environment variables for Frontend
export STREAMLIT_SERVER_PORT="8501"
export STREAMLIT_SERVER_ADDRESS="0.0.0.0"
export PYTHONPATH="$PROJECT_DIR/src"

echo -e "${GREEN}⚙️  Configuration:${NC}"
echo "   Port: $STREAMLIT_SERVER_PORT"
echo "   Address: $STREAMLIT_SERVER_ADDRESS"
echo "   Backend URL: http://localhost:9000"
echo "   Python Path: $PYTHONPATH"
echo

echo -e "${GREEN}🚀 Starting frontend service...${NC}"
echo -e "${GREEN}📱 Access at: http://localhost:$STREAMLIT_SERVER_PORT${NC}"
echo

streamlit run src/biometric_flow/frontend/app.py --server.port $STREAMLIT_SERVER_PORT --server.address $STREAMLIT_SERVER_ADDRESS

echo
echo -e "${RED}❌ Frontend service stopped${NC}"
