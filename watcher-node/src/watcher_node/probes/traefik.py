"""Traefik probe for TeleMesh Watcher Node."""

import logging
import threading
import time
from urllib.request import urlopen, Request
from urllib.error import URLError
import json

from .base import BaseProbe

logger = logging.getLogger(__name__)


class TraefikProbe(BaseProbe):
    """Probe for monitoring Traefik API for service events."""

    def __init__(
        self,
        api_url: str = "http://localhost:8080/api",
        poll_interval: float = 10.0,
        source_id: str = "watcher-001",
    ):
        """Initialize Traefik probe.

        Args:
            api_url: Base URL for Traefik API
            poll_interval: Seconds between API polls
            source_id: Identifier for this watcher node
        """
        super().__init__(source_id)
        self.api_url = api_url.rstrip("/")
        self.poll_interval = poll_interval
        self._thread: threading.Thread | None = None
        self._previous_services: dict = {}
        self._previous_routers: dict = {}

    @property
    def probe_name(self) -> str:
        """Return probe name."""
        return "traefik"

    def start(self) -> None:
        """Start monitoring Traefik API."""
        if self._running:
            return

        logger.info("Starting Traefik probe for %s", self.api_url)
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()
        logger.info("Traefik probe started")

    def stop(self) -> None:
        """Stop monitoring Traefik API."""
        if not self._running:
            return

        logger.info("Stopping Traefik probe")
        self._running = False
        if self._thread:
            self._thread.join(timeout=self.poll_interval + 1)
        logger.info("Traefik probe stopped")

    def _poll_loop(self) -> None:
        """Main polling loop."""
        while self._running:
            try:
                self._check_services()
                self._check_routers()
            except Exception as e:
                logger.error("Error polling Traefik API: %s", e)

            time.sleep(self.poll_interval)

    def _fetch_api(self, endpoint: str) -> dict | list | None:
        """Fetch data from Traefik API."""
        url = f"{self.api_url}/{endpoint}"
        try:
            request = Request(url, headers={"Accept": "application/json"})
            with urlopen(request, timeout=5) as response:
                return json.loads(response.read().decode())
        except URLError as e:
            logger.debug("Failed to fetch %s: %s", url, e)
            return None
        except json.JSONDecodeError as e:
            logger.warning("Invalid JSON from %s: %s", url, e)
            return None

    def _check_services(self) -> None:
        """Check for service changes."""
        services = self._fetch_api("http/services")
        if not isinstance(services, list):
            return

        current = {s.get("name"): s for s in services if s.get("name")}

        # Check for new services
        for name, service in current.items():
            if name not in self._previous_services:
                self.emit_event({
                    "type": "service_added",
                    "service_name": name,
                    "provider": service.get("provider", "unknown"),
                    "status": service.get("status", "unknown"),
                })

        # Check for removed services
        for name in self._previous_services:
            if name not in current:
                self.emit_event({
                    "type": "service_removed",
                    "service_name": name,
                })

        # Check for status changes
        for name, service in current.items():
            if name in self._previous_services:
                prev = self._previous_services[name]
                if service.get("status") != prev.get("status"):
                    self.emit_event({
                        "type": "service_status_changed",
                        "service_name": name,
                        "old_status": prev.get("status"),
                        "new_status": service.get("status"),
                    })

        self._previous_services = current

    def _check_routers(self) -> None:
        """Check for router changes."""
        routers = self._fetch_api("http/routers")
        if not isinstance(routers, list):
            return

        current = {r.get("name"): r for r in routers if r.get("name")}

        # Check for new routers
        for name, router in current.items():
            if name not in self._previous_routers:
                self.emit_event({
                    "type": "router_added",
                    "router_name": name,
                    "rule": router.get("rule", ""),
                    "service": router.get("service", "unknown"),
                })

        # Check for removed routers
        for name in self._previous_routers:
            if name not in current:
                self.emit_event({
                    "type": "router_removed",
                    "router_name": name,
                })

        self._previous_routers = current
