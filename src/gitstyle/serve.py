"""Local web viewer for gitstyle wikis — stdlib HTTP server, zero dependencies."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any
from urllib.parse import unquote


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Extract YAML frontmatter from markdown. Returns (metadata, body)."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("---", 3)
    if end == -1:
        return {}, text
    raw = text[3:end].strip()
    meta: dict[str, Any] = {}
    current_key: str | None = None
    current_list: list[str] | None = None
    for line in raw.splitlines():
        if line.startswith("  - ") and current_key and current_list is not None:
            current_list.append(line[4:].strip())
            continue
        if current_key and current_list is not None:
            meta[current_key] = current_list
            current_list = None
            current_key = None
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if val == "":
            current_key = key
            current_list = []
        else:
            # Handle inline YAML lists: [item1, item2]
            if val.startswith("[") and val.endswith("]"):
                items = [v.strip() for v in val[1:-1].split(",") if v.strip()]
                meta[key] = items
            else:
                # Try numeric
                # Strip surrounding quotes (YAML string delimiters)
                if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
                    val = val[1:-1]
                try:
                    meta[key] = float(val) if "." in val else int(val)
                except ValueError:
                    meta[key] = val
    if current_key and current_list is not None:
        meta[current_key] = current_list
    body = text[end + 3:].strip()
    return meta, body


_WIKILINK_RE = re.compile(r"\[\[([^\]|]+?)(?:\|[^\]]+?)?\]\]")


def _extract_wikilinks(text: str) -> list[str]:
    return _WIKILINK_RE.findall(text)


def _scan_wiki(wiki_dir: Path) -> list[dict[str, Any]]:
    """Scan wiki directory, return list of file metadata dicts."""
    files = []
    for md in sorted(wiki_dir.rglob("*.md")):
        rel = md.relative_to(wiki_dir).as_posix()
        text = md.read_text(encoding="utf-8")
        meta, body = _parse_frontmatter(text)
        files.append({
            "path": rel,
            "slug": md.stem,
            "meta": meta,
            "body": body,
            "wikilinks": _extract_wikilinks(text),
        })
    return files


def _build_graph(files: list[dict[str, Any]]) -> dict[str, Any]:
    """Build graph data from scanned files."""
    nodes = []
    edges = []
    slug_to_path: dict[str, str] = {}

    for f in files:
        slug_to_path[f["slug"]] = f["path"]
        # Also map path-without-extension
        path_no_ext = f["path"].removesuffix(".md")
        slug_to_path[path_no_ext] = f["path"]

    for f in files:
        cat = f["meta"].get("category", "meta")
        link_count = len(f["wikilinks"])
        # Also count incoming links
        for other in files:
            if f["path"] in other["wikilinks"] or f["slug"] in other["wikilinks"]:
                link_count += 1
        nodes.append({
            "id": f["path"],
            "slug": f["slug"],
            "title": f["meta"].get("title", f["slug"]),
            "category": cat,
            "confidence": f["meta"].get("confidence", 0),
            "links": link_count,
        })

        for link in f["wikilinks"]:
            target = slug_to_path.get(link)
            if not target:
                target = slug_to_path.get(link.removesuffix(".md"))
            if target and target != f["path"]:
                edges.append({"source": f["path"], "target": target})

        # Also add edges from `related` frontmatter
        related = f["meta"].get("related", [])
        if isinstance(related, list):
            for r in related:
                target = slug_to_path.get(r)
                if target and target != f["path"]:
                    edges.append({"source": f["path"], "target": target})

    # Deduplicate edges
    seen = set()
    unique_edges = []
    for e in edges:
        key = (e["source"], e["target"])
        rev = (e["target"], e["source"])
        if key not in seen and rev not in seen:
            seen.add(key)
            unique_edges.append(e)

    return {"nodes": nodes, "edges": unique_edges}


def _get_viewer_html() -> str:
    viewer_path = Path(__file__).parent / "viewer.html"
    return viewer_path.read_text(encoding="utf-8")


class WikiHandler(SimpleHTTPRequestHandler):
    wiki_dir: Path = Path("wiki")

    def log_message(self, format: str, *args: Any) -> None:
        # Suppress default logging noise
        pass

    def _send_json(self, data: Any, status: int = 200) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html: str, status: int = 200) -> None:
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = unquote(self.path)

        if path == "/api/files":
            files = _scan_wiki(self.wiki_dir)
            # Strip body from list response to keep it light
            result = []
            for f in files:
                result.append({
                    "path": f["path"],
                    "slug": f["slug"],
                    "meta": f["meta"],
                })
            self._send_json({
                "wiki_name": self.wiki_dir.resolve().name,
                "files": result,
            })
            return

        if path.startswith("/api/file/"):
            rel = path[len("/api/file/"):]
            file_path = self.wiki_dir / rel
            if not file_path.exists() or not file_path.is_file():
                self._send_json({"error": "not found"}, 404)
                return
            # Prevent path traversal
            try:
                file_path.resolve().relative_to(self.wiki_dir.resolve())
            except ValueError:
                self._send_json({"error": "forbidden"}, 403)
                return
            text = file_path.read_text(encoding="utf-8")
            meta, body = _parse_frontmatter(text)
            self._send_json({"path": rel, "meta": meta, "body": body})
            return

        if path == "/api/graph":
            files = _scan_wiki(self.wiki_dir)
            graph = _build_graph(files)
            self._send_json(graph)
            return

        # Default: serve viewer
        self._send_html(_get_viewer_html())


def start_server(wiki_dir: Path, port: int = 8080) -> HTTPServer:
    """Create and return an HTTPServer (does not start serving)."""
    WikiHandler.wiki_dir = wiki_dir.resolve()
    server = HTTPServer(("127.0.0.1", port), WikiHandler)
    return server
