#!/bin/bash
# =================================================================
# BiometricFlow-ZK Docker Deployment Script
# =================================================================
# Comprehensive Docker deployment and management script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"
COMPOSE_PROD_FILE="$PROJECT_ROOT/docker-compose.prod.yml"
ENV_FILE="$PROJECT_ROOT/.env.docker"

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "\n${BLUE}🚀 BiometricFlow-ZK Docker Manager${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

# Function to check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to setup environment
setup_environment() {
    print_info "Setting up environment..."
    
    cd "$PROJECT_ROOT"
    
    # Copy environment file if it doesn't exist
    if [ ! -f ".env" ]; then
        cp ".env.docker" ".env"
        print_success "Created .env file from template"
    fi
    
    # Create required directories
    mkdir -p logs data/place_backend data/gateway data/frontend backups
    
    # Generate authentication keys if they don't exist
    if [ ! -f "place_backend.env" ] || [ ! -f "unified_gateway.env" ] || [ ! -f "frontend.env" ]; then
        print_info "Generating authentication keys..."
        python generate_keys.py
        print_success "Authentication keys generated"
    fi
    
    print_success "Environment setup completed"
}

# Function to build images
build_images() {
    local environment=${1:-development}
    print_info "Building Docker images for $environment environment..."
    
    cd "$PROJECT_ROOT"
    
    if [ "$environment" = "production" ]; then
        docker-compose -f "$COMPOSE_PROD_FILE" build --no-cache
    else
        docker-compose -f "$COMPOSE_FILE" build --no-cache
    fi
    
    print_success "Docker images built successfully"
}

# Function to start services
start_services() {
    local environment=${1:-development}
    print_info "Starting BiometricFlow-ZK services in $environment mode..."
    
    cd "$PROJECT_ROOT"
    
    if [ "$environment" = "production" ]; then
        docker-compose -f "$COMPOSE_PROD_FILE" up -d
    else
        docker-compose -f "$COMPOSE_FILE" up -d
    fi
    
    print_success "Services started successfully"
    print_info "Waiting for services to be ready..."
    
    # Wait for services to be healthy
    sleep 30
    
    # Check service health
    check_service_health
}

# Function to stop services
stop_services() {
    local environment=${1:-development}
    print_info "Stopping BiometricFlow-ZK services..."
    
    cd "$PROJECT_ROOT"
    
    if [ "$environment" = "production" ]; then
        docker-compose -f "$COMPOSE_PROD_FILE" down
    else
        docker-compose -f "$COMPOSE_FILE" down
    fi
    
    print_success "Services stopped successfully"
}

# Function to check service health
check_service_health() {
    print_info "Checking service health..."
    
    local services=("place-backend:8000" "unified-gateway:9000" "frontend:8501")
    local all_healthy=true
    
    for service in "${services[@]}"; do
        IFS=':' read -r name port <<< "$service"
        
        if curl -f -s "http://localhost:$port/health" > /dev/null 2>&1 || 
           curl -f -s "http://localhost:$port/healthz" > /dev/null 2>&1; then
            print_success "$name service is healthy"
        else
            print_warning "$name service is not responding"
            all_healthy=false
        fi
    done
    
    if [ "$all_healthy" = true ]; then
        print_success "All services are healthy!"
    else
        print_warning "Some services may need more time to start"
    fi
}

# Function to show logs
show_logs() {
    local service=${1:-""}
    local environment=${2:-development}
    
    cd "$PROJECT_ROOT"
    
    if [ -n "$service" ]; then
        print_info "Showing logs for $service..."
        if [ "$environment" = "production" ]; then
            docker-compose -f "$COMPOSE_PROD_FILE" logs -f "$service"
        else
            docker-compose -f "$COMPOSE_FILE" logs -f "$service"
        fi
    else
        print_info "Showing logs for all services..."
        if [ "$environment" = "production" ]; then
            docker-compose -f "$COMPOSE_PROD_FILE" logs -f
        else
            docker-compose -f "$COMPOSE_FILE" logs -f
        fi
    fi
}

# Function to show status
show_status() {
    local environment=${1:-development}
    print_info "Service Status:"
    
    cd "$PROJECT_ROOT"
    
    if [ "$environment" = "production" ]; then
        docker-compose -f "$COMPOSE_PROD_FILE" ps
    else
        docker-compose -f "$COMPOSE_FILE" ps
    fi
    
    echo ""
    check_service_health
    
    echo ""
    print_info "Access URLs:"
    echo "🌐 Frontend Dashboard: http://localhost:8501"
    echo "🔗 Unified Gateway API: http://localhost:9000"
    echo "🏢 Place Backend API: http://localhost:8000"
    echo "📚 API Documentation: http://localhost:9000/docs"
}

# Function to clean up
cleanup() {
    local remove_volumes=${1:-false}
    print_info "Cleaning up Docker resources..."
    
    cd "$PROJECT_ROOT"
    
    # Stop and remove containers
    docker-compose -f "$COMPOSE_FILE" down
    docker-compose -f "$COMPOSE_PROD_FILE" down
    
    # Remove unused images
    docker image prune -f
    
    # Remove volumes if requested
    if [ "$remove_volumes" = true ]; then
        print_warning "Removing persistent volumes (this will delete all data)..."
        docker volume prune -f
    fi
    
    print_success "Cleanup completed"
}

# Function to show help
show_help() {
    echo "BiometricFlow-ZK Docker Management Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  setup                    Setup environment and generate keys"
    echo "  build [dev|prod]         Build Docker images"
    echo "  start [dev|prod]         Start all services"
    echo "  stop [dev|prod]          Stop all services"
    echo "  restart [dev|prod]       Restart all services"
    echo "  status [dev|prod]        Show service status"
    echo "  logs [service] [env]     Show logs (optional: specific service)"
    echo "  health                   Check service health"
    echo "  cleanup [--volumes]      Clean up Docker resources"
    echo "  help                     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup                 # Setup environment"
    echo "  $0 start dev             # Start development environment"
    echo "  $0 start prod            # Start production environment"
    echo "  $0 logs frontend         # Show frontend logs"
    echo "  $0 cleanup --volumes     # Clean up including volumes"
    echo ""
}

# Main script logic
main() {
    print_header
    
    case "${1:-help}" in
        setup)
            check_prerequisites
            setup_environment
            ;;
        build)
            check_prerequisites
            build_images "${2:-development}"
            ;;
        start)
            check_prerequisites
            setup_environment
            start_services "${2:-development}"
            ;;
        stop)
            stop_services "${2:-development}"
            ;;
        restart)
            stop_services "${2:-development}"
            start_services "${2:-development}"
            ;;
        status)
            show_status "${2:-development}"
            ;;
        logs)
            show_logs "$2" "${3:-development}"
            ;;
        health)
            check_service_health
            ;;
        cleanup)
            if [ "$2" = "--volumes" ]; then
                cleanup true
            else
                cleanup false
            fi
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
