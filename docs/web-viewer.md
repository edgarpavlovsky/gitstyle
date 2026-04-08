# Web Viewer

gitstyle includes a built-in web viewer with an interactive force-directed knowledge graph. Launch it with `gitstyle serve`.

## Quick Start

```bash
# Serve the default wiki/ directory
gitstyle serve

# Serve a specific wiki
gitstyle serve -w examples/karpathy

# Custom port, don't auto-open browser
gitstyle serve --port 3000 --no-open
```

The viewer opens automatically in your default browser at `http://127.0.0.1:8080`.

## Features

### Force-Directed Graph

The main view is a full-bleed D3.js force-directed graph. Each node represents a wiki article, and edges represent cross-references (`[[wikilinks]]` and `related` frontmatter links).

- **Node size** scales with the number of connections (more cross-referenced articles are larger)
- **Node color** indicates category — style dimensions, languages, and meta articles each have distinct colors
- **Click** any node to open its article in the slide-over reader
- **Drag** nodes to rearrange the layout
- **Zoom and pan** with scroll/trackpad

### Floating Navigation

A glassmorphism-style floating sidebar shows all articles organized by category. Click any entry to navigate directly.

### Article Reader

The slide-over reader panel displays the full article content with rendered markdown. It shows the article's confidence score, source repos, and category.

## Architecture

The viewer is a single HTML file (`src/gitstyle/viewer.html`) built with:

- **Vue 3** (CDN) — reactive state management
- **Tailwind CSS** (CDN) — styling
- **D3.js** (CDN) — force-directed graph visualization

No build step required. The file is served directly by a Python stdlib HTTP server.

### API Endpoints

The built-in server exposes three JSON endpoints:

| Endpoint | Description |
|----------|-------------|
| `GET /api/files` | List all wiki articles with metadata (no body content) |
| `GET /api/file/{path}` | Get a single article's metadata and body |
| `GET /api/graph` | Get the full graph structure (nodes + edges) |

Any other path serves the viewer HTML.

### `/api/files` Response

```json
{
  "wiki_name": "karpathy",
  "files": [
    {
      "path": "naming-conventions.md",
      "slug": "naming-conventions",
      "meta": {
        "title": "Naming Conventions",
        "category": "dimension",
        "confidence": 0.82,
        "last_updated": "2026-04-07"
      }
    }
  ]
}
```

### `/api/graph` Response

```json
{
  "nodes": [
    {
      "id": "naming-conventions.md",
      "slug": "naming-conventions",
      "title": "Naming Conventions",
      "category": "dimension",
      "confidence": 0.82,
      "links": 5
    }
  ],
  "edges": [
    {
      "source": "naming-conventions.md",
      "target": "code-structure.md"
    }
  ]
}
```

## Server Details

- **Implementation**: Python `http.server.HTTPServer` with a custom `WikiHandler`
- **Binding**: `127.0.0.1` only (not exposed to the network)
- **Cache headers**: `Cache-Control: no-cache, no-store, must-revalidate` on HTML responses to prevent stale content during development
- **Path traversal protection**: File requests are validated against the wiki directory root
- **YAML frontmatter parsing**: Built-in parser (no PyYAML dependency), supports nested lists and inline arrays

## D3 Graph Physics

The force-directed graph uses these parameters for readable layouts:

- **Charge force**: -100 (high repulsion keeps nodes spread)
- **Link strength**: 0.3 (low, allows clusters to form without oscillation)
- **Center force**: Pulls the graph toward the viewport center

The combination of high charge repulsion with low link strength is the key insight — it creates natural clusters around connected articles without the graph collapsing or oscillating.

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--wiki-dir, -w` | `wiki/` | Wiki directory to serve |
| `--port, -p` | `8080` | Port to listen on |
| `--no-open` | `false` | Don't auto-open browser |
