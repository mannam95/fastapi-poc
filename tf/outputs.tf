output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.rg.name
}

output "postgres_server_name" {
  description = "Name of the PostgreSQL server"
  value       = azurerm_postgresql_flexible_server.postgres.name
}

output "postgres_server_fqdn" {
  description = "FQDN of the PostgreSQL server"
  value       = azurerm_postgresql_flexible_server.postgres.fqdn
}

output "postgres_connection_string" {
  description = "Connection string for PostgreSQL"
  value       = "postgresql://${var.postgres_admin_username}:${var.postgres_admin_password}@${azurerm_postgresql_flexible_server.postgres.fqdn}:5432/postgres"
  sensitive   = true
}

output "backend_container_ip" {
  description = "Private IP address of the backend container"
  value       = azurerm_container_group.backend.ip_address
}

output "backend_api_url" {
  description = "URL for the backend API"
  value       = "http://${azurerm_public_ip.agw.ip_address}:${var.backend_port}"
}
