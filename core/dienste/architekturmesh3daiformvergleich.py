# -*- coding: utf-8 -*-
"""Architekturmesh3daiformvergleich — Formkopf in der Pose gegen Formkopf auf der A-Pose-Wolke, auf Hilfe → Architektur → Mesh3DAI, Abschnitt 3 (17.10.2026).

Edgar: „BAUE das: Mein Vorschlag ist, die Form ebenfalls auf der A-Pose-Wolke zu lernen“. GELESEN: `3DObjects/mesh3dai/_vorstufe/form_vergleich.json`, geschrieben von
`ProjektTemp/_wegwerf/mesh3dai_form_vergleich.py` aus den beiden Läufen (`mesh3dai_form_alle.py` in der Pose, `mesh3dai_vorstufe_form.py` auf der A-Pose). Fehlt die Datei: None, der Abschnitt sagt es.
"""

import json
from pathlib import Path

__all__ = ['Architekturmesh3daiformvergleich']


class Architekturmesh3daiformvergleich:
    JOBS = ('Ursula1', 'Damira0', 'Mann1', 'Matt0')
    GRUPPE = {'training': 'Trainingsposen', 'pruefung': 'Prüfposen (nie trainiert)'}

    @staticmethod
    def datei():
        from django.conf import settings
        return Path(settings.OBJECTS_ROOT) / 'mesh3dai' / '_vorstufe' / 'form_vergleich.json'

    @classmethod
    def lesen(cls):
        try:
            d = json.loads(cls.datei().read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None
        jobs = []
        for job in cls.JOBS:
            for g, titel in cls.GRUPPE.items():
                w = d.get('figuren', {}).get(job, {}).get(g)
                if w:
                    jobs.append({'job': job, 'gruppe': titel, 'pose': w['pose'], 'apose': w['apose']})
        return {'pose': d.get('pose'), 'apose': d.get('apose'), 'regler': d.get('regler'),
                'zeilen': [{'titel': t, **z} for t, z in d.get('zusammen', {}).items()], 'jobs': jobs}
