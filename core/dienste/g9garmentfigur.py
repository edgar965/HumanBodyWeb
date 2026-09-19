# -*- coding: utf-8 -*-
u"""G9garmentfigur — die Genesis-9-Figur so, wie GarmentCode einen Koerper braucht.

WARUM (Edgar, 19.09.2026: „garment Code Assets funktioniert nicht auf Genesis,
kann man das evtl. anpassen?"): Der GarmentCode-Weg ist figurunabhaengig —
Koerpernetz plus Segmentierung aus den Knochengewichten, Masse am Netz,
Schnitt, Drapierung, Nacharbeit, Bindung an die Haut —, kannte aber nur
HumanBody (`Charakterdaten`) und die SMPL-Referenzkoerper. Eine Genesis-Figur
schickte weder Bauart noch Morphs: gemessen und drapiert wurde der HumanBody-
Grundkoerper, das Rig trug DEF-Namen, im Browser traf kein Knochen — ein
starres Netz in falscher Groesse neben der Figur.

Hier steht alles, was `Assets/GarmentCode/genesis9drapierung.py` von der Figur
braucht, ueber die `webbruecke` geholt (die Kleidung bleibt drueben):

    punkte / dreiecke   Kaefig-Browsernetz (Stufe 0, 27.087 Punkte), Y oben,
                        Fuesse auf dem Boden — die Reglerstellung der Figur
    sichtbar            dasselbe auf der Ansichtsstufe 1 (104.480 Punkte): gegen
                        DIESE Flaeche wird der Stoff nachgearbeitet, sonst
                        schiene die Haut durch (Befund 08.09.2026 bei HumanBody)
    haut                `{knochen, index, gewicht}` — Daz-Knochennamen; damit
                        bindet der Browser das Stueck an das Genesis-Skelett
    segmente            die sechs GarmentCode-Teile aus dem staerksten Knochen
                        je Punkt (`l_upperarm` … -> left_arm, `l_thigh` … ->
                        left_leg); `Mouth Cavity` -> face_internal, sonst body.
                        Das Schluesselbein (`l_shoulder`) bleibt Rumpf — wie bei
                        HumanBody (`Segmentierung.ARM` ohne `shoulder`)
    geschlecht          aus den Reglern Feminine/Masculine — waehlt die Vorlage
                        der Masse (mean_female/mean_male)
    schulterneigung     Winkel des Schluesselbeins ueber der Waagrechten, aus
                        der Kette der Stellung (Basis 9,2 Grad)

`projekt()` dreht in Projektkoordinaten (m, Z oben), in denen Ablage,
Nacharbeit und `Anziehen` rechnen — wie `_smpl_traeger` in `drapierdienst.py`.
"""
import math

import numpy as np

from Genesis9.basisnetz import G9basisnetz
from Genesis9.formung import G9formung

__all__ = ['G9garmentfigur']


class G9garmentfigur:
    u"""Netz, Haut, Segmente und Masse-Vorgaben einer Genesis-9-Stellung."""

    #: Stamm eines Daz-Knochens (ohne `l_`/`r_`), der zum ARM gehoert.
    ARM = ('upperarm', 'upperarmtwist1', 'upperarmtwist2', 'forearm', 'forearmtwist1',
           'forearmtwist2', 'hand', 'hand_anchor', 'thumb1', 'thumb2', 'thumb3',
           'index1', 'index2', 'index3', 'indexmetacarpal', 'mid1', 'mid2', 'mid3',
           'midmetacarpal', 'ring1', 'ring2', 'ring3', 'ringmetacarpal', 'pinky1',
           'pinky2', 'pinky3', 'pinkymetacarpal')
    #: … der zum BEIN gehoert.
    BEIN = ('thigh', 'thightwist1', 'thightwist2', 'shin', 'foot', 'metatarsal', 'toes',
            'bigtoe1', 'bigtoe2', 'indextoe1', 'indextoe2', 'midtoe1', 'midtoe2',
            'ringtoe1', 'ringtoe2', 'pinkytoe1', 'pinkytoe2')
    #: Materialgruppen, die keine Haut sind und nicht kollidieren duerfen.
    INNEN = ('Mouth Cavity',)
    SEGMENTE = ('body', 'left_arm', 'left_leg', 'right_arm', 'right_leg', 'face_internal')
    FEMININ = 'BaseFeminine_figure_ctrl_Character'
    MASKULIN = 'BaseMasculine_figure_ctrl_Character'
    #: Die Stufe, die der Browser zeigt (`G9unterteilung.ANSICHT`).
    SICHTBAR = 1

    def __init__(self, regler):
        self.regler = {str(k): v for k, v in (regler or {}).items()}
        self.formung = G9formung.aus_abfrage(dict(self.regler), {})
        self._roh = None

    # ---------------------------------------------------------------- Netz

    def fingerabdruck(self):
        return self.formung.fingerabdruck()

    def roh(self):
        u"""Die Kaefigpunkte der Stellung, Fuesse auf dem Boden (Y oben)."""
        if self._roh is None:
            self._roh = self.formung.punkte() - np.array([0.0, self.formung.boden(), 0.0])
        return self._roh

    def stufe(self, stufen=0):
        return G9basisnetz.holen().netzstufe(stufen)

    def punkte(self):
        return np.asarray(self.stufe(0).punkte(self.roh()), dtype=np.float64)

    def dreiecke(self):
        return np.asarray(self.stufe(0).dreiecke, dtype=np.int64)

    def sichtbar(self):
        u"""(Punkte, Dreiecke) der Ansichtsstufe — die Flaeche, die man sieht."""
        stufe = self.stufe(self.SICHTBAR)
        return (np.asarray(stufe.punkte(self.roh()), dtype=np.float64),
                np.asarray(stufe.dreiecke, dtype=np.int64))

    def haut(self):
        u"""`{knochen, index (N, 4), gewicht (N, 4)}` der Kaefig-Browserpunkte."""
        return self.stufe(0).haut

    @staticmethod
    def projekt(punkte):
        u"""Three (m, Y oben) -> Projekt (m, Z oben)."""
        a = np.asarray(punkte, dtype=np.float64)
        return np.column_stack([a[:, 0], -a[:, 2], a[:, 1]])

    # ------------------------------------------------------------ Segmente

    def segmente(self):
        u"""`{body, left_arm, left_leg, right_arm, right_leg, face_internal}` — Listen
        von Punktnummern, jeder Punkt genau einmal."""
        haut = self.haut()
        teile = [self.knochenteil(name) for name in haut['knochen']]
        index = np.asarray(haut['index'], dtype=np.int64)
        gewicht = np.asarray(haut['gewicht'], dtype=np.float64)
        staerkster = index[np.arange(len(index)), gewicht.argmax(axis=1)]
        nummer = {name: n for n, name in enumerate(self.SEGMENTE)}
        zuordnung = np.array([nummer[teile[k] or 'body'] for k in staerkster], dtype=np.int8)
        zuordnung[gewicht.max(axis=1) <= 0] = 0
        stufe = self.stufe(0)
        ecken = np.asarray(stufe.dreiecke, dtype=np.int64).ravel()
        for gruppe in stufe.gruppen:
            if gruppe.get('name') in self.INNEN:
                ab, anzahl = int(gruppe['index_ab']), int(gruppe['index_anzahl'])
                zuordnung[np.unique(ecken[ab:ab + anzahl])] = nummer['face_internal']
        return {name: np.where(zuordnung == n)[0].tolist() for name, n in nummer.items()}

    @classmethod
    def knochenteil(cls, name):
        u"""'l_forearm' -> 'left_arm', 'r_toes' -> 'right_leg', sonst None (Rumpf)."""
        if len(name) < 3 or name[1] != '_' or name[0] not in 'lr':
            return None
        stamm = name[2:]
        if stamm in cls.ARM:
            art = 'arm'
        elif stamm in cls.BEIN:
            art = 'leg'
        else:
            return None
        return ('left_' if name[0] == 'l' else 'right_') + art

    # ----------------------------------------------------- Masse-Vorgaben

    def geschlecht(self):
        u"""'male', wenn der Masculine-Regler den Feminine-Regler uebersteigt."""
        def wert(name):
            try:
                return float(self.regler.get(name) or 0.0)
            except (TypeError, ValueError):
                return 0.0
        return 'male' if wert(self.MASKULIN) > wert(self.FEMININ) else 'female'

    def schulterneigung(self):
        u"""Grad des linken Schluesselbeins ueber der Waagrechten — oder None."""
        try:
            knochen = self.formung.skelett().bauen()['knochen']
            schulter = next(k for k in knochen if k['name'] == 'l_shoulder')
            kopf, schwanz = np.asarray(schulter['kopf']), np.asarray(schulter['schwanz'])
        except (KeyError, StopIteration, TypeError, ValueError):
            return None
        weg = schwanz - kopf
        quer = math.hypot(weg[0], weg[2])
        if quer < 1e-9:
            return None
        return float(math.degrees(math.atan2(weg[1], quer)))
