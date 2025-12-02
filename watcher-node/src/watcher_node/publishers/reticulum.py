"""Reticulum publisher for TeleMesh Watcher Node."""

import logging
import threading
import time

from ..probes.base import ProbeEvent
from .base import BasePublisher

logger = logging.getLogger(__name__)

# Reticulum is optional
try:
    import RNS
    HAS_RETICULUM = True
except ImportError:
    HAS_RETICULUM = False
    logger.debug("Reticulum Network Stack not available")


class ReticulumPublisher(BasePublisher):
    """Publisher for sending events over Reticulum network."""

    def __init__(
        self,
        app_name: str = "telemesh",
        aspect: str = "events",
        destination_hash: str | None = None,
    ):
        """Initialize Reticulum publisher.

        Args:
            app_name: Application name for Reticulum
            aspect: Aspect filter for destination
            destination_hash: Specific destination hash to send to
        """
        self.app_name = app_name
        self.aspect = aspect
        self.destination_hash = destination_hash

        self._reticulum = None
        self._identity = None
        self._destination = None
        self._connected = False
        self._lock = threading.Lock()

    def connect(self) -> None:
        """Connect to Reticulum network."""
        if not HAS_RETICULUM:
            logger.warning("Reticulum not installed, publisher disabled")
            return

        if self._connected:
            return

        logger.info("Initializing Reticulum connection")

        try:
            # Initialize Reticulum
            self._reticulum = RNS.Reticulum()

            # Create or load identity
            identity_path = RNS.Reticulum.storagepath + "/identity"
            if RNS.Identity.from_file(identity_path):
                self._identity = RNS.Identity.from_file(identity_path)
            else:
                self._identity = RNS.Identity()
                self._identity.to_file(identity_path)

            # Set up destination if hash provided
            if self.destination_hash:
                dest_hash = bytes.fromhex(self.destination_hash)
                self._destination = RNS.Destination(
                    None,
                    RNS.Destination.OUT,
                    RNS.Destination.SINGLE,
                    self.app_name,
                    self.aspect,
                )
                self._destination.set_destination_hash(dest_hash)

            self._connected = True
            logger.info("Reticulum connection established")

        except Exception as e:
            logger.error("Failed to initialize Reticulum: %s", e)
            self._connected = False

    def disconnect(self) -> None:
        """Disconnect from Reticulum network."""
        if not self._connected:
            return

        logger.info("Disconnecting from Reticulum")
        self._reticulum = None
        self._identity = None
        self._destination = None
        self._connected = False

    def publish(self, event: ProbeEvent) -> bool:
        """Publish an event over Reticulum.

        Args:
            event: The probe event to publish

        Returns:
            True if published successfully
        """
        if not HAS_RETICULUM or not self._connected:
            logger.warning("Not connected to Reticulum")
            return False

        with self._lock:
            try:
                payload = self.serialize_event(event).encode("utf-8")

                if self._destination:
                    # Send to specific destination
                    packet = RNS.Packet(self._destination, payload)
                    packet.send()
                    logger.debug("Sent event via Reticulum packet")
                else:
                    # Announce on network
                    announce_dest = RNS.Destination(
                        self._identity,
                        RNS.Destination.IN,
                        RNS.Destination.SINGLE,
                        self.app_name,
                        self.aspect,
                    )
                    announce_dest.announce(payload)
                    logger.debug("Announced event via Reticulum")

                return True

            except Exception as e:
                logger.error("Error publishing via Reticulum: %s", e)
                return False
