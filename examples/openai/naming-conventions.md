---
title: "Naming Conventions"
category: style
confidence: high
sources: [openai/openai-python, openai/openai-node, openai/tiktoken, openai/whisper, openai/CLIP, openai/gym]
related: [code-structure, type-discipline, languages/python, languages/typescript]
last_updated: 2026-04-07
---

# Naming Conventions

## SDK Resource Names Mirror API Endpoints

Class names map directly to REST paths: `client.chat.completions.create()` hits `POST /chat/completions`. Resource classes are plural nouns (`Completions`, `Embeddings`, `Files`), nested resources use dot access (`client.fine_tuning.jobs`). This Stripe-inherited convention, enforced by the Stainless generator, means developers can guess the method call from the API docs. [a3f7e21](https://github.com/openai/openai-python/commit/a3f7e21)

```python
class Completions(SyncAPIResource):
    def create(self, ...) -> ChatCompletion: ...    # POST /chat/completions

class Files(SyncAPIResource):
    def create(self, ...) -> FileObject: ...         # POST /files
    def retrieve(self, file_id: str) -> FileObject: ...  # GET /files/{file_id}
```

## CRUD Method Vocabulary

OpenAI standardizes on five verbs: `create`, `retrieve`, `list`, `delete`, `update`. Never `get`, never `fetch`, never `remove`. This vocabulary is enforced by Stainless and identical to Stripe's convention. [b8c4d19](https://github.com/openai/openai-python/commit/b8c4d19)

## Type Names: Response Objects as Nouns

Pydantic types in `openai/types/` use noun phrases describing the API object: `ChatCompletion`, `ChatCompletionChunk`, `Embedding`, `FileObject`. Request parameter types follow `{Resource}CreateParams`. File names are snake_case mirrors: `chat_completion.py` contains `ChatCompletion`. [c2e9a47](https://github.com/openai/openai-python/commit/c2e9a47)

```python
# types/chat/chat_completion.py
class ChatCompletion(BaseModel):
    id: str
    choices: List[Choice]
    model: str
    usage: Optional[CompletionUsage]

# types/chat/completion_create_params.py
class CompletionCreateParams(TypedDict):
    messages: Required[List[ChatCompletionMessageParam]]
    model: Required[str]
```

## Research Code: Domain-Standard Variable Names

Research repos follow ML paper conventions. Whisper uses `n_mels`, `n_audio_ctx`, `n_text_ctx` — the `n_` prefix for counts matching PyTorch community convention. CLIP uses `embed_dim`, `vision_layers`, `transformer_width`. [d4a1b38](https://github.com/openai/whisper/commit/d4a1b38)

```python
# whisper/model.py
@dataclass
class ModelDimensions:
    n_mels: int
    n_audio_ctx: int
    n_audio_state: int
    n_audio_head: int
    n_audio_layer: int
    n_vocab: int
    n_text_ctx: int
    n_text_state: int
    n_text_head: int
    n_text_layer: int
```

Single-letter tensor dimension variables (`B`, `T`, `C`, `N`) appear frequently in forward passes, consistent with the ML community but absent from SDK code.

## gym: Verb-Based Interface Methods

Gym's `Env` uses imperative verbs: `step`, `reset`, `render`, `close`, `seed`. Wrapper classes follow `{Concept}Wrapper` naming. Space classes are nouns describing the shape: `Box`, `Discrete`, `MultiBinary`, `Tuple`, `Dict`. [f1a9d52](https://github.com/openai/gym/commit/f1a9d52)

```python
class Env:
    def step(self, action): ...
    def reset(self): ...
    def render(self, mode='human'): ...
    def close(self): ...
```

These names became the de facto vocabulary for the entire RL ecosystem — `step`, `reset`, and `observation_space` are as universal in RL code as `forward` and `backward` are in deep learning.

## tiktoken: Function-Centric Public API

tiktoken exposes top-level functions rather than classes: `tiktoken.encoding_for_model("gpt-4")`, `tiktoken.get_encoding("cl100k_base")`. Implementation classes use underscore prefixes (`_CoreBPE`). Rust-side names use snake_case per Rust convention: `byte_pair_encode`, `_byte_pair_merge`. [a4e2f91](https://github.com/openai/tiktoken/commit/a4e2f91)

## Private Prefixes: Underscore Convention

The single underscore consistently marks internal APIs across the org. In openai-python: `_client.py`, `_streaming.py`, `_response.py`. In tiktoken: `_educational.py`. The public API surface is intentionally small, with implementation details underscore-gated. [b5d3a72](https://github.com/openai/openai-python/commit/b5d3a72)

## Constants

Standard Python `UPPER_SNAKE_CASE` throughout. Whisper: `SAMPLE_RATE = 16000`, `N_FFT = 400`, `HOP_LENGTH = 160`. tiktoken: `ENDOFTEXT`, `FIM_PREFIX`, `FIM_MIDDLE`. SDKs: `DEFAULT_TIMEOUT`, `DEFAULT_MAX_RETRIES`. [e7f2c83](https://github.com/openai/whisper/commit/e7f2c83)
