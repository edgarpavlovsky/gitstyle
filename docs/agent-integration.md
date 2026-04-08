# Agent Integration

The primary purpose of a gitstyle wiki is to give coding agents context about your engineering style. This page shows how to set that up for popular agents.

## Claude Code

Add to your project's `CLAUDE.md` (or `.claude/instructions.md`):

```markdown
## Engineering Style

Load and follow the engineering style wiki in the `wiki/` directory for all code in this project.
Start with wiki/index.md for an overview, then reference individual articles for specific conventions.

Key articles:
- wiki/naming-conventions.md — naming patterns for variables, functions, files
- wiki/patterns.md — error handling, architecture patterns
- wiki/code-structure.md — file organization and module boundaries
- wiki/testing.md — test structure and conventions
```

Claude Code will read these files when working on your codebase and follow the conventions documented in them.

## Cursor

Add to `.cursorrules` in your project root:

```
When writing code for this project, follow the engineering style conventions
documented in the wiki/ directory:

- wiki/naming-conventions.md for naming patterns
- wiki/patterns.md for error handling and architecture patterns
- wiki/testing.md for test structure and conventions
- wiki/code-structure.md for file organization

Every article includes specific examples from real commits. Follow these patterns.
```

## Aider

Add to `.aider.conf.yml`:

```yaml
read:
  - wiki/index.md
  - wiki/naming-conventions.md
  - wiki/patterns.md
  - wiki/code-structure.md
  - wiki/testing.md
```

Or pass wiki files as read-only context:

```bash
aider --read wiki/index.md --read wiki/naming-conventions.md
```

## Windsurf

Add to `.windsurfrules` in your project root:

```
Follow the engineering style conventions documented in the wiki/ directory.
Start with wiki/index.md for the overview, then reference specific articles
as needed (naming-conventions, patterns, code-structure, testing, etc.).
Each article cites real commit evidence — follow the documented patterns.
```

## Generic Pattern (Any Agent)

If your agent supports a system prompt or context injection, load the wiki programmatically:

```python
from pathlib import Path

# Load the full wiki as context
wiki_dir = Path("wiki")
style_context = ""
for md_file in sorted(wiki_dir.rglob("*.md")):
    style_context += f"\n\n--- {md_file.relative_to(wiki_dir)} ---\n"
    style_context += md_file.read_text()

# Feed to your agent's system prompt
system_prompt = f"""You are writing code for a developer with specific
engineering preferences. Their style guide:

{style_context}

Follow these conventions when writing or reviewing code."""
```

### Selective Loading

For large wikis or limited context windows, load only the most relevant articles:

```python
# Load only high-confidence articles
import yaml

for md_file in wiki_dir.rglob("*.md"):
    text = md_file.read_text()
    if text.startswith("---"):
        fm_end = text.find("---", 3)
        frontmatter = yaml.safe_load(text[3:fm_end])
        if frontmatter.get("confidence", 0) >= 0.7:
            style_context += text
```

## Organization Wikis

For org wikis (e.g., `gitstyle run anthropic`), the wiki captures team-wide patterns. These are particularly useful as shared context for a whole team:

```markdown
## Team Engineering Standards

Our engineering style is documented in wiki/ (generated from our GitHub commit history).
All team members and coding agents should follow these patterns:

- wiki/code-structure.md — how we organize code
- wiki/patterns.md — standard patterns for error handling, async, etc.
- wiki/naming-conventions.md — naming standards
- wiki/commit-hygiene.md — commit message format and PR conventions
```

## Tips

1. **Commit the wiki to your repo** — this way it's always available to any agent working on your codebase, and it tracks version history.

2. **Re-run periodically** — `gitstyle run` is incremental, so re-running is cheap and keeps the wiki current with your evolving style.

3. **Focus on high-confidence articles** — articles with 80%+ confidence have strong evidence across multiple repos. Lower-confidence articles may be less reliable.

4. **Use the confidence scores** — agents can prioritize more confident patterns over tentative ones. A confidence of 0.9 means "very consistent pattern" while 0.5 means "sometimes, depends on context."

5. **Language-specific articles are most actionable** — `languages/python.md` will have the most concrete, directly applicable patterns for Python code.
