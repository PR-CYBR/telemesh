/**
 * TeleMesh Edge Sensor Node - Main Application
 *
 * ESP32-S3/Heltec firmware for environmental monitoring.
 * Reads BME280 and INA219 sensors, transmits JSON telemetry,
 * and generates probe_event messages on threshold violations.
 */

#include <Arduino.h>
#include <Wire.h>
#include "config.h"
#include "sensors.h"
#include "telemetry.h"

// Timing variables
static unsigned long lastTelemetryTime = 0;
static unsigned long lastProbeCheckTime = 0;

// Buffers for JSON messages
static char telemetryBuffer[TELEMETRY_BUFFER_SIZE];
static char eventBuffer[PROBE_EVENT_BUFFER_SIZE];

void setup() {
    // Initialize serial for debugging
    Serial.begin(DEBUG_BAUD);
    while (!Serial && millis() < 3000) {
        delay(10);
    }

    Serial.println();
    Serial.println("========================================");
    Serial.println("TeleMesh Edge Sensor Node");
    Serial.printf("Node ID: %s\n", NODE_ID);
    Serial.printf("Version: %s\n", NODE_VERSION);
    Serial.println("========================================");

    // Initialize I2C
    Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
    Serial.println("I2C initialized");

    // Initialize sensors
    if (!sensors_init()) {
        Serial.println("ERROR: Sensor initialization failed!");
        // Continue anyway, sensors may recover
    } else {
        Serial.println("Sensors initialized successfully");
    }

    Serial.println("Setup complete. Starting main loop...");
    Serial.println();
}

void loop() {
    unsigned long currentTime = millis();

    // Check for telemetry interval
    if (currentTime - lastTelemetryTime >= TELEMETRY_INTERVAL_MS) {
        lastTelemetryTime = currentTime;

        sensor_readings_t readings;
        if (sensors_read_all(&readings)) {
            int len = telemetry_format_json(&readings, telemetryBuffer,
                                             sizeof(telemetryBuffer));
            if (len > 0) {
                Serial.println("Telemetry:");
                Serial.println(telemetryBuffer);
                Serial.println();
                // TODO: Transmit via LoRa or WiFi
            }
        }
    }

    // Check for probe events
    if (currentTime - lastProbeCheckTime >= PROBE_CHECK_INTERVAL_MS) {
        lastProbeCheckTime = currentTime;

        sensor_readings_t readings;
        if (sensors_read_all(&readings)) {
            probe_event_t event;
            if (telemetry_check_thresholds(&readings, &event)) {
                int len = telemetry_format_probe_event(&event, eventBuffer,
                                                        sizeof(eventBuffer));
                if (len > 0) {
                    Serial.println("Probe Event:");
                    Serial.println(eventBuffer);
                    Serial.println();
                    // TODO: Transmit via LoRa or WiFi
                }
            }
        }
    }

    // Small delay to prevent watchdog issues
    delay(10);
}
