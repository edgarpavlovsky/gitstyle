---
title: MDX Style Guide
category: language
confidence: 0.85
source_repos:
  - openai/CLIP
  - openai/DALL-E
  - openai/baselines
  - openai/chatgpt-retrieval-plugin
  - openai/codex
  - openai/codex-plugin-cc
  - openai/consistency_models
  - openai/evals
  - openai/gpt-2
  - openai/gpt-3
  - openai/gpt-oss
  - openai/guided-diffusion
  - openai/gym
  - openai/jukebox
  - openai/openai-agents-python
  - openai/openai-cookbook
  - openai/openai-cs-agents-demo
  - openai/openai-node
  - openai/openai-python
  - openai/openai-realtime-agents
  - openai/parameter-golf
  - openai/point-e
  - openai/shap-e
  - openai/skills
  - openai/spinningup
  - openai/swarm
  - openai/symphony
  - openai/tiktoken
  - openai/universe
  - openai/whisper
last_updated: 2026-04-08
---
The developer demonstrates a sophisticated approach to MDX, leveraging it as a documentation format that seamlessly integrates markdown with executable code examples, particularly in the context of Jupyter notebooks.

## Documentation-as-Code Philosophy

The developer uses MDX to create living documentation where code examples are not just static text but executable components. This pattern is evident across multiple commits (c2d6fbe0, d2832f4d, 9085ae61, 51007543, 1d283bd3, 65d66826) where MDX files combine explanatory text with interactive code blocks.

This approach aligns with modern [[comments-and-docs]] practices by ensuring documentation stays synchronized with actual code behavior. Rather than maintaining separate documentation and example files, the developer embeds runnable examples directly within the narrative flow.

## Integration with Jupyter Ecosystem

The developer's MDX usage shows a clear preference for Jupyter notebook integration, suggesting a data science or educational context. This pattern reflects broader [[language-idioms]] where MDX serves as a bridge between traditional documentation formats and interactive computing environments.

The choice to use MDX over pure markdown or Jupyter notebooks alone indicates a deliberate [[code-structure]] decision to maintain both human readability and machine executability in a single format.
