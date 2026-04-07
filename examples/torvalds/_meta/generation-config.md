---
title: "Generation Config"
category: meta
last_updated: 2026-04-07
---

# Generation Configuration

Pipeline configuration used to produce this wiki.

```json
{
  "fetch": {
    "username": "torvalds",
    "include_forks": false,
    "max_commits_per_repo": 200,
    "include_merges": true,
    "repos": ["torvalds/linux"]
  },
  "sample": {
    "max_samples_per_cluster": 20,
    "min_diff_lines": 5,
    "strategy": "balanced",
    "dedup_by_diff": true
  },
  "llm": {
    "model": "claude-sonnet-4-20250514",
    "temperature": 0.3,
    "max_tokens_per_article": 4096
  },
  "wiki": {
    "dimensions": [
      "code-structure",
      "naming-conventions",
      "patterns",
      "type-discipline",
      "testing",
      "comments-and-docs",
      "dependencies",
      "commit-hygiene"
    ],
    "languages": ["c"],
    "cross_reference": true,
    "min_confidence": "low"
  },
  "output_dir": "examples/torvalds",
  "cache_dir": ".gitstyle"
}
```

## Notes

- `include_merges: true` was set because Torvalds' primary contribution pattern is merging subsystem pulls with detailed merge messages
- `dedup_by_diff: true` filters out trivial merge commits that only combine branches without conflict resolution
- The `balanced` sampling strategy ensures coverage across all subsystems rather than overweighting high-churn directories like `drivers/`
