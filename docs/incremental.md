# Incremental Synthesis

Starting in v0.6.0, gitstyle wikis **evolve** over time. Instead of rebuilding from scratch on every run, gitstyle detects what's changed since the last run and only processes the delta.

## How It Works

### First run (full pipeline)

```bash
gitstyle run karpathy
```

The first run has no cache, so it executes the full pipeline:

```
Fetch all commits → Sample → Extract → Compile → Lint → Build
```

All intermediate results are cached in `.gitstyle/`.

### Subsequent runs (incremental)

```bash
gitstyle run karpathy
```

When cache exists, gitstyle:

1. **Loads cached commits** from `.gitstyle/commits.jsonl`
2. **Finds the most recent commit date** across all cached commits
3. **Fetches only new commits** from GitHub (using `?since=` parameter)
4. **Deduplicates** — removes any commits that already exist in the cache (by SHA)
5. **Merges** new commits into the cache

If there are new commits:

```
Fetch delta → Sample new only → Extract new only → Evolve articles → Lint → Build
```

If there are no new commits:

```
"Wiki is up to date" → exit
```

### Force a full rebuild

```bash
gitstyle run karpathy --fresh
```

The `--fresh` flag ignores all cached data and runs the full pipeline from scratch.

## The Evolution Step

The key innovation is in Stage 4. Instead of `compile_wiki()` (which writes articles from scratch), the incremental path uses `evolve_wiki()`.

### What evolve does

For each existing article that has new observations:

1. The LLM receives the **existing article text** plus the **new observations**
2. It's instructed to **evolve** the article:
   - Preserve insights that remain valid
   - Incorporate new observations naturally
   - **Strengthen** claims that are reinforced (raise confidence)
   - **Note contradictions** when new evidence conflicts with existing claims (lower confidence)
   - Add new sections if genuinely new patterns emerge
   - Cite new commit SHAs as evidence

For style dimensions with new observations but no existing article (e.g., a developer starts using a new language), a fresh article is compiled.

For existing articles with no new observations, they pass through unchanged.

### Confidence dynamics

The evolution prompt explicitly handles confidence in both directions:

- **Reinforcement**: If new commits confirm an existing pattern, the LLM raises the confidence score and adds the new evidence
- **Contradiction**: If new commits contradict an existing claim, the LLM lowers the confidence score and notes the evolution ("Initially X, but recent commits suggest Y")

This means a wiki that initially says "Prefers functional patterns (85% confidence)" might evolve to "Previously favored functional patterns, but recent work shows increasing use of OOP (60% confidence)" if the developer's style shifts.

## Cache Structure

```
.gitstyle/
  commits.jsonl       # All commits (grows over time as new ones are appended)
  samples.json        # Invalidated on incremental runs
  extractions.json    # Merged: old + new extractions combined
  articles.json       # Updated with evolved articles
  lint.json           # Invalidated and re-run on incremental runs
```

### What gets invalidated

On an incremental run:
- `commits.jsonl` — **appended** (new commits merged in)
- `samples.json` — **deleted** (stale, since it was built from old commits)
- `extractions.json` — **merged** (new extractions combined with existing, deduplicated by claim text)
- `articles.json` — **replaced** (with the evolved articles)
- `lint.json` — **deleted** and re-run (since articles changed)

## Graceful Degradation

If the GitHub API is unreachable during an incremental fetch (network error, rate limit, token expired), gitstyle falls back gracefully:

```
Could not check for new commits: [error]
Using cached commits
```

It continues using the cached data and produces the existing wiki. No data is lost.

## Cost Savings

Incremental runs are significantly cheaper than full runs:

| Scenario | API calls | LLM calls | Typical cost |
|----------|-----------|-----------|--------------|
| Full run (2000 commits) | ~2000+ | 15-30 | $0.10-0.50 |
| Incremental (50 new commits) | ~50 | 5-15 | $0.02-0.10 |
| No new commits | 1 (repos list) | 0 | ~$0.00 |

The GitHub API calls are the main bottleneck — each commit detail requires a separate API call. Incremental fetch only calls the API for genuinely new commits.

## Clearing the Cache

```bash
# Delete all cached data, force next run to start fresh
gitstyle clean

# Or manually
rm -rf .gitstyle/
```

## When to Use `--fresh`

Use `--fresh` when:
- You've changed pipeline parameters (e.g., different `--samples` count)
- You suspect the cache is corrupted or stale
- You want a completely clean analysis
- You've changed the LLM model and want consistent output

For routine use, just run `gitstyle run <username>` and let incremental synthesis handle it.
