"""GitHub API client for fetching commit history."""

from __future__ import annotations

import httpx
from rich.progress import Progress, SpinnerColumn, TextColumn

from gitstyle.models import Commit, CommitFile, RepoInfo


class GitHubClient:
    """Fetches repos and commits from the GitHub REST API."""

    BASE = "https://api.github.com"

    def __init__(self, token: str | None = None) -> None:
        headers = {"Accept": "application/vnd.github+json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._client = httpx.Client(
            base_url=self.BASE,
            headers=headers,
            timeout=30.0,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> GitHubClient:
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def _paginate(self, url: str, params: dict | None = None) -> list[dict]:
        """Fetch all pages from a paginated endpoint."""
        params = dict(params or {})
        params.setdefault("per_page", 100)
        results: list[dict] = []
        while url:
            resp = self._client.get(url, params=params)
            resp.raise_for_status()
            results.extend(resp.json())
            # Follow Link: <url>; rel="next"
            link = resp.headers.get("Link", "")
            url = ""
            for part in link.split(","):
                if 'rel="next"' in part:
                    url = part.split(";")[0].strip(" <>")
            params = {}  # params are baked into the next URL
        return results

    def get_account_type(self, name: str) -> str:
        """Check if a GitHub name is a 'User' or 'Organization'."""
        resp = self._client.get(f"/users/{name}")
        resp.raise_for_status()
        return resp.json().get("type", "User")

    def get_user_repos(
        self,
        username: str,
        include_forks: bool = False,
    ) -> list[RepoInfo]:
        """List repos owned by a user."""
        raw = self._paginate(f"/users/{username}/repos", {"sort": "pushed"})
        repos = []
        for r in raw:
            if not include_forks and r.get("fork"):
                continue
            repos.append(
                RepoInfo(
                    name=r["name"],
                    full_name=r["full_name"],
                    description=r.get("description"),
                    language=r.get("language"),
                    is_fork=r.get("fork", False),
                    stars=r.get("stargazers_count", 0),
                    url=r.get("html_url", ""),
                )
            )
        return repos

    def get_org_repos(
        self,
        org: str,
        include_forks: bool = False,
    ) -> list[RepoInfo]:
        """List repos owned by an organization, sorted by stars descending."""
        raw = self._paginate(f"/orgs/{org}/repos", {"sort": "stars", "direction": "desc"})
        repos = []
        for r in raw:
            if not include_forks and r.get("fork"):
                continue
            repos.append(
                RepoInfo(
                    name=r["name"],
                    full_name=r["full_name"],
                    description=r.get("description"),
                    language=r.get("language"),
                    is_fork=r.get("fork", False),
                    stars=r.get("stargazers_count", 0),
                    url=r.get("html_url", ""),
                )
            )
        return repos

    def get_repo_languages(self, full_name: str) -> dict[str, int]:
        """Get language breakdown for a repo."""
        resp = self._client.get(f"/repos/{full_name}/languages")
        resp.raise_for_status()
        return resp.json()

    def get_commits(
        self,
        full_name: str,
        author: str,
        max_commits: int = 200,
        since: str | None = None,
        until: str | None = None,
    ) -> list[Commit]:
        """Fetch commits authored by a user in a repo."""
        params: dict = {"author": author}
        if since:
            params["since"] = since
        if until:
            params["until"] = until

        raw = self._paginate(f"/repos/{full_name}/commits", params)
        commits: list[Commit] = []
        for item in raw[:max_commits]:
            c = item.get("commit", {})
            commits.append(
                Commit(
                    sha=item["sha"],
                    repo=full_name,
                    message=c.get("message", ""),
                    date=c.get("author", {}).get("date", ""),
                    url=item.get("html_url", ""),
                )
            )
        return commits

    def get_commit_detail(self, full_name: str, sha: str) -> Commit:
        """Fetch full commit detail including file diffs."""
        resp = self._client.get(f"/repos/{full_name}/commits/{sha}")
        resp.raise_for_status()
        data = resp.json()
        c = data.get("commit", {})
        stats = data.get("stats", {})
        files = [
            CommitFile(
                filename=f["filename"],
                status=f.get("status", ""),
                additions=f.get("additions", 0),
                deletions=f.get("deletions", 0),
                patch=f.get("patch"),
            )
            for f in data.get("files", [])
        ]
        return Commit(
            sha=data["sha"],
            repo=full_name,
            message=c.get("message", ""),
            date=c.get("author", {}).get("date", ""),
            files=files,
            additions=stats.get("additions", 0),
            deletions=stats.get("deletions", 0),
            url=data.get("html_url", ""),
        )

    def fetch_all(
        self,
        username: str,
        include_forks: bool = False,
        include_repos: list[str] | None = None,
        exclude_repos: list[str] | None = None,
        max_commits_per_repo: int = 200,
        max_repos: int = 0,
        since: str | None = None,
        until: str | None = None,
    ) -> tuple[list[RepoInfo], list[Commit], str]:
        """Fetch all repos and commits for a user or org.

        Returns (repos, commits, account_type) where account_type is 'User' or 'Organization'.
        """
        account_type = self.get_account_type(username)

        if account_type == "Organization":
            repos = self.get_org_repos(username, include_forks=include_forks)
        else:
            repos = self.get_user_repos(username, include_forks=include_forks)

        if include_repos:
            repos = [r for r in repos if r.name in include_repos]
        if exclude_repos:
            repos = [r for r in repos if r.name not in exclude_repos]

        # Cap repos (sorted by stars for orgs, already sorted by pushed for users)
        if max_repos > 0:
            repos = repos[:max_repos]

        all_commits: list[Commit] = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task("Fetching commits...", total=len(repos))
            for repo in repos:
                progress.update(task, description=f"Fetching {repo.full_name}...")
                try:
                    repo.languages = self.get_repo_languages(repo.full_name)
                except httpx.HTTPStatusError:
                    pass
                try:
                    commits = self.get_commits(
                        repo.full_name,
                        author=username,
                        max_commits=max_commits_per_repo,
                        since=since,
                        until=until,
                    )
                    all_commits.extend(commits)
                except httpx.HTTPStatusError:
                    pass
                progress.advance(task)

        return repos, all_commits, account_type
