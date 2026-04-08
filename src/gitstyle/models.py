"""Pydantic models for the gitstyle pipeline."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Stage 1 – Fetch
# ---------------------------------------------------------------------------

class CommitFile(BaseModel):
    filename: str
    status: str  # added, modified, removed, renamed
    additions: int = 0
    deletions: int = 0
    patch: Optional[str] = None


class RawCommit(BaseModel):
    sha: str
    repo: str  # owner/name
    message: str
    author: str
    authored_at: datetime
    additions: int = 0
    deletions: int = 0
    files: list[CommitFile] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Stage 2 – Sample
# ---------------------------------------------------------------------------

class CommitGroup(BaseModel):
    repo: str
    language: str
    commits: list[RawCommit]


class SampledCluster(BaseModel):
    repo: str
    language: str
    commits: list[RawCommit]
    total_in_group: int


# ---------------------------------------------------------------------------
# Stage 3 – Extract
# ---------------------------------------------------------------------------

class StyleDimension(str, Enum):
    CODE_STRUCTURE = "code-structure"
    NAMING = "naming-conventions"
    PATTERNS = "patterns"
    TYPE_DISCIPLINE = "type-discipline"
    TESTING = "testing"
    COMMENTS_DOCS = "comments-and-docs"
    DEPENDENCIES = "dependencies"
    COMMIT_HYGIENE = "commit-hygiene"
    LANGUAGE_IDIOMS = "language-idioms"


class Observation(BaseModel):
    dimension: StyleDimension
    claim: str
    evidence: list[str] = Field(default_factory=list)  # commit SHAs
    confidence: float = Field(ge=0.0, le=1.0, default=0.7)
    language: Optional[str] = None


class ClusterExtraction(BaseModel):
    repo: str
    language: str
    observations: list[Observation]


# ---------------------------------------------------------------------------
# Stage 4 – Compile
# ---------------------------------------------------------------------------

class WikiArticle(BaseModel):
    slug: str  # e.g. "code-structure"
    title: str
    category: str  # "dimension" or "language"
    confidence: float = Field(ge=0.0, le=1.0)
    source_repos: list[str] = Field(default_factory=list)
    content: str  # markdown body (no frontmatter)
    wikilinks: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Stage 5 – Lint
# ---------------------------------------------------------------------------

class LintSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class LintIssue(BaseModel):
    article: str  # slug
    severity: LintSeverity
    message: str
    suggestion: Optional[str] = None


class LintReport(BaseModel):
    issues: list[LintIssue] = Field(default_factory=list)
    passed: bool = True


# ---------------------------------------------------------------------------
# Fetch result (supports incremental)
# ---------------------------------------------------------------------------

class FetchResult(BaseModel):
    all_commits: list[RawCommit]
    new_commits: list[RawCommit]
    is_incremental: bool = False
