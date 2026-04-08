---
title: CMake Style Guide
category: language
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
The developer demonstrates proficiency with CMake for embedded development, particularly with the Raspberry Pi Pico SDK. Their CMake files follow established [[patterns]] for SDK-based projects.

## Project Structure

The developer consistently uses the standard Pico SDK initialization pattern. Projects begin with `pico_sdk_init()` (d12d8cda, 749d90d4, b19dca57), establishing the foundation for Pico development. This reflects adherence to [[language-idioms]] specific to the Pico ecosystem.

## Target Definition

Executable targets are defined using the standard CMake pattern of `add_executable()` followed by `target_sources()`. This separation allows for cleaner [[code-structure]] and makes it easier to manage source files across different build configurations.

## Dependency Management

The developer uses `target_link_libraries()` to specify [[dependencies]], following CMake's modern target-based approach. This ensures proper propagation of include directories and compile flags from the Pico SDK to the application code.

## SDK Integration

The consistent use of Pico SDK CMake functions across multiple projects (d12d8cda, 749d90d4, b19dca57) demonstrates a standardized approach to embedded CMake configuration. This pattern enables USB output, hardware abstraction layers, and other SDK features through CMake's dependency system.
