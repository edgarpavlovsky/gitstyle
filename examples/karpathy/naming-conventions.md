---
title: Naming Conventions
category: dimension
confidence: 0.92
source_repos:
  - karpathy/EigenLibSVM
  - karpathy/KarpathyTalk
  - karpathy/LLM101n
  - karpathy/Random-Forest-Matlab
  - karpathy/arxiv-sanity-lite
  - karpathy/arxiv-sanity-preserver
  - karpathy/autoresearch
  - karpathy/build-nanogpt
  - karpathy/calorie
  - karpathy/char-rnn
  - karpathy/convnetjs
  - karpathy/covid-sanity
  - karpathy/cryptos
  - karpathy/deep-vector-quantization
  - karpathy/find-birds
  - karpathy/forestjs
  - karpathy/hn-time-capsule
  - karpathy/jobs
  - karpathy/karpathy
  - karpathy/karpathy.github.io
  - karpathy/lecun1989-repro
  - karpathy/llama2.c
  - karpathy/llm-council
  - karpathy/llm.c
  - karpathy/makemore
  - karpathy/micrograd
  - karpathy/minGPT
  - karpathy/minbpe
  - karpathy/nanoGPT
  - karpathy/nanochat
  - karpathy/neuraltalk
  - karpathy/neuraltalk2
  - karpathy/ng-video-lecture
  - karpathy/nipspreview
  - karpathy/nn-zero-to-hero
  - karpathy/notpygamejs
  - karpathy/paper-notes
  - karpathy/pytorch-normalizing-flows
  - karpathy/randomfun
  - karpathy/reader3
  - karpathy/recurrentjs
  - karpathy/reinforcejs
  - karpathy/rendergit
  - karpathy/researchlei
  - karpathy/researchpooler
  - karpathy/rustbpe
  - karpathy/scholaroctopus
  - karpathy/svmjs
  - karpathy/tf-agent
  - karpathy/tsnejs
  - karpathy/twoolpy
  - karpathy/ulogme
last_updated: 2026-04-08
---
The developer demonstrates strong adherence to language-specific naming conventions across their multi-language codebase, with a clear preference for descriptive, self-documenting names that indicate purpose and functionality.

## Language-Specific Patterns

### Python
The developer strictly follows PEP 8 conventions in [[python]] code:
- **Functions and variables**: Consistently uses snake_case (e.g., `get_papers_db`, `extract_features`, `generate_conversation_title`) [d7a303b4, 2c99eac2, 827bfd3d]
- **Classes**: Uses PascalCase convention (e.g., `LSTMGenerator`, `RNNGenerator`, `ChapterContent`) [2c99eac2, 64960f99, ac30aa07]
- **Constants**: Employs UPPER_CASE (e.g., `MAX_SEQ_LEN`, `TIME_BUDGET`, `BOOKS_DIR`) [b11d6f28, 8a5c4869, 64960f99]
- **Private methods**: Prefixes with underscore (e.g., `_backward`, `_prev`, `_op`) [9fd9cc02, 6e6a5281]

### JavaScript
The developer follows standard [[javascript]] conventions:
- **Functions and variables**: Uses camelCase consistently (e.g., `loadPubs`, `sendMessageStream`, `makeRbfKernel`) [c7940cf8, 87b4a178, f480d05e]
- **Constructors**: Applies PascalCase (e.g., `SVM`, `WordList`) [46b290ea, 759f7e73]
- **Library namespacing**: Creates namespace patterns with uppercase prefixes (e.g., `NPGinit`, `NPGcanvas`) [6ee48fa7]

### Go
The developer strictly adheres to [[go]] idioms:
- **Functions**: Uses PascalCase for exported functions (e.g., `GetFollowingTimelinePosts`, `RebuildTrending`, `IsBanned`) [38406bcc, 9a458854, eed8b1b9]
- **Variables**: Employs camelCase for all variables [38406bcc, 9a458854]
- **Database columns**: Maintains snake_case for SQL compatibility [38406bcc, a8101e25]

### CSS and HTML
The developer follows web standards in [[css]] and [[html]]:
- **CSS classes**: Uses kebab-case consistently (e.g., `ai-post`, `welcome-banner`, `activity-card`, `rel-paper`) [ca230d95, 3cc3390f, c8a2ab52]
- **CSS files**: Names with underscores (e.g., `index_style.css`, `overview_style.css`) [74b4fa86, 88259a07]
- **HTML IDs**: Applies kebab-case (e.g., `time-filter-field`, `profile-login-form`) [d7a303b4, 759f7e73]

### C/C++/CUDA
The developer maintains consistency across low-level languages in [[c]], [[cplusplus]], and [[cuda]]:
- **Functions**: Uses snake_case (e.g., `gpt2_allocate_state`, `malloc_run_state`, `quantize_q80`) [e33402f7, d9862069, 1fcdf04f]
- **Variables**: Employs snake_case with descriptive names [29aacba1, 5186b505]

## Cross-Language Patterns

### Descriptive Naming Philosophy
The developer prioritizes clarity over brevity, using names that clearly indicate purpose:
- Action-oriented function names with verb prefixes (e.g., `fetch_`, `parse_`, `build_`, `render_`) [e9345a4b, 739f1013]
- Domain-specific prefixes for context (e.g., `gpt2_` for model functions, `vq_` for vector quantization) [e33402f7, e2fa7913]
- Self-documenting boolean functions (e.g., `IsBanned`, `isActive`) [38406bcc]

### File Naming Conventions
The developer maintains consistent file naming across project types:
- **Python scripts**: snake_case with descriptive names (e.g., `make_cache.py`, `export_events.py`) [7d5030b2, 74b4fa86]
- **Notebooks**: Descriptive snake_case with part numbers for sequences (e.g., `makemore_part1_bigrams.ipynb`) [56eda75e, 4c355970]
- **Blog posts**: Follows Jekyll convention with date prefixes (e.g., `2024-01-15-post-title.markdown`) [757d5da4, 08dc797b]
- **Shell scripts**: Action-oriented names (e.g., `spawn.sh`, `killall.sh`, `runworker.sh`) [7513852b]

### Domain-Specific Abbreviations
The developer uses consistent abbreviations within specific domains:
- **Machine Learning**: Short tensor names (e.g., `x`, `y`, `B`, `T` for batch/time dimensions) [7822fce8, 4a63e6a5]
- **Cryptography**: Standard abbreviations (e.g., `sk` for secret key, `pk` for public key) [80f72e7d, e661637e]
- **Neural Networks**: Common shortcuts (e.g., `embd` for embedding, `ffwd` for feedforward) [8050fde8, 97dd3f9d]

### Exceptions and Inconsistencies
While generally consistent, the developer occasionally deviates from conventions:
- Uses camelCase in Python code when interfacing with JavaScript libraries [c7940cf8]
- Employs short, mathematical variable names in scientific computing contexts (e.g., `x1i`, `x2i`, `pj` in t-SNE implementation) [6d6a4754, 5ccbde63]
- Sometimes uses abbreviated variable names in performance-critical code (e.g., `nh`, `ns`, `na` in algorithm implementations) [08d2030d, 53bf4862]

The developer's naming conventions reflect a pragmatic approach that balances readability with [[language-idioms]], consistently choosing descriptive names that enhance [[code-structure]] clarity while respecting the conventions of each programming language.
