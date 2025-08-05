# =================================================================
# BiometricFlow-ZK Multi-Architecture Docker Build
# =================================================================
# Multi-platform build configuration for AMD64 and ARM64

variable "BUILD_DATE" {
  default = formatdate("YYYY-MM-DD'T'hh:mm:ssZ", timestamp())
}

variable "VERSION" {
  default = "3.1.0"
}

variable "VCS_REF" {
  default = "main"
}

group "default" {
  targets = ["place-backend", "unified-gateway", "frontend"]
}

target "place-backend" {
  dockerfile = "Dockerfile.place-backend"
  platforms = ["linux/amd64", "linux/arm64"]
  
  args = {
    BUILD_DATE = BUILD_DATE
    VERSION = VERSION
    VCS_REF = VCS_REF
  }
  
  tags = [
    "biometric-flow/place-backend:latest",
    "biometric-flow/place-backend:${VERSION}"
  ]
  
  labels = {
    "org.opencontainers.image.title" = "BiometricFlow-ZK Place Backend"
    "org.opencontainers.image.description" = "Enterprise fingerprint attendance backend service"
    "org.opencontainers.image.version" = VERSION
    "org.opencontainers.image.created" = BUILD_DATE
    "org.opencontainers.image.revision" = VCS_REF
    "org.opencontainers.image.vendor" = "BiometricFlow-ZK"
    "org.opencontainers.image.source" = "https://github.com/OsamaM0/BiometricFlow-ZK"
    "org.opencontainers.image.licenses" = "MIT"
  }
}

target "unified-gateway" {
  dockerfile = "Dockerfile.unified-gateway"
  platforms = ["linux/amd64", "linux/arm64"]
  
  args = {
    BUILD_DATE = BUILD_DATE
    VERSION = VERSION
    VCS_REF = VCS_REF
  }
  
  tags = [
    "biometric-flow/unified-gateway:latest",
    "biometric-flow/unified-gateway:${VERSION}"
  ]
  
  labels = {
    "org.opencontainers.image.title" = "BiometricFlow-ZK Unified Gateway"
    "org.opencontainers.image.description" = "Enterprise API gateway and aggregation service"
    "org.opencontainers.image.version" = VERSION
    "org.opencontainers.image.created" = BUILD_DATE
    "org.opencontainers.image.revision" = VCS_REF
    "org.opencontainers.image.vendor" = "BiometricFlow-ZK"
    "org.opencontainers.image.source" = "https://github.com/OsamaM0/BiometricFlow-ZK"
    "org.opencontainers.image.licenses" = "MIT"
  }
}

target "frontend" {
  dockerfile = "Dockerfile.frontend"
  platforms = ["linux/amd64", "linux/arm64"]
  
  args = {
    BUILD_DATE = BUILD_DATE
    VERSION = VERSION
    VCS_REF = VCS_REF
  }
  
  tags = [
    "biometric-flow/frontend:latest",
    "biometric-flow/frontend:${VERSION}"
  ]
  
  labels = {
    "org.opencontainers.image.title" = "BiometricFlow-ZK Frontend"
    "org.opencontainers.image.description" = "Enterprise Streamlit dashboard for biometric attendance"
    "org.opencontainers.image.version" = VERSION
    "org.opencontainers.image.created" = BUILD_DATE
    "org.opencontainers.image.revision" = VCS_REF
    "org.opencontainers.image.vendor" = "BiometricFlow-ZK"
    "org.opencontainers.image.source" = "https://github.com/OsamaM0/BiometricFlow-ZK"
    "org.opencontainers.image.licenses" = "MIT"
  }
}
