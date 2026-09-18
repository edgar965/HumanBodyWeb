# -*- coding: utf-8 -*-
"""Mimikvorschau — ein Kopfbild je Pose für den Dialog „Pose setzen".

Rendert das HumanBody-Netz mit den MB-Lab-Verschiebungen der Pose (exakt,
nicht über Knochen) von vorn auf den Kopf, 160 × 160 px, mit pyrender im
Prozess des Commands (`manage.py mimik_vorbereiten --vorschau`). Die Bilder
liegen als `static/mimik/vorschau/<pose>.png` und sind versioniert.
"""

import os

import numpy as np


class Mimikvorschau:
    GROESSE = 160
    HAUT = (0.86, 0.68, 0.58, 1.0)
    #: Kopfhöhe (Blender-z) und Abstand der Kamera vor dem Gesicht.
    KOPF_Z = 1.56
    ABSTAND = 0.42

    def __init__(self, ausdruecke, datenordner, zielordner):
        self.ausdruecke = ausdruecke
        self.netz = np.load(os.path.join(datenordner, 'vertices_tpose.npy')).astype(float)
        self.flaechen = np.load(os.path.join(datenordner, 'faces.npy'))
        self.ziel = str(zielordner)
        self.einheiten = ausdruecke.einheiten()

    def alle(self, posen):
        os.makedirs(self.ziel, exist_ok=True)
        renderer = self._renderer()
        anzahl = 0
        for pose in posen:
            bild = self._rendern(renderer, self.verschoben(pose['gewichte']))
            self._speichern(bild, os.path.join(self.ziel, pose['id'] + '.png'))
            anzahl += 1
        renderer.delete()
        return anzahl

    def verschoben(self, gewichte):
        """Das Netz mit den Verschiebungen der Pose (Blender-Achsen)."""
        punkte = self.netz.copy()
        for einheit, g in gewichte.items():
            eintrag = self.einheiten.get(einheit)
            if not eintrag or not g:
                continue
            for idx, dx, dy, dz in eintrag['plus'] if g > 0 else eintrag['minus']:
                punkte[int(idx)] += abs(g) * np.array([dx, dy, dz])
        return punkte

    def _renderer(self):
        import pyrender

        return pyrender.OffscreenRenderer(self.GROESSE, self.GROESSE)

    def _rendern(self, renderer, punkte):
        import pyrender
        import trimesh

        # Blender (z hoch, y nach hinten) → Kamera schaut entlang −z: y hoch, −y vorn.
        three = np.column_stack([punkte[:, 0], punkte[:, 2], -punkte[:, 1]])
        netz = trimesh.Trimesh(three, self.flaechen, process=False)
        material = pyrender.MetallicRoughnessMaterial(
            baseColorFactor=self.HAUT, metallicFactor=0.0, roughnessFactor=0.7
        )
        szene = pyrender.Scene(bg_color=(0.10, 0.10, 0.18, 1.0), ambient_light=(0.35, 0.35, 0.35))
        szene.add(pyrender.Mesh.from_trimesh(netz, material=material, smooth=True))
        kamera = pyrender.PerspectiveCamera(yfov=np.radians(28))
        lage = np.eye(4)
        lage[:3, 3] = [0.0, self.KOPF_Z, self.ABSTAND]
        szene.add(kamera, pose=lage)
        licht = np.eye(4)
        licht[:3, 3] = [0.3, self.KOPF_Z + 0.4, self.ABSTAND + 0.3]
        szene.add(pyrender.PointLight(color=np.ones(3), intensity=1.2), pose=licht)
        farbe, _tiefe = renderer.render(szene)
        return farbe

    @staticmethod
    def _speichern(bild, pfad):
        from PIL import Image

        Image.fromarray(bild).save(pfad)
