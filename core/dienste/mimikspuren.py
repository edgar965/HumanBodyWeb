# -*- coding: utf-8 -*-
u"""Mimikspuren — die eingerechnete Mimik neben einer BVH, als Gesichtsspuren.

Edgar, 13.09.2026: „meinetwegen kann das auch per Klick zusammengerechnet
werden in dann eine BVH-Datei." Eine Quell-BVH (CMU, Mixamo, SMPL-X …) hat
keine DEF-Gesichtsknochen — das Gesicht entsteht erst im Retarget. Deshalb
liegt die Mimik wie das Video-Gesicht (`_blendshapes.json`, `Gesichtsspuren`)
als Nachbardatei `<stamm>_mimik.json` neben der BVH und wird beim Retarget
auf das DEF-Ergebnis gelegt (`Retargetdaten.holen` → `mischen`). Damit hat
JEDE Seite die Mimik, die diese BVH abspielt.

Die Datei schreibt das Studio (`Mimikeinrechnen` → `save-bvh-effects`):
``{"fps": 30, "einheiten": ["mouthSmile", …], "bilder": [[g, …], …]}`` —
je Quellbild die Gewichte auf den MB-Lab-Einheiten, Lebendigkeit schon drin.
Die Knochendrehungen kommen aus `static/mimik/basis.json` (Drehvektor je
Einheit, `manage.py mimik_vorbereiten`); der Versatz der Lider bleibt beim
Retarget weg — der Player setzt nur Drehungen.
"""
import json
import os

import numpy as np
from django.conf import settings

ENDUNG = '_mimik.json'


class Mimikspuren:

    @staticmethod
    def pfad(bvh_pfad):
        return str(bvh_pfad).rsplit('.', 1)[0] + ENDUNG

    @classmethod
    def schreiben(cls, bvh_pfad, mimik):
        u"""Nachbardatei schreiben; leere Mimik löscht sie."""
        pfad = cls.pfad(bvh_pfad)
        if not mimik or not mimik.get('bilder'):
            if os.path.isfile(pfad):
                os.remove(pfad)
            return pfad
        with open(pfad, 'w', encoding='utf-8') as datei:
            json.dump({'fps': float(mimik.get('fps') or 30.0),
                       'einheiten': list(mimik.get('einheiten') or []),
                       'bilder': mimik['bilder']}, datei, separators=(',', ':'))
        return pfad

    @classmethod
    def laden(cls, bvh_pfad):
        u"""`Bewegungsspuren` (Deltas je Gesichtsknochen) oder None ohne Datei."""
        pfad = cls.pfad(bvh_pfad)
        if not os.path.isfile(pfad):
            return None
        with open(pfad, encoding='utf-8') as datei:
            daten = json.load(datei)
        return cls.spuren(daten, cls.basis())

    @classmethod
    def mischen(cls, ergebnis, bvh_pfad):
        u"""Die Mimik neben `bvh_pfad` auf ein DEF-Ergebnis legen (wie das Video-Gesicht)."""
        spuren = cls.laden(bvh_pfad)
        if spuren is None:
            return ergebnis
        from .gesichtsspuren import Gesichtsspuren
        return Gesichtsspuren.mischen(ergebnis, spuren)

    _basis = None

    @classmethod
    def basis(cls):
        if cls._basis is None:
            pfad = settings.BASE_DIR / 'static' / 'mimik' / 'basis.json'
            with open(pfad, encoding='utf-8') as datei:
                cls._basis = json.load(datei)
        return cls._basis

    @staticmethod
    def spuren(daten, basis):
        u"""Gewichte je Bild → Delta-Quaternionen je Knochen (Three.js [x,y,z,w])."""
        from scipy.spatial.transform import Rotation
        from humanbody_core.skeleton.bewegungsspuren import Bewegungsspuren
        fps = float(daten.get('fps') or 30.0)
        einheiten = daten.get('einheiten') or []
        bilder = np.asarray(daten.get('bilder') or [], dtype=float)
        if bilder.size == 0:
            return Bewegungsspuren.leer()
        anzahl = bilder.shape[0]
        knochen = Mimikspuren._knochen(einheiten, basis)
        drehung = {k: np.zeros((anzahl, 3)) for k in knochen}
        for j, einheit in enumerate(einheiten):
            Mimikspuren._einheit(drehung, basis.get(einheit), bilder[:, j])
        tracks = {k: Rotation.from_rotvec(v).as_quat().reshape(-1).tolist()
                  for k, v in drehung.items()}
        return Bewegungsspuren(
            duration=anzahl / fps, times=[i / fps for i in range(anzahl)],
            tracks=tracks, frame_count=anzahl, mapped_bones=knochen)

    @staticmethod
    def _knochen(einheiten, basis):
        u"""Alle Knochen, die eine der Einheiten bewegt — sortiert."""
        return sorted({k for e in einheiten if e in basis
                       for r in basis[e].values() for k in r})

    @staticmethod
    def _einheit(drehung, eintrag, g):
        u"""Die Drehvektoren EINER Einheit (Gewichte `g` je Bild, positiv →
        `plus`, negativ → `minus`) auf die Knochen addieren."""
        if eintrag is None:
            return
        for richtung, betrag in ((eintrag['plus'], np.clip(g, 0, None)),
                                 (eintrag['minus'], np.clip(-g, 0, None))):
            if not betrag.any():
                continue
            for k, werte in richtung.items():
                drehung[k] += betrag[:, None] * np.asarray(werte[:3], dtype=float)
