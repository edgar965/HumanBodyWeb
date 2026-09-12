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

DIE AUSDRÜCKE SIND DELTAS, DER PLAYER WILL LAGEN (Befund Edgar, 12.09.2026,
„das Gesicht ist zermatscht"): `blendshapes_to_bone_tracks` liefert je
Knochen eine kleine Drehung RELATIV zur Ruhelage — so hat sie
`photo_to_3d/facial_expression.js` immer benutzt (`ruhe.multiply(drehung)`).
Der Retarget-Player setzt eine Spur aber ABSOLUT auf `bone.quaternion`
(`QuaternionKeyframeTrack`), wie die Körper- und Fingerspuren des Motors.
Gemessen am ersten SMPL-X-Lauf: DEF-jaw Ruhelage 89°, Spur 2°; DEF-lip.T.L
Ruhelage 175°, Spur 1° — jeder Gesichtsknochen sprang auf die Einheitslage.
Deshalb legt `auf_ruhelage` vor dem Mischen die Ruhelage des DEF-Skeletts
unter jede Spur: `q = ruhe · delta`, dieselbe Reihenfolge wie im JS.
"""
import json
import os

import numpy as np


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

    @staticmethod
    def auf_ruhelage(spuren, geometrie):
        u"""Aus Deltas absolute Lagen: je Knochen und Bild `ruhe · delta`.

        `geometrie` ist das Zielskelett (`SkeletonGeometry`); ein Knochen,
        den es dort nicht gibt, bleibt, wie er ist — der Mischer lässt ihn
        ohnehin fallen. Ändert `spuren` an Ort und Stelle und gibt sie zurück.
        """
        from humanbody_core.quaternion import Quat
        for name, werte in spuren.tracks.items():
            knochen = geometrie.bones.get(name)
            if knochen is None:
                continue
            deltas = np.asarray(werte, dtype=float).reshape(-1, 4)
            lagen = Quat.mul_reihe(knochen.rest_local_quat, deltas)
            spuren.tracks[name] = lagen.reshape(-1).tolist()
        return spuren

    @classmethod
    def mischen(cls, gemischt, ausdruecke, geometrie=None):
        u"""`gemischt` (Körper + v4 [+ Finger]) mit den Gesichtsknochen aus
        `ausdruecke` — beides `Bewegungsspuren`. Die Ausdrücke sind Deltas
        und werden hier auf die Ruhelage des DEF-Skeletts gelegt (`geometrie`,
        sonst `Skelettgeometrie.holen()`)."""
        if ausdruecke is None or ausdruecke.frame_count == 0:
            return gemischt
        from humanbody_core.skeleton.retarget.zusammenfuegen import merge_retargeted
        if geometrie is None:
            from .skelettgeometrie import Skelettgeometrie
            geometrie = Skelettgeometrie.holen()
        lagen = cls.auf_ruhelage(ausdruecke, geometrie)
        knochen = {name.replace('.', '_') for name in lagen.tracks}
        return merge_retargeted(gemischt, lagen, face_hand_bones=knochen,
                                filter_noisy_face=False)
