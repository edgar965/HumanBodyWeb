"""Zeitstempel auf stdout/stderr — und der Auftragskontext aus djangoBase.

Beispiel:
    from core.logging_utils import Auftragskontext

    with Auftragskontext.mit_auftrag(job_uuid):
        logger.info('analyze START')

Alle Log-Records in diesem Block bekommen `record.job_id` und `record.job_str`;
der Formatierer setzt daraus '[job=...] ' bzw. nichts.

UMBAU 28.08.2026 (djangoBase-Konformitaet): ContextVar, `with`-Block und
`JobContextFilter` standen hier als eigene Fassung — Zeile fuer Zeile
dasselbe wie `djangobase.jobctx`, was der alte Kopf der Datei mit „Portiert
aus dem CamTrack-Projekt" auch sagte. Zwei Kopien einer ContextVar sind
schlimmer als zwei Kopien einer Rechnung: Setzt der eine Weg den Wert und
liest der andere, fehlt die Auftragskennung im Log — still, und niemand
sieht, dass sie fehlt.

`TimestampedStream` bleibt hier: Den gibt es in djangoBase nicht.
"""
from __future__ import annotations

import re
import sys
import threading
import time

from djangobase.jobctx import JobContextFilter, with_job_id

__all__ = ['Auftragskontext', 'JobContextFilter', 'TimestampedStream',
           'Zeitstempelausgabe']


class Auftragskontext:
    """Welcher Auftrag gerade laeuft — je Faden bzw. Task getrennt.

    Der Wert steht in einer `ContextVar` (djangoBase), nicht in einem
    Klassenfeld: Daphne beantwortet Anfragen nebenlaeufig, und ein
    gemeinsames Feld haette allen Anfragen dieselbe Auftragskennung
    untergeschoben.

    Die Klasse bleibt als deutscher Name fuer den djangoBase-Block: 20
    Aufrufstellen heissen `Auftragskontext.mit_auftrag(...)`, und der Name
    sagt hier mehr als `with_job_id`.
    """

    @staticmethod
    def mit_auftrag(job_id):
        """Setzt die Auftragskennung fuer alle Log-Aufrufe im `with`-Block."""
        return with_job_id(job_id)


_TS_PREFIX_RE = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')


class TimestampedStream:
    """Wrapper um sys.stdout/sys.stderr der pro-Zeile ein Datum vorhaengt
    wenn die Zeile noch keines hat. So kriegen print()-Calls + Third-Party-
    Libs (torch, tqdm, ffmpeg-Output) im Server-Log einen Zeitstempel.

    Gepuffert wird bis zum naechsten Zeilenende — sonst stuende der
    Zeitstempel mitten im Satz, weil `write` nicht immer ganze Zeilen
    bekommt.

    ZEILENENDE HEISST `\n` ODER `\r`. Fortschrittsbalken (tqdm, ffmpeg)
    schreiben mit `\r`; jeder Tick bekommt deshalb SEINEN EIGENEN
    Zeitstempel. Das ist keine schoene Ausgabe, aber die richtige: Ohne
    `\r` als Ende stuende ein ganzer Balkenlauf als EINE Zeile im Log,
    mit einem Stempel ganz vorn — die Dauer waere nicht mehr ablesbar.
    (Dieser Absatz behauptete bis zum 30.08.2026 das Gegenteil; der Code
    tat schon immer dies.)
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

    @staticmethod
    def _zeilenende(s, ab):
        """Stelle des naechsten `\n` oder `\r` ab `ab` — oder -1.

        BEIDE Zeichen, weil Fortschrittsbalken (`tqdm`, ffmpeg) mit `\r`
        arbeiten: Ohne `\r` waere ein ganzer Lauf EINE Zeile, und der
        Zeitstempel stuende nur ganz am Anfang.
        """
        stellen = [x for x in (s.find('\n', ab), s.find('\r', ab)) if x != -1]
        return min(stellen) if stellen else -1

    @staticmethod
    def _mit_stempel(stueck, zeilenanfang):
        """Eine Zeile, bei Bedarf mit Zeitstempel davor.

        Leerzeilen und Zeilen, die schon einen Stempel tragen, bleiben wie sie
        sind — sonst stuende in Log-Dateien zweimal eine Uhrzeit, und der
        Leser in Hilfe -> Logs erkennt die Zeile dann nicht mehr.
        """
        if not zeilenanfang or not stueck.strip():
            return stueck
        if _TS_PREFIX_RE.match(stueck):
            return stueck
        return f'{time.strftime("%Y-%m-%d %H:%M:%S")} {stueck}'

    def _write_locked(self, s):
        """Fertige Zeilen durchreichen, den Rest bis zum naechsten Mal halten.

        Der Puffer ist der Punkt: `write` bekommt nicht immer ganze Zeilen.
        Wer den Rest sofort schreibt, bekommt einen Zeitstempel mitten im Satz.
        """
        s = self._buffer + s
        fertig = []
        i, n = 0, len(s)
        zeilenanfang = self._at_line_start
        while i < n:
            ende = self._zeilenende(s, i)
            if ende == -1:
                self._buffer = s[i:]
                self._at_line_start = zeilenanfang
                break
            fertig.append(self._mit_stempel(s[i:ende + 1], zeilenanfang))
            zeilenanfang = True
            i = ende + 1
        else:
            self._buffer = ''
            self._at_line_start = zeilenanfang
        if fertig:
            self._wrapped.write(''.join(fertig))
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
