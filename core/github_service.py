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

import html
import json
import logging
import re
import subprocess
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, TypeVar

logger = logging.getLogger('core')

T = TypeVar('T')


# --- Mini-Markdown -> HTML ----------------------------------------------
# Portiert aus dem Assistant-Projekt (mail/views/VersionsView.py).
# Wir rendern Commit-Bodies als Bullet-Liste mit Bold-Prefix + Code,
# damit die Versionen-Seite optisch aussieht wie ein Changelog.

_MD_BOLD = re.compile(r'\*\*(.+?)\*\*')
_MD_INLINE_CODE = re.compile(r'`([^`\n]+)`')
_MD_BULLET = re.compile(r'^(\s*)[-*]\s+(.+)$')


def _md_inline(text: str) -> str:
    """text -> HTML mit <strong> + <code>. Escaped erstmal alles."""
    out = html.escape(text)
    out = _MD_INLINE_CODE.sub(r'<code>\1</code>', out)
    out = _MD_BOLD.sub(r'<strong>\1</strong>', out)
    return out


def _render_body_html(body: str) -> str:
    """Wandelt einen Commit-Body in HTML um.

    Erwartete Struktur (Konvention der Commit-Messages):
      Section-Header:    ohne Bullet, optional gefolgt von ':'
      Bullet-Eintrag:    '- ' oder '* ' am Zeilenanfang
      Sub-Bullet:        '  * ' / '  - ' (2+ Spaces Einrueckung)
      Freitext-Absatz:   alles andere

    Erste Zeile eines Bullets die mit 'Wort:' oder 'WortWort:' anfaengt
    bekommt das Wort vor dem ':' als <strong> (Konvention: 'Foo-Bar: text').
    """
    if not body:
        return ''
    out: list[str] = []
    cur_list_depth = 0   # 0 = ausserhalb, 1 = top-list, 2 = sub-list
    para_buf: list[str] = []

    def flush_para():
        if para_buf:
            txt = ' '.join(para_buf).strip()
            if txt:
                out.append(f'<p>{_md_inline(txt)}</p>')
            para_buf.clear()

    def close_lists(target_depth: int):
        nonlocal cur_list_depth
        while cur_list_depth > target_depth:
            out.append('</ul>')
            cur_list_depth -= 1

    def open_lists(target_depth: int):
        nonlocal cur_list_depth
        while cur_list_depth < target_depth:
            out.append('<ul>')
            cur_list_depth += 1

    for raw_line in body.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            flush_para()
            continue
        m = _MD_BULLET.match(line)
        if m:
            flush_para()
            indent = len(m.group(1).replace('\t', '    '))
            text = m.group(2).rstrip()
            depth = 1 if indent < 2 else 2
            if depth > cur_list_depth:
                open_lists(depth)
            elif depth < cur_list_depth:
                close_lists(depth)
            colon_pos = text.find(':')
            if 0 < colon_pos < 60 and ' ' not in text[:colon_pos]:
                head = text[:colon_pos]
                rest = text[colon_pos:]
                rendered = f'<strong>{html.escape(head)}</strong>{_md_inline(rest)}'
            else:
                rendered = _md_inline(text)
            out.append(f'<li>{rendered}</li>')
        else:
            stripped = line.strip()
            if stripped.endswith(':') and len(stripped) < 60:
                if cur_list_depth > 0:
                    close_lists(0)
                flush_para()
                out.append(f'<h3>{_md_inline(stripped)}</h3>')
            else:
                para_buf.append(stripped)

    flush_para()
    close_lists(0)
    return '\n'.join(out)


@dataclass(frozen=True)
class RepoSpec:
    """Statische Definition eines Repos."""
    display: str        # angezeigter Name z.B. "HumanBodyWeb"
    gh_repo: str        # "owner/name" wie von gh CLI erwartet
    local_dir: str      # Pfad-Komponente unter TOOLS_ROOT


@dataclass(frozen=True)
class RepoInfo:
    """Snapshot mit allem was die UI braucht.

    groups: List von Release-Gruppen (siehe `_group_by_tag`). Jede Gruppe
    enthaelt einen Tag-Release-Commit + die Commits die nach diesem Release
    folgten ("post_commits"). Die UI rendert das als Changelog mit
    Version-Spalte links + Content rechts.
    """
    spec: RepoSpec
    head_sha: str
    commits: list[dict]
    tags: list[dict]
    groups: list[dict]
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
        current_version: str = '',
        ttl_seconds: float = DEFAULT_TTL_SECONDS,
        gh_binary: str = 'gh',
        git_binary: str = 'git',
    ) -> None:
        self._specs = list(specs)
        self._tools_root = Path(tools_root)
        self._current_version = current_version
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
        groups = self._group_by_tag(commits, tags, self._current_version)
        return RepoInfo(
            spec=spec,
            head_sha=head,
            commits=commits,
            tags=tags,
            groups=groups,
            local_exists=exists,
            local_path=str(local_path),
        )

    @staticmethod
    def _group_by_tag(
        commits: list[dict], tags: list[dict], current_version: str,
    ) -> list[dict]:
        """Walks Commits (newest first) und gruppiert nach Git-Tag-Marker.

        Jeder Commit, dessen SHA von einem Tag referenziert wird, beendet
        eine Gruppe. Commits NEUER als der juengste getaggte Commit landen
        als 'post_commits' am Anfang der ersten Gruppe -- semantisch
        "Arbeit nach dem letzten Release".

        Ist current_version z.B. '0.49' wird die Gruppe mit Tag 'v0.49' (oder
        '0.49') als is_current=True markiert.

        Returns: Liste von Gruppen (neueste zuerst), jede mit:
            version_label   = 'v0.49' oder None (= unreleased)
            is_current      = matched current_version
            release_commit  = der getaggte Commit (oder None bei unreleased)
            post_commits    = neuere Commits vor dem Release-Marker
        """
        # SHA -> Tag-Name (1:1; mehrere Tags an einem SHA: letzter gewinnt)
        sha_to_tag: dict[str, str] = {}
        for t in tags:
            sha_full = t.get('sha_full') or t.get('sha') or ''
            name = t.get('name', '')
            if sha_full and name:
                sha_to_tag[sha_full] = name

        norm_current = (current_version or '').lstrip('v').strip()
        groups: list[dict] = []
        pending_post: list = []

        for c in commits:
            sha_full = c.get('sha_full') or c.get('sha') or ''
            tag_name = sha_to_tag.get(sha_full)
            if tag_name:
                groups.append({
                    'version_label': tag_name,
                    'is_current': tag_name.lstrip('v') == norm_current,
                    'release_commit': c,
                    'post_commits': pending_post,
                })
                pending_post = []
            else:
                pending_post.append(c)

        # Dangling Pre-Tag-Commits (vor erstem Tag) bewusst NICHT als Gruppe
        # rendern -- ist Repo-Vorgeschichte, kein "Release". Wer sie sehen
        # will, oeffnet das Repo auf GitHub.
        return groups

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
            full_msg = (commit.get('message') or '').strip()
            if '\n\n' in full_msg:
                subject, body = full_msg.split('\n\n', 1)
            else:
                subject, body = full_msg, ''
            # Co-Authored-By / Signed-off-by-Trailer raus -- ist Rauschen
            # im Changelog.
            body_lines = []
            for ln in body.splitlines():
                if ln.startswith(('Co-Authored-By:', 'Co-authored-by:',
                                  'Signed-off-by:')):
                    continue
                body_lines.append(ln)
            body = '\n'.join(body_lines).strip()
            sha_full = c.get('sha') or ''
            out.append({
                'sha': sha_full[:7],
                'sha_full': sha_full,
                'subject': subject.strip()[:240],
                'title': subject.strip()[:240],
                'body': body,
                'body_html': _render_body_html(body),
                'author': author.get('name') or '?',
                'date': (author.get('date') or '')[:10],
                'url': c.get('html_url') or '',
                # Backwards-compat fuer alte Templates die `msg` lesen:
                'msg': subject.strip()[:240],
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
                # sha_full noetig fuer _group_by_tag SHA-Matching gegen
                # commits[].sha_full.
                'sha_full': (t.get('commit') or {}).get('sha') or '',
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
