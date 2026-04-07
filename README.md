# gitstyle

Generate a personal engineering style wiki from your GitHub commit history.

**gitstyle** ingests a developer's GitHub commits and compiles them into a portable markdown wiki that any coding agent (Claude Code, Cursor, Aider, etc.) can load as context to write code in that developer's style.

Inspired by [Karpathy's post on LLM Knowledge Bases](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — the idea that an LLM works best when it has a structured, personal knowledge base to draw from.

![gitstyle demo](demo/demo.gif)

## Why

Every developer has a style: naming conventions, error handling patterns, testing philosophy, commit hygiene, preferred libraries. When you bring a coding agent into your workflow, it starts from zero. **gitstyle** fixes that by mining your real commit history for patterns and packaging them as a wiki any agent can read.

The output is plain markdown — no tool lock-in, no proprietary format. It works with Obsidian for browsing, with any coding agent for context, or as standalone documentation of your engineering preferences.

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

- Python 3.10+
- A GitHub token for API rate limits: `export GITHUB_TOKEN=ghp_...`
- An Anthropic API key for LLM stages: `export ANTHROPIC_API_KEY=sk-ant-...`

## Quickstart

```bash
# Generate your engineering style wiki
gitstyle run edgarpavlovsky

# Output lands in wiki/ by default
ls wiki/
```

That's it. The tool runs a 5-stage pipeline:

1. **Fetch** — Pull commits + diffs via GitHub API
2. **Sample** — Cluster by repo/language, select representative commits
3. **Extract** — LLM analyzes each cluster for style patterns
4. **Compile** — LLM synthesizes observations into wiki articles
5. **Lint** — LLM health check for contradictions and weak evidence

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

### Sampling strategy

Not every commit goes through the LLM. gitstyle clusters commits by repo and language, then samples up to 20 per cluster using a **balanced** strategy:

- ~1/3 most recent commits (captures current style)
- ~1/3 largest diffs (captures substantive changes)
- ~1/3 random (captures breadth)

Configurable via `--strategy` (`balanced`, `recent`, `largest`) and `--max-samples`.

## How to Plug Into Your Coding Agent

### Claude Code

Add to your project's `CLAUDE.md`:

```markdown
## My Engineering Style

Load and follow the engineering style wiki in the `wiki/` directory for all code in this project.
Start with wiki/index.md for an overview, then reference individual articles for specific conventions.
```

Or pass the wiki as context directly:

```bash
# Add wiki directory to Claude Code context
claude --context wiki/
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

# Fetch only (useful for inspecting data before running full pipeline)
gitstyle fetch <username>

# Show version
gitstyle version
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--output, -o` | `wiki/` | Output directory |
| `--cache` | `.gitstyle/` | Cache directory |
| `--model, -m` | `claude-sonnet-4-20250514` | LLM model |
| `--forks` | `false` | Include forked repos |
| `--max-commits` | `200` | Max commits per repo |
| `--max-samples` | `20` | Max samples per cluster |
| `--since` | — | Start date (ISO 8601) |
| `--until` | — | End date (ISO 8601) |
| `--include-repos` | — | Comma-separated repos to include |
| `--exclude-repos` | — | Comma-separated repos to exclude |
| `--strategy` | `balanced` | Sampling: balanced, recent, largest |
| `--skip-lint` | `false` | Skip lint stage |

### Environment Variables

- `GITHUB_TOKEN` — GitHub personal access token (recommended for rate limits, required for private repos)
- `ANTHROPIC_API_KEY` — Anthropic API key for LLM stages

## Caching

gitstyle caches aggressively to avoid redundant API calls and LLM invocations:

- `.gitstyle/repos.jsonl` — Fetched repo metadata
- `.gitstyle/commits.jsonl` — Fetched commit summaries
- `.gitstyle/diffs/<sha>.json` — Individual commit diffs
- `.gitstyle/extractions/<cluster>.json` — LLM extraction results per cluster
- `.gitstyle/articles/<slug>.json` — Compiled article data

Delete `.gitstyle/` to start fresh, or delete individual cache files to re-run specific stages.

## Examples

See the `examples/` directory for complete wiki outputs:

- [`examples/edgarpavlovsky/`](examples/edgarpavlovsky/) — The author's engineering style wiki
- [`examples/torvalds/`](examples/torvalds/) — Linus Torvalds' kernel C style

## Development

```bash
git clone https://github.com/edgarpavlovsky/gitstyle.git
cd gitstyle
pip install -e ".[dev]"
pytest
```

## License

[MIT](LICENSE)
