# 🐳 BiometricFlow-ZK Docker Deployment Guide

## Overview

BiometricFlow-ZK now includes comprehensive **Docker containerization** support for enterprise-grade deployment with isolated services, automated orchestration, and production-ready configurations.

## 🏗️ Docker Architecture

### **Container Services**
```
┌─────────────────────────────────────────────────────────────────┐
│                    🐳 Docker Environment                        │
│                                                                 │
│  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────┐ │
│  │   Frontend      │    │ Unified Gateway  │    │Place Backend│ │
│  │  Container      │    │   Container      │    │ Container   │ │
│  │                 │    │                  │    │             │ │
│  │ - Streamlit     │◄──►│ - FastAPI       │◄──►│ - FastAPI   │ │
│  │ - Port 8501     │    │ - Port 9000      │    │ - Port 8000 │ │
│  │ - Auto Auth     │    │ - Token Manager  │    │ - Device Mgr│ │
│  │ - Volume Mount  │    │ - Health Checks  │    │ - Local Data│ │
│  └─────────────────┘    └──────────────────┘    └─────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                🌐 Docker Network                            │ │
│  │     biometric-flow-network (172.20.0.0/16)                │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                💾 Docker Volumes                           │ │
│  │  • place_backend_data  • gateway_data  • frontend_data     │ │
│  │  • production_logs     • backup_data                       │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### **Key Features**
- ✅ **Multi-stage builds** for optimized image sizes
- ✅ **Non-root user execution** for enhanced security
- ✅ **Health checks** for all services
- ✅ **Volume persistence** for data and logs
- ✅ **Environment isolation** with separate configurations
- ✅ **Automatic service dependencies** and startup ordering
- ✅ **Resource limits** and constraints for production

## 🚀 Quick Start

### **Prerequisites**
```bash
# Install Docker Desktop (Windows/macOS) or Docker Engine (Linux)
# Verify installation
docker --version
docker-compose --version
```

### **1. Clone and Setup**
```bash
# Clone repository
git clone https://github.com/OsamaM0/BiometricFlow-ZK.git
cd BiometricFlow-ZK

# Make scripts executable (Linux/macOS)
chmod +x docker/deploy.sh docker/health_check.sh
```

### **2. Development Deployment (Recommended for testing)**
```bash
# Linux/macOS
./docker/deploy.sh setup
./docker/deploy.sh start dev

# Windows PowerShell
.\docker\deploy.ps1 setup
.\docker\deploy.ps1 start dev
```

### **3. Production Deployment**
```bash
# Linux/macOS
./docker/deploy.sh setup
./docker/deploy.sh start prod

# Windows PowerShell
.\docker\deploy.ps1 setup
.\docker\deploy.ps1 start prod
```

### **4. Verify Deployment**
```bash
# Check service status
./docker/deploy.sh status

# Run health check
./docker/health_check.sh

# View logs
./docker/deploy.sh logs
```

## 🔧 Manual Docker Commands

### **Build Images**
```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build place-backend
docker-compose build unified-gateway
docker-compose build frontend
```

### **Start Services**
```bash
# Start all services (development)
docker-compose up -d

# Start all services (production)
docker-compose -f docker-compose.prod.yml up -d

# Start specific service
docker-compose up -d place-backend
```

### **View Logs**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f frontend
docker-compose logs -f unified-gateway
docker-compose logs -f place-backend

# Last 100 lines
docker-compose logs --tail=100 frontend
```

### **Stop Services**
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v
```

## 📁 Docker Files Structure

```
BiometricFlow-ZK/
├── 🐳 Docker Configuration
│   ├── Dockerfile.place-backend      # Place backend service
│   ├── Dockerfile.unified-gateway    # Gateway service  
│   ├── Dockerfile.frontend           # Frontend service
│   ├── docker-compose.yml            # Development environment
│   ├── docker-compose.prod.yml       # Production environment
│   └── .env.docker                   # Environment template
├── 🛠️ Management Scripts
│   ├── docker/deploy.sh              # Linux/macOS deployment script
│   ├── docker/deploy.ps1             # Windows deployment script
│   └── docker/health_check.sh        # Health monitoring script
└── 📄 Configuration Files
    ├── devices_config.json           # Device configuration
    ├── backend_places_config.json    # Backend routing config
    └── *.env                         # Service environment files
```

## ⚙️ Configuration

### **Environment Variables (.env)**
```bash
# Copy template and customize
cp .env.docker .env

# Key configuration options
COMPOSE_PROJECT_NAME=biometricflow-zk
ENVIRONMENT=production
RATE_LIMIT_REQUESTS=50
SESSION_TIMEOUT=3600

# Resource limits (production)
PLACE_BACKEND_CPU_LIMIT=1.0
PLACE_BACKEND_MEMORY_LIMIT=512M
GATEWAY_CPU_LIMIT=1.5
GATEWAY_MEMORY_LIMIT=768M
FRONTEND_CPU_LIMIT=2.0
FRONTEND_MEMORY_LIMIT=1024M
```

### **Volume Persistence**
```yaml
# Data volumes (automatically created)
volumes:
  place_backend_data:    # Device and attendance data
  gateway_data:          # Gateway cache and logs
  frontend_data:         # Frontend session data
  production_logs:       # Centralized logging
```

### **Network Configuration**
```yaml
# Internal network for service communication
networks:
  biometric-network:
    driver: bridge
    subnet: 172.20.0.0/16  # Development
    # subnet: 172.21.0.0/16  # Production
```

## 🔐 Security Features

### **Container Security**
- ✅ **Non-root execution** - All services run as `biometric` user
- ✅ **Read-only filesystem** - Production containers use read-only mode
- ✅ **No new privileges** - Prevents privilege escalation
- ✅ **Security options** - Additional hardening for production

### **Network Security**
- ✅ **Isolated network** - Services communicate only within Docker network
- ✅ **Port exposure** - Only necessary ports exposed to host
- ✅ **Health checks** - Built-in health monitoring for all services

### **Data Security**
- ✅ **Volume encryption** - Data volumes can be encrypted
- ✅ **Secret management** - Environment files for sensitive data
- ✅ **Access control** - Proper file permissions in containers

## 📊 Monitoring & Health Checks

### **Built-in Health Checks**
```bash
# Service health endpoints
curl http://localhost:8000/health    # Place Backend
curl http://localhost:9000/health    # Unified Gateway  
curl http://localhost:8501/healthz   # Frontend

# Docker health status
docker-compose ps
```

### **Comprehensive Health Monitoring**
```bash
# Run complete health check
./docker/health_check.sh

# Continuous monitoring
./docker/health_check.sh --continuous 60

# Generate health report
./docker/health_check.sh --report
```

### **Log Monitoring**
```bash
# Real-time log monitoring
docker-compose logs -f

# Error detection
docker-compose logs | grep -i "error\|exception\|failed"

# Log rotation (production)
# Automatic log rotation configured with max size and files
```

## 🔧 Troubleshooting

### **Common Issues**

#### **Services Won't Start**
```bash
# Check Docker daemon
docker info

# Check available ports
netstat -tlnp | grep -E "(8000|8501|9000)"

# Check logs for errors
docker-compose logs place-backend
docker-compose logs unified-gateway
docker-compose logs frontend
```

#### **Authentication Errors**
```bash
# Regenerate authentication keys
python generate_keys.py

# Restart services
docker-compose restart

# Test authentication flow
python test_auth_flow.py
```

#### **Port Conflicts**
```bash
# Modify ports in docker-compose.yml
ports:
  - "8001:8000"  # Change host port if 8000 is occupied
  - "9001:9000"  # Change host port if 9000 is occupied
  - "8502:8501"  # Change host port if 8501 is occupied
```

#### **Resource Issues**
```bash
# Check resource usage
docker stats

# Increase resource limits in docker-compose.prod.yml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 1024M
```

### **Debug Mode**
```bash
# Run with debug logging
docker-compose up --build

# Access container shell
docker exec -it biometric-place-backend /bin/bash
docker exec -it biometric-unified-gateway /bin/bash
docker exec -it biometric-frontend /bin/bash

# View container logs in real-time
docker logs -f biometric-place-backend
```

## 🚀 Production Deployment

### **Production Checklist**
- [ ] Use `docker-compose.prod.yml` for production
- [ ] Configure resource limits appropriately
- [ ] Set up log rotation and monitoring
- [ ] Configure backup strategy for volumes
- [ ] Set up reverse proxy (nginx/traefik) if needed
- [ ] Configure SSL/TLS certificates
- [ ] Set up monitoring and alerting
- [ ] Test disaster recovery procedures

### **Production Commands**
```bash
# Production deployment
./docker/deploy.sh start prod

# Production health monitoring
./docker/health_check.sh --continuous 30

# Production backup (manual)
docker run --rm -v biometric-place-backend-prod-data:/data -v $(pwd)/backups:/backup alpine tar czf /backup/place_backend_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .
```

### **Scaling (Future Enhancement)**
```bash
# Scale services (requires Docker Swarm or Kubernetes)
docker-compose up -d --scale unified-gateway=3
docker-compose up -d --scale place-backend=2
```

## 📚 Additional Resources

### **Access URLs (after deployment)**
- 🌐 **Frontend Dashboard**: http://localhost:8501
- 🔗 **Unified Gateway API**: http://localhost:9000
- 🏢 **Place Backend API**: http://localhost:8000
- 📚 **API Documentation**: http://localhost:9000/docs
- 📋 **Alternative Docs**: http://localhost:9000/redoc

### **Management Commands**
```bash
# View all available commands
./docker/deploy.sh help
./docker/deploy.ps1 help

# System cleanup
./docker/deploy.sh cleanup
./docker/deploy.sh cleanup --volumes  # ⚠️ Deletes all data
```

---

## 🎉 Success Verification

After successful deployment, you should see:
1. ✅ All three containers running (`docker-compose ps`)
2. ✅ Health checks passing (`./docker/health_check.sh`)
3. ✅ Frontend accessible at http://localhost:8501
4. ✅ API gateway responding at http://localhost:9000/docs
5. ✅ Authentication flow working (`python test_auth_flow.py`)

**Your BiometricFlow-ZK system is now running in Docker with enterprise-grade containerization! 🐳**
