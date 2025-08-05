# =================================================================
# BiometricFlow-ZK Enhanced Docker Makefile
# =================================================================
# Simplified commands for Docker ecosystem management

.PHONY: help setup build start stop restart logs health cleanup scale backup restore
.DEFAULT_GOAL := help

# Configuration
PROJECT_NAME := biometric-flow
COMPOSE_FILE := docker-compose.yml
COMPOSE_PROD_FILE := docker-compose.prod.yml
COMPOSE_MONITORING_FILE := docker/docker-compose.monitoring.yml
SWARM_STACK_FILE := docker/docker-stack.yml
BACKUP_DIR := backups/$(shell date +%Y%m%d_%H%M%S)

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Helper functions
define print_info
	@echo -e "${BLUE}ℹ️  $(1)${NC}"
endef

define print_success
	@echo -e "${GREEN}✅ $(1)${NC}"
endef

define print_warning
	@echo -e "${YELLOW}⚠️  $(1)${NC}"
endef

define print_error
	@echo -e "${RED}❌ $(1)${NC}"
endef

##@ Help
help: ## Display this help
	@echo -e "\n${BLUE}🚀 BiometricFlow-ZK Enhanced Docker Commands${NC}"
	@echo -e "${BLUE}===========================================${NC}\n"
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Setup and Configuration
setup: ## Setup environment and generate keys
	$(call print_info,"Setting up environment...")
	@if [ -f "generate_keys.py" ]; then python generate_keys.py; fi
	@if [ ! -f ".env.docker" ]; then cp .env.docker.example .env.docker 2>/dev/null || echo "# Docker environment" > .env.docker; fi
	$(call print_success,"Environment setup complete")

check: ## Check prerequisites and system status
	$(call print_info,"Checking prerequisites...")
	@command -v docker >/dev/null 2>&1 || { $(call print_error,"Docker is not installed"); exit 1; }
	@command -v docker-compose >/dev/null 2>&1 || { $(call print_error,"Docker Compose is not installed"); exit 1; }
	@docker info >/dev/null 2>&1 || { $(call print_error,"Docker daemon is not running"); exit 1; }
	$(call print_success,"All prerequisites met")

##@ Development Environment
dev-build: ## Build development images
	$(call print_info,"Building development images...")
	docker-compose -f $(COMPOSE_FILE) build --parallel
	$(call print_success,"Development images built")

dev-start: setup ## Start development environment
	$(call print_info,"Starting development environment...")
	docker-compose -f $(COMPOSE_FILE) up -d
	@sleep 5
	$(call print_success,"Development environment started")
	@echo "🌐 Access URLs:"
	@echo "   Frontend: http://localhost:8501"
	@echo "   Place Backend: http://localhost:8000"
	@echo "   Unified Gateway: http://localhost:9000"

dev-stop: ## Stop development environment
	$(call print_info,"Stopping development environment...")
	docker-compose -f $(COMPOSE_FILE) down
	$(call print_success,"Development environment stopped")

dev-restart: dev-stop dev-start ## Restart development environment

dev-logs: ## Show development logs
	docker-compose -f $(COMPOSE_FILE) logs -f

##@ Production Environment
prod-build: ## Build production images
	$(call print_info,"Building production images...")
	docker-compose -f $(COMPOSE_PROD_FILE) build --parallel
	$(call print_success,"Production images built")

prod-start: setup ## Start production environment
	$(call print_info,"Starting production environment...")
	docker-compose -f $(COMPOSE_PROD_FILE) up -d
	@sleep 10
	$(call print_success,"Production environment started")

prod-stop: ## Stop production environment
	$(call print_info,"Stopping production environment...")
	docker-compose -f $(COMPOSE_PROD_FILE) down
	$(call print_success,"Production environment stopped")

prod-restart: prod-stop prod-start ## Restart production environment

prod-logs: ## Show production logs
	docker-compose -f $(COMPOSE_PROD_FILE) logs -f

##@ Multi-Architecture and Advanced Builds
build-multiarch: ## Build multi-architecture images
	$(call print_info,"Building multi-architecture images...")
	@command -v docker >/dev/null 2>&1 && docker buildx version >/dev/null 2>&1 || { $(call print_error,"Docker Buildx is required"); exit 1; }
	docker buildx create --name biometric-builder --use --bootstrap 2>/dev/null || true
	docker buildx bake -f docker/docker-bake.hcl --push
	$(call print_success,"Multi-architecture images built and pushed")

##@ Orchestration
swarm-init: ## Initialize Docker Swarm
	$(call print_info,"Initializing Docker Swarm...")
	@if docker info --format '{{.Swarm.LocalNodeState}}' | grep -q "active"; then \
		$(call print_warning,"Docker Swarm is already initialized"); \
	else \
		docker swarm init --advertise-addr $$(hostname -I | awk '{print $$1}'); \
		docker network create --driver=overlay --attachable traefik-public || true; \
		$(call print_success,"Docker Swarm initialized"); \
	fi

swarm-deploy: swarm-init ## Deploy to Docker Swarm
	$(call print_info,"Deploying to Docker Swarm...")
	@if [ -f "generate_keys.py" ]; then python generate_keys.py; fi
	docker secret create place_backend_env place_backend.env 2>/dev/null || true
	docker secret create unified_gateway_env unified_gateway.env 2>/dev/null || true
	docker secret create frontend_env frontend.env 2>/dev/null || true
	docker config create devices_config devices_config.json 2>/dev/null || true
	docker config create backend_places_config backend_places_config.json 2>/dev/null || true
	docker stack deploy -c $(SWARM_STACK_FILE) $(PROJECT_NAME)
	$(call print_success,"Stack deployed to Docker Swarm")
	@echo "\n📊 Swarm Services:"
	@docker stack services $(PROJECT_NAME)

swarm-remove: ## Remove Docker Swarm stack
	$(call print_info,"Removing Docker Swarm stack...")
	docker stack rm $(PROJECT_NAME)
	$(call print_success,"Docker Swarm stack removed")

k8s-deploy: ## Deploy to Kubernetes
	$(call print_info,"Deploying to Kubernetes...")
	@command -v kubectl >/dev/null 2>&1 || { $(call print_error,"kubectl is not installed"); exit 1; }
	kubectl apply -f k8s/
	$(call print_success,"Deployed to Kubernetes")
	@echo "\n📊 Kubernetes Status:"
	@kubectl get pods -n biometric-flow 2>/dev/null || echo "Namespace not yet ready..."

k8s-remove: ## Remove Kubernetes deployment
	$(call print_info,"Removing Kubernetes deployment...")
	kubectl delete -f k8s/ --ignore-not-found=true
	$(call print_success,"Kubernetes deployment removed")

##@ Monitoring and Observability
monitoring-start: ## Start monitoring stack
	$(call print_info,"Starting monitoring stack...")
	@mkdir -p monitoring/{prometheus/rules,grafana/{dashboards,datasources,alerting},alertmanager,loki,promtail,blackbox}
	docker-compose -f $(COMPOSE_MONITORING_FILE) up -d
	@sleep 10
	$(call print_success,"Monitoring stack started")
	@echo "\n📊 Monitoring URLs:"
	@echo "   Grafana: http://localhost:3000 (admin/BiometricFlow2025!)"
	@echo "   Prometheus: http://localhost:9090"
	@echo "   AlertManager: http://localhost:9093"
	@echo "   Loki: http://localhost:3100"

monitoring-stop: ## Stop monitoring stack
	$(call print_info,"Stopping monitoring stack...")
	docker-compose -f $(COMPOSE_MONITORING_FILE) down
	$(call print_success,"Monitoring stack stopped")

monitoring-logs: ## Show monitoring logs
	docker-compose -f $(COMPOSE_MONITORING_FILE) logs -f

##@ Service Management
scale-dev: ## Scale development services (usage: make scale-dev SERVICES="place-backend=3,frontend=2")
	$(call print_info,"Scaling development services: $(SERVICES)")
	@if [ -z "$(SERVICES)" ]; then \
		$(call print_warning,"Usage: make scale-dev SERVICES=\"place-backend=3,frontend=2\""); \
		exit 1; \
	fi
	docker-compose -f $(COMPOSE_FILE) up -d --scale $(shell echo "$(SERVICES)" | tr ',' ' ' | sed 's/=/=/g')
	$(call print_success,"Development services scaled")

scale-prod: ## Scale production services (usage: make scale-prod SERVICES="place-backend=3,frontend=2")
	$(call print_info,"Scaling production services: $(SERVICES)")
	@if [ -z "$(SERVICES)" ]; then \
		$(call print_warning,"Usage: make scale-prod SERVICES=\"place-backend=3,frontend=2\""); \
		exit 1; \
	fi
	docker-compose -f $(COMPOSE_PROD_FILE) up -d --scale $(shell echo "$(SERVICES)" | tr ',' ' ' | sed 's/=/=/g')
	$(call print_success,"Production services scaled")

##@ Health and Status
health: ## Check service health
	$(call print_info,"Checking service health...")
	@echo "\n🏥 Health Check Results:"
	@curl -s -f http://localhost:8000/health >/dev/null && echo "✅ Place Backend: Healthy" || echo "❌ Place Backend: Unhealthy"
	@curl -s -f http://localhost:9000/health >/dev/null && echo "✅ Unified Gateway: Healthy" || echo "❌ Unified Gateway: Unhealthy"
	@curl -s -f http://localhost:8501/healthz >/dev/null && echo "✅ Frontend: Healthy" || echo "❌ Frontend: Unhealthy"

status: ## Show system status
	$(call print_info,"System Status:")
	@echo "\n🐳 Docker Containers:"
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
	@echo "\n💾 Docker Volumes:"
	@docker volume ls --format "table {{.Name}}\t{{.Driver}}"
	@echo "\n🌐 Docker Networks:"
	@docker network ls --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}"

logs: ## Show logs (usage: make logs SERVICE=place-backend ENV=dev)
	@if [ -z "$(SERVICE)" ]; then \
		$(call print_info,"Showing all logs..."); \
		if [ "$(ENV)" = "prod" ]; then \
			docker-compose -f $(COMPOSE_PROD_FILE) logs -f; \
		else \
			docker-compose -f $(COMPOSE_FILE) logs -f; \
		fi; \
	else \
		$(call print_info,"Showing logs for $(SERVICE)..."); \
		if [ "$(ENV)" = "prod" ]; then \
			docker-compose -f $(COMPOSE_PROD_FILE) logs -f $(SERVICE); \
		else \
			docker-compose -f $(COMPOSE_FILE) logs -f $(SERVICE); \
		fi; \
	fi

##@ Backup and Restore
backup: ## Create backup of all data
	$(call print_info,"Creating backup in $(BACKUP_DIR)...")
	@mkdir -p $(BACKUP_DIR)
	docker run --rm -v biometric-place-backend-data:/source -v $(PWD)/$(BACKUP_DIR):/backup alpine tar czf /backup/place-backend-data.tar.gz -C /source .
	docker run --rm -v biometric-gateway-data:/source -v $(PWD)/$(BACKUP_DIR):/backup alpine tar czf /backup/gateway-data.tar.gz -C /source .
	docker run --rm -v biometric-frontend-data:/source -v $(PWD)/$(BACKUP_DIR):/backup alpine tar czf /backup/frontend-data.tar.gz -C /source .
	@cp *.env $(BACKUP_DIR)/ 2>/dev/null || true
	@cp *.json $(BACKUP_DIR)/ 2>/dev/null || true
	$(call print_success,"Backup created: $(BACKUP_DIR)")

restore: ## Restore from backup (usage: make restore BACKUP_DIR=backups/20241217_120000)
	@if [ -z "$(BACKUP_DIR)" ] || [ ! -d "$(BACKUP_DIR)" ]; then \
		$(call print_error,"Please provide valid BACKUP_DIR. Usage: make restore BACKUP_DIR=backups/20241217_120000"); \
		exit 1; \
	fi
	$(call print_info,"Restoring from $(BACKUP_DIR)...")
	@make dev-stop prod-stop 2>/dev/null || true
	docker run --rm -v biometric-place-backend-data:/target -v $(PWD)/$(BACKUP_DIR):/backup alpine tar xzf /backup/place-backend-data.tar.gz -C /target
	docker run --rm -v biometric-gateway-data:/target -v $(PWD)/$(BACKUP_DIR):/backup alpine tar xzf /backup/gateway-data.tar.gz -C /target
	docker run --rm -v biometric-frontend-data:/target -v $(PWD)/$(BACKUP_DIR):/backup alpine tar xzf /backup/frontend-data.tar.gz -C /target
	@cp $(BACKUP_DIR)/*.env . 2>/dev/null || true
	@cp $(BACKUP_DIR)/*.json . 2>/dev/null || true
	$(call print_success,"Data restored from $(BACKUP_DIR)")

##@ Testing
test-performance: ## Run performance tests
	$(call print_info,"Running performance tests...")
	@command -v hey >/dev/null 2>&1 || { $(call print_warning,"Installing 'hey' for load testing..."); go install github.com/rakyll/hey@latest; }
	@echo "\n🧪 Testing Place Backend..."
	@hey -n 1000 -c 10 http://localhost:8000/health | head -20
	@echo "\n🧪 Testing Unified Gateway..."
	@hey -n 1000 -c 10 http://localhost:9000/health | head -20
	@echo "\n🧪 Testing Frontend..."
	@hey -n 100 -c 5 http://localhost:8501/healthz | head -20
	$(call print_success,"Performance tests completed")

test-endpoints: ## Test API endpoints
	$(call print_info,"Testing API endpoints...")
	@echo "\n🔗 API Endpoint Tests:"
	@curl -s -o /dev/null -w "Place Backend Health: %{http_code} (%{time_total}s)\n" http://localhost:8000/health
	@curl -s -o /dev/null -w "Unified Gateway Health: %{http_code} (%{time_total}s)\n" http://localhost:9000/health
	@curl -s -o /dev/null -w "Frontend Health: %{http_code} (%{time_total}s)\n" http://localhost:8501/healthz
	$(call print_success,"Endpoint tests completed")

##@ Cleanup
cleanup: ## Clean up Docker resources
	$(call print_info,"Cleaning up Docker resources...")
	docker system prune -f
	$(call print_success,"Docker cleanup completed")

cleanup-all: ## Clean up all Docker resources including volumes
	$(call print_warning,"This will remove ALL Docker resources including volumes!")
	@read -p "Are you sure? [y/N] " -n 1 -r; echo; if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker system prune -a -f --volumes; \
		$(call print_success,"Complete Docker cleanup completed"); \
	else \
		$(call print_info,"Cleanup cancelled"); \
	fi

##@ Utility
shell: ## Access container shell (usage: make shell SERVICE=place-backend ENV=dev)
	@if [ -z "$(SERVICE)" ]; then \
		$(call print_error,"Please specify SERVICE. Usage: make shell SERVICE=place-backend ENV=dev"); \
		exit 1; \
	fi
	$(call print_info,"Accessing shell for $(SERVICE)...")
	@if [ "$(ENV)" = "prod" ]; then \
		docker-compose -f $(COMPOSE_PROD_FILE) exec $(SERVICE) /bin/bash || docker-compose -f $(COMPOSE_PROD_FILE) exec $(SERVICE) /bin/sh; \
	else \
		docker-compose -f $(COMPOSE_FILE) exec $(SERVICE) /bin/bash || docker-compose -f $(COMPOSE_FILE) exec $(SERVICE) /bin/sh; \
	fi

report: ## Generate comprehensive status report
	$(call print_info,"Generating comprehensive status report...")
	@mkdir -p logs
	@{  \
		echo "{"; \
		echo "  \"timestamp\": \"$$(date -Iseconds)\","; \
		echo "  \"version\": \"3.1.0\","; \
		echo "  \"environment\": \"docker\","; \
		echo "  \"docker_version\": \"$$(docker --version | cut -d' ' -f3 | cut -d',' -f1)\","; \
		echo "  \"docker_compose_version\": \"$$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)\","; \
		echo "  \"containers\": $$(docker ps --format json | jq -s .),"; \
		echo "  \"volumes\": $$(docker volume ls --format json | jq -s .),"; \
		echo "  \"networks\": $$(docker network ls --format json | jq -s .)"; \
		echo "}"; \
	} > logs/system_status_$$(date +%Y%m%d_%H%M%S).json
	$(call print_success,"Status report generated in logs/ directory")

##@ Information
env-info: ## Show environment information
	@echo -e "\n${BLUE}🔧 Environment Information${NC}"
	@echo "============================="
	@echo "Docker Version: $$(docker --version)"
	@echo "Docker Compose Version: $$(docker-compose --version)"
	@echo "Docker Buildx Version: $$(docker buildx version 2>/dev/null || echo 'Not available')"
	@echo "Kubectl Version: $$(kubectl version --client --short 2>/dev/null || echo 'Not available')"
	@echo "Current Directory: $$(pwd)"
	@echo "Available Make Targets: $$(make -qp | awk -F':' '/^[a-zA-Z0-9][^$$#\/\\t=]*:([^=]|$$)/ {split($$1,A,/ /);for(i in A)print A[i]}' | sort -u | grep -v '^Makefile$$' | wc -l) targets"

# Include local makefile extensions if they exist
-include Makefile.local
