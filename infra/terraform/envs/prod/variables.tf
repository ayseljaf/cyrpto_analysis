variable "location" {
  type        = string
  description = "Azure region"
  default     = "westeurope"
}

variable "environment" {
  type        = string
  description = "Environment name"
  default     = "prod"
}

variable "project_name" {
  type        = string
  description = "Project prefix"
  default     = "crypto-analysis"
}

variable "compute_platform" {
  type        = string
  description = "Primary compute platform: aks or app_service."
  default     = "aks"
}

variable "vnet_cidr" {
  type        = string
  description = "CIDR block for the application VNet."
  default     = "10.20.0.0/16"
}

variable "subnet_cidrs" {
  type = object({
    aks_nodes         = optional(string)
    aks_pods          = optional(string)
    app_service_apps  = optional(string)
    private_endpoints = string
    app_gateway       = string
    bastion           = optional(string)
    management        = optional(string)
  })
  description = "Subnet CIDR allocation by purpose."
  default = {
    aks_nodes         = "10.20.0.0/21"
    aks_pods          = "10.20.8.0/21"
    private_endpoints = "10.20.16.0/24"
    app_gateway       = "10.20.17.0/24"
    bastion           = "10.20.18.0/26"
    management        = "10.20.19.0/24"
  }
}

variable "create_nat_gateway" {
  type        = bool
  description = "Create NAT gateway for controlled egress."
  default     = true
}
