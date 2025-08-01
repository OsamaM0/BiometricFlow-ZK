# BiometricFlow-ZK Deployment Guide

## Overview

This guide covers deployment options for the BiometricFlow-ZK system in various environments.

## Prerequisites

- Python 3.8 or higher
- Windows/Linux/macOS
- Network access to fingerprint devices
- Minimum 2GB RAM, 1GB disk space

## Quick Start Deployment

### Windows

1. **Clone and Setup**
   ```batch
   git clone <repository-url>
   cd BiometricFlow-ZK
   scripts\deployment\setup.bat
   ```

2. **Start All Services**
   ```batch
   scripts\deployment\start_all_services.bat
   ```

3. **Access the System**
   - Frontend: http://localhost:8501
   - API Gateway: http://localhost:9000

### Linux/Mac

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd BiometricFlow-ZK
   chmod +x scripts/deployment/*.sh
   scripts/deployment/setup.sh
   ```

2. **Start All Services**
   ```bash
   scripts/deployment/start_all_services.sh
   ```

## Manual Deployment

### 1. Environment Setup

Create virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

Install dependencies:
```bash
pip install -r requirements.txt
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
