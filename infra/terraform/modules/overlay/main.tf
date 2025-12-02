# TeleMesh Overlay Network Module
# Manages Tailscale and ZeroTier overlay networks

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "tailscale_enabled" {
  description = "Enable Tailscale overlay"
  type        = bool
  default     = false
}

variable "tailscale_authkey" {
  description = "Tailscale authentication key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "zerotier_enabled" {
  description = "Enable ZeroTier overlay"
  type        = bool
  default     = false
}

variable "zerotier_network" {
  description = "ZeroTier network ID"
  type        = string
  default     = ""
}

# Tailscale configuration
resource "null_resource" "tailscale" {
  count = var.tailscale_enabled ? 1 : 0

  triggers = {
    environment = var.environment
  }

  provisioner "local-exec" {
    command = "echo 'Tailscale overlay configured for ${var.environment}'"
  }
}

# ZeroTier configuration
resource "null_resource" "zerotier" {
  count = var.zerotier_enabled ? 1 : 0

  triggers = {
    environment = var.environment
    network_id  = var.zerotier_network
  }

  provisioner "local-exec" {
    command = "echo 'ZeroTier overlay configured for ${var.environment} (network: ${var.zerotier_network})'"
  }
}

output "overlay_type" {
  description = "Active overlay network type"
  value       = var.tailscale_enabled ? "tailscale" : (var.zerotier_enabled ? "zerotier" : "none")
}
