import logging
import socket
import time

from data_model import TelemetrySample


class TcpTelemetryClient:
    """Sends telemetry samples from the Pi to the laptop-side receiver.

    Decoupled from local storage: pi_main.py calls storage.write(sample)
    and telemetry.send(sample) independently, so a missing or broken
    telemetry link never affects local recording.

    Reconnects automatically with exponential backoff instead of
    attempting a fresh connect on every sample - at a 50 Hz sample rate,
    retrying unconditionally would mean up to 50 connection attempts per
    second while the laptop is unreachable.
    """

    def __init__(
        self,
        host: str,
        port: int,
        connect_timeout_s: float = 0.5,
        reconnect_initial_delay_s: float = 1.0,
        reconnect_max_delay_s: float = 30.0,
    ) -> None:
        self._address = (host, port)
        self._connect_timeout_s = connect_timeout_s
        self._reconnect_initial_delay_s = reconnect_initial_delay_s
        self._reconnect_max_delay_s = reconnect_max_delay_s
        self._socket: socket.socket | None = None
        self._next_reconnect_attempt = 0.0
        self._reconnect_delay = reconnect_initial_delay_s

    def send(self, sample: TelemetrySample) -> None:
        if self._socket is None:
            self._maybe_reconnect()
        if self._socket is None:
            return  # no link right now - the sample is still stored locally by the caller

        try:
            self._socket.sendall(sample.to_json_line().encode("utf-8"))
        except OSError as exc:
            logging.warning("Telemetry send failed: %s", exc)
            self._disconnect()

    def close(self) -> None:
        self._disconnect()

    def _maybe_reconnect(self) -> None:
        now = time.monotonic()
        if now < self._next_reconnect_attempt:
            return
        try:
            sock = socket.create_connection(self._address, timeout=self._connect_timeout_s)
        except OSError as exc:
            logging.debug("Telemetry receiver unavailable: %s", exc)
            self._next_reconnect_attempt = now + self._reconnect_delay
            self._reconnect_delay = min(self._reconnect_delay * 2, self._reconnect_max_delay_s)
            return

        sock.settimeout(self._connect_timeout_s)
        self._socket = sock
        self._reconnect_delay = self._reconnect_initial_delay_s
        self._next_reconnect_attempt = 0.0
        logging.info("Telemetry connected to %s:%s", *self._address)

    def _disconnect(self) -> None:
        if self._socket is not None:
            try:
                self._socket.close()
            except OSError:
                pass
            self._socket = None
