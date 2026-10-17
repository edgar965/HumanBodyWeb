# -*- coding: utf-8 -*-
"""Architekturmesh3daigroesse — Größe und Grafikspeicher des Netzes, und wie viele Regler eine Ausgabe „Genesis + Kleider“ hätte (Hilfe → Architektur → Mesh3DAI, 16.10.2026).

Edgar: „schreibe auch die Größe des Netzes darunter, sowie den GPU-Bedarf beim Laden“ und „bei der Ausgabe schreibe die gesamte Anzahl der Parameter für die Genesis- und Kleider-Regler“.
Beides sind MESSUNGEN mit Datum, gelesen aus `3DObjects/mesh3dai/`:
    netzgroesse.json   `ProjektTemp/_wegwerf/mesh3dai_netz_groesse.py` (python10, GPU): Gewichte, Datei, Speicher nach dem Laden, Spitze je Vorhersage und Trainingsschritt bei 4.096/8.192/16.384 Punkten
    reglerzahl.json    `ProjektTemp/_wegwerf/mesh3dai_kleider_regler_zaehlen.py`: Reglerkatalog des Bedienfelds (`G9reglerplan.bereiche()`) und die Regler aller Garderobe-Einträge (`G9garderobe.liste()`)
Fehlt eine Datei, wirft `lesen` — die Seite zeigt den Grund als Befund (`Architekturmesh3dai.teil`).
"""

import json
from pathlib import Path

__all__ = ['Architekturmesh3daigroesse']


class Architekturmesh3daigroesse:
    @staticmethod
    def _datei(name):
        from django.conf import settings
        pfad = Path(settings.OBJECTS_ROOT) / 'mesh3dai' / name
        if not pfad.is_file():
            raise FileNotFoundError('%s fehlt — erst das Messskript aus ProjektTemp/_wegwerf/ laufen lassen' % name)
        return json.loads(pfad.read_text(encoding='utf-8'))

    @classmethod
    def lesen(cls):
        netz = cls._datei('netzgroesse.json')
        regler = cls._datei('reglerzahl.json')
        regler['gesamt'] = int(regler['genesis']) + int(regler['kleider_regler'])
        regler['kleidung_passform'] = 2 * int(regler['stuecke_je_art'].get('kleidung', 0))      # je Kleidungsstück Länge und Weite (`G9passform.regler`, in `regler` enthalten)
        vorhersage = {v['punkte']: v for v in netz.get('vorhersage', [])}
        return {'netz': netz, 'regler': regler, 'vorhersage_4096': vorhersage.get(4096), 'training_4096': next((t for t in netz.get('training', []) if t['punkte'] == 4096), None)}
