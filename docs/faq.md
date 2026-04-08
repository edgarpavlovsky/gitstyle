# FAQ

## General

### What is gitstyle?

A CLI tool that generates engineering style wikis from GitHub commit history. It analyzes how you (or an organization) actually writes code and packages those patterns into a structured markdown wiki that coding agents can use as context.

### Who is this for?

- **Individual developers** who want coding agents to write code in their style
- **Engineering teams** who want to document their team's conventions automatically (from actual code, not aspirational docs)
- **Anyone curious** about what patterns emerge from their commit history

### How is this different from just reading someone's code?

gitstyle synthesizes across hundreds or thousands of commits to find *patterns* — things that are consistent across repos, languages, and time. Reading a single file shows one example; gitstyle shows whether that example is representative or an exception.

### Does it work with private repos?

Yes, if your `GITHUB_TOKEN` has access to those repos. The token needs `repo` scope for private repo access (vs `public_repo` for public only).

## Pipeline & Usage

### How long does a full run take?

Typically 3-10 minutes, depending on the number of repos and commits. The bottleneck is GitHub API calls (one per commit detail). The LLM calls add another 1-3 minutes.

### How much does it cost?

A typical run (one developer, ~2000 commits) costs **$0.10-0.50** in Anthropic API usage with the default model (`claude-sonnet-4-20250514`). Incremental runs are significantly cheaper since they only process new commits.

### Can I use a cheaper model?

Yes. Use `--model claude-haiku-4-5-20251001` for faster, cheaper runs. Quality is slightly lower but often good enough for initial exploration.

### Can I use OpenAI or other LLM providers?

Not currently. gitstyle is hardcoded to the Anthropic SDK. The prompts are model-agnostic (plain text), so adding another provider is a clean change in `llm_client.py`. See [Architecture](architecture.md#adding-a-new-llm-provider).

### What does `--dry-run` do?

It runs the fetch and sample stages (no LLM calls, no cost) and shows how many clusters would be analyzed. Useful for estimating cost before committing to a full run.

### Can I analyze specific repos only?

Yes: `gitstyle run karpathy --repos karpathy/nanoGPT,karpathy/micrograd`

### Can I limit the time range?

Yes: `gitstyle run karpathy --since 2024-01-01 --until 2024-12-31`

## Caching & Incremental

### Why does my run complete instantly with no output?

You likely have stale cache from a previous failed run. Before v0.5.0, empty results were cached, so a failed run (e.g., missing API key) would permanently poison the cache. Fix:

```bash
gitstyle clean
gitstyle run <username>
```

This was fixed in v0.5.0 — empty results are no longer cached.

### Does my wiki update when I make new commits?

Yes, starting in v0.6.0. Just re-run `gitstyle run <username>` and it will:
1. Fetch only new commits since the last run
2. Extract observations from new commits only
3. Evolve existing articles with the new observations

See [Incremental Synthesis](incremental.md).

### When should I use `--fresh`?

Use `--fresh` when:
- You've changed parameters (different `--samples` count, different model)
- You suspect cache corruption
- You want a completely clean rebuild
- You've changed models and want consistent output

### Where is the cache stored?

In `.gitstyle/` relative to where you run the command (configurable with `--cache`). It contains:
- `commits.jsonl` — raw commit data
- `samples.json` — sampled clusters
- `extractions.json` — LLM observations
- `articles.json` — compiled articles
- `lint.json` — quality report

### Can I share cache between machines?

The cache files are portable JSON. You can copy `.gitstyle/` to another machine and `gitstyle run` will use it (and run incrementally from there).

## Output & Integration

### What format is the output?

Plain markdown with YAML frontmatter and `[[wikilinks]]`. Compatible with Obsidian, any text editor, and any coding agent. See [Output Format](output-format.md).

### How do I view the wiki?

Three ways:
1. **Text editor**: Open `wiki/index.md` in any editor
2. **Obsidian**: Open the `wiki/` folder as a vault — wikilinks and graph view work natively
3. **Web viewer**: `gitstyle serve` launches an interactive graph visualization

### How do I plug this into Claude Code / Cursor / etc.?

See [Agent Integration](agent-integration.md) for setup instructions for each tool.

### Should I commit the wiki to my repo?

Yes, generally. It makes the wiki available to any coding agent working on your codebase, and Git tracks its evolution over time. The wiki is plain markdown — no sensitive data unless your commit messages contain it.

## Troubleshooting

### `Error: GitHub token is invalid or expired`

Your `GITHUB_TOKEN` is not valid. Generate a new one at [github.com/settings/tokens](https://github.com/settings/tokens) with `public_repo` scope.

### `Error: No Anthropic API credentials found`

Set either `ANTHROPIC_API_KEY` or `ANTHROPIC_AUTH_TOKEN`:
```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### `Error: No commits found`

Possible causes:
- The username doesn't exist or has no public repos
- The user has repos but no commits authored by them (all commits are from other contributors)
- Previous failed run cached empty results — run `gitstyle clean` first

### `Rate limited. Waiting Xs...`

GitHub API rate limits. With a token, you get 5,000 requests/hour. Large analyses (many repos, many commits) can hit this. The tool waits automatically and resumes. You can reduce `--max-commits` to stay under limits.

### The web viewer shows stale content

The server sends `Cache-Control: no-cache` headers, but your browser may still cache aggressively. Hard refresh with `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows/Linux).

### `ModuleNotFoundError: No module named 'gitstyle'`

gitstyle isn't installed in your current Python environment. Either:
```bash
pip install gitstyle                    # From PyPI
pip install -e .                        # From source (in the repo directory)
```

Make sure you're using the same Python environment where you installed it.
