"""Loki collector for TeleMesh Gateway Node."""

import json
import logging
import time

import httpx

from .base import BaseCollector, TelemetryPoint

logger = logging.getLogger(__name__)


class LokiCollector(BaseCollector):
    """Collector for pushing logs to Loki."""

    def __init__(
        self,
        url: str = "http://localhost:3100",
        labels: dict | None = None,
    ):
        """Initialize Loki collector.

        Args:
            url: Loki server URL
            labels: Default labels for all log entries
        """
        self.url = url.rstrip("/")
        self.labels = labels or {"app": "telemesh"}
        self._client: httpx.AsyncClient | None = None
        self._connected = False

    async def connect(self) -> None:
        """Connect to Loki (initialize HTTP client)."""
        if self._connected:
            return

        logger.info("Connecting to Loki at %s", self.url)

        self._client = httpx.AsyncClient(timeout=10.0)
        self._connected = True
        logger.info("Connected to Loki")

    async def disconnect(self) -> None:
        """Disconnect from Loki."""
        if not self._connected:
            return

        logger.info("Disconnecting from Loki")

        if self._client:
            await self._client.aclose()

        self._connected = False
        self._client = None

    async def write(self, point: TelemetryPoint) -> bool:
        """Push telemetry point to Loki as a log entry.

        Args:
            point: The telemetry point to write

        Returns:
            True if pushed successfully
        """
        if not self._connected or not self._client:
            logger.warning("Not connected to Loki")
            return False

        try:
            # Build labels
            labels = {**self.labels, **point.tags}
            labels["measurement"] = point.measurement

            # Format labels as Loki string
            label_str = ",".join(f'{k}="{v}"' for k, v in labels.items())

            # Build log entry
            timestamp_ns = int(point.timestamp * 1e9)
            log_line = json.dumps(point.fields)

            payload = {
                "streams": [
                    {
                        "stream": labels,
                        "values": [[str(timestamp_ns), log_line]]
                    }
                ]
            }

            # Push to Loki
            response = await self._client.post(
                f"{self.url}/loki/api/v1/push",
                json=payload,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 204:
                logger.debug("Pushed to Loki: %s", point.measurement)
                return True
            else:
                logger.warning("Loki push failed: %s", response.status_code)
                return False

        except Exception as e:
            logger.error("Error pushing to Loki: %s", e)
            return False
