# Constitution

## Purpose

TeleMesh is a distributed telemetry mesh network for environmental and infrastructure monitoring. This project provides a complete stack from edge sensor nodes through gateway aggregation to cloud-based data processing and visualization.

## Principles

1. **Specification-Driven Development**
All development begins with clear specifications. Code implements specifications, not vice versa.

2. **Modular Architecture**
Components are designed as independent, loosely-coupled modules that communicate through well-defined interfaces. Each component (edge-esn-firmware, watcher-node, gateway-node) can be developed, tested, and deployed independently.

3. **Resilient Mesh Networking**
The system must operate in degraded conditions. Mesh networking via Reticulum and Meshtastic ensures connectivity even when individual nodes fail or network paths are disrupted.

4. **Security by Design**
All communications are encrypted. Secrets are managed through Vault. Authentication and authorization are enforced at every layer.

5. **Infrastructure as Code**
All infrastructure is defined declaratively using Terraform, Kubernetes, Helm, and Ansible. No manual configuration of production systems.

6. **Observable Systems**
Comprehensive telemetry collection, logging, and monitoring are built into every component. Data flows to InfluxDB for metrics, Loki for logs, and NATS for event streaming.

7. **Documentation as Code**
Documentation lives alongside code, versioned and reviewed through the same processes.

## Structure

```
/telemesh
├── edge-esn-firmware/    # ESP32-S3/Heltec Arduino firmware
├── watcher-node/         # Python probe detectors
├── gateway-node/         # Reticulum router and bridge
├── infra/                # Infrastructure as Code
├── docs/                 # Documentation
└── .specify/             # Spec-Kit specifications
```

## Component Responsibilities

### Edge Sensor Node (edge-esn-firmware)
- Collect environmental data from BME280 and INA219 sensors
- Transmit JSON telemetry and probe_event messages
- Operate on low power with LoRa communication

### Watcher Node (watcher-node)
- Monitor digital and RF signals (syslog, Traefik, RTL-SDR, WiFi HaLow)
- Publish events to MQTT and Reticulum networks
- Provide configurable probe detection logic

### Gateway Node (gateway-node)
- Route mesh network traffic via Reticulum
- Bridge Meshtastic networks to MQTT
- Collect and forward telemetry to NATS, InfluxDB, Loki

### Infrastructure (infra)
- Kubernetes manifests for container orchestration
- Helm charts for packaged deployments
- Ansible playbooks for node provisioning
- Terraform modules for cloud resources
- Vault policies for secrets management
- Overlay networking via Tailscale/ZeroTier

## Governance

Changes to the constitution require explicit review and approval. The constitution serves as the foundational agreement for how the project operates.

## Branching Strategy

This repository implements a comprehensive branching scheme to support specification-driven development. See [BRANCHING.md](../BRANCHING.md) for complete documentation.
