---
title: "Data Sources"
category: meta
last_updated: 2026-04-07
---

# Data Sources

## Repositories Analyzed

| Repository | Commits Fetched | Commits Sampled | Primary Language |
|------------|----------------|-----------------|------------------|
| torvalds/linux | 200 | 180 | C |

## Sampling Notes

- The `torvalds/linux` repository contains over 1,100,000 commits spanning 30+ years
- Sampling was limited to 200 recent commits authored or merged by torvalds
- Merge commits were included because Torvalds' primary contribution pattern is merging subsystem pulls with detailed merge messages
- Commits were deduplicated by diff content to avoid overweighting trivial merges
- Style signal was extracted from both the merge messages (review philosophy, commit hygiene expectations) and the underlying code changes (naming, structure, patterns)

## Coverage Gaps

- **Private repositories**: None known; Torvalds works entirely in public
- **Mailing list context**: LKML discussion is not captured by commit analysis alone — review style patterns (see [[comments-and-docs]]) are inferred from commit messages and inline comments
- **Historical evolution**: The 200-commit window captures current style but may miss conventions that evolved over the kernel's 30-year history
- **Subsystem variation**: Individual subsystem maintainers may have local conventions that diverge from Torvalds' direct preferences; this wiki focuses on the style enforced at the top level

## Confidence Impact

Articles referencing only merge commits (e.g., [[testing]]) have lower confidence than articles grounded in direct code changes (e.g., [[naming-conventions]], [[patterns]]).

**Total commits fetched:** 200
**Total commits sampled:** 180
**Unique files touched:** 1,247
**Date range:** 2024-08 to 2026-03
