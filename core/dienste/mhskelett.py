# -*- coding: utf-8 -*-
u"""Mhskelett — das Skelett, das MakeHuman selbst mitbringt.

WARUM (Edgar, 07.09.2026): „jedes Hinzufuegen eines Modells soll auch das
Skeleton dazu erzeugen … MakeHuman weiss ich nicht, welches Skeleton das
mitbringt." Gemessen: Es bringt genau eines mit — `data/rigs/default.mhskel`,
163 Knochen. Andere Rigs (cmu_mb, game engine) liegen im Upstream nicht bei;
diese eine Datei ist das Rig, das MakeHuman beim Start anbietet.

DIE GELENKE HAENGEN AM NETZ, NICHT AN ZAHLEN
============================================
`default.mhskel` speichert KEINE Koordinaten. Jeder Knochen nennt zwei
Gelenknamen (`head`, `tail`), und jeder Gelenkname steht in `joints` fuer
eine Liste von Vertexnummern — die Ecken eines Gelenkwuerfels in der
Helfergeometrie. Die Position ist deren Mittelwert:

    verts.mean(axis=0)          (`MakeHuman/makehuman/shared/skeleton.py`,
                                 `Skeleton.getJointPosition`, Zeile 434)

Deshalb folgt das Skelett den 269 Modellierreglern von selbst: Wer die Figur
groesser macht, verschiebt die Gelenkwuerfel mit, und der Mittelwert wandert.
Es ist kein zweiter Rechenweg, der mit dem ersten Schritt halten muesste.

MITTELWERT, NICHT MITTE DER HUELLE. Der Upstream nimmt `mean`, nicht das
Zentrum der Bounding-Box. Bei einem gleichmaessigen Wuerfel ist das dasselbe;
bei den Gelenkwuerfeln, die an ungleich dichte Stellen genaeht sind, nicht.

DIE PUNKTE KOMMEN AUS DEM BASISNETZ, NIE AUS DEM ANGEZEIGTEN
============================================================
Das angezeigte Netz kann geglaettet (Catmull-Clark) und um `delete_verts`
beschnitten sein — beides aendert die Vertexnummern. MakeHuman rechnet die
Gelenke ebenfalls auf dem Seed-Mesh (`getRestposeCoordinates`). Nur der
Bodenversatz wird uebernommen, damit Knochen und Haut im selben Raum stehen.
"""

import json
import logging
import os
import threading

import numpy as np

from django.conf import settings

from .mhbasisnetz import Mhbasisnetz

logger = logging.getLogger('core')

__all__ = ['Mhskelett']


class Mhskelett:
    u"""Knochen des MakeHuman-Rigs, gerechnet auf einem Netzzustand."""

    #: Der Upstream-Ordner, in dem MakeHuman seine Rigs fuehrt.
    ORDNER = 'rigs'
    DATEI = 'default.mhskel'

    #: Die Datei wird EINMAL gelesen (163 Knochen, 326 Gelenke). Sie aendert
    #: sich nicht, und jeder Figurwechsel wuerde sie sonst neu einlesen.
    _rig = None
    _schloss = threading.Lock()

    def __init__(self, formung=None):
        #: Die Reglerstellung (`Mhformung`); ohne sie das Basisnetz.
        self.formung = formung

    # --------------------------------------------------------------- lesen

    @classmethod
    def pfad(cls):
        return os.path.join(str(settings.MAKEHUMAN_DATA_DIR),
                            cls.ORDNER, cls.DATEI)

    @classmethod
    def vorhanden(cls):
        return os.path.isfile(cls.pfad())

    @classmethod
    def rig(cls):
        u"""`{bones, joints}` aus `default.mhskel` — einmal gelesen."""
        if cls._rig is not None:
            return cls._rig
        with cls._schloss:
            if cls._rig is None:
                with open(cls.pfad(), 'r', encoding='utf-8') as datei:
                    roh = json.load(datei)
                cls._rig = {'bones': roh.get('bones') or {},
                            'joints': roh.get('joints') or {},
                            'name': roh.get('name') or cls.DATEI}
        return cls._rig

    # --------------------------------------------------------------- bauen

    def bauen(self):
        u"""`{name, knochen: [{name, eltern, kopf, schwanz, pos, quat, ende}]}`.

        `kopf`/`schwanz` sind Weltpunkte in Three-Metern mit Y oben und den
        Fuessen auf 0 — derselbe Raum wie `Mhkoerpernetz.bauen()`; `pos` und
        `quat` sind daraus die lokale Lage jedes Knochens
        (`Gelenkskelett`). Knochen, deren Gelenke im Netz fehlen, fallen
        heraus statt auf (0,0,0) zu zeigen; ein Knochen im Boden ist
        schlimmer als ein fehlender.
        """
        return {'name': self.rig()['name'], 'knochen': self.kette().bauplan()}

    def kette(self):
        u"""Das `Gelenkskelett` dieser Reglerstellung — Anzeige UND Retarget-Ziel.

        Es ordnet die Knochen, rechnet `kopf`/`schwanz` in die LOKALE Lage um
        (`pos`, `quat`) und haengt an jedes Blatt einen Endknochen. Dieselbe
        Kette liefert dem Retarget-Motor sein Zielskelett; zwei Rechnungen,
        die auseinanderlaufen koennen, gibt es damit nicht.
        """
        from humanbody_core.skeleton.gelenkskelett import Gelenkskelett
        return Gelenkskelett(self._gelenkknochen())

    def _gelenkknochen(self):
        u"""`[{name, eltern, kopf, schwanz}]` — die rohen Gelenke der Datei."""
        rig = self.rig()
        stellen = self._gelenkstellen()
        knochen = []
        for name, angaben in rig['bones'].items():
            kopf = stellen.get(angaben.get('head'))
            schwanz = stellen.get(angaben.get('tail'))
            if kopf is None or schwanz is None:
                continue
            knochen.append({
                'name': name,
                'eltern': angaben.get('parent') or None,
                'kopf': [round(float(w), 6) for w in kopf],
                'schwanz': [round(float(w), 6) for w in schwanz],
            })
        return self._sortiert(knochen)

    def _gelenkstellen(self):
        u"""Gelenkname -> (x, y, z) im Raum des angezeigten Netzes."""
        basis = Mhbasisnetz.holen()
        roh = self.formung.punkte() if self.formung else None
        punkte = basis.punkte_three(roh)
        boden = basis.boden_von(roh)
        letzter = len(punkte) - 1
        stellen = {}
        for gelenk, nummern in self.rig()['joints'].items():
            gueltig = [n for n in nummern if 0 <= n <= letzter]
            if not gueltig:
                continue
            mitte = punkte[gueltig].mean(axis=0)
            stellen[gelenk] = (mitte[0], mitte[1] - boden, mitte[2])
        return stellen

    @staticmethod
    def _sortiert(knochen):
        u"""Eltern vor ihren Kindern.

        Der Browser haengt jeden Knochen an seinen Elternknochen; steht das
        Kind zuerst, gibt es den Elternteil noch nicht. Die Reihenfolge in
        `default.mhskel` ist alphabetisch (`breast.L` vor `spine01`), also
        genau nicht die gebrauchte.

        Wer zyklisch oder auf einen fehlenden Elternteil zeigt, kommt ans
        Ende und wird im Browser zu einem Wurzelknochen — verworfen wird
        nichts, sonst verschwaende eine kaputte Zeile in der Datei stumm
        einen halben Arm.
        """
        offen = {k['name']: k for k in knochen}
        aus, gesetzt = [], set()
        rest = True
        while rest:
            rest = False
            for name, k in list(offen.items()):
                eltern = k['eltern']
                if eltern is None or eltern in gesetzt or eltern not in offen:
                    aus.append(k)
                    gesetzt.add(name)
                    del offen[name]
                    rest = True
        aus.extend(offen.values())
        return aus
