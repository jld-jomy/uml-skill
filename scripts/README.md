# uml-skill scripts

Small **stdlib-only** helpers agents can run without installing uml-mcp. Both talk to a **local Kroki server in Docker** (`$KROKI_URL`, default `http://localhost:8090`), never the public kroki.io.

Start the server once:

```bash
docker start kroki 2>/dev/null || docker run -d --name kroki -p 8090:8000 yuzutech/kroki
```

## `kroki_render.py` (preferred)

POSTs diagram source to the local server and writes the rendered file.

```bash
python3 kroki_render.py -t plantuml diagram.puml          # -> diagram.svg
python3 kroki_render.py -t plantuml -f png diagram.puml   # -> diagram.png
python3 kroki_render.py -t mermaid -o out.svg diagram.mmd
cat diagram.puml | python3 kroki_render.py > diagram.svg
```

| Option | Meaning |
| --- | --- |
| `-t`, `--diagram-type` | Kroki backend (default: `plantuml`) |
| `-f`, `--format` | Output format (default: from `-o` extension, else `svg`) |
| `-o`, `--output` | Output file (default: input path with new extension; stdout for stdin) |
| `--base` | Kroki base URL (default: `$KROKI_URL` or `http://localhost:8090`) |

Exit codes: `0` ok (prints output path), `2` Kroki rejected the diagram (message on stderr), `3` server unreachable.

## `kroki_url.py`

Prints a **Kroki GET URL** for diagram source (zlib + base64url, same encoding as [Kroki](https://kroki.io/) expects).

**When to use:** you want a GET URL to open in a browser on this machine. The URL points at the local server, so it is not shareable; use `kroki_render.py` to get a file.

**When to prefer uml-mcp:** The server maps **logical** `diagram_type` keys, themes, PlantUML preparation, validation, and fallbacks. This script takes a Kroki **backend** name (`plantuml`, `mermaid`, `d2`, …) and **raw** source—no uml-mcp wrapping.

### uml-mcp logical type vs Kroki `-t` backend

| uml-mcp `diagram_type` (examples) | Typical Kroki `-t` for `kroki_url.py` |
| --- | --- |
| `class`, `sequence`, `activity`, `usecase`, … | `plantuml` (PlantUML body, often with `@startuml` … `@enduml`) |
| `mermaid` | `mermaid` |
| `d2` | `d2` |
| `bpmn` | `bpmn` |
| `c4plantuml` | `c4plantuml` |
| `wireviz` | `wireviz` |

When unsure, read **`uml://types`** in uml-mcp (each entry lists the **backend** segment Kroki uses).

### Usage

```bash
python kroki_url.py --help
```

From a file:

```bash
python kroki_url.py -t mermaid diagram.mmd
python kroki_url.py -t plantuml -f png diagram.puml
```

From stdin (PowerShell):

```powershell
Get-Content diagram.puml -Raw | python kroki_url.py -t plantuml
```

From stdin (Unix):

```bash
cat diagram.puml | python kroki_url.py -t plantuml
```

### Options

| Option | Meaning |
| --- | --- |
| `-t`, `--diagram-type` | Kroki backend path segment (default: `plantuml`) |
| `-f`, `--format` | Output format segment (default: `svg`) |
| `--base` | Kroki base URL (default: `$KROKI_URL` or `http://localhost:8090`) |

Positional `file` is optional; if omitted, diagram text is read from **stdin** (not from an interactive TTY).
