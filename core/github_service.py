"""GitHubReposService - holt Commits/Tags via `gh` CLI mit Thread-Safe-Cache.

Vorher in `help_views.py` als 3 freie Funktionen + Modul-Cache-Dict. Probleme
die hier geloest werden:

- **Thundering Herd:** 2 parallele Page-Renders auf Cache-Miss spawnten 8 statt
  4 Subprocesses. Jetzt: per-Key-Lock haelt zweite Anfrage zurueck bis der
  erste Refill fertig ist.
- **Race waehrend `invalidate()`:** `clear()` mitten in einem Read produzierte
  inkonsistente Snapshots (Repo A frisch, Repo B alt). Jetzt: alle Cache-Ops
  unter RLock.
- **`_local_head_sha` ohne Cache:** Sync-Git-Call pro Render ueber alle Repos.
  Jetzt: mit gleichem TTL gecacht.
"""
from __future__ import annotations

import json
import logging
import subprocess
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, TypeVar

logger = logging.getLogger('core')

T = TypeVar('T')


@dataclass(frozen=True)
class RepoSpec:
    """Statische Definition eines Repos."""
    display: str        # angezeigter Name z.B. "HumanBodyWeb"
    gh_repo: str        # "owner/name" wie von gh CLI erwartet
    local_dir: str      # Pfad-Komponente unter TOOLS_ROOT


@dataclass(frozen=True)
class RepoInfo:
    """Snapshot mit allem was die UI braucht."""
    spec: RepoSpec
    head_sha: str
    commits: list[dict]
    tags: list[dict]
    local_exists: bool
    local_path: str

    @property
    def gh_url(self) -> str:
        return f'https://github.com/{self.spec.gh_repo}'


class _TTLCache:
    """Mini-TTL-Cache mit RLock + per-Key-Lock-Sammlung gegen Thundering Herd."""

    def __init__(self, ttl_seconds: float) -> None:
        self._ttl = float(ttl_seconds)
        self._data: dict[str, tuple[float, object]] = {}
        # _data und _key_locks werden beide unter _meta_lock geschuetzt.
        self._meta_lock = threading.RLock()
        self._key_locks: dict[str, threading.Lock] = {}

    def get_or_compute(self, key: str, producer: Callable[[], T]) -> T:
        """Fresh value zurueckliefern. Andere Caller blockieren waehrend dem
        produzieren des gleichen Keys (per-key Lock)."""
        now = time.time()

        # Fast-path: lock-free read. dict.get ist GIL-atomar; falsch-stale-
        # eintrag waere harmlos, da wir gleich nochmal unter Lock pruefen.
        hit = self._data.get(key)
        if hit and (now - hit[0]) < self._ttl:
            return hit[1]  # type: ignore[return-value]

        # Slow-path: per-Key-Lock holen (erst Meta-Lock fuer das Lookup).
        with self._meta_lock:
            key_lock = self._key_locks.setdefault(key, threading.Lock())

        with key_lock:
            # Double-check: anderer Thread hat in der Zwischenzeit refilled.
            now = time.time()
            hit = self._data.get(key)
            if hit and (now - hit[0]) < self._ttl:
                return hit[1]  # type: ignore[return-value]
            value = producer()
            self._data[key] = (now, value)
            return value

    def clear(self) -> None:
        with self._meta_lock:
            self._data.clear()


class GitHubReposService:
    """Liefert RepoInfo pro RepoSpec, mit TTL-Cache + Thread-Safety.

    Kein User-Input geht in die `gh`-Aufrufe (Repo-Namen sind hardkodiert),
    daher keine Shell-Injection-Risiken.
    """

    DEFAULT_TTL_SECONDS = 300.0
    DEFAULT_COMMITS_PER_PAGE = 20
    DEFAULT_TAGS_PER_PAGE = 20

    # Timeouts -- gh CLI darf hartnaeckig sein bei flakey Netzwerk; lokales
    # git rev-parse sollte sub-second sein.
    _GH_TIMEOUT_S = 10.0
    _GIT_TIMEOUT_S = 5.0

    def __init__(
        self,
        specs: list[RepoSpec],
        tools_root: Path,
        ttl_seconds: float = DEFAULT_TTL_SECONDS,
        gh_binary: str = 'gh',
        git_binary: str = 'git',
    ) -> None:
        self._specs = list(specs)
        self._tools_root = Path(tools_root)
        self._gh = gh_binary
        self._git = git_binary
        self._cache = _TTLCache(ttl_seconds)

    def list_repos(self, refresh: bool = False) -> list[RepoInfo]:
        """Snapshot aller Repos. refresh=True wirft den Cache komplett weg."""
        if refresh:
            self._cache.clear()
        return [self._info_for(spec) for spec in self._specs]

    def invalidate(self) -> None:
        self._cache.clear()

    def _info_for(self, spec: RepoSpec) -> RepoInfo:
        local_path = self._tools_root / spec.local_dir
        exists = local_path.exists()
        head = self._head_sha(local_path) if exists else ''
        commits = self._commits(spec.gh_repo)
        tags = self._tags(spec.gh_repo)
        return RepoInfo(
            spec=spec,
            head_sha=head,
            commits=commits,
            tags=tags,
            local_exists=exists,
            local_path=str(local_path),
        )

    # --- gh CLI calls -----------------------------------------------------

    def _commits(self, repo: str) -> list[dict]:
        return self._cache.get_or_compute(
            f'commits:{repo}',
            lambda: self._fetch_commits(repo),
        )

    def _tags(self, repo: str) -> list[dict]:
        return self._cache.get_or_compute(
            f'tags:{repo}',
            lambda: self._fetch_tags(repo),
        )

    def _head_sha(self, repo_path: Path) -> str:
        return self._cache.get_or_compute(
            f'head:{repo_path}',
            lambda: self._fetch_head_sha(repo_path),
        )

    def _fetch_commits(self, repo: str) -> list[dict]:
        raw = self._gh_api(f'repos/{repo}/commits?per_page={self.DEFAULT_COMMITS_PER_PAGE}')
        if not raw:
            return []
        out: list[dict] = []
        for c in raw:
            commit = c.get('commit') or {}
            author = commit.get('author') or {}
            msg = (commit.get('message') or '').splitlines()[0][:240]
            out.append({
                'sha': (c.get('sha') or '')[:7],
                'msg': msg,
                'author': author.get('name') or '?',
                'date': (author.get('date') or '')[:10],
                'url': c.get('html_url') or '',
            })
        return out

    def _fetch_tags(self, repo: str) -> list[dict]:
        raw = self._gh_api(f'repos/{repo}/tags?per_page={self.DEFAULT_TAGS_PER_PAGE}')
        if not raw:
            return []
        return [
            {
                'name': t.get('name', ''),
                'sha': ((t.get('commit') or {}).get('sha') or '')[:7],
            }
            for t in raw
        ]

    def _gh_api(self, endpoint: str) -> list:
        """Ruft `gh api <endpoint>` auf und parst JSON. [] bei Fehler."""
        try:
            r = subprocess.run(
                [self._gh, 'api', endpoint],
                capture_output=True, text=True, timeout=self._GH_TIMEOUT_S,
                encoding='utf-8', errors='replace',
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            logger.error('gh api %s spawn/timeout: %s', endpoint, exc)
            return []
        if r.returncode != 0:
            logger.error('gh api %s rc=%s err=%s', endpoint, r.returncode, (r.stderr or '')[:200])
            return []
        try:
            data = json.loads(r.stdout or '[]')
        except json.JSONDecodeError as exc:
            logger.error('gh api %s json: %s', endpoint, exc)
            return []
        return data if isinstance(data, list) else []

    def _fetch_head_sha(self, repo_path: Path) -> str:
        try:
            r = subprocess.run(
                [self._git, '-C', str(repo_path), 'rev-parse', '--short=7', 'HEAD'],
                capture_output=True, text=True, timeout=self._GIT_TIMEOUT_S,
                encoding='utf-8', errors='replace',
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            logger.error('git rev-parse %s spawn/timeout: %s', repo_path, exc)
            return ''
        if r.returncode != 0:
            return ''
        return (r.stdout or '').strip()
