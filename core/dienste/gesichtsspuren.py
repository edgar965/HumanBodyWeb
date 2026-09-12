# -*- coding: utf-8 -*-
u"""Gesichtsspuren — die SMPLest-X-Ausdrücke eines Hybrid-Auftrags aufs Rig.

DER HYBRID HATTE SEIT DEM 05.04.2026 KEIN GESICHT (Befund 12.09.2026, Edgar:
„ich sehe aber keine gesichter?"). `Hybridlauf._gesichtsausdruecke` schreibt
seit dem 05.04. `<gesicht>_blendshapes.json` neben die v4-BVH — und am selben
Tag nahm Commit a6c1c07 der Zusammenführung das Lesen dieser Datei weg
(„filter ALL noisy v4 face bones → neutral face"); der angekündigte Ersatz
kam nie. Dazu lagen die SMPL-X-Modelle seit dem 08.05. im Archiv, sodass die
Datei ohnehin nicht entstand. Jeder Hybrid seither: starres Gesicht.

Hier wird sie wieder gelesen: `Gesichtsformen.blendshapes_to_bone_tracks`
macht aus den zehn Ausdruckswerten je Bild 36 Gesichtsknochen-Spuren und
setzt den gemessenen Kiefer ein (`Kieferspuren`); der Mischer legt sie über
das Gemisch — nur die Knochen, die die Ausdrücke wirklich stellen, und ohne
den Gesichtsfilter, der hier die falsche Quelle träfe. Fehlt die Datei,
bleibt das Gesicht, wie es war (neutral).
"""
import json
import os


class Gesichtsspuren:

    #: So heißt die Datei neben der Gesichts-BVH (`Hybridlauf`).
    ENDUNG = '_blendshapes.json'

    @classmethod
    def datei(cls, gesicht_bvh):
        return gesicht_bvh.rsplit('.', 1)[0] + cls.ENDUNG

    @classmethod
    def laden(cls, gesicht_bvh):
        u"""`Bewegungsspuren` der Ausdrücke oder `None`, wenn keine Datei da ist."""
        pfad = cls.datei(gesicht_bvh)
        if not os.path.isfile(pfad):
            return None
        from humanbody_core.skeleton.face_blendshapes import Gesichtsformen
        with open(pfad, encoding='utf-8') as datei:
            daten = json.load(datei)
        return Gesichtsformen.blendshapes_to_bone_tracks(daten)

    @classmethod
    def mischen(cls, gemischt, ausdruecke):
        u"""`gemischt` (Körper + v4 [+ Finger]) mit den Gesichtsknochen aus
        `ausdruecke` — beides `Bewegungsspuren`."""
        if ausdruecke is None or ausdruecke.frame_count == 0:
            return gemischt
        from humanbody_core.skeleton.retarget.zusammenfuegen import merge_retargeted
        knochen = {name.replace('.', '_') for name in ausdruecke.tracks}
        return merge_retargeted(gemischt, ausdruecke, face_hand_bones=knochen,
                                filter_noisy_face=False)
