# Output Format

gitstyle produces a directory of plain markdown files with YAML frontmatter. The format is designed to be readable by humans, Obsidian, and coding agents alike.

## Directory Structure

```
wiki/
  index.md                    # Master index linking to all articles
  code-structure.md           # Style dimension articles
  naming-conventions.md
  patterns.md
  type-discipline.md
  testing.md
  comments-and-docs.md
  dependencies.md
  commit-hygiene.md
  languages/
    python.md                 # Language-specific articles
    c.md
    javascript.md
    ...
  _meta/
    sources.md                # Which repos were analyzed
    generation-config.md      # Pipeline configuration
    log.md                    # Generation timestamp + lint results
```

### What articles get created

Not every wiki will have all 9 dimension articles. An article is only created if the extract stage found observations for that dimension. If a developer has no test-related commits, there won't be a `testing.md`.

Language articles are created for any language with `language-idioms` observations. A developer who writes Python and JavaScript will get `languages/python.md` and `languages/javascript.md`.

## YAML Frontmatter

Every article has YAML frontmatter at the top:

```yaml
---
title: Naming Conventions
category: dimension
confidence: 0.82
source_repos:
  - karpathy/nanoGPT
  - karpathy/micrograd
  - karpathy/llm.c
last_updated: 2026-04-07
---
```

### Frontmatter fields

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Human-readable article title |
| `category` | string | One of: `dimension`, `language`, `index`, `meta` |
| `confidence` | float | 0.0-1.0, aggregate confidence across all claims in the article |
| `source_repos` | list[string] | GitHub repos that provided evidence (`owner/name` format) |
| `last_updated` | string | ISO date of last generation/update |

### Confidence scores

Confidence reflects how strong the evidence is for the article's claims:

| Range | Meaning |
|-------|---------|
| 0.8-1.0 | Strong pattern with evidence across multiple repos/commits |
| 0.6-0.8 | Clear pattern but limited evidence or some variation |
| 0.4-0.6 | Tentative pattern, may be context-dependent |
| 0.0-0.4 | Weak signal, likely based on very few commits |

Confidence scores change over time with [incremental synthesis](incremental.md) — reinforced patterns go up, contradicted patterns go down.

## Article Body

Article bodies are markdown written in third person:

```markdown
The developer consistently uses snake_case for function and variable names,
with PascalCase reserved for class definitions. This pattern holds across all
analyzed repositories [abc1234] [def5678].

In test files, a `test_` prefix is universal — no exceptions were found
across 847 test functions [ghi9012].

See also: [[code-structure]], [[testing]]
```

### Key conventions

- **Third person**: "The developer tends to..." / "The organization prefers..."
- **Commit SHA citations**: Referenced inline as `[abc1234]` (first 7 characters)
- **Wikilinks**: Cross-references use Obsidian-compatible `[[slug]]` or `[[slug|Display Name]]` syntax
- **Specificity**: Claims are concrete ("uses 4-space indentation in Python") not vague ("follows good practices")
- **Contradiction handling**: When evidence conflicts, both sides are noted with their relative strength

## Wikilinks

Articles cross-reference each other using Obsidian-compatible wikilinks:

```markdown
[[naming-conventions]]                    # Links to naming-conventions.md
[[languages/python|Python Style]]         # Links to languages/python.md, displays as "Python Style"
[[code-structure]]                        # Links to code-structure.md
```

The web viewer resolves these links for navigation. In Obsidian, they work natively with the graph view.

## Index File

`index.md` is auto-generated and lists all articles by category:

```markdown
# Engineering Style Wiki

## Style Dimensions

- [[code-structure|Code Structure]] (85% confidence)
- [[naming-conventions|Naming Conventions]] (82% confidence)
- [[patterns|Patterns]] (78% confidence)
...

## Languages

- [[languages/python|Python Style]] (80% confidence)
- [[languages/c|C Style]] (75% confidence)

## Meta

- [[_meta/sources|Sources]]
- [[_meta/generation-config|Generation Config]]
- [[_meta/log|Generation Log]]
```

## Meta Files

### `_meta/sources.md`

Lists all repositories that were analyzed, with links to GitHub:

```markdown
## Repositories Analyzed

- [karpathy/nanoGPT](https://github.com/karpathy/nanoGPT)
- [karpathy/micrograd](https://github.com/karpathy/micrograd)
- [karpathy/llm.c](https://github.com/karpathy/llm.c)
```

### `_meta/generation-config.md`

Records the pipeline configuration used for this run:

```markdown
- **Username:** karpathy
- **Max commits:** 2000
- **Samples per group:** 20
- **LLM model:** claude-sonnet-4-20250514
```

### `_meta/log.md`

Timestamp, article count, lint pass/fail, and any lint issues:

```markdown
**Generated at:** 2026-04-07 14:30:00 UTC
**Articles:** 11
**Lint passed:** Yes
```

## Obsidian Compatibility

The wiki is designed to work as an Obsidian vault:

1. Open the `wiki/` directory as a vault in Obsidian
2. `[[wikilinks]]` resolve automatically
3. The Obsidian graph view shows the same knowledge graph as the web viewer
4. Frontmatter is visible in Obsidian's properties panel
5. `index.md` serves as the home page

## Machine Readability

The wiki is designed to be consumed by coding agents. The combination of:
- Structured YAML frontmatter (parseable metadata)
- Wikilink cross-references (navigable graph)
- Commit SHA citations (verifiable evidence)
- Explicit confidence scores (weighted trustworthiness)

...makes it easy for an agent to load, search, and prioritize the most confident patterns. See [Agent Integration](agent-integration.md) for setup instructions.
