# Task: Edge Sensor Node Implementation

## Objective

Complete implementation of the ESP32-S3/Heltec edge sensor node firmware with BME280 and INA219 sensor support, JSON telemetry transmission, and probe_event generation.

## Requirements

- [x] Create PlatformIO project structure
- [x] Implement BME280 sensor driver (temperature, humidity, pressure)
- [x] Implement INA219 sensor driver (voltage, current, power)
- [x] Create JSON telemetry message formatting
- [x] Implement probe_event generation for threshold violations
- [ ] Add LoRa communication layer
- [ ] Add WiFi fallback communication
- [ ] Implement deep sleep for power saving
- [ ] Create unit tests

## Implementation Notes

### Hardware Configuration

- ESP32-S3 or Heltec WiFi LoRa 32 v3
- I2C bus: SDA=GPIO21, SCL=GPIO22
- BME280 at address 0x76
- INA219 at address 0x40

### Telemetry Format

```json
{
  "node_id": "esn-001",
  "timestamp": 1701532800,
  "sensors": {
    "bme280": {"temperature_c": 22.5, "humidity_pct": 45.2, "pressure_hpa": 1013.25},
    "ina219": {"voltage_v": 3.7, "current_ma": 125.4, "power_mw": 463.98}
  }
}
```

### Probe Event Format

```json
{
  "node_id": "esn-001",
  "event_type": "probe_event",
  "probe": "threshold",
  "trigger": "temperature_high",
  "value": 35.2,
  "threshold": 30.0
}
```

## Acceptance Criteria

- [x] Firmware compiles without errors
- [x] Sensor readings are valid and within expected ranges
- [x] JSON telemetry is properly formatted
- [x] Probe events trigger on threshold violations
- [ ] Communication layer transmits data successfully
- [ ] Power consumption meets design targets

## Status

**In Progress** - Core sensor functionality complete, communication layer pending.
