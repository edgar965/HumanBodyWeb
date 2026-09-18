# -*- coding: utf-8 -*-
"""Haut- und Lagenmaske fuer den Film — was unter Stoff liegt, wird nicht
gerendert.

Dieselbe Entscheidung wie in der Szene (`scene/hautverdeckung.js`,
`scene/lagenverdeckung.js`, 11.09.2026): Die Rechnung steht in
`hautmaske.py`, hier nur, wo sie im Film ansetzt. Gerechnet wird EINMAL in
Ruhelage (die Teile sind noch nicht gehaeutet), gerendert wird je Bild mit
dem gekuerzten Index und dem Einzug der verdeckten Ecken — seit dem
13.09.2026 mit dem `Saumband`: Verdeckte Haut neben der gezeichneten bleibt
versenkt im Bild, aus dem Index faellt nur, was jenseits des Bands liegt.

Die Physik (`Filmphysik`, `Stoffgrenze`) rechnet weiter mit dem VOLLEN
Index — die verdeckten Punkte sind genau die, an denen der Stoff haengt.
"""

import logging
from collections import namedtuple

import numpy as np

from feinkoerper import Feinkoerper
from hautmaske import Hautmaske
from lagenmaske import Lagenmaske
from maskengeometrie import Geometrie
from saumband import Saumband
from saumschnitt import Saumschnitt

logger = logging.getLogger(__name__)


#: Eine Berichtszeile je maskiertem Teil: Name, verdeckte Punkte, nicht
#: gerenderte Dreiecke, die Stuecke darueber.
Maskenzeile = namedtuple("Maskenzeile", "name punkte dreiecke unter")


class Filmmasken:
    """Masken an die Teile eines `Hbfilm` haengen und beim Rendern anwenden."""

    @classmethod
    def anwenden(cls, teile, melder=None):
        """`teile[0]` ist der Koerper, der Rest die Stuecke (Ruhelage)."""
        if not teile:
            return []
        koerper = teile[0]
        stoffe = [(t["name"], t["haut"].punkte, t["dreiecke"]) for t in teile[1:]]
        if not stoffe:
            return []
        if melder:
            melder("Hautmaske", 0.08)
        kp, kd = Feinkoerper.ruhe(koerper), Feinkoerper.dreiecke(koerper)
        maske = Hautmaske.verdeckt(kp, kd, [(p, d) for _n, p, d in stoffe])
        bericht = [cls._eintragen(koerper, maske, [n for n, _p, _d in stoffe], teile[1:])]
        bericht.extend(cls._lagen(teile[1:], kp, kd, stoffe))
        cls._melden(bericht)
        return bericht

    @classmethod
    def _lagen(cls, stuecke, kp, kd, stoffe):
        """Stoff unter Stoff — je Stueck, das ein anderes ueberdeckt, eine Zeile."""
        if len(stoffe) < 2:
            return []
        lagen = Lagenmaske.verdeckt(kp, kd, stoffe)
        aus = []
        for teil in stuecke:
            maske, ueber = lagen.get(teil["name"], (None, []))
            if ueber:
                darueber = [t for t in stuecke if t["name"] in ueber]
                aus.append(cls._eintragen(teil, maske, ueber, darueber))
        return aus

    @staticmethod
    def _melden(bericht):
        """Ins Log UND auf die Konsole: `filmlauf.py` laeuft als Unterprozess,
        dessen Ausgabe die `lauf.log` des Auftrags ist."""
        for z in bericht:
            zeile = "Maske: %s — %d Punkte unter %s, %d Dreiecke nicht gerendert" % (
                z.name,
                z.punkte,
                ", ".join(z.unter),
                z.dreiecke,
            )
            logger.info(zeile)
            print(zeile)

    @staticmethod
    def _eintragen(teil, maske, unter, darueber):
        """Maske, gekuerzten Index und Saumschnitt am Teil ablegen; eine
        Berichtszeile (Name, verdeckte Punkte, nicht gerenderte Dreiecke,
        Stuecke darueber). `darueber`: die Teile, deren Kanten zaehlen."""
        teil["maske"] = maske
        dreiecke = Feinkoerper.dreiecke(teil)
        # Neben der gezeichneten Haut bleibt ein versenktes Band (`saumband.py`).
        teil["abstand_haut"] = Saumband.abstaende(Feinkoerper.ruhe(teil), maske, dreiecke)
        teil["naht"] = Geometrie.naht(Feinkoerper.ruhe(teil))
        teil["dreiecke_sichtbar"], _weg = Hautmaske.index_ohne(
            dreiecke, Saumband.weg(maske, teil["abstand_haut"])
        )
        # Verdeckte Randecken nahe einer Kante der Stuecke darueber enden an
        # dieser Kante (13.09.2026, `saumschnitt.py`) — gebunden in Ruhelage,
        # je Bild auf den gestellten Kanten ausgewertet.
        teil["saum"] = Saumschnitt.binden(
            Feinkoerper.ruhe(teil),
            dreiecke,
            maske,
            [(Feinkoerper.ruhe(t), Feinkoerper.dreiecke(t)) for t in darueber],
        )
        teil["saum_teile"] = list(darueber)
        return Maskenzeile(
            teil["name"], int(maske.sum()), len(dreiecke) - len(teil["dreiecke_sichtbar"]), unter
        )

    @staticmethod
    def gerendert(teil, nummer):
        """Punkte, Dreiecke und Normalen fuer Bild `nummer`: gekuerzter
        Index, die verdeckten Punkte mit dem Abstand zur gezeichneten Haut
        versenkt (`Saumband`), die Randecken unter die Kante (`Saumschnitt`).
        Die Normalen (nach aussen, signiertes Volumen) kommen mit — der
        Renderer braucht sie ohnehin, und `trimesh` rechnete sie sonst je
        Bild ein zweites Mal aus 138.304 Dreiecken."""
        punkte = np.asarray(Feinkoerper.bild(teil, nummer), dtype=np.float64)
        dreiecke = Feinkoerper.dreiecke(teil)
        normalen = Geometrie.normalen(punkte, dreiecke, teil.get("naht"))
        maske = teil.get("maske")
        if maske is None or not maske.any():
            return punkte, dreiecke, normalen
        eingezogen = np.array(punkte)
        saum = teil.get("saum")
        nach_innen = np.array(maske, dtype=bool)
        if saum is not None and len(saum):
            nach_innen[saum.ecken] = False
        tiefe = Saumband.tiefe(teil["abstand_haut"])
        eingezogen[nach_innen] -= tiefe[nach_innen, None] * normalen[nach_innen]
        if saum is not None and len(saum):
            saum.anwenden(eingezogen, normalen, [Feinkoerper.bild(t, nummer) for t in teil["saum_teile"]])
        return eingezogen, teil["dreiecke_sichtbar"], normalen
