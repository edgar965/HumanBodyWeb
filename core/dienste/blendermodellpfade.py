# -*- coding: utf-8 -*-
"""Blendermodellpfade — wo die Ergebnisse eines Auftrags auf der Platte liegen, zum Kopieren (29.09.2026).

Wie `Meshpfade` (Edgar, 27.09.2026: „zeige mir in den Job seiten … wo das Mesh gespeichert ist, so
dass ich den Pfad kopieren kann"): Ordner zuerst, dann die Dateien, dann die Ablage. Jeder Eintrag
wird gegen die Platte geprüft (`fehlt`), damit die Seite keinen Pfad anbietet, der nicht existiert.
Reine Leseoperation.

    Auftragsordner   `<OBJECTS_ROOT>/blendermodellauftraege/<kennung>/` — die Quelle der Wahrheit
    Netz (GLB)       das Netz aus den Fotos, `netz/mesh.glb`
    Ablage           `output/Export/BlenderModel/<Name>_<Anlagezeit>/` — Modell, Kacheln, Bilder, Netz
"""

from ..daten.blendermodellablage import Blendermodellablage
from .blendermodellspeichern import Blendermodellspeichern

__all__ = ['Blendermodellpfade']


class Blendermodellpfade:
    @classmethod
    def fuer(cls, job):
        """`[{art, label, pfad, fehlt}, …]` für `Meshpfadliste.zeichnen`."""
        ablage = Blendermodellablage(job.kennung)
        return [
            cls._eintrag('ordner', 'Auftragsordner', ablage.ordner()),
            cls._eintrag('netz', 'Netz (GLB)', ablage.netz(Blendermodellablage.NETZDATEI)),
            cls._eintrag('ablage', 'Ablage (BlenderModel)', Blendermodellspeichern.zielordner_fuer(job)),
        ]

    @staticmethod
    def _eintrag(art, label, pfad):
        return {'art': art, 'label': label, 'pfad': str(pfad), 'fehlt': not pfad.exists()}
