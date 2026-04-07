---
title: "Generation Configuration"
category: meta
last_updated: 2026-04-07
---

# Generation Configuration

```yaml
user: karpathy
model: claude-opus-4-20250514
output_dir: wiki/
max_commits: 400
repos: null  # auto-discover
min_stars: 100
languages: [python, c]
sample_strategy: balanced
sample_size: 20
```

## Pipeline Settings

| Setting | Value |
|---------|-------|
| gitstyle version | 0.2.0 |
| LLM model | claude-opus-4-20250514 |
| Max commits per repo | 400 |
| Sample size per cluster | 20 |
| Sample strategy | balanced (recent + largest + random) |
| Min repo stars | 100 |
| Cache enabled | true |
| Cache directory | .gitstyle/karpathy/ |
