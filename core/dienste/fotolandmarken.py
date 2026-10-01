# -*- coding: utf-8 -*-
"""Fotolandmarken — Posen- und Gesichtslandmarken je Bild aus dem python10-Wrapper (`_run_fotolandmarken.py`,
MediaPipe Tasks; python14 hat kein MediaPipe), mit Ablage je Auftrag (01.10.2026).

`holen(pfade)` gibt `{dateiname: befund}` — gerechnet nur, was in `arbeit/fotolandmarken.json` noch nicht mit
demselben Dateistand (Größe, mtime) steht. Ein Aufruf lädt die Modelle einmal (≈ 2 s) und rechnet ≈ 0,3 s je Bild;
scheitert der Wrapper, kommt ein leeres Wörterbuch und eine Warnung im Log — Blickwinkel und Gesichtsmaße bleiben
dann, wie sie sind.
"""

import json
import logging
import os
import subprocess

from django.conf import settings

from ..atomic_write import AtomarSchreiber
from ..daten.wrapperpfad import Wrapperpfad

logger = logging.getLogger('core')

__all__ = ['Fotolandmarken']


class Fotolandmarken:
    RUNNER = '_run_fotolandmarken.py'
    DATEI = 'fotolandmarken.json'
    ZEIT_S = 600
    #: Fassung des Wrappers (`FASSUNG` dort) — ein Eintrag anderer Fassung wird neu gerechnet, nicht weiterverwendet
    #: (01.10.2026: Fassung 2 sucht das Gesicht auch im Kopfausschnitt der Pose; `artefakte-benennen`).
    FASSUNG = 2

    def __init__(self, ablage):
        self.ablage = ablage
        self.pfad = ablage.arbeit(self.DATEI)

    def _lesen(self):
        if not self.pfad.is_file():
            return {}
        try:
            with open(self.pfad, encoding='utf-8') as datei:
                return json.load(datei)
        except (OSError, ValueError):
            return {}

    @staticmethod
    def _stand(pfad):
        try:
            st = os.stat(pfad)
            return [int(st.st_size), int(st.st_mtime_ns)]
        except OSError:
            return None

    def holen(self, pfade):
        """`pfade`: Bilddateien → `{name: befund}` (Befunde wie im Wrapper, dazu `stand`)."""
        pfade = [str(p) for p in pfade if os.path.isfile(str(p))]
        alt = self._lesen()
        fehlend = [p for p in pfade if (alt.get(os.path.basename(p)) or {}).get('stand') != self._stand(p)
                   or (alt.get(os.path.basename(p)) or {}).get('fassung') != self.FASSUNG]
        if fehlend:
            neu = self._rechnen(fehlend)
            for p in fehlend:
                befund = neu.get(os.path.basename(p))
                if befund is not None:
                    befund['stand'] = self._stand(p)
                    alt[os.path.basename(p)] = befund
            if neu:
                self.pfad.parent.mkdir(parents=True, exist_ok=True)
                AtomarSchreiber.json_schreiben(self.pfad, alt)
        return {os.path.basename(p): alt.get(os.path.basename(p)) for p in pfade if alt.get(os.path.basename(p))}

    def _rechnen(self, pfade):
        befehl = [str(settings.PIPELINE_PYTHON), os.path.join(Wrapperpfad.pfad(), self.RUNNER)] + pfade
        try:
            lauf = subprocess.run(befehl, capture_output=True, timeout=self.ZEIT_S, check=False,
                                  cwd=Wrapperpfad.pfad())
        except (OSError, subprocess.TimeoutExpired) as fehler:
            logger.warning('Fotolandmarken: Wrapper nicht gelaufen (%s)', fehler)
            return {}
        zeile = None
        for roh in (lauf.stdout or b'').decode('utf-8', errors='replace').splitlines()[::-1]:
            roh = roh.strip()
            if roh.startswith('{'):
                zeile = roh
                break
        if not zeile:
            logger.warning('Fotolandmarken: keine Antwort (Code %s): %s', lauf.returncode,
                           (lauf.stderr or b'')[-600:].decode('utf-8', errors='replace'))
            return {}
        try:
            antwort = json.loads(zeile)
        except ValueError:
            logger.warning('Fotolandmarken: Antwort unlesbar')
            return {}
        if antwort.get('error'):
            logger.warning('Fotolandmarken: %s', antwort['error'])
            return {}
        return {b['datei']: b for b in antwort.get('bilder') or [] if isinstance(b, dict) and b.get('datei')}
