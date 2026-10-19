# -*- coding: utf-8 -*-
u"""G9anatomiedrapierung — Stoff über dem männlichen Geograft drapieren (16.10.2026): die Anbindung von `G9drapierer` an die Stückrechnung.

WARUM (Edgar, 16.10.2026: „bei dem männlichen Geschlechtsteile fitten die Kleider alle nicht" — „das soll schön drapieren, wie ein Kleidungsstück,
und nicht das Kleidungsstück nach vorne ziehen, wo dann das Genital sichtbar ist" — „dieser Drapierer soll auch einstellbar sein")
============================================================================================================================================
Ohne dies stehen Hose und Shorts als Zackenstern um das Geograft, die Spitze schaut mittig durch (gesehen im Chrome, Daz Mann, JS Pants). Verfahren,
Quellen, Maße und Grenzen: `Genesis9/drapierer.py`; die drei Regler (Abstand, Ausbreitung, Glättung) und ihre Vorgaben: `Genesis9/drapierung.py`.

Nur über dem MÄNNLICHEN Geograft (`ANATOMIEN`): Am weiblichen ging es mit der Kollision allein (28,2 % → 11,5 %, `genesis9-daz-geograft.md`), es
liegt flach auf der Haut. Ob der Drapierer dort schadet oder nützt, ist nicht gemessen.
"""
import logging

import numpy as np
from Genesis9.drapierer import G9drapierer
from Genesis9.drapierhindernis import G9drapierhindernis
from Genesis9.drapierung import G9drapierung

from .g9hbstoffkorrektur import G9hbstoffkorrektur

logger = logging.getLogger('core')

__all__ = ['G9anatomiedrapierung']


class G9anatomiedrapierung:
    u"""`fuer(innen)` -> Drapierung oder None; `anwenden(punkte, flaechen, normalen, regler)` -> (Punkte, Bilanz)."""

    #: Nur diese Anatomien (`G9stueckersatz.anatomie_fuer`).
    ANATOMIEN = ('penis',)

    def __init__(self, hindernis):
        self.hindernis = hindernis

    @classmethod
    def fuer(cls, innen, formung=None):
        u"""Das Hindernis aus den Anatomie-Stücken unter `innen` (Kennungen) — oder None, wenn keines der `ANATOMIEN` getragen wird. Mit `formung` liegen die Stücke dort,
        wo der Browser sie zeigt: Ruhelage (`G9stueckstarr.punkte`), an den Ring der Haut gerückt (`G9stueckstarr.nachgezogen`, wie `G9lagen.kaefig`).

        Edgar, 19.10.2026: „mach das auch für männliche Genitalien mit Matt0" — an Matt0 steht das Geograft im Browser gleichmäßig 31,5 mm neben der Ruhelage; der
        Drapierer hob den Stoff über eine Stelle, an der das gezeigte Glied nicht hängt, und die Eichel stach unter dem Bund der GC Pants Wool durch."""
        from Genesis9.garderobe import G9garderobe
        from Genesis9.stueckersatz import G9stueckersatz
        from Genesis9.stueckstarr import G9stueckstarr

        from .g9lagenanfrage import G9lagenanfrage
        stuecke, haut = [], None
        for kennung in innen:
            if not G9lagenanfrage._anatomie(kennung):
                continue
            eintrag = G9garderobe.eintrag(kennung) or {}
            if G9stueckersatz.anatomie_fuer(eintrag) not in cls.ANATOMIEN:
                continue
            teile = G9garderobe.teile(kennung)
            if haut is None and formung is not None:
                from Genesis9.koerpernetz import G9koerpernetz
                haut = G9koerpernetz(formung, stufen=1).koerperflaeche()[0]
            punkte = G9stueckstarr.nachgezogen(eintrag, G9stueckstarr.punkte(teile, formung), haut, formung)
            stuecke += list(zip(punkte, (folger.polys for folger, _lage in teile), strict=True))
        if not stuecke:
            return None
        return cls(G9drapierhindernis.aus_stuecken(stuecke))

    def anwenden(self, punkte, flaechen, normalen, regler):
        u"""`(punkte (N, 3), bilanz)`: der Stoff mit `flaechen` (Dreiecke oder Vierecke des Browsernetzes) und seinen Normalen `normalen` (N, 3),
        über das Hindernis drapiert; `regler`: `regler_stueck` des Rumpfs (`G9drapierung.werte`)."""
        punkte = np.asarray(punkte, dtype=np.float64)
        dreiecke = G9hbstoffkorrektur.dreiecke(flaechen, len(punkte))
        if not len(punkte) or not len(dreiecke) or normalen is None:
            return punkte, {'gehoben': 0}
        abstand, ausbreitung, glaettung = G9drapierung.werte(regler)
        return G9drapierer.drapieren(punkte, dreiecke, np.asarray(normalen, dtype=np.float64), self.hindernis, abstand, ausbreitung, glaettung)
