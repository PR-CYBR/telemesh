/**
 * TeleMesh Edge Sensor Node - Telemetry Interface
 *
 * JSON message formatting for telemetry and probe events.
 */

#ifndef TELEMETRY_H
#define TELEMETRY_H

#include "sensors.h"
#include <stdint.h>
#include <stdbool.h>

#define TELEMETRY_BUFFER_SIZE 512
#define PROBE_EVENT_BUFFER_SIZE 256

/**
 * Probe event types
 */
typedef enum {
    PROBE_EVENT_TEMP_HIGH,
    PROBE_EVENT_TEMP_LOW,
    PROBE_EVENT_HUMIDITY_HIGH,
    PROBE_EVENT_VOLTAGE_LOW,
    PROBE_EVENT_SENSOR_ERROR
} probe_event_type_t;

/**
 * Probe event structure
 */
typedef struct {
    probe_event_type_t type;
    const char *trigger;
    float value;
    float threshold;
    uint32_t timestamp;
} probe_event_t;

/**
 * Format sensor readings as JSON telemetry message
 * @param readings Sensor readings to format
 * @param buffer Output buffer for JSON string
 * @param buffer_size Size of output buffer
 * @return Number of bytes written, or -1 on error
 */
int telemetry_format_json(const sensor_readings_t *readings,
                          char *buffer, size_t buffer_size);

/**
 * Format probe event as JSON message
 * @param event Probe event to format
 * @param buffer Output buffer for JSON string
 * @param buffer_size Size of output buffer
 * @return Number of bytes written, or -1 on error
 */
int telemetry_format_probe_event(const probe_event_t *event,
                                  char *buffer, size_t buffer_size);

/**
 * Check sensor readings for threshold violations
 * @param readings Sensor readings to check
 * @param event Output probe event if threshold violated
 * @return true if a threshold was violated
 */
bool telemetry_check_thresholds(const sensor_readings_t *readings,
                                 probe_event_t *event);

#endif // TELEMETRY_H
