import argparse
import json
import logging
import socketserver
from pathlib import Path


class TelemetryHandler(socketserver.StreamRequestHandler):
    output_path: Path

    def handle(self) -> None:
        logging.info("Client connected from %s", self.client_address)
        with self.output_path.open("a", encoding="utf-8") as output:
            for line in self.rfile:
                decoded = line.decode("utf-8", errors="replace").strip()
                if not decoded:
                    continue
                try:
                    json.loads(decoded)
                except json.JSONDecodeError as exc:
                    logging.warning("Dropping malformed telemetry packet: %s", exc)
                    continue
                output.write(decoded + "\n")
                output.flush()
                print(decoded)
        logging.info("Client disconnected: %s", self.client_address)


def main() -> None:
    parser = argparse.ArgumentParser(description="Laptop TCP receiver for telemetry JSON lines")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--output", default="received_telemetry.jsonl")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    TelemetryHandler.output_path = Path(args.output)
    with socketserver.ThreadingTCPServer((args.host, args.port), TelemetryHandler) as server:
        logging.info("Listening on %s:%s", args.host, args.port)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logging.info("Stopping receiver")


if __name__ == "__main__":
    main()
