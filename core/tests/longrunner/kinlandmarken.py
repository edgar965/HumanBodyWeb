# -*- coding: utf-8 -*-
u"""Kinlandmarken — Höhen am Kin-Körper (Genesis 9, Fixture `gemeinsam_kin`),
gegen die die GarmentCode-Versprechen gemessen werden.

Alles in Metern über dem Boden, am Netz selbst gemessen — nicht aus den
Maßen, die GarmentCode bekommt (die sind der Prüfling, siehe
`Docu/konzepte/2026-09-20_garmentcode-genesis9-konzept.md`):

    schritt   topologisch (`Stoffhochziehen`/`Roehrenschnitt`, 20.09.2026: 0,845)
    knie      Oberkante der Punkte, die am Schienbein hängen (`l_shin`)
    knoechel  Oberkante der Punkte, die am Fuß hängen (`l_foot`)
    taille    GarmentCodes `_waist_level` = height − head_l − waist_line
    brust     GarmentCodes Brustlinie (2/3 vert_bust_line + 1/3 bust_line)
"""

import json

import numpy as np
from django.conf import settings

FIXTURE = settings.ASSETS_ROOT / 'GarmentCode' / 'test' / 'gemeinsam_kin'


class Kinlandmarken:
    u"""Einmal je Testklasse gerechnet (`setUpClass`)."""

    _stand = None

    @classmethod
    def regler(cls):
        return json.load(open(FIXTURE / 'figur_regler.json', encoding='utf-8'))['regler']

    @classmethod
    def holen(cls):
        if cls._stand is None:
            cls._stand = cls._messen()
        return cls._stand

    @classmethod
    def _messen(cls):
        from GarmentCode.genesis9drapierung import Genesis9drapierung
        from GarmentCode.stoffhochziehen import Stoffhochziehen

        regler = cls.regler()
        figur = Genesis9drapierung.figur(regler)
        punkte = np.asarray(figur.punkte(), dtype=np.float64)        # Y oben, Meter
        haut = figur.haut()
        namen = np.array(haut['knochen'])
        index = np.asarray(haut['index'], dtype=np.int64)
        gewicht = np.asarray(haut['gewicht'], dtype=np.float64)
        staerkster = namen[index[np.arange(len(index)), gewicht.argmax(axis=1)]]

        def oberkante(knochen):
            y = punkte[staerkster == knochen][:, 1]
            return float(y.max()) if len(y) else None

        sichtbar, dreiecke = figur.sichtbar()
        hoch = Stoffhochziehen(figur.projekt(sichtbar), np.asarray(dreiecke))
        schritt_z = float(hoch.schritt[1])          # (x, z) — Stoffhochziehen._schritt

        masse, _ = Genesis9drapierung.masse(regler, figur)
        cm = 100.0
        taille = (masse['height'] - masse['head_l'] - masse['waist_line']) / cm
        schulter = (masse['height'] - masse['head_l']) / cm
        brustlinie = ((2.0 / 3.0) * masse.get('vert_bust_line', masse['bust_line'])
                      + (1.0 / 3.0) * masse['bust_line']) / cm
        return {
            'schritt': schritt_z,
            'knie': oberkante('l_shin'),
            'knoechel': oberkante('l_foot'),
            'taille': taille,
            'brust': schulter - brustlinie,
            'schulter': schulter,
            'boden': 0.0,
            'hoehe': float(punkte[:, 1].max()),
        }


class Rigmasse:
    u"""Höhen eines drapierten Stücks (Rig-JSON: Punkte in Metern, Z oben)."""

    def __init__(self, punkte):
        self.p = np.asarray(punkte, dtype=np.float64)

    def bund(self):
        return float(self.p[:, 2].max())

    def saum(self, seite=None, band_m=0.015):
        u"""Median der untersten `band_m` — links (x<0), rechts (x>0) oder alle."""
        p = self.p
        if seite == 'links':
            p = p[p[:, 0] < -0.03]
        elif seite == 'rechts':
            p = p[p[:, 0] > 0.03]
        z = p[:, 2]
        return float(np.median(z[z < z.min() + band_m]))

    def mitte_unten(self, breite_m=0.015):
        z = self.p[np.abs(self.p[:, 0]) < breite_m][:, 2]
        return float(z.min()) if len(z) else None

    def seite_unten(self, ab_m=0.12):
        z = self.p[np.abs(self.p[:, 0]) > ab_m][:, 2]
        return float(z.min()) if len(z) else None

    def streifen_unten(self, von_m, bis_m):
        u"""Tiefster Punkt im Streifen `von_m` <= |x| < `bis_m` (beide Seiten)."""
        x = np.abs(self.p[:, 0])
        z = self.p[(x >= von_m) & (x < bis_m)][:, 2]
        return float(z.min()) if len(z) else None
