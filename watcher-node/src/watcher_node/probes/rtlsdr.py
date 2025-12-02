"""RTL-SDR probe for TeleMesh Watcher Node."""

import logging
import threading
import time
from typing import Optional

from .base import BaseProbe

logger = logging.getLogger(__name__)

# RTL-SDR is optional
try:
    from rtlsdr import RtlSdr
    HAS_RTLSDR = True
except ImportError:
    HAS_RTLSDR = False
    logger.debug("RTL-SDR library not available")

# numpy is optional (only needed for signal processing)
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    np = None  # type: ignore
    HAS_NUMPY = False
    logger.debug("numpy library not available")


class RTLSDRProbe(BaseProbe):
    """Probe for detecting RF signals using RTL-SDR."""

    def __init__(
        self,
        center_freq: float = 433.92e6,  # 433 MHz ISM band
        sample_rate: float = 2.4e6,
        gain: str = "auto",
        threshold_db: float = -30.0,
        scan_interval: float = 1.0,
        source_id: str = "watcher-001",
    ):
        """Initialize RTL-SDR probe.

        Args:
            center_freq: Center frequency in Hz
            sample_rate: Sample rate in Hz
            gain: Gain setting ('auto' or float)
            threshold_db: Signal detection threshold in dB
            scan_interval: Seconds between scans
            source_id: Identifier for this watcher node
        """
        super().__init__(source_id)
        self.center_freq = center_freq
        self.sample_rate = sample_rate
        self.gain = gain
        self.threshold_db = threshold_db
        self.scan_interval = scan_interval
        self._thread: threading.Thread | None = None
        self._sdr: Optional["RtlSdr"] = None

    @property
    def probe_name(self) -> str:
        """Return probe name."""
        return "rtlsdr"

    def start(self) -> None:
        """Start RTL-SDR monitoring."""
        if self._running:
            return

        if not HAS_RTLSDR:
            logger.warning("RTL-SDR library not installed, probe disabled")
            return

        logger.info("Starting RTL-SDR probe at %.2f MHz", self.center_freq / 1e6)

        try:
            self._sdr = RtlSdr()
            self._sdr.sample_rate = self.sample_rate
            self._sdr.center_freq = self.center_freq
            if self.gain == "auto":
                self._sdr.gain = "auto"
            else:
                self._sdr.gain = float(self.gain)

            self._running = True
            self._thread = threading.Thread(target=self._scan_loop, daemon=True)
            self._thread.start()
            logger.info("RTL-SDR probe started")

        except Exception as e:
            logger.error("Failed to initialize RTL-SDR: %s", e)
            self._sdr = None

    def stop(self) -> None:
        """Stop RTL-SDR monitoring."""
        if not self._running:
            return

        logger.info("Stopping RTL-SDR probe")
        self._running = False

        if self._thread:
            self._thread.join(timeout=self.scan_interval + 1)

        if self._sdr:
            try:
                self._sdr.close()
            except Exception as e:
                logger.warning("Error closing RTL-SDR: %s", e)
            self._sdr = None

        logger.info("RTL-SDR probe stopped")

    def _scan_loop(self) -> None:
        """Main scanning loop."""
        if not HAS_NUMPY:
            logger.error("numpy not available, cannot run RTL-SDR scanning")
            return

        while self._running and self._sdr:
            try:
                # Read samples
                samples = self._sdr.read_samples(256 * 1024)

                # Compute power spectrum
                spectrum = np.fft.fftshift(np.fft.fft(samples))
                power_db = 20 * np.log10(np.abs(spectrum) + 1e-10)
                peak_power = float(np.max(power_db))
                peak_freq_idx = int(np.argmax(power_db))

                # Calculate frequency of peak
                freq_range = np.linspace(
                    self.center_freq - self.sample_rate / 2,
                    self.center_freq + self.sample_rate / 2,
                    len(power_db)
                )
                peak_freq = float(freq_range[peak_freq_idx])

                # Check threshold
                if peak_power > self.threshold_db:
                    self.emit_event({
                        "type": "signal_detected",
                        "frequency_hz": peak_freq,
                        "frequency_mhz": peak_freq / 1e6,
                        "power_db": peak_power,
                        "threshold_db": self.threshold_db,
                    })

            except Exception as e:
                logger.error("Error reading RTL-SDR: %s", e)

            time.sleep(self.scan_interval)
