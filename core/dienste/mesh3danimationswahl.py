# -*- coding: utf-8 -*-
"""Mesh3danimationswahl — die Standardanimation eines Mesh-3D-Auftrags (13.10.2026).

Edgar: „standardanimation soll bei jedem Job einstellbar sein unterhalb der Animation Controls, standard animation ist danceKurz“. Die Animationsleiste der 3D-Ansicht spielt die Bewegung, die der Knopf
„Animation“ rechnet (`Mesh3dbewegung`); bis 13.10.2026 war das immer der Tanz der Bibliothek (`Daz/Dance.bvh`). Jetzt wählt der Auftrag seine Datei selbst, Vorgabe `A_Results/DanceKurz.bvh`.

Gespeichert wird die Wahl als `animation.json` im Importordner (`{"bvh": "Kategorie/Name"}`, der Name ohne `.bvh`, wie `Animationsauswahl` mit `wertformat=pfad` ihn liefert) — NICHT in `stand.json`: die schreibt der Arbeitsprozess
eines rechnenden Auftrags aus seinem eigenen Wörterbuch neu und risse ein ergänztes Feld mit weg (wie bei `mesh3d_reiter.json`). Eine Kopie des Auftrags erbt die Wahl (`animation.json` steht nicht in `Ordnerkopie.NIE_NAMEN`).

Ist die gewählte Datei nicht mehr im Bestand, meldet `zustand()` `fehlt` und `pfad()` fällt auf die Vorgabe zurück — kein stiller Wechsel: die Seite zeigt die Wahl samt Hinweis.
"""

import json
import logging

from ..atomic_write import AtomarSchreiber
from ..daten.blendimportablage import Blendimportablage
from .bvhverzeichnis import Bvhverzeichnis

logger = logging.getLogger('core')

__all__ = ['Mesh3danimationswahl']


class Mesh3danimationswahl:
    DATEI = 'animation.json'
    #: Die Vorgabe jedes Auftrags: Kategorie und Name (ohne `.bvh`) in der BVH-Bibliothek.
    STANDARD = ('A_Results', 'DanceKurz')

    def __init__(self, kennung, verzeichnis=None):
        self.ablage = Blendimportablage(kennung)
        self.verzeichnis = verzeichnis or Bvhverzeichnis()

    # ------------------------------------------------------------------ Lesen

    def _datei(self):
        return self.ablage.ordner() / self.DATEI

    @classmethod
    def standardwert(cls):
        return '%s/%s' % cls.STANDARD

    def gespeichert(self):
        """Der gespeicherte Wert `Kategorie/Name` oder `''` (keine Datei, kaputt, leer)."""
        try:
            roh = json.loads(self._datei().read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return ''
        wert = roh.get('bvh') if isinstance(roh, dict) else ''
        return wert if isinstance(wert, str) else ''

    def gewaehlt(self):
        """Was dieser Auftrag spielt: die gespeicherte Wahl, sonst die Vorgabe."""
        return self.gespeichert() or self.standardwert()

    @staticmethod
    def zerlegen(wert):
        """`(Kategorie, Name)` aus `Kategorie/Name`, sonst `None` — nur ein Schrägstrich, keine Pfadsprünge."""
        teile = str(wert or '').split('/')
        if len(teile) != 2 or not all(t.strip() for t in teile) or any(t in ('.', '..') or '\\' in t for t in teile):
            return None
        return teile[0], teile[1]

    def _vorhanden(self, kategorie, name):
        """Die Datei als Pfad, wenn es sie im Bestand gibt — geprüft gegen die Listen des Verzeichnisses, nicht gegen einen zusammengesetzten Pfad."""
        if kategorie not in self.verzeichnis.kategorienamen():
            return ''
        for datei in self.verzeichnis.dateien(kategorie):
            if datei.name == name:
                return datei.pfad
        return ''

    def pfad(self):
        """Der Pfad der `.bvh`, die gespielt wird: die Wahl, wenn es sie gibt, sonst die Vorgabe, sonst `''` (dann nimmt `Mesh3dbewegung` den Tanz der Bibliothek)."""
        for wert in (self.gewaehlt(), self.standardwert()):
            teile = self.zerlegen(wert)
            pfad = self._vorhanden(*teile) if teile else ''
            if pfad:
                return pfad
        return ''

    def zustand(self):
        """`{wahl, kategorie, name, standard, fehlt}` für die Jobseite."""
        wahl = self.gewaehlt()
        teile = self.zerlegen(wahl) or ('', '')
        return {
            'wahl': wahl,
            'kategorie': teile[0],
            'name': teile[1],
            'standard': wahl == self.standardwert(),
            'standardwahl': self.standardwert(),
            'fehlt': not (teile[0] and self._vorhanden(*teile)),
        }

    def kategorien(self):
        """`[{name, anzahl}]` — die Kategorien der Bibliothek ohne die leeren (die Einträge holt `/api/animationen/<kategorie>/`)."""
        aus = []
        for name in self.verzeichnis.kategorienamen():
            anzahl = self.verzeichnis.anzahl(name)
            if anzahl:
                aus.append({'name': name, 'anzahl': anzahl})
        return aus

    # ---------------------------------------------------------------- Schreiben

    def setzen(self, wert):
        """Die Wahl speichern; `ValueError` mit Grund, wenn es die Datei nicht gibt. Gibt `zustand()` zurück."""
        teile = self.zerlegen(wert)
        if teile is None:
            raise ValueError('Keine Animation: „%s“ (erwartet Kategorie/Name)' % wert)
        if not self._vorhanden(*teile):
            raise ValueError('Die Animation %s/%s gibt es nicht in der Bibliothek' % teile)
        AtomarSchreiber.json_schreiben(self._datei(), {'bvh': '%s/%s' % teile})
        logger.info('Mesh-3D %s: Standardanimation %s/%s', self.ablage.kennung, *teile)
        return self.zustand()
