---
title: "Generation Config"
category: meta
---

# Generation Configuration

```json
{
  "fetch": {
    "username": "torvalds",
    "include_forks": false,
    "max_commits_per_repo": 200
  },
  "sample": {
    "max_samples_per_cluster": 20,
    "min_diff_lines": 5,
    "strategy": "balanced"
  },
  "llm": {
    "model": "claude-sonnet-4-20250514"
  },
  "output_dir": "examples/torvalds",
  "cache_dir": ".gitstyle"
}
```
