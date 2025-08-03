#!/bin/bash

# =================================================================
# Enhanced Universal Service Launcher - Linux/Mac
# Works from any location with proper path detection
# =================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"
LOG_DIR="$PROJECT_DIR/logs"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if virtual environment exists
check_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        print_error "Virtual environment not found at $VENV_DIR"
        print_status "Please run setup_enhanced.sh first"
        exit 1
    fi
    print_success "Virtual environment found"
}

# Function to check if source files exist
check_source_files() {
    local required_files=(
        "src/biometric_flow/backend/place_backend.py"
        "src/biometric_flow/backend/unified_gateway.py"
        "src/biometric_flow/frontend/app.py"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$PROJECT_DIR/$file" ]; then
            print_error "Required file not found: $file"
            exit 1
        fi
    done
    
    print_success "All source files found"
}

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1
    fi
    return 0
}

# Function to start a service in background
start_service() {
    local service_name=$1
    local script_name=$2
    local port=$3
    
    print_status "Starting $service_name on port $port..."
    
    if ! check_port $port; then
        print_warning "Port $port is already in use"
        return 1
    fi
    
    cd "$PROJECT_DIR"
    nohup ./scripts/deployment/${script_name} > "$LOG_DIR/${service_name}.log" 2>&1 &
    echo $! > "$LOG_DIR/${service_name}.pid"
    
    sleep 2
    
    if ps -p $(cat "$LOG_DIR/${service_name}.pid") > /dev/null 2>&1; then
        print_success "$service_name started successfully"
        return 0
    else
        print_error "Failed to start $service_name"
        return 1
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local port=$1
    local service_name=$2
    local max_attempts=30
    local attempt=0
    
    print_status "Waiting for $service_name to be ready..."
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
            print_success "$service_name is ready"
            return 0
        fi
        
        attempt=$((attempt + 1))
        sleep 1
    done
    
    print_warning "$service_name may not be fully ready yet"
    return 1
}

# Function to stop all services
stop_services() {
    print_status "Stopping all services..."
    
    local services=("place1_backend" "place2_backend" "place3_backend" "unified_gateway" "frontend")
    
    for service in "${services[@]}"; do
        local pid_file="$LOG_DIR/${service}.pid"
        if [ -f "$pid_file" ]; then
            local pid=$(cat "$pid_file")
            if ps -p $pid > /dev/null 2>&1; then
                kill $pid
                print_status "Stopped $service (PID: $pid)"
            fi
            rm -f "$pid_file"
        fi
    done
    
    print_success "All services stopped"
}

# Function to show service status
show_status() {
    echo
    echo "======================================================================"
    echo "Service Status"
    echo "======================================================================"
    
    local services=("place1_backend:8000" "place2_backend:8001" "place3_backend:8002" "unified_gateway:9000" "frontend:8501")
    
    for service_port in "${services[@]}"; do
        local service=$(echo $service_port | cut -d':' -f1)
        local port=$(echo $service_port | cut -d':' -f2)
        
        if check_port $port; then
            echo -e "$service (port $port): ${RED}STOPPED${NC}"
        else
            echo -e "$service (port $port): ${GREEN}RUNNING${NC}"
        fi
    done
    
    echo
}

# Function to start all services
start_all_services() {
    print_status "Starting all services..."
    echo
    
    # Start backends first
    start_service "place1_backend" "start_place1_backend.sh" 8000
    sleep 3
    
    start_service "place2_backend" "start_place2_backend.sh" 8001
    sleep 3
    
    start_service "place3_backend" "start_place3_backend.sh" 8002
    sleep 3
    
    # Start unified gateway
    start_service "unified_gateway" "start_unified_backend.sh" 9000
    sleep 5
    
    # Start frontend
    start_service "frontend" "start_frontend.sh" 8501
    
    echo
    print_success "All services started!"
    echo
    echo "Access the system:"
    echo "  Frontend: http://localhost:8501"
    echo "  Unified Gateway: http://localhost:9000"
    echo "  Place 1 Backend: http://localhost:8000"
    echo "  Place 2 Backend: http://localhost:8001"
    echo "  Place 3 Backend: http://localhost:8002"
    echo
    echo "Log files: $LOG_DIR/"
    echo "Project root: $PROJECT_DIR"
}

# Function to restart all services
restart_all_services() {
    stop_services
    sleep 3
    start_all_services
}

# Function to view logs
view_logs() {
    local service=$1
    local log_file="$LOG_DIR/${service}.log"
    
    if [ -f "$log_file" ]; then
        tail -f "$log_file"
    else
        print_error "Log file not found: $log_file"
    fi
}

# Main menu function
show_menu() {
    echo
    echo "======================================================================"
    echo "  Multi-Place Fingerprint Attendance System Launcher"
    echo "  Enhanced Universal Version"
    echo "======================================================================"
    echo
    echo "📁 Working from: $PROJECT_DIR"
    echo
    echo "Select an option:"
    echo "1) Start all services"
    echo "2) Stop all services"
    echo "3) Restart all services"
    echo "4) Show service status"
    echo "5) View logs"
    echo "6) Exit"
    echo
    read -p "Enter choice [1-6]: " choice
    
    case $choice in
        1) start_all_services ;;
        2) stop_services ;;
        3) restart_all_services ;;
        4) show_status ;;
        5) 
            echo "Available logs: place1_backend, place2_backend, place3_backend, unified_gateway, frontend"
            read -p "Enter service name: " service
            view_logs "$service"
            ;;
        6) 
            print_status "Goodbye!"
            exit 0 
            ;;
        *) 
            print_error "Invalid option"
            ;;
    esac
}

# Trap to handle Ctrl+C
trap 'echo ""; print_status "Interrupted by user"; stop_services; exit 0' INT

# Change to project directory
cd "$PROJECT_DIR"

# === Load .env from root project directory ===
if [ -f "$PROJECT_DIR/.env" ]; then
    print_status "🔄 Loading environment variables from .env..."
    set -a
    source "$PROJECT_DIR/.env"
    set +a
else
    print_warning "⚠️  .env file not found in $PROJECT_DIR"
fi

# Check prerequisites
check_venv
check_source_files

# Check if running with arguments
if [ $# -gt 0 ]; then
    case $1 in
        "start") start_all_services ;;
        "stop") stop_services ;;
        "restart") restart_all_services ;;
        "status") show_status ;;
        *) 
            echo "Usage: $0 [start|stop|restart|status]"
            exit 1
            ;;
    esac
    exit 0
fi

# Interactive menu
while true; do
    show_menu
done
