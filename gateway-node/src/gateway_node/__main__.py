"""TeleMesh Gateway Node - Main entry point."""

import argparse
import asyncio
import logging
import signal
import sys
from pathlib import Path

import yaml

from .collectors import NATSCollector, InfluxDBCollector, LokiCollector
from .bridges import MeshtasticMQTTBridge

logger = logging.getLogger(__name__)


def load_config(config_path: Path) -> dict:
    """Load configuration from YAML file."""
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {}


async def main_async(config: dict) -> None:
    """Async main function."""
    collectors = []
    bridges = []

    # Initialize collectors
    nats_config = config.get("collectors", {}).get("nats", {})
    if nats_config.get("enabled", False):
        collectors.append(NATSCollector(
            url=nats_config.get("url", "nats://localhost:4222"),
            subject=nats_config.get("subject", "telemesh.telemetry"),
        ))

    influx_config = config.get("collectors", {}).get("influxdb", {})
    if influx_config.get("enabled", False):
        collectors.append(InfluxDBCollector(
            url=influx_config.get("url", "http://localhost:8086"),
            token=influx_config.get("token", ""),
            org=influx_config.get("org", "telemesh"),
            bucket=influx_config.get("bucket", "telemetry"),
        ))

    loki_config = config.get("collectors", {}).get("loki", {})
    if loki_config.get("enabled", False):
        collectors.append(LokiCollector(
            url=loki_config.get("url", "http://localhost:3100"),
        ))

    # Initialize bridges
    mesh_config = config.get("bridges", {}).get("meshtastic", {})
    if mesh_config.get("enabled", False):
        bridges.append(MeshtasticMQTTBridge(
            mqtt_broker=mesh_config.get("mqtt_broker", "localhost"),
            mqtt_port=mesh_config.get("mqtt_port", 1883),
            mqtt_topic=mesh_config.get("mqtt_topic", "meshtastic/events"),
        ))

    # Start all components
    try:
        for collector in collectors:
            await collector.connect()
            logger.info("Started collector: %s", collector.__class__.__name__)

        for bridge in bridges:
            await bridge.start()
            logger.info("Started bridge: %s", bridge.__class__.__name__)

        logger.info("Gateway node running. Press Ctrl+C to stop.")

        # Wait for shutdown signal
        stop_event = asyncio.Event()

        def signal_handler():
            stop_event.set()

        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, signal_handler)

        await stop_event.wait()

    finally:
        logger.info("Shutting down...")
        for bridge in bridges:
            await bridge.stop()
        for collector in collectors:
            await collector.disconnect()


def main() -> int:
    """Main entry point for gateway-node."""
    parser = argparse.ArgumentParser(description="TeleMesh Gateway Node")
    parser.add_argument(
        "-c", "--config",
        type=Path,
        default=Path("config.yaml"),
        help="Path to configuration file"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger.info("TeleMesh Gateway Node starting...")

    # Load configuration
    config = load_config(args.config)
    logger.debug("Loaded configuration: %s", config)

    try:
        asyncio.run(main_async(config))
    except KeyboardInterrupt:
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
