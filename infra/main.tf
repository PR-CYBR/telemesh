# TeleMesh Infrastructure Configuration
# This file contains the core infrastructure setup for TeleMesh deployment

# Terraform backend configuration
# Uncomment and configure when ready to use remote state
# terraform {
#   backend "remote" {
#     organization = "PR-CYBR"
#     workspaces {
#       name = "telemesh-${var.environment}"
#     }
#   }
# }

# TeleMesh Agent Configuration
resource "null_resource" "agent_config" {
  triggers = {
    agent_id    = var.agent_id
    agent_role  = var.agent_role
    environment = var.environment
  }

  provisioner "local-exec" {
    command = "echo 'TeleMesh Agent ${var.agent_id} configured for ${var.environment} environment'"
  }
}

# Networking module for overlay networks
module "networking" {
  source = "./terraform/modules/networking"

  environment = var.environment
  vpc_cidr    = var.vpc_cidr
  enable_ipv6 = var.enable_ipv6
}

# Overlay network module (Tailscale/ZeroTier)
module "overlay" {
  source = "./terraform/modules/overlay"

  environment       = var.environment
  tailscale_enabled = var.tailscale_enabled
  tailscale_authkey = var.tailscale_authkey
  zerotier_enabled  = var.zerotier_enabled
  zerotier_network  = var.zerotier_network
}
