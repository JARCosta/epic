from __future__ import annotations

import json
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
STATIC_DIR = ROOT_DIR / "static"
DATA_FILE = ROOT_DIR / "data.json"


def load_items() -> list[dict[str, str]]:
    if not DATA_FILE.exists():
        return []

    try:
        raw_data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    if not isinstance(raw_data, list):
        return []

    valid_items: list[dict[str, str]] = []
    for item in raw_data:
        if (
            isinstance(item, dict)
            and isinstance(item.get("id"), str)
            and isinstance(item.get("text"), str)
            and isinstance(item.get("created_at"), str)
        ):
            valid_items.append(item)
    return valid_items


def save_items(items: list[dict[str, str]]) -> None:
    DATA_FILE.write_text(json.dumps(items, indent=2), encoding="utf-8")


class AppHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self) -> None:
        if self.path == "/api/items":
            self._send_json({"items": load_items()})
            return

        if self.path == "/":
            self.path = "/index.html"

        super().do_GET()

    def do_POST(self) -> None:
        if self.path != "/api/items":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)

        try:
            payload = json.loads(raw_body)
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
            return

        text = payload.get("text", "") if isinstance(payload, dict) else ""
        text = text.strip() if isinstance(text, str) else ""
        if not text:
            self._send_json({"error": "text is required"}, status=HTTPStatus.BAD_REQUEST)
            return

        items = load_items()
        item = {
            "id": f"item-{len(items) + 1}",
            "text": text,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        items.append(item)
        save_items(items)

        self._send_json(item, status=HTTPStatus.CREATED)

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 8000), AppHandler)
    print("Serving on http://127.0.0.1:8000")
    server.serve_forever()


if __name__ == "__main__":
    run()
