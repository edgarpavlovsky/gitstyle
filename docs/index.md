# gitstyle Documentation

**gitstyle** generates engineering style wikis from GitHub commit history. It analyzes how a developer or organization actually writes code — naming conventions, error handling patterns, testing philosophy, commit hygiene, preferred libraries — and packages those patterns into a portable markdown wiki.

The wiki is designed to be loaded as context by any coding agent (Claude Code, Cursor, Aider, etc.) so it can write code in your style from day one.

## How It Works

gitstyle runs a 6-stage pipeline:

```
GitHub API → Fetch → Sample → Extract (LLM) → Compile (LLM) → Lint (LLM) → Wiki
```

1. **Fetch** commits and diffs via the GitHub REST API
2. **Sample** representative commits by clustering across repos and languages
3. **Extract** style observations using an LLM (Claude) to analyze each cluster
4. **Compile** observations into coherent wiki articles per style dimension
5. **Lint** the wiki for contradictions, weak evidence, and quality issues
6. **Build** the final markdown files with YAML frontmatter and wikilinks

On subsequent runs, gitstyle operates **incrementally** — only fetching new commits and evolving existing articles rather than rebuilding from scratch.

## Documentation

| Page | Description |
|------|-------------|
| [Getting Started](getting-started.md) | Installation, prerequisites, and your first wiki |
| [The Pipeline](pipeline.md) | Deep dive into each of the 6 stages |
| [Incremental Synthesis](incremental.md) | How wikis evolve over time with new commits |
| [Web Viewer](web-viewer.md) | Interactive graph visualization with `gitstyle serve` |
| [Configuration](configuration.md) | All CLI options, environment variables, and flags |
| [Output Format](output-format.md) | Wiki structure, frontmatter schema, and wikilinks |
| [Agent Integration](agent-integration.md) | How to plug a gitstyle wiki into Claude Code, Cursor, or any agent |
| [Architecture](architecture.md) | Source code walkthrough for contributors |
| [FAQ](faq.md) | Common questions and troubleshooting |

## Quick Example

```bash
pip install gitstyle

export GITHUB_TOKEN=ghp_...
export ANTHROPIC_API_KEY=sk-ant-...

# Generate a wiki for any GitHub user or org
gitstyle run karpathy

# Browse it interactively
gitstyle serve
```

Output lands in `wiki/` — plain markdown files you can open in Obsidian, feed to a coding agent, or browse with the built-in web viewer.

## Links

- **GitHub**: [edgarpavlovsky/gitstyle](https://github.com/edgarpavlovsky/gitstyle)
- **Latest Release**: [v0.6.1](https://github.com/edgarpavlovsky/gitstyle/releases/tag/v0.6.1)
- **License**: MIT
