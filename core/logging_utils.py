"""Strukturiertes Logging mit ContextVar-basierter Korrelation.

Beispiel:
    from core.logging_utils import Auftragskontext

    with Auftragskontext.mit_auftrag(job_uuid):
        logger.info('analyze START')
        ...

Alle Log-Records aus diesem ContextVar-Scope kriegen `record.job_id`
gesetzt; der Format-String '%(job_str)s' macht daraus '[job=...] ' bzw.
leeren String wenn nicht gesetzt.

Portiert aus dem CamTrack-Projekt (app/logging_utils.py).
"""
from __future__ import annotations

import contextvars
import logging
import re
import sys
import threading
import time
from contextlib import contextmanager

_job_id_var: contextvars.ContextVar = contextvars.ContextVar(
    'humanbody_job_id', default=None,
)


class Auftragskontext:
    """Welcher Auftrag gerade laeuft — je Faden bzw. Task getrennt.

    Der Wert steht in einer `ContextVar`, nicht in einem Klassenfeld: Daphne
    beantwortet Anfragen nebenlaeufig, und ein gemeinsames Feld haette allen
    Anfragen dieselbe Auftragskennung untergeschoben.
    """

    @staticmethod
    @contextmanager
    def mit_auftrag(job_id):
        """Setzt die Auftragskennung fuer alle Log-Aufrufe im `with`-Block."""
        marke = _job_id_var.set(job_id)
        try:
            yield
        finally:
            _job_id_var.reset(marke)


class JobContextFilter(logging.Filter):
    """Haengt job_id + job_str an jeden LogRecord."""

    def filter(self, record: logging.LogRecord) -> bool:
        job_id = _job_id_var.get()
        record.job_id = job_id if job_id is not None else ''
        record.job_str = f'[job={job_id}] ' if job_id is not None else ''
        return True


_TS_PREFIX_RE = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')


class TimestampedStream:
    """Wrapper um sys.stdout/sys.stderr der pro-Zeile ein Datum vorhaengt
    wenn die Zeile noch keines hat. So kriegen print()-Calls + Third-Party-
    Libs (torch, tqdm, ffmpeg-Output) im Server-Log einen Zeitstempel.

    Buffert Teil-Schreibvorgaenge bis zum naechsten '\\n' - sonst kriegen
    z.B. tqdm-Progress-Bar-Updates jeweils einen eigenen Timestamp pro
    Carriage-Return-Tick (waere unleserlich).
    """

    def __init__(self, wrapped):
        self._wrapped = wrapped
        self._buffer = ''
        self._at_line_start = True
        self._lock = threading.Lock()

    def write(self, s):
        if not s:
            return 0
        with self._lock:
            return self._write_locked(s)

    def _write_locked(self, s):
        s = self._buffer + s
        out = []
        i = 0
        n = len(s)
        line_start = self._at_line_start
        broke_early = False
        while i < n:
            j_n = s.find('\n', i)
            j_r = s.find('\r', i)
            j = min(x for x in (j_n, j_r) if x != -1) if (j_n != -1 or j_r != -1) else -1
            if j == -1:
                self._buffer = s[i:]
                self._at_line_start = line_start
                broke_early = True
                break
            chunk = s[i:j+1]
            if line_start and chunk.strip() and not _TS_PREFIX_RE.match(chunk):
                ts = time.strftime('%Y-%m-%d %H:%M:%S')
                out.append(f'{ts} {chunk}')
            else:
                out.append(chunk)
            line_start = True
            i = j + 1
        if not broke_early:
            self._buffer = ''
            self._at_line_start = line_start
        if out:
            self._wrapped.write(''.join(out))
        return len(s)

    def flush(self):
        with self._lock:
            if self._buffer:
                ts = time.strftime('%Y-%m-%d %H:%M:%S')
                if not _TS_PREFIX_RE.match(self._buffer):
                    self._wrapped.write(f'{ts} {self._buffer}')
                else:
                    self._wrapped.write(self._buffer)
                self._buffer = ''
            self._wrapped.flush()

    def __getattr__(self, name):
        return getattr(self._wrapped, name)


class Zeitstempelausgabe:
    """Haengt `TimestampedStream` vor stdout und stderr. Genau einmal.

    Als Klasse statt `global _INSTALLED` (Befund `klassenreif`, Frage 1,
    27.08.2026): Der Merker haengt jetzt an der Klasse und laesst sich in einer
    Pruefung zuruecksetzen, ohne ein Modul neu zu laden.
    """

    #: Schon eingehaengt? Der Entwicklungsserver laedt bei jeder Aenderung neu.
    eingehaengt = False
    _schloss = threading.Lock()

    @classmethod
    def einhaengen(cls):
        with cls._schloss:
            if cls.eingehaengt:
                return
            if not isinstance(sys.stdout, TimestampedStream):
                sys.stdout = TimestampedStream(sys.stdout)
            if not isinstance(sys.stderr, TimestampedStream):
                sys.stderr = TimestampedStream(sys.stderr)
            cls.eingehaengt = True
