---
title: Testing
category: dimension
confidence: 0.85
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
The developer demonstrates a strong commitment to testing, though their approach varies significantly across different projects and contexts. Rather than adhering to a single testing philosophy, they adapt their testing strategy to match the project's needs and constraints.

## Test-Driven Development Practices

The developer frequently follows test-driven development (TDD) practices, particularly in library and SDK projects. They consistently write comprehensive test suites alongside feature implementations `[4b2549e8, 3bf8fd5a, 5d0cc745]`, often updating tests when changing functionality `[ffc925f6, 25e460eb]`. Their [[commit-hygiene]] often includes test verification details, with commits mentioning specific test counts and CI status `[e6f97adc, 48e94261, 950b63a7]`.

## Testing Frameworks and Tools

The developer is proficient with multiple testing frameworks across different [[language-idioms]]:

- **[[python]]**: Primarily uses pytest with async support, fixtures, and parametrized tests `[4b2549e8, ee3afd9b, a10bd57a]`
- **[[typescript]]**: Uses both Jest `[43686025, 4105fd6c]` and Bun test framework `[5d0cc745, d8af4e9f]` with describe/it/expect patterns
- **[[go]]**: Writes table-driven tests with subtests using t.Run() for different scenarios `[075180aa, ebbfa46b, 253ee445]`
- **[[kotlin]]**: Uses JUnit and AssertJ for fluent assertions `[52273b43, 3014518d, 97cadfc2]`
- **[[rust]]**: Writes comprehensive unit tests with edge case coverage `[e6f97adc, 48e94261, f3ed3faa]`

## Test Organization and Structure

The developer maintains consistent [[code-structure]] for tests:
- Test files mirror source structure with appropriate naming conventions (test_*.py, *_test.go, *.test.ts) `[c19afa74, f7e7e64a, 43686025]`
- Separates unit tests from integration tests, often gating live tests behind environment variables like ANTHROPIC_LIVE=1 `[28873dfc, 52273b43, 87d86d97]`
- Creates dedicated test fixtures and example data in organized directories `[fa27d432, 80b621ad]`

## Alternative Testing Approaches

Interestingly, the developer doesn't always rely on traditional unit tests. In some projects, particularly those focused on AI/ML evaluation, they build custom evaluation frameworks instead:

- Creates evaluation-driven development systems with automated test runners and grading agents `[b0cbd3df, 37292f37, 3d595115]`
- Builds benchmarking frameworks for performance measurement `[3d595115, b0cbd3df]`
- Implements validation scripts and automated checks rather than unit tests `[272de726, 76826f2c]`

## Testing Coverage Patterns

The developer's test coverage is generally comprehensive when present:
- Writes parametrized tests to cover multiple implementations `[4b2549e8, a10bd57a, 3bf8fd5a]`
- Includes edge cases and error scenarios `[767ef5f9, ca73b27d, b64dd4c0]`
- Uses snapshot testing for API responses `[c3017a22, 5ccd6b41, 75f2e082]`
- Reports test results across multiple architectures `[dc196034, e0a7ceb5, e98e5611]`

## Projects Without Tests

Notably, some projects lack automated tests entirely, particularly demo and prototype code `[826b2685, 7e1930ff, f55b539c]`. In these cases, the developer appears to rely on manual testing and comprehensive documentation instead. This suggests a pragmatic approach where testing investment matches the project's intended lifecycle and audience.

## CI/CD Integration

The developer integrates testing into their CI/CD workflows through GitHub Actions `[0313b3ec, 9eb13495]`, running separate jobs for different linters and multi-architecture builds. This demonstrates a commitment to automated quality assurance beyond just unit tests.
