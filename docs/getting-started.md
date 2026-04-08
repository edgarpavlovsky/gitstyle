# Getting Started

## Prerequisites

- **Python 3.9+**
- **GitHub token** — for API rate limits (5,000 req/hr authenticated vs. 60 unauthenticated). Required for private repos. Generate one at [github.com/settings/tokens](https://github.com/settings/tokens) with `public_repo` scope.
- **Anthropic API key** — for the LLM stages (extract, compile, lint). Get one at [console.anthropic.com](https://console.anthropic.com).

## Installation

### From PyPI

```bash
pip install gitstyle
```

### From source (for development)

```bash
git clone https://github.com/edgarpavlovsky/gitstyle.git
cd gitstyle
pip install -e ".[dev]"
```

The `-e` flag installs in editable mode — changes to the source are immediately reflected without reinstalling.

## Set Up Credentials

```bash
export GITHUB_TOKEN=ghp_your_token_here
export ANTHROPIC_API_KEY=sk-ant-your_key_here
```

gitstyle validates both credentials before starting the pipeline. If either is missing or invalid, you'll get a clear error message immediately.

### Alternative: Anthropic OAuth

If you have an Anthropic OAuth token (from enterprise SSO or similar), you can use it instead:

```bash
export ANTHROPIC_AUTH_TOKEN=your_oauth_token
```

`ANTHROPIC_API_KEY` takes precedence if both are set.

## Generate Your First Wiki

### For an individual developer

```bash
gitstyle run karpathy
```

This fetches Andrej Karpathy's public commits, analyzes them with Claude, and outputs a wiki to `wiki/`.

### For a GitHub organization

```bash
gitstyle run anthropic
```

gitstyle auto-detects whether the name is a user or an organization and adjusts accordingly. For organizations, repos are sorted by stars and capped at 30 by default (configurable with `--max-commits`).

### For yourself

```bash
gitstyle run your-github-username
```

## Browse the Wiki

### In a text editor or Obsidian

The wiki is plain markdown with YAML frontmatter and `[[wikilinks]]`. Open `wiki/index.md` in any editor, or open the `wiki/` folder in Obsidian for full graph view and link navigation.

### With the built-in web viewer

```bash
gitstyle serve
```

This launches a local web server with an interactive force-directed graph. Click any node to read the article. See [Web Viewer](web-viewer.md) for details.

### Pre-built examples

If you want to see what a gitstyle wiki looks like without running the pipeline:

```bash
# Comes with four example wikis
gitstyle serve -w examples/karpathy     # ML researcher, Python/C
gitstyle serve -w examples/torvalds     # Kernel, C
gitstyle serve -w examples/anthropic    # AI company, multi-language
gitstyle serve -w examples/openai       # AI company, research + SDK
```

## What It Costs

A typical run (one developer, ~2000 commits) makes 15-30 LLM calls and costs roughly **$0.10-0.50** in Anthropic API usage. The default model is `claude-sonnet-4-20250514`.

Subsequent runs are cheaper thanks to [incremental synthesis](incremental.md) — only new commits are processed.

## Next Steps

- [The Pipeline](pipeline.md) — understand what each stage does
- [Configuration](configuration.md) — all available flags and options
- [Agent Integration](agent-integration.md) — plug the wiki into your coding workflow
