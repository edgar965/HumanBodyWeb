# -*- coding: utf-8 -*-
"""Meshfigurrunnerbahn — ein Schritt des python10-Runners von „Mesh to 3D" (`_run_meshfigur.py`), im Dauerprozess oder einzeln.

Herausgelöst aus `Meshfigurlauf.runner` (12.10.2026, die Datei stand bei 342 Zeilen): die Deutung der Ausgabezeilen — `[fortschritt] <0..100> <Text>`, `[ergebnis] {…}`, `[fehler] {…}` — ist für beide Wege dieselbe;
der Weg unterscheidet sich nur darin, WOHER die Zeilen kommen. Mit `Meshfigurdauerprozess` (Vorgabe) rechnet EIN Prozess alle Schritte des Laufs, sonst startet jeder Schritt seinen eigenen (`MESHFIGUR_DAUER=0`, oder wenn der
Dauerprozess nicht startet — dann steht der Grund im Log und der Schritt läuft einzeln, nie stumm).
Mit `lauf.im_prozess` (05.11.2026, Edgar: „alles möglichst in einem Prozess“, Mesh3D-AI-Kette im Skriptdienst) rechnet der Runner in DIESEM Prozess, die Zeilen kommen über `sys.stdout` wie sonst über die Pipe:
python14 hat dieselbe torch-Fassung wie python10 (2.10.0+cu128), statt des Pakets `mediapipe` dieselben Netze in torch (`Meshfigurpunkte`).
"""

import contextlib
import json
import logging
import os
import sys

from django.conf import settings

from ..daten.meshto3dpfad import Meshto3dpfad
from ..models import Meshfigurauftrag
from ..pipeline_process import PipelineProzess, PipelineStille

logger = logging.getLogger('core')

__all__ = ['Meshfigurrunnerbahn']


def _endlich(wert):
    """NaN und unendlich werden `None` — `json.loads` liest „NaN" als Zahl, und SQLite lehnt sie im JSON-Feld ab
    (`CHECK constraint failed: JSON_VALID`, Seori-Import 10.10.2026: `gesicht_fehler_px` ohne Gesichtspunkte)."""
    if isinstance(wert, float):
        return wert if (wert == wert and abs(wert) != float('inf')) else None
    if isinstance(wert, dict):
        return {k: _endlich(v) for k, v in wert.items()}
    if isinstance(wert, list):
        return [_endlich(v) for v in wert]
    return wert


class _Zeilenstrom:
    """`sys.stdout` für einen Runner im selben Prozess: jede fertige Zeile geht an `Meshfigurrunnerbahn._zeile`."""

    encoding = 'utf-8'

    def __init__(self, zeile):
        self.zeile, self.rest = zeile, ''

    def write(self, text):
        teile = (self.rest + text).split('\n')
        self.rest = teile.pop()
        for z in teile:
            self.zeile(z)
        return len(text)

    def flush(self):
        pass


class Meshfigurrunnerbahn:
    """Ein Schritt: Befehl bauen, Zeilen lesen, Ergebnis oder Fehler zurückgeben."""

    def __init__(self, lauf):
        self.lauf = lauf
        self.ergebnis = None
        self.meldung = None
        self._schritt, self._von, self._bis = '', 0.0, 1.0

    def rechnen(self, schritt, runde=None, von=0.0, bis=1.0):
        """`[ergebnis]` (dict) des Schritts — oder ein `RuntimeError` mit der Meldung des Runners."""
        self._schritt, self._von, self._bis = schritt, von, bis
        auftrag = self.lauf.auftrag()           # schreibt auftrag.json — auch der Dauerprozess liest es bei JEDEM Schritt neu
        if self.lauf.im_prozess:
            return self._im_prozess(auftrag, schritt, runde)
        if self.lauf.dauer.erlaubt():
            try:
                return self._im_dauerprozess(auftrag, schritt, runde)
            except self.lauf.Angehalten:
                raise
            except PipelineStille as fehler:
                raise RuntimeError('Runner schweigt (%s)' % fehler) from fehler
            except OSError as fehler:                          # der Prozess startet nicht (Interpreter, Rechte): einzeln weiter, sichtbar
                logger.warning('Mesh to 3D %s: Dauerprozess nicht möglich (%s) — Schritt %s einzeln', self.lauf.job.kennung, fehler, schritt)
        return self._einzeln(auftrag, schritt, runde)

    # ------------------------------------------------------------ Dauerprozess

    def _befehl_dauer(self):
        return [settings.PIPELINE_PYTHON, os.path.join(Meshto3dpfad.pfad(), self.lauf.RUNNER), '--dauer']

    def _im_dauerprozess(self, auftrag, schritt, runde):
        fehlertext = self.lauf.dauer.rechnen(self._befehl_dauer(), auftrag, schritt, runde, self.lauf.umgebung(), Meshto3dpfad.pfad(), self._zeile, self.lauf.STILLE_S)
        if self.ergebnis is None:
            raise RuntimeError(self.meldung or fehlertext or 'Runner ohne Ergebnis')
        return self.ergebnis

    # ---------------------------------------------------------------- im Prozess

    def _im_prozess(self, auftrag, schritt, runde):
        """Wie ein Schritt im Dauerprozess (`Meshfigurdauerlauf.laufen`): `Meshfigurrunner`, danach aufräumen; Arbeitsordner und Umgebung des Runners nur für die Dauer des Schritts."""
        pfad = Meshto3dpfad.pfad()
        if pfad not in sys.path:
            sys.path.insert(0, pfad)
        from _run_meshfigur import Meshfigurrunner
        from meshfigur_dauerlauf import Meshfigurdauerlauf

        ordner, umgebung = os.getcwd(), self.lauf.umgebung()
        alt = {k: os.environ.get(k) for k in umgebung}
        os.environ.update(umgebung)
        os.chdir(pfad)
        strom = _Zeilenstrom(self._zeile)
        try:
            with contextlib.redirect_stdout(strom):
                Meshfigurrunner(str(auftrag), schritt, runde or 1).ausfuehren()
        finally:
            os.chdir(ordner)
            for k, v in alt.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
            Meshfigurdauerlauf.aufraeumen()
        if self.ergebnis is None:
            raise RuntimeError(self.meldung or 'Runner ohne Ergebnis')
        return self.ergebnis

    # ---------------------------------------------------------------- einzeln

    def _einzeln(self, auftrag, schritt, runde):
        befehl = [settings.PIPELINE_PYTHON, os.path.join(Meshto3dpfad.pfad(), self.lauf.RUNNER), str(auftrag), schritt]
        if runde is not None:
            befehl.append(str(runde))
        pp = PipelineProzess.starten(befehl, cwd=Meshto3dpfad.pfad(), env_extra=self.lauf.umgebung())
        try:
            for zeile in pp.stdout_zeilen(stille_timeout=self.lauf.STILLE_S):
                self._zeile(zeile.rstrip('\n'))
        except self.lauf.Angehalten:
            pp.beenden()
            raise
        except PipelineStille as fehler:
            pp.beenden()
            raise RuntimeError('Runner schweigt (%s)' % fehler) from fehler
        rc = pp.warten(timeout=120)
        if rc != 0 or self.ergebnis is None:
            raise RuntimeError(self.meldung or pp.fehlertext(1500) or 'Runner endete mit %s' % rc)
        return self.ergebnis

    # ------------------------------------------------------------------ Zeilen

    def _zeile(self, zeile):
        """Eine Ausgabezeile des Runners deuten; wirft `Angehalten`, sobald der Nutzer angehalten hat."""
        if zeile.startswith('[fortschritt] '):
            teile = zeile[14:].split(' ', 1)
            try:
                wert = float(teile[0]) / 100.0
            except ValueError:
                wert = None
            if wert is not None:
                self.lauf.melden(self._von + (self._bis - self._von) * wert, teile[1] if len(teile) > 1 else self._schritt)
        elif zeile.startswith('[ergebnis] '):
            self.ergebnis = _endlich(json.loads(zeile[11:]))
        elif zeile.startswith('[fehler] '):
            self.meldung = json.loads(zeile[9:]).get('fehler')
        if Meshfigurauftrag.objects.filter(pk=self.lauf.job.pk, status='angehalten').exists():
            raise self.lauf.Angehalten()
