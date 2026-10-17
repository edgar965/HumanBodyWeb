# -*- coding: utf-8 -*-
"""Mesh3daidatensatz — was vom Datensatz eines Jobs wirklich auf der Platte liegt (14.10.2026).

Edgar: „eine Spalte ‚Datensatz‘ mit den echten Proben auf der Platte". Die Spalten „Proben / Training / Prüfposen" der Jobtabelle sind die Zahlen der Attrappe (die Posen, die die Seite zeigt);
hier steht, wie viele Proben des echten Datensatzes (`3DObjects/mesh3dai/<Modell>/`, nicht im Git) bereits gerechnet sind.

    Mesh3daidatensatz.zaehlen('Ursula1') -> {'vorhanden': 216, 'geplant': 425}     geplant = Einträge in `proben.json`, `None` ohne die Datei

Eine Probe zählt als fertig, wenn `proben/<NNNN>/eingabe.npz` existiert: das Datenskript schreibt sie zuletzt (`soll.npz` und `eingabe.glb` davor), ihr Vorhandensein heißt dort „fertig".
Gezählt wird bei jedem Aufruf neu (ein Verzeichnislauf über rund 400 Ordner, ein Stat je Ordner) — der Lauf wächst, während die Seite offen ist.
"""

import json
import logging
from pathlib import Path

from django.conf import settings

log = logging.getLogger('core')

__all__ = ['Mesh3daidatensatz']


class Mesh3daidatensatz:
    FERTIG = 'eingabe.npz'

    @staticmethod
    def ordner(modell):
        return Path(settings.OBJECTS_ROOT) / 'mesh3dai' / str(modell)

    @classmethod
    def zaehlen(cls, modell):
        """`{'vorhanden': Zahl fertiger Proben, 'geplant': Zahl der Einträge in proben.json oder None}`."""
        ordner = cls.ordner(modell)
        return {'vorhanden': cls._vorhanden(ordner / 'proben'), 'geplant': cls._geplant(ordner / 'proben.json')}

    @classmethod
    def _vorhanden(cls, proben):
        if not proben.is_dir():
            return 0
        return sum(1 for p in proben.iterdir() if (p / cls.FERTIG).is_file())

    @staticmethod
    def _geplant(datei):
        if not datei.is_file():
            return None
        try:
            return len(json.loads(datei.read_text(encoding='utf-8')))
        except (OSError, ValueError):
            log.warning('Mesh3daidatensatz: %s nicht lesbar - die Zahl der geplanten Proben fehlt', datei)
            return None
