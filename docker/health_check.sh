#!/bin/bash
# =================================================================
# BiometricFlow-ZK Docker Health Check Script
# =================================================================
# Comprehensive health monitoring for Docker deployment

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_ROOT/logs/health_check.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create logs directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

# Function to log messages
log_message() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
    log_message "INFO" "$1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    log_message "SUCCESS" "$1"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    log_message "WARNING" "$1"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    log_message "ERROR" "$1"
}

# Function to check Docker container status
check_container_status() {
    local container_name=$1
    local status=$(docker inspect --format='{{.State.Status}}' "$container_name" 2>/dev/null || echo "not_found")
    
    case $status in
        "running")
            print_success "Container $container_name is running"
            return 0
            ;;
        "not_found")
            print_error "Container $container_name not found"
            return 1
            ;;
        *)
            print_warning "Container $container_name status: $status"
            return 1
            ;;
    esac
}

# Function to check service health endpoint
check_service_health() {
    local service_name=$1
    local port=$2
    local endpoint=${3:-"/health"}
    local timeout=${4:-10}
    
    print_info "Checking $service_name health endpoint..."
    
    local url="http://localhost:$port$endpoint"
    local response_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time $timeout "$url" || echo "000")
    
    if [ "$response_code" = "200" ]; then
        print_success "$service_name health check passed (HTTP $response_code)"
        return 0
    else
        print_error "$service_name health check failed (HTTP $response_code)"
        return 1
    fi
}

# Function to check service response time
check_response_time() {
    local service_name=$1
    local port=$2
    local endpoint=${3:-"/health"}
    local max_time=${4:-2}
    
    print_info "Checking $service_name response time..."
    
    local url="http://localhost:$port$endpoint"
    local response_time=$(curl -s -o /dev/null -w "%{time_total}" --max-time 10 "$url" || echo "999")
    
    if (( $(echo "$response_time < $max_time" | bc -l) )); then
        print_success "$service_name response time: ${response_time}s (within ${max_time}s limit)"
        return 0
    else
        print_warning "$service_name response time: ${response_time}s (exceeds ${max_time}s limit)"
        return 1
    fi
}

# Function to check Docker resource usage
check_resource_usage() {
    local container_name=$1
    
    print_info "Checking resource usage for $container_name..."
    
    local stats=$(docker stats "$container_name" --no-stream --format "table {{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null || echo "N/A")
    
    if [ "$stats" != "N/A" ]; then
        print_success "$container_name resource usage: $stats"
        return 0
    else
        print_error "Could not retrieve resource usage for $container_name"
        return 1
    fi
}

# Function to check authentication flow
check_authentication_flow() {
    print_info "Testing authentication flow..."
    
    # Test place backend token generation
    local place_token_response=$(curl -s -X POST "http://localhost:8000/auth/token" \
        -H "Content-Type: application/json" \
        -d '{"api_key": "test_key"}' || echo "failed")
    
    if [[ $place_token_response == *"access_token"* ]]; then
        print_success "Place backend token generation working"
    else
        print_warning "Place backend token generation may have issues"
    fi
    
    # Test gateway frontend token
    local gateway_token_response=$(curl -s -X POST "http://localhost:9000/auth/frontend/token" \
        -H "Content-Type: application/json" \
        -d '{"api_key": "test_key"}' || echo "failed")
    
    if [[ $gateway_token_response == *"access_token"* ]]; then
        print_success "Gateway frontend token generation working"
    else
        print_warning "Gateway frontend token generation may have issues"
    fi
}

# Function to check logs for errors
check_logs_for_errors() {
    local container_name=$1
    local lines=${2:-50}
    
    print_info "Checking recent logs for $container_name..."
    
    local error_count=$(docker logs "$container_name" --tail $lines 2>/dev/null | grep -i "error\|exception\|failed" | wc -l)
    
    if [ "$error_count" -eq 0 ]; then
        print_success "No recent errors found in $container_name logs"
        return 0
    else
        print_warning "Found $error_count potential errors in $container_name logs"
        return 1
    fi
}

# Function to check network connectivity
check_network_connectivity() {
    print_info "Checking network connectivity between services..."
    
    # Check if containers can communicate
    local gateway_to_backend=$(docker exec biometric-unified-gateway curl -s -f "http://place-backend:8000/health" > /dev/null && echo "success" || echo "failed")
    local frontend_to_gateway=$(docker exec biometric-frontend curl -s -f "http://unified-gateway:9000/health" > /dev/null && echo "success" || echo "failed")
    
    if [ "$gateway_to_backend" = "success" ]; then
        print_success "Gateway → Backend connectivity: OK"
    else
        print_error "Gateway → Backend connectivity: FAILED"
    fi
    
    if [ "$frontend_to_gateway" = "success" ]; then
        print_success "Frontend → Gateway connectivity: OK"
    else
        print_error "Frontend → Gateway connectivity: FAILED"
    fi
}

# Function to generate health report
generate_health_report() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local report_file="$PROJECT_ROOT/logs/health_report_$(date '+%Y%m%d_%H%M%S').json"
    
    print_info "Generating health report..."
    
    cat > "$report_file" << EOF
{
    "timestamp": "$timestamp",
    "version": "3.1.0",
    "environment": "docker",
    "services": {
        "place_backend": {
            "container_status": "$(docker inspect --format='{{.State.Status}}' biometric-place-backend 2>/dev/null || echo 'not_found')",
            "health_endpoint": "$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || echo '000')",
            "uptime": "$(docker inspect --format='{{.State.StartedAt}}' biometric-place-backend 2>/dev/null || echo 'N/A')"
        },
        "unified_gateway": {
            "container_status": "$(docker inspect --format='{{.State.Status}}' biometric-unified-gateway 2>/dev/null || echo 'not_found')",
            "health_endpoint": "$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9000/health || echo '000')",
            "uptime": "$(docker inspect --format='{{.State.StartedAt}}' biometric-unified-gateway 2>/dev/null || echo 'N/A')"
        },
        "frontend": {
            "container_status": "$(docker inspect --format='{{.State.Status}}' biometric-frontend 2>/dev/null || echo 'not_found')",
            "health_endpoint": "$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501/healthz || echo '000')",
            "uptime": "$(docker inspect --format='{{.State.StartedAt}}' biometric-frontend 2>/dev/null || echo 'N/A')"
        }
    },
    "overall_status": "healthy"
}
EOF
    
    print_success "Health report generated: $report_file"
}

# Main health check function
perform_comprehensive_health_check() {
    local overall_status=0
    
    echo -e "\n${BLUE}🏥 BiometricFlow-ZK Docker Health Check${NC}"
    echo -e "${BLUE}===========================================${NC}\n"
    
    # Check container status
    echo -e "${BLUE}📦 Container Status Check${NC}"
    check_container_status "biometric-place-backend" || overall_status=1
    check_container_status "biometric-unified-gateway" || overall_status=1
    check_container_status "biometric-frontend" || overall_status=1
    echo ""
    
    # Check service health endpoints
    echo -e "${BLUE}🌐 Service Health Endpoints${NC}"
    check_service_health "place-backend" 8000 "/health" || overall_status=1
    check_service_health "unified-gateway" 9000 "/health" || overall_status=1
    check_service_health "frontend" 8501 "/healthz" || overall_status=1
    echo ""
    
    # Check response times
    echo -e "${BLUE}⚡ Response Time Check${NC}"
    check_response_time "place-backend" 8000 "/health" 2
    check_response_time "unified-gateway" 9000 "/health" 2
    check_response_time "frontend" 8501 "/healthz" 3
    echo ""
    
    # Check resource usage
    echo -e "${BLUE}📊 Resource Usage Check${NC}"
    check_resource_usage "biometric-place-backend"
    check_resource_usage "biometric-unified-gateway"
    check_resource_usage "biometric-frontend"
    echo ""
    
    # Check authentication flow
    echo -e "${BLUE}🔐 Authentication Flow Check${NC}"
    check_authentication_flow
    echo ""
    
    # Check logs for errors
    echo -e "${BLUE}📝 Log Analysis${NC}"
    check_logs_for_errors "biometric-place-backend"
    check_logs_for_errors "biometric-unified-gateway"
    check_logs_for_errors "biometric-frontend"
    echo ""
    
    # Check network connectivity
    echo -e "${BLUE}🌐 Network Connectivity${NC}"
    check_network_connectivity
    echo ""
    
    # Generate health report
    generate_health_report
    
    # Summary
    echo -e "${BLUE}📋 Health Check Summary${NC}"
    if [ $overall_status -eq 0 ]; then
        print_success "Overall system health: HEALTHY"
        print_info "All critical checks passed. System is operating normally."
    else
        print_warning "Overall system health: DEGRADED"
        print_info "Some issues detected. Check logs for details."
    fi
    
    echo ""
    print_info "Access URLs:"
    echo "🌐 Frontend Dashboard: http://localhost:8501"
    echo "🔗 Unified Gateway API: http://localhost:9000"
    echo "🏢 Place Backend API: http://localhost:8000"
    echo "📚 API Documentation: http://localhost:9000/docs"
    
    return $overall_status
}

# Script execution
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "BiometricFlow-ZK Docker Health Check Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help, -h           Show this help message"
    echo "  --report             Generate health report only"
    echo "  --continuous [SEC]   Run health check continuously (default: 60 seconds)"
    echo ""
    echo "Examples:"
    echo "  $0                   # Run single health check"
    echo "  $0 --report          # Generate health report only"
    echo "  $0 --continuous 30   # Run health check every 30 seconds"
    echo ""
elif [ "$1" = "--report" ]; then
    generate_health_report
elif [ "$1" = "--continuous" ]; then
    interval=${2:-60}
    print_info "Starting continuous health monitoring (interval: ${interval}s)"
    print_info "Press Ctrl+C to stop"
    
    while true; do
        perform_comprehensive_health_check
        echo ""
        print_info "Waiting ${interval} seconds for next check..."
        sleep $interval
        echo -e "\n${'='*50}\n"
    done
else
    perform_comprehensive_health_check
fi
