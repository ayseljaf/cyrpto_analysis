output "environment" {
  value = var.environment
}

output "network_resource_group_name" {
  value = module.network.resource_group_name
}

output "network_vnet_id" {
  value = module.network.vnet_id
}

output "network_subnet_ids" {
  value = module.network.subnet_ids
}
