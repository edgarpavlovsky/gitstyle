# Configuration

gitstyle is configured entirely through CLI flags and environment variables. There is no config file.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_TOKEN` | Yes* | GitHub personal access token. Required for reasonable rate limits (5,000 req/hr vs 60 unauthenticated) and for private repos. Can also be passed via `--token`. |
| `ANTHROPIC_API_KEY` | Yes** | Anthropic API key for LLM stages. Get one at [console.anthropic.com](https://console.anthropic.com). |
| `ANTHROPIC_AUTH_TOKEN` | No | Alternative to `ANTHROPIC_API_KEY` — Anthropic OAuth token for enterprise SSO. `ANTHROPIC_API_KEY` takes precedence if both are set. |

\* Can be passed via `--token` flag instead.
\** Not required for `--dry-run` mode.

## `gitstyle run` Options

The main command. Runs the full pipeline: fetch, sample, extract, compile, lint, build.

```bash
gitstyle run <username> [options]
```

| Flag | Default | Description |
|------|---------|-------------|
| `<username>` | (required) | GitHub username or organization name. gitstyle auto-detects which. |
| `--output, -o` | `wiki/` | Output directory for the generated wiki. |
| `--cache` | `.gitstyle/` | Directory for intermediate cache files. |
| `--max-commits, -n` | `2000` | Maximum total commits to fetch across all repos. Spread evenly across repos. |
| `--samples, -s` | `20` | Maximum commits sampled per `(repo, language)` cluster. Higher values = more evidence per article but more LLM tokens. |
| `--repos, -r` | all | Comma-separated repo filter. Format: `owner/name`. Only analyze these specific repos. |
| `--since` | none | Only include commits after this date. ISO 8601 format (e.g., `2024-01-01`). |
| `--until` | none | Only include commits before this date. ISO 8601 format. |
| `--model, -m` | `claude-sonnet-4-20250514` | Anthropic model ID for LLM stages. Must be a valid Anthropic model. |
| `--token, -t` | `$GITHUB_TOKEN` | GitHub personal access token. Overrides the environment variable. |
| `--dry-run` | `false` | Run fetch and sample stages only — skip all LLM calls. Useful for estimating costs. |
| `--fresh` | `false` | Force a full pipeline run, ignoring all cached data. Without this, subsequent runs are incremental. |

### Examples

```bash
# Basic run
gitstyle run karpathy

# Analyze only specific repos
gitstyle run karpathy --repos karpathy/nanoGPT,karpathy/micrograd

# Limit to commits from 2024 onwards
gitstyle run karpathy --since 2024-01-01

# Use a faster/cheaper model
gitstyle run karpathy --model claude-haiku-4-5-20251001

# More samples per cluster (richer articles, higher cost)
gitstyle run karpathy --samples 40

# Force full rebuild
gitstyle run karpathy --fresh

# Check what would happen without LLM calls
gitstyle run karpathy --dry-run
```

## `gitstyle serve` Options

Launch the local web viewer.

```bash
gitstyle serve [options]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--wiki-dir, -w` | `wiki/` | Wiki directory to serve. |
| `--port, -p` | `8080` | Port to listen on. |
| `--no-open` | `false` | Don't auto-open browser. |

### Examples

```bash
# Serve default wiki
gitstyle serve

# Serve an example wiki on a custom port
gitstyle serve -w examples/anthropics --port 3000

# Serve without opening browser (e.g., in a remote session)
gitstyle serve --no-open
```

## `gitstyle clean` Options

Remove cached intermediate files.

```bash
gitstyle clean [options]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--cache` | `.gitstyle/` | Cache directory to remove. |

## Individual Stage Commands

Run a single pipeline stage (requires cached data from prior stages):

```bash
gitstyle fetch-cmd <username> [--cache DIR] [--max-commits N] [--repos LIST] [--since DATE] [--until DATE] [--token TOKEN] [--fresh]
gitstyle sample-cmd <username> [--cache DIR] [--samples N]
gitstyle extract-cmd <username> [--cache DIR] [--model MODEL] [--dry-run]
gitstyle compile-cmd <username> [--cache DIR] [--output DIR] [--model MODEL] [--dry-run]
gitstyle lint-cmd <username> [--cache DIR] [--model MODEL] [--dry-run]
```

These are useful for:
- Re-running a single expensive stage with different parameters
- Debugging pipeline issues at a specific stage
- Manually controlling the pipeline flow

## `gitstyle --version`

Print the installed version and exit.

```bash
$ gitstyle --version
gitstyle 0.6.1
```

## LLM Model Selection

gitstyle currently supports Anthropic models only. The model is passed directly to the Anthropic SDK's `messages.create()` API.

Recommended models:

| Model | Speed | Cost | Quality | Best for |
|-------|-------|------|---------|----------|
| `claude-sonnet-4-20250514` | Medium | Medium | High | Default, good balance |
| `claude-haiku-4-5-20251001` | Fast | Low | Good | Quick/cheap runs, iteration |
| `claude-opus-4-6` | Slow | High | Highest | Maximum quality analysis |

The model is used for all three LLM stages (extract, compile, lint). There's currently no way to use different models for different stages.
