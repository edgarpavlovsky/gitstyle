# The Pipeline

gitstyle transforms raw GitHub commits into a structured engineering style wiki through a 6-stage pipeline. Each stage reads from the previous stage's output and writes its own cache file.

```
fetch → sample → extract → compile → lint → build
```

## Overview

| Stage | Input | Output | Cache file | Uses LLM? |
|-------|-------|--------|------------|-----------|
| Fetch | GitHub username | Raw commits + diffs | `.gitstyle/commits.jsonl` | No |
| Sample | Raw commits | Representative clusters | `.gitstyle/samples.json` | No |
| Extract | Clusters | Style observations | `.gitstyle/extractions.json` | Yes |
| Compile | Observations | Wiki articles | `.gitstyle/articles.json` | Yes |
| Lint | Articles | Quality report | `.gitstyle/lint.json` | Yes |
| Build | Articles + lint | Markdown files | `wiki/` | No |

## Stage 1: Fetch

**Source:** `src/gitstyle/fetch.py`

Fetch pulls commits from the GitHub REST API for a given user or organization.

### What it does

1. Lists all public (non-fork) repos for the user via `GET /users/{name}/repos`
2. For each repo, fetches commits authored by the user via `GET /repos/{owner}/{repo}/commits`
3. For each commit, fetches the full detail (files, patches, stats) via `GET /repos/{owner}/{repo}/commits/{sha}`
4. Detects repo languages via `GET /repos/{owner}/{repo}/languages`

### Key behaviors

- **Rate limit handling**: If the GitHub API returns a 403 rate limit response, gitstyle reads the `X-RateLimit-Reset` header and waits automatically.
- **Commit cap**: Defaults to 2,000 commits total, spread evenly across repos. Configurable with `--max-commits`.
- **Incremental fetch**: If a cache already exists, gitstyle only fetches commits newer than the most recent cached commit. See [Incremental Synthesis](incremental.md).
- **Empty result protection**: If 0 commits are fetched, the result is NOT cached — preventing "cache poisoning" from failed runs.

### Output format

Each commit is stored as a `RawCommit` object:

```python
RawCommit(
    sha="abc1234...",
    repo="owner/repo-name",
    message="commit message",
    author="username",
    authored_at=datetime(...),
    additions=42,
    deletions=10,
    files=[CommitFile(filename="src/main.py", status="modified", patch="...")],
    languages=["Python", "JavaScript"],
)
```

Commits are stored one per line in `.gitstyle/commits.jsonl` (JSON Lines format).

## Stage 2: Sample

**Source:** `src/gitstyle/sample.py`

Sampling selects a representative subset of commits for LLM analysis. This is critical — analyzing all 2,000 commits would be prohibitively expensive and mostly redundant.

### What it does

1. **Groups** commits by `(repo, language)` pairs. A commit in a repo with Python and JavaScript appears in both groups.
2. **Samples** up to N commits per group (default: 20, configurable with `--samples`), using a three-way strategy:
   - **Most recent** (top 1/3 of N): Captures current style
   - **Largest diffs** (top 1/3 of N): Captures structural decisions
   - **Random fill** (remaining): Adds diversity, with a fixed seed (42) for reproducibility

### Why this sampling strategy

Most recent commits reflect the developer's *current* style (which may have evolved). Largest diffs tend to be the most architecturally informative — a 500-line commit reveals more about code structure preferences than a one-line typo fix. Random fill prevents blind spots.

### Output

A list of `SampledCluster` objects, each containing the sampled commits for one `(repo, language)` pair along with the total count in the original group.

## Stage 3: Extract

**Source:** `src/gitstyle/extract.py`

Extract is the first LLM stage. It sends each cluster to Claude and asks it to identify style observations across 9 dimensions.

### The 9 style dimensions

| Dimension | What it captures |
|-----------|-----------------|
| `code-structure` | File organization, module boundaries, function/class sizing |
| `naming-conventions` | Variable, function, class, file naming patterns |
| `patterns` | Design patterns, architectural patterns, common abstractions |
| `type-discipline` | Type annotations, generics, type safety approach |
| `testing` | Test coverage, test style, testing frameworks, TDD signals |
| `comments-and-docs` | Documentation style, comment density, docstrings |
| `dependencies` | Dependency management, third-party library choices |
| `commit-hygiene` | Commit message style, commit size, branching patterns |
| `language-idioms` | Language-specific patterns, idiomatic usage |

### How it works

For each cluster, gitstyle builds a prompt containing:
- Repository name and language
- Each commit's SHA, date, message, stats, file changes, and patch snippets (capped at 500 chars per file to stay within token limits)

The LLM returns structured JSON:

```json
{
  "observations": [
    {
      "dimension": "naming-conventions",
      "claim": "Uses snake_case for all function names, PascalCase for classes",
      "evidence": ["abc1234", "def5678"],
      "confidence": 0.85,
      "language": "Python"
    }
  ]
}
```

Each observation includes:
- **dimension**: Which of the 9 categories it falls into
- **claim**: A specific, concrete statement about the developer's style
- **evidence**: Commit SHAs that support the claim
- **confidence**: 0.0-1.0, reflecting how strong the evidence is
- **language**: Optional, for language-specific observations

### LLM parameters

- Model: `claude-sonnet-4-20250514` (configurable with `--model`)
- Temperature: 0.2 (low, for consistent structured output)
- Max tokens: 8,192

## Stage 4: Compile

**Source:** `src/gitstyle/compile.py`

Compile synthesizes all extracted observations into coherent wiki articles — one per style dimension, plus one per programming language.

### What it does

1. **Groups** all observations by dimension and by language
2. **Compiles dimension articles**: For each of the 9 dimensions that has observations, sends all observations for that dimension to the LLM with a synthesis prompt
3. **Compiles language articles**: For language-specific observations (dimension = `language-idioms`), creates per-language articles (e.g., "Python Style", "C Style")

### The compilation prompt

The LLM is instructed to:
- Write in third person ("The developer tends to...")
- Use `[[wikilinks]]` to cross-reference other dimensions
- Cite specific commit SHAs inline as evidence
- Note contradictions when observations conflict
- Be specific and concrete — avoid vague generalities

### Output

A list of `WikiArticle` objects:

```python
WikiArticle(
    slug="naming-conventions",
    title="Naming Conventions",
    category="dimension",      # or "language"
    confidence=0.82,
    source_repos=["owner/repo-a", "owner/repo-b"],
    content="... markdown body ...",
    wikilinks=["code-structure", "patterns"],
)
```

### Evolution path

When running incrementally, this stage uses `evolve_wiki()` instead of `compile_wiki()`. See [Incremental Synthesis](incremental.md).

## Stage 5: Lint

**Source:** `src/gitstyle/lint.py`

Lint is a quality check — the LLM reviews the full wiki for issues.

### What it checks

1. **Contradictions** — Claims in one article that conflict with another
2. **Weak evidence** — Claims citing only 1 commit or with low confidence
3. **Missing categories** — Style dimensions that should be covered but aren't
4. **Vague claims** — Observations too generic to be useful
5. **Cross-reference errors** — `[[wikilinks]]` pointing to articles that don't exist

### Output

A `LintReport` containing:
- A list of `LintIssue` objects, each with severity (`info`, `warning`, `error`), the affected article slug, a message, and a suggestion
- A `passed` boolean

The lint report is included in the wiki's `_meta/log.md` file so users can see what quality issues exist.

## Stage 6: Build

**Source:** `src/gitstyle/wiki_writer.py`

Build writes the final markdown files to disk.

### What it writes

```
wiki/
  index.md                    # Master index with links to all articles
  code-structure.md           # One file per style dimension
  naming-conventions.md
  patterns.md
  type-discipline.md
  testing.md
  comments-and-docs.md
  dependencies.md
  commit-hygiene.md
  languages/
    python.md                 # One file per detected language
    c.md
    javascript.md
  _meta/
    sources.md                # Which repos were analyzed
    generation-config.md      # Pipeline configuration used
    log.md                    # Generation log + lint results
```

Each article gets YAML frontmatter (title, category, confidence, source repos, last updated date). See [Output Format](output-format.md) for the full schema.

## Running Individual Stages

You can run any stage independently (each requires cached data from prior stages):

```bash
gitstyle fetch-cmd karpathy       # Just fetch
gitstyle sample-cmd karpathy      # Fetch + sample
gitstyle extract-cmd karpathy     # Fetch + sample + extract
gitstyle compile-cmd karpathy     # Fetch + sample + extract + compile
gitstyle lint-cmd karpathy        # Full pipeline minus build
```

This is useful for debugging or re-running a single expensive stage with different parameters.

## Dry Run

```bash
gitstyle run karpathy --dry-run
```

Dry run executes fetch and sample (which don't use the LLM) but skips all LLM calls. Useful for checking how many clusters will be analyzed and estimating costs before committing to a full run.
