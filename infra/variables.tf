# TeleMesh Infrastructure Variables

variable "agent_id" {
  description = "Unique identifier for the PR-CYBR agent"
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.agent_id))
    error_message = "Agent ID must contain only lowercase letters, numbers, and hyphens."
  }
}

variable "agent_role" {
  description = "Role of the TeleMesh agent (gateway, watcher, edge)"
  type        = string
  default     = "gateway"

  validation {
    condition     = contains(["gateway", "watcher", "edge", "controller"], var.agent_role)
    error_message = "Agent role must be one of: gateway, watcher, edge, controller."
  }
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "dockerhub_user" {
  description = "DockerHub username for container registry access"
  type        = string
  sensitive   = true
  default     = ""
}

variable "notion_page_id" {
  description = "Notion page ID for agent documentation"
  type        = string
  default     = ""
}

# Networking variables
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "enable_ipv6" {
  description = "Enable IPv6 support"
  type        = bool
  default     = false
}

# Overlay network variables
variable "tailscale_enabled" {
  description = "Enable Tailscale overlay network"
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
  description = "Enable ZeroTier overlay network"
  type        = bool
  default     = false
}

variable "zerotier_network" {
  description = "ZeroTier network ID"
  type        = string
  default     = ""
}
