"""Dev helper: receives marker.png / targets.mind POSTed by compile.html.

Run alongside the static server, then open /compile.html in a browser:
    python upload_server.py
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import urllib.parse

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
ALLOWED = {"marker.png", "targets.mind"}


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        query = urllib.parse.urlparse(self.path).query
        name = urllib.parse.parse_qs(query).get("name", [""])[0]
        name = os.path.basename(name)
        if name not in ALLOWED:
            self.send_response(400)
            self._cors()
            self.end_headers()
            self.wfile.write(b"bad name")
            return
        length = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(length)
        with open(os.path.join(OUT_DIR, name), "wb") as f:
            f.write(data)
        self.send_response(200)
        self._cors()
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    print("upload server on http://127.0.0.1:8124")
    HTTPServer(("127.0.0.1", 8124), Handler).serve_forever()
