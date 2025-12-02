"""MQTT publisher for TeleMesh Watcher Node."""

import logging
import threading
import uuid

import paho.mqtt.client as mqtt

from ..probes.base import ProbeEvent
from .base import BasePublisher

logger = logging.getLogger(__name__)


class MQTTPublisher(BasePublisher):
    """Publisher for sending events to MQTT broker."""

    def __init__(
        self,
        broker: str = "localhost",
        port: int = 1883,
        topic: str = "telemesh/events",
        client_id: str | None = None,
        username: str | None = None,
        password: str | None = None,
        tls: bool = False,
    ):
        """Initialize MQTT publisher.

        Args:
            broker: MQTT broker hostname
            port: MQTT broker port
            topic: Topic to publish events to
            client_id: MQTT client identifier (auto-generated if not provided)
            username: Optional username for authentication
            password: Optional password for authentication
            tls: Enable TLS encryption
        """
        self.broker = broker
        self.port = port
        self.topic = topic
        # Generate unique client_id to prevent conflicts with multiple nodes
        self.client_id = client_id or f"watcher-node-{uuid.uuid4().hex[:8]}"
        self.username = username
        self.password = password
        self.tls = tls

        self._client: mqtt.Client | None = None
        self._connected = False
        self._lock = threading.Lock()

    def connect(self) -> None:
        """Connect to MQTT broker."""
        if self._connected:
            return

        logger.info("Connecting to MQTT broker %s:%d", self.broker, self.port)

        self._client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=self.client_id
        )

        # Set up callbacks
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect

        # Configure authentication
        if self.username and self.password:
            self._client.username_pw_set(self.username, self.password)

        # Configure TLS
        if self.tls:
            self._client.tls_set()

        try:
            self._client.connect(self.broker, self.port, keepalive=60)
            self._client.loop_start()
        except Exception as e:
            logger.error("Failed to connect to MQTT broker: %s", e)
            raise

    def disconnect(self) -> None:
        """Disconnect from MQTT broker."""
        if not self._client:
            return

        logger.info("Disconnecting from MQTT broker")
        self._client.loop_stop()
        self._client.disconnect()
        self._connected = False
        self._client = None

    def publish(self, event: ProbeEvent) -> bool:
        """Publish an event to MQTT.

        Args:
            event: The probe event to publish

        Returns:
            True if published successfully
        """
        if not self._connected or not self._client:
            logger.warning("Not connected to MQTT broker")
            return False

        with self._lock:
            try:
                payload = self.serialize_event(event)
                topic = f"{self.topic}/{event.probe}"

                result = self._client.publish(topic, payload, qos=1)
                result.wait_for_publish(timeout=5)

                if result.is_published():
                    logger.debug("Published event to %s", topic)
                    return True
                else:
                    logger.warning("Failed to publish event to %s", topic)
                    return False

            except Exception as e:
                logger.error("Error publishing event: %s", e)
                return False

    def _on_connect(
        self,
        client: mqtt.Client,
        userdata: object,
        flags: mqtt.ConnectFlags,
        reason_code: mqtt.ReasonCode,
        properties: mqtt.Properties | None,
    ) -> None:
        """Handle connection callback."""
        if reason_code == mqtt.ReasonCode(0):
            logger.info("Connected to MQTT broker")
            self._connected = True
        else:
            logger.error("MQTT connection failed: %s", reason_code)
            self._connected = False

    def _on_disconnect(
        self,
        client: mqtt.Client,
        userdata: object,
        disconnect_flags: mqtt.DisconnectFlags,
        reason_code: mqtt.ReasonCode,
        properties: mqtt.Properties | None,
    ) -> None:
        """Handle disconnection callback."""
        logger.warning("Disconnected from MQTT broker: %s", reason_code)
        self._connected = False
