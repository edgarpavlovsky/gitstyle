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

    def detect_account_type(self, username: str) -> str:
        """Detect whether a GitHub username is a 'User' or 'Organization'."""
        resp = self._request("GET", f"/users/{username}")
        return resp.json().get("type", "User")

    def list_repos(
        self,
        username: str,
        repos_filter: Optional[list[str]] = None,
        is_org: bool = False,
        max_repos: int = 0,
    ) -> list[str]:
        """List public repos for a user or org. Returns list of 'owner/name' strings.

        For orgs, sorts by stars (descending) so max_repos keeps the most popular.
        """
        repos: list[str] = []
        page = 1

        if is_org:
            endpoint = f"/orgs/{username}/repos"
            params_base = {"per_page": 100, "type": "public", "sort": "pushed"}
        else:
            endpoint = f"/users/{username}/repos"
            params_base = {"per_page": 100, "type": "owner", "sort": "updated"}

        while True:
            params = {**params_base, "page": page}
            resp = self._request("GET", endpoint, params=params)
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

        # For orgs, sort by stargazers (descending) and limit
        if is_org and max_repos > 0 and len(repos) > max_repos:
            # Re-fetch star counts for limiting
            starred = []
            for repo_name in repos:
                try:
                    resp = self._request("GET", f"/repos/{repo_name}")
                    stars = resp.json().get("stargazers_count", 0)
                    starred.append((repo_name, stars))
                except Exception:
                    starred.append((repo_name, 0))
            starred.sort(key=lambda x: x[1], reverse=True)
            repos = [name for name, _ in starred[:max_repos]]

        return repos

    def get_repo_languages(self, repo: str) -> list[str]:
        """Get languages for a repo. Returns list of language names."""
        resp = self._request("GET", f"/repos/{repo}/languages")
        return list(resp.json().keys())

    def list_commits(
        self,
        repo: str,
        author: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        max_commits: int = 500,
    ) -> list[dict]:
        """List commits in a repo. If author is given, filter by that author."""
        commits: list[dict] = []
        page = 1
        params: dict = {"per_page": 100, "page": page}
        if author:
            params["author"] = author
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
        author: Optional[str] = None,
        languages: list[str] | None = None,
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
            # Extract author login from the commit
            commit_author = (
                author
                or (c.get("author") or {}).get("login", "")
                or commit_data.get("author", {}).get("name", "unknown")
            )
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
                author=commit_author,
                authored_at=author_date,
                additions=stats.get("additions", 0),
                deletions=stats.get("deletions", 0),
                files=files,
                languages=languages or [],
            ))
        return results
