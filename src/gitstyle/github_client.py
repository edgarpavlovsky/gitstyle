"""GitHub REST API client for fetching commit data."""

from __future__ import annotations

import time
from typing import Optional

import httpx
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from gitstyle.models import CommitFile, RawCommit

console = Console()

GITHUB_API = "https://api.github.com"


class GitHubClient:
    def __init__(self, token: Optional[str] = None):
        headers = {"Accept": "application/vnd.github+json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._client = httpx.Client(
            base_url=GITHUB_API,
            headers=headers,
            timeout=30.0,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        resp = self._client.request(method, url, **kwargs)
        if resp.status_code == 403 and "rate limit" in resp.text.lower():
            reset = int(resp.headers.get("X-RateLimit-Reset", time.time() + 60))
            wait = max(reset - int(time.time()), 1)
            console.print(f"[yellow]Rate limited. Waiting {wait}s...[/yellow]")
            time.sleep(wait)
            resp = self._client.request(method, url, **kwargs)
        resp.raise_for_status()
        return resp

    def list_repos(self, username: str, repos_filter: Optional[list[str]] = None) -> list[str]:
        """List public repos for a user. Returns list of 'owner/name' strings."""
        repos: list[str] = []
        page = 1
        while True:
            resp = self._request(
                "GET",
                f"/users/{username}/repos",
                params={"per_page": 100, "page": page, "type": "owner", "sort": "updated"},
            )
            data = resp.json()
            if not data:
                break
            for r in data:
                if r.get("fork"):
                    continue
                full_name = r["full_name"]
                if repos_filter and full_name not in repos_filter:
                    continue
                repos.append(full_name)
            page += 1
        return repos

    def get_repo_languages(self, repo: str) -> list[str]:
        """Get languages for a repo. Returns list of language names."""
        resp = self._request("GET", f"/repos/{repo}/languages")
        return list(resp.json().keys())

    def list_commits(
        self,
        repo: str,
        author: str,
        since: Optional[str] = None,
        until: Optional[str] = None,
        max_commits: int = 500,
    ) -> list[dict]:
        """List commits by author in a repo. Returns raw API dicts."""
        commits: list[dict] = []
        page = 1
        params: dict = {"author": author, "per_page": 100, "page": page}
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        while len(commits) < max_commits:
            params["page"] = page
            try:
                resp = self._request("GET", f"/repos/{repo}/commits", params=params)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 409:  # empty repo
                    break
                raise
            data = resp.json()
            if not data:
                break
            commits.extend(data)
            if len(data) < 100:
                break
            page += 1
        return commits[:max_commits]

    def get_commit_detail(self, repo: str, sha: str) -> dict:
        """Get full commit detail including files/patch."""
        resp = self._request("GET", f"/repos/{repo}/commits/{sha}")
        return resp.json()

    def fetch_commits_for_repo(
        self,
        repo: str,
        author: str,
        languages: list[str],
        since: Optional[str] = None,
        until: Optional[str] = None,
        max_commits: int = 500,
    ) -> list[RawCommit]:
        """Fetch and parse all commits for a single repo."""
        raw_commits = self.list_commits(repo, author, since, until, max_commits)
        results: list[RawCommit] = []
        for c in raw_commits:
            commit_data = c.get("commit", {})
            author_date = commit_data.get("author", {}).get("date", "")
            sha = c["sha"]
            # Get detail for files
            try:
                detail = self.get_commit_detail(repo, sha)
            except httpx.HTTPStatusError:
                detail = {}
            files = []
            for f in detail.get("files", []):
                files.append(CommitFile(
                    filename=f.get("filename", ""),
                    status=f.get("status", "modified"),
                    additions=f.get("additions", 0),
                    deletions=f.get("deletions", 0),
                    patch=f.get("patch"),
                ))
            stats = detail.get("stats", {})
            results.append(RawCommit(
                sha=sha,
                repo=repo,
                message=commit_data.get("message", ""),
                author=author,
                authored_at=author_date,
                additions=stats.get("additions", 0),
                deletions=stats.get("deletions", 0),
                files=files,
                languages=languages,
            ))
        return results
