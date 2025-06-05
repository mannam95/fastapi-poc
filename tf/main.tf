terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# Resource Group
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

# Virtual Network
resource "azurerm_virtual_network" "vnet" {
  name                = "loadtest-poc-vnet"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  address_space       = [var.vnet_cidr]
  tags                = var.tags
}

# Subnets
resource "azurerm_subnet" "database" {
  name                 = "database-subnet"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = [var.subnet_cidrs.database]
  service_endpoints    = ["Microsoft.Storage"]

  delegation {
    name = "fs"
    service_delegation {
      name = "Microsoft.DBforPostgreSQL/flexibleServers"
      actions = [
        "Microsoft.Network/virtualNetworks/subnets/join/action",
      ]
    }
  }
}

resource "azurerm_subnet" "backend" {
  name                 = "backend-subnet"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = [var.subnet_cidrs.backend]
  service_endpoints    = ["Microsoft.Storage"]

  delegation {
    name = "aci"
    service_delegation {
      name = "Microsoft.ContainerInstance/containerGroups"
      actions = [
        "Microsoft.Network/virtualNetworks/subnets/action"
      ]
    }
  }
}

# Subnet for Application Gateway
resource "azurerm_subnet" "agw" {
  name                 = "agw-subnet"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = [var.subnet_cidrs.agw]
}

# Network Security Groups
resource "azurerm_network_security_group" "database" {
  name                = "loadtest-poc-db-nsg"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  security_rule {
    name                       = "allow-postgres"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "5432"
    source_address_prefix      = var.subnet_cidrs.backend
    destination_address_prefix = "*"
  }
  tags = var.tags
}

resource "azurerm_network_security_group" "backend" {
  name                = "loadtest-poc-backend-nsg"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  security_rule {
    name                       = "allow-http-backend"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = var.backend_port
    source_address_prefix      = var.subnet_cidrs.agw
    destination_address_prefix = "*"
  }

  tags = var.tags
}

resource "azurerm_network_security_group" "agw" {
  name                = "loadtest-poc-agw-nsg"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  # Allow inbound traffic on backend port
  security_rule {
    name                       = "allow-backend-port"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = var.backend_port
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  # Required for Application Gateway management traffic
  security_rule {
    name                       = "allow-agw-management"
    priority                   = 200
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "65200-65535"
    source_address_prefix      = "GatewayManager"
    destination_address_prefix = "*"
  }

  # Allow all outbound (AGW needs to reach backend)
  security_rule {
    name                       = "allow-all-outbound"
    priority                   = 100
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  tags = var.tags
}

# NSG Associations
resource "azurerm_subnet_network_security_group_association" "database" {
  subnet_id                 = azurerm_subnet.database.id
  network_security_group_id = azurerm_network_security_group.database.id
}

resource "azurerm_subnet_network_security_group_association" "backend" {
  subnet_id                 = azurerm_subnet.backend.id
  network_security_group_id = azurerm_network_security_group.backend.id
}

resource "azurerm_subnet_network_security_group_association" "agw" {
  subnet_id                 = azurerm_subnet.agw.id
  network_security_group_id = azurerm_network_security_group.agw.id
}

# Private DNS Zone for PostgreSQL
resource "azurerm_private_dns_zone" "postgres" {
  name                = "loadtest-poc.postgres.database.azure.com"
  resource_group_name = azurerm_resource_group.rg.name
  tags                = var.tags
}

resource "azurerm_private_dns_zone_virtual_network_link" "postgres" {
  name                  = "loadtest-poc-postgres-link"
  resource_group_name   = azurerm_resource_group.rg.name
  private_dns_zone_name = azurerm_private_dns_zone.postgres.name
  virtual_network_id    = azurerm_virtual_network.vnet.id
  tags                  = var.tags
}

# PostgreSQL Flexible Server
resource "azurerm_postgresql_flexible_server" "postgres" {
  name                          = "loadtest-poc-postgres"
  resource_group_name           = azurerm_resource_group.rg.name
  location                      = azurerm_resource_group.rg.location
  version                       = "14"
  administrator_login           = var.postgres_admin_username
  administrator_password        = var.postgres_admin_password
  zone                          = "1"
  storage_mb                    = var.postgres_storage_mb
  sku_name                      = var.postgres_sku_name
  public_network_access_enabled = false

  private_dns_zone_id = azurerm_private_dns_zone.postgres.id
  delegated_subnet_id = azurerm_subnet.database.id

  tags = var.tags
}

# Add firewall rule to allow connections from backend subnet
resource "azurerm_postgresql_flexible_server_firewall_rule" "backend" {
  name             = "allow-backend-subnet"
  server_id        = azurerm_postgresql_flexible_server.postgres.id
  start_ip_address = cidrhost(var.subnet_cidrs.backend, 0)
  end_ip_address   = cidrhost(var.subnet_cidrs.backend, -1)
}

# Create go_rest_api database
resource "azurerm_postgresql_flexible_server_database" "go_rest_api" {
  name      = "go_rest_api"
  server_id = azurerm_postgresql_flexible_server.postgres.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

# Backend Container Instance
resource "azurerm_container_group" "backend" {
  name                = "loadtest-poc-backend"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  ip_address_type     = "Private"
  os_type             = "Linux"
  subnet_ids          = [azurerm_subnet.backend.id]

  image_registry_credential {
    username = var.docker_username
    password = var.docker_pat
    server   = "index.docker.io"
  }

  container {
    name     = "loadtest-poc-backend"
    image    = var.backend_image
    cpu      = var.backend_container_cpu
    memory   = var.backend_container_memory
    commands = var.backend_command

    ports {
      port     = var.backend_port
      protocol = "TCP"
    }

    ports {
      port     = 8080
      protocol = "TCP"
    }

    environment_variables = {
      # FASTAPI-POC
      POSTGRES_SERVER   = "${azurerm_postgresql_flexible_server.postgres.name}.postgres.database.azure.com"
      POSTGRES_USER     = var.postgres_admin_username
      POSTGRES_PASSWORD = var.postgres_admin_password
      POSTGRES_DB       = "sri_fastapi_poc"
      POSTGRES_PORT     = 5432
      ENV               = "development"
      WORKERS           = 4

      # GO-POC
      DB_HOST     = "${azurerm_postgresql_flexible_server.postgres.name}.postgres.database.azure.com"
      DB_PORT     = 5432
      DB_USER     = var.postgres_admin_username
      DB_PASSWORD = var.postgres_admin_password
      DB_NAME     = "go_rest_api"
      DB_SSLMODE  = "require"
    }
  }

  tags = var.tags
}

# Public IP for Application Gateway
resource "azurerm_public_ip" "agw" {
  name                = "loadtest-poc-agw-pip"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  allocation_method   = "Static"
  sku                 = "Standard"
  tags                = var.tags
}

# Application Gateway
resource "azurerm_application_gateway" "agw" {
  name                = "loadtest-poc-agw"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  sku {
    name     = "Standard_v2"
    tier     = "Standard_v2"
    capacity = 1
  }

  gateway_ip_configuration {
    name      = "gateway-ip-config"
    subnet_id = azurerm_subnet.agw.id
  }

  frontend_port {
    name = "backend-port"
    port = var.backend_port
  }

  frontend_ip_configuration {
    name                 = "frontend-ip-config"
    public_ip_address_id = azurerm_public_ip.agw.id
  }

  backend_address_pool {
    name         = "backend-pool"
    ip_addresses = [azurerm_container_group.backend.ip_address]
  }

  backend_http_settings {
    name                  = "backend-http-settings"
    cookie_based_affinity = "Disabled"
    port                  = var.backend_port
    protocol              = "Http"
    request_timeout       = 60
    probe_name            = "backend-health-probe"
  }

  probe {
    name                = "backend-health-probe"
    protocol            = "Http"
    host                = "localhost"
    path                = "/health"
    interval            = 30
    timeout             = 30
    unhealthy_threshold = 3
    match {
      status_code = ["200-399"]
    }
  }

  http_listener {
    name                           = "backend-listener"
    frontend_ip_configuration_name = "frontend-ip-config"
    frontend_port_name             = "backend-port"
    protocol                       = "Http"
  }

  request_routing_rule {
    name                       = "backend-routing-rule"
    rule_type                  = "Basic"
    http_listener_name         = "backend-listener"
    backend_address_pool_name  = "backend-pool"
    backend_http_settings_name = "backend-http-settings"
    priority                   = 1
  }

  tags = var.tags
}
