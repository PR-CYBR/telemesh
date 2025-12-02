# TeleMesh Watcher Node Vault Policy
# Allows access to secrets required by watcher nodes

# Read access to MQTT credentials
path "secret/data/telemesh/mqtt/*" {
  capabilities = ["read"]
}

# Read access to Reticulum identity
path "secret/data/telemesh/reticulum/watcher" {
  capabilities = ["read"]
}

# Read access to probe credentials
path "secret/data/telemesh/probes/*" {
  capabilities = ["read"]
}

# Deny access to collector secrets
path "secret/data/telemesh/collectors/*" {
  capabilities = ["deny"]
}
