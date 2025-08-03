# 🚀 BiometricFlow-ZK Enterprise Deployment Guide v3.0

## 🌟 Executive Deployment Overview

**BiometricFlow-ZK Enterprise** delivers world-class deployment flexibility, supporting everything from rapid prototyping to global enterprise installations. Our deployment architecture is built for **zero-downtime updates**, **horizontal scalability**, and **enterprise security compliance** across cloud, on-premise, and hybrid environments.

### **🎯 Enterprise Deployment Strategies**

#### **⚡ Development & Testing**
- **🔧 Local Development**: Instant setup for developers and QA teams
- **🧪 Staging Environment**: Production-like testing with data isolation
- **🔄 CI/CD Integration**: Automated testing and deployment pipelines

#### **🏢 Enterprise Production**
- **🌐 High Availability**: Multi-region deployments with 99.99% uptime SLA
- **⚖️ Load Balancing**: Intelligent traffic distribution and auto-scaling
- **🔒 Security Hardening**: Enterprise-grade security with compliance frameworks
- **📊 Observability**: Comprehensive monitoring, alerting, and performance analytics

#### **☁️ Cloud-Native Deployment**
- **🚀 Kubernetes**: Container orchestration with Helm charts and operators
- **🐳 Docker**: Containerized microservices with multi-stage builds
- **🌍 Multi-Cloud**: AWS, Azure, GCP deployment with cloud-specific optimizations
- **🔄 GitOps**: Infrastructure as Code with automated rollbacks and versioning

## ⚡ Enterprise Quick Start Deployment

### **📋 Prerequisites & System Requirements**

#### **Production Environment Specifications**
```yaml
system_requirements:
  operating_systems:
    - "Windows Server 2019+ / Windows 10/11 Pro"
    - "Ubuntu Server 20.04+ LTS / Red Hat Enterprise Linux 8+"
    - "macOS 11+ (development environments)"
  
  hardware_minimums:
    development:
      cpu: "2 cores (4 vCPUs recommended)"
      memory: "4GB RAM (8GB recommended)"
      storage: "20GB SSD (50GB recommended)"
    production:
      cpu: "8 cores (16 vCPUs recommended)"
      memory: "16GB RAM (32GB recommended)"
      storage: "100GB SSD (NVMe preferred)"
      network: "1Gbps ethernet (10Gbps for enterprise)"
  
  software_dependencies:
    runtime: "Python 3.8+ (3.11 recommended)"
    database: "PostgreSQL 13+ / Redis 6+ / MongoDB 5+"
    web_server: "NGINX 1.20+ / Apache 2.4+ / HAProxy 2.4+"
    monitoring: "Prometheus 2.30+ / Grafana 8.0+"
```

#### **🔐 Security & Compliance Requirements**
- **🛡️ SSL/TLS Certificates**: Valid certificates for production domains
- **🔥 Firewall Configuration**: Ports 80, 443, 8000-9001 for application traffic
- **🔐 Secret Management**: HashiCorp Vault, AWS Secrets Manager, or Azure Key Vault
- **📋 Compliance**: GDPR, HIPAA, SOX, or industry-specific compliance requirements
- **🚨 Security Monitoring**: SIEM integration for threat detection and response

### **🖥️ Windows Enterprise Production Deployment**

#### **🚀 PowerShell Automated Enterprise Setup**
```powershell
# Prerequisites validation and system preparation
Write-Host "🔍 Validating Enterprise Prerequisites..." -ForegroundColor Cyan

# Clone enterprise repository with authentication
git clone https://github.com/OsamaM0/BiometricFlow-ZK.git
Set-Location BiometricFlow-ZK

# Initialize enterprise security framework
Write-Host "🛡️ Initializing Enterprise Security..." -ForegroundColor Yellow
.\setup_security.ps1 -Environment "Production" -ComplianceLevel "Enterprise" -EnableMFA

# Configure high-availability deployment
$deploymentConfig = @{
    Environment = "Production"
    SecurityLevel = "Enterprise" 
    HighAvailability = $true
    LoadBalancing = $true
    Monitoring = $true
    BackupStrategy = "RealTime"
    SSL = $true
    ComplianceMode = "GDPR,HIPAA"
}

# Execute enterprise deployment with monitoring
Write-Host "🚀 Deploying Enterprise Stack..." -ForegroundColor Green
.\scripts\deployment\deploy_enterprise.ps1 @deploymentConfig

# Verify deployment health and performance
Write-Host "✅ Running Post-Deployment Validation..." -ForegroundColor Green
.\scripts\deployment\validate_deployment.ps1 -HealthChecks -PerformanceTests -SecurityValidation
```

#### **🏢 Windows Service Installation (Production)**
```powershell
# Install as Windows Services for enterprise reliability
$services = @(
    @{Name="BiometricFlow-Gateway"; Path=".\src\biometric_flow\backend\unified_gateway.py"; Port=9000},
    @{Name="BiometricFlow-Place1"; Path=".\src\biometric_flow\backend\place_backend.py"; Port=8000},
    @{Name="BiometricFlow-Place2"; Path=".\src\biometric_flow\backend\place_backend.py"; Port=8001},
    @{Name="BiometricFlow-Frontend"; Path=".\src\biometric_flow\frontend\app.py"; Port=8501}
)

foreach ($service in $services) {
    Write-Host "Installing service: $($service.Name)" -ForegroundColor Yellow
    
    # Create Windows Service with automatic restart
    sc.exe create $service.Name binPath="python $($service.Path)" start=auto
    sc.exe description $service.Name "BiometricFlow-ZK Enterprise Service - $($service.Name)"
    
    # Configure service recovery options
    sc.exe failure $service.Name reset=86400 actions=restart/5000/restart/10000/restart/30000
    
    # Start service
    Start-Service -Name $service.Name
}

# Verify all services are running
Get-Service -Name "BiometricFlow-*" | Format-Table -AutoSize
```

### **🐧 Linux/Unix Enterprise Production Deployment**

#### **🚀 Automated Production Setup with SystemD**
```bash
#!/bin/bash
# BiometricFlow-ZK Enterprise Linux Deployment Script

echo "🔍 Enterprise Prerequisites Validation..."

# System requirements validation
check_system_requirements() {
    echo "🖥️  Checking system requirements..."
    
    # Check Python version
    python_version=$(python3 --version | cut -d' ' -f2)
    if [[ "$(printf '%s\n' "3.8" "$python_version" | sort -V | head -n1)" != "3.8" ]]; then
        echo "❌ Python 3.8+ required. Current: $python_version"
        exit 1
    fi
    
    # Check available memory
    total_memory=$(free -m | grep '^Mem:' | awk '{print $2}')
    if [[ $total_memory -lt 4096 ]]; then
        echo "⚠️  Warning: Less than 4GB RAM available. Performance may be impacted."
    fi
    
    # Check disk space
    available_space=$(df -m . | tail -1 | awk '{print $4}')
    if [[ $available_space -lt 20480 ]]; then
        echo "❌ Insufficient disk space. At least 20GB required."
        exit 1
    fi
    
    echo "✅ System requirements validated successfully"
}

# Enterprise security hardening
setup_enterprise_security() {
    echo "🛡️ Setting up enterprise security..."
    
    # Create dedicated user for security isolation
    sudo useradd -r -s /bin/false biometricflow
    sudo mkdir -p /opt/biometricflow
    sudo chown biometricflow:biometricflow /opt/biometricflow
    
    # Set up SSL certificates
    sudo mkdir -p /etc/ssl/biometricflow
    # Generate self-signed certificates for development
    sudo openssl req -x509 -nodes -days 365 -newkey rsa:4096 \
        -keyout /etc/ssl/biometricflow/server.key \
        -out /etc/ssl/biometricflow/server.crt \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=biometricflow.local"
    
    # Set proper permissions
    sudo chmod 600 /etc/ssl/biometricflow/server.key
    sudo chmod 644 /etc/ssl/biometricflow/server.crt
    
    echo "✅ Enterprise security configured successfully"
}

# Deploy application with enterprise configuration
deploy_enterprise_application() {
    echo "🚀 Deploying BiometricFlow-ZK Enterprise..."
    
    # Clone repository
    git clone https://github.com/OsamaM0/BiometricFlow-ZK.git /opt/biometricflow/app
    cd /opt/biometricflow/app
    
    # Create virtual environment
    python3 -m venv /opt/biometricflow/venv
    source /opt/biometricflow/venv/bin/activate
    
    # Install dependencies
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install gunicorn uvicorn[standard] prometheus-client
    
    # Set ownership
    sudo chown -R biometricflow:biometricflow /opt/biometricflow
    
    echo "✅ Application deployed successfully"
}

# Create SystemD services for enterprise reliability
create_systemd_services() {
    echo "⚙️ Creating SystemD services..."
    
    # Gateway Service
    sudo tee /etc/systemd/system/biometricflow-gateway.service > /dev/null <<EOF
[Unit]
Description=BiometricFlow-ZK Enterprise Gateway
After=network.target
Requires=network.target

[Service]
Type=exec
User=biometricflow
Group=biometricflow
WorkingDirectory=/opt/biometricflow/app
Environment=PATH=/opt/biometricflow/venv/bin
Environment=PYTHONPATH=/opt/biometricflow/app/src
ExecStart=/opt/biometricflow/venv/bin/uvicorn src.biometric_flow.backend.unified_gateway:app --host 0.0.0.0 --port 9000 --workers 4
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    # Place Backend Services (Template)
    for i in {1..3}; do
        port=$((7999 + i))
        sudo tee /etc/systemd/system/biometricflow-place${i}.service > /dev/null <<EOF
[Unit]
Description=BiometricFlow-ZK Place ${i} Backend
After=network.target
Requires=network.target

[Service]
Type=exec
User=biometricflow
Group=biometricflow
WorkingDirectory=/opt/biometricflow/app
Environment=PATH=/opt/biometricflow/venv/bin
Environment=PYTHONPATH=/opt/biometricflow/app/src
Environment=PLACE_ID=${i}
Environment=PLACE_PORT=${port}
ExecStart=/opt/biometricflow/venv/bin/uvicorn src.biometric_flow.backend.place_backend:app --host 0.0.0.0 --port ${port}
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    done

    # Frontend Service
    sudo tee /etc/systemd/system/biometricflow-frontend.service > /dev/null <<EOF
[Unit]
Description=BiometricFlow-ZK Enterprise Frontend
After=network.target
Requires=network.target

[Service]
Type=exec
User=biometricflow
Group=biometricflow
WorkingDirectory=/opt/biometricflow/app
Environment=PATH=/opt/biometricflow/venv/bin
Environment=PYTHONPATH=/opt/biometricflow/app/src
ExecStart=/opt/biometricflow/venv/bin/streamlit run src/biometric_flow/frontend/app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    # Reload SystemD and enable services
    sudo systemctl daemon-reload
    
    # Enable and start services
    services=("biometricflow-gateway" "biometricflow-place1" "biometricflow-place2" "biometricflow-place3" "biometricflow-frontend")
    for service in "${services[@]}"; do
        sudo systemctl enable "$service"
        sudo systemctl start "$service"
        echo "✅ Started service: $service"
    done
    
    echo "✅ SystemD services configured and started successfully"
}

# Configure NGINX reverse proxy for enterprise
setup_nginx_proxy() {
    echo "🌐 Setting up NGINX reverse proxy..."
    
    sudo apt update && sudo apt install -y nginx
    
    # Create NGINX configuration
    sudo tee /etc/nginx/sites-available/biometricflow > /dev/null <<EOF
upstream biometricflow_gateway {
    server 127.0.0.1:9000;
}

upstream biometricflow_frontend {
    server 127.0.0.1:8501;
}

server {
    listen 80;
    server_name biometricflow.local;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name biometricflow.local;
    
    ssl_certificate /etc/ssl/biometricflow/server.crt;
    ssl_certificate_key /etc/ssl/biometricflow/server.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    
    # API Gateway
    location /api/ {
        proxy_pass http://biometricflow_gateway/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Frontend Dashboard
    location / {
        proxy_pass http://biometricflow_frontend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

    # Enable site and restart NGINX
    sudo ln -sf /etc/nginx/sites-available/biometricflow /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl restart nginx
    
    echo "✅ NGINX reverse proxy configured successfully"
}

# Main deployment execution
main() {
    echo "🚀 Starting BiometricFlow-ZK Enterprise Deployment..."
    
    check_system_requirements
    setup_enterprise_security
    deploy_enterprise_application
    create_systemd_services
    setup_nginx_proxy
    
    echo ""
    echo "🎉 Enterprise deployment completed successfully!"
    echo ""
    echo "📊 Service Status:"
    sudo systemctl status biometricflow-* --no-pager -l
    echo ""
    echo "🌐 Access Points:"
    echo "  • Dashboard: https://biometricflow.local"
    echo "  • API Gateway: https://biometricflow.local/api"
    echo "  • API Documentation: https://biometricflow.local/api/docs"
    echo ""
    echo "🔍 Monitoring Commands:"
    echo "  • View logs: sudo journalctl -f -u biometricflow-gateway"
    echo "  • Service status: sudo systemctl status biometricflow-*"
    echo "  • Restart services: sudo systemctl restart biometricflow-*"
}

# Execute main deployment
main "$@"
```

### **🐳 Docker Enterprise Deployment**

#### **🏗️ Production Docker Compose Configuration**
```yaml
# docker-compose.enterprise.yml
version: '3.8'

services:
  # Redis Cache for Enterprise Performance
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    networks:
      - biometric_network
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # PostgreSQL Database for Production Data
  postgresql:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: biometricflow
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./sql/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - biometric_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 30s
      timeout: 10s
      retries: 5

  # Enterprise API Gateway
  gateway:
    build:
      context: .
      dockerfile: docker/Dockerfile.gateway
      args:
        BUILD_ENV: production
    restart: unless-stopped
    ports:
      - "9000:9000"
    environment:
      - ENVIRONMENT=production
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgresql:5432/biometricflow
      - JWT_SECRET=${JWT_SECRET}
      - API_KEY=${API_KEY}
    depends_on:
      redis:
        condition: service_healthy
      postgresql:
        condition: service_healthy
    networks:
      - biometric_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'

  # Place Backend Services (Auto-scaling)
  place-backend-1:
    build:
      context: .
      dockerfile: docker/Dockerfile.backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - PLACE_ID=1
      - ENVIRONMENT=production
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgresql:5432/biometricflow
    depends_on:
      redis:
        condition: service_healthy
      postgresql:
        condition: service_healthy
    networks:
      - biometric_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  place-backend-2:
    build:
      context: .
      dockerfile: docker/Dockerfile.backend
    restart: unless-stopped
    ports:
      - "8001:8001"
    environment:
      - PLACE_ID=2
      - ENVIRONMENT=production
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgresql:5432/biometricflow
    depends_on:
      redis:
        condition: service_healthy
      postgresql:
        condition: service_healthy
    networks:
      - biometric_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Enterprise Frontend Dashboard
  frontend:
    build:
      context: .
      dockerfile: docker/Dockerfile.frontend
    restart: unless-stopped
    ports:
      - "8501:8501"
    environment:
      - ENVIRONMENT=production
      - API_GATEWAY_URL=http://gateway:9000
    depends_on:
      - gateway
    networks:
      - biometric_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # NGINX Reverse Proxy with SSL
  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - gateway
      - frontend
    networks:
      - biometric_network

  # Prometheus Monitoring
  prometheus:
    image: prom/prometheus:latest
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
    networks:
      - biometric_network

  # Grafana Dashboard
  grafana:
    image: grafana/grafana:latest
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
    depends_on:
      - prometheus
    networks:
      - biometric_network

volumes:
  redis_data:
  postgres_data:
  prometheus_data:
  grafana_data:

networks:
  biometric_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

#### **🚀 Docker Enterprise Deployment Commands**
```bash
# Production deployment with Docker Compose
echo "🐳 Deploying BiometricFlow-ZK Enterprise with Docker..."

# Create environment file
cat > .env.production <<EOF
# Database Configuration
DB_USER=biometricflow
DB_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)

# Security Configuration
JWT_SECRET=$(openssl rand -base64 64)
API_KEY=$(uuidgen)

# Grafana Configuration
GRAFANA_PASSWORD=$(openssl rand -base64 16)

# Environment
ENVIRONMENT=production
EOF

# Deploy enterprise stack
docker-compose -f docker-compose.enterprise.yml --env-file .env.production up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
docker-compose -f docker-compose.enterprise.yml ps

# Verify deployment
echo "✅ Verifying enterprise deployment..."
curl -f http://localhost:9000/health || echo "❌ Gateway health check failed"
curl -f http://localhost:8501/_stcore/health || echo "❌ Frontend health check failed"

echo "🎉 Enterprise Docker deployment completed successfully!"
echo ""
echo "🌐 Access Points:"
echo "  • Dashboard: http://localhost:8501"
echo "  • API Gateway: http://localhost:9000"
echo "  • Monitoring: http://localhost:3000 (admin/$(grep GRAFANA_PASSWORD .env.production | cut -d'=' -f2))"
echo "  • Metrics: http://localhost:9090"
```

### **☁️ Cloud-Native Kubernetes Deployment**

#### **🚀 Kubernetes Enterprise Manifests**
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: biometricflow-enterprise
  labels:
    name: biometricflow-enterprise
    environment: production

---
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: biometricflow-secrets
  namespace: biometricflow-enterprise
type: Opaque
data:
  db-password: # base64 encoded password
  jwt-secret: # base64 encoded JWT secret
  api-key: # base64 encoded API key

---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: biometricflow-config
  namespace: biometricflow-enterprise
data:
  environment: "production"
  log-level: "INFO"
  metrics-enabled: "true"

---
# k8s/gateway-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: biometricflow-gateway
  namespace: biometricflow-enterprise
  labels:
    app: biometricflow-gateway
    version: v3.0.0
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: biometricflow-gateway
  template:
    metadata:
      labels:
        app: biometricflow-gateway
        version: v3.0.0
    spec:
      containers:
      - name: gateway
        image: biometricflow/gateway:v3.0.0
        ports:
        - containerPort: 9000
          name: http
        env:
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: biometricflow-config
              key: environment
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: biometricflow-secrets
              key: jwt-secret
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: biometricflow-secrets
              key: api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        readinessProbe:
          httpGet:
            path: /health
            port: 9000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        livenessProbe:
          httpGet:
            path: /health
            port: 9000
          initialDelaySeconds: 60
          periodSeconds: 30
          timeoutSeconds: 10
          failureThreshold: 3
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL

---
# k8s/gateway-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: biometricflow-gateway-service
  namespace: biometricflow-enterprise
  labels:
    app: biometricflow-gateway
spec:
  type: ClusterIP
  ports:
  - port: 9000
    targetPort: 9000
    name: http
  selector:
    app: biometricflow-gateway

---
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: biometricflow-ingress
  namespace: biometricflow-enterprise
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
spec:
  tls:
  - hosts:
    - biometricflow.company.com
    secretName: biometricflow-tls
  rules:
  - host: biometricflow.company.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: biometricflow-gateway-service
            port:
              number: 9000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: biometricflow-frontend-service
            port:
              number: 8501

---
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: biometricflow-gateway-hpa
  namespace: biometricflow-enterprise
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: biometricflow-gateway
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
```

#### **🚀 Kubernetes Deployment Commands**
```bash
# Deploy to Kubernetes cluster
echo "☸️ Deploying BiometricFlow-ZK Enterprise to Kubernetes..."

# Create namespace and secrets
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml

# Deploy application components
kubectl apply -f k8s/gateway-deployment.yaml
kubectl apply -f k8s/gateway-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml

# Configure ingress and auto-scaling
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml

# Wait for deployment to be ready
kubectl wait --for=condition=available --timeout=300s deployment/biometricflow-gateway -n biometricflow-enterprise
kubectl wait --for=condition=available --timeout=300s deployment/biometricflow-frontend -n biometricflow-enterprise

# Verify deployment
kubectl get all -n biometricflow-enterprise

echo "✅ Kubernetes enterprise deployment completed successfully!"
echo ""
echo "🌐 Access Points:"
echo "  • External URL: https://biometricflow.company.com"
echo "  • Port Forward: kubectl port-forward -n biometricflow-enterprise svc/biometricflow-gateway-service 9000:9000"
echo ""
echo "🔍 Monitoring Commands:"
echo "  • Logs: kubectl logs -f -n biometricflow-enterprise deployment/biometricflow-gateway"
echo "  • Status: kubectl get pods -n biometricflow-enterprise"
echo "  • Scale: kubectl scale deployment biometricflow-gateway --replicas=5 -n biometricflow-enterprise"
```

## 🌐 Enterprise Service Access Matrix

### **🎯 Production Access Points**
| **Service** | **URL** | **Purpose** | **Security** | **SLA** | **Monitoring** |
|-------------|---------|-------------|--------------|---------|----------------|
| 🏢 **Executive Dashboard** | https://dashboard.company.com | C-level analytics & KPIs | 🔒 SSO + MFA + RBAC | 99.99% | Real-time |
| 🔗 **Enterprise API Gateway** | https://api.company.com | Unified API integration | 🛡️ JWT + API Keys + Rate Limiting | 99.99% | <100ms |
| 📖 **API Documentation** | https://api.company.com/docs | Interactive developer portal | 🔐 Developer access control | 99.9% | Static CDN |
| 📊 **System Monitoring** | https://monitoring.company.com | Operational dashboards | 🔒 Admin + DevOps access | 99.9% | 24/7 |
| 🔍 **Log Analytics** | https://logs.company.com | Centralized logging & search | 🔒 Security + Audit access | 99.9% | Real-time |

### **🚨 Health Check & Monitoring Endpoints**
```bash
# Comprehensive health validation
curl -f https://api.company.com/health | jq '.'
curl -f https://dashboard.company.com/_stcore/health

# Performance metrics validation
curl -f https://api.company.com/metrics/prometheus
curl -f https://monitoring.company.com/api/v1/query?query=up

# Security validation
curl -H "Authorization: Bearer invalid-token" https://api.company.com/users/all
# Should return 401 Unauthorized

# Load testing validation
ab -n 1000 -c 10 https://api.company.com/health
# Should maintain <100ms response times
```

---

## 🔧 Post-Deployment Configuration

### **🛡️ Security Hardening Checklist**
- [ ] **SSL/TLS Configuration**: Valid certificates with A+ SSL Labs rating
- [ ] **Firewall Rules**: Only necessary ports open (80, 443, management ports)
- [ ] **User Access Control**: Role-based permissions with principle of least privilege
- [ ] **API Security**: Rate limiting, input validation, and OWASP compliance
- [ ] **Monitoring Setup**: Security event logging and alerting
- [ ] **Backup Strategy**: Automated backups with disaster recovery testing
- [ ] **Compliance Validation**: GDPR, HIPAA, SOX compliance verification

### **📊 Performance Optimization**
- [ ] **Database Tuning**: Index optimization and query performance
- [ ] **Cache Configuration**: Redis cluster setup with proper eviction policies
- [ ] **Load Balancing**: Multi-instance deployment with health checks
- [ ] **CDN Integration**: Static asset delivery optimization
- [ ] **Monitoring Setup**: Comprehensive metrics collection and alerting

### **🔄 Maintenance Procedures**
- [ ] **Update Strategy**: Blue-green deployment for zero-downtime updates
- [ ] **Backup Verification**: Regular restore testing and data integrity checks
- [ ] **Security Scanning**: Automated vulnerability assessment and patching
- [ ] **Performance Testing**: Regular load testing and capacity planning
- [ ] **Documentation**: Runbook creation and team training

---

**🏆 BiometricFlow-ZK Enterprise Deployment v3.0** - *Powering Scalable Workforce Management*

**© 2025 BiometricFlow-ZK Project | Engineered by [Eng. Osama Mohamed](https://github.com/OsamaM0)**
```

### 2. Configuration

Edit configuration files in `config/`:

- `config/environments/development.env` - Environment variables
- `config/environments/backends.json` - Place backend configurations
- `config/devices/place*.json` - Device configurations for each place

### 3. Service Startup

Start services in order:

1. **Place Backends**
   ```bash
   python src/biometric_flow/backend/place_backend.py --config=config/devices/place1.json --port=8000
   python src/biometric_flow/backend/place_backend.py --config=config/devices/place2.json --port=8001
   python src/biometric_flow/backend/place_backend.py --config=config/devices/place3.json --port=8002
   ```

2. **Unified Gateway**
   ```bash
   python src/biometric_flow/backend/unified_gateway.py --port=9000
   ```

3. **Frontend Application**
   ```bash
   streamlit run src/biometric_flow/frontend/app.py --server.port=8501
   ```

## Docker Deployment

### Build Images

```bash
# Backend services
docker build -f Dockerfile.backend -t biometric-flow-backend .

# Frontend application
docker build -f Dockerfile.frontend -t biometric-flow-frontend .
```

### Run with Docker Compose

```bash
docker-compose up -d
```

## Production Deployment

### Using Systemd (Linux)

1. **Create Service Files**

   `/etc/systemd/system/biometric-flow-place1.service`:
   ```ini
   [Unit]
   Description=BiometricFlow Place 1 Backend
   After=network.target

   [Service]
   Type=simple
   User=biometric
   WorkingDirectory=/opt/biometric-flow
   Environment=PATH=/opt/biometric-flow/.venv/bin
   ExecStart=/opt/biometric-flow/.venv/bin/python src/biometric_flow/backend/place_backend.py --config=config/devices/place1.json --port=8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

2. **Enable and Start Services**
   ```bash
   sudo systemctl enable biometric-flow-place1
   sudo systemctl start biometric-flow-place1
   ```

### Using Nginx (Reverse Proxy)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:9000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Cloud Deployment

### AWS EC2

1. **Launch EC2 Instance**
   - Ubuntu 20.04 LTS
   - t3.medium or larger
   - Security group allowing ports 80, 443, 8000-9000

2. **Setup Application**
   ```bash
   # Install dependencies
   sudo apt update
   sudo apt install python3.8 python3-pip nginx supervisor

   # Deploy application
   git clone <repository-url>
   cd BiometricFlow-ZK
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Supervisor**
   ```ini
   [program:biometric-flow-gateway]
   command=/opt/biometric-flow/.venv/bin/python src/biometric_flow/backend/unified_gateway.py
   directory=/opt/biometric-flow
   autostart=true
   autorestart=true
   user=ubuntu
   ```

### Azure Container Instances

```yaml
apiVersion: 2019-12-01
location: eastus
name: biometric-flow
properties:
  containers:
  - name: backend
    properties:
      image: biometric-flow-backend:latest
      ports:
      - port: 9000
      resources:
        requests:
          cpu: 1
          memoryInGb: 2
  - name: frontend
    properties:
      image: biometric-flow-frontend:latest
      ports:
      - port: 8501
      resources:
        requests:
          cpu: 0.5
          memoryInGb: 1
  osType: Linux
  ipAddress:
    type: Public
    ports:
    - protocol: tcp
      port: 80
    - protocol: tcp
      port: 9000
    - protocol: tcp
      port: 8501
```

## Monitoring and Maintenance

### Health Checks

Test system health:
```bash
python tests/test_unified_system.py
```

### Log Management

Logs are stored in `logs/` directory:
- `logs/place_backend_*.log`
- `logs/unified_gateway.log`
- `logs/frontend.log`

### Backup Procedures

1. **Configuration Backup**
   ```bash
   tar -czf backup-config-$(date +%Y%m%d).tar.gz config/
   ```

2. **Database Backup** (if using database)
   ```bash
   pg_dump biometric_flow > backup-db-$(date +%Y%m%d).sql
   ```

### Updates

1. **Stop Services**
   ```bash
   scripts/deployment/stop_all_services.sh
   ```

2. **Update Code**
   ```bash
   git pull origin main
   pip install -r requirements.txt
   ```

3. **Restart Services**
   ```bash
   scripts/deployment/start_all_services.sh
   ```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   netstat -tulpn | grep :8000
   kill -9 <process_id>
   ```

2. **Device Connection Failed**
   - Check device IP and port
   - Verify network connectivity
   - Check firewall settings

3. **Service Won't Start**
   - Check logs in `logs/` directory
   - Verify configuration files
   - Check Python environment

### Support

For deployment issues:
- Check logs in `logs/` directory
- Run health checks: `python tests/test_unified_system.py`
- Review configuration files
- Contact support with log files
