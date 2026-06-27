from __future__ import annotations

import argparse
import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .state_reader import StateFileError, evaluate_state_file

PACKAGE_DIR = Path(__file__).resolve().parent
STATIC_DIR = PACKAGE_DIR / "web" / "static"
DEFAULT_STATE_FILE = Path("spire_state.json")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sts-agent-web",
        description="Run a local Slay the Spire companion web panel.",
    )
    parser.add_argument(
        "--state",
        default=str(DEFAULT_STATE_FILE),
        help="Path to a Slay the Spire state JSON file.",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)

    handler = build_handler(Path(args.state))
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"STS Agent panel: http://{args.host}:{args.port}")
    print(f"Reading state from: {Path(args.state).resolve()}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
    finally:
        server.server_close()
    return 0


def build_handler(state_path: Path):
    class StsAgentHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path in {"/api/state", "/api/decision"}:
                override = parse_qs(parsed.query).get("state", [None])[0]
                self._send_state(Path(override) if override else state_path)
                return
            if parsed.path == "/api/sample":
                self._send_file(STATIC_DIR / "sample_state.json")
                return
            if parsed.path in {"/", "/index.html"}:
                self._send_file(STATIC_DIR / "index.html")
                return
            static_target = STATIC_DIR / parsed.path.lstrip("/")
            if static_target.exists() and static_target.is_file():
                self._send_file(static_target)
                return
            self._send_json({"ok": False, "error": "Not found"}, HTTPStatus.NOT_FOUND)

        def log_message(self, format: str, *args) -> None:
            return

        def _send_state(self, path: Path) -> None:
            try:
                payload = evaluate_state_file(path)
            except StateFileError as exc:
                payload = {"ok": False, "source": str(path), "error": str(exc)}
                self._send_json(payload, HTTPStatus.BAD_REQUEST)
                return
            self._send_json(payload)

        def _send_json(
            self, payload: dict, status: HTTPStatus = HTTPStatus.OK
        ) -> None:
            body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_file(self, path: Path) -> None:
            if not path.exists() or not path.is_file():
                self._send_json({"ok": False, "error": "File not found"}, HTTPStatus.NOT_FOUND)
                return
            body = path.read_bytes()
            content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return StsAgentHandler


if __name__ == "__main__":
    raise SystemExit(main())
