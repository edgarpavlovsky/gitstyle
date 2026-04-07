---
title: "Generation Configuration"
category: meta
last_updated: 2026-04-07
---

# Generation Configuration

```yaml
org: openai
mode: organization
model: claude-opus-4-20250514
output_dir: wiki/
max_commits: 500
repos:
  - openai/openai-python
  - openai/openai-node
  - openai/tiktoken
  - openai/whisper
  - openai/CLIP
  - openai/gym
  - openai/openai-cookbook
  - openai/triton
min_stars: 500
languages: [python, typescript, rust, c++]
sample_strategy: balanced
sample_size: 30
```

## Pipeline Settings

| Setting | Value |
|---------|-------|
| gitstyle version | 0.2.0 |
| Mode | organization (multi-repo, multi-contributor) |
| LLM model | claude-opus-4-20250514 |
| Max commits per repo | 500 |
| Sample size per cluster | 30 |
| Sample strategy | balanced (recent + largest + random) |
| Min repo stars | 500 |
| Cache enabled | true |
| Cache directory | .gitstyle/openai/ |
| Cross-repo analysis | enabled |
| Contributor dedup | enabled (normalize bot vs. human commits) |

## Organization-Specific Settings

| Setting | Value |
|---------|-------|
| Bot commit detection | enabled (Stainless bot commits flagged) |
| Generated code detection | enabled (Stainless SDK output identified) |
| Category tagging | SDK / Research / Tooling / Documentation |
| Contrast analysis | enabled (highlight divergent patterns across categories) |
