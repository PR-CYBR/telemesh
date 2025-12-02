/**
 * TeleMesh Edge Sensor Node - Sensor Implementations
 *
 * Driver implementations for BME280 and INA219 sensors.
 */

#include "sensors.h"
#include "config.h"
#include <Wire.h>
#include <Adafruit_BME280.h>
#include <Adafruit_INA219.h>

// Sensor instances
static Adafruit_BME280 bme280;
static Adafruit_INA219 ina219(INA219_I2C_ADDR);

// Initialization flags
static bool bme280_initialized = false;
static bool ina219_initialized = false;

bool sensors_init(void) {
    bool success = true;

    // Initialize BME280
    if (bme280.begin(BME280_I2C_ADDR, &Wire)) {
        bme280_initialized = true;
        Serial.println("BME280 initialized at 0x76");
    } else {
        Serial.println("WARNING: BME280 not found at 0x76");
        success = false;
    }

    // Initialize INA219
    if (ina219.begin()) {
        ina219_initialized = true;
        Serial.println("INA219 initialized at 0x40");
    } else {
        Serial.println("WARNING: INA219 not found at 0x40");
        success = false;
    }

    return success;
}

bool sensors_read_bme280(bme280_reading_t *reading) {
    if (!reading) return false;

    reading->valid = false;

    if (!bme280_initialized) {
        return false;
    }

    reading->temperature_c = bme280.readTemperature();
    reading->humidity_pct = bme280.readHumidity();
    reading->pressure_hpa = bme280.readPressure() / 100.0F;

    // Validate readings (check for NaN or impossible values)
    if (isnan(reading->temperature_c) || isnan(reading->humidity_pct) ||
        isnan(reading->pressure_hpa)) {
        return false;
    }

    if (reading->temperature_c < -40 || reading->temperature_c > 85) {
        return false;
    }

    if (reading->humidity_pct < 0 || reading->humidity_pct > 100) {
        return false;
    }

    if (reading->pressure_hpa < 300 || reading->pressure_hpa > 1100) {
        return false;
    }

    reading->valid = true;
    return true;
}

bool sensors_read_ina219(ina219_reading_t *reading) {
    if (!reading) return false;

    reading->valid = false;

    if (!ina219_initialized) {
        return false;
    }

    reading->voltage_v = ina219.getBusVoltage_V();
    reading->current_ma = ina219.getCurrent_mA();
    reading->power_mw = ina219.getPower_mW();

    // Validate readings
    if (isnan(reading->voltage_v) || isnan(reading->current_ma) ||
        isnan(reading->power_mw)) {
        return false;
    }

    // INA219 voltage range is 0-26V
    if (reading->voltage_v < 0 || reading->voltage_v > 26) {
        return false;
    }

    reading->valid = true;
    return true;
}

bool sensors_read_all(sensor_readings_t *readings) {
    if (!readings) return false;

    readings->timestamp = millis() / 1000; // Convert to seconds

    bool bme_ok = sensors_read_bme280(&readings->bme280);
    bool ina_ok = sensors_read_ina219(&readings->ina219);

    return bme_ok || ina_ok; // At least one sensor must be working
}
