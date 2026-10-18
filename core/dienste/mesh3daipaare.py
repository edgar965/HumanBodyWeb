# -*- coding: utf-8 -*-
"""Mesh3daipaare — Trainingspaare als Jobs von Mesh3D-AI (18.10.2026 abends).

Edgar: „die neuen Personen-Trainingsjobs sind alle hier: A:\\3DTools\\3DObjects\\modelsExport, lege die schon mal an als neue Training-Jobs“. Ein Paar ist ein Tripo-Netz (Start) MIT Wahrheit
(Genesis-Export der Charakter-Seite: Ziel). Den Job baut `ProjektTemp/_wegwerf/mesh3dai_paar_job.py` im Format der übrigen Jobs unter `3DObjects/mesh3dai/<Ordnername>/`; die Marke ist
`paar.json` dort. Diese Klasse findet die gebauten Paare — ein neues Paar erscheint in Tabelle, Menü und unter `/mesh-3D-AI/<job>/`, sobald es gebaut ist, ohne Eintrag im Code.

    Mesh3daipaare.stammdaten() -> [{id, name, modell, ordner, geschlecht, paar: True}]

Billig, weil das Menü es auf JEDER Seite fragt (`Mesh3daimenue`): nur Verzeichnis und `paar.json` lesen, gemerkt für `FRIST_S` und solange sich das Verzeichnis nicht ändert.
"""

import json
import logging
import time
from pathlib import Path

from django.conf import settings

logger = logging.getLogger('core')

__all__ = ['Mesh3daipaare']


class Mesh3daipaare:
    MARKE = 'paar.json'
    FRIST_S = 30.0
    _ablage = {}

    @staticmethod
    def ordner():
        return Path(settings.OBJECTS_ROOT) / 'mesh3dai'

    @classmethod
    def stammdaten(cls):
        wurzel = cls.ordner()
        try:
            stand = wurzel.stat().st_mtime_ns
        except OSError:
            return []
        gemerkt = cls._ablage.get('paare')
        if gemerkt and gemerkt['stand'] == stand and time.monotonic() - gemerkt['zeit'] < cls.FRIST_S:
            return [dict(p) for p in gemerkt['paare']]
        paare = []
        for marke in sorted(wurzel.glob('*/' + cls.MARKE)):
            try:
                info = json.loads(marke.read_text(encoding='utf-8'))
            except (OSError, ValueError) as fehler:
                logger.warning('Mesh3daipaare: %s nicht lesbar (%s)', marke, fehler)
                continue
            ordner = marke.parent.name
            paare.append({'id': str(info.get('kennung') or ordner.lower()), 'name': info.get('name') or ordner, 'modell': info.get('name') or ordner, 'ordner': ordner,
                          'geschlecht': info.get('geschlecht') if info.get('geschlecht') in ('weiblich', 'maennlich') else 'weiblich', 'paar': True})
        cls._ablage['paare'] = {'stand': stand, 'zeit': time.monotonic(), 'paare': paare}
        return [dict(p) for p in paare]
