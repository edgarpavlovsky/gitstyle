---
title: Naming Conventions
category: dimension
confidence: 0.92
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
The developer demonstrates strong consistency in naming conventions across different languages and contexts, adapting appropriately to each language's idioms while maintaining clear patterns.

## File and Directory Naming

The developer predominantly uses **kebab-case** for file and directory names across all languages and contexts. This pattern is evident in shell scripts like `edit-issue-labels.sh` [76826f2c], TypeScript projects like `ask-user-question-previews` [826b2685], and Python projects like `session-report` [62f2063a]. The developer shows remarkable consistency with this convention, applying it to configuration files (`docker-compose.yml` [02777441]), command files (`triage-issue.md` [76c0cbae]), and demo directories (`browser-use-demo` [2eb3b14a]).

For Python-specific contexts, the developer sometimes uses **snake_case** for module and script files, as seen in `extract_form_structure.py` [4e6907a3] and `perf_takehome.py` [f88c9458]. This follows [[python]] conventions while maintaining consistency within Python-heavy projects.

## Language-Specific Conventions

### Python
The developer strictly follows PEP 8 conventions with **snake_case** for functions, variables, and module names [c19afa74], and **PascalCase** for classes [4b2549e8]. Private functions are prefixed with underscores, as seen in internal implementations [f144dcc4]. The developer shows particular attention to descriptive naming, avoiding abbreviations in favor of clarity.

### JavaScript/TypeScript
In [[javascript]] and [[typescript]] code, the developer uses **camelCase** for variables and functions [79d1d73f], **PascalCase** for classes, interfaces, and React components [826b2685], and **SCREAMING_SNAKE_CASE** for constants and environment variables [b64dd4c0]. This adherence to JavaScript conventions is consistent across different project types.

### Go
For [[go]] code, the developer follows standard Go conventions with **camelCase** for unexported identifiers and **PascalCase** for exported types and functions [76c83bf3]. Service types follow consistent patterns like `BetaAgentService` [f7e7e64a].

### Rust
In [[rust]] projects, the developer uses **snake_case** for functions and variables [e836df40], **PascalCase** for types and structs [543efbee], and **kebab-case** for crate names [09601e21], perfectly aligning with Rust conventions.

### Shell
For [[shell]] scripts, the developer uses **SCREAMING_SNAKE_CASE** for environment variables [849c98c8] and **kebab-case** for script filenames [76826f2c], following standard shell conventions.

## Special Naming Patterns

### Version Suffixes
The developer uses date-based version suffixes for evolving APIs, particularly evident in tool implementations like `BetaCodeExecutionTool20250522` [97cadfc2] and `ComputerTool20241022` [4b2549e8]. This pattern provides clear versioning while maintaining backward compatibility.

### Beta/Experimental Features
Beta or experimental features are consistently prefixed with 'Beta' or 'beta_', as seen in `BetaMessageParam` [90cd2008] and `beta_capability_support.rb` [66a7ff9f]. This clear labeling helps distinguish stable from experimental APIs.

### Descriptive Naming
The developer favors descriptive, self-documenting names over abbreviations. Examples include `resolve_numeric_refs_in_expr` [e836df40] rather than abbreviated forms, and verb-noun patterns for commands like `view-pdf` and `draft-response` [f55b539c].

## Cross-Language Consistency

Despite adapting to language-specific conventions, the developer maintains conceptual consistency. For instance, configuration keys consistently use **snake_case** across JSON and YAML files regardless of the consuming language (`bootstrap_url`, `mcp_servers` [90d7a0c0]).

The developer's naming conventions strongly support their [[code-structure]] practices by making file purposes immediately clear, and complement their [[comments-and-docs]] approach by reducing the need for explanatory comments through self-documenting names.
