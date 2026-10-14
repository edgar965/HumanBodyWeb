# -*- coding: utf-8 -*-
"""Meshfigurgriffmodell — das Fingermodell des Blender-Imports, dazu Arm und Handgelenk der Seite (14.10.2026).

Beim Blender-Import liegt die Hand der Figur fast dort, wo die Hand des Originals ist (Median 3,9–9,3 mm), die Suche stellt nur die Finger. Beim Weg „netz" stimmt die Lage der Hand nicht so gut: am Zauberer liegen die
Sapiens-Handflächen im Mittel 9,4 cm neben der Käfig-Handmitte der Figur (gemessen `griff_ziel_arten.py`). Die erste Suche ohne Spielraum wählte darum die Handgröße am Anschlag (−30 %) statt die Finger zu beugen
(Median 13,7 → 10,1 mm, p90 an der Kappe, nicht angenommen). Mit einem freien Versatz der ganzen Hand (Probe 14.10.2026, 122 s) schloss sich die Faust (Median 16,5 → 4,1 mm, p90 30 → 11 mm gegenüber der gestreckten Hand an
bester Stelle), und der Versatz zeigte, wohin die echte Faust liegt: 5,7 cm hinter der Figurhand — auf der Achse des Stabs, den sie hält (Abstand der Stabachse zur Figurhand 4,4 cm, zur Faust 0).

Darum stellt dieses Modell zusätzlich NEUN Armwinkel der Seite (Oberarm, Unterarm, Handgelenk, je drei Kanäle, Zuwachs gegen die Haltung der Anpassung, `ARM`): die Hand kann auf die Faust des Netzes wandern, und weil es Winkel sind,
gelten sie für die gebackene Figur (`Meshfigurgriff.anwenden` addiert sie zu den Winkeln der Haltung). Die Vorliebe für Null (`VORLIEBE_M`) hält sie klein. Der Vergleich „vorher" für die Annahme ist die beste Lage der GESTRECKTEN Hand mit
denselben Armwinkeln (`ohne_finger`): nur was die Finger darüber hinaus verbessern, zählt.
"""

import numpy as np

from .blendimportfingermodell import Blendimportfingermodell

__all__ = ['Meshfigurgriffmodell']


class Meshfigurgriffmodell(Blendimportfingermodell):
    #: Glied, Grenze in Grad (Zuwachs gegen die Haltung der Anpassung), Kanäle. Setzungen: der Zauberer braucht rund 5 cm Hand-Versatz = einige Grad am Oberarm; die Gelenke der Anpassung sind auf 1–16 mm an SAM gepasst und bleiben nah.
    ARM = (('upperarm', 40.0, ('rotation/x', 'rotation/y', 'rotation/z')),
           ('forearm', 60.0, ('rotation/x', 'rotation/y', 'rotation/z')),
           ('hand', 40.0, ('rotation/x', 'rotation/y', 'rotation/z')))
    FINGER_TEILE = ('thumb', 'index', 'mid', 'ring', 'pinky')

    def _parameter(self):
        liste = super()._parameter()
        for glied, grenze, kanaele in self.ARM:
            for kanal in kanaele:
                liste.append({'knochen': '%s_%s' % (self.seite, glied), 'kanal': kanal, 'unten': -grenze, 'oben': grenze, 'griff': 0.0})
        return liste

    def arm_winkel(self, phi):
        """`{knochen: {kanal: Grad}}` — nur die Armwinkel von `phi` (Zuwachs gegen die Haltung), ohne die kleinen unter 0,5°."""
        aus = {}
        for (knochen, kanal), w in zip(self.schluessel, phi[:self.n], strict=True):
            if not any(f in knochen for f in self.FINGER_TEILE) and abs(w) >= 0.5:
                aus.setdefault(knochen, {})[kanal] = round(float(w), 2)
        return aus

    def ohne_finger(self):
        """Die beste Lage der GESTRECKTEN Hand (Armwinkel und Größe frei, Finger bei 0) — der Maßstab, den die Finger schlagen müssen: `{kennzahlen, phi}`."""
        from scipy.optimize import least_squares

        frei = np.array([not any(f in k for f in self.FINGER_TEILE) for k, _ in self.schluessel] + [True])
        start = np.zeros(self.anzahl)

        def reste(u):
            phi = start.copy()
            phi[frei] = u * 10.0
            return self.reste(phi)

        erg = least_squares(reste, np.zeros(int(frei.sum())), bounds=(self.unten[frei] / 10.0, self.oben[frei] / 10.0), loss='soft_l1', f_scale=0.008, diff_step=0.1, max_nfev=30)
        phi = start.copy()
        phi[frei] = erg.x * 10.0
        return {'kennzahlen': self.kennzahlen(phi), 'phi': phi}
