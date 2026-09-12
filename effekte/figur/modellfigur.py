# -*- coding: utf-8 -*-
u"""Modellfigur — ein gespeichertes Modell der Szene als Stueckliste des Films.

Ein Modell (`HumanBody/data/models/<name>.json`, geschrieben von der
Szene-Seite) nennt Koerpertyp und Morphs, seine GarmentCode-Stuecke ueber
ihre Rig-Adresse (`/api/garmentcode/datei/<ordner>/<name>_rig.json/`) und
die Frisur ueber ihre GLB-Adresse (`/api/character/hairstyle/<name>/`).
Der Film (`hbfilm.py`) will davon: die Morphs als Parameter, je Stueck
einen Dateipfad und eine Farbe.

DIE FRISUR IST EIN STUECK OHNE VERFORMUNG: Im Browser haengen alle ihre
Punkte am Kopfknochen (`skinifyHairGroup`, `Hautgewichte.anEinenKnochen`).
Hier wird die GLB gelesen und als `.npz` im Format der Szenenstuecke
(`figurvideostuecke.py`) neben die Ausgabe gelegt — alle Gewichte auf
`DEF-spine.006`. Die GLB liegt in der Lage des Browsers (y oben); der
Film rechnet in Blender-Lage (z oben): `(x, y, z) -> (x, -z, y)`, dieselbe
Umsetzung wie `Figurvideostuecke._schreiben`. Belegt ueber die Sitzprobe
des Films (Abstand Frisur zu Haut, Millimeter) — in der falschen Lage
staende das Haar einen Meter neben dem Kopf.
"""
import json
import os

import numpy as np

__all__ = ['Modellfigur']


class Modellfigur:

    KOPFKNOCHEN = 'DEF-spine.006'
    VORGABE_KOERPER = 'Female_Caucasian'
    VORGABE_STOFF = (0.3, 0.45, 0.7)
    VORGABE_HAAR = (0.02, 0.02, 0.02)
    ENDUNG_RIG = '_rig.json'

    def __init__(self, pfad):
        self.pfad = pfad
        with open(pfad, encoding='utf-8') as datei:
            self.daten = json.load(datei)
        self.name = self.daten.get('name') or os.path.splitext(
            os.path.basename(pfad))[0]

    # --------------------------------------------------------------- Figur

    def koerpertyp(self):
        return self.daten.get('body_type') or self.VORGABE_KOERPER

    def morphs(self):
        return {str(k): float(v) for k, v in (self.daten.get('morphs') or {}).items()}

    def geschlecht(self):
        return 'female' if self.koerpertyp().lower().startswith('female') else 'male'

    # ------------------------------------------------------------- Stuecke

    def stuecke(self, ablage):
        u"""[{name, pfad, farbe}] fuer `Hbfilm(stuecke=…)`; `ablage` ist der
        Ordner, in den die Frisur als `.npz` geschrieben wird."""
        liste = [self._garmentcode(eintrag)
                 for eintrag in (self.daten.get('garmentcode') or [])]
        liste = [s for s in liste if s]
        haar = self.frisur(ablage)
        if haar:
            liste.append(haar)
        return liste

    def _garmentcode(self, eintrag):
        from GarmentCode.entwurf import Entwurf
        rig = eintrag.get('rig_url') or ''
        teile = [t for t in rig.split('/') if t]
        if len(teile) < 2 or not teile[-1].endswith(self.ENDUNG_RIG):
            return None
        wurzel = os.path.abspath(Entwurf.AUSGABE)
        pfad = os.path.abspath(os.path.join(wurzel, teile[-2], teile[-1]))
        if not pfad.startswith(wurzel + os.sep) or not os.path.isfile(pfad):
            raise ValueError(u'Stueck %s: Rig-Datei fehlt (%s)'
                             % (eintrag.get('stueck'), pfad))
        material = eintrag.get('material') or {}
        return {'name': eintrag.get('stueck') or teile[-1],
                'pfad': pfad,
                'farbe': self.farbe(material.get('farbe'), self.VORGABE_STOFF)}

    @staticmethod
    def farbe(hexwert, vorgabe):
        u"""`#b42727` -> (0.706, 0.153, 0.153); sonst die Vorgabe."""
        text = (hexwert or '').strip().lstrip('#')
        if len(text) != 6:
            return tuple(vorgabe)
        try:
            return tuple(int(text[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
        except ValueError:
            return tuple(vorgabe)

    # -------------------------------------------------------------- Frisur

    def frisur(self, ablage):
        from django.conf import settings
        from core.api.modelldateien import Modelldateien
        frisur = self.daten.get('hair_style') or {}
        adresse = frisur.get('url') or ''
        teile = [t for t in adresse.split('/') if t]
        if not teile:
            return None
        ordner = os.path.join(str(settings.HUMANBODY_DATA_DIR), 'hairstyles')
        glb = os.path.join(ordner, '%s.glb' % teile[-1])
        if not os.path.isfile(glb):
            raise ValueError(u'Frisur fehlt: %s' % glb)
        farbe = (Modelldateien.HAARFARBEN.get(frisur.get('color') or '') or {}
                 ).get('viewport') or self.VORGABE_HAAR
        pfad = os.path.join(ablage, 'frisur_%s.npz' % teile[-1])
        self.frisur_schreiben(glb, pfad)
        return {'name': u'Frisur %s' % (frisur.get('name') or teile[-1]),
                'pfad': pfad, 'farbe': tuple(farbe)}

    @classmethod
    def frisur_schreiben(cls, glb, pfad):
        u"""GLB -> Szenenstueck-`.npz`, alle Punkte am Kopfknochen."""
        import trimesh
        szene = trimesh.load(glb, force='scene')
        netz = szene.to_geometry() if hasattr(szene, 'to_geometry') \
            else szene.dump(concatenate=True)
        punkte = np.asarray(netz.vertices, dtype=np.float64)
        blender = np.column_stack([punkte[:, 0], -punkte[:, 2], punkte[:, 1]])
        n = len(blender)
        gewichte = np.zeros((n, 4), dtype=np.float64)
        gewichte[:, 0] = 1.0
        np.savez(pfad, punkte=blender,
                 dreiecke=np.asarray(netz.faces, dtype=np.int64),
                 skin_index=np.zeros((n, 4), dtype=np.int32),
                 skin_weight=gewichte,
                 knochen=np.array([cls.KOPFKNOCHEN]))
        return n

    # ------------------------------------------------------------ Bericht

    def beschreibung(self):
        return {'name': self.name, 'koerpertyp': self.koerpertyp(),
                'morphs': len(self.morphs()),
                'stuecke': [e.get('stueck') for e in (self.daten.get('garmentcode') or [])],
                'frisur': (self.daten.get('hair_style') or {}).get('name') or ''}
