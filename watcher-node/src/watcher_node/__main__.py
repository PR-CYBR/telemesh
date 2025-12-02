"""TeleMesh Watcher Node - Main entry point."""

import argparse
import logging
import sys
from pathlib import Path

import yaml

from .probes import SyslogProbe, TraefikProbe
from .publishers import MQTTPublisher

logger = logging.getLogger(__name__)


def load_config(config_path: Path) -> dict:
    """Load configuration from YAML file."""
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {}


def main() -> int:
    """Main entry point for watcher-node."""
    parser = argparse.ArgumentParser(description="TeleMesh Watcher Node")
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

    logger.info("TeleMesh Watcher Node starting...")

    # Load configuration
    config = load_config(args.config)
    logger.debug("Loaded configuration: %s", config)

    # Initialize publisher
    mqtt_config = config.get("mqtt", {})
    publisher = MQTTPublisher(
        broker=mqtt_config.get("broker", "localhost"),
        port=mqtt_config.get("port", 1883),
        topic=mqtt_config.get("topic", "telemesh/events")
    )

    # Initialize probes
    probes = []

    syslog_config = config.get("probes", {}).get("syslog", {})
    if syslog_config.get("enabled", True):
        probes.append(SyslogProbe(
            log_path=Path(syslog_config.get("path", "/var/log/syslog")),
            patterns=syslog_config.get("patterns", [])
        ))

    traefik_config = config.get("probes", {}).get("traefik", {})
    if traefik_config.get("enabled", False):
        probes.append(TraefikProbe(
            api_url=traefik_config.get("api_url", "http://localhost:8080/api")
        ))

    # Register probes with publisher
    for probe in probes:
        probe.on_event = publisher.publish
        logger.info("Registered probe: %s", probe.__class__.__name__)

    # Start publisher and probes
    try:
        publisher.connect()
        for probe in probes:
            probe.start()

        logger.info("Watcher node running. Press Ctrl+C to stop.")
        # Keep running until interrupted
        import time
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        for probe in probes:
            probe.stop()
        publisher.disconnect()

    return 0


if __name__ == "__main__":
    sys.exit(main())
