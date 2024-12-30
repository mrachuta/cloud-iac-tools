variable "resource_prefix" {
  description = "Prefix for all resources"
  type        = string
  default     = "mytest"
}

variable "custom_tags" {
  description = "Custom tags to be added to each resource"
  type        = map(string)
  default = {
    "test" = "true"
  }
}

variable "deployment_region" {
  description = "Region to deploy resources to"
  type        = string
  default     = "East US"
}

variable "whitelisted_ip_ranges" {
  description = "IP ranges allowed to ssh to target vm"
  type        = list(string)
  nullable    = false
}

variable "ssh_public_key_path" {
  description = "Path in your filesystem to your public ssh key to be added to VM"
  type        = string
  nullable    = false
}

