variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "loadtest-poc-rg"
}

variable "location" {
  description = "Azure region for all resources"
  type        = string
  default     = "northeurope"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "poc"
}

variable "vnet_cidr" {
  description = "CIDR block for the virtual network"
  type        = string
  default     = "10.0.0.0/16"
}

variable "subnet_cidrs" {
  description = "CIDR blocks for subnets"
  type = object({
    database = string
    backend  = string
    agw      = string
  })
  default = {
    database = "10.0.1.0/24"
    backend  = "10.0.2.0/24"
    agw      = "10.0.4.0/24"
  }
}

variable "postgres_admin_username" {
  description = "PostgreSQL admin username"
  type        = string
  default     = "psqladmin"
}

variable "postgres_admin_password" {
  description = "PostgreSQL admin password"
  type        = string
  sensitive   = true
}

variable "postgres_sku_name" {
  description = "PostgreSQL SKU name"
  type        = string
  default     = "Standard_D4ds_v5"
}

variable "postgres_storage_mb" {
  description = "PostgreSQL storage size in MB"
  type        = number
  default     = 32768
}

variable "postgres_iops" {
  description = "PostgreSQL IOPS"
  type        = number
  default     = 120
}

variable "backend_container_cpu" {
  description = "Backend container CPU cores"
  type        = number
  default     = 4
}

variable "backend_container_memory" {
  description = "Backend container memory in GB"
  type        = number
  default     = 16
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Environment = "POC"
    Project     = "LoadTesting"
    ManagedBy   = "Terraform"
  }
}

variable "docker_username" {
  description = "Docker Hub username"
  type        = string
  sensitive   = true
}

variable "docker_pat" {
  description = "Docker Hub Personal Access Token (PAT)"
  type        = string
  sensitive   = true
}

variable "docker_registry_server" {
  description = "Docker registry server URL"
  type        = string
  default     = "index.docker.io"
}

variable "backend_image" {
  description = "Docker image for backend application"
  type        = string
  default     = "mvsrinath/sri-fast-api-poc:latest"
}

variable "backend_port" {
  description = "Port on which the backend application runs"
  type        = number
  default     = 8000
}

variable "backend_command" {
  description = "Command to run the backend application"
  type        = list(string)
  default     = ["./app"]
}
