# -*- coding: utf-8 -*-
"""Engine2d3dKleidervorbereitungsliste — die Fotos nach dem Schritt „Vorbereitung", wie die Seite sie unter den Originalen zeigt (03.10.2026).

Liest `vorbereitet/vorbereitung.json` (`mesh_vorbereitungsstand`) und gibt je Foto Datei, Rolle, Größe, Vorschaubild und den Befund der Ausrichtung zurück — nur Fotos, deren Vorschaubild da ist. `veraltet` sagt, dass
die Ablage nicht mehr zu den Fotos und Optionen des Auftrags passt (ein Foto ersetzt, die Option geändert): Die Seite zeigt sie dann mit Warnung statt als aktuellen Stand. Maßgeblich ist DIESELBE Prüfung wie im Runner
(`Vorbereitungsstand.aktuell`, geladen über `Wrapperpfad`) — der Schritt „Netz" übernimmt die Bilder genau dann, wenn sie hier nicht veraltet sind.
"""

import logging

from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
from ..daten.wrapperpfad import Wrapperpfad
from .engine2d3dkleidernetz import Engine2d3dKleidernetz
from .engine2d3dkleideroptionen import Engine2d3dKleideroptionen

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleidervorbereitungsliste']


class Engine2d3dKleidervorbereitungsliste:
    @staticmethod
    def von(job):
        """`None`, wenn der Schritt noch nicht gerechnet hat, sonst `{stand, optionen, veraltet, grund, bilder}`."""
        ablage = Engine2d3dKleiderablage(job.kennung)
        ordner = str(ablage.unter(Engine2d3dKleiderablage.VORBEREITET))
        with Wrapperpfad():
            from mesh_vorbereitungsstand import Vorbereitungsstand
        stand = Vorbereitungsstand.lesen(ordner)
        if not stand:
            return None
        optionen = {**Engine2d3dKleideroptionen.netz(job.optionen), **Engine2d3dKleideroptionen.mesh(job.optionen),
                    **Engine2d3dKleideroptionen.vorbereitung(job.optionen)}
        passt, grund = Vorbereitungsstand.aktuell(ordner, Engine2d3dKleidernetz.bilder_fuer(job, ablage), optionen)
        bilder = []
        for e in stand.get('bilder', []):
            if (ablage.unter(Engine2d3dKleiderablage.VORBEREITET) / str(e.get('vorschau') or '-')).is_file():
                bilder.append({k: e.get(k) for k in ('datei', 'rolle', 'breite', 'hoehe', 'vorschau', 'ausrichtung')})
        return {'stand': stand.get('stand'), 'optionen': stand.get('optionen'), 'veraltet': not passt, 'grund': grund, 'bilder': bilder}
