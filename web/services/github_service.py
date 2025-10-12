import os
import shutil
import subprocess
from datetime import datetime, timezone


def repo_cache_root():
    root = os.getenv("REPO_CACHE_DIR")
    if not root:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        root = os.path.join(base, ".repo_cache")
    os.makedirs(root, exist_ok=True)
    return root


def repo_dir(owner: str, name: str) -> str:
    safe = f"{owner.replace('/', '_')}__{name.replace('/', '_')}"

    return os.path.join(repo_cache_root(), safe)


def remote_url(owner: str, name: str) -> str:
    return f"https://github.com/{owner}/{name}.git"


def ensure_local_repo(owner: str, name: str) -> str:
    path = repo_dir(owner, name)
    url = remote_url(owner, name)

    # check if repo is already cloned
    if not os.path.isdir(path) or not os.path.isdir(os.path.join(path, ".git")):
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
        
        # don't checkout for faster performance
        subprocess.run(["git", "clone", "--no-checkout", url, path], check=True)
        return path

    try:
        current = subprocess.check_output(["git", "-C", path, "remote", "get-url", "origin"], text=True).strip()
        if current != url:
            subprocess.run(["git", "-C", path, "remote", "set-url", "origin", url], check=True)
    except subprocess.CalledProcessError:
        subprocess.run(["git", "-C", path, "remote", "add", "origin", url], check=True)

    return path


def safe_walk_py_files(root_dir: str):
    for root, _, filenames in os.walk(root_dir):
        # Skip .git directory
        parts = set(root.replace("\\", "/").split("/"))
        if ".git" in parts:
            continue
        for filename in filenames:
            if filename.endswith(".py"):
                yield root, filename


def fetch_files(owner, name, _branch, commit_sha):
    repo_path = ensure_local_repo(owner, name)
    files = []
    
    # checkout commit
    try:
        subprocess.run(["git", "-C", repo_path, "fetch", "--depth", "1", "origin", commit_sha], check=True)
        subprocess.run(["git", "-C", repo_path, "checkout", "-f", commit_sha], check=True)
    except subprocess.CalledProcessError:
        raise

    for root, filename in safe_walk_py_files(repo_path):
        file_path = os.path.join(root, filename)
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                code = f.read()
                rel_path = os.path.relpath(file_path, repo_path)
                files.append((rel_path, code))
        except Exception:
            pass

    return files


def get_closest_commit(repo_url: str, branch: str, date_str: str) -> tuple[str | None, str | None]:
    """
    Find the commit on `branch` of `repo_url` whose committer date is closest to `date_str`.

    - Searches on both sides of the target date (before and after)
    - Uses a local persistent clone with shallow fetch and progressive deepening
    - If both sides are equidistant, prefers the later commit (assumption documented)

    Returns:
      (commit_sha, commit_date_dd_mm_YYYY_HH_MM) or (None, None) if not found.
    """
    # Normalize target to UTC and use ISO format for git options
    target_dt = datetime.strptime(date_str, "%d/%m/%Y %H:%M").replace(tzinfo=timezone.utc)
    target_git_date = target_dt.isoformat(" ")

    # Derive owner/name from URL
    url_no_git = repo_url[:-4] if repo_url.endswith(".git") else repo_url
    parts = url_no_git.rstrip('/').split('/')
    owner, name = parts[-2], parts[-1]
    repo_path = ensure_local_repo(owner, name)

    def _get_commit_date(sha: str) -> datetime | None:
        if not sha:
            return None
        try:
            iso = subprocess.check_output(
                ["git", "-C", repo_path, "show", "-s", "--format=%cI", sha],
                text=True,
            ).strip()

            # Convert commit date to UTC for consistent comparisons
            dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
            return dt.astimezone(timezone.utc)
        except subprocess.CalledProcessError:
            return None

    def _rev_before() -> str:
        try:
            return subprocess.check_output(
                [
                    "git", "-C", repo_path, "rev-list", "-n", "1",
                    f"--before={target_git_date}", f"refs/remotes/origin/{branch}"
                ],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        except subprocess.CalledProcessError:
            return ""

    def _rev_after() -> str:
        try:
            return subprocess.check_output(
                [
                    "git", "-C", repo_path, "rev-list", "--reverse", "-n", "1",
                    f"--since={target_git_date}", f"refs/remotes/origin/{branch}"
                ],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        except subprocess.CalledProcessError:
            return ""

    def _select_best() -> tuple[str, datetime] | None:
        before_sha = _rev_before()
        after_sha = _rev_after()
        before_dt = _get_commit_date(before_sha)
        after_dt = _get_commit_date(after_sha)
        if not before_dt and not after_dt:
            return None
        if before_dt and after_dt:
            diff_before = abs((target_dt - before_dt).total_seconds())
            diff_after = abs((after_dt - target_dt).total_seconds())
            return (
                (after_sha, after_dt) if diff_after <= diff_before else (before_sha, before_dt)
            )
        if before_dt:
            return before_sha, before_dt
        return after_sha, after_dt

    try:
        max_depth = 131072
        fetched_since = False
        try:
            subprocess.run(
                [
                    "git", "-C", repo_path, "fetch", "--force", "--prune",
                    f"--shallow-since={target_git_date}", "origin",
                    f"{branch}:refs/remotes/origin/{branch}",
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            fetched_since = True
        except subprocess.CalledProcessError:
            subprocess.run(
                [
                    "git", "-C", repo_path, "fetch", "--depth", "32", "origin",
                    f"{branch}:refs/remotes/origin/{branch}",
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        # Initial selection after fetch
        best = _select_best()
        if best:
            best_sha, best_dt = best
            # If we fetched with shallow-since, the 'after' candidate is globally earliest after target.
            # We only need to deepen if 'before' is missing and could be the closer one.
            before_sha = _rev_before()
            if before_sha:
                return best_sha, best_dt.astimezone(timezone.utc).strftime("%d/%m/%Y %H:%M")

        # Progressive backward deepening loop
        depth = 32
        while True:
            before_sha = _rev_before()
            if before_sha:
                # Recompute best with the new history in place
                best2 = _select_best()
                if best2:
                    best_sha, best_dt = best2
                    return best_sha, best_dt.astimezone(timezone.utc).strftime("%d/%m/%Y %H:%M")

            if depth >= max_depth:
                # Try to unshallow fully and decide
                try:
                    subprocess.run(
                        [
                            "git", "-C", repo_path, "fetch", "--unshallow", "origin",
                            f"{branch}:refs/remotes/origin/{branch}"
                        ],
                        check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                except subprocess.CalledProcessError:
                    pass

                best3 = _select_best()
                if best3:
                    best_sha, best_dt = best3
                    return best_sha, best_dt.astimezone(timezone.utc).strftime("%d/%m/%Y %H:%M")
                return None, None

            deepen_by = depth if depth < 8192 else 8192
            subprocess.run(
                [
                    "git", "-C", repo_path, "fetch", f"--deepen={deepen_by}", "origin",
                    f"{branch}:refs/remotes/origin/{branch}"
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            depth += deepen_by
    except subprocess.CalledProcessError:
        pass

    return None, None


def get_commit_message(repo_url: str, sha: str) -> str | None:
    """Return the commit subject (first line) for the given SHA, or None if unavailable."""
    if not sha:
        return None
    # Derive owner/name from URL
    url_no_git = repo_url[:-4] if repo_url.endswith(".git") else repo_url
    parts = url_no_git.rstrip('/').split('/')
    owner, name = parts[-2], parts[-1]
    repo_path = ensure_local_repo(owner, name)
    try:
        subject = subprocess.check_output(
            ["git", "-C", repo_path, "show", "-s", "--format=%s", sha],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        return subject or None
    except subprocess.CalledProcessError:
        return None


def fetch_branches(owner, name):
    """Return list of branch names for the repo using the local cached clone."""
    try:
        repo_path = ensure_local_repo(owner, name)
        # Update refs from origin (quietly)
        try:
            subprocess.run(["git", "-C", repo_path, "fetch", "--prune", "origin"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            pass
        # List remote heads and parse branch names
        out = subprocess.check_output(["git", "-C", repo_path, "ls-remote", "--heads", "origin"], text=True)
        branches = []
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 2 and parts[1].startswith("refs/heads/"):
                branches.append(parts[1].replace("refs/heads/", ""))
        
        return branches
    except subprocess.CalledProcessError as e:
        return []