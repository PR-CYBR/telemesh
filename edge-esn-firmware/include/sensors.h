/**
 * TeleMesh Edge Sensor Node - Sensor Interface
 *
 * Interface definitions for BME280 and INA219 sensors.
 */

#ifndef SENSORS_H
#define SENSORS_H

#include <stdint.h>
#include <stdbool.h>

/**
 * BME280 sensor readings
 */
typedef struct {
    float temperature_c;
    float humidity_pct;
    float pressure_hpa;
    bool valid;
} bme280_reading_t;

/**
 * INA219 sensor readings
 */
typedef struct {
    float voltage_v;
    float current_ma;
    float power_mw;
    bool valid;
} ina219_reading_t;

/**
 * Combined sensor readings
 */
typedef struct {
    bme280_reading_t bme280;
    ina219_reading_t ina219;
    uint32_t timestamp;
} sensor_readings_t;

/**
 * Initialize all sensors
 * @return true if all sensors initialized successfully
 */
bool sensors_init(void);

/**
 * Read BME280 sensor
 * @param reading Pointer to reading structure
 * @return true if reading successful
 */
bool sensors_read_bme280(bme280_reading_t *reading);

/**
 * Read INA219 sensor
 * @param reading Pointer to reading structure
 * @return true if reading successful
 */
bool sensors_read_ina219(ina219_reading_t *reading);

/**
 * Read all sensors
 * @param readings Pointer to combined readings structure
 * @return true if all readings successful
 */
bool sensors_read_all(sensor_readings_t *readings);

#endif // SENSORS_H
