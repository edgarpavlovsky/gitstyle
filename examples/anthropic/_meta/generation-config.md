---
title: "Generation Configuration"
category: meta
last_updated: 2026-04-07
---

# Generation Configuration

```yaml
org: anthropics
model: claude-sonnet-4-20250514
output_dir: wiki/
max_commits: 500
repos: null  # auto-discover
min_stars: 50
languages: [python, typescript]
sample_strategy: balanced
sample_size: 25
mode: org  # org wiki, not individual developer
```

## Pipeline Settings

| Setting | Value |
|---------|-------|
| gitstyle version | 0.1.0 |
| LLM model | claude-sonnet-4-20250514 |
| Max commits per repo | 500 |
| Sample size per cluster | 25 |
| Sample strategy | balanced (recent + largest + random) |
| Min repo stars | 50 |
| Cache enabled | true |
| Cache directory | .gitstyle/anthropics/ |
| Mode | org (aggregate patterns across repos) |
| Languages | Python (primary), TypeScript (secondary) |
