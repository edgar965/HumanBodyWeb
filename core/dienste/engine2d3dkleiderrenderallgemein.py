# -*- coding: utf-8 -*-
"""Engine2d3dKleiderrenderallgemein — das Render-Rezept für Aufträge OHNE eigene `arbeit/render/rezept.json` (04.10.2026).

Edgar: „warum sehe ich diese Bereiche: Rendern usw. nicht auf …11.11.44? Mach mir Buttons zum Erzeugen des Videos usw." — „Rendern" war nur bei Randy möglich, weil dort ein Rezept liegt
(seine Programme in `ProjektTemp/_wegwerf/randy/film`, mit Stoff- und Strähnenwerten für Hemd, Federn und Ketten). Das allgemeine Rezept rendert das Standmodell jedes Auftrags: Figurcache
(Haut, Mimik, Gelenkkorrektur) und Mitsuba — ohne Simulation, Kleider, Haar und Zubehör hängen gehäutet an der Figur.

Die Programme stehen als Vorlage in `Figurfilm/standfilm/` und werden je Auftrag nach `arbeit/render/film/` KOPIERT (`einrichten`, vom Render-Prozess vor dem Lauf): `Engine2d3dKleiderrender`
schreibt vor jedem Lauf die GLB in `figur.json` des Programmordners und räumt `videos/<name>` — zwei Aufträge dürfen sich diesen Ordner nicht teilen. Ein eigenes Rezept des Auftrags geht vor.
"""

import shutil
from pathlib import Path

from django.conf import settings

__all__ = ['Engine2d3dKleiderrenderallgemein']


class Engine2d3dKleiderrenderallgemein:
    VORLAGE = Path(str(settings.BASE_DIR)).parent / 'Figurfilm' / 'standfilm'
    ORDNER = 'film'
    #: Programme und Profil werden bei jedem Lauf von der Vorlage übernommen; `figur.json` ist Zustand des Auftrags und bleibt, wenn sie schon da ist.
    PROGRAMME = ('video_bauen.py', 'film_video.py', 'mimik_export.py', 'korrektur_export.py', 'dj_ohne_log.py', 'profil_generisch.json')
    ZUSTAND = ('figur.json',)

    def __init__(self, render_ordner):
        """`render_ordner`: `arbeit/render/` des Auftrags (`Engine2d3dKleiderrender._datei('').parent`)."""
        self.ziel = Path(render_ordner) / self.ORDNER

    def verfuegbar(self):
        return all((self.VORLAGE / name).is_file() for name in self.PROGRAMME + self.ZUSTAND)

    def rezept(self):
        """Das Rezept im Format von `rezept.json` — oder None, wenn die Vorlage fehlt. Schreibt nichts (der Zustand der Seite fragt das bei jeder Abfrage)."""
        if not self.verfuegbar():
            return None
        return {'programme': str(self.ziel), 'name': 'render', 'allgemein': True,
                'hinweis': 'Allgemeines Rezept (Figurfilm/standfilm): Standmodell mit Bewegung und Ton, ohne Stoff- und Straehnensimulation.'}

    def einrichten(self):
        """Die Programme der Vorlage nach `arbeit/render/film/` kopieren — der Programmordner des Auftrags."""
        if not self.verfuegbar():
            raise RuntimeError('Die Vorlage des allgemeinen Render-Rezepts fehlt: %s' % self.VORLAGE)
        self.ziel.mkdir(parents=True, exist_ok=True)
        for name in self.PROGRAMME:
            shutil.copyfile(self.VORLAGE / name, self.ziel / name)
        for name in self.ZUSTAND:
            if not (self.ziel / name).is_file():
                shutil.copyfile(self.VORLAGE / name, self.ziel / name)
        return self.ziel
