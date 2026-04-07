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

Across openai-python and openai-node, class names map directly to REST API resource paths. `client.chat.completions.create()` corresponds to `POST /chat/completions`. Resource classes are named as plural nouns: `Completions`, `Embeddings`, `Files`, `Models`. Nested resources use dot access: `client.fine_tuning.jobs`. [a3f7e21](https://github.com/openai/openai-python/commit/a3f7e21)

```python
# the class name IS the URL path segment
class Completions(SyncAPIResource):
    def create(self, ...) -> ChatCompletion: ...
    # POST /chat/completions

class Files(SyncAPIResource):
    def create(self, ...) -> FileObject: ...
    # POST /files
    def retrieve(self, file_id: str) -> FileObject: ...
    # GET /files/{file_id}
```

This Stripe-influenced convention means developers can guess the method call from the API docs and vice versa. The pattern holds across both Python and TypeScript SDKs. See [[patterns]] for the full resource method vocabulary.

## CRUD Method Vocabulary

OpenAI standardizes on a fixed set of method names for resource operations: `create`, `retrieve`, `list`, `delete`, `update`. Never `get` (it is `retrieve`), never `fetch`, never `remove`. This vocabulary is enforced by the Stainless code generator and is identical to Stripe's convention. [b8c4d19](https://github.com/openai/openai-python/commit/b8c4d19)

```python
client.files.create(file=open("data.jsonl", "rb"), purpose="fine-tune")
client.files.retrieve("file-abc123")
client.files.list()
client.files.delete("file-abc123")
```

## Type Names: Response Objects are Nouns

Pydantic model types in `openai/types/` use noun phrases that describe the API object: `ChatCompletion`, `ChatCompletionChunk`, `Embedding`, `FileObject`, `FineTuningJob`. Request parameter types use the pattern `{Resource}CreateParams`. [c2e9a47](https://github.com/openai/openai-python/commit/c2e9a47)

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

File names use snake_case versions of the class names: `chat_completion.py` contains `ChatCompletion`, `file_object.py` contains `FileObject`.

## Research Code: Domain-Standard Variable Names

In research repositories, variable naming follows ML paper conventions rather than SDK conventions. Whisper uses `n_mels`, `n_audio_ctx`, `n_text_ctx`, `n_vocab` — the `n_` prefix for counts matches PyTorch community convention. CLIP uses `embed_dim`, `image_resolution`, `vision_layers`, `transformer_width`. [d4a1b38](https://github.com/openai/whisper/commit/d4a1b38)

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

Single-letter tensor dimension variables (`B`, `T`, `C`, `N`) appear frequently in whisper and CLIP forward passes, consistent with the broader ML community. This contrasts sharply with the SDK code where such abbreviations never appear.

## gym: Verb-Based Interface Methods

Gym's `Env` base class uses imperative verbs for interface methods: `step`, `reset`, `render`, `close`, `seed`. Wrapper classes follow the pattern `{Concept}Wrapper`: `TimeLimit`, `FlattenObservation`, `RecordVideo`. Space classes are nouns describing the shape: `Box`, `Discrete`, `MultiBinary`, `Tuple`, `Dict`. [f1a9d52](https://github.com/openai/gym/commit/f1a9d52)

```python
class Env:
    def step(self, action): ...
    def reset(self): ...
    def render(self, mode='human'): ...
    def close(self): ...
```

## tiktoken: Function-Centric Public API

tiktoken exposes a small public API of top-level functions rather than classes: `tiktoken.encoding_for_model("gpt-4")`, `tiktoken.get_encoding("cl100k_base")`. Internal implementation classes use underscore-prefixed names (`_CoreBPE`). The Rust-side function names use snake_case per Rust convention: `byte_pair_encode`, `_byte_pair_merge`. [a4e2f91](https://github.com/openai/tiktoken/commit/a4e2f91)

## Private Prefixes: Underscore Convention

Across the organization, the single underscore prefix marks internal/private APIs consistently. In openai-python: `_client.py`, `_streaming.py`, `_response.py`, `_base_client.py`. In tiktoken: `_educational.py`. Public API surface is intentionally small, with implementation details underscore-gated. [b5d3a72](https://github.com/openai/openai-python/commit/b5d3a72)

```
openai/
  _client.py        # internal: base client implementation
  _streaming.py     # internal: SSE stream handling
  _response.py      # internal: response parsing
  resources/        # public: resource classes
  types/            # public: type definitions
```

## Constant Naming

OpenAI follows standard Python `UPPER_SNAKE_CASE` for module-level constants. In whisper: `SAMPLE_RATE = 16000`, `N_FFT = 400`, `HOP_LENGTH = 160`, `CHUNK_LENGTH = 30`. In tiktoken: `ENDOFTEXT`, `FIM_PREFIX`, `FIM_MIDDLE`, `FIM_SUFFIX`. SDK code uses `DEFAULT_TIMEOUT`, `DEFAULT_MAX_RETRIES`. [e7f2c83](https://github.com/openai/whisper/commit/e7f2c83)
