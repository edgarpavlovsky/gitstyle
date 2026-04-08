---
title: Comments and Documentation Style
category: dimension
confidence: 0.9
source_repos:
  - torvalds/1590A
  - torvalds/AudioNoise
  - torvalds/GuitarPedal
  - torvalds/HunspellColorize
  - torvalds/linux
  - torvalds/pesconvert
  - torvalds/test-tlb
  - torvalds/uemacs
last_updated: 2026-04-08
---
The developer demonstrates a distinctive documentation philosophy that prioritizes explanatory value over volume, with a particular emphasis on the 'why' rather than the 'what' of code decisions.

## Inline Comments

The developer uses inline comments sparingly but strategically. When comments do appear, they focus on explaining complex logic [4210d1cf, 4ac62b97], hardware-specific behaviors [3036cd0d, 86782c16], and non-obvious design decisions [c9098c2c, 2f3c1c07]. The developer strongly prefers inline comments over block comments for explaining implementation details [86782c16, 66d64899], particularly when dealing with:

- Hardware workarounds and timing issues [bfe62a45, f8f5627a]
- Character encoding complexities [e8f984a1, ec6f4f36]
- Mathematical calculations and algorithms [c9098c2c, b19dca57]
- Performance considerations [cedcf700, 784130fa]

The commenting style is notably conversational and informal, often including self-deprecating humor [1ac1fc73, 66ff8cb8] and candid observations like "XML? F*ck me with a ten-foot pole" [7a7221a3]. This informal tone extends to acknowledging the age and limitations of codebases [1c1b25ef, 1cdcf9df].

## Commit Messages

The developer's [[commit-hygiene]] is exceptional, with commit messages that often exceed the code changes themselves in length. These messages consistently include:

- Detailed problem descriptions and solution rationale [3036cd0d, 86782c16]
- Historical context and cultural references [6a6daef2, f434a0e2]
- Personal anecdotes and philosophical musings [ea71138d, 5c6c230f]
- Test results and future plans [e3660495, eb0d867a]
- Attribution to original authors and external help [93a72563, 4e524250]

Merge commits receive particular attention, containing comprehensive changelogs with bullet-pointed summaries, CVE references, and subsystem categorization [66d64899, f8f5627a, 85fb6da4].

## Documentation Philosophy

The developer follows a "self-documenting code" philosophy, preferring clear [[naming-conventions]] and [[code-structure]] over excessive inline documentation [bc93b501, d2f2439e]. When documentation is necessary, it tends to be comprehensive - README files explain motivation, usage, and limitations thoroughly [bc93b501, 0d99d1c8].

The developer openly acknowledges external assistance, including AI/Google help, in both commits and comments [93a72563, 4e524250, ed2e0c15]. This transparency extends to crediting external sources and libraries [b19dca57, 749d90d4].

## Language-Specific Patterns

Across different [[language-idioms]], the documentation approach remains consistent:
- In [[c]], comments focus on hardware behavior and performance
- In [[assembly]], comments explain timing and hardware workarounds
- In [[python]] and scripting languages, comments are minimal, relying on clear code
- In [[openscad]] and domain-specific languages, commit messages carry the documentation burden

The developer's documentation style reflects a pragmatic approach: document thoroughly when it matters (complex logic, non-obvious decisions, historical context) but avoid redundant comments that merely restate the code.
