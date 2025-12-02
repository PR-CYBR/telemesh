# TeleMesh Quick Start Guide

## Prerequisites

- Python 3.10+
- PlatformIO (for edge nodes)
- Docker (optional, for containerized deployment)
- Kubernetes cluster (for production deployment)

## 1. Edge Sensor Node Setup

### Hardware Requirements

- ESP32-S3 or Heltec WiFi LoRa 32 v3
- BME280 sensor (I2C address 0x76)
- INA219 power monitor (I2C address 0x40)

### Wiring

| ESP32 Pin | BME280 | INA219 |
|-----------|--------|--------|
| GPIO21 (SDA) | SDA | SDA |
| GPIO22 (SCL) | SCL | SCL |
| 3.3V | VCC | VCC |
| GND | GND | GND |

### Firmware Upload

```bash
cd edge-esn-firmware

# Install PlatformIO
pip install platformio

# Build and upload
pio run -e heltec_wifi_lora_32_v3 -t upload

# Monitor serial output
pio device monitor
```

## 2. Watcher Node Setup

```bash
cd watcher-node

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install package
pip install -e .

# Run watcher node
watcher-node -c config.yaml -v
```

## 3. Gateway Node Setup

```bash
cd gateway-node

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install package with all extras
pip install -e ".[all]"

# Run gateway node
gateway-node -c config.yaml -v
```

## 4. Kubernetes Deployment

```bash
cd infra/helm/telemesh

# Install with Helm
helm install telemesh . -n telemesh --create-namespace

# Verify deployment
kubectl get pods -n telemesh
```

## 5. Verify Installation

### Check Edge Node

Monitor serial output for telemetry messages.

### Check Watcher Node

Subscribe to MQTT topic to see events.

### Check Gateway Node

Verify collectors are receiving data in InfluxDB/Loki dashboards.

## Troubleshooting

### Edge Node Not Sending Data

1. Check I2C connections
2. Verify sensor addresses (use I2C scanner)
3. Check serial output for errors

### Watcher Node Not Detecting Events

1. Verify log file permissions
2. Check pattern syntax
3. Enable verbose logging (-v)

### Gateway Node Connection Issues

1. Verify backend URLs
2. Check authentication credentials
3. Test network connectivity
