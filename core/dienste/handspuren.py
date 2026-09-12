# -*- coding: utf-8 -*-
u"""Handspuren — die Fingerknochen einer dritten Quelle über das Gemisch legen.

Der Hybrid mischt auf dem Rig: Körperspur (GVHMR/PromptHMR/GEM) plus die
56 `FACE_HAND_BONES` aus der v4-Spur (`Spurenmischer`). Seit dem 12.09.2026
kann eine DRITTE Spur die Finger stellen (GEM-X, `BVHJob.bvh_file_hands`):
Derselbe Mischer, nur mit den 38 Hand-Knochen als Menge — Finger, Daumen,
Mittelhand — und ohne den Gesichtsfilter, der hier nichts zu filtern hat.

Die Gesichtsknochen der v4-Spur bleiben, was sie waren; nur die Hände werden
ersetzt. Fehlt in der dritten Spur ein Knochen (GEM-X kennt keine
`DEF-palm_*`), bleibt der aus dem Gemisch stehen: Der Mischer WIRFT aus der
ersten Spur alles weg, was zur Menge gehört — deshalb wird die Menge hier auf
das eingeschränkt, was die dritte Spur wirklich mitbringt (gemessen 12.09.2026:
30 Fingerspuren).
"""


class Handspuren:

    #: Anfänge der Knochennamen (Three.js-Schreibweise), die eine Hand ausmachen.
    ANFAENGE = ('DEF-f_', 'DEF-thumb', 'DEF-palm')

    @classmethod
    def knochen(cls):
        from humanbody_core.skeleton.retarget_mappings import FACE_HAND_BONES
        return frozenset(k for k in FACE_HAND_BONES if k.startswith(cls.ANFAENGE))

    @classmethod
    def mischen(cls, gemischt, haende):
        u"""`gemischt` (Körper + v4) mit den Fingern aus `haende` — beides
        `Bewegungsspuren` aus dem Retarget."""
        from humanbody_core.skeleton.retarget.zusammenfuegen import merge_retargeted
        vorhanden = {name.replace('.', '_') for name in haende.tracks}
        return merge_retargeted(gemischt, haende,
                                face_hand_bones=cls.knochen() & vorhanden,
                                filter_noisy_face=False)
