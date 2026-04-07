---
title: "C Idioms"
category: language
confidence: high
sources: [karpathy/llm.c]
related: [naming-conventions, type-discipline, dependencies, patterns]
last_updated: 2026-04-07
---

# C Idioms

## Single Translation Unit

`llm.c` keeps the entire GPT-2 implementation in a single `.c` file (`train_gpt2.c`). All functions, structs, and the `main()` entry point live together. There is no separate header file for the core implementation — `#include` is used only for standard library headers. [e8c3f1a](https://github.com/karpathy/llm.c/commit/e8c3f1a)

```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

// --- all type definitions ---
// --- all forward pass functions ---
// --- all backward pass functions ---
// --- training loop ---
// --- main() ---
```

This mirrors the single-file Python pattern (see [[code-structure]]) and makes `gcc train_gpt2.c -o train_gpt2 -lm` the complete build command. No Makefile, no cmake — the barrier to compilation is as low as the barrier to running `python train.py`.

## Structs as Namespaces

C structs serve the same role as Python dataclasses — grouping related data. `GPT2Config`, `GPT2`, `ParameterTensors`, `ActivationTensors` are all `typedef struct`. Functions that operate on them take the struct as the first argument, mimicking methods: [e8c3f1a](https://github.com/karpathy/llm.c/commit/e8c3f1a)

```c
typedef struct {
    GPT2Config config;
    ParameterTensors params;
    ActivationTensors acts;
    int batch_size;
    int seq_len;
    float mean_loss;
} GPT2;

void gpt2_forward(GPT2 *model, int* inputs, int* targets, int B, int T);
void gpt2_backward(GPT2 *model);
void gpt2_update(GPT2 *model, float learning_rate, float beta1, float beta2, float eps, float weight_decay, int t);
void gpt2_free(GPT2 *model);
```

The `gpt2_*` prefix convention creates a pseudo-namespace. This is the C equivalent of `class GPT` with methods — same conceptual grouping, just expressed through naming convention rather than language syntax.

## Flat Memory Layout

Tensors are stored as flat `float*` arrays with manual offset computation. There is no tensor library, no multi-dimensional array abstraction. Shape information is tracked by convention (comments) and computed inline: [e8c3f1a](https://github.com/karpathy/llm.c/commit/e8c3f1a)

```c
// parameters are stored in a single contiguous block
float* params_memory;
// individual tensors are views into this block
model->params.wte = params_memory;
model->params.wpe = params_memory + V * C;
model->params.ln1w = params_memory + V * C + T * C;
```

This forces the reader to understand exactly where each parameter lives in memory — the same knowledge that PyTorch's `nn.Parameter` hides behind an abstraction. The flat layout also mirrors how GPU memory works, making the transition to the CUDA version conceptually straightforward.

## Manual BLAS

Matrix multiplications are written as explicit triple-nested loops. No calls to CBLAS, MKL, or OpenBLAS: [e8c3f1a](https://github.com/karpathy/llm.c/commit/e8c3f1a)

```c
void matmul_forward(float* out, float* inp, float* weight, float* bias,
                    int B, int T, int C, int OC) {
    for (int b = 0; b < B; b++) {
        for (int t = 0; t < T; t++) {
            float* out_bt = out + b * T * OC + t * OC;
            float* inp_bt = inp + b * T * C + t * C;
            for (int o = 0; o < OC; o++) {
                float val = (bias != NULL) ? bias[o] : 0.0f;
                float* wrow = weight + o * C;
                for (int i = 0; i < C; i++) {
                    val += inp_bt[i] * wrow[i];
                }
                out_bt[o] = val;
            }
        }
    }
}
```

This is intentionally slow but completely transparent. Every multiply-accumulate is visible. The CUDA version uses optimized kernels, but the C reference prioritizes readability — a reader can trace a single element through the entire matmul with pen and paper.

## Error Handling Via Immediate Exit

Error handling uses `fprintf(stderr, ...)` followed by `exit(1)`. There are no error codes, no `errno` checking, no recovery paths. If something goes wrong (file not found, allocation failure), the program prints a message and exits: [e8c3f1a](https://github.com/karpathy/llm.c/commit/e8c3f1a)

```c
FILE *model_file = fopen(checkpoint_path, "rb");
if (model_file == NULL) {
    printf("Error opening model file\n");
    exit(1);
}
```

This matches the educational context: error recovery adds complexity without teaching anything about GPT-2. The only failure mode the reader should encounter is "fix the file path and re-run."

## Shape Comments Carry Over

The `(B, T, C)` shape comment convention from Python appears identically in C code. This creates visual continuity between the Python reference and C implementation — a reader who learned the shapes in nanoGPT can navigate llm.c by following the same annotations: [e8c3f1a](https://github.com/karpathy/llm.c/commit/e8c3f1a)

```c
float* wte;  // (V, C)
float* wpe;  // (maxT, C)
float* ln1w; // (L, C)
```

## Compile-Time Constants

Configuration values that affect memory allocation are `#define` constants or struct fields read from the checkpoint file. There are no command-line argument parsers — the binary reads its configuration from the model checkpoint: [e8c3f1a](https://github.com/karpathy/llm.c/commit/e8c3f1a)

```c
// read model header from checkpoint
fread(&config, sizeof(GPT2Config), 1, model_file);
int V = config.vocab_size;
int L = config.num_layers;
int C = config.channels;
```

This eliminates argument parsing code entirely. The checkpoint file _is_ the configuration, which means there is exactly one way to configure the model: provide the right checkpoint.

## Forward/Backward Symmetry

The C code organizes forward and backward passes as paired functions. For every `*_forward` function there is a corresponding `*_backward` function with the same parameter layout: [e8c3f1a](https://github.com/karpathy/llm.c/commit/e8c3f1a)

```c
void layernorm_forward(float* out, float* mean, float* rstd, float* inp,
                       float* weight, float* bias, int B, int T, int C);
void layernorm_backward(float* dinp, float* dweight, float* dbias,
                        float* dout, float* inp, float* weight, float* mean,
                        float* rstd, int B, int T, int C);
```

This structural symmetry makes the backward pass navigable — the reader finds the backward function directly below its forward counterpart, and the parameter names share a consistent prefix (`d` for gradient). In PyTorch, autograd hides this pairing; in `llm.c`, it is explicit and visible.
