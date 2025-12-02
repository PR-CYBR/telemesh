# TeleMesh Architecture Overview

## System Design

TeleMesh implements a three-tier telemetry mesh network architecture:

1. **Edge Layer**: Sensor nodes collecting environmental data
2. **Watcher Layer**: Probe detectors monitoring digital and RF signals
3. **Gateway Layer**: Aggregation, routing, and data forwarding

## Component Diagram

```
                                   ┌─────────────────┐
                                   │   Cloud/Data    │
                                   │   Center        │
                                   │                 │
                                   │  ┌───────────┐  │
                                   │  │ InfluxDB  │  │
                                   │  │ Loki      │  │
                                   │  │ NATS      │  │
                                   │  └───────────┘  │
                                   └────────┬────────┘
                                            │
                                   ┌────────▼────────┐
                                   │  Gateway Node   │
                                   │                 │
                                   │  ┌───────────┐  │
                                   │  │Reticulum  │  │
                                   │  │Router     │  │
                                   │  ├───────────┤  │
                                   │  │Meshtastic │  │
                                   │  │Bridge     │  │
                                   │  ├───────────┤  │
                                   │  │Telemetry  │  │
                                   │  │Collectors │  │
                                   │  └───────────┘  │
                                   └────────┬────────┘
                                            │
                    ┌───────────────────────┼───────────────────────┐
                    │                       │                       │
           ┌────────▼────────┐     ┌────────▼────────┐     ┌────────▼────────┐
           │  Watcher Node   │     │  Watcher Node   │     │  Watcher Node   │
           │                 │     │                 │     │                 │
           │  ┌───────────┐  │     │  ┌───────────┐  │     │  ┌───────────┐  │
           │  │Syslog     │  │     │  │Traefik    │  │     │  │RTL-SDR    │  │
           │  │Probe      │  │     │  │Probe      │  │     │  │Probe      │  │
           │  └───────────┘  │     │  └───────────┘  │     │  └───────────┘  │
           └────────┬────────┘     └────────┬────────┘     └────────┬────────┘
                    │                       │                       │
                    └───────────────────────┼───────────────────────┘
                                            │
                                   ┌────────▼────────┐
                                   │   Mesh Network  │
                                   │  (Reticulum/    │
                                   │   Meshtastic)   │
                                   └────────┬────────┘
                                            │
                    ┌───────────────────────┼───────────────────────┐
                    │                       │                       │
           ┌────────▼────────┐     ┌────────▼────────┐     ┌────────▼────────┐
           │  Edge Node      │     │  Edge Node      │     │  Edge Node      │
           │  (ESP32-S3)     │     │  (Heltec)       │     │  (ESP32-S3)     │
           │                 │     │                 │     │                 │
           │  ┌───────────┐  │     │  ┌───────────┐  │     │  ┌───────────┐  │
           │  │BME280     │  │     │  │BME280     │  │     │  │BME280     │  │
           │  │INA219     │  │     │  │INA219     │  │     │  │INA219     │  │
           │  └───────────┘  │     │  └───────────┘  │     │  └───────────┘  │
           └─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Data Flow

1. **Edge Nodes** collect sensor readings and transmit JSON telemetry
2. **Watcher Nodes** detect events and publish to MQTT/Reticulum
3. **Gateway Node** aggregates data and forwards to backend systems
4. **Backend** stores data in InfluxDB, Loki, and NATS

## Communication Protocols

| Layer | Protocol | Purpose |
|-------|----------|---------|
| Edge ↔ Mesh | LoRa | Low-power, long-range |
| Watcher ↔ Gateway | MQTT, Reticulum | Event distribution |
| Gateway ↔ Backend | NATS, HTTP | Data ingestion |
| All | Tailscale/ZeroTier | Secure overlay |

## Security Model

- All communications encrypted (TLS, RNSL)
- Secrets managed in HashiCorp Vault
- Node authentication via certificates
- Network segmentation via overlay
