"""Meshtastic to MQTT bridge for TeleMesh Gateway Node."""

import asyncio
import json
import logging
import threading

import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)

# Meshtastic is optional
try:
    import meshtastic
    from meshtastic.serial_interface import SerialInterface
    from meshtastic.tcp_interface import TCPInterface
    HAS_MESHTASTIC = True
except ImportError:
    HAS_MESHTASTIC = False
    logger.debug("Meshtastic library not available")


class MeshtasticMQTTBridge:
    """Bridge between Meshtastic network and MQTT broker."""

    def __init__(
        self,
        mqtt_broker: str = "localhost",
        mqtt_port: int = 1883,
        mqtt_topic: str = "meshtastic/events",
        meshtastic_connection: str = "serial",
        meshtastic_device: str = "/dev/ttyUSB0",
        meshtastic_host: str = "localhost",
    ):
        """Initialize Meshtastic-MQTT bridge.

        Args:
            mqtt_broker: MQTT broker hostname
            mqtt_port: MQTT broker port
            mqtt_topic: Base topic for Meshtastic events
            meshtastic_connection: Connection type ('serial' or 'tcp')
            meshtastic_device: Serial device path (for serial connection)
            meshtastic_host: Hostname (for TCP connection)
        """
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_topic = mqtt_topic
        self.meshtastic_connection = meshtastic_connection
        self.meshtastic_device = meshtastic_device
        self.meshtastic_host = meshtastic_host

        self._mqtt_client: mqtt.Client | None = None
        self._meshtastic_interface = None
        self._running = False
        self._mqtt_connected = False

    async def start(self) -> None:
        """Start the bridge."""
        if self._running:
            return

        logger.info("Starting Meshtastic-MQTT bridge")

        # Connect to MQTT
        await self._connect_mqtt()

        # Connect to Meshtastic
        if HAS_MESHTASTIC:
            await self._connect_meshtastic()
        else:
            logger.warning("Meshtastic library not installed, only MQTT side active")

        self._running = True
        logger.info("Meshtastic-MQTT bridge started")

    async def stop(self) -> None:
        """Stop the bridge."""
        if not self._running:
            return

        logger.info("Stopping Meshtastic-MQTT bridge")

        if self._meshtastic_interface:
            try:
                self._meshtastic_interface.close()
            except Exception as e:
                logger.warning("Error closing Meshtastic: %s", e)
            self._meshtastic_interface = None

        if self._mqtt_client:
            self._mqtt_client.loop_stop()
            self._mqtt_client.disconnect()
            self._mqtt_client = None

        self._running = False
        logger.info("Meshtastic-MQTT bridge stopped")

    async def _connect_mqtt(self) -> None:
        """Connect to MQTT broker."""
        self._mqtt_client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id="meshtastic-bridge"
        )

        self._mqtt_client.on_connect = self._on_mqtt_connect
        self._mqtt_client.on_disconnect = self._on_mqtt_disconnect
        self._mqtt_client.on_message = self._on_mqtt_message

        try:
            self._mqtt_client.connect(self.mqtt_broker, self.mqtt_port)
            self._mqtt_client.loop_start()

            # Subscribe to control topic
            control_topic = f"{self.mqtt_topic}/control/#"
            self._mqtt_client.subscribe(control_topic)
            logger.info("Subscribed to %s", control_topic)

        except Exception as e:
            logger.error("Failed to connect to MQTT: %s", e)

    async def _connect_meshtastic(self) -> None:
        """Connect to Meshtastic device."""
        try:
            if self.meshtastic_connection == "serial":
                self._meshtastic_interface = SerialInterface(self.meshtastic_device)
            else:
                self._meshtastic_interface = TCPInterface(self.meshtastic_host)

            # Register callback for received packets
            from pubsub import pub
            pub.subscribe(self._on_meshtastic_receive, "meshtastic.receive")

            logger.info("Connected to Meshtastic via %s", self.meshtastic_connection)

        except Exception as e:
            logger.error("Failed to connect to Meshtastic: %s", e)

    def _on_mqtt_connect(
        self,
        client: mqtt.Client,
        userdata: object,
        flags: mqtt.ConnectFlags,
        reason_code: mqtt.ReasonCode,
        properties: mqtt.Properties | None,
    ) -> None:
        """Handle MQTT connection."""
        if reason_code == mqtt.ReasonCode(0):
            logger.info("MQTT connected")
            self._mqtt_connected = True
        else:
            logger.error("MQTT connection failed: %s", reason_code)

    def _on_mqtt_disconnect(
        self,
        client: mqtt.Client,
        userdata: object,
        disconnect_flags: mqtt.DisconnectFlags,
        reason_code: mqtt.ReasonCode,
        properties: mqtt.Properties | None,
    ) -> None:
        """Handle MQTT disconnection."""
        logger.warning("MQTT disconnected: %s", reason_code)
        self._mqtt_connected = False

    def _on_mqtt_message(
        self,
        client: mqtt.Client,
        userdata: object,
        message: mqtt.MQTTMessage,
    ) -> None:
        """Handle incoming MQTT messages."""
        try:
            payload = json.loads(message.payload.decode())
            logger.debug("Received MQTT message: %s", payload)

            # Forward to Meshtastic if connected
            if self._meshtastic_interface:
                self._forward_to_meshtastic(payload)

        except json.JSONDecodeError:
            logger.warning("Invalid JSON in MQTT message")

    def _on_meshtastic_receive(self, packet: dict, interface) -> None:
        """Handle incoming Meshtastic packets."""
        try:
            # Extract relevant fields
            event = {
                "from": packet.get("fromId", ""),
                "to": packet.get("toId", ""),
                "port": packet.get("decoded", {}).get("portnum", ""),
                "payload": packet.get("decoded", {}).get("payload", {}),
                "snr": packet.get("snr", 0),
                "rssi": packet.get("rssi", 0),
                "hop_limit": packet.get("hopLimit", 0),
            }

            # Publish to MQTT
            if self._mqtt_connected and self._mqtt_client:
                topic = f"{self.mqtt_topic}/received"
                self._mqtt_client.publish(topic, json.dumps(event))
                logger.debug("Published Meshtastic event to MQTT")

        except Exception as e:
            logger.error("Error processing Meshtastic packet: %s", e)

    def _forward_to_meshtastic(self, payload: dict) -> None:
        """Forward an MQTT message to Meshtastic."""
        try:
            dest_id = payload.get("to", "^all")
            text = payload.get("text", "")

            if text and self._meshtastic_interface:
                self._meshtastic_interface.sendText(text, destinationId=dest_id)
                logger.debug("Forwarded message to Meshtastic")

        except Exception as e:
            logger.error("Error forwarding to Meshtastic: %s", e)
