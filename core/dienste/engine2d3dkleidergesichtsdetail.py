# -*- coding: utf-8 -*-
"""Engine2d3dKleiderGesichtsdetail — die Bilderreihen Augen/Mund/Nase des Reiters „Gesicht" ausliefern (07.10.2026).

Das Rendern macht `Engine2d3dKleiderGesichtsdetailrender` in einem eigenen Prozess (`manage.py engine2d3dkleider_gesichtsdetail`, ~25 s für alle drei) — pyrender braucht einen GL-Kontext, den kein
Anfrage-Faden des Servers halten soll; dieses Modul importiert ihn deshalb nicht. Die Dateien tragen die FASSUNG im Namen (`ergebnis/gesicht_<bereich>_<fassung>.png`; Fassung = Darstellung +
Netzart + Fassung des Modells aus `stand.json` + Stand von `posiert.npy`): ein neuer Stand oder ein anderes Netz rendert neu, eine vorhandene Datei wird nie für einen anderen Stand ausgeliefert
(`artefakte-benennen.md`). Fehlt sie, wird sie hier bestellt; zwei Anfragen zugleich teilen sich den Lauf (Sperre je Auftrag). Ältere Fassungen räumt der Lauf weg.
"""

import json
import logging
import subprocess
import sys
import threading

from django.conf import settings

from .engine2d3dkleidergesichtslage import Engine2d3dKleiderGesichtslage

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleiderGesichtsdetail']


class Engine2d3dKleiderGesichtsdetail:
    BEREICHE = ('augen', 'mund', 'nase')
    #: Fassung der Darstellung (Kamera, Ringe, Licht, Beschriftung) — beim Ändern hochzählen, sonst bliebe das alte Bild liegen.
    DARSTELLUNG = 3
    ZEITGRENZE_S = 300
    _sperren = {}
    _sperrenliste = threading.Lock()

    @staticmethod
    def dateiname(bereich, fassung):
        return 'gesicht_%s_%s.png' % (bereich, fassung)

    @classmethod
    def fassung(cls, job, ablage):
        """Der Fassungsname der Bilder des aktuellen Stands. ValueError, wenn noch kein Modell des Stands da ist."""
        stand = ablage.ergebnis('stand.json')
        if not stand.is_file():
            raise ValueError('Noch kein Modell des Stands (`ergebnis/stand.json`) — erst nach dem Schritt „Körper“.')
        modell = json.loads(stand.read_text(encoding='utf-8')).get('fassung') or 'ohne'
        posiert = ablage.arbeit('posiert.npy')
        stempel = posiert.stat().st_mtime_ns if posiert.is_file() else 0
        art = 'k' if Engine2d3dKleiderGesichtslage.netzart(job, ablage) == 'Kopfnetz' else 'n'
        return 'v%d_%s_%s_%x' % (cls.DARSTELLUNG, art, modell, stempel)

    @classmethod
    def datei(cls, job, ablage, bereich):
        """Der Pfad des Bildes (rendert zuerst, wenn es fehlt). ValueError mit Grund, wenn es nicht geht."""
        if bereich not in cls.BEREICHE:
            raise ValueError('Unbekannter Bereich: %s' % bereich)
        fassung = cls.fassung(job, ablage)
        pfad = ablage.ergebnis(cls.dateiname(bereich, fassung))
        if pfad.is_file():
            return pfad
        with cls._sperre(job.id):
            if not pfad.is_file():                      # ein anderer Aufruf hat gerendert, während dieser wartete
                cls._rendern(job, ablage, fassung)
        if not pfad.is_file():
            raise ValueError('Das Rendern hat keine Datei geliefert.')
        return pfad

    @classmethod
    def _sperre(cls, job_id):
        with cls._sperrenliste:
            return cls._sperren.setdefault(str(job_id), threading.Lock())

    @classmethod
    def _rendern(cls, job, ablage, fassung):
        befehl = [sys.executable, str(settings.BASE_DIR / 'manage.py'), 'engine2d3dkleider_gesichtsdetail', str(job.id), fassung]
        flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
        try:
            lauf = subprocess.run(befehl, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=cls.ZEITGRENZE_S, cwd=str(settings.BASE_DIR), creationflags=flags, check=False)
        except subprocess.TimeoutExpired as fehler:
            raise ValueError('Das Rendern der Gesichtsbilder dauerte länger als %d s.' % cls.ZEITGRENZE_S) from fehler
        if lauf.returncode != 0:
            letzte = [z for z in (lauf.stderr or '').strip().splitlines() if z.strip()]
            logger.error('2D3D Kleider %s: Gesichtsbilder nicht gerendert: %s', job.kennung, '\n'.join(letzte[-8:]))
            raise ValueError('Gesichtsbilder nicht gerendert: %s' % (letzte[-1] if letzte else 'Prozess endete mit %d' % lauf.returncode))
        cls._aufraeumen(ablage, fassung)

    @classmethod
    def _aufraeumen(cls, ablage, fassung):
        """Die Bilder älterer Fassungen entfernen — nur die dieses Reiters (`gesicht_<bereich>_*.png`)."""
        behalten = {cls.dateiname(b, fassung) for b in cls.BEREICHE}
        for bereich in cls.BEREICHE:
            for alt in ablage.ergebnis().glob('gesicht_%s_*.png' % bereich):
                if alt.name not in behalten:
                    alt.unlink(missing_ok=True)
