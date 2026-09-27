# -*- coding: utf-8 -*-
"""Meshpfade — wo das fertige Netz auf der Platte liegt, zum Kopieren.

Edgar (27.09.2026): „zeige mir in den Job seiten … wo das Mesh gespeichert ist, so
dass ich den Pfad kopieren kann". Die Auftragsseite zeigte bis dahin nur
Download-Knöpfe — der Pfad stand nirgends, obwohl es zwei Orte gibt:

  1. den Auftragsordner (`<OBJECTS_ROOT>/meshauftraege/<kennung>/ergebnis/`, die Quelle
     der Wahrheit — dort liegen GLB, OBJ+MTL und PLY desselben Laufs),
  2. die Ablagekopie unter `settings.MESH_FOTO3D_EXPORT_DIR` (`Meshexportablage`).

Jeder Eintrag wird gegen die Platte geprüft (`fehlt`), damit die Seite keinen Pfad
anbietet, der nicht existiert — ein kopierter Pfad ins Leere kostet mehr Zeit als
keiner. Reine Leseoperation, kein Ordner wird angelegt.
"""

from ..daten.meshablage import Meshablage
from .meshexportablage import Meshexportablage

__all__ = ['Meshpfade']


class Meshpfade:
    """Die Ablageorte eines Mesh-Auftrags als Liste für die Oberfläche."""

    #: Welche Ergebnisdateien einen eigenen Pfadeintrag bekommen (Reihenfolge = Anzeige).
    DATEIEN = (('glb', 'GLB'), ('obj', 'OBJ'), ('ply', 'PLY'))

    @classmethod
    def fuer(cls, job):
        """`[{art, label, pfad, fehlt}, …]` — Ordner zuerst, dann die Dateien, dann die Ablage."""
        ablage = Meshablage(job.kennung)
        ergebnis = ablage.unter(Meshablage.ERGEBNIS)
        aus = [cls._eintrag('ordner', 'Ergebnisordner', ergebnis)]
        dateien = ((job.ergebnis or {}).get('dateien') or {})
        for art, label in cls.DATEIEN:
            name = dateien.get(art)
            if name:
                aus.append(cls._eintrag(art, label, ergebnis / name))
        kopie = Meshexportablage.pfad(job)
        aus.append(cls._eintrag('ablage', 'Ablage (Foto3D)', kopie))
        return aus

    @staticmethod
    def _eintrag(art, label, pfad):
        return {'art': art, 'label': label, 'pfad': str(pfad), 'fehlt': not pfad.exists()}
