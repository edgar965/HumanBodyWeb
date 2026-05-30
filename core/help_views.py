"""Hilfe-Seiten: Logs (Logviewer) + Versionen (GitHub-Commits pro Repo).

Slim Views — die Arbeit machen `LogService` und `GitHubReposService`.
"""
from __future__ import annotations

import logging
from pathlib import Path

from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from core.github_service import GitHubReposService, RepoSpec
from core.logs_service import LogService

logger = logging.getLogger('core')


# Singletons (Modul-Level OK -- beide intern Thread-Safe).
_log_service = LogService(Path(settings.BASE_DIR) / 'logs')

_REPO_SPECS = [
    RepoSpec('HumanBodyWeb',     'edgar965/HumanBodyWeb',     'HumanBodyWeb'),
    RepoSpec('HumanBody',        'edgar965/HumanBody',        'HumanBody'),
    RepoSpec('HumanBodyBlender', 'edgar965/HumanBodyBlender', 'HumanBodyBlender'),
    RepoSpec('VideoToBVH',       'edgar965/VideoToBVH',       'VideoToBVH'),
]
_repos_service = GitHubReposService(
    _REPO_SPECS,
    Path(settings.TOOLS_ROOT),
    current_version=getattr(settings, 'VERSION', ''),
)


# --- Logs -----------------------------------------------------------------

_VALID_LINE_RANGE = (50, 5000)


def _parse_max_lines(raw: str | None, default: int = 500) -> int:
    """GET-Param-Validation mit Clamp auf Range."""
    try:
        v = int(raw) if raw else default
    except (TypeError, ValueError):
        v = default
    lo, hi = _VALID_LINE_RANGE
    return max(lo, min(hi, v))


def help_logs(request):
    """Logs-Seite mit zwei Tabs: Exceptions + Alle Logs."""
    source_key = request.GET.get('source', _log_service.AGGREGATE_KEY)
    if not _log_service.is_valid_key(source_key):
        source_key = _log_service.AGGREGATE_KEY
    max_lines = _parse_max_lines(request.GET.get('lines'))
    order = (request.GET.get('order') or 'desc').lower()

    if source_key == _log_service.AGGREGATE_KEY:
        all_lines, exception_lines = _log_service.read_aggregate(max_lines)
        out_path = err_path = None
    else:
        all_lines, exception_lines = _log_service.read_single_source(source_key, max_lines)
        out_path, err_path = _log_service.paths_for_key(source_key)

    if order != 'asc':
        all_lines = list(reversed(all_lines))
        exception_lines = list(reversed(exception_lines))

    return render(request, 'help_logs.html', {
        'title': 'Logs',
        'source_key': source_key,
        'source_label': _log_service.label_for(source_key),
        'sources': [{'key': k, 'label': lab} for k, lab in _log_service.all_keys_with_labels()],
        'exception_lines': exception_lines,   # list[LogLine]
        'all_lines': all_lines,                # list[LogLine]
        'exception_count': len(exception_lines),
        'all_count': len(all_lines),
        'max_lines': max_lines,
        'order': order,
        'out_path': str(out_path) if out_path else '',
        'err_path': str(err_path) if err_path else '',
    })


@require_POST
def api_log_clear(request):
    """Truncate alle Logs der gewaehlten Source."""
    from django.contrib import messages as _msg
    source_key = (request.POST.get('source') or '').strip()
    if not _log_service.is_valid_key(source_key):
        _msg.error(request, f'Unbekannte Log-Quelle: {source_key}')
        return redirect('help_logs')

    label = _log_service.label_for(source_key)
    res = _log_service.truncate(source_key)

    parts = []
    if res.cleared:
        parts.append(f'{res.cleared} Datei(en) geleert')
    if res.locked:
        parts.append(f'{len(res.locked)} gesperrt: {", ".join(res.locked)}')
    if res.failed:
        parts.append(f'{len(res.failed)} Fehler: {"; ".join(res.failed)}')
    summary = '; '.join(parts) if parts else 'nichts zu leeren'

    if res.failed or res.locked:
        _msg.warning(request, f'{label}: {summary}.')
    else:
        _msg.success(request, f'{label}: {summary}.')
    logger.info('api_log_clear source=%s result=%s', source_key, summary)
    return redirect(f"{reverse('help_logs')}?source={source_key}")


# --- Versions -------------------------------------------------------------

def help_versions(request):
    """Versionen-Seite: GitHub-Commits + Tags + lokaler HEAD pro Repo.

    Per-key Locks im Service halten parallele Refreshes zurueck. Cache TTL
    5 min damit GitHub-API-Limit nicht verbrannt wird (60 req/h unauth)."""
    refresh = request.GET.get('refresh') == '1'
    repos = _repos_service.list_repos(refresh=refresh)
    return render(request, 'help_versions.html', {
        'title': 'Versionen',
        'current_version': getattr(settings, 'VERSION', ''),
        'repos': repos,
    })
