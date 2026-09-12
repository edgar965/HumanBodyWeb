# -*- coding: utf-8 -*-
u"""Vorbildbild — das Icon eines eigenen Vorbilds der Kleiderbibliothek.

Edgar (11.09.2026): „mach fuer leggins eine Voreinstellung fuer
kleiderbibliothek, mit Icon". Die Bibliotheksstuecke bringen ihr Bild als
`.thumb` mit (256x256 RGBA); ein eigenes Vorbild (`eigenevorbilder.py`) hat
keins. Dieses Werkzeug rendert es: die Figur mit dem Stueck aus einer
`*_rig.json`, Kamera auf das Stueck, Hintergrund durchsichtig — wie die
Icons der Bibliothek.

    python werkzeug/vorbildbild.py <rig.json> <ziel.png> [--modell NAME]
                                   [--farbe #202020] [--groesse 256]
"""
import argparse
import json
import os
import sys

import django
import numpy as np

sys.path.insert(0, r'A:\3DTools\HumanBodyWeb')
sys.path.insert(0, r'A:\3DTools\HumanBody')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ui.settings')
django.setup()

from django.conf import settings                             # noqa: E402

from GarmentCode.dienst import GarmentcodeDienst             # noqa: E402
from GarmentCode.drapierdienst import Garmentdrapierung      # noqa: E402
from GarmentCode.webbruecke import charakterdaten            # noqa: E402


class Vorbildbild:
    u"""Rendert Figur + Stueck als quadratisches Icon mit Alphakanal."""

    #: Projektlage (z oben) -> Renderlage (y oben), wie `Filmrender.DREHUNG`.
    DREHUNG = np.array([[1.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, -1.0, 0.0]])
    HAUT = (0.87, 0.72, 0.62)

    def __init__(self, modell, geschlecht='female'):
        pfad = os.path.join(str(settings.HUMANBODY_MODELS_DIR), modell + '.json')
        with open(pfad, encoding='utf-8') as datei:
            morphs = json.load(datei).get('morphs') or {}
        figur = np.asarray(GarmentcodeDienst.figurnetz(geschlecht, morphs, None))
        netz = charakterdaten().netzdaten(geschlecht)
        self.koerper, self.flaechen = Garmentdrapierung.sichtbares_netz(
            figur, geschlecht, netz)
        self.koerper = np.asarray(self.koerper, dtype=np.float64)

    def rendern(self, rig, ziel, farbe=(0.13, 0.13, 0.13), groesse=256):
        import trimesh
        import pyrender
        from PIL import Image
        with open(rig, encoding='utf-8') as datei:
            daten = json.load(datei)
        stoff = np.asarray(daten['punkte'], dtype=np.float64)
        dreiecke = np.asarray(daten['dreiecke'])
        d = self.DREHUNG
        szene = pyrender.Scene(bg_color=[0, 0, 0, 0], ambient_light=[0.45, 0.45, 0.47])
        haut = pyrender.MetallicRoughnessMaterial(
            baseColorFactor=list(self.HAUT) + [1.0], metallicFactor=0.0,
            roughnessFactor=0.8)
        stoffwerk = pyrender.MetallicRoughnessMaterial(
            baseColorFactor=list(farbe) + [1.0], metallicFactor=0.0,
            roughnessFactor=0.7, doubleSided=True)
        koerpernetz = trimesh.Trimesh(self.koerper @ d.T, np.asarray(self.flaechen),
                                      process=False)
        szene.add(pyrender.Mesh.from_trimesh(koerpernetz, smooth=True, material=haut))
        # Koerpernormalen der Rig-Datei (Leggings, 11.09.2026) — wie der Browser.
        stoffnetz = trimesh.Trimesh(stoff @ d.T, dreiecke, process=False)
        if daten.get('normalen'):
            normalen = np.asarray(daten['normalen'], dtype=np.float64)
            stoffnetz.vertex_normals = normalen @ d.T
        szene.add(pyrender.Mesh.from_trimesh(stoffnetz, smooth=True,
                                             material=stoffwerk))
        # Kamera: von schraeg vorn auf die Mitte des Stuecks, so nah, dass
        # das Stueck das Bild fuellt (yfov 30 Grad, Rand 15 %).
        s = stoff @ d.T
        mitte = (s.min(axis=0) + s.max(axis=0)) / 2
        hoehe = float(s[:, 1].max() - s[:, 1].min())
        abstand = 1.15 * hoehe / (2 * np.tan(np.deg2rad(15)))
        richtung = np.array([0.35, 0.12, 1.0])
        richtung /= np.linalg.norm(richtung)
        lage = np.eye(4)
        lage[:3, 3] = mitte + abstand * richtung
        lage[:3, :3] = self._blick(lage[:3, 3], mitte)
        szene.add(pyrender.PerspectiveCamera(yfov=np.deg2rad(30.0)), pose=lage)
        licht = np.eye(4)
        licht[:3, 3] = mitte + abstand * np.array([0.6, 0.9, 0.8])
        licht[:3, :3] = self._blick(licht[:3, 3], mitte)
        szene.add(pyrender.DirectionalLight(color=np.ones(3), intensity=3.2),
                  pose=licht)
        werk = pyrender.OffscreenRenderer(groesse, groesse)
        try:
            bild, _ = werk.render(szene, flags=pyrender.RenderFlags.RGBA)
        finally:
            werk.delete()
        Image.fromarray(np.asarray(bild, dtype=np.uint8), 'RGBA').save(ziel)
        return ziel

    @staticmethod
    def _blick(lage, ziel):
        z = lage - ziel
        z /= np.linalg.norm(z)
        x = np.cross([0.0, 1.0, 0.0], z)
        x /= np.linalg.norm(x)
        y = np.cross(z, x)
        return np.column_stack([x, y, z])


def main():
    p = argparse.ArgumentParser()
    p.add_argument('rig')
    p.add_argument('ziel')
    p.add_argument('--modell', default='FemaleWithHair')
    p.add_argument('--farbe', default='#202020')
    p.add_argument('--groesse', type=int, default=256)
    a = p.parse_args()
    farbe = tuple(int(a.farbe.lstrip('#')[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    ziel = Vorbildbild(a.modell).rendern(a.rig, a.ziel, farbe, a.groesse)
    print('geschrieben:', ziel)


if __name__ == '__main__':
    main()
