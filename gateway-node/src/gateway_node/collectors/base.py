"""Base collector interface for TeleMesh Gateway Node."""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class TelemetryPoint:
    """A single telemetry data point."""

    measurement: str
    tags: dict = field(default_factory=dict)
    fields: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class BaseCollector(ABC):
    """Abstract base class for telemetry collectors."""

    @abstractmethod
    async def connect(self) -> None:
        """Connect to the backend system."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the backend system."""
        pass

    @abstractmethod
    async def write(self, point: TelemetryPoint) -> bool:
        """Write a telemetry point.

        Args:
            point: The telemetry point to write

        Returns:
            True if written successfully
        """
        pass

    async def write_batch(self, points: list[TelemetryPoint]) -> bool:
        """Write multiple telemetry points.

        Args:
            points: List of telemetry points

        Returns:
            True if all written successfully
        """
        success = True
        for point in points:
            if not await self.write(point):
                success = False
        return success
