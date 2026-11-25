#!/usr/bin/env python3
"""Render diagram source to a file using a local Kroki server (Docker).

Use this when uml-mcp is not connected. Diagram source is POSTed to a Kroki
server running locally, so nothing is sent to the public kroki.io service.

Start the server once with:

    docker run -d --name kroki -p 8090:8000 yuzutech/kroki

(or `docker start kroki` if the container already exists).

The server URL defaults to $KROKI_URL, or http://localhost:8090 when unset.
"""

from __future__ import annotations

import argparse
import os
import sys
import urllib.error
import urllib.request

DEFAULT_BASE = os.environ.get("KROKI_URL", "http://localhost:8090")
DOCKER_HINT = (
    "Start it with:  docker start kroki 2>/dev/null || "
    "docker run -d --name kroki -p 8090:8000 yuzutech/kroki"
)


def render(code: str, diagram_type: str, fmt: str, base: str) -> bytes:
    """POST diagram source to Kroki and return the rendered bytes."""
    url = f"{base.rstrip('/')}/{diagram_type}/{fmt}"
    req = urllib.request.Request(
        url,
        data=code.encode("utf-8"),
        headers={"Content-Type": "text/plain"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render diagram source (file or stdin) via a local Kroki server.",
    )
    parser.add_argument(
        "-t",
        "--diagram-type",
        default="plantuml",
        metavar="BACKEND",
        help="Kroki backend, e.g. plantuml, mermaid, d2 (default: plantuml)",
    )
    parser.add_argument(
        "-f",
        "--format",
        default=None,
        help="Output format, e.g. svg, png, pdf (default: from -o extension, else svg)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file; default is the input path with the format's extension, "
        "or stdout when reading stdin",
    )
    parser.add_argument(
        "--base",
        default=DEFAULT_BASE,
        help=f"Kroki server base URL (default: $KROKI_URL or {DEFAULT_BASE})",
    )
    parser.add_argument("file", nargs="?", help="Diagram source; if omitted, read stdin")
    args = parser.parse_args()

    fmt = args.format
    if not fmt and args.output and "." in os.path.basename(args.output):
        fmt = args.output.rsplit(".", 1)[1]
    fmt = (fmt or "svg").strip().lower()

    if args.file:
        try:
            with open(args.file, encoding="utf-8") as fh:
                code = fh.read()
        except OSError as e:
            print(f"kroki_render: {args.file}: {e}", file=sys.stderr)
            return 1
    else:
        if sys.stdin.isatty():
            print("kroki_render: provide a FILE or pipe diagram source on stdin", file=sys.stderr)
            return 1
        code = sys.stdin.read()

    output = args.output
    if not output and args.file:
        output = os.path.splitext(args.file)[0] + "." + fmt

    try:
        data = render(code, args.diagram_type.strip().lower(), fmt, args.base)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace").strip()
        print(f"kroki_render: HTTP {e.code} from Kroki (diagram error?):\n{detail}", file=sys.stderr)
        return 2
    except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
        reason = getattr(e, "reason", e)
        print(
            f"kroki_render: cannot reach Kroki at {args.base} ({reason}).\n{DOCKER_HINT}",
            file=sys.stderr,
        )
        return 3

    if output:
        with open(output, "wb") as fh:
            fh.write(data)
        print(output)
    else:
        sys.stdout.buffer.write(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
