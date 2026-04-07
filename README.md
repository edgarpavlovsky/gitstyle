# gitstyle

Analyze a developer's GitHub commit history and compile it into a personal **engineering style wiki** — plain markdown, agent-agnostic, Obsidian-compatible.

## Install

```bash
pip install gitstyle
```

## Quickstart

```bash
export GITHUB_TOKEN=ghp_...
gitstyle run <username>
```

This runs the full pipeline:
1. **Fetch** — pulls commit data from GitHub REST API
2. **Sample** — selects representative commits per repo × language
3. **Extract** — LLM analyzes commits for style patterns across 9 dimensions
4. **Compile** — LLM merges observations into markdown wiki articles
5. **Lint** — LLM checks for contradictions and weak evidence

Output lands in `wiki/` — open it in Obsidian or any markdown viewer.

## Options

```
gitstyle run <username> [OPTIONS]

  --output, -o PATH       Output directory (default: wiki)
  --cache PATH            Cache directory (default: .gitstyle)
  --max-commits, -n INT   Max commits to fetch (default: 2000)
  --samples, -s INT       Samples per group (default: 20)
  --repos, -r TEXT        Comma-separated repo filter (owner/name)
  --since TEXT            Only commits after this date (ISO 8601)
  --until TEXT            Only commits before this date (ISO 8601)
  --model, -m TEXT        LLM model (default: claude-sonnet-4-20250514)
  --dry-run               Show cost estimates without making LLM calls
  --token, -t TEXT        GitHub token (or set GITHUB_TOKEN)
```

## Individual Stages

Run stages independently — each reads from cache if prior stages have run:

```bash
gitstyle fetch-cmd <username>
gitstyle sample-cmd <username>
gitstyle extract-cmd <username>
gitstyle compile-cmd <username>
gitstyle lint-cmd <username>
```

Clean cached data:

```bash
gitstyle clean
```

## Wiki Output

```
wiki/
  index.md                    # Overview with links to all articles
  code-structure.md           # File organization, module boundaries
  naming-conventions.md       # Variable, function, class naming
  patterns.md                 # Design patterns, abstractions
  type-discipline.md          # Type annotations, generics
  testing.md                  # Test coverage, frameworks, style
  comments-and-docs.md        # Documentation approach
  dependencies.md             # Third-party library choices
  commit-hygiene.md           # Commit messages, branching
  languages/
    python.md                 # Language-specific idioms
    typescript.md
    ...
  _meta/
    sources.md                # Repositories analyzed
    generation-config.md      # Config used for generation
    log.md                    # Generation log and lint results
```

Each article includes:
- **YAML frontmatter** — title, category, confidence level, source repos, last updated
- **`[[wikilinks]]`** — cross-references between articles (Obsidian-compatible)
- **Commit SHA citations** — every claim links back to specific commits

## Cost Estimate

Use `--dry-run` to see how many LLM calls will be made:

```bash
gitstyle run <username> --dry-run
```

Typical run: ~10–30 LLM calls depending on repo count and language diversity.

## Agent Integration

The wiki output is plain markdown — any AI agent can read it to understand a developer's style:

```python
# Load a developer's style context
from pathlib import Path

style_context = ""
for md in Path("wiki").glob("*.md"):
    style_context += md.read_text() + "\n\n"

# Pass to your agent's system prompt
system = f"Follow this developer's coding style:\n\n{style_context}"
```

```yaml
# CLAUDE.md / .cursorrules / etc.
# Reference the wiki directly:
# See wiki/ for my engineering style preferences.
```

## Development

```bash
git clone https://github.com/yourusername/gitstyle
cd gitstyle
pip install -e ".[dev]"
pytest
```

## License

MIT
