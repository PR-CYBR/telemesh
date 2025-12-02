"""Reticulum router for TeleMesh Gateway Node."""

import logging
from typing import Callable

logger = logging.getLogger(__name__)

# Reticulum is optional
try:
    import RNS
    HAS_RETICULUM = True
except ImportError:
    HAS_RETICULUM = False
    logger.debug("Reticulum Network Stack not available")


class ReticulumRouter:
    """Reticulum mesh network router."""

    def __init__(
        self,
        app_name: str = "telemesh",
        aspects: list[str] | None = None,
    ):
        """Initialize Reticulum router.

        Args:
            app_name: Application name for Reticulum destinations
            aspects: List of aspects to listen for
        """
        self.app_name = app_name
        self.aspects = aspects or ["telemetry", "events", "control"]

        self._reticulum = None
        self._identity = None
        self._destinations: dict = {}
        self._handlers: dict[str, list[Callable]] = {}
        self._running = False

    async def start(self) -> None:
        """Start the Reticulum router."""
        if not HAS_RETICULUM:
            logger.warning("Reticulum not installed, router disabled")
            return

        if self._running:
            return

        logger.info("Starting Reticulum router")

        try:
            # Initialize Reticulum
            self._reticulum = RNS.Reticulum()

            # Create or load identity
            identity_path = RNS.Reticulum.storagepath + "/gateway_identity"
            if RNS.Identity.from_file(identity_path):
                self._identity = RNS.Identity.from_file(identity_path)
            else:
                self._identity = RNS.Identity()
                self._identity.to_file(identity_path)

            # Create destinations for each aspect
            for aspect in self.aspects:
                dest = RNS.Destination(
                    self._identity,
                    RNS.Destination.IN,
                    RNS.Destination.SINGLE,
                    self.app_name,
                    aspect,
                )
                dest.set_packet_callback(self._create_packet_handler(aspect))
                self._destinations[aspect] = dest
                logger.info("Created destination for %s.%s", self.app_name, aspect)

            self._running = True
            logger.info("Reticulum router started")

        except Exception as e:
            logger.error("Failed to start Reticulum router: %s", e)

    async def stop(self) -> None:
        """Stop the Reticulum router."""
        if not self._running:
            return

        logger.info("Stopping Reticulum router")
        self._destinations.clear()
        self._reticulum = None
        self._running = False

    def register_handler(
        self,
        aspect: str,
        handler: Callable[[bytes, str], None]
    ) -> None:
        """Register a handler for messages on an aspect.

        Args:
            aspect: The aspect to handle
            handler: Callback function(data, source_hash)
        """
        if aspect not in self._handlers:
            self._handlers[aspect] = []
        self._handlers[aspect].append(handler)
        logger.debug("Registered handler for aspect: %s", aspect)

    def _create_packet_handler(self, aspect: str) -> Callable:
        """Create a packet handler for an aspect."""
        def handler(data, packet):
            source_hash = packet.destination_hash.hex() if packet.destination_hash else "unknown"
            logger.debug("Received packet on %s from %s", aspect, source_hash)

            for callback in self._handlers.get(aspect, []):
                try:
                    callback(data, source_hash)
                except Exception as e:
                    logger.error("Error in handler for %s: %s", aspect, e)

        return handler

    async def send(
        self,
        aspect: str,
        data: bytes,
        destination_hash: str | None = None
    ) -> bool:
        """Send data on an aspect.

        Args:
            aspect: The aspect to send on
            data: Data to send
            destination_hash: Optional specific destination

        Returns:
            True if sent successfully
        """
        if not HAS_RETICULUM or not self._running:
            return False

        try:
            if destination_hash:
                # Send to specific destination
                dest = RNS.Destination(
                    None,
                    RNS.Destination.OUT,
                    RNS.Destination.SINGLE,
                    self.app_name,
                    aspect,
                )
                dest.set_destination_hash(bytes.fromhex(destination_hash))
                packet = RNS.Packet(dest, data)
                packet.send()
            else:
                # Announce on network
                if aspect in self._destinations:
                    self._destinations[aspect].announce(data)

            return True

        except Exception as e:
            logger.error("Error sending on %s: %s", aspect, e)
            return False
