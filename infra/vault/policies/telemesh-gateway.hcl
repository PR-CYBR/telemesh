# TeleMesh Gateway Node Vault Policy
# Allows access to secrets required by gateway nodes

# Read access to collector credentials
path "secret/data/telemesh/collectors/*" {
  capabilities = ["read"]
}

# Read access to MQTT credentials
path "secret/data/telemesh/mqtt/*" {
  capabilities = ["read"]
}

# Read access to Reticulum identity
path "secret/data/telemesh/reticulum/gateway" {
  capabilities = ["read"]
}

# Read access to overlay network credentials
path "secret/data/telemesh/overlay/*" {
  capabilities = ["read"]
}

# Deny access to other secrets
path "secret/data/telemesh/edge/*" {
  capabilities = ["deny"]
}
