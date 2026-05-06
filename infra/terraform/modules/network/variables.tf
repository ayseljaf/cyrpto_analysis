variable "location" {
  type = string
}

variable "environment" {
  type = string
}

variable "project" {
  type = string
}

variable "vnet_cidr" {
  type        = string
  description = "CIDR block for the workload VNet."
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
}

variable "compute_platform" {
  type        = string
  description = "Primary compute platform: aks or app_service."
  validation {
    condition     = contains(["aks", "app_service"], var.compute_platform)
    error_message = "compute_platform must be either 'aks' or 'app_service'."
  }
}

variable "create_nat_gateway" {
  type        = bool
  description = "Create NAT gateway for controlled egress."
  default     = true
}
