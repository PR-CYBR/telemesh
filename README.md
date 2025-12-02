# TeleMesh - PR-CYBR Telemetry Mesh Network

[![Spec-Kit Validation](https://github.com/PR-CYBR/telemesh/actions/workflows/spec-kit.yml/badge.svg?branch=main)](https://github.com/PR-CYBR/telemesh/actions/workflows/spec-kit.yml)

**Branch Purpose:** The `main` branch is the stable baseline representing production-ready code. All changes integrated through the CI/CD pipeline eventually land here.

## Overview

TeleMesh is a distributed telemetry mesh network designed for environmental and infrastructure monitoring. It provides a complete stack from edge sensor nodes through gateway aggregation to cloud-based data processing and visualization.

## Architecture

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│  Edge Sensor Nodes  │────▶│    Watcher Nodes    │────▶│    Gateway Node     │
│  (ESP32-S3/Heltec)  │     │   (Python Probes)   │     │ (Reticulum Router)  │
│  BME280 + INA219    │     │  Syslog/Traefik/    │     │  Meshtastic→MQTT    │
│  JSON Telemetry     │     │  RTL-SDR/WiFi HaLow │     │  NATS/Influx/Loki   │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
                                      │                           │
                                      ▼                           ▼
                            ┌─────────────────────┐     ┌─────────────────────┐
                            │  MQTT / Reticulum   │     │  Infrastructure     │
                            │    Message Bus      │     │  K8s/Helm/Ansible   │
                            └─────────────────────┘     └─────────────────────┘
```

## Repository Structure

```
telemesh/
├── edge-esn-firmware/    # ESP32-S3/Heltec Arduino firmware
│   ├── src/              # Main firmware source
│   ├── lib/              # Local libraries
│   ├── include/          # Header files
│   └── test/             # Unit tests
├── watcher-node/         # Python probe detectors
│   ├── src/probes/       # Syslog/Traefik/RTL-SDR/WiFi probes
│   ├── src/publishers/   # MQTT/Reticulum publishers
│   └── tests/            # Test suite
├── gateway-node/         # Reticulum router and bridge
│   ├── src/collectors/   # Telemetry collectors
│   ├── src/bridges/      # Protocol bridges
│   ├── src/router/       # Reticulum router
│   └── tests/            # Test suite
├── infra/                # Infrastructure as Code
│   ├── kubernetes/       # K8s manifests
│   ├── helm/             # Helm charts
│   ├── ansible/          # Ansible playbooks
│   ├── terraform/        # Terraform modules
│   └── vault/            # Vault policies
├── docs/                 # Documentation
│   ├── architecture/     # System design
│   ├── setup/            # Installation guides
│   └── api/              # API references
└── .specify/             # Spec-Kit specifications
```

## Components

### Edge Sensor Node (edge-esn-firmware)

ESP32-S3/Heltec-based environmental sensor nodes:

- **Hardware**: ESP32-S3, Heltec LoRa modules
- **Sensors**: BME280 (temp/humidity/pressure), INA219 (power monitoring)
- **Communication**: JSON telemetry over LoRa, WiFi, or serial
- **Events**: probe_event for sensor state changes
- **Platform**: Arduino/PlatformIO

### Watcher Node (watcher-node)

Python-based digital and RF probe detectors:

- **Syslog Probe**: Monitor system logs for events
- **Traefik Probe**: HTTP/HTTPS traffic monitoring
- **RTL-SDR Probe**: Software-defined radio signal detection
- **WiFi HaLow Probe**: 802.11ah long-range WiFi monitoring
- **Publishing**: MQTT and Reticulum network integration

### Gateway Node (gateway-node)

Central aggregation and routing:

- **Reticulum Router**: Mesh network routing
- **Meshtastic Bridge**: Meshtastic to MQTT protocol bridge
- **Collectors**: Telemetry ingestion for NATS, InfluxDB, Loki
- **Data Pipeline**: Event correlation and forwarding

### Infrastructure (infra)

Complete deployment automation:

- **Kubernetes**: Container orchestration manifests
- **Helm**: Packaged deployments
- **Ansible**: Node provisioning playbooks
- **Terraform**: Cloud infrastructure
- **Vault**: Secrets management
- **Overlay Networks**: Tailscale/ZeroTier integration

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/PR-CYBR/telemesh.git
cd telemesh
```

### 2. Edge Sensor Node Setup

```bash
cd edge-esn-firmware
# Install PlatformIO
pip install platformio
# Build and upload
pio run -t upload
```

### 3. Watcher Node Setup

```bash
cd watcher-node
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m watcher_node
```

### 4. Gateway Node Setup

```bash
cd gateway-node
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m gateway_node
```

### 5. Infrastructure Deployment

```bash
cd infra/terraform
terraform init
terraform plan
terraform apply
```

## Specifications

This project follows the Spec-Kit specification-driven development framework:

- **Constitution**: [.specify/constitution.md](.specify/constitution.md) - Project principles
- **Specifications**: [.specify/spec.md](.specify/spec.md) - Technical requirements
- **Implementation Plan**: [.specify/plan.md](.specify/plan.md) - Development roadmap
- **Tasks**: [.specify/tasks/](.specify/tasks/) - Actionable work items

## Branching Strategy

See [BRANCHING.md](BRANCHING.md) for the complete branching workflow supporting specification-driven development.

## License

This project is released under the [MIT License](LICENSE).
