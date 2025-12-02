/**
 * TeleMesh Edge Sensor Node Configuration
 *
 * Configuration constants for the ESP32-S3/Heltec edge sensor node.
 */

#ifndef CONFIG_H
#define CONFIG_H

// Node identification
#define NODE_ID "esn-001"
#define NODE_VERSION "1.0.0"

// Sensor intervals (milliseconds)
#define TELEMETRY_INTERVAL_MS 10000
#define PROBE_CHECK_INTERVAL_MS 1000

// I2C configuration
#define I2C_SDA_PIN 21
#define I2C_SCL_PIN 22

// BME280 configuration
#define BME280_I2C_ADDR 0x76

// INA219 configuration
#define INA219_I2C_ADDR 0x40

// Probe thresholds
#define TEMP_HIGH_THRESHOLD 35.0
#define TEMP_LOW_THRESHOLD 0.0
#define HUMIDITY_HIGH_THRESHOLD 80.0
#define VOLTAGE_LOW_THRESHOLD 3.3

// WiFi configuration (if used)
#define WIFI_SSID "telemesh-network"
#define WIFI_PASSWORD ""

// MQTT configuration (if used)
#define MQTT_BROKER "mqtt.local"
#define MQTT_PORT 1883
#define MQTT_TOPIC_TELEMETRY "telemesh/telemetry"
#define MQTT_TOPIC_EVENTS "telemesh/events"

// LoRa configuration
#define LORA_FREQUENCY 915E6
#define LORA_BANDWIDTH 125E3
#define LORA_SPREADING_FACTOR 7
#define LORA_CODING_RATE 5

// Serial debug
#define DEBUG_ENABLED true
#define DEBUG_BAUD 115200

#endif // CONFIG_H
