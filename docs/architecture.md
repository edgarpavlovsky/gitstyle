# Architecture

This page describes the source code structure for contributors and anyone who wants to understand how gitstyle works under the hood.

## Project Layout

```
gitstyle/
  src/gitstyle/
    __init__.py          # Version string
    cli.py               # Typer CLI, pipeline orchestration
    config.py            # GitStyleConfig (Pydantic model)
    models.py            # All data models (Pydantic)
    fetch.py             # Stage 1: GitHub API → raw commits
    sample.py            # Stage 2: Clustering + sampling
    extract.py           # Stage 3: LLM extraction → observations
    compile.py           # Stage 4: LLM compilation → wiki articles
    lint.py              # Stage 5: LLM quality check
    wiki_writer.py       # Stage 6: Articles → markdown files
    github_client.py     # GitHub REST API client (httpx)
    llm_client.py        # Anthropic SDK wrapper
    serve.py             # HTTP server + viewer API
    viewer.html          # Vue 3 + Tailwind web viewer (single file)
  tests/
    test_cli.py          # CLI integration tests
    test_pipeline.py     # Pipeline stage tests
    test_incremental.py  # Incremental synthesis tests
    test_v032_qa.py      # Regression tests
  docs/                  # This documentation
  examples/              # Pre-built example wikis
    karpathy/
    torvalds/
    anthropic/
    openai/
  pyproject.toml         # Package metadata + dependencies
  README.md
```

## Key Abstractions

### `GitStyleConfig` (`config.py`)

A Pydantic `BaseModel` that holds all pipeline configuration. Created once from CLI arguments and threaded through every stage.

```python
class GitStyleConfig(BaseModel):
    username: str
    github_token: Optional[str]
    output_dir: Path        # default: wiki/
    cache_dir: Path         # default: .gitstyle/
    max_commits: int        # default: 2000
    samples_per_group: int  # default: 20
    repos: Optional[list[str]]
    since: Optional[str]
    until: Optional[str]
    llm_model: str          # default: claude-sonnet-4-20250514
    dry_run: bool
    fresh: bool
```

Provides helper methods for cache file paths: `commits_path()`, `samples_path()`, `extractions_path()`, `articles_path()`, `lint_path()`.

### Data Models (`models.py`)

All pipeline data flows through Pydantic models:

```
RawCommit → SampledCluster → ClusterExtraction (with Observations) → WikiArticle → LintReport
```

| Model | Stage | Purpose |
|-------|-------|---------|
| `CommitFile` | Fetch | Single file in a commit (filename, status, patch) |
| `RawCommit` | Fetch | Full commit with metadata, stats, files, languages |
| `SampledCluster` | Sample | Group of sampled commits for one (repo, language) pair |
| `Observation` | Extract | Single style observation with dimension, claim, evidence, confidence |
| `ClusterExtraction` | Extract | All observations from one cluster |
| `WikiArticle` | Compile | One wiki article (slug, title, category, confidence, content, wikilinks) |
| `LintIssue` | Lint | One quality issue (article, severity, message, suggestion) |
| `LintReport` | Lint | Collection of issues + passed boolean |
| `FetchResult` | Fetch | Wraps all_commits + new_commits + is_incremental flag |

### `StyleDimension` enum

The 9 style dimensions are defined as an enum:

```python
class StyleDimension(str, Enum):
    CODE_STRUCTURE = "code-structure"
    NAMING = "naming-conventions"
    PATTERNS = "patterns"
    TYPE_DISCIPLINE = "type-discipline"
    TESTING = "testing"
    COMMENTS_DOCS = "comments-and-docs"
    DEPENDENCIES = "dependencies"
    COMMIT_HYGIENE = "commit-hygiene"
    LANGUAGE_IDIOMS = "language-idioms"
```

This enum is used to categorize observations, compile dimension articles, and route the evolution logic.

## Pipeline Orchestration (`cli.py`)

The `run` command creates a `GitStyleConfig`, validates credentials, then calls `_run_pipeline()`.

`_run_pipeline()` decides between two code paths:

1. **`_run_full_pipeline()`** — Used for fresh runs (no cache, or `--fresh` flag). Calls each stage sequentially: `fetch → sample → extract → compile_wiki → lint → write_wiki`.

2. **`_run_incremental_pipeline()`** — Used when cache exists and there are new commits. Calls: `fetch (incremental) → sample (new only, no cache) → extract (new only, no cache) → evolve_wiki → lint → write_wiki`.

The decision logic:

```python
is_incremental = (
    fetch_result.is_incremental
    and has_new_commits
    and has_existing_articles
    and not config.fresh
)
```

## GitHub Client (`github_client.py`)

Thin wrapper around `httpx.Client` for the GitHub REST API.

Key features:
- **Automatic rate limit handling**: Detects 403 rate limit responses, reads `X-RateLimit-Reset` header, and sleeps until reset
- **Pagination**: All list endpoints paginate automatically (100 per page)
- **Fork filtering**: `list_repos()` skips forked repositories
- **Error handling**: 409 (empty repo) is caught and skipped gracefully

The client uses `Bearer` token authentication and sets `Accept: application/vnd.github+json`.

## LLM Client (`llm_client.py`)

Minimal wrapper around the Anthropic Python SDK.

```python
class LLMClient:
    def complete(system, prompt, max_tokens=8192, temperature=0.3) -> str
    def complete_json(system, prompt, max_tokens=8192, temperature=0.2) -> dict
```

`complete_json()` calls `complete()`, then strips markdown code fences if present and parses the result as JSON. This handles the common case where Claude wraps JSON output in ` ```json ` blocks.

Authentication precedence: `ANTHROPIC_API_KEY` > `ANTHROPIC_AUTH_TOKEN` > error.

## Web Viewer (`serve.py` + `viewer.html`)

The server is a stdlib `HTTPServer` with a custom `WikiHandler` that serves:
- `/api/files` — wiki file listing
- `/api/file/{path}` — individual article content
- `/api/graph` — node/edge graph data
- Everything else — the viewer HTML

The viewer HTML is a single file using Vue 3 + Tailwind CSS + D3.js, all loaded from CDN. State management is entirely in Vue's reactivity system. The D3 force simulation runs independently with parameters tuned for readable graph layouts.

### Graph construction (`_build_graph`)

1. Scan all `.md` files in the wiki directory
2. Parse YAML frontmatter and extract `[[wikilinks]]` via regex
3. Build a slug-to-path mapping for link resolution
4. Create nodes (one per file) with metadata (title, category, confidence, link count)
5. Create edges from wikilinks and `related` frontmatter fields
6. Deduplicate edges (A→B and B→A collapse to one undirected edge)

## Caching Strategy

Each stage follows the same pattern:

```python
def stage(input, config, use_cache=True):
    cache = config.stage_path()

    if use_cache and cache.exists():
        return load_from_cache(cache)

    # ... do work ...

    if results and use_cache:  # Never cache empty results
        save_to_cache(cache, results)

    return results
```

The `use_cache=False` parameter is used in the incremental pipeline for stages that process only new data (sample and extract) — their output is a delta, not a complete result.

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `typer` | >=0.9.0 | CLI framework |
| `httpx` | >=0.25.0 | HTTP client for GitHub API |
| `anthropic` | >=0.39.0 | Anthropic SDK for LLM calls |
| `pydantic` | >=2.0.0 | Data validation and serialization |
| `rich` | >=13.0.0 | Terminal formatting, progress bars |

Dev dependencies: `pytest`, `pytest-asyncio`, `respx` (HTTP mocking).

The web viewer has zero server-side dependencies beyond Python stdlib. Client-side dependencies (Vue, Tailwind, D3) are loaded from CDN.

## Testing

Tests live in `tests/` and use pytest. The test suite covers:

- **CLI tests** (`test_cli.py`): Version output, help text, pipeline execution with mocked LLM/GitHub calls
- **Pipeline tests** (`test_pipeline.py`): Each stage individually, sampling logic, extraction parsing, compilation, lint
- **Incremental tests** (`test_incremental.py`): Fetch deduplication, merge logic, evolution prompts, pipeline routing, cache invalidation
- **QA regression tests** (`test_v032_qa.py`): Version consistency across all files, viewer HTML assertions

Run tests:

```bash
pytest                    # All tests
pytest tests/test_cli.py  # Just CLI tests
pytest -x                 # Stop on first failure
pytest -v                 # Verbose output
```

Current test count: **205 tests** (all passing as of v0.6.1).

## Adding a New Style Dimension

1. Add the enum value to `StyleDimension` in `models.py`
2. Update the `EXTRACT_SYSTEM` prompt in `extract.py` to include it in the numbered list
3. The rest of the pipeline handles it automatically — compile will create an article for it, lint will check it, and the writer will output it

## Adding a New LLM Provider

The LLM integration is isolated in `llm_client.py`. To add a new provider:

1. Detect the provider from the model name or add a `--provider` flag
2. Add an alternative SDK client path in `LLMClient.__init__()`
3. The `complete()` and `complete_json()` interfaces stay the same — all prompts are provider-agnostic (plain system + user messages)
