# =================================================================
# BiometricFlow-ZK Enhanced Docker Management Script (PowerShell)
# =================================================================
# Complete Docker ecosystem management with monitoring and scaling

param(
    [Parameter(Position=0)]
    [string]$Command = "help",
    
    [Parameter(Position=1)]
    [string]$Environment = "development",
    
    [Parameter(Position=2)]
    [string]$Option = ""
)

# Script configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$ComposeFile = Join-Path $ProjectRoot "docker-compose.yml"
$ComposeProdFile = Join-Path $ProjectRoot "docker-compose.prod.yml"
$ComposeMonitoringFile = Join-Path $ProjectRoot "docker\docker-compose.monitoring.yml"
$SwarmStackFile = Join-Path $ProjectRoot "docker\docker-stack.yml"
$EnvFile = Join-Path $ProjectRoot ".env.docker"

# Colors for output
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Blue }
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Header { 
    Write-Host "`n🚀 BiometricFlow-ZK Enhanced Docker Manager" -ForegroundColor Magenta
    Write-Host "==============================================" -ForegroundColor Magenta
    Write-Host ""
}

# Function to check Docker Swarm
function Test-SwarmMode {
    try {
        $swarmInfo = docker info --format '{{.Swarm.LocalNodeState}}' 2>$null
        return $swarmInfo -eq "active"
    } catch {
        return $false
    }
}

# Function to initialize Docker Swarm
function Initialize-Swarm {
    Write-Info "Initializing Docker Swarm..."
    
    if (Test-SwarmMode) {
        Write-Warning "Docker Swarm is already initialized"
        return
    }
    
    # Get local IP address
    $localIP = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Ethernet*" | Select-Object -First 1).IPAddress
    
    docker swarm init --advertise-addr $localIP
    
    # Create overlay network for Traefik
    docker network create --driver=overlay --attachable traefik-public 2>$null
    
    Write-Success "Docker Swarm initialized successfully"
}

# Function to create Docker secrets
function New-DockerSecrets {
    Write-Info "Creating Docker secrets..."
    
    Set-Location $ProjectRoot
    
    # Generate keys if they don't exist
    if (-not (Test-Path "place_backend.env") -or -not (Test-Path "unified_gateway.env") -or -not (Test-Path "frontend.env")) {
        python generate_keys.py
    }
    
    # Create secrets
    try { docker secret create place_backend_env place_backend.env 2>$null } catch { Write-Warning "Secret place_backend_env already exists" }
    try { docker secret create unified_gateway_env unified_gateway.env 2>$null } catch { Write-Warning "Secret unified_gateway_env already exists" }
    try { docker secret create frontend_env frontend.env 2>$null } catch { Write-Warning "Secret frontend_env already exists" }
    
    # Create configs
    try { docker config create devices_config devices_config.json 2>$null } catch { Write-Warning "Config devices_config already exists" }
    try { docker config create backend_places_config backend_places_config.json 2>$null } catch { Write-Warning "Config backend_places_config already exists" }
    
    Write-Success "Docker secrets and configs created"
}

# Function to build multi-architecture images
function Build-MultiArchImages {
    Write-Info "Building multi-architecture Docker images..."
    
    Set-Location $ProjectRoot
    
    # Create buildx builder if it doesn't exist
    try { docker buildx create --name biometric-builder --use --bootstrap 2>$null } catch { }
    
    # Build all images
    docker buildx bake -f docker\docker-bake.hcl --push
    
    Write-Success "Multi-architecture images built and pushed"
}

# Function to deploy monitoring stack
function Deploy-MonitoringStack {
    Write-Info "Deploying monitoring stack..."
    
    Set-Location $ProjectRoot
    
    # Create monitoring directories
    $monitoringDirs = @(
        "monitoring\prometheus\rules",
        "monitoring\grafana\dashboards",
        "monitoring\grafana\datasources",
        "monitoring\grafana\alerting",
        "monitoring\alertmanager",
        "monitoring\loki",
        "monitoring\promtail",
        "monitoring\blackbox"
    )
    
    foreach ($dir in $monitoringDirs) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    
    # Start monitoring stack
    docker-compose -f $ComposeMonitoringFile up -d
    
    Write-Success "Monitoring stack deployed successfully"
    Write-Info "Access URLs:"
    Write-Host "📊 Grafana: http://localhost:3000 (admin/BiometricFlow2025!)"
    Write-Host "📈 Prometheus: http://localhost:9090"
    Write-Host "🚨 AlertManager: http://localhost:9093"
    Write-Host "📋 Loki: http://localhost:3100"
}

# Function to deploy to Docker Swarm
function Deploy-SwarmStack {
    Write-Info "Deploying to Docker Swarm..."
    
    if (-not (Test-SwarmMode)) {
        Initialize-Swarm
    }
    
    New-DockerSecrets
    
    # Deploy stack
    docker stack deploy -c $SwarmStackFile biometric-flow
    
    Write-Success "Stack deployed to Docker Swarm"
    
    # Show services
    docker stack services biometric-flow
}

# Function to scale services
function Set-ServiceScale {
    param(
        [string]$Environment = "development",
        [string]$ScaleConfig = "place-backend=2,unified-gateway=3,frontend=2"
    )
    
    Write-Info "Scaling services: $ScaleConfig"
    
    Set-Location $ProjectRoot
    
    $scaleArgs = $ScaleConfig -split ',' | ForEach-Object { "--scale $_" }
    
    if ($Environment -eq "production") {
        & docker-compose -f $ComposeProdFile up -d @scaleArgs
    } else {
        & docker-compose -f $ComposeFile up -d @scaleArgs
    }
    
    Write-Success "Services scaled successfully"
}

# Function to backup data
function Backup-Data {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupDir = Join-Path $ProjectRoot "backups\$timestamp"
    
    Write-Info "Creating backup in $backupDir..."
    
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    
    # Backup volumes
    docker run --rm -v biometric-place-backend-data:/source -v "${backupDir}:/backup" alpine tar czf /backup/place-backend-data.tar.gz -C /source .
    docker run --rm -v biometric-gateway-data:/source -v "${backupDir}:/backup" alpine tar czf /backup/gateway-data.tar.gz -C /source .
    docker run --rm -v biometric-frontend-data:/source -v "${backupDir}:/backup" alpine tar czf /backup/frontend-data.tar.gz -C /source .
    
    # Backup configurations
    Get-ChildItem $ProjectRoot -Filter "*.env" | Copy-Item -Destination $backupDir -ErrorAction SilentlyContinue
    Get-ChildItem $ProjectRoot -Filter "*.json" | Copy-Item -Destination $backupDir -ErrorAction SilentlyContinue
    
    Write-Success "Backup created: $backupDir"
}

# Function to restore data
function Restore-Data {
    param([string]$BackupDir)
    
    if (-not $BackupDir -or -not (Test-Path $BackupDir)) {
        Write-Error "Please provide a valid backup directory"
        return
    }
    
    Write-Info "Restoring from $BackupDir..."
    
    # Stop services first
    docker-compose -f $ComposeFile down
    docker-compose -f $ComposeProdFile down
    
    # Restore volumes
    docker run --rm -v biometric-place-backend-data:/target -v "${BackupDir}:/backup" alpine tar xzf /backup/place-backend-data.tar.gz -C /target
    docker run --rm -v biometric-gateway-data:/target -v "${BackupDir}:/backup" alpine tar xzf /backup/gateway-data.tar.gz -C /target
    docker run --rm -v biometric-frontend-data:/target -v "${BackupDir}:/backup" alpine tar xzf /backup/frontend-data.tar.gz -C /target
    
    # Restore configurations
    Get-ChildItem $BackupDir -Filter "*.env" | Copy-Item -Destination $ProjectRoot -ErrorAction SilentlyContinue
    Get-ChildItem $BackupDir -Filter "*.json" | Copy-Item -Destination $ProjectRoot -ErrorAction SilentlyContinue
    
    Write-Success "Data restored from $BackupDir"
}

# Function to run performance tests
function Invoke-PerformanceTest {
    Write-Info "Running performance tests..."
    
    # Check if hey is available
    if (-not (Get-Command hey -ErrorAction SilentlyContinue)) {
        Write-Warning "Installing 'hey' for load testing..."
        Write-Info "Please install 'hey' manually: go install github.com/rakyll/hey@latest"
        return
    }
    
    # Test endpoints
    Write-Info "Testing Place Backend..."
    hey -n 1000 -c 10 http://localhost:8000/health
    
    Write-Info "Testing Unified Gateway..."
    hey -n 1000 -c 10 http://localhost:9000/health
    
    Write-Info "Testing Frontend..."
    hey -n 100 -c 5 http://localhost:8501/healthz
    
    Write-Success "Performance tests completed"
}

# Function to generate status report
function New-StatusReport {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $reportFile = Join-Path $ProjectRoot "logs\system_status_$timestamp.json"
    
    Write-Info "Generating comprehensive status report..."
    
    $logsDir = Split-Path $reportFile
    if (-not (Test-Path $logsDir)) {
        New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
    }
    
    # Get system information
    $dockerVersion = (docker --version).Split(' ')[2].TrimEnd(',')
    $dockerComposeVersion = (docker-compose --version).Split(' ')[2].TrimEnd(',')
    $swarmMode = Test-SwarmMode
    
    # Test service health
    function Test-ServiceHealth {
        param([string]$Url)
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
            return @{
                status = $response.StatusCode
                response_time = "N/A"
            }
        } catch {
            return @{
                status = 0
                response_time = "999s"
            }
        }
    }
    
    $status = @{
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
        version = "3.1.0"
        environment = "docker"
        system = @{
            docker_version = $dockerVersion
            docker_compose_version = $dockerComposeVersion
            swarm_mode = $swarmMode
            host_info = @{
                hostname = $env:COMPUTERNAME
                os = "Windows"
                kernel = (Get-CimInstance Win32_OperatingSystem).Version
                architecture = $env:PROCESSOR_ARCHITECTURE
            }
        }
        services = @{
            place_backend = Test-ServiceHealth "http://localhost:8000/health"
            unified_gateway = Test-ServiceHealth "http://localhost:9000/health"
            frontend = Test-ServiceHealth "http://localhost:8501/healthz"
        }
    }
    
    $status | ConvertTo-Json -Depth 10 | Out-File $reportFile -Encoding UTF8
    
    Write-Success "Status report generated: $reportFile"
}

# Function to show help
function Show-Help {
    Write-Host "BiometricFlow-ZK Enhanced Docker Management Script (PowerShell)"
    Write-Host ""
    Write-Host "Usage: .\deploy-enhanced.ps1 [COMMAND] [ENVIRONMENT] [OPTION]"
    Write-Host ""
    Write-Host "Core Commands:"
    Write-Host "  setup                      Setup environment and generate keys"
    Write-Host "  build [dev|prod]           Build Docker images"
    Write-Host "  start [dev|prod]           Start all services"
    Write-Host "  stop [dev|prod]            Stop all services"
    Write-Host "  restart [dev|prod]         Restart all services"
    Write-Host "  status [dev|prod]          Show service status"
    Write-Host "  health                     Check service health"
    Write-Host "  cleanup                    Clean up Docker resources"
    Write-Host ""
    Write-Host "Enhanced Commands:"
    Write-Host "  build-multiarch            Build multi-architecture images"
    Write-Host "  deploy-monitoring          Deploy monitoring stack"
    Write-Host "  deploy-swarm               Deploy to Docker Swarm"
    Write-Host "  init-swarm                 Initialize Docker Swarm"
    Write-Host "  scale [env] [config]       Scale services"
    Write-Host "  backup                     Backup all data"
    Write-Host "  restore [backup_dir]       Restore from backup"
    Write-Host "  performance-test           Run performance tests"
    Write-Host "  status-report              Generate comprehensive status report"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\deploy-enhanced.ps1 setup"
    Write-Host "  .\deploy-enhanced.ps1 start prod"
    Write-Host "  .\deploy-enhanced.ps1 deploy-monitoring"
    Write-Host "  .\deploy-enhanced.ps1 deploy-swarm"
    Write-Host "  .\deploy-enhanced.ps1 scale dev ""place-backend=3,frontend=2"""
    Write-Host "  .\deploy-enhanced.ps1 backup"
    Write-Host ""
}

# Main script logic
function Main {
    Write-Header
    
    switch ($Command.ToLower()) {
        "build-multiarch" { Build-MultiArchImages }
        "deploy-monitoring" { Deploy-MonitoringStack }
        "deploy-swarm" { Deploy-SwarmStack }
        "init-swarm" { Initialize-Swarm }
        "scale" { Set-ServiceScale -Environment $Environment -ScaleConfig $Option }
        "backup" { Backup-Data }
        "restore" { Restore-Data -BackupDir $Environment }
        "performance-test" { Invoke-PerformanceTest }
        "status-report" { New-StatusReport }
        "help" { Show-Help }
        default {
            # Fallback to basic Docker Compose commands
            Set-Location $ProjectRoot
            
            switch ($Command.ToLower()) {
                "setup" {
                    Write-Info "Setting up environment..."
                    if (Test-Path "generate_keys.py") { python generate_keys.py }
                }
                "build" {
                    Write-Info "Building images for $Environment environment..."
                    if ($Environment -eq "prod") {
                        docker-compose -f $ComposeProdFile build
                    } else {
                        docker-compose -f $ComposeFile build
                    }
                }
                "start" {
                    Write-Info "Starting services in $Environment mode..."
                    if ($Environment -eq "prod") {
                        docker-compose -f $ComposeProdFile up -d
                    } else {
                        docker-compose -f $ComposeFile up -d
                    }
                }
                "stop" {
                    Write-Info "Stopping services..."
                    if ($Environment -eq "prod") {
                        docker-compose -f $ComposeProdFile down
                    } else {
                        docker-compose -f $ComposeFile down
                    }
                }
                "restart" {
                    Write-Info "Restarting services..."
                    if ($Environment -eq "prod") {
                        docker-compose -f $ComposeProdFile restart
                    } else {
                        docker-compose -f $ComposeFile restart
                    }
                }
                "status" {
                    Write-Info "Service status..."
                    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
                }
                "health" {
                    Write-Info "Checking service health..."
                    $services = @("http://localhost:8000/health", "http://localhost:9000/health", "http://localhost:8501/healthz")
                    foreach ($service in $services) {
                        try {
                            $response = Invoke-WebRequest -Uri $service -UseBasicParsing -TimeoutSec 5
                            Write-Success "$service - Status: $($response.StatusCode)"
                        } catch {
                            Write-Error "$service - Status: Failed"
                        }
                    }
                }
                "cleanup" {
                    Write-Info "Cleaning up Docker resources..."
                    docker system prune -f
                    if ($Option -eq "--volumes") {
                        docker volume prune -f
                    }
                }
                default {
                    Write-Error "Unknown command: $Command"
                    Show-Help
                }
            }
        }
    }
}

# Run main function
Main
