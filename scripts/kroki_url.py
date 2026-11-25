#!/usr/bin/env python3
"""Build a shareable Kroki GET URL from diagram source (stdin or file).

Use this when uml-mcp is not connected and you only need a Kroki URL. The
base defaults to the local Docker Kroki server ($KROKI_URL or
http://localhost:8090), so the URL only works on this machine; to get a file,
use kroki_render.py instead. The
uml-mcp server's generate_uml tool maps logical diagram_type values, applies
themes, and prepares PlantUML/Mermaid for backends; this script sends **raw**
source to a Kroki **backend** path segment (e.g. plantuml, mermaid, d2) with no
extra wrapping.

Encoding matches Kroki's usual zlib + base64url pipeline (see uml-mcp
examples/kroki_standalone_encoding.py).
"""

from __future__ import annotations

import argparse
import base64
import os
import sys
import zlib

DEFAULT_BASE = os.environ.get("KROKI_URL", "http://localhost:8090")


def encode_for_kroki(text: str) -> str:
    """Compress and base64url-encode text for Kroki GET requests."""
    if not text:
        return ""
    compress_obj = zlib.compressobj(level=9, method=zlib.DEFLATED, wbits=15)
    compressed = compress_obj.compress(text.encode("utf-8")) + compress_obj.flush()
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii")
    return encoded.replace("+", "-").replace("/", "_")


def kroki_url(
    code: str,
    diagram_type: str = "plantuml",
    fmt: str = "svg",
    base: str = DEFAULT_BASE,
) -> str:
    """Build a Kroki diagram URL from diagram source text."""
    return f"{base.rstrip('/')}/{diagram_type}/{fmt}/{encode_for_kroki(code)}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print a Kroki URL for diagram source read from a file or stdin.",
    )
    parser.add_argument(
        "-t",
        "--diagram-type",
        default="plantuml",
        metavar="BACKEND",
        help="Kroki path segment (backend), e.g. plantuml, mermaid, d2 (default: plantuml)",
    )
    parser.add_argument(
        "-f",
        "--format",
        default="svg",
        help="Output format segment, e.g. svg, png, pdf (default: svg)",
    )
    parser.add_argument(
        "--base",
        default=DEFAULT_BASE,
        help=f"Kroki server base URL (default: $KROKI_URL or {DEFAULT_BASE})",
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="Path to diagram source; if omitted, read stdin",
    )
    args = parser.parse_args()

    if args.file:
        try:
            code = open(args.file, encoding="utf-8").read()
        except OSError as e:
            print(f"kroki_url: {args.file}: {e}", file=sys.stderr)
            return 1
    else:
        if sys.stdin.isatty():
            print(
                "kroki_url: provide a FILE or pipe diagram source on stdin",
                file=sys.stderr,
            )
            return 1
        code = sys.stdin.read()

    url = kroki_url(
        code,
        diagram_type=args.diagram_type.strip().lower(),
        fmt=args.format.strip().lower(),
        base=args.base,
    )
    print(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
