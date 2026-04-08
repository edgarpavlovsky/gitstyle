---
title: Dependencies
category: dimension
confidence: 0.88
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
The developer demonstrates a strongly minimalist philosophy toward external dependencies across all their projects, consistently preferring to implement functionality from scratch rather than relying on third-party libraries.

## Minimal External Dependencies

The developer maintains an exceptionally lean dependency footprint. In userspace projects, they rely almost exclusively on standard C libraries and POSIX system calls [bf9779cf, cea02218, d352c0df]. Even when implementing complex functionality like DSP algorithms, they prefer writing custom implementations over using established libraries [1c3e8c3b, f434a0e2, efa7475a]. This pattern extends to mathematical functions, which are implemented from scratch rather than pulled from external sources [d999fef1, b19dca57, e15140c3].

When external libraries are absolutely necessary, the developer is highly selective. They only add dependencies for specific, essential functionality — such as libpng for PNG handling and cairo for graphics [7a54bf82, 5107cd54]. The math library (-lm) often represents their only linked dependency beyond the standard C library [fba59060].

## Platform-Specific Approaches

In kernel development, the developer relies primarily on kernel internal APIs and subsystem-specific interfaces [3036cd0d, 86782c16, 66d64899]. They prefer platform-specific conditional compilation using #ifdef directives over external dependencies [5a28f140, c2a7e41f, c0970c42]. Feature availability is ensured through platform-specific defines like _GNU_SOURCE and _XOPEN_SOURCE rather than legacy alternatives [5a28f140].

For embedded projects, the developer leverages hardware-specific SDKs like the Raspberry Pi Pico SDK, but maintains the same minimalist approach by only using essential hardware libraries (hardware_pwm, hardware_adc, hardware_i2c, hardware_watchdog) [d12d8cda, 749d90d4, b19dca57].

## Dependency Management Strategies

The developer employs different dependency management strategies based on the project context. In kernel development, they use the Kconfig system extensively with explicit select/depends statements for managing build-time configuration options and driver dependencies [61c0b2ae, 1791c390]. Complex dependency chains across subsystems are handled through careful merge ordering [3036cd0d, 86782c16, 66d64899].

For userspace projects, the developer transitions from hardcoded library paths to pkg-config when cleaning up initial implementations, demonstrating a preference for portable dependency management [fcf22836]. Their [[makefile]] configurations reflect this minimalist approach, using only essential system utilities and avoiding complex build systems [1ac1fc73, 4c3c754d].

## Subsystem Boundaries

In large-scale projects like the Linux kernel, the developer maintains strict subsystem boundaries with minimal cross-subsystem dependencies [3036cd0d, 86782c16, 66d64899]. They manage complex dependency trees through clear maintainer boundaries and a pull request workflow [3036cd0d, 86782c16, 66d64899], regularly updating the MAINTAINERS file to track subsystem ownership [abacaf55, 1c9982b4].

This disciplined approach to dependencies aligns with their broader [[code-structure]] philosophy, emphasizing self-contained, maintainable code that minimizes external coupling. The preference for implementing functionality directly rather than importing it reflects their deep understanding of [[language-idioms]] and commitment to keeping systems lean and comprehensible.
