"""Unit tests for fetch_ics."""

import io
import sys
import unittest
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
import urllib.error

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from fetch_ics import fetch_ics

# ---------------------------------------------------------------------------
# Tiny in-process HTTP server that serves a fake iCal payload
# ---------------------------------------------------------------------------

VALID_ICS = "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nBEGIN:VEVENT\r\nDTSTART:20260817T120000Z\r\nSUMMARY:Test Event\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n"

NOT_ICS = "This is not an iCal file."


class _Handler(BaseHTTPRequestHandler):
    """Serves a fixed response based on the request path."""

    def do_GET(self):
        if self.path == "/valid.ics":
            self.send_response(200)
            self.send_header("Content-Type", "text/calendar; charset=utf-8")
            self.end_headers()
            self.wfile.write(VALID_ICS.encode())
        elif self.path == "/not-ics":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(NOT_ICS.encode())
        elif self.path == "/empty":
            self.send_response(200)
            self.send_header("Content-Type", "text/calendar")
            self.end_headers()
            self.wfile.write(b"")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *_):
        pass   # silence the server log


def _make_server() -> tuple[HTTPServer, int]:
    """Start a background server on a random free port. Returns (server, port)."""
    # Bind to port 0 = OS picks a free port
    srv = HTTPServer(("127.0.0.1", 0), _Handler)
    srv.server_activate()
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    return srv, srv.server_address[1]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestFetchIcs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.port = _make_server()
        cls.base = f"http://127.0.0.1:{cls.port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_fetch_valid_ics(self):
        with self.assertNoLogs():
            path = fetch_ics(f"{self.base}/valid.ics")
        from pathlib import Path
        self.assertTrue(Path(path).exists())
        self.assertTrue(Path(path).read_text().startswith("BEGIN:VCALENDAR"))

    def test_fetch_valid_ics_custom_name(self):
        path = fetch_ics(f"{self.base}/valid.ics", "my_custom_name.ics")
        self.assertTrue(path.endswith("my_custom_name.ics"))

    def test_fetch_not_ics_raises(self):
        with self.assertRaises(ValueError) as ctx:
            fetch_ics(f"{self.base}/not-ics")
        self.assertIn("doesn't look like an iCal file", str(ctx.exception))

    def test_raises_on_404(self):
        with self.assertRaises(urllib.error.URLError):
            fetch_ics(f"{self.base}/does-not-exist.ics")


if __name__ == "__main__":
    unittest.main()
