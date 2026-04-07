"""Data models for the gitstyle pipeline."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RepoInfo(BaseModel):
    """Metadata about a GitHub repository."""

    name: str
    full_name: str
    description: str | None = None
    language: str | None = None
    languages: dict[str, int] = Field(default_factory=dict)
    is_fork: bool = False
    stars: int = 0
    url: str = ""


class CommitFile(BaseModel):
    """A file changed in a commit."""

    filename: str
    status: str = ""  # added, modified, removed, renamed
    additions: int = 0
    deletions: int = 0
    patch: str | None = None


class Commit(BaseModel):
    """A single Git commit with metadata and diff."""

    sha: str
    repo: str  # full_name e.g. "edgarpavlovsky/project"
    message: str
    date: str
    files: list[CommitFile] = Field(default_factory=list)
    additions: int = 0
    deletions: int = 0
    url: str = ""


class CommitCluster(BaseModel):
    """A group of related commits for LLM analysis."""

    label: str  # e.g. "edgarpavlovsky/project:python"
    repo: str
    language: str | None = None
    commits: list[Commit] = Field(default_factory=list)


class StyleObservation(BaseModel):
    """A structured observation about engineering style from one cluster."""

    cluster_label: str
    category: str  # one of the 9 style dimensions
    observation: str
    evidence: list[str] = Field(default_factory=list)  # commit SHAs
    confidence: str = "medium"  # low, medium, high


class StyleExtractionResult(BaseModel):
    """All observations from a single cluster extraction."""

    cluster_label: str
    observations: list[StyleObservation] = Field(default_factory=list)


class WikiArticle(BaseModel):
    """A compiled wiki article ready to be written to disk."""

    slug: str  # filename without .md
    title: str
    category: str
    content: str
    sources: list[str] = Field(default_factory=list)  # repo names
    confidence: str = "medium"
    related: list[str] = Field(default_factory=list)  # slugs of related articles


class LintIssue(BaseModel):
    """An issue found during the lint pass."""

    article: str  # slug
    severity: str  # info, warning, error
    message: str
    suggestion: str | None = None
