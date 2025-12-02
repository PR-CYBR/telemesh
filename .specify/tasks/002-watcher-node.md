# Task: Watcher Node Implementation

## Objective

Implement Python-based probe detectors for monitoring digital and RF signals, with publishing to MQTT and Reticulum networks.

## Requirements

- [x] Create Python package structure with pyproject.toml
- [x] Implement base probe interface
- [x] Implement syslog probe for log monitoring
- [x] Implement Traefik probe for HTTP traffic monitoring
- [x] Implement RTL-SDR probe for RF signal detection
- [x] Implement WiFi HaLow probe for 802.11ah monitoring
- [x] Implement MQTT publisher
- [x] Implement Reticulum publisher
- [ ] Add comprehensive configuration management
- [ ] Create integration tests
- [ ] Add health check endpoint

## Implementation Notes

### Probe Types

| Probe | Source | Detection Method |
|-------|--------|-----------------|
| Syslog | /var/log/syslog | Regex pattern matching |
| Traefik | Traefik API | Service/router changes |
| RTL-SDR | RTL-SDR dongle | Power spectrum analysis |
| WiFi HaLow | wlan interface | iw scan output parsing |

### Event Format

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

## Acceptance Criteria

- [x] Package installs without errors
- [x] All probes implement base interface
- [x] MQTT publisher connects and publishes events
- [x] Reticulum publisher works with RNS
- [ ] Configuration loads from YAML file
- [ ] Integration tests cover all probes
- [ ] Health endpoint reports probe status

## Status

**In Progress** - Core probes and publishers complete, testing and configuration pending.
