# gitstyle

Generate a personal engineering style wiki from your GitHub commit history.

**gitstyle** ingests a developer's or organization's GitHub commits and compiles them into a portable markdown wiki that any coding agent (Claude Code, Cursor, Aider, etc.) can load as context to write code in that style.

Inspired by [Karpathy's post on LLM Knowledge Bases](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — the idea that an LLM works best when it has a structured, personal knowledge base to draw from.

![gitstyle demo](demo/demo.gif)

## Why

Every developer and engineering org has a style: naming conventions, error handling patterns, testing philosophy, commit hygiene, preferred libraries. When you bring a coding agent into your workflow, it starts from zero. **gitstyle** fixes that by mining real commit history for patterns and packaging them as a wiki any agent can read.

Works for individual developers and GitHub organizations — gitstyle auto-detects which and adjusts its analysis accordingly.

The output is plain markdown — no tool lock-in, no proprietary format. Browse it with the built-in web viewer (`gitstyle serve`), Obsidian, any coding agent, or as standalone documentation of your engineering preferences.

## Install

```bash
pip install gitstyle
```

Or from source:

```bash
git clone https://github.com/edgarpavlovsky/gitstyle.git
cd gitstyle
pip install -e .
```

### Requirements

- Python 3.9+
- A GitHub token for API rate limits: `export GITHUB_TOKEN=ghp_...`
- An Anthropic API key for LLM stages: `export ANTHROPIC_API_KEY=sk-ant-...`

## Quickstart

```bash
# Generate a developer's engineering style wiki
gitstyle run karpathy

# Or generate an org's engineering patterns wiki
gitstyle run anthropic

# Output lands in wiki/ by default
ls wiki/
```

That's it. The tool runs a 5-stage pipeline:

1. **Fetch** — Pull commits + diffs via GitHub API
2. **Sample** — Cluster by repo/language, select representative commits
3. **Extract** — LLM analyzes each cluster for style patterns
4. **Compile** — LLM synthesizes observations into wiki articles
5. **Lint** — LLM health check for contradictions and weak evidence

### Incremental Updates

Re-run `gitstyle run` at any time — the wiki **evolves** with new commits:

```bash
# First run: full analysis
gitstyle run karpathy

# Later: only fetches new commits, evolves existing articles
gitstyle run karpathy

# Force a full rebuild from scratch
gitstyle run karpathy --fresh
```

The incremental pipeline only fetches commits since the last run, extracts observations from new data only, and uses the LLM to evolve existing articles (preserving valid insights, incorporating new patterns, noting contradictions). This saves API calls, LLM costs, and time.

## Output Format

gitstyle produces a directory of markdown files with YAML frontmatter, designed to be Obsidian-compatible and agent-readable:

```
wiki/
  index.md                    # Master index with links to all articles
  code-structure.md           # File/folder organization, module boundaries
  naming-conventions.md       # Variable, function, file naming patterns
  patterns.md                 # Error handling, async, state management
  type-discipline.md          # Typing style and strictness
  testing.md                  # Test structure, coverage philosophy
  comments-and-docs.md        # Documentation density and style
  dependencies.md             # Preferred libraries and tools
  commit-hygiene.md           # Commit message style, branching patterns
  languages/
    python.md                 # Python-specific idioms
    typescript.md             # TypeScript-specific idioms
    ...
  _meta/
    sources.md                # Repos and commit counts analyzed
    generation-config.md      # Pipeline configuration used
    log.md                    # Generation log
```

### Article format

Each article has YAML frontmatter:

```yaml
---
title: "Naming Conventions"
category: style
confidence: high
sources: [user/repo-a, user/repo-b]
related: [code-structure, patterns]
last_updated: 2026-04-07
---
```

Cross-references use `[[wikilinks]]` (Obsidian-compatible). Every claim cites specific commits by SHA.

## Web Viewer

gitstyle includes a built-in web viewer with an interactive knowledge graph:

```bash
# Launch the viewer (opens browser automatically)
gitstyle serve

# Serve a specific wiki directory
gitstyle serve -w examples/karpathy

# Custom port, no auto-open
gitstyle serve -w wiki/ --port 3000 --no-open
```

The viewer features a full-bleed force-directed graph with floating navigation and a slide-over article reader. Click any node to read the article. Built with Vue 3 + Tailwind CSS.

## How to Plug Into Your Coding Agent

### Claude Code

Add to your project's `CLAUDE.md`:

```markdown
## My Engineering Style

Load and follow the engineering style wiki in the `wiki/` directory for all code in this project.
Start with wiki/index.md for an overview, then reference individual articles for specific conventions.
```

### Cursor

Add to `.cursorrules` in your project root:

```
When writing code for this project, follow the engineering style conventions
documented in the wiki/ directory:

- wiki/naming-conventions.md for naming patterns
- wiki/patterns.md for error handling and architecture patterns
- wiki/testing.md for test structure and conventions
- wiki/code-structure.md for file organization

Every article includes specific examples from real commits. Follow these patterns.
```

### Any Agent (generic pattern)

Include the wiki contents in your agent's system prompt or context window:

```python
from pathlib import Path

# Load the full wiki as context
wiki_dir = Path("wiki")
style_context = ""
for md_file in sorted(wiki_dir.rglob("*.md")):
    style_context += f"\n\n--- {md_file.relative_to(wiki_dir)} ---\n"
    style_context += md_file.read_text()

# Feed to your agent's system prompt
system_prompt = f"""You are writing code for a developer with specific engineering preferences.
Their style guide:

{style_context}

Follow these conventions when writing or reviewing code."""
```

## CLI Reference

```bash
# Full pipeline
gitstyle run <username> [options]

# Individual stages (each requires cached data from prior stages)
gitstyle fetch-cmd <username>
gitstyle sample-cmd <username>
gitstyle extract-cmd <username>
gitstyle compile-cmd <username>
gitstyle lint-cmd <username>

# Launch web viewer with interactive graph
gitstyle serve [-w wiki_dir]

# Clean cached data
gitstyle clean

# Show version
gitstyle --version
```

### Options for `run`

| Flag | Default | Description |
|------|---------|-------------|
| `--output, -o` | `wiki/` | Output directory |
| `--cache` | `.gitstyle/` | Cache directory |
| `--max-commits, -n` | `2000` | Max commits to fetch |
| `--samples, -s` | `20` | Samples per repo/language group |
| `--repos, -r` | all | Comma-separated repo filter (`owner/name`) |
| `--since` | — | Start date (ISO 8601) |
| `--until` | — | End date (ISO 8601) |
| `--model, -m` | `claude-sonnet-4-20250514` | LLM model |
| `--token, -t` | `$GITHUB_TOKEN` | GitHub token |
| `--dry-run` | `false` | Show what would happen without LLM calls |
| `--fresh` | `false` | Force full rebuild, ignoring cache |

### Options for `serve`

| Flag | Default | Description |
|------|---------|-------------|
| `--wiki-dir, -w` | `wiki/` | Wiki directory to serve |
| `--port, -p` | `8080` | Port to listen on |
| `--no-open` | `false` | Don't auto-open browser |

### Environment Variables

| Variable | Description |
|----------|-------------|
| `GITHUB_TOKEN` | GitHub personal access token (recommended for rate limits, required for private repos) |
| `ANTHROPIC_API_KEY` | Anthropic API key for LLM stages |
| `ANTHROPIC_AUTH_TOKEN` | Alternative: Anthropic OAuth token |

If no API credentials are set, gitstyle will show a clear error before starting the pipeline.

## Caching & Incremental Runs

gitstyle caches intermediate data in `.gitstyle/`:

```
.gitstyle/
  commits.jsonl       # Fetched commit data
  samples.json        # Sampled clusters
  extractions.json    # LLM extraction results
  articles.json       # Compiled article data
  lint.json           # Lint report
```

When you re-run `gitstyle run`, it automatically detects cached data and runs incrementally — only fetching new commits and evolving existing articles. This means your wiki grows richer over time without redundant API calls or LLM costs.

- `gitstyle run <user>` — incremental (default when cache exists)
- `gitstyle run <user> --fresh` — full rebuild from scratch
- `gitstyle clean` — delete all cached data

## Examples

See the `examples/` directory for complete wiki outputs:

### Individual developers
- [`examples/karpathy/`](examples/karpathy/) — Andrej Karpathy's Python + C style (nanoGPT, llm.c, micrograd)
- [`examples/torvalds/`](examples/torvalds/) — Linus Torvalds' kernel C style

### Organizations
- [`examples/anthropic/`](examples/anthropic/) — Anthropic's SDK and developer tools patterns (anthropic-sdk-python, anthropic-cookbook, claude-code)
- [`examples/openai/`](examples/openai/) — OpenAI's SDK + research code patterns (openai-python, tiktoken, whisper, CLIP)

## Development

```bash
git clone https://github.com/edgarpavlovsky/gitstyle.git
cd gitstyle
pip install -e ".[dev]"
pytest
```

## License

[MIT](LICENSE)
