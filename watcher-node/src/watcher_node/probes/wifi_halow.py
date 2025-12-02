"""WiFi HaLow (802.11ah) probe for TeleMesh Watcher Node."""

import logging
import re
import subprocess
import threading
import time

from .base import BaseProbe

logger = logging.getLogger(__name__)

# WiFi HaLow (802.11ah) frequency range constants (MHz)
HALOW_FREQ_MIN_MHZ = 750
HALOW_FREQ_MAX_MHZ = 950


class WiFiHaLowProbe(BaseProbe):
    """Probe for monitoring WiFi HaLow (802.11ah) networks."""

    def __init__(
        self,
        interface: str = "wlan0",
        scan_interval: float = 30.0,
        source_id: str = "watcher-001",
    ):
        """Initialize WiFi HaLow probe.

        Args:
            interface: Network interface to monitor
            scan_interval: Seconds between scans
            source_id: Identifier for this watcher node
        """
        super().__init__(source_id)
        self.interface = interface
        self.scan_interval = scan_interval
        self._thread: threading.Thread | None = None
        self._previous_stations: set = set()

    @property
    def probe_name(self) -> str:
        """Return probe name."""
        return "wifi_halow"

    def start(self) -> None:
        """Start WiFi HaLow monitoring."""
        if self._running:
            return

        logger.info("Starting WiFi HaLow probe on %s", self.interface)
        self._running = True
        self._thread = threading.Thread(target=self._scan_loop, daemon=True)
        self._thread.start()
        logger.info("WiFi HaLow probe started")

    def stop(self) -> None:
        """Stop WiFi HaLow monitoring."""
        if not self._running:
            return

        logger.info("Stopping WiFi HaLow probe")
        self._running = False
        if self._thread:
            self._thread.join(timeout=self.scan_interval + 1)
        logger.info("WiFi HaLow probe stopped")

    def _scan_loop(self) -> None:
        """Main scanning loop."""
        while self._running:
            try:
                self._scan_networks()
                self._check_stations()
            except Exception as e:
                logger.error("Error during WiFi scan: %s", e)

            time.sleep(self.scan_interval)

    def _scan_networks(self) -> None:
        """Scan for nearby WiFi networks."""
        try:
            # Use iw to scan for networks
            result = subprocess.run(
                ["iw", "dev", self.interface, "scan"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                logger.debug("Scan failed: %s", result.stderr)
                return

            # Parse scan results
            networks = self._parse_scan_output(result.stdout)

            for network in networks:
                # Emit event for each detected network
                self.emit_event({
                    "type": "network_detected",
                    "ssid": network.get("ssid", ""),
                    "bssid": network.get("bssid", ""),
                    "frequency_mhz": network.get("frequency", 0),
                    "signal_dbm": network.get("signal", 0),
                    "is_halow": network.get("is_halow", False),
                })

        except subprocess.TimeoutExpired:
            logger.warning("WiFi scan timed out")
        except FileNotFoundError:
            logger.warning("iw command not found")

    def _parse_scan_output(self, output: str) -> list[dict]:
        """Parse iw scan output into network list."""
        networks = []
        current_network = {}

        for line in output.split("\n"):
            line = line.strip()

            # New BSS entry
            if line.startswith("BSS "):
                if current_network:
                    networks.append(current_network)
                bssid_match = re.search(r"BSS ([0-9a-f:]+)", line)
                current_network = {
                    "bssid": bssid_match.group(1) if bssid_match else "",
                    "ssid": "",
                    "frequency": 0,
                    "signal": 0,
                    "is_halow": False,
                }

            # Frequency
            elif line.startswith("freq:"):
                freq_match = re.search(r"freq: (\d+)", line)
                if freq_match:
                    freq = int(freq_match.group(1))
                    current_network["frequency"] = freq
                    # 802.11ah uses sub-1GHz frequencies (typically 900MHz band)
                    current_network["is_halow"] = (
                        HALOW_FREQ_MIN_MHZ <= freq <= HALOW_FREQ_MAX_MHZ
                    )

            # Signal level
            elif line.startswith("signal:"):
                signal_match = re.search(r"signal: ([-\d.]+)", line)
                if signal_match:
                    current_network["signal"] = float(signal_match.group(1))

            # SSID
            elif line.startswith("SSID:"):
                ssid_match = re.search(r"SSID: (.+)", line)
                if ssid_match:
                    current_network["ssid"] = ssid_match.group(1)

        if current_network:
            networks.append(current_network)

        return networks

    def _check_stations(self) -> None:
        """Check for connected stations (in AP mode)."""
        try:
            result = subprocess.run(
                ["iw", "dev", self.interface, "station", "dump"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return

            current_stations = set()
            for line in result.stdout.split("\n"):
                if line.startswith("Station "):
                    mac_match = re.search(r"Station ([0-9a-f:]+)", line)
                    if mac_match:
                        current_stations.add(mac_match.group(1))

            # Check for new stations
            for mac in current_stations - self._previous_stations:
                self.emit_event({
                    "type": "station_connected",
                    "mac_address": mac,
                })

            # Check for disconnected stations
            for mac in self._previous_stations - current_stations:
                self.emit_event({
                    "type": "station_disconnected",
                    "mac_address": mac,
                })

            self._previous_stations = current_stations

        except subprocess.TimeoutExpired:
            logger.warning("Station check timed out")
        except FileNotFoundError:
            pass  # iw not available
