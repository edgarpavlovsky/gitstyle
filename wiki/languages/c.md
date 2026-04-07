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

This mirrors the single-file Python pattern (see [[code-structure]]) and makes `gcc train_gpt2.c -o train_gpt2 -lm` the complete build command.

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

The `gpt2_*` prefix convention creates a pseudo-namespace. Every function is prefixed with its "class."

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

This is explicitly pedagogical — it forces the reader to understand exactly where each parameter lives in memory.

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

This is intentionally slow but completely transparent. The CUDA version uses optimized kernels but the C reference prioritizes readability over performance.

## Error Handling Via Immediate Exit

Error handling uses `fprintf(stderr, ...)` followed by `exit(1)`. There are no error codes, no `errno` checking, no recovery paths. If something goes wrong (file not found, allocation failure), the program prints a message and exits: [e8c3f1a](https://github.com/karpathy/llm.c/commit/e8c3f1a)

```c
FILE *model_file = fopen(checkpoint_path, "rb");
if (model_file == NULL) {
    printf("Error opening model file\n");
    exit(1);
}
```

## Shape Comments Carry Over

The `(B, T, C)` shape comment convention from Python appears identically in C code. This creates visual continuity between the Python reference and C implementation: [e8c3f1a](https://github.com/karpathy/llm.c/commit/e8c3f1a)

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
