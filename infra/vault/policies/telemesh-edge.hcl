# TeleMesh Edge Node Vault Policy
# Minimal access for edge sensor nodes

# Read access to device credentials
path "secret/data/telemesh/edge/+/credentials" {
  capabilities = ["read"]
}

# Read access to WiFi/LoRa configuration
path "secret/data/telemesh/edge/config" {
  capabilities = ["read"]
}

# Deny access to all other secrets
path "secret/data/telemesh/*" {
  capabilities = ["deny"]
}
