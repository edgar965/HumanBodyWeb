# -*- coding: utf-8 -*-
u"""Haut- und Lagenmaske fuer den Film — was unter Stoff liegt, wird nicht
gerendert.

Dieselbe Entscheidung wie in der Szene (`scene/hautverdeckung.js`,
`scene/lagenverdeckung.js`, 11.09.2026): Die Rechnung steht in
`hautmaske.py`, hier nur, wo sie im Film ansetzt. Gerechnet wird EINMAL in
Ruhelage (die Teile sind noch nicht gehaeutet), gerendert wird je Bild mit
dem gekuerzten Index und dem Einzug der verdeckten Ecken.

Die Physik (`Filmphysik`, `Stoffgrenze`) rechnet weiter mit dem VOLLEN
Index — die verdeckten Punkte sind genau die, an denen der Stoff haengt.
"""
import logging

import numpy as np

from feinkoerper import Feinkoerper
from hautmaske import Hautmaske
from lagenmaske import Lagenmaske
from maskengeometrie import Geometrie

logger = logging.getLogger(__name__)


class Filmmasken:
    u"""Masken an die Teile eines `Hbfilm` haengen und beim Rendern anwenden."""

    @classmethod
    def anwenden(cls, teile, melder=None):
        u"""`teile[0]` ist der Koerper, der Rest die Stuecke (Ruhelage)."""
        if not teile:
            return []
        koerper = teile[0]
        stoffe = [(t['name'], t['haut'].punkte, t['dreiecke']) for t in teile[1:]]
        if not stoffe:
            return []
        if melder:
            melder(u'Hautmaske', 0.08)
        kp, kd = Feinkoerper.ruhe(koerper), Feinkoerper.dreiecke(koerper)
        maske = Hautmaske.verdeckt(kp, kd, [(p, d) for _n, p, d in stoffe])
        bericht = [cls._eintragen(koerper, maske, [n for n, _p, _d in stoffe])]
        lagen = Lagenmaske.verdeckt(kp, kd, stoffe) if len(stoffe) > 1 else {}
        for teil in teile[1:]:
            maske, ueber = lagen.get(teil['name'], (None, []))
            if ueber:
                bericht.append(cls._eintragen(teil, maske, ueber))
        cls._melden(bericht)
        return bericht

    @staticmethod
    def _melden(bericht):
        u"""Ins Log UND auf die Konsole: `filmlauf.py` laeuft als Unterprozess,
        dessen Ausgabe die `lauf.log` des Auftrags ist."""
        for name, punkte, dreiecke, unter in bericht:
            zeile = (u'Maske: %s — %d Punkte unter %s, %d Dreiecke nicht gerendert'
                     % (name, punkte, u', '.join(unter), dreiecke))
            logger.info(zeile)
            print(zeile)

    @staticmethod
    def _eintragen(teil, maske, unter):
        u"""Maske und gekuerzten Index am Teil ablegen; eine Berichtszeile
        (Name, verdeckte Punkte, nicht gerenderte Dreiecke, Stuecke darueber)."""
        teil['maske'] = maske
        dreiecke = Feinkoerper.dreiecke(teil)
        teil['dreiecke_sichtbar'], _weg = Hautmaske.index_ohne(dreiecke, maske)
        return (teil['name'], int(maske.sum()),
                len(dreiecke) - len(teil['dreiecke_sichtbar']), unter)

    @staticmethod
    def gerendert(teil, nummer):
        u"""Punkte, Dreiecke und Normalen fuer Bild `nummer`: gekuerzter
        Index, die verdeckten Ecken der Randdreiecke nach innen gezogen.
        Die Normalen (nach aussen, signiertes Volumen) kommen mit — der
        Renderer braucht sie ohnehin, und `trimesh` rechnete sie sonst je
        Bild ein zweites Mal aus 138.304 Dreiecken."""
        punkte = np.asarray(Feinkoerper.bild(teil, nummer), dtype=np.float64)
        dreiecke = Feinkoerper.dreiecke(teil)
        normalen = Geometrie.normalen(punkte, dreiecke)
        maske = teil.get('maske')
        if maske is None or not maske.any():
            return punkte, dreiecke, normalen
        eingezogen = np.array(punkte)
        eingezogen[maske] -= Hautmaske.EINZUG_M * normalen[maske]
        return eingezogen, teil['dreiecke_sichtbar'], normalen
