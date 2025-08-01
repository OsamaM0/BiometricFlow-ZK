#!/usr/bin/env python3
"""
BiometricFlow-ZK Project Manager

A comprehensive project management utility for development and deployment.
"""

import os
import sys
import subprocess
import argparse
import json
from pathlib import Path
from typing import List, Dict


class ProjectManager:
    """Project management utility for BiometricFlow-ZK"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.src_dir = self.project_root / "src"
        self.config_dir = self.project_root / "config"
        self.scripts_dir = self.project_root / "scripts"
        self.logs_dir = self.project_root / "logs"
        
        # Ensure logs directory exists
        self.logs_dir.mkdir(exist_ok=True)
    
    def install_dependencies(self):
        """Install project dependencies"""
        print("🔧 Installing dependencies...")
        
        # Install main dependencies
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        
        # Install development dependencies
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements-dev.txt"], check=True)
        
        # Install package in development mode
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], check=True)
        
        print("✅ Dependencies installed successfully!")
    
    def start_place_backend(self, place_name: str, port: int):
        """Start a place backend service"""
        print(f"🚀 Starting place backend: {place_name} on port {port}")
        
        config_file = self.config_dir / "devices" / f"{place_name}.json"
        if not config_file.exists():
            print(f"❌ Configuration file not found: {config_file}")
            return False
        
        cmd = [
            sys.executable, "-m", "biometric_flow.backend.place_backend",
            "--config", str(config_file),
            "--port", str(port),
            "--place", place_name
        ]
        
        log_file = self.logs_dir / f"place_backend_{place_name}.log"
        
        with open(log_file, "w") as log:
            process = subprocess.Popen(cmd, stdout=log, stderr=log)
            print(f"✅ Place backend {place_name} started (PID: {process.pid})")
            return True
    
    def start_unified_gateway(self, port: int = 9000):
        """Start the unified gateway service"""
        print(f"🌐 Starting unified gateway on port {port}")
        
        cmd = [
            sys.executable, "-m", "biometric_flow.backend.unified_gateway",
            "--port", str(port)
        ]
        
        log_file = self.logs_dir / "unified_gateway.log"
        
        with open(log_file, "w") as log:
            process = subprocess.Popen(cmd, stdout=log, stderr=log)
            print(f"✅ Unified gateway started (PID: {process.pid})")
            return True
    
    def start_frontend(self, port: int = 8501):
        """Start the frontend application"""
        print(f"🖥️ Starting frontend on port {port}")
        
        app_file = self.src_dir / "biometric_flow" / "frontend" / "app.py"
        
        cmd = [
            "streamlit", "run", str(app_file),
            "--server.port", str(port),
            "--server.headless", "true"
        ]
        
        log_file = self.logs_dir / "frontend.log"
        
        with open(log_file, "w") as log:
            process = subprocess.Popen(cmd, stdout=log, stderr=log)
            print(f"✅ Frontend started (PID: {process.pid})")
            return True
    
    def start_all_services(self):
        """Start all services in the correct order"""
        print("🚀 Starting all BiometricFlow-ZK services...")
        
        # Load backend configuration
        backends_config_file = self.config_dir / "environments" / "backends.json"
        if not backends_config_file.exists():
            backends_config_file = self.config_dir / "unified_backends_config.json"
        
        if not backends_config_file.exists():
            print("❌ Backend configuration file not found")
            return False
        
        with open(backends_config_file) as f:
            backends_config = json.load(f)
        
        # Start place backends
        for place_name, place_config in backends_config.get("places", {}).items():
            port = place_config.get("port", 8000)
            self.start_place_backend(place_name, port)
        
        # Start unified gateway
        self.start_unified_gateway()
        
        # Start frontend
        self.start_frontend()
        
        print("\n🎉 All services started successfully!")
        print("📊 Access the system:")
        print("   - Frontend: http://localhost:8501")
        print("   - API Gateway: http://localhost:9000")
        print("   - API Docs: http://localhost:9000/docs")
        
        return True
    
    def run_tests(self):
        """Run the test suite"""
        print("🧪 Running tests...")
        
        test_commands = [
            [sys.executable, "-m", "pytest", "tests/", "-v"],
            [sys.executable, "tests/test_unified_system.py"],
            [sys.executable, "tests/test_api_endpoints.py"]
        ]
        
        for cmd in test_commands:
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError:
                print(f"❌ Test failed: {' '.join(cmd)}")
                return False
        
        print("✅ All tests passed!")
        return True
    
    def check_health(self):
        """Check system health"""
        print("🔍 Checking system health...")
        
        health_script = self.project_root / "tests" / "test_unified_system.py"
        if health_script.exists():
            subprocess.run([sys.executable, str(health_script)])
        else:
            print("❌ Health check script not found")
    
    def format_code(self):
        """Format code using black and isort"""
        print("🎨 Formatting code...")
        
        # Run black
        subprocess.run(["black", "src/", "tests/", "scripts/"], check=True)
        
        # Run isort
        subprocess.run(["isort", "src/", "tests/", "scripts/"], check=True)
        
        print("✅ Code formatting completed!")
    
    def lint_code(self):
        """Lint code using flake8"""
        print("🔍 Linting code...")
        
        subprocess.run(["flake8", "src/", "tests/", "scripts/"], check=True)
        
        print("✅ Code linting completed!")
    
    def build_docs(self):
        """Build documentation"""
        print("📚 Building documentation...")
        
        docs_dir = self.project_root / "docs"
        if docs_dir.exists():
            # Here you could add Sphinx documentation building
            print("📚 Documentation is available in docs/ directory")
        else:
            print("❌ Documentation directory not found")
    
    def clean_project(self):
        """Clean project artifacts"""
        print("🧹 Cleaning project...")
        
        # Remove Python cache
        subprocess.run(["find", ".", "-name", "*.pyc", "-delete"], shell=True)
        subprocess.run(["find", ".", "-name", "__pycache__", "-type", "d", "-delete"], shell=True)
        
        # Remove logs
        if self.logs_dir.exists():
            for log_file in self.logs_dir.glob("*.log"):
                log_file.unlink()
        
        print("✅ Project cleaned!")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="BiometricFlow-ZK Project Manager")
    parser.add_argument("command", choices=[
        "install", "start-all", "start-place", "start-gateway", "start-frontend",
        "test", "health", "format", "lint", "docs", "clean"
    ], help="Command to execute")
    
    parser.add_argument("--place", help="Place name for place-specific commands")
    parser.add_argument("--port", type=int, help="Port number for services")
    
    args = parser.parse_args()
    
    manager = ProjectManager()
    
    if args.command == "install":
        manager.install_dependencies()
    elif args.command == "start-all":
        manager.start_all_services()
    elif args.command == "start-place":
        if not args.place or not args.port:
            print("❌ --place and --port required for start-place command")
            sys.exit(1)
        manager.start_place_backend(args.place, args.port)
    elif args.command == "start-gateway":
        port = args.port or 9000
        manager.start_unified_gateway(port)
    elif args.command == "start-frontend":
        port = args.port or 8501
        manager.start_frontend(port)
    elif args.command == "test":
        manager.run_tests()
    elif args.command == "health":
        manager.check_health()
    elif args.command == "format":
        manager.format_code()
    elif args.command == "lint":
        manager.lint_code()
    elif args.command == "docs":
        manager.build_docs()
    elif args.command == "clean":
        manager.clean_project()


if __name__ == "__main__":
    main()
