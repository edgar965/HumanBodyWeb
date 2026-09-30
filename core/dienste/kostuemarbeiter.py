# -*- coding: utf-8 -*-
"""Kostuemarbeiter — EIN dauerhaft laufender Blender-Prozess des Kostüm-Kreislaufs
(`effekte/blender/kostuembau.py`).

Blender starten und die Grundfigur laden kostet je Aufruf 4–9 s (gemessen 30.09.2026, unter Last), ein
Kandidat danach 0,6–0,8 s. Der Arbeiter lädt die Figur EINMAL und rechnet dann Befehle ab: Der Vater legt
`befehl_<nr>.json` in das Postfach (`arbeit/kostuem_dienst/w<n>/`), der Arbeiter antwortet mit
`antwort_<nr>.json`. Ein Postfach-Ordner statt stdin, weil Blender im Hintergrund stdin nicht verlässlich
liest — und weil Dateien unteilbar ersetzt werden.

Ein Arbeiter wird nach `LEBENSDAUER` Befehlen erneuert (Blender gibt Speicher nach Tausenden Kostümen nicht
vollständig zurück) und nach einem Fehler; stirbt er mitten in einem Befehl, meldet `antwort` das mit den
letzten Zeilen seiner Fehlerausgabe. Beendet wird er über `beenden` (Befehl `ende`, danach der Prozessbaum).
"""

import json
import logging
import shutil
import time
from pathlib import Path

from django.conf import settings

from ..atomic_write import AtomarSchreiber
from ..pipeline_process import PipelineProzess

logger = logging.getLogger('core')

__all__ = ['Kostuemarbeiter']


class Kostuemarbeiter:
    SKRIPT = Path(settings.BASE_DIR) / 'effekte' / 'blender' / 'kostuembau.py'
    BEREIT_S = 240
    ANTWORT_S = 900
    LEBENSDAUER = 300
    TAKT_S = 0.02

    def __init__(self, lauf, nummer, koerper, breite, hoehe, wurzel=None):
        """`wurzel`: der Ordner, in dem alle Postfächer EINES Kostuemblender liegen (Vorgabe: `arbeit/kostuem_dienst`)."""
        self.lauf = lauf
        self.ablage = lauf.ablage
        self.nummer = nummer
        self.koerper = str(koerper)
        self.breite, self.hoehe = breite, hoehe
        self.postfach = (wurzel or self.ablage.arbeit('kostuem_dienst')) / ('w%d' % nummer)
        self.pp = None
        self.befehle = 0
        self.kopf = {}

    def lebt(self):
        return self.pp is not None and self.pp.proc.poll() is None

    def starten(self):
        """Blender starten (die Figur lädt er im Hintergrund; `bereit` wartet darauf)."""
        shutil.rmtree(self.postfach, ignore_errors=True)
        self.postfach.mkdir(parents=True, exist_ok=True)
        start = self.postfach / 'start.json'
        AtomarSchreiber.json_schreiben(
            start,
            {
                'koerper': self.koerper,
                'breite': self.breite,
                'hoehe': self.hoehe,
                'dienst': str(self.postfach),
            },
        )
        tmp = self.ablage.arbeit('tmp')
        tmp.mkdir(parents=True, exist_ok=True)
        self.pp = PipelineProzess.starten(
            [
                str(settings.BLENDER_EXE),
                '-b',
                '--factory-startup',
                '--python',
                str(self.SKRIPT),
                '--',
                '--auftrag',
                str(start),
            ],
            cwd=str(self.SKRIPT.parent),
            env_extra={'TMP': str(tmp), 'TEMP': str(tmp), 'PYTHONIOENCODING': 'utf-8'},
            stdout_lesen=False,
        )
        self.befehle = 0

    def bereit(self):
        """Wartet, bis der Arbeiter die Figur geladen hat. → sein Bericht über die Figur (`kopf`)."""
        bis = time.time() + self.BEREIT_S
        datei = self.postfach / 'bereit.json'
        while not datei.is_file():
            self._pruefen(bis, 'Blender-Arbeiter %d wird nicht bereit' % self.nummer)
            time.sleep(self.TAKT_S)
        self.kopf = self._lesen(datei).get('kopf') or {}
        return self.kopf

    def senden(self, auftrag):
        """Einen Befehl ablegen. → seine Nummer."""
        self.befehle += 1
        AtomarSchreiber.json_schreiben(self.postfach / ('befehl_%06d.json' % self.befehle), auftrag)
        return self.befehle

    def antwort(self, nummer):
        """Wartet auf die Antwort zu Befehl `nummer`. → der Bericht; ein Fehler des Arbeiters wird ein
        RuntimeError."""
        bis = time.time() + self.ANTWORT_S
        datei = self.postfach / ('antwort_%06d.json' % nummer)
        while not datei.is_file():
            self._pruefen(bis, 'Blender-Arbeiter %d antwortet nicht' % self.nummer)
            time.sleep(self.TAKT_S)
        antwort = self._lesen(datei)
        datei.unlink(missing_ok=True)
        if antwort.get('fehler'):
            raise RuntimeError('Blender-Arbeiter %d: %s' % (self.nummer, antwort['fehler']))
        return antwort

    LESEN_S = 8.0

    @classmethod
    def _lesen(cls, datei):
        """Eine Antwortdatei lesen. Windows verweigert den Zugriff kurz nach dem Ersetzen (Virenscanner,
        Indexdienst) — 30.09.2026 01:39 riss ein einziges `PermissionError` einen Lauf nach 770 Runden ab.
        Also kurz warten und wiederholen; erst nach `LESEN_S` ist es ein Fehler (RuntimeError:
        `Kostuemblender` versucht die Runde dann noch einmal mit frischen Arbeitern)."""
        bis = time.time() + cls.LESEN_S
        while True:
            try:
                with open(datei, encoding='utf-8') as f:
                    return json.load(f)
            except (OSError, ValueError) as fehler:
                if time.time() > bis:
                    raise RuntimeError('Antwort %s nicht lesbar: %s' % (datei.name, fehler)) from fehler
                time.sleep(0.1)

    def _pruefen(self, bis, text):
        """Zwischen zwei Blicken ins Postfach: Anhalten, Zeitgrenze, Lebenszeichen."""
        if self.lauf.angehalten():
            self.beenden()
            raise self.lauf.Angehalten()
        if self.pp is None or self.pp.proc.poll() is not None:
            raise RuntimeError(
                'Blender-Arbeiter %d ist beendet: %s'
                % (self.nummer, self.pp.fehlertext(1500) if self.pp else '')
            )
        if time.time() > bis:
            fehler = '%s (Zeitgrenze)' % text
            self.beenden()
            raise RuntimeError(fehler)

    def alt(self):
        return self.befehle >= self.LEBENSDAUER

    def beenden(self):
        if self.pp is None:
            return
        try:
            if self.lebt():
                AtomarSchreiber.json_schreiben(self.postfach / 'befehl_999999.json', {'ende': True})
                try:
                    self.pp.proc.wait(timeout=3)
                except Exception:  # noqa: BLE001 — er reagiert nicht: der Prozessbaum wird beendet
                    logger.debug('Blender-Arbeiter %d beendet sich nicht von selbst', self.nummer)
            self.pp.beenden()
        finally:
            self.pp = None
