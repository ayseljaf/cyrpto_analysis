locals {
  name_prefix   = replace(lower("${var.project}-${var.environment}"), "_", "-")
  use_aks       = var.compute_platform == "aks"
  use_appsvc    = var.compute_platform == "app_service"
  resource_tags = {
    project     = var.project
    environment = var.environment
    managed_by  = "terraform"
    component   = "network"
  }

  subnet_definitions = merge(
    {
      private_endpoints = var.subnet_cidrs.private_endpoints
      app_gateway       = var.subnet_cidrs.app_gateway
    },
    local.use_aks ? {
      aks_nodes = var.subnet_cidrs.aks_nodes
      aks_pods  = var.subnet_cidrs.aks_pods
    } : {},
    local.use_appsvc ? {
      app_service_apps = var.subnet_cidrs.app_service_apps
    } : {},
    var.subnet_cidrs.bastion != null ? {
      bastion = var.subnet_cidrs.bastion
    } : {},
    var.subnet_cidrs.management != null ? {
      management = var.subnet_cidrs.management
    } : {}
  )

  private_dns_zones = toset([
    "privatelink.postgres.database.azure.com",
    "privatelink.servicebus.windows.net",
    "privatelink.vaultcore.azure.net",
    "privatelink.azurecr.io",
  ])
}

resource "azurerm_resource_group" "network" {
  name     = "rg-${local.name_prefix}-network"
  location = var.location
  tags     = local.resource_tags
}

resource "azurerm_virtual_network" "this" {
  name                = "vnet-${local.name_prefix}"
  location            = azurerm_resource_group.network.location
  resource_group_name = azurerm_resource_group.network.name
  address_space       = [var.vnet_cidr]
  tags                = local.resource_tags
}

resource "azurerm_network_security_group" "subnet" {
  for_each            = local.subnet_definitions
  name                = "nsg-${local.name_prefix}-${replace(each.key, "_", "-")}"
  location            = azurerm_resource_group.network.location
  resource_group_name = azurerm_resource_group.network.name
  tags                = local.resource_tags
}

resource "azurerm_subnet" "this" {
  for_each             = local.subnet_definitions
  name                 = "snet-${local.name_prefix}-${replace(each.key, "_", "-")}"
  resource_group_name  = azurerm_resource_group.network.name
  virtual_network_name = azurerm_virtual_network.this.name
  address_prefixes     = [each.value]

  dynamic "delegation" {
    for_each = each.key == "app_service_apps" ? [1] : []
    content {
      name = "appsvc-delegation"
      service_delegation {
        name = "Microsoft.Web/serverFarms"
      }
    }
  }
}

resource "azurerm_subnet_network_security_group_association" "this" {
  for_each                  = local.subnet_definitions
  subnet_id                 = azurerm_subnet.this[each.key].id
  network_security_group_id = azurerm_network_security_group.subnet[each.key].id
}

resource "azurerm_public_ip" "nat" {
  count               = var.create_nat_gateway ? 1 : 0
  name                = "pip-${local.name_prefix}-nat"
  location            = azurerm_resource_group.network.location
  resource_group_name = azurerm_resource_group.network.name
  allocation_method   = "Static"
  sku                 = "Standard"
  tags                = local.resource_tags
}

resource "azurerm_nat_gateway" "this" {
  count                   = var.create_nat_gateway ? 1 : 0
  name                    = "nat-${local.name_prefix}"
  location                = azurerm_resource_group.network.location
  resource_group_name     = azurerm_resource_group.network.name
  sku_name                = "Standard"
  idle_timeout_in_minutes = 10
  tags                    = local.resource_tags
}

resource "azurerm_nat_gateway_public_ip_association" "this" {
  count                = var.create_nat_gateway ? 1 : 0
  nat_gateway_id       = azurerm_nat_gateway.this[0].id
  public_ip_address_id = azurerm_public_ip.nat[0].id
}

resource "azurerm_subnet_nat_gateway_association" "egress" {
  for_each = var.create_nat_gateway ? {
    for k, v in local.subnet_definitions : k => v
    if k != "private_endpoints" && k != "bastion"
  } : {}

  subnet_id      = azurerm_subnet.this[each.key].id
  nat_gateway_id = azurerm_nat_gateway.this[0].id
}

resource "azurerm_private_dns_zone" "this" {
  for_each            = local.private_dns_zones
  name                = each.value
  resource_group_name = azurerm_resource_group.network.name
  tags                = local.resource_tags
}

resource "azurerm_private_dns_zone_virtual_network_link" "this" {
  for_each              = local.private_dns_zones
  name                  = "link-${local.name_prefix}-${replace(each.value, ".", "-")}"
  resource_group_name   = azurerm_resource_group.network.name
  private_dns_zone_name = azurerm_private_dns_zone.this[each.value].name
  virtual_network_id    = azurerm_virtual_network.this.id
  registration_enabled  = false
  tags                  = local.resource_tags
}
