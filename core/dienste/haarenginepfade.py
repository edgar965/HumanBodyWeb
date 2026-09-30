# -*- coding: utf-8 -*-
"""Haarenginepfade — wo die Ergebnisse eines Auftrags auf der Platte liegen, zum Kopieren (30.09.2026).

Wie `Meshpfade`: Ordner zuerst, dann die Ablage. Jeder Eintrag wird gegen die Platte geprüft (`fehlt`),
damit die Seite keinen Pfad anbietet, der nicht existiert. Reine Leseoperation.

    Auftragsordner   `<OBJECTS_ROOT>/haarengineauftraege/<kennung>/` — die Quelle der Wahrheit
    Ablage           `output/Export/HaarEngine/<Name>_<Anlagezeit>/` — Modell, Kacheln, Bilder, Bericht
"""

from ..daten.haarengineablage import Haarengineablage
from .haarenginespeichern import Haarenginespeichern

__all__ = ['Haarenginepfade']


class Haarenginepfade:
    @classmethod
    def fuer(cls, job):
        """`[{art, label, pfad, fehlt}, …]` für `Meshpfadliste.zeichnen`."""
        ablage = Haarengineablage(job.kennung)
        return [
            cls._eintrag('ordner', 'Auftragsordner', ablage.ordner()),
            cls._eintrag('ablage', 'Ablage (Haar Engine)', Haarenginespeichern.zielordner_fuer(job)),
        ]

    @staticmethod
    def _eintrag(art, label, pfad):
        return {'art': art, 'label': label, 'pfad': str(pfad), 'fehlt': not pfad.exists()}
