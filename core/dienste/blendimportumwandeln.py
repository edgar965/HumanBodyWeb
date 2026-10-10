# -*- coding: utf-8 -*-
"""Blendimportumwandeln — Schritt „umwandeln": eine OBJ oder FBX wird zur `quelle.blend` (Modell-Import, 10.10.2026).

Blender liest die Datei im Hintergrund (`blendumwandeln.py`: Import, fehlende Texturen suchen, Deckkraft der Materialien klären,
als .blend speichern) — derselbe Weg wie `Blendimportblender` für Export und Backen, nur ohne Quell-.blend davor. Danach ist die Datei
eine .blend wie jede andere: `blendexport.py`, Rollen, Körper, „Mesh to 3D", Stücke und Haut backen lesen sie unverändert. Das ist der
Grund, warum der OBJ/FBX-Import keinen eigenen Leser für Netze, Gewichte und Materialien hat: was Blender aus der Datei macht, ist
bereits der Vertrag der bestehenden Kette.

Der Bericht des Skripts (`export/umwandeln.json`) steht im Ergebnis des Schritts: benutztes Werkzeug, Netze, Armaturen, Knochen, Höhe,
Bilder (gefunden / umgelenkt / fehlen). Ein Bild, das fehlt, bricht nichts ab — das Material hat dann keinen Kanal (wie bei der .blend).
"""

import json
import logging

from .blendimportblender import Blendimportblender

logger = logging.getLogger('core')

__all__ = ['Blendimportumwandeln']


class Blendimportumwandeln:
    SKRIPT = 'blendumwandeln.py'
    BERICHT = 'umwandeln.json'

    def __init__(self, ablage, melden=None):
        self.ablage = ablage
        self.melden = melden

    def wandeln(self, datei, format):
        """`datei` (.obj/.fbx) → `ablage.quelle_blend()`; gibt den Bericht des Skripts zurück."""
        ziel = self.ablage.quelle_blend()
        bericht = self.ablage.export(self.BERICHT)
        Blendimportblender(self.ablage, self.melden).laufen(
            self.SKRIPT, None, ['--quelle', datei, '--format', format, '--ziel', ziel, '--bericht', bericht], ziel)
        daten = json.loads(bericht.read_text(encoding='utf-8'))
        if daten.get('bilder', {}).get('fehlen'):
            logger.warning('Modell-Import %s: %d Bilder nicht gefunden (%s)', self.ablage.kennung, len(daten['bilder']['fehlen']),
                           ', '.join(daten['bilder']['fehlen'][:6]))
        return daten
