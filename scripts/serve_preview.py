from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class PreviewHandler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve a built Materials-to-Mission site over local HTTP/1.1.")
    parser.add_argument("--directory", required=True, type=Path, help="Built site directory to serve.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: localhost only).")
    parser.add_argument("--port", default=8000, type=int, help="Bind port (default: 8000; use 0 for an available port).")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    directory = args.directory.resolve(strict=True)
    if not directory.is_dir():
        raise SystemExit(f"STOP - preview directory is not a directory: {directory}")
    handler = partial(PreviewHandler, directory=str(directory))
    server = ThreadingHTTPServer((args.host, args.port), handler)
    host, port = server.server_address[:2]
    print(f"Serving {directory} at http://{host}:{port}/ over HTTP/1.1", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
