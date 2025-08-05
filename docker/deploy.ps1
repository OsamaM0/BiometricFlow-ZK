# =================================================================
# BiometricFlow-ZK Docker Deployment Script (Windows PowerShell)
# =================================================================
# Comprehensive Docker deployment and management script for Windows

param(
    [Parameter(Position=0)]
    [ValidateSet("setup", "build", "start", "stop", "restart", "status", "logs", "health", "cleanup", "help")]
    [string]$Command = "help",
    
    [Parameter(Position=1)]
    [ValidateSet("dev", "prod", "development", "production")]
    [string]$Environment = "development",
    
    [Parameter(Position=2)]
    [string]$Service = "",
    
    [switch]$Volumes,
    [switch]$Help
)

# Script configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir
$ComposeFile = Join-Path $ProjectRoot "docker-compose.yml"
$ComposeProdFile = Join-Path $ProjectRoot "docker-compose.prod.yml"
$EnvFile = Join-Path $ProjectRoot ".env.docker"

# Function to write colored output
function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Header {
    Write-Host ""
    Write-Host "🚀 BiometricFlow-ZK Docker Manager" -ForegroundColor Blue
    Write-Host "========================================" -ForegroundColor Blue
    Write-Host ""
}

# Function to check prerequisites
function Test-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    # Check Docker
    try {
        $null = docker --version
    }
    catch {
        Write-Error "Docker is not installed. Please install Docker Desktop for Windows first."
        exit 1
    }
    
    # Check Docker Compose
    try {
        $null = docker-compose --version
    }
    catch {
        try {
            $null = docker compose version
        }
        catch {
            Write-Error "Docker Compose is not available. Please ensure Docker Desktop is properly installed."
            exit 1
        }
    }
    
    # Check if Docker daemon is running
    try {
        $null = docker info 2>$null
    }
    catch {
        Write-Error "Docker daemon is not running. Please start Docker Desktop first."
        exit 1
    }
    
    Write-Success "Prerequisites check passed"
}

# Function to setup environment
function Initialize-Environment {
    Write-Info "Setting up environment..."
    
    Set-Location $ProjectRoot
    
    # Copy environment file if it doesn't exist
    if (-not (Test-Path ".env")) {
        Copy-Item ".env.docker" ".env"
        Write-Success "Created .env file from template"
    }
    
    # Create required directories
    $directories = @("logs", "data", "data\place_backend", "data\gateway", "data\frontend", "backups")
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    
    # Generate authentication keys if they don't exist
    $envFiles = @("place_backend.env", "unified_gateway.env", "frontend.env")
    $needsKeys = $false
    foreach ($file in $envFiles) {
        if (-not (Test-Path $file)) {
            $needsKeys = $true
            break
        }
    }
    
    if ($needsKeys) {
        Write-Info "Generating authentication keys..."
        python generate_keys.py
        Write-Success "Authentication keys generated"
    }
    
    Write-Success "Environment setup completed"
}

# Function to build images
function Build-Images {
    param([string]$Env = "development")
    
    Write-Info "Building Docker images for $Env environment..."
    
    Set-Location $ProjectRoot
    
    if ($Env -eq "production" -or $Env -eq "prod") {
        docker-compose -f $ComposeProdFile build --no-cache
    }
    else {
        docker-compose -f $ComposeFile build --no-cache
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker images built successfully"
    }
    else {
        Write-Error "Failed to build Docker images"
        exit 1
    }
}

# Function to start services
function Start-Services {
    param([string]$Env = "development")
    
    Write-Info "Starting BiometricFlow-ZK services in $Env mode..."
    
    Set-Location $ProjectRoot
    
    if ($Env -eq "production" -or $Env -eq "prod") {
        docker-compose -f $ComposeProdFile up -d
    }
    else {
        docker-compose -f $ComposeFile up -d
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Services started successfully"
        Write-Info "Waiting for services to be ready..."
        
        # Wait for services to be healthy
        Start-Sleep -Seconds 30
        
        # Check service health
        Test-ServiceHealth
    }
    else {
        Write-Error "Failed to start services"
        exit 1
    }
}

# Function to stop services
function Stop-Services {
    param([string]$Env = "development")
    
    Write-Info "Stopping BiometricFlow-ZK services..."
    
    Set-Location $ProjectRoot
    
    if ($Env -eq "production" -or $Env -eq "prod") {
        docker-compose -f $ComposeProdFile down
    }
    else {
        docker-compose -f $ComposeFile down
    }
    
    Write-Success "Services stopped successfully"
}

# Function to check service health
function Test-ServiceHealth {
    Write-Info "Checking service health..."
    
    $services = @(
        @{Name="place-backend"; Port=8000},
        @{Name="unified-gateway"; Port=9000},
        @{Name="frontend"; Port=8501}
    )
    
    $allHealthy = $true
    
    foreach ($service in $services) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$($service.Port)/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Success "$($service.Name) service is healthy"
            }
            else {
                Write-Warning "$($service.Name) service returned status $($response.StatusCode)"
                $allHealthy = $false
            }
        }
        catch {
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:$($service.Port)/healthz" -Method GET -TimeoutSec 5 -ErrorAction Stop
                if ($response.StatusCode -eq 200) {
                    Write-Success "$($service.Name) service is healthy"
                }
                else {
                    Write-Warning "$($service.Name) service is not responding"
                    $allHealthy = $false
                }
            }
            catch {
                Write-Warning "$($service.Name) service is not responding"
                $allHealthy = $false
            }
        }
    }
    
    if ($allHealthy) {
        Write-Success "All services are healthy!"
    }
    else {
        Write-Warning "Some services may need more time to start"
    }
}

# Function to show logs
function Show-Logs {
    param(
        [string]$ServiceName = "",
        [string]$Env = "development"
    )
    
    Set-Location $ProjectRoot
    
    if ($ServiceName) {
        Write-Info "Showing logs for $ServiceName..."
        if ($Env -eq "production" -or $Env -eq "prod") {
            docker-compose -f $ComposeProdFile logs -f $ServiceName
        }
        else {
            docker-compose -f $ComposeFile logs -f $ServiceName
        }
    }
    else {
        Write-Info "Showing logs for all services..."
        if ($Env -eq "production" -or $Env -eq "prod") {
            docker-compose -f $ComposeProdFile logs -f
        }
        else {
            docker-compose -f $ComposeFile logs -f
        }
    }
}

# Function to show status
function Show-Status {
    param([string]$Env = "development")
    
    Write-Info "Service Status:"
    
    Set-Location $ProjectRoot
    
    if ($Env -eq "production" -or $Env -eq "prod") {
        docker-compose -f $ComposeProdFile ps
    }
    else {
        docker-compose -f $ComposeFile ps
    }
    
    Write-Host ""
    Test-ServiceHealth
    
    Write-Host ""
    Write-Info "Access URLs:"
    Write-Host "🌐 Frontend Dashboard: http://localhost:8501"
    Write-Host "🔗 Unified Gateway API: http://localhost:9000"
    Write-Host "🏢 Place Backend API: http://localhost:8000"
    Write-Host "📚 API Documentation: http://localhost:9000/docs"
}

# Function to clean up
function Remove-Resources {
    param([bool]$IncludeVolumes = $false)
    
    Write-Info "Cleaning up Docker resources..."
    
    Set-Location $ProjectRoot
    
    # Stop and remove containers
    docker-compose -f $ComposeFile down 2>$null
    docker-compose -f $ComposeProdFile down 2>$null
    
    # Remove unused images
    docker image prune -f
    
    # Remove volumes if requested
    if ($IncludeVolumes) {
        Write-Warning "Removing persistent volumes (this will delete all data)..."
        docker volume prune -f
    }
    
    Write-Success "Cleanup completed"
}

# Function to show help
function Show-Help {
    Write-Host "BiometricFlow-ZK Docker Management Script (PowerShell)"
    Write-Host ""
    Write-Host "Usage: .\deploy.ps1 [COMMAND] [ENVIRONMENT] [OPTIONS]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  setup                    Setup environment and generate keys"
    Write-Host "  build [dev|prod]         Build Docker images"
    Write-Host "  start [dev|prod]         Start all services"
    Write-Host "  stop [dev|prod]          Stop all services"
    Write-Host "  restart [dev|prod]       Restart all services"
    Write-Host "  status [dev|prod]        Show service status"
    Write-Host "  logs [service] [env]     Show logs (optional: specific service)"
    Write-Host "  health                   Check service health"
    Write-Host "  cleanup [-Volumes]       Clean up Docker resources"
    Write-Host "  help                     Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\deploy.ps1 setup                 # Setup environment"
    Write-Host "  .\deploy.ps1 start dev             # Start development environment"
    Write-Host "  .\deploy.ps1 start prod            # Start production environment"
    Write-Host "  .\deploy.ps1 logs frontend         # Show frontend logs"
    Write-Host "  .\deploy.ps1 cleanup -Volumes      # Clean up including volumes"
    Write-Host ""
}

# Main script logic
function Main {
    Write-Header
    
    if ($Help) {
        Show-Help
        return
    }
    
    switch ($Command.ToLower()) {
        "setup" {
            Test-Prerequisites
            Initialize-Environment
        }
        "build" {
            Test-Prerequisites
            Build-Images -Env $Environment
        }
        "start" {
            Test-Prerequisites
            Initialize-Environment
            Start-Services -Env $Environment
        }
        "stop" {
            Stop-Services -Env $Environment
        }
        "restart" {
            Stop-Services -Env $Environment
            Start-Services -Env $Environment
        }
        "status" {
            Show-Status -Env $Environment
        }
        "logs" {
            Show-Logs -ServiceName $Service -Env $Environment
        }
        "health" {
            Test-ServiceHealth
        }
        "cleanup" {
            Remove-Resources -IncludeVolumes $Volumes
        }
        "help" {
            Show-Help
        }
        default {
            Write-Error "Unknown command: $Command"
            Show-Help
            exit 1
        }
    }
}

# Run main function
Main
