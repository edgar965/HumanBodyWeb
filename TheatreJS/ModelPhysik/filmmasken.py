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
import numpy as np

from feinkoerper import Feinkoerper
from hautmaske import Geometrie, Hautmaske, Lagenmaske


class Filmmasken:
    u"""Masken an die Teile eines `Hbfilm` haengen und beim Rendern anwenden."""

    @classmethod
    def anwenden(cls, teile, melder=None):
        u"""`teile[0]` ist der Koerper, der Rest die Stuecke (Ruhelage)."""
        if not teile:
            return []
        koerper = teile[0]
        kp, kd = Feinkoerper.ruhe(koerper), Feinkoerper.dreiecke(koerper)
        stoffe = [(t['name'], t['haut'].punkte, t['dreiecke']) for t in teile[1:]]
        bericht = []
        if stoffe:
            if melder:
                melder(u'Hautmaske', 0.08)
            maske = Hautmaske.verdeckt(kp, kd, [(p, d) for _n, p, d in stoffe])
            cls._eintragen(koerper, maske)
            bericht.append((koerper['name'], int(maske.sum()),
                            len(kd) - len(koerper['dreiecke_sichtbar']),
                            [n for n, _p, _d in stoffe]))
            lagen = Lagenmaske.verdeckt(kp, kd, stoffe) if len(stoffe) > 1 else {}
            for teil in teile[1:]:
                maske, ueber = lagen.get(teil['name'], (None, []))
                if maske is not None and ueber:
                    cls._eintragen(teil, maske)
                    bericht.append((teil['name'], int(maske.sum()),
                                    len(teil['dreiecke']) - len(teil['dreiecke_sichtbar']),
                                    ueber))
        for name, punkte, dreiecke, unter in bericht:
            print(u'Maske: %s — %d Punkte unter %s, %d Dreiecke nicht gerendert'
                  % (name, punkte, u', '.join(unter), dreiecke))
        return bericht

    @staticmethod
    def _eintragen(teil, maske):
        teil['maske'] = maske
        teil['dreiecke_sichtbar'], _weg = Hautmaske.index_ohne(
            Feinkoerper.dreiecke(teil), maske)

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
