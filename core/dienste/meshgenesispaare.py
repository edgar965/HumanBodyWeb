# -*- coding: utf-8 -*-
"""Meshgenesispaare — Trainingspaare als Jobs von Mesh-Genesis (18.10.2026 abends).

Edgar: „die neuen Personen-Trainingsjobs sind alle hier: A:\\3DTools\\3DObjects\\modelsExport, lege die schon mal an als neue Training-Jobs“. Ein Paar ist ein Tripo-Netz (Start) MIT Wahrheit
(Genesis-Export der Charakter-Seite: Ziel). Den Job baut `ProjektTemp/_wegwerf/meshgenesis_paar_job.py` im Format der übrigen Jobs unter `3DObjects/meshgenesis/<Ordnername>/`; die Marke ist
`paar.json` dort. Diese Klasse findet die gebauten Paare — ein neues Paar erscheint in Tabelle, Menü und unter `/mesh-genesis/<job>/`, sobald es gebaut ist, ohne Eintrag im Code.

    Meshgenesispaare.stammdaten() -> [{id, name, modell, ordner, geschlecht, paar: True}]

Billig, weil das Menü es auf JEDER Seite fragt (`Meshgenesismenue`): nur Verzeichnis und `paar.json` lesen, gemerkt für `FRIST_S` und solange sich das Verzeichnis nicht ändert.
"""

import json
import logging
import time
from pathlib import Path

from django.conf import settings

logger = logging.getLogger('core')

__all__ = ['Meshgenesispaare']


class Meshgenesispaare:
    MARKE = 'paar.json'
    FRIST_S = 30.0
    _ablage = {}

    @staticmethod
    def ordner():
        return Path(settings.OBJECTS_ROOT) / 'meshgenesis'

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
                logger.warning('Meshgenesispaare: %s nicht lesbar (%s)', marke, fehler)
                continue
            ordner = marke.parent.name
            paare.append({'id': str(info.get('kennung') or ordner.lower()), 'name': info.get('name') or ordner, 'modell': info.get('name') or ordner, 'ordner': ordner,
                          'geschlecht': info.get('geschlecht') if info.get('geschlecht') in ('weiblich', 'maennlich') else 'weiblich', 'paar': True})
        cls._ablage['paare'] = {'stand': stand, 'zeit': time.monotonic(), 'paare': paare}
        return [dict(p) for p in paare]
