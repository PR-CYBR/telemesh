# Specification

## Overview

TeleMesh is a distributed telemetry mesh network providing environmental and infrastructure monitoring through a layered architecture of edge sensors, watcher nodes, and gateway aggregation.

## System Architecture

### Component Overview

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│  Edge Sensor Nodes  │────▶│    Watcher Nodes    │────▶│    Gateway Node     │
│  (ESP32-S3/Heltec)  │     │   (Python Probes)   │     │ (Reticulum Router)  │
│  BME280 + INA219    │     │  Syslog/Traefik/    │     │  Meshtastic→MQTT    │
│  JSON Telemetry     │     │  RTL-SDR/WiFi HaLow │     │  NATS/Influx/Loki   │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
```

### Communication Protocols

- **LoRa**: Edge nodes to mesh network
- **MQTT**: Pub/sub messaging
- **Reticulum**: Encrypted mesh routing
- **Meshtastic**: LoRa mesh network
- **NATS**: Event streaming
- **HTTP/REST**: API interfaces

## Edge Sensor Node (edge-esn-firmware)

### Hardware Requirements

| Component | Model | Purpose |
|-----------|-------|---------|
| MCU | ESP32-S3 | Main processor |
| LoRa Module | Heltec | Mesh communication |
| Temp/Humidity/Pressure | BME280 | Environmental sensing |
| Power Monitor | INA219 | Voltage/current measurement |

### Firmware Specifications

#### Platform
- **Framework**: Arduino
- **Build System**: PlatformIO
- **Target**: ESP32-S3 (Heltec)

#### Telemetry Message Format

```json
{
  "node_id": "esn-001",
  "timestamp": 1701532800,
  "sensors": {
    "bme280": {
      "temperature_c": 22.5,
      "humidity_pct": 45.2,
      "pressure_hpa": 1013.25
    },
    "ina219": {
      "voltage_v": 3.7,
      "current_ma": 125.4,
      "power_mw": 463.98
    }
  }
}
```

#### Probe Event Format

```json
{
  "node_id": "esn-001",
  "event_type": "probe_event",
  "timestamp": 1701532800,
  "probe": "threshold",
  "trigger": "temperature_high",
  "value": 35.2,
  "threshold": 30.0
}
```

### Directory Structure

```
edge-esn-firmware/
├── platformio.ini        # PlatformIO configuration
├── src/
│   ├── main.cpp          # Main application entry
│   ├── sensors.cpp       # Sensor reading logic
│   ├── telemetry.cpp     # JSON message formatting
│   └── communication.cpp # LoRa/WiFi transmission
├── include/
│   ├── config.h          # Configuration constants
│   ├── sensors.h         # Sensor interface
│   └── telemetry.h       # Message structures
├── lib/                  # Local libraries
└── test/                 # Unit tests
```

## Watcher Node (watcher-node)

### Probe Types

| Probe | Source | Events |
|-------|--------|--------|
| Syslog | /var/log/syslog | Log pattern matches |
| Traefik | Traefik API/logs | HTTP traffic events |
| RTL-SDR | RTL-SDR dongle | RF signal detection |
| WiFi HaLow | 802.11ah interface | Connection events |

### Python Package Specifications

#### Dependencies

- `paho-mqtt>=2.0` - MQTT client
- `rns>=0.7` - Reticulum Network Stack
- `pyrtlsdr>=0.3` - RTL-SDR interface
- `watchdog>=4.0` - File system monitoring

#### Module Structure

```
watcher-node/
├── pyproject.toml
├── src/
│   ├── watcher_node/
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── config.py
│   │   ├── probes/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── syslog.py
│   │   │   ├── traefik.py
│   │   │   ├── rtlsdr.py
│   │   │   └── wifi_halow.py
│   │   └── publishers/
│   │       ├── __init__.py
│   │       ├── base.py
│   │       ├── mqtt.py
│   │       └── reticulum.py
└── tests/
    ├── test_probes.py
    └── test_publishers.py
```

### Event Message Format

```json
{
  "source": "watcher-001",
  "probe": "syslog",
  "timestamp": 1701532800,
  "event": {
    "pattern": "ssh_login",
    "message": "Accepted publickey for user from 192.168.1.100",
    "severity": "info"
  }
}
```

## Gateway Node (gateway-node)

### Components

| Component | Function |
|-----------|----------|
| Reticulum Router | Mesh network routing |
| Meshtastic Bridge | Meshtastic to MQTT protocol conversion |
| NATS Collector | Event stream ingestion |
| InfluxDB Collector | Time-series metrics storage |
| Loki Collector | Log aggregation |

### Python Package Specifications

#### Dependencies

- `rns>=0.7` - Reticulum Network Stack
- `meshtastic>=2.0` - Meshtastic interface
- `paho-mqtt>=2.0` - MQTT client
- `nats-py>=2.0` - NATS client
- `influxdb-client>=1.40` - InfluxDB client
- `httpx>=0.25` - HTTP client (for Loki)

#### Module Structure

```
gateway-node/
├── pyproject.toml
├── src/
│   ├── gateway_node/
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── config.py
│   │   ├── router/
│   │   │   ├── __init__.py
│   │   │   └── reticulum.py
│   │   ├── bridges/
│   │   │   ├── __init__.py
│   │   │   └── meshtastic_mqtt.py
│   │   └── collectors/
│   │       ├── __init__.py
│   │       ├── base.py
│   │       ├── nats.py
│   │       ├── influxdb.py
│   │       └── loki.py
└── tests/
    ├── test_router.py
    ├── test_bridges.py
    └── test_collectors.py
```

## Infrastructure

### Kubernetes

- Namespace: `telemesh`
- Deployments: gateway-node, watcher-node replicas
- Services: ClusterIP for internal, LoadBalancer for external
- ConfigMaps: Application configuration
- Secrets: Credentials and certificates

### Helm Chart

```
infra/helm/telemesh/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   └── secret.yaml
```

### Ansible

```
infra/ansible/
├── playbooks/
│   ├── edge-node.yml      # Edge sensor provisioning
│   ├── watcher-node.yml   # Watcher node setup
│   └── gateway-node.yml   # Gateway node setup
├── roles/
│   ├── common/            # Base system configuration
│   ├── reticulum/         # Reticulum installation
│   └── monitoring/        # Prometheus/Grafana
```

### Terraform

```
infra/terraform/
├── main.tf
├── variables.tf
├── outputs.tf
├── modules/
│   ├── networking/        # VPC, subnets
│   ├── compute/           # EC2/VMs
│   └── overlay/           # Tailscale/ZeroTier
```

### Vault

- Secret engines: KV v2 for credentials
- Policies: Per-component access control
- Auth methods: Kubernetes, AppRole

### Overlay Networking

- **Tailscale**: Primary overlay for secure mesh
- **ZeroTier**: Alternative for self-hosted deployments

## Non-Functional Requirements

### Performance
- Edge nodes: <1s telemetry interval capability
- Watcher nodes: <100ms event detection latency
- Gateway: Handle 1000+ msgs/sec throughput

### Reliability
- Mesh networking tolerates node failures
- Data buffering during connectivity loss
- Automatic reconnection and retry logic

### Security
- All communications encrypted (TLS/RNSL)
- Mutual TLS for service-to-service
- Secrets never in code or config files

### Observability
- Structured logging (JSON)
- Prometheus metrics exposure
- Distributed tracing support
