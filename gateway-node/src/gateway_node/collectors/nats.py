"""NATS collector for TeleMesh Gateway Node."""

import json
import logging

from .base import BaseCollector, TelemetryPoint

logger = logging.getLogger(__name__)

# NATS is optional
try:
    import nats
    HAS_NATS = True
except ImportError:
    HAS_NATS = False
    logger.debug("NATS library not available")


class NATSCollector(BaseCollector):
    """Collector for publishing telemetry to NATS."""

    def __init__(
        self,
        url: str = "nats://localhost:4222",
        subject: str = "telemesh.telemetry",
    ):
        """Initialize NATS collector.

        Args:
            url: NATS server URL
            subject: Subject to publish to
        """
        self.url = url
        self.subject = subject
        self._client = None
        self._connected = False

    async def connect(self) -> None:
        """Connect to NATS server."""
        if not HAS_NATS:
            logger.warning("NATS library not installed")
            return

        if self._connected:
            return

        logger.info("Connecting to NATS at %s", self.url)

        try:
            self._client = await nats.connect(self.url)
            self._connected = True
            logger.info("Connected to NATS")
        except Exception as e:
            logger.error("Failed to connect to NATS: %s", e)

    async def disconnect(self) -> None:
        """Disconnect from NATS server."""
        if not self._connected or not self._client:
            return

        logger.info("Disconnecting from NATS")

        try:
            await self._client.drain()
        except Exception as e:
            logger.warning("Error draining NATS connection: %s", e)

        self._connected = False
        self._client = None

    async def write(self, point: TelemetryPoint) -> bool:
        """Publish telemetry point to NATS.

        Args:
            point: The telemetry point to publish

        Returns:
            True if published successfully
        """
        if not self._connected or not self._client:
            logger.warning("Not connected to NATS")
            return False

        try:
            # Format message
            message = {
                "measurement": point.measurement,
                "tags": point.tags,
                "fields": point.fields,
                "timestamp": point.timestamp,
            }

            # Publish
            subject = f"{self.subject}.{point.measurement}"
            await self._client.publish(subject, json.dumps(message).encode())
            logger.debug("Published to NATS: %s", subject)
            return True

        except Exception as e:
            logger.error("Error publishing to NATS: %s", e)
            return False
