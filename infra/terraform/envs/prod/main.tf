module "network" {
  source      = "../../modules/network"
  location    = var.location
  environment = var.environment
  project     = var.project_name
  compute_platform  = var.compute_platform
  vnet_cidr         = var.vnet_cidr
  subnet_cidrs      = var.subnet_cidrs
  create_nat_gateway = var.create_nat_gateway
}

module "acr" {
  source      = "../../modules/acr"
  location    = var.location
  environment = var.environment
  project     = var.project_name
}

module "aks" {
  source      = "../../modules/aks"
  location    = var.location
  environment = var.environment
  project     = var.project_name
}

module "postgres" {
  source      = "../../modules/postgres"
  location    = var.location
  environment = var.environment
  project     = var.project_name
}

module "kafka" {
  source      = "../../modules/kafka"
  location    = var.location
  environment = var.environment
  project     = var.project_name
}

module "keyvault" {
  source      = "../../modules/keyvault"
  location    = var.location
  environment = var.environment
  project     = var.project_name
}

module "monitoring" {
  source      = "../../modules/monitoring"
  location    = var.location
  environment = var.environment
  project     = var.project_name
}
