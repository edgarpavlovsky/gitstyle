---
title: Kotlin Style Guide
category: language
confidence: 0.88
source_repos:
  - anthropics/ConstitutionalHarmlessnessPaper
  - anthropics/anthropic-cli
  - anthropics/anthropic-sdk-go
  - anthropics/anthropic-sdk-java
  - anthropics/anthropic-sdk-python
  - anthropics/anthropic-sdk-ruby
  - anthropics/anthropic-sdk-typescript
  - anthropics/anthropic-tools
  - anthropics/buffa
  - anthropics/claude-agent-sdk-demos
  - anthropics/claude-agent-sdk-python
  - anthropics/claude-agent-sdk-typescript
  - anthropics/claude-code
  - anthropics/claude-code-action
  - anthropics/claude-code-base-action
  - anthropics/claude-code-monitoring-guide
  - anthropics/claude-code-security-review
  - anthropics/claude-cookbooks
  - anthropics/claude-plugins-official
  - anthropics/claude-quickstarts
  - anthropics/claudes-c-compiler
  - anthropics/courses
  - anthropics/evals
  - anthropics/financial-services-plugins
  - anthropics/hh-rlhf
  - anthropics/knowledge-work-plugins
  - anthropics/life-sciences
  - anthropics/original_performance_takehome
  - anthropics/prompt-eng-interactive-tutorial
  - anthropics/skills
last_updated: 2026-04-08
---
# Kotlin Style Guide

This developer demonstrates a mature, idiomatic Kotlin development style that fully embraces the language's modern features and design philosophy.

## Core Language Features

The codebase shows consistent use of Kotlin's distinctive [[language-idioms]]:

### Data Classes and Sealed Classes
Extensive use of data classes for value objects and DTOs is evident throughout commits 52273b43, 26250c82, and 97cadfc2. The developer leverages Kotlin's concise syntax for immutable data structures, preferring data classes over traditional POJOs. Sealed classes appear in eb369e5b, demonstrating sophisticated type modeling for exhaustive when expressions.

### Extension Functions
The developer actively uses extension functions to enhance existing types with domain-specific functionality (52273b43, 97cadfc2). This approach keeps code organized and readable while avoiding utility class proliferation.

### Null Safety
Kotlin's null safety system is embraced throughout, with consistent use of safe call operators (`?.`) and elvis operators (`?:`) visible in commits 26250c82 and 5137631b. The developer clearly understands and leverages Kotlin's type system to eliminate null pointer exceptions at compile time.

## Java Interoperability

The codebase demonstrates thoughtful Java interop patterns, particularly through the use of `kotlin.jvm.optionals` (5137631b). This shows awareness of bridging Kotlin's nullable types with Java's Optional pattern when working with mixed codebases or Java libraries.

## Overall Philosophy

This is definitively a "Kotlin-first" development approach. Rather than writing Java-style code in Kotlin syntax, the developer fully embraces Kotlin's expressive power, functional programming features, and concise syntax. The consistent use of these patterns across multiple commits (52273b43, 26250c82, 97cadfc2, eb369e5b) indicates this is a deliberate architectural choice rather than sporadic usage.
