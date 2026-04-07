---
title: "Generation Config"
category: meta
last_updated: 2026-04-07
---

# Generation Config

## Pipeline Configuration

The following configuration was used to generate this wiki.

```yaml
# gitstyle.config.yaml
target: edgarpavlovsky
output_dir: ./wiki
format: markdown

sources:
  provider: github
  include_forks: false
  min_commits: 10
  exclude_repos:
    - "*.github.io"
    - dotfiles

analysis:
  model: claude-sonnet-4-20250514
  commit_batch_size: 50
  max_tokens_per_batch: 8000
  temperature: 0.2

dimensions:
  - code-structure
  - naming-conventions
  - patterns
  - type-discipline
  - testing
  - comments-and-docs
  - dependencies
  - commit-hygiene

languages:
  - swift
  - typescript

output:
  frontmatter: true
  wikilinks: true
  commit_links: true
  confidence_scores: true
  index_page: true
  meta_pages: true
```

## Pipeline Stages

1. **Fetch** — Clone or pull latest commits from all public repos
2. **Filter** — Remove merge commits, bot commits, and low-signal changes
3. **Chunk** — Batch commits into groups of 50 for analysis
4. **Analyze** — Send each batch to the LLM with dimension-specific prompts
5. **Synthesize** — Merge per-batch observations into coherent articles
6. **Render** — Generate markdown files with frontmatter and wikilinks
7. **Validate** — Check for broken wikilinks and missing frontmatter fields

## Runtime

- Total pipeline duration: **4m 23s**
- LLM calls: **31** (15 analysis batches + 8 dimension syntheses + 2 language pages + 6 validation passes)
- Input tokens: ~142,000
- Output tokens: ~38,000
