"""Base publisher interface for TeleMesh Watcher Node."""

import json
import logging
from abc import ABC, abstractmethod

from ..probes.base import ProbeEvent

logger = logging.getLogger(__name__)


class BasePublisher(ABC):
    """Abstract base class for all publishers."""

    @abstractmethod
    def connect(self) -> None:
        """Connect to the message broker."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the message broker."""
        pass

    @abstractmethod
    def publish(self, event: ProbeEvent) -> bool:
        """Publish an event to the message broker.

        Args:
            event: The probe event to publish

        Returns:
            True if published successfully
        """
        pass

    def serialize_event(self, event: ProbeEvent) -> str:
        """Serialize an event to JSON string."""
        return json.dumps(event.to_dict())
