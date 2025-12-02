"""InfluxDB collector for TeleMesh Gateway Node."""

import logging
from datetime import datetime

from .base import BaseCollector, TelemetryPoint

logger = logging.getLogger(__name__)

# InfluxDB is optional
try:
    from influxdb_client import InfluxDBClient, Point
    from influxdb_client.client.write_api import SYNCHRONOUS
    HAS_INFLUXDB = True
except ImportError:
    HAS_INFLUXDB = False
    logger.debug("InfluxDB library not available")


class InfluxDBCollector(BaseCollector):
    """Collector for writing telemetry to InfluxDB."""

    def __init__(
        self,
        url: str = "http://localhost:8086",
        token: str = "",
        org: str = "telemesh",
        bucket: str = "telemetry",
    ):
        """Initialize InfluxDB collector.

        Args:
            url: InfluxDB server URL
            token: Authentication token
            org: Organization name
            bucket: Bucket to write to
        """
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        self._client = None
        self._write_api = None
        self._connected = False

    async def connect(self) -> None:
        """Connect to InfluxDB."""
        if not HAS_INFLUXDB:
            logger.warning("InfluxDB library not installed")
            return

        if self._connected:
            return

        logger.info("Connecting to InfluxDB at %s", self.url)

        try:
            self._client = InfluxDBClient(
                url=self.url,
                token=self.token,
                org=self.org
            )
            self._write_api = self._client.write_api(write_options=SYNCHRONOUS)
            self._connected = True
            logger.info("Connected to InfluxDB")
        except Exception as e:
            logger.error("Failed to connect to InfluxDB: %s", e)

    async def disconnect(self) -> None:
        """Disconnect from InfluxDB."""
        if not self._connected:
            return

        logger.info("Disconnecting from InfluxDB")

        if self._write_api:
            self._write_api.close()
        if self._client:
            self._client.close()

        self._connected = False
        self._client = None
        self._write_api = None

    async def write(self, point: TelemetryPoint) -> bool:
        """Write telemetry point to InfluxDB.

        Args:
            point: The telemetry point to write

        Returns:
            True if written successfully
        """
        if not self._connected or not self._write_api:
            logger.warning("Not connected to InfluxDB")
            return False

        try:
            # Build InfluxDB point
            influx_point = Point(point.measurement)

            # Add tags
            for key, value in point.tags.items():
                influx_point.tag(key, value)

            # Add fields
            for key, value in point.fields.items():
                influx_point.field(key, value)

            # Set timestamp
            influx_point.time(datetime.fromtimestamp(point.timestamp))

            # Write
            self._write_api.write(bucket=self.bucket, record=influx_point)
            logger.debug("Wrote to InfluxDB: %s", point.measurement)
            return True

        except Exception as e:
            logger.error("Error writing to InfluxDB: %s", e)
            return False
