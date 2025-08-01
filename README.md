# 🌐 Multi-Place Fingerprint Attendance System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.47.1-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive, scalable fingerprint attendance management system designed for organizations with multiple locations and devices. Built with modern web technologies and real-time data processing capabilities.

## 🚀 Quick Start

### Windows
```batch
# One-command startup
start_all_services.bat
```

### Linux/Mac
```bash
# One-command startup
./scripts/start_all_services.sh
```

**Access the system:** http://localhost:8501

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Development](#-development)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

## ✨ Features

### 🏢 **Multi-Place Support**
- ✅ Unlimited locations with independent backends
- ✅ Each place can have multiple fingerprint devices
- ✅ Centralized data aggregation and analysis
- ✅ Place-specific and device-specific reporting

### 🔧 **Technical Features**
- ✅ **Modern Web Stack**: FastAPI + Streamlit + Python 3.8+
- ✅ **Real-time Analytics**: Live attendance monitoring and statistics
- ✅ **Async Processing**: High-performance concurrent operations
- ✅ **RESTful APIs**: Comprehensive API endpoints for all operations
- ✅ **Cross-platform**: Windows, Linux, and macOS support
- ✅ **Scalable Architecture**: Easy to add new places and devices

### 📊 **Analytics & Reporting**
- ✅ **Multi-level Analysis**: System, place, device, and user levels
- ✅ **Interactive Dashboards**: Real-time charts and visualizations
- ✅ **Export Capabilities**: CSV export with filtering options
- ✅ **Holiday Management**: Configurable holidays with custom dates
- ✅ **Working Hours Tracking**: Progress monitoring and compliance

### 🔒 **Security & Reliability**
- ✅ **CORS Protection**: Secure cross-origin resource sharing
- ✅ **Input Validation**: Comprehensive data validation
- ✅ **Error Handling**: Graceful error handling and recovery
- ✅ **Health Monitoring**: Real-time system health checks

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend Layer (Port 8501)                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              Streamlit Cloud Dashboard                     │ │
│  │  • Multi-place analytics and visualization                 │ │
│  │  • Real-time data aggregation and reporting                │ │
│  │  • Interactive charts and export capabilities              │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTP API Calls
┌─────────────────────▼───────────────────────────────────────────┐
│              Unified Gateway Layer (Port 9000)                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │               Unified Backend Gateway                       │ │
│  │  • Single API endpoint for all places                      │ │
│  │  • Data aggregation and normalization                      │ │
│  │  • Async calls to place backends                           │ │
│  │  • Health monitoring and failover                          │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──┬─────────────────┬─────────────────┬─────────────────────────────┘
   │                 │                 │ HTTP API Calls
┌──▼─────┐  ┌────────▼─────┐  ┌────────▼─────┐
│Place 1 │  │ Place 2      │  │ Place 3      │
│8000    │  │ 8001         │  │ 8002         │
│        │  │              │  │              │
│Backend │  │ Backend      │  │ Backend      │
│API     │  │ API          │  │ API          │
│        │  │              │  │              │
│Device1 │  │ Device1      │  │ Device1      │
│Device2 │  │ Device2      │  │ Device2      │
└────────┘  └──────────────┘  └──────────────┘
```

## 🛠️ Installation

### Prerequisites

- **Python 3.8+** (recommended: Python 3.9 or 3.10)
- **Git** for version control
- **ZK Fingerprint Devices** with network connectivity

### Option 1: Automatic Setup (Recommended)

#### Windows
```batch
# Clone the repository
git clone https://github.com/your-org/BiometricFlow-ZK.git
cd BiometricFlow-ZK

# Run automatic setup
setup.bat
```

#### Linux/Mac
```bash
# Clone the repository
git clone https://github.com/your-org/BiometricFlow-ZK.git
cd BiometricFlow-ZK

# Make scripts executable
chmod +x scripts/*.sh

# Run automatic setup
./scripts/setup.sh
```

### Option 2: Manual Setup

1. **Clone Repository**
```bash
git clone https://github.com/your-org/BiometricFlow-ZK.git
cd BiometricFlow-ZK
```

2. **Create Virtual Environment**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Devices**
```bash
# Copy and edit device configurations
cp backend/devices_config_example.json backend/devices_config_place1.json
# Edit the file with your device details
```

## ⚙️ Configuration

### Device Configuration

Create device configuration files for each place:

```json
// backend/devices_config_place1.json
{
  "Back Office": {
    "name": "Back Office",
    "ip": "192.168.1.151",
    "port": 4370,
    "password": 0
  },
  "Reception": {
    "name": "Reception",
    "ip": "192.168.1.152",
    "port": 4370,
    "password": 0
  }
}
```

### Place Configuration

Edit `backend/unified_backends_config.json`:

```json
{
  "Place_1_MainOffice": {
    "name": "Place_1_MainOffice",
    "location": "Main Office Building",
    "url": "http://localhost:8000",
    "timeout": 30,
    "devices": ["Back Office", "Reception"],
    "description": "Main office with multiple devices"
  },
  "Place_2_ShowRoom": {
    "name": "Place_2_ShowRoom",
    "location": "Show Room Complex",
    "url": "http://localhost:8001",
    "timeout": 30,
    "devices": ["Show-Room-1", "Show-Room-4"],
    "description": "Customer show room facility"
  }
}
```

### Environment Variables

Create `.env` file in the root directory:

```env
# Backend Configuration
BACKEND_NAME=Place_1_MainOffice
BACKEND_PORT=8000
BACKEND_LOCATION=Main Office Building
DEVICES_CONFIG_FILE=devices_config_place1.json

# Gateway Configuration
GATEWAY_PORT=9000
FRONTEND_BACKEND_PORT=9001
ALLOWED_ORIGINS=http://localhost:8501,http://localhost:9001

# Security
API_KEY=your_secure_api_key_here
DEBUG=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/system.log
```

## 🚀 Usage

### Starting the System

#### Complete System (All Services)

**Windows:**
```batch
start_all_services.bat
```

**Linux/Mac:**
```bash
./scripts/start_all_services.sh
```

#### Individual Services

**Place Backends:**
```batch
# Windows
start_place1_backend.bat
start_place2_backend.bat
start_place3_backend.bat

# Linux/Mac
./scripts/start_place1_backend.sh
./scripts/start_place2_backend.sh
./scripts/start_place3_backend.sh
```

**Unified Gateway:**
```batch
# Windows
start_unified_backend.bat

# Linux/Mac
./scripts/start_unified_backend.sh
```

**Frontend:**
```batch
# Windows
start_frontend.bat

# Linux/Mac
./scripts/start_frontend.sh
```

### Accessing the System

| Service | URL | Purpose |
|---------|-----|---------|
| **Main Dashboard** | http://localhost:8501 | Primary user interface |
| **Unified API** | http://localhost:9000 | Central API gateway |
| **API Documentation** | http://localhost:9000/docs | Interactive API docs |
| **Place 1 API** | http://localhost:8000 | Direct place 1 access |
| **Place 2 API** | http://localhost:8001 | Direct place 2 access |
| **Place 3 API** | http://localhost:8002 | Direct place 3 access |

## 📚 API Documentation

### Unified Gateway Endpoints

#### **Global Operations**
- `GET /` - Gateway information and status
- `GET /health` - Health check for all places
- `GET /places` - List all configured places
- `GET /devices/all` - All devices from all places
- `GET /attendance/all` - All attendance data unified
- `GET /users/all` - All users from all places
- `GET /summary/all` - Summary statistics from all places

#### **Place-Specific Operations**
- `GET /place/{place_name}/devices` - Devices from specific place
- `GET /place/{place_name}/attendance` - Attendance from specific place
- `GET /place/{place_name}/users` - Users from specific place
- `GET /place/{place_name}/summary` - Summary for specific place

#### **Device-Specific Operations**
- `GET /device/{device_name}/info` - Device information
- `GET /device/{device_name}/attendance` - Attendance for specific device

### Example API Calls

```bash
# Get all devices
curl "http://localhost:9000/devices/all"

# Get attendance for specific date range
curl "http://localhost:9000/attendance/all?start_date=2025-01-01&end_date=2025-01-31"

# Get attendance with custom holidays
curl "http://localhost:9000/attendance/all?start_date=2025-01-01&end_date=2025-01-31&additional_holidays=2025-01-15,2025-01-20"

# Get place-specific data
curl "http://localhost:9000/place/Place_1_MainOffice/attendance?start_date=2025-01-01&end_date=2025-01-31"
```

## 🔧 Development

### Project Structure

```
BiometricFlow-ZK/
├── 📂 backend/                     # Backend Services
│   ├── fingerprint_backend_local.py   # Place backend service
│   ├── unified_backend_cloud.py       # Unified gateway service
│   ├── devices_config_*.json          # Device configurations
│   ├── unified_backends_config.json   # Place configurations
│   └── requirements.txt                # Backend dependencies
├── 📂 frontend/                    # Frontend Application
│   ├── streamlit_cloud_app.py         # Main UI application
│   └── requirements.txt                # Frontend dependencies
├── 📂 scripts/                    # Cross-platform Scripts
│   ├── setup.sh                       # Linux/Mac setup
│   ├── start_all_services.sh          # Linux/Mac launcher
│   ├── start_place*_backend.sh        # Linux/Mac place starters
│   ├── start_unified_backend.sh       # Linux/Mac gateway starter
│   └── start_frontend.sh              # Linux/Mac frontend starter
├── 📂 docs/                       # Documentation
│   ├── api.md                         # API documentation
│   ├── deployment.md                  # Deployment guide
│   └── troubleshooting.md             # Common issues
├── 📂 tests/                      # Test Suite
│   ├── test_backend.py               # Backend tests
│   ├── test_frontend.py              # Frontend tests
│   └── test_integration.py           # Integration tests
├── 📦 Docker/                     # Container Deployment
│   ├── Dockerfile.backend            # Backend container
│   ├── Dockerfile.frontend           # Frontend container
│   └── docker-compose.yml            # Multi-container setup
├── requirements.txt               # Complete system dependencies
├── setup.bat                     # Windows setup script
├── start_*.bat                   # Windows startup scripts
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest

# Run specific test categories
pytest tests/test_backend.py
pytest tests/test_frontend.py
pytest tests/test_integration.py

# Run with coverage
pytest --cov=backend --cov=frontend
```

### Code Quality

```bash
# Format code
black backend/ frontend/

# Lint code
flake8 backend/ frontend/

# Type checking
mypy backend/ frontend/
```

## 🐳 Deployment

### Docker Deployment (Recommended)

```bash
# Build and run all services
docker-compose up --build

# Run in background
docker-compose up -d

# Stop all services
docker-compose down
```

### Production Deployment

```bash
# Install production dependencies
pip install gunicorn supervisor

# Copy supervisor configuration
cp configs/supervisord.conf /etc/supervisor/conf.d/

# Start services
supervisorctl start all
```

### Environment-Specific Configurations

- **Development**: Use `start_all_services.*` scripts
- **Testing**: Use `pytest` with test configurations
- **Staging**: Use Docker Compose with staging environment
- **Production**: Use supervisor with production configs

## 🔍 Troubleshooting

### Common Issues

#### Device Connection Problems
```bash
# Check device connectivity
ping 192.168.1.151

# Test device ports
telnet 192.168.1.151 4370

# Check backend logs
tail -f logs/backend.log
```

#### Service Startup Issues
```bash
# Check if ports are available
netstat -an | grep :8000
netstat -an | grep :9000

# Kill existing processes
pkill -f "fingerprint_backend"
pkill -f "unified_backend"
```

#### Performance Issues
```bash
# Monitor system resources
top
htop

# Check memory usage
free -h

# Monitor disk usage
df -h
```

### Support

- **Documentation**: Check `docs/` directory
- **Issues**: Create GitHub issue with logs
- **Discussions**: Use GitHub Discussions for questions
- **Email**: support@yourcompany.com

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Code Standards

- Follow PEP 8 for Python code
- Use meaningful commit messages
- Add tests for new features
- Update documentation for changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **ZK-SDK**: Fingerprint device integration
- **FastAPI**: Modern web framework
- **Streamlit**: Rapid web app development
- **Plotly**: Interactive visualizations
- **Community**: All contributors and users

---

## 📊 Project Status

**Current Version**: 1.0.0
**Status**: ✅ Production Ready

### Recent Updates

- ✅ Multi-place architecture implementation
- ✅ Cross-platform script support
- ✅ Enhanced holiday management
- ✅ Improved error handling and logging
- ✅ Comprehensive documentation

### Roadmap

- 🔄 Database integration for persistence
- 🔄 User authentication and authorization  
- 🔄 Mobile application development
- 🔄 Advanced analytics and ML insights
- 🔄 Real-time notifications system

---

**Made with ❤️ by the [Eng. Osama Mohamed](https://github.com/OsamaM0)**