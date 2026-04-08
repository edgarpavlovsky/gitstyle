"""Tests for the serve module — HTTP server + frontmatter parsing + graph building."""

from __future__ import annotations

import json
import threading
from http.client import HTTPConnection
from pathlib import Path
from textwrap import dedent

import pytest

from gitstyle.serve import (
    _build_graph,
    _extract_wikilinks,
    _parse_frontmatter,
    _scan_wiki,
    start_server,
)


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------

def test_parse_frontmatter_basic():
    text = dedent("""\
        ---
        title: Code Structure
        category: dimension
        confidence: 0.85
        last_updated: 2026-04-07
        ---

        # Code Structure

        Some content here.
    """)
    meta, body = _parse_frontmatter(text)
    assert meta["title"] == "Code Structure"
    assert meta["category"] == "dimension"
    assert meta["confidence"] == 0.85
    assert body.startswith("# Code Structure")


def test_parse_frontmatter_with_list():
    text = dedent("""\
        ---
        title: Python
        source_repos:
          - karpathy/nanoGPT
          - karpathy/micrograd
        confidence: 0.9
        ---

        Body text.
    """)
    meta, body = _parse_frontmatter(text)
    assert meta["source_repos"] == ["karpathy/nanoGPT", "karpathy/micrograd"]
    assert meta["confidence"] == 0.9
    assert body == "Body text."


def test_parse_frontmatter_missing():
    text = "# Just markdown\n\nNo frontmatter here."
    meta, body = _parse_frontmatter(text)
    assert meta == {}
    assert body == text


def test_parse_frontmatter_integer():
    text = "---\ncount: 42\n---\nBody"
    meta, body = _parse_frontmatter(text)
    assert meta["count"] == 42
    assert isinstance(meta["count"], int)


# ---------------------------------------------------------------------------
# Wikilink extraction
# ---------------------------------------------------------------------------

def test_extract_wikilinks_simple():
    text = "See [[code-structure]] and [[naming-conventions|Naming]]."
    links = _extract_wikilinks(text)
    assert links == ["code-structure", "naming-conventions"]


def test_extract_wikilinks_none():
    assert _extract_wikilinks("No links here.") == []


def test_extract_wikilinks_nested_path():
    text = "Check [[languages/python|Python]] and [[_meta/sources]]."
    links = _extract_wikilinks(text)
    assert "languages/python" in links
    assert "_meta/sources" in links


# ---------------------------------------------------------------------------
# Wiki scanning
# ---------------------------------------------------------------------------

def test_scan_wiki(tmp_path: Path):
    (tmp_path / "index.md").write_text(
        "---\ntitle: Index\ncategory: index\n---\n\n# Index\n\n- [[code-structure]]\n"
    )
    (tmp_path / "code-structure.md").write_text(
        "---\ntitle: Code Structure\ncategory: dimension\nconfidence: 0.8\n---\n\n# Code Structure\n"
    )
    (tmp_path / "languages").mkdir()
    (tmp_path / "languages" / "python.md").write_text(
        "---\ntitle: Python\ncategory: language\nconfidence: 0.9\n---\n\nPython content.\n"
    )

    files = _scan_wiki(tmp_path)
    assert len(files) == 3
    paths = [f["path"] for f in files]
    assert "index.md" in paths
    assert "code-structure.md" in paths
    assert "languages/python.md" in paths


# ---------------------------------------------------------------------------
# Graph building
# ---------------------------------------------------------------------------

def test_build_graph_basic():
    files = [
        {
            "path": "index.md",
            "slug": "index",
            "meta": {"title": "Index", "category": "index"},
            "body": "",
            "wikilinks": ["code-structure"],
        },
        {
            "path": "code-structure.md",
            "slug": "code-structure",
            "meta": {"title": "Code Structure", "category": "dimension", "confidence": 0.8},
            "body": "",
            "wikilinks": [],
        },
    ]
    graph = _build_graph(files)
    assert len(graph["nodes"]) == 2
    assert len(graph["edges"]) == 1
    assert graph["edges"][0]["source"] == "index.md"
    assert graph["edges"][0]["target"] == "code-structure.md"


def test_build_graph_deduplicates_edges():
    files = [
        {
            "path": "a.md",
            "slug": "a",
            "meta": {"title": "A", "category": "dimension"},
            "body": "",
            "wikilinks": ["b"],
        },
        {
            "path": "b.md",
            "slug": "b",
            "meta": {"title": "B", "category": "dimension"},
            "body": "",
            "wikilinks": ["a"],
        },
    ]
    graph = _build_graph(files)
    # Bidirectional links should deduplicate to 1 edge
    assert len(graph["edges"]) == 1


def test_build_graph_related_frontmatter():
    files = [
        {
            "path": "a.md",
            "slug": "a",
            "meta": {"title": "A", "category": "dimension", "related": ["b"]},
            "body": "",
            "wikilinks": [],
        },
        {
            "path": "b.md",
            "slug": "b",
            "meta": {"title": "B", "category": "dimension"},
            "body": "",
            "wikilinks": [],
        },
    ]
    graph = _build_graph(files)
    assert len(graph["edges"]) == 1


def test_build_graph_node_categories():
    files = [
        {"path": "index.md", "slug": "index", "meta": {"category": "index"}, "body": "", "wikilinks": []},
        {"path": "x.md", "slug": "x", "meta": {"category": "dimension"}, "body": "", "wikilinks": []},
        {"path": "languages/py.md", "slug": "py", "meta": {"category": "language"}, "body": "", "wikilinks": []},
        {"path": "_meta/log.md", "slug": "log", "meta": {"category": "meta"}, "body": "", "wikilinks": []},
    ]
    graph = _build_graph(files)
    cats = {n["slug"]: n["category"] for n in graph["nodes"]}
    assert cats == {"index": "index", "x": "dimension", "py": "language", "log": "meta"}


# ---------------------------------------------------------------------------
# HTTP server integration
# ---------------------------------------------------------------------------

@pytest.fixture()
def wiki_server(tmp_path: Path):
    """Start a server on a random port, yield (connection, port), then shut down."""
    (tmp_path / "index.md").write_text(
        "---\ntitle: Index\ncategory: index\n---\n\n# Index\n\n- [[code-structure]]\n"
    )
    (tmp_path / "code-structure.md").write_text(
        "---\ntitle: Code Structure\ncategory: dimension\nconfidence: 0.85\n---\n\n# Code Structure\n\nContent.\n"
    )
    (tmp_path / "languages").mkdir()
    (tmp_path / "languages" / "python.md").write_text(
        "---\ntitle: Python\ncategory: language\nconfidence: 0.9\n---\n\n# Python\n"
    )

    server = start_server(tmp_path, port=0)  # port 0 = OS picks a free port
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield HTTPConnection("127.0.0.1", port), port
    server.shutdown()
    server.server_close()


def test_api_files(wiki_server):
    conn, _ = wiki_server
    conn.request("GET", "/api/files")
    resp = conn.getresponse()
    assert resp.status == 200
    data = json.loads(resp.read())
    assert isinstance(data, dict)
    assert "wiki_name" in data
    assert "files" in data
    file_list = data["files"]
    assert len(file_list) == 3
    paths = [f["path"] for f in file_list]
    assert "index.md" in paths


def test_api_file(wiki_server):
    conn, _ = wiki_server
    conn.request("GET", "/api/file/code-structure.md")
    resp = conn.getresponse()
    assert resp.status == 200
    data = json.loads(resp.read())
    assert data["meta"]["title"] == "Code Structure"
    assert data["meta"]["confidence"] == 0.85
    assert "Content." in data["body"]


def test_api_file_not_found(wiki_server):
    conn, _ = wiki_server
    conn.request("GET", "/api/file/nonexistent.md")
    resp = conn.getresponse()
    assert resp.status == 404


def test_api_file_path_traversal(wiki_server):
    conn, _ = wiki_server
    conn.request("GET", "/api/file/../../etc/passwd")
    resp = conn.getresponse()
    assert resp.status in (403, 404)


def test_api_graph(wiki_server):
    conn, _ = wiki_server
    conn.request("GET", "/api/graph")
    resp = conn.getresponse()
    assert resp.status == 200
    data = json.loads(resp.read())
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) == 3
    # index.md links to code-structure.md
    assert any(
        e["source"] == "index.md" and e["target"] == "code-structure.md"
        for e in data["edges"]
    )


def test_root_serves_html(wiki_server):
    conn, _ = wiki_server
    conn.request("GET", "/")
    resp = conn.getresponse()
    assert resp.status == 200
    body = resp.read().decode()
    assert "<!DOCTYPE html>" in body
    assert "gitstyle" in body


def test_api_file_nested(wiki_server):
    conn, _ = wiki_server
    conn.request("GET", "/api/file/languages/python.md")
    resp = conn.getresponse()
    assert resp.status == 200
    data = json.loads(resp.read())
    assert data["meta"]["title"] == "Python"
    assert data["meta"]["category"] == "language"


# ---------------------------------------------------------------------------
# CLI integration
# ---------------------------------------------------------------------------

def test_cli_serve_missing_dir():
    from typer.testing import CliRunner
    from gitstyle.cli import app

    runner = CliRunner()
    result = runner.invoke(app, ["serve", "--wiki-dir", "/tmp/nonexistent_gitstyle_wiki_dir"])
    assert result.exit_code == 1
    assert "not found" in result.stdout
