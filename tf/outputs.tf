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

output "fastapi_container_ip" {
  description = "Private IP address of the FastAPI container"
  value       = azurerm_container_group.fastapi.ip_address
}

output "locust_container_ip" {
  description = "Private IP address of the Locust container"
  value       = azurerm_container_group.locust.ip_address
}

output "locust_web_interface" {
  description = "URL for the Locust web interface"
  value       = "http://${azurerm_public_ip.agw.ip_address}:8089"
}
