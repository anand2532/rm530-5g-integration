"""Connection health monitoring."""

import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional

from rm530_5g_integration.core.manager import RM530Manager
from rm530_5g_integration.utils.logging import get_logger
from rm530_5g_integration.utils.retry import retry

logger = get_logger(__name__)


@dataclass
class HealthStatus:
    """Health status information."""

    is_healthy: bool
    last_check: datetime
    consecutive_failures: int = 0
    issues: list[str] = field(default_factory=list)
    connection_stats: Optional[Dict[str, Any]] = None
    signal_quality: Optional[Dict[str, Any]] = None

    def __str__(self) -> str:
        """String representation."""
        status = "Healthy" if self.is_healthy else "Unhealthy"
        return f"Health Status: {status} (Failures: {self.consecutive_failures})"


class HealthMonitor:
    """Monitor connection health and trigger callbacks."""

    def __init__(
        self,
        manager: RM530Manager,
        interface: str = "usb0",
        check_interval: int = 60,
        failure_threshold: int = 3,
    ):
        """
        Initialize health monitor.

        Args:
            manager: RM530Manager instance
            interface: Network interface to monitor
            check_interval: Seconds between health checks
            failure_threshold: Number of consecutive failures before alerting
        """
        self.manager = manager
        self.interface = interface
        self.check_interval = check_interval
        self.failure_threshold = failure_threshold

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_status: Optional[HealthStatus] = None
        self._callbacks: list[Callable[[HealthStatus], None]] = []
        self._lock = threading.Lock()

    def start(self) -> None:
        """Start health monitoring in background thread."""
        if self._running:
            logger.warning("Health monitor is already running")
            return

        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        logger.info(f"Health monitor started (check interval: {self.check_interval}s)")

    def stop(self) -> None:
        """Stop health monitoring."""
        if not self._running:
            return

        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Health monitor stopped")

    def add_callback(self, callback: Callable[[HealthStatus], None]) -> None:
        """
        Add callback function to be called on health status changes.

        Args:
            callback: Function that takes HealthStatus as argument
        """
        with self._lock:
            self._callbacks.append(callback)

    def remove_callback(self, callback: Callable[[HealthStatus], None]) -> None:
        """Remove a callback function."""
        with self._lock:
            if callback in self._callbacks:
                self._callbacks.remove(callback)

    def check_health(self) -> HealthStatus:
        """
        Perform a health check.

        Returns:
            HealthStatus object
        """
        issues = []
        is_healthy = True
        connection_stats = None
        signal_quality = None

        try:
            # Check connection status
            stats = self.manager.status(self.interface)
            connection_stats = {
                "is_connected": stats.is_connected,
                "ip_address": stats.ip_address,
                "bytes_sent": stats.bytes_sent,
                "bytes_received": stats.bytes_received,
            }

            if not stats.is_connected:
                is_healthy = False
                issues.append("Connection not active")

            if stats.is_connected and not stats.ip_address:
                is_healthy = False
                issues.append("No IP address assigned")

            # Check internet connectivity
            if stats.is_connected:
                try:
                    if not self.manager.verify():
                        is_healthy = False
                        issues.append("Internet connectivity failed")
                except Exception as e:
                    logger.warning(f"Failed to verify internet connectivity: {e}")
                    is_healthy = False
                    issues.append(f"Connectivity check failed: {e}")

            # Try to get signal quality (may require root)
            try:
                signal = self.manager.signal_quality()
                signal_quality = {
                    "rssi": signal.rssi,
                    "rsrp": signal.rsrp,
                    "network_type": signal.network_type,
                }

                # Check signal strength
                if signal.rssi is not None and signal.rssi < -110:
                    is_healthy = False
                    issues.append(f"Poor signal strength: {signal.rssi} dBm")
            except Exception as e:
                logger.debug(f"Could not check signal quality: {e}")
                # Not critical if we can't check signal

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            is_healthy = False
            issues.append(f"Health check error: {e}")

        # Determine consecutive failures
        consecutive_failures = 0
        if self._last_status:
            if is_healthy:
                consecutive_failures = 0
            else:
                consecutive_failures = self._last_status.consecutive_failures + 1

        status = HealthStatus(
            is_healthy=is_healthy,
            last_check=datetime.now(),
            consecutive_failures=consecutive_failures,
            issues=issues,
            connection_stats=connection_stats,
            signal_quality=signal_quality,
        )

        with self._lock:
            self._last_status = status

        return status

    def _monitor_loop(self) -> None:
        """Background monitoring loop."""
        logger.info("Health monitoring loop started")

        while self._running:
            try:
                status = self.check_health()

                # Call callbacks if status changed or threshold reached
                previous_healthy = (
                    self._last_status.is_healthy
                    if self._last_status and hasattr(self._last_status, "is_healthy")
                    else True
                )

                status_changed = status.is_healthy != previous_healthy
                threshold_reached = (
                    not status.is_healthy and status.consecutive_failures >= self.failure_threshold
                )

                if status_changed or threshold_reached:
                    with self._lock:
                        callbacks = self._callbacks.copy()

                    for callback in callbacks:
                        try:
                            callback(status)
                        except Exception as e:
                            logger.error(f"Callback error: {e}")

                logger.debug(f"Health check: {status}")

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")

            # Wait for next check
            time.sleep(self.check_interval)

    def get_last_status(self) -> Optional[HealthStatus]:
        """Get last health status."""
        with self._lock:
            return self._last_status

    @property
    def is_running(self) -> bool:
        """Check if monitor is running."""
        return self._running


def create_health_monitor(
    manager: RM530Manager,
    interface: str = "usb0",
    check_interval: int = 60,
    failure_threshold: int = 3,
) -> HealthMonitor:
    """
    Create a health monitor instance.

    Args:
        manager: RM530Manager instance
        interface: Network interface to monitor
        check_interval: Seconds between checks
        failure_threshold: Consecutive failures before alerting

    Returns:
        HealthMonitor instance
    """
    return HealthMonitor(
        manager=manager,
        interface=interface,
        check_interval=check_interval,
        failure_threshold=failure_threshold,
    )
