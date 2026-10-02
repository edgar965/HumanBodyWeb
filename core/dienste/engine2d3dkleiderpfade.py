# -*- coding: utf-8 -*-
"""Engine2d3dKleiderpfade — wo die Ergebnisse eines Auftrags auf der Platte liegen, zum Kopieren (30.09.2026).

Wie `Meshpfade`: Ordner zuerst, dann die Ablage. Jeder Eintrag wird gegen die Platte geprüft (`fehlt`),
damit die Seite keinen Pfad anbietet, der nicht existiert. Reine Leseoperation.

    Auftragsordner   `<OBJECTS_ROOT>/engine2d3dkleiderauftraege/<kennung>/` — die Quelle der Wahrheit
    Ablage           `output/Export/Engine2d3dKleider/<Name>_<Anlagezeit>/` — Modell, Kacheln, Bilder, Bericht
"""

from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
from .engine2d3dkleiderspeichern import Engine2d3dKleiderspeichern

__all__ = ['Engine2d3dKleiderpfade']


class Engine2d3dKleiderpfade:
    @classmethod
    def fuer(cls, job):
        """`[{art, label, pfad, fehlt}, …]` für `Meshpfadliste.zeichnen`."""
        ablage = Engine2d3dKleiderablage(job.kennung)
        return [
            cls._eintrag('ordner', 'Auftragsordner', ablage.ordner()),
            cls._eintrag('ablage', 'Ablage (Haar Engine)', Engine2d3dKleiderspeichern.zielordner_fuer(job)),
        ]

    @staticmethod
    def _eintrag(art, label, pfad):
        return {'art': art, 'label': label, 'pfad': str(pfad), 'fehlt': not pfad.exists()}
