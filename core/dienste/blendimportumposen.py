# -*- coding: utf-8 -*-
"""Blendimportumposen — Schritt „umposen": Körper, Kleider und Haar der .blend in die Genesis-Haltung bringen.

Edgar (08.10.2026): „baue die Knochenkarten (ist das Modell nicht geriggt?)". Das Modell IST geriggt (Auto-Rig Pro); sein Rig
liefert, was „Mesh to 3D" sonst aus Bildern schätzen müsste — die Haltung. Die Karte ARP → Genesis (`G9arpknochenkarte`)
nennt je Gliedmaß die Richtung in der Genesis-Ruhelage; `blendumposen.py` dreht die Segmente im Rig starr dorthin und
häutet alle Netze mit den Gewichten der .blend nach (Einzelheiten dort). Danach lesen alle weiteren Schritte die Punkte in
Genesis-Haltung aus dem Export (`punkte`; `punkte_vorher` bleibt als Original).

Die Form liefert das Rig NICHT: das Modell hat keine Morphs, nur Knochen — Regler und Eigenmorph, die das Aussehen
tragen, rechnet weiter „Mesh to 3D" (`Blendimportfigur`), jetzt auf einem Körper, der schon in Genesis-Haltung steht.

Schritt aus (Einstellung `umposen` = `aus`) oder passt das Rig nicht (weniger als die Hälfte der Segmente gefunden, z. B.
ein anderes Rig als Auto-Rig Pro): die Punkte bleiben, wie der Export sie las; der Grund steht im Ergebnis.
"""

import json
import logging

logger = logging.getLogger('core')

__all__ = ['Blendimportumposen']


class Blendimportumposen:
    SKRIPT = 'blendumposen.py'
    ERGEBNIS = 'umposen.json'
    KARTE = 'umposen_karte.json'

    def __init__(self, ablage, melden=None):
        self.ablage = ablage
        self.melden = melden

    def karte(self):
        from Genesis9.arpknochenkarte import G9arpknochenkarte

        pfad = self.ablage.export(self.KARTE)
        pfad.write_text(json.dumps(G9arpknochenkarte.karte(), ensure_ascii=False, indent=1), encoding='utf-8')
        return pfad

    def umposen(self, blend):
        """Blender rechnen lassen; `{segmente, netze, …}` aus `umposen.json` oder `{'uebersprungen': Grund}`."""
        from .blendimportblender import Blendimportblender

        ergebnis = Blendimportblender(self.ablage, self.melden).laufen(
            self.SKRIPT, blend, ['--ziel', self.ablage.export(), '--karte', self.karte()],
            self.ablage.export(self.ERGEBNIS))
        bericht = json.loads(ergebnis.read_text(encoding='utf-8'))
        gefunden = [s for s in bericht['segmente'] if s['drehung_grad'] is not None]
        logger.info('Blender-Import %s: Umposen, %d von %d Segmenten gedreht', self.ablage.kennung, len(gefunden),
                    len(bericht['segmente']))
        return bericht
