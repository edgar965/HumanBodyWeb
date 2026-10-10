# -*- coding: utf-8 -*-
"""Hautbacken — backt die Bilder einer Kachel (Farbe, Rauheit, Normalen) aus dem Körper der fremden Datei auf die Figur, ohne Blender.

    quelle = Hautbackenquelle(punkte, dreiecke, uv_ecken)                  # einmal je Import
    backen = Hautbacken(quelle, px=8192)
    ergebnis = backen.backen(figur, farbe=Hautbackenbild.aus_datei(…), rauheit=…, normalen=…)

Die Regeln sind die von `blendbacken.py` (Blender, Cycles „Selected to Active"): ein Strahl je Texel, `AUSZUG_M` über der Figur gestartet, entlang der geglätteten Normale
nach innen, höchstens `STRAHL_M` weit — `STRAHL_M` ist die GANZE Länge ab dem Start, nicht ab der Fläche (gemessen an Rosemarys Kachel 1001: bei 15 + 20 mm trifft der Nachbau
keinen Texel, den Blender schwarz lässt; bei 15 + 25 mm 44.882). Die Treffer teilen sich alle Kanäle: Blender schoss für jedes Bild neu.
"""

from .hautbackenkachel import Hautbackenkachel
from .hautbackennormalen import Hautbackennormalen
from .hautbackenrand import Hautbackenrand

__all__ = ['Hautbacken']


class Hautbacken:
    #: Wie `Blendbacken.AUSZUG_M` / `STRAHL_M` (Meter).
    AUSZUG_M = 0.015
    STRAHL_M = 0.035

    def __init__(self, quelle, px, geraet='cuda:0'):
        self.quelle, self.px, self.geraet = quelle, int(px), geraet

    def kachel(self, figur):
        """Das Raster einer Kachel der Figur (`Hautbackenflaeche`)."""
        return Hautbackenkachel(figur, self.px, self.geraet)

    def treffer(self, kachel):
        return kachel.schiessen(self.quelle, self.AUSZUG_M, self.STRAHL_M)

    def backen(self, figur, farbe=None, rauheit=None, normalen=None, rand=True):
        """`{'treffer': Hautbackentreffer, 'maske': (px, px) bool (getroffen), 'belegt': … (getroffen + Rand), 'farbe'|'rauheit'|'normalen': (px, px, 3) uint8}` — nur die Kanäle,
        deren Bild (`Hautbackenbild`) übergeben ist. Mit `rand` (Vorgabe, wie Blender) liegt um die getroffenen Texel ein Rand von `Hautbackenrand.BREITE_PX` Texeln."""
        kachel = self.kachel(figur)
        treffer = self.treffer(kachel)
        maske = treffer.maske()
        aus = {'treffer': treffer, 'maske': maske, 'belegt': maske}
        kanaele = {}
        if farbe is not None:
            kanaele['farbe'] = farbe.abtasten(treffer, self.quelle)
        if rauheit is not None:
            kanaele['rauheit'] = rauheit.abtasten(treffer, self.quelle)
        if normalen is not None:
            kanaele['normalen'] = Hautbackennormalen(self.quelle).backen(kachel, treffer, normalen)
        for name, bild in kanaele.items():
            aus[name], belegt = Hautbackenrand(self.geraet).erweitern(bild, maske) if rand else (bild, maske)
            aus['belegt'] = belegt
        return aus
