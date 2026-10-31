#!/usr/bin/env python3
"""Serve dist/ on loopback only. Usage: python3 serve.py [port]  (default 8765)."""
import functools
import http.server
import sys
from pathlib import Path

DIST = Path(__file__).resolve().parent / "dist"


class Handler(http.server.SimpleHTTPRequestHandler):
    # Show Markdown and llms.txt in the browser instead of downloading them.
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".md": "text/plain; charset=utf-8",
        ".txt": "text/plain; charset=utf-8",
    }


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    handler = functools.partial(Handler, directory=str(DIST))
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        print(f"Serving {DIST} at http://127.0.0.1:{port}/", flush=True)
        httpd.serve_forever()


if __name__ == "__main__":
    main()
