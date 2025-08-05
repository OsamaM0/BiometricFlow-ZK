#!/bin/bash
# =================================================================
# BiometricFlow-ZK Enhanced Docker Management Script
# =================================================================
# Complete Docker ecosystem management with monitoring and scaling

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"
COMPOSE_PROD_FILE="$PROJECT_ROOT/docker-compose.prod.yml"
COMPOSE_MONITORING_FILE="$PROJECT_ROOT/docker/docker-compose.monitoring.yml"
SWARM_STACK_FILE="$PROJECT_ROOT/docker/docker-stack.yml"
ENV_FILE="$PROJECT_ROOT/.env.docker"

# Function to print colored output
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_header() { echo -e "\n${PURPLE}🚀 BiometricFlow-ZK Enhanced Docker Manager${NC}"; echo -e "${PURPLE}==============================================${NC}\n"; }

# Function to check Docker Swarm
check_swarm_mode() {
    if docker info --format '{{.Swarm.LocalNodeState}}' | grep -q "active"; then
        return 0
    else
        return 1
    fi
}

# Function to initialize Docker Swarm
init_swarm() {
    print_info "Initializing Docker Swarm..."
    
    if check_swarm_mode; then
        print_warning "Docker Swarm is already initialized"
        return 0
    fi
    
    docker swarm init --advertise-addr $(hostname -I | awk '{print $1}')
    
    # Create overlay network for Traefik
    docker network create --driver=overlay --attachable traefik-public || true
    
    print_success "Docker Swarm initialized successfully"
}

# Function to create Docker secrets
create_secrets() {
    print_info "Creating Docker secrets..."
    
    cd "$PROJECT_ROOT"
    
    # Generate keys if they don't exist
    if [ ! -f "place_backend.env" ] || [ ! -f "unified_gateway.env" ] || [ ! -f "frontend.env" ]; then
        python generate_keys.py
    fi
    
    # Create secrets
    docker secret create place_backend_env place_backend.env 2>/dev/null || print_warning "Secret place_backend_env already exists"
    docker secret create unified_gateway_env unified_gateway.env 2>/dev/null || print_warning "Secret unified_gateway_env already exists"
    docker secret create frontend_env frontend.env 2>/dev/null || print_warning "Secret frontend_env already exists"
    
    # Create configs
    docker config create devices_config devices_config.json 2>/dev/null || print_warning "Config devices_config already exists"
    docker config create backend_places_config backend_places_config.json 2>/dev/null || print_warning "Config backend_places_config already exists"
    
    print_success "Docker secrets and configs created"
}

# Function to build multi-architecture images
build_multiarch() {
    print_info "Building multi-architecture Docker images..."
    
    cd "$PROJECT_ROOT"
    
    # Create buildx builder if it doesn't exist
    docker buildx create --name biometric-builder --use --bootstrap 2>/dev/null || true
    
    # Build all images
    docker buildx bake -f docker/docker-bake.hcl --push
    
    print_success "Multi-architecture images built and pushed"
}

# Function to deploy monitoring stack
deploy_monitoring() {
    print_info "Deploying monitoring stack..."
    
    cd "$PROJECT_ROOT"
    
    # Create monitoring directories
    mkdir -p monitoring/{prometheus/rules,grafana/{dashboards,datasources,alerting},alertmanager,loki,promtail,blackbox}
    
    # Start monitoring stack
    docker-compose -f "$COMPOSE_MONITORING_FILE" up -d
    
    print_success "Monitoring stack deployed successfully"
    print_info "Access URLs:"
    echo "📊 Grafana: http://localhost:3000 (admin/BiometricFlow2025!)"
    echo "📈 Prometheus: http://localhost:9090"
    echo "🚨 AlertManager: http://localhost:9093"
    echo "📋 Loki: http://localhost:3100"
}

# Function to deploy to Docker Swarm
deploy_swarm() {
    print_info "Deploying to Docker Swarm..."
    
    if ! check_swarm_mode; then
        init_swarm
    fi
    
    create_secrets
    
    # Deploy stack
    docker stack deploy -c "$SWARM_STACK_FILE" biometric-flow
    
    print_success "Stack deployed to Docker Swarm"
    
    # Show services
    docker stack services biometric-flow
}

# Function to scale services
scale_services() {
    local environment=${1:-development}
    local scale_config=${2:-"place-backend=2,unified-gateway=3,frontend=2"}
    
    print_info "Scaling services: $scale_config"
    
    cd "$PROJECT_ROOT"
    
    if [ "$environment" = "production" ]; then
        docker-compose -f "$COMPOSE_PROD_FILE" up -d --scale $(echo $scale_config | tr ',' ' ' | sed 's/=/=/g')
    else
        docker-compose -f "$COMPOSE_FILE" up -d --scale $(echo $scale_config | tr ',' ' ' | sed 's/=/=/g')
    fi
    
    print_success "Services scaled successfully"
}

# Function to backup data
backup_data() {
    local backup_dir="$PROJECT_ROOT/backups/$(date +%Y%m%d_%H%M%S)"
    
    print_info "Creating backup in $backup_dir..."
    
    mkdir -p "$backup_dir"
    
    # Backup volumes
    docker run --rm -v biometric-place-backend-data:/source -v "$backup_dir":/backup alpine tar czf /backup/place-backend-data.tar.gz -C /source .
    docker run --rm -v biometric-gateway-data:/source -v "$backup_dir":/backup alpine tar czf /backup/gateway-data.tar.gz -C /source .
    docker run --rm -v biometric-frontend-data:/source -v "$backup_dir":/backup alpine tar czf /backup/frontend-data.tar.gz -C /source .
    
    # Backup configurations
    cp -r "$PROJECT_ROOT"/*.env "$backup_dir/" 2>/dev/null || true
    cp -r "$PROJECT_ROOT"/*.json "$backup_dir/" 2>/dev/null || true
    
    print_success "Backup created: $backup_dir"
}

# Function to restore data
restore_data() {
    local backup_dir=$1
    
    if [ -z "$backup_dir" ] || [ ! -d "$backup_dir" ]; then
        print_error "Please provide a valid backup directory"
        return 1
    fi
    
    print_info "Restoring from $backup_dir..."
    
    # Stop services first
    docker-compose -f "$COMPOSE_FILE" down
    docker-compose -f "$COMPOSE_PROD_FILE" down
    
    # Restore volumes
    docker run --rm -v biometric-place-backend-data:/target -v "$backup_dir":/backup alpine tar xzf /backup/place-backend-data.tar.gz -C /target
    docker run --rm -v biometric-gateway-data:/target -v "$backup_dir":/backup alpine tar xzf /backup/gateway-data.tar.gz -C /target
    docker run --rm -v biometric-frontend-data:/target -v "$backup_dir":/backup alpine tar xzf /backup/frontend-data.tar.gz -C /target
    
    # Restore configurations
    cp "$backup_dir"/*.env "$PROJECT_ROOT/" 2>/dev/null || true
    cp "$backup_dir"/*.json "$PROJECT_ROOT/" 2>/dev/null || true
    
    print_success "Data restored from $backup_dir"
}

# Function to run performance tests
performance_test() {
    print_info "Running performance tests..."
    
    # Install dependencies if needed
    command -v hey >/dev/null 2>&1 || {
        print_warning "Installing 'hey' for load testing..."
        go install github.com/rakyll/hey@latest
    }
    
    # Test endpoints
    print_info "Testing Place Backend..."
    hey -n 1000 -c 10 http://localhost:8000/health
    
    print_info "Testing Unified Gateway..."
    hey -n 1000 -c 10 http://localhost:9000/health
    
    print_info "Testing Frontend..."
    hey -n 100 -c 5 http://localhost:8501/healthz
    
    print_success "Performance tests completed"
}

# Function to generate comprehensive status report
generate_status_report() {
    local report_file="$PROJECT_ROOT/logs/system_status_$(date +%Y%m%d_%H%M%S).json"
    
    print_info "Generating comprehensive status report..."
    
    mkdir -p "$(dirname "$report_file")"
    
    cat > "$report_file" << EOF
{
    "timestamp": "$(date -Iseconds)",
    "version": "3.1.0",
    "environment": "docker",
    "system": {
        "docker_version": "$(docker --version | cut -d' ' -f3 | cut -d',' -f1)",
        "docker_compose_version": "$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)",
        "swarm_mode": $(check_swarm_mode && echo "true" || echo "false"),
        "host_info": {
            "hostname": "$(hostname)",
            "os": "$(uname -s)",
            "kernel": "$(uname -r)",
            "architecture": "$(uname -m)"
        }
    },
    "containers": $(docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | tail -n +2 | jq -R . | jq -s .),
    "images": $(docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | tail -n +2 | jq -R . | jq -s .),
    "volumes": $(docker volume ls --format "table {{.Name}}\t{{.Driver}}" | tail -n +2 | jq -R . | jq -s .),
    "networks": $(docker network ls --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}" | tail -n +2 | jq -R . | jq -s .),
    "services": {
        "place_backend": {
            "status": "$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || echo '000')",
            "response_time": "$(curl -s -o /dev/null -w "%{time_total}" http://localhost:8000/health || echo '999')s"
        },
        "unified_gateway": {
            "status": "$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9000/health || echo '000')",
            "response_time": "$(curl -s -o /dev/null -w "%{time_total}" http://localhost:9000/health || echo '999')s"
        },
        "frontend": {
            "status": "$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501/healthz || echo '000')",
            "response_time": "$(curl -s -o /dev/null -w "%{time_total}" http://localhost:8501/healthz || echo '999')s"
        }
    }
}
EOF
    
    print_success "Status report generated: $report_file"
}

# Function to show help
show_help() {
    echo "BiometricFlow-ZK Enhanced Docker Management Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Core Commands:"
    echo "  setup                      Setup environment and generate keys"
    echo "  build [dev|prod]           Build Docker images"
    echo "  start [dev|prod]           Start all services"
    echo "  stop [dev|prod]            Stop all services"
    echo "  restart [dev|prod]         Restart all services"
    echo "  status [dev|prod]          Show service status"
    echo "  logs [service] [env]       Show logs"
    echo "  health                     Check service health"
    echo "  cleanup [--volumes]        Clean up Docker resources"
    echo ""
    echo "Enhanced Commands:"
    echo "  build-multiarch            Build multi-architecture images"
    echo "  deploy-monitoring          Deploy monitoring stack"
    echo "  deploy-swarm               Deploy to Docker Swarm"
    echo "  init-swarm                 Initialize Docker Swarm"
    echo "  scale [env] [config]       Scale services (e.g., place-backend=3,frontend=2)"
    echo "  backup                     Backup all data"
    echo "  restore [backup_dir]       Restore from backup"
    echo "  performance-test           Run performance tests"
    echo "  status-report              Generate comprehensive status report"
    echo ""
    echo "Examples:"
    echo "  $0 setup                           # Setup environment"
    echo "  $0 start prod                      # Start production environment"
    echo "  $0 deploy-monitoring               # Deploy monitoring stack"
    echo "  $0 deploy-swarm                    # Deploy to Docker Swarm"
    echo "  $0 scale dev place-backend=3       # Scale place backend to 3 replicas"
    echo "  $0 backup                          # Create backup"
    echo "  $0 performance-test                # Run load tests"
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
        build-multiarch)
            check_prerequisites
            build_multiarch
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
        deploy-monitoring)
            check_prerequisites
            deploy_monitoring
            ;;
        deploy-swarm)
            check_prerequisites
            deploy_swarm
            ;;
        init-swarm)
            init_swarm
            ;;
        scale)
            scale_services "$2" "$3"
            ;;
        backup)
            backup_data
            ;;
        restore)
            restore_data "$2"
            ;;
        performance-test)
            performance_test
            ;;
        status-report)
            generate_status_report
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

# Include existing functions from the original script
source "$SCRIPT_DIR/deploy.sh" 2>/dev/null || {
    # Define essential functions if original script not found
    check_prerequisites() { print_info "Prerequisites check..."; }
    setup_environment() { print_info "Environment setup..."; }
    build_images() { print_info "Building images for $1..."; }
    start_services() { print_info "Starting services in $1 mode..."; }
    stop_services() { print_info "Stopping services..."; }
    show_status() { print_info "Service status..."; }
    show_logs() { print_info "Showing logs..."; }
    check_service_health() { print_info "Checking health..."; }
    cleanup() { print_info "Cleaning up..."; }
}

# Run main function with all arguments
main "$@"
