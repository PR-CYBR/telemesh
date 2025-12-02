"""Syslog probe for TeleMesh Watcher Node."""

import logging
import re
import threading
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .base import BaseProbe

logger = logging.getLogger(__name__)


class SyslogHandler(FileSystemEventHandler):
    """Handler for syslog file modifications."""

    def __init__(self, probe: "SyslogProbe"):
        self.probe = probe
        self._last_position = 0

    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return

        if Path(event.src_path) == self.probe.log_path:
            self.probe.process_new_lines()


class SyslogProbe(BaseProbe):
    """Probe for monitoring syslog files."""

    def __init__(
        self,
        log_path: Path = Path("/var/log/syslog"),
        patterns: list[dict] | None = None,
        source_id: str = "watcher-001",
    ):
        """Initialize syslog probe.

        Args:
            log_path: Path to the syslog file
            patterns: List of pattern definitions with name and regex
            source_id: Identifier for this watcher node
        """
        super().__init__(source_id)
        self.log_path = log_path
        self.patterns = patterns or []
        self._compiled_patterns: list[tuple[str, re.Pattern]] = []
        self._observer: Observer | None = None
        self._handler: SyslogHandler | None = None
        self._file_position = 0
        self._lock = threading.Lock()

        # Compile patterns
        for pattern in self.patterns:
            name = pattern.get("name", "unknown")
            regex = pattern.get("pattern", "")
            if regex:
                try:
                    compiled = re.compile(regex)
                    self._compiled_patterns.append((name, compiled))
                    logger.debug("Compiled pattern '%s': %s", name, regex)
                except re.error as e:
                    logger.warning("Invalid pattern '%s': %s", name, e)

    @property
    def probe_name(self) -> str:
        """Return probe name."""
        return "syslog"

    def start(self) -> None:
        """Start monitoring the syslog file."""
        if self._running:
            return

        logger.info("Starting syslog probe for %s", self.log_path)

        # Initialize file position to end of file
        if self.log_path.exists():
            with open(self.log_path, "rb") as f:
                f.seek(0, 2)  # Seek to end
                self._file_position = f.tell()

        # Set up file watcher
        self._handler = SyslogHandler(self)
        self._observer = Observer()
        self._observer.schedule(
            self._handler,
            str(self.log_path.parent),
            recursive=False
        )
        self._observer.start()
        self._running = True

        logger.info("Syslog probe started")

    def stop(self) -> None:
        """Stop monitoring the syslog file."""
        if not self._running:
            return

        logger.info("Stopping syslog probe")

        if self._observer:
            self._observer.stop()
            self._observer.join(timeout=5)
            self._observer = None

        self._running = False
        logger.info("Syslog probe stopped")

    def process_new_lines(self) -> None:
        """Process new lines added to the syslog file."""
        with self._lock:
            try:
                with open(self.log_path, "r") as f:
                    f.seek(self._file_position)
                    new_lines = f.readlines()
                    self._file_position = f.tell()

                for line in new_lines:
                    self._process_line(line.strip())

            except FileNotFoundError:
                logger.warning("Syslog file not found: %s", self.log_path)
            except PermissionError:
                logger.warning("Permission denied reading: %s", self.log_path)

    def _process_line(self, line: str) -> None:
        """Process a single log line against patterns."""
        if not line:
            return

        for name, pattern in self._compiled_patterns:
            match = pattern.search(line)
            if match:
                self.emit_event({
                    "pattern": name,
                    "message": line,
                    "severity": self._extract_severity(line),
                    "matched_groups": match.groupdict() if match.lastgroup else {},
                })
                break  # Only emit first matching pattern

    def _extract_severity(self, line: str) -> str:
        """Extract severity level from log line."""
        line_lower = line.lower()
        if "error" in line_lower or "crit" in line_lower:
            return "error"
        elif "warn" in line_lower:
            return "warning"
        elif "debug" in line_lower:
            return "debug"
        return "info"
