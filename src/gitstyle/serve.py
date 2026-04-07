"""Local web viewer for gitstyle wikis."""

from __future__ import annotations

import json
import re
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any


def _parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return {}, content
    end = content.find("---", 3)
    if end == -1:
        return {}, content
    raw = content[3:end].strip()
    body = content[end + 3:].strip()
    meta: dict[str, Any] = {}
    for line in raw.split("\n"):
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip()
        # Parse simple YAML values
        if val.startswith("[") and val.endswith("]"):
            items = val[1:-1]
            meta[key] = [s.strip().strip('"').strip("'") for s in items.split(",") if s.strip()]
        elif val in ("true", "false"):
            meta[key] = val == "true"
        elif val.isdigit():
            meta[key] = int(val)
        else:
            meta[key] = val.strip('"').strip("'")
    return meta, body


def _extract_wikilinks(content: str) -> list[str]:
    """Extract [[wikilink]] targets from markdown content."""
    return re.findall(r"\[\[([^\]]+)\]\]", content)


def _slug_from_path(filepath: Path, wiki_dir: Path) -> str:
    """Convert a file path to a slug relative to wiki dir."""
    rel = filepath.relative_to(wiki_dir)
    return str(rel.with_suffix(""))


def _scan_wiki(wiki_dir: Path) -> dict[str, dict[str, Any]]:
    """Scan wiki directory and return file metadata keyed by slug."""
    files: dict[str, dict[str, Any]] = {}
    for md in sorted(wiki_dir.rglob("*.md")):
        slug = _slug_from_path(md, wiki_dir)
        content = md.read_text(encoding="utf-8")
        meta, body = _parse_frontmatter(content)
        wikilinks = _extract_wikilinks(content)
        related = meta.get("related", [])
        if isinstance(related, str):
            related = [related]
        files[slug] = {
            "slug": slug,
            "title": meta.get("title", slug),
            "category": meta.get("category", "other"),
            "confidence": meta.get("confidence"),
            "sources": meta.get("sources", []),
            "related": related,
            "wikilinks": wikilinks,
            "last_updated": meta.get("last_updated"),
        }
    return files


def _build_graph(files: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Build graph nodes and edges from wiki files."""
    nodes = []
    edges = []
    slugs = set(files.keys())
    edge_set: set[tuple[str, str]] = set()

    for slug, info in files.items():
        # Count links (wikilinks + related)
        link_targets = set(info["wikilinks"]) | set(info["related"])
        link_count = sum(1 for t in link_targets if t in slugs)
        nodes.append({
            "id": slug,
            "title": info["title"],
            "category": info["category"],
            "confidence": info["confidence"],
            "links": link_count,
        })
        # Edges from wikilinks
        for target in info["wikilinks"]:
            if target in slugs:
                pair = tuple(sorted([slug, target]))
                if pair not in edge_set:
                    edge_set.add(pair)
                    edges.append({"source": slug, "target": target})
        # Edges from related
        for target in info["related"]:
            if target in slugs:
                pair = tuple(sorted([slug, target]))
                if pair not in edge_set:
                    edge_set.add(pair)
                    edges.append({"source": slug, "target": target})

    return {"nodes": nodes, "edges": edges}


def _make_handler(wiki_dir: Path, template: str) -> type:
    """Create a request handler class with the wiki dir bound."""
    files_cache = _scan_wiki(wiki_dir)
    graph_cache = _build_graph(files_cache)

    class WikiHandler(SimpleHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            # Suppress default logging
            pass

        def _json_response(self, data: Any, status: int = 200) -> None:
            body = json.dumps(data).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _html_response(self, html: str) -> None:
            body = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            path = self.path.split("?")[0]

            if path == "/api/files":
                self._json_response(list(files_cache.values()))
            elif path == "/api/graph":
                self._json_response(graph_cache)
            elif path.startswith("/api/file/"):
                slug = path[len("/api/file/"):]
                filepath = wiki_dir / f"{slug}.md"
                if filepath.exists() and filepath.is_relative_to(wiki_dir):
                    content = filepath.read_text(encoding="utf-8")
                    meta = files_cache.get(slug, {})
                    self._json_response({"content": content, "meta": meta})
                else:
                    self._json_response({"error": "Not found"}, 404)
            else:
                # Serve the SPA for any other path
                self._html_response(template)

    return WikiHandler


def run_server(wiki_dir: Path, port: int = 8080, no_open: bool = False) -> None:
    """Start the wiki viewer server."""
    import webbrowser

    if not wiki_dir.exists():
        raise FileNotFoundError(f"Wiki directory not found: {wiki_dir}")
    if not list(wiki_dir.rglob("*.md")):
        raise FileNotFoundError(f"No markdown files found in {wiki_dir}")

    template_path = Path(__file__).parent / "templates" / "viewer.html"
    template = template_path.read_text(encoding="utf-8")

    handler_class = _make_handler(wiki_dir, template)
    server = HTTPServer(("127.0.0.1", port), handler_class)

    from rich.console import Console
    console = Console()
    url = f"http://localhost:{port}"
    console.print(f"\n[bold cyan]gitstyle viewer[/bold cyan]")
    console.print(f"  Serving [bold]{wiki_dir}[/bold] at [link={url}]{url}[/link]")
    console.print(f"  Press Ctrl+C to stop\n")

    if not no_open:
        webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        console.print("\n[dim]Stopped.[/dim]")
        server.server_close()
