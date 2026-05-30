"""LogService - kapselt Log-Quellen, Tail-Reads, Exception-Scan, Truncate.

Portiert aus dem CamTrack-Projekt (app/services/system/logs_service.py), aber
mit ein paar Bugfixes:

- `tail_lines` zaehlte O(N**2) durch wiederholtes count() ueber den gesamten
  Buffer, und hatte einen Off-by-one (`<=` statt `<`). Jetzt: inkrementelles
  Zaehlen, korrekte Abbruch-Bedingung, Live-Size statt stat()-Cache (race-
  resistent bei parallelem Truncate).
- `read_aggregate_lines` sortierte nach Timestamp NACH dem Merge — Traceback-
  Continuation-Frames (Timestamp '') landeten dabei verschachtelt aus
  verschiedenen Quellen. Jetzt: `_stitch_continuations` pro Quelle vor dem
  Merge, dann heapq.merge() statt sort().
- Klassifizierung ist nicht mehr Teil des Services — `LogClassifier` macht
  das stateful (siehe Bug #6).
"""
from __future__ import annotations

import heapq
import logging
import re
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator, Sequence

from core.log_classifier import LogClassifier

logger = logging.getLogger('core')


@dataclass(frozen=True)
class LogSource:
    key: str
    label: str
    out_name: str | None
    err_name: str | None


@dataclass(frozen=True)
class LogLine:
    """Eine Log-Zeile mit vor-berechneter Severity-Klasse."""
    text: str
    severity: str  # 'critical' | 'err' | 'trace' | 'warn' | 'info'


class LogService:
    """Single source of truth fuer Log-Files."""

    AGGREGATE_KEY = 'all'
    AGGREGATE_LABEL = 'Alle Quellen'

    # errors.log haengt als Cross-Cutting-Aggregat von WARNING+ aus allen
    # Producern dran. Ins "Alle Quellen"-Aggregat aufnehmen wuerde jede
    # Error-Zeile doppelt anzeigen -> getrennt halten.
    DEFAULT_SOURCES: tuple[LogSource, ...] = (
        LogSource('django',   'Django Server',   'django.log',   None),
        LogSource('core',     'HumanBody API',   'core.log',     None),
        LogSource('pipeline', 'Video-to-BVH',    'pipeline.log', None),
        LogSource('client',   'Browser / JS',    'client.log',   None),
    )
    DEFAULT_ERROR_SOURCE = LogSource(
        'errors', 'Errors (alle Quellen)', 'errors.log', None,
    )

    _TS_RE = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')
    # Tail-Read in 64-KB-Blocken vom Ende der Datei.
    _BLOCK_SIZE = 65536

    def __init__(
        self,
        log_dir: Path | str,
        *,
        sources: Sequence[LogSource] | None = None,
        error_source: LogSource | None = None,
        classifier: type[LogClassifier] = LogClassifier,
    ) -> None:
        self.log_dir = Path(log_dir)
        self._sources = tuple(sources) if sources is not None else self.DEFAULT_SOURCES
        self._error_source = error_source if error_source is not None else self.DEFAULT_ERROR_SOURCE
        self._sources_by_key: dict[str, LogSource] = {s.key: s for s in self._sources}
        if self._error_source is not None:
            self._sources_by_key[self._error_source.key] = self._error_source
        self._classifier = classifier

    # --- Discovery --------------------------------------------------------

    def is_valid_key(self, key: str) -> bool:
        return key == self.AGGREGATE_KEY or key in self._sources_by_key

    def label_for(self, key: str) -> str:
        if key == self.AGGREGATE_KEY:
            return self.AGGREGATE_LABEL
        return self._sources_by_key[key].label

    def all_keys_with_labels(self) -> list[tuple[str, str]]:
        """Dropdown-Reihenfolge: Aggregat, Producer, errors am Ende."""
        result = [(self.AGGREGATE_KEY, self.AGGREGATE_LABEL)]
        result.extend((s.key, s.label) for s in self._sources)
        if self._error_source is not None:
            result.append((self._error_source.key, self._error_source.label))
        return result

    def iter_real_sources(self) -> Iterator[LogSource]:
        return iter(self._sources)

    def sources_for(self, key: str) -> list[LogSource]:
        if key == self.AGGREGATE_KEY:
            return list(self._sources)
        return [self._sources_by_key[key]]

    def file_paths_for(self, key: str) -> list[tuple[str, str, Path]]:
        out: list[tuple[str, str, Path]] = []
        for src in self.sources_for(key):
            if src.out_name:
                out.append((src.label, src.out_name, self.log_dir / src.out_name))
            if src.err_name:
                out.append((src.label, src.err_name, self.log_dir / src.err_name))
        return out

    def paths_for_key(self, key: str) -> tuple[Path | None, Path | None]:
        if key == self.AGGREGATE_KEY:
            return None, None
        src = self._sources_by_key[key]
        return (
            (self.log_dir / src.out_name) if src.out_name else None,
            (self.log_dir / src.err_name) if src.err_name else None,
        )

    # --- Tail reads -------------------------------------------------------

    @classmethod
    def tail_lines(cls, path: Path | str | None, max_lines: int) -> list[str]:
        """Letzte max_lines Zeilen einer Datei. Liest in 64-KB-Bloecken vom
        Ende. Race-resistent gegen paralleles Truncate (nimmt Live-Size aus
        dem File-Handle, nicht aus stat-Cache).

        Akzeptiert Path oder str (oder None) -- str wird zu Path normalisiert.
        """
        if path is None or max_lines <= 0:
            return []
        path = Path(path)
        if not path.exists():
            return []
        try:
            with open(path, 'rb') as f:
                pos = f.seek(0, 2)  # live size, kein stat-cache
                data = b''
                # Wir wollen abbrechen sobald wir GENUG Newlines haben.
                # +1 weil das erste Stueck oft kein vollstaendiger Block ist.
                nl_count = 0
                while pos > 0 and nl_count <= max_lines:
                    read = min(cls._BLOCK_SIZE, pos)
                    pos -= read
                    f.seek(pos)
                    chunk = f.read(read)
                    nl_count += chunk.count(b'\n')
                    data = chunk + data
        except OSError as exc:
            logger.error('tail_lines failed for %s: %s', path, exc)
            return []
        return data.decode('utf-8', errors='replace').splitlines()[-max_lines:]

    @classmethod
    def _stitch_continuations(cls, lines: list[str]) -> list[str]:
        """Haengt Zeilen ohne eigenen Timestamp an den letzten bekannten Ts.
        Resultat: jede Zeile hat einen Timestamp-Praefix, damit nachfolgender
        Sort/Merge die Reihenfolge bewahrt."""
        out: list[str] = []
        last_ts = ''
        for ln in lines:
            m = cls._TS_RE.match(ln)
            if m:
                last_ts = m.group(1)
                out.append(ln)
            elif last_ts and ln.strip():
                out.append(f'{last_ts} {ln}')
            else:
                out.append(ln)
        return out

    @staticmethod
    def _ts_key(line: str) -> str:
        """Sort-Key: 19-Char-Timestamp am Zeilenanfang oder leer."""
        # Praefix-only Match -- Continuation-Frames ohne Ts bekommen ''.
        if len(line) >= 19 and line[4] == '-' and line[7] == '-' and line[10] == ' ':
            return line[:19]
        return ''

    # --- Single-source reads ---------------------------------------------

    def read_single_source(
        self, key: str, max_lines: int,
    ) -> tuple[list[LogLine], list[LogLine]]:
        """(all_lines, exception_lines) fuer eine konkrete Source mit Severity."""
        out_path, err_path = self.paths_for_key(key)
        all_raw = self.tail_lines(out_path, max_lines)
        err_raw = self.tail_lines(err_path, max_lines)
        all_raw = self._stitch_continuations(all_raw) + self._stitch_continuations(err_raw)

        exc_raw = list(self._classifier.iter_exceptions(all_raw))
        return self._classify(all_raw), self._classify(exc_raw)

    # --- Aggregate reads --------------------------------------------------

    def read_aggregate(
        self, max_lines: int,
    ) -> tuple[list[LogLine], list[LogLine]]:
        """(all_lines, exception_lines) ueber alle realen Quellen, mit
        Severity. Continuation-Stitching pro Quelle VOR dem Merge, damit
        Tracebacks zusammenbleiben."""
        per_source: list[list[str]] = []
        for src in self._sources:
            for fname in (src.out_name, src.err_name):
                if not fname:
                    continue
                lines = self.tail_lines(self.log_dir / fname, max_lines)
                per_source.append(self._stitch_continuations(lines))

        # heapq.merge: stable merge ueber pre-sortierte Streams. Jede Quelle
        # ist chrono sortiert (Log-Files werden append-only geschrieben),
        # daher braucht es kein voriges sort() pro Source.
        merged = list(heapq.merge(*per_source, key=self._ts_key))
        merged = merged[-max_lines:]

        exc_raw = list(self._classifier.iter_exceptions(merged))
        return self._classify(merged), self._classify(exc_raw)

    def _classify(self, lines: Iterable[str]) -> list[LogLine]:
        return [LogLine(text=ln, severity=self._classifier.severity(ln)) for ln in lines]

    # --- Truncate ---------------------------------------------------------

    @dataclass
    class TruncateResult:
        cleared: int = 0
        locked: list[str] = field(default_factory=list)
        failed: list[str] = field(default_factory=list)

    def truncate(self, key: str) -> 'LogService.TruncateResult':
        """Truncate alle Logs der Source.

        Achtung: best-effort. Wenn ein RotatingFileHandler die Datei offen
        haelt und parallel schreibt, kann Windows die Datei zwar `open('w')`-
        truncaten lassen aber der Handler's Append-Pointer steht beim alten
        End-Offset -> Null-Byte-Padding bis dahin. Robuster waere ein
        Handler-Lock-aware Pfad; das ist ein TODO.
        """
        result = self.TruncateResult()
        for _label, fname, path in self.file_paths_for(key):
            if not path.exists():
                continue
            try:
                with open(path, 'w', encoding='utf-8'):
                    pass
                result.cleared += 1
            except PermissionError:
                result.locked.append(fname)
            except OSError as exc:
                result.failed.append(f'{fname}: {exc}')
        return result
