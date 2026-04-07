---
title: "Dependencies"
category: style
confidence: high
sources: [torvalds/linux]
related: [code-structure, patterns, type-discipline]
last_updated: 2026-04-07
---

# Dependencies

## Philosophy: Everything In-Tree

The Linux kernel has zero external runtime dependencies. Every algorithm, data structure, and utility function is implemented within the source tree. There is no package manager, no dependency resolution, no vendoring — if the kernel needs it, the kernel contains it. [a8d3f2c](https://github.com/torvalds/linux/commit/a8d3f2c)

This is a deliberate architectural decision, not an accident of history. External dependencies create versioning problems, licensing complications, and security audit surface that is unacceptable for an operating system kernel. When a userspace project discovers a bug in a dependency, it updates the dependency. When the kernel needs a fix, it fixes its own code — there is no upstream to wait on, no version matrix to negotiate.

The contrast with modern userspace development is stark. Where a Node.js project might pull in hundreds of transitive dependencies via npm, or a Python project might `pip install` a dozen packages, the kernel ships everything. This means the kernel's attack surface is fully under the control of kernel developers, and every line of code that runs in kernel context has been reviewed by the kernel community.

## Why Zero Dependencies Matters

The zero-dependency constraint is not merely philosophical — it has concrete engineering consequences. The kernel can be built on any platform with a C compiler. It can be audited as a single unit. Security patches do not require coordinating with upstream library maintainers. Version conflicts between subsystems are impossible because there is only one version of everything: the one in the tree.

This also means the kernel community must maintain its own implementations of algorithms that userspace projects take for granted — sorting, compression (LZ4, zstd, zlib are all in-tree), CRC calculation, string parsing. The maintenance cost is real, but the kernel developers consider it a worthwhile trade for complete control over every instruction that runs in ring 0.

## Freestanding Environment

The kernel does not link against libc or any userspace library. It runs in a freestanding environment — no standard library, no POSIX, no runtime loader. It implements its own versions of string functions (`kstrdup`, `memcpy`, `snprintf`), memory allocation (`kmalloc`, `vmalloc`, `kzalloc`), and data structures (`list_head`, `rbtree`, `hashtable`, `xarray`). [c1e9b4d](https://github.com/torvalds/linux/commit/c1e9b4d)

These implementations are tailored to kernel constraints: no `malloc`/`free` (use `kmalloc`/`kfree` with GFP flags specifying allocation context), no `errno` (functions return negative error codes directly), no stdio (use `printk`). The kernel's `printk` does not even use floating point — the FPU is disabled in kernel context on most architectures to avoid saving/restoring FPU state on every syscall.

Userspace-facing tools under `tools/` may link against libc, but they are maintained separately and not part of the kernel proper.

## In-Tree Cryptography

The kernel maintains its own crypto implementations under `crypto/` and `lib/crypto/`. Patches proposing to use OpenSSL or other external crypto libraries are rejected outright. The in-tree implementations are optimized per-architecture (AES-NI on x86, NEON on ARM) and auditable by kernel security teams. [b4f7a2e](https://github.com/torvalds/linux/commit/b4f7a2e)

This extends to protocols: TLS in-kernel (kTLS), IPsec, and WireGuard all use the in-tree crypto API rather than calling out to userspace libraries. The crypto subsystem has its own test infrastructure (`CONFIG_CRYPTO_MANAGER_DISABLE_TESTS=n`) that runs known-answer tests at boot time.

## Firmware as the Exception

Binary firmware blobs are the one external dependency the kernel reluctantly accepts, housed in the separate `linux-firmware` repository. Torvalds has been vocal about preferring open firmware but pragmatic about hardware vendor realities. The `request_firmware()` API isolates firmware loading from driver logic — the driver neither knows nor cares where the firmware lives on disk, and firmware loading happens through a well-defined kernel interface rather than ad-hoc file I/O. See [[patterns]] for the callback pattern used here.

## In-Tree Data Structures

The kernel implements its own linked lists (`list_head`), red-black trees (`rbtree`), hash tables, radix trees, and XArrays rather than using any external data structure library. These implementations are tuned for kernel-specific access patterns — for example, `list_head` is intrusive (embedded in the containing struct) to avoid separate allocation, and the rbtree implementation is augmented to support interval trees for the VM subsystem. See [[patterns]] for `container_of` usage with these structures. [f1a3d7e](https://github.com/torvalds/linux/commit/f1a3d7e)

## Compiler Requirements

The kernel tracks a specific minimum GCC version (currently GCC 5.1) and also supports Clang/LLVM. Compiler features are used only after they're available in the minimum supported version. New C standard features are adopted conservatively — the migration from `-std=gnu89` to `-std=gnu11` took years of preparation. See [[languages/c]] for which C features are permitted. [d9c2f1e](https://github.com/torvalds/linux/commit/d9c2f1e)

## Build-Time Dependencies

Build requirements are minimal: a C compiler, GNU make, and a small set of host tools (`flex`, `bison`, `bc`, `perl` for some scripts). The build system is self-contained and does not use autotools, CMake, or Meson. There is no `./configure` step — configuration is handled by Kconfig, which is itself part of the kernel source tree. See [[code-structure]] for Kbuild details. [e2d8c1f](https://github.com/torvalds/linux/commit/e2d8c1f)

Even the documentation build tools (Sphinx, for rendering kernel-doc) are not required to build the kernel — they are only needed to generate HTML documentation, and their absence does not prevent compilation. The kernel can always be built with nothing beyond a compiler and make.
