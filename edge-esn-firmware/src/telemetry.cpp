/**
 * TeleMesh Edge Sensor Node - Telemetry Implementation
 *
 * JSON message formatting for telemetry and probe events.
 */

#include "telemetry.h"
#include "config.h"
#include <ArduinoJson.h>

int telemetry_format_json(const sensor_readings_t *readings,
                          char *buffer, size_t buffer_size) {
    if (!readings || !buffer || buffer_size == 0) {
        return -1;
    }

    JsonDocument doc;

    doc["node_id"] = NODE_ID;
    doc["timestamp"] = readings->timestamp;

    JsonObject sensors = doc["sensors"].to<JsonObject>();

    if (readings->bme280.valid) {
        JsonObject bme = sensors["bme280"].to<JsonObject>();
        bme["temperature_c"] = readings->bme280.temperature_c;
        bme["humidity_pct"] = readings->bme280.humidity_pct;
        bme["pressure_hpa"] = readings->bme280.pressure_hpa;
    }

    if (readings->ina219.valid) {
        JsonObject ina = sensors["ina219"].to<JsonObject>();
        ina["voltage_v"] = readings->ina219.voltage_v;
        ina["current_ma"] = readings->ina219.current_ma;
        ina["power_mw"] = readings->ina219.power_mw;
    }

    size_t len = serializeJson(doc, buffer, buffer_size);
    return (int)len;
}

int telemetry_format_probe_event(const probe_event_t *event,
                                  char *buffer, size_t buffer_size) {
    if (!event || !buffer || buffer_size == 0) {
        return -1;
    }

    JsonDocument doc;

    doc["node_id"] = NODE_ID;
    doc["event_type"] = "probe_event";
    doc["timestamp"] = event->timestamp;
    doc["probe"] = "threshold";
    doc["trigger"] = event->trigger;
    doc["value"] = event->value;
    doc["threshold"] = event->threshold;

    size_t len = serializeJson(doc, buffer, buffer_size);
    return (int)len;
}

bool telemetry_check_thresholds(const sensor_readings_t *readings,
                                 probe_event_t *event) {
    if (!readings || !event) {
        return false;
    }

    event->timestamp = readings->timestamp;

    // Check temperature high threshold
    if (readings->bme280.valid &&
        readings->bme280.temperature_c > TEMP_HIGH_THRESHOLD) {
        event->type = PROBE_EVENT_TEMP_HIGH;
        event->trigger = "temperature_high";
        event->value = readings->bme280.temperature_c;
        event->threshold = TEMP_HIGH_THRESHOLD;
        return true;
    }

    // Check temperature low threshold
    if (readings->bme280.valid &&
        readings->bme280.temperature_c < TEMP_LOW_THRESHOLD) {
        event->type = PROBE_EVENT_TEMP_LOW;
        event->trigger = "temperature_low";
        event->value = readings->bme280.temperature_c;
        event->threshold = TEMP_LOW_THRESHOLD;
        return true;
    }

    // Check humidity high threshold
    if (readings->bme280.valid &&
        readings->bme280.humidity_pct > HUMIDITY_HIGH_THRESHOLD) {
        event->type = PROBE_EVENT_HUMIDITY_HIGH;
        event->trigger = "humidity_high";
        event->value = readings->bme280.humidity_pct;
        event->threshold = HUMIDITY_HIGH_THRESHOLD;
        return true;
    }

    // Check voltage low threshold
    if (readings->ina219.valid &&
        readings->ina219.voltage_v < VOLTAGE_LOW_THRESHOLD) {
        event->type = PROBE_EVENT_VOLTAGE_LOW;
        event->trigger = "voltage_low";
        event->value = readings->ina219.voltage_v;
        event->threshold = VOLTAGE_LOW_THRESHOLD;
        return true;
    }

    return false;
}
