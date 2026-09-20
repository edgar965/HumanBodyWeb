# -*- coding: utf-8 -*-
"""Bildmodellgvhmrbild — das SMPL-X-Netz aus GVHMR mit Rig als Standbild (pyrender).

Edgar (20.09.2026): „mach das SMPL ausgabefenster nun auch dauernd sichtbar,
als neue Spalte." Die Tabelle der Proportionen zeigt je Zeile ein Bild wie das
Ausgabefenster: das Netz bläulich, das Rig orange (Gelenke als Kugeln, Knochen
als Striche) — gerendert nach dem Lauf im Arbeitsprozess, wie die Vorher- und
Nachher-Bilder (`G9vorschaubild`, pyrender in python14). Kamera und Licht
erbt es von dort; nur Dreiecke, Normalen und das Rig sind eigene.

Ablage: `ergebnis/gvhmr_<stamm>.png` (der Datei-Endpunkt liefert `ergebnis/`).
"""

import numpy as np
from Genesis9.vorschaubild import G9vorschaubild

__all__ = ['Bildmodellgvhmrbild']


class Bildmodellgvhmrbild(G9vorschaubild):
    FARBE = (0.73, 0.78, 0.86, 1.0)
    GELENK = (1.0, 0.70, 0.28, 1.0)
    KNOCHEN = (1.0, 0.48, 0.11, 1.0)
    KOERPER = 22

    def __init__(self, punkte, dreiecke, gelenke=None, eltern=None):
        super().__init__(punkte)
        self.dreiecke = np.asarray(dreiecke, dtype=np.uint32).reshape(-1, 3)
        self.gelenke = None if gelenke is None else np.asarray(gelenke, dtype=np.float32).reshape(-1, 3)
        self.eltern = list(eltern or [])

    def _dreiecke(self):
        return self.dreiecke

    def _normalen(self):
        import trimesh

        netz = trimesh.Trimesh(self.punkte, self.dreiecke, process=False)
        return np.asarray(netz.vertex_normals, np.float32)

    def _mesh(self, pyrender):
        if self._netz is None:
            material = pyrender.MetallicRoughnessMaterial(
                baseColorFactor=self.FARBE, metallicFactor=0.0, roughnessFactor=0.8
            )
            self._netz = pyrender.Mesh(
                [pyrender.Primitive(positions=self.punkte, normals=self._normalen(), indices=self.dreiecke,
                                    material=material)]
            )
        return self._netz

    # ------------------------------------------------------------------ Rig

    def _rig(self, pyrender, gelenke=None):
        """Kugeln je Gelenk (Körper größer als Finger) und Striche zu den Eltern — `gelenke`
        statt der eigenen, wenn sie schon zur Kamera gerückt sind (`bild_kamera`)."""
        import trimesh

        g = self.gelenke if gelenke is None else gelenke
        if g is None or len(g) < 2:
            return []
        hoehe = max(0.5, float(self.punkte[:, 1].max() - self.punkte[:, 1].min()))
        teile = []
        for radius, auswahl in ((hoehe * 0.012, range(0, min(self.KOERPER, len(g)))),
                                (hoehe * 0.004, range(self.KOERPER, len(g)))):
            auswahl = list(auswahl)
            if not auswahl:
                continue
            kugel = trimesh.creation.icosphere(subdivisions=1, radius=radius)
            posen = np.tile(np.eye(4), (len(auswahl), 1, 1))
            posen[:, :3, 3] = g[auswahl]
            material = pyrender.MetallicRoughnessMaterial(baseColorFactor=self.GELENK, metallicFactor=0.0)
            teile.append(pyrender.Mesh.from_trimesh(kugel, material=material, poses=posen))
        striche = []
        for i, e in enumerate(self.eltern[:len(g)]):
            if 0 <= e < len(g) and i != e:
                striche.append(g[i])
                striche.append(g[e])
        if striche:
            material = pyrender.MetallicRoughnessMaterial(baseColorFactor=self.KNOCHEN, metallicFactor=0.0)
            linien = pyrender.Primitive(positions=np.asarray(striche, np.float32), mode=1, material=material)
            teile.append(pyrender.Mesh([linien]))
        return teile

    def bild(self, ansicht='vorn', breite=600, hoehe=800, ausschnitt=None):
        """Wie `G9vorschaubild.bild`, mit dem Rig VOR dem Netz (Tiefentest bleibt — die Kugeln liegen
        auf den Gelenken in der Figur, darum werden sie leicht nach vorn zur Kamera gerückt)."""
        import pyrender

        grad = self.ANSICHTEN.get(ansicht, float(ansicht) if not isinstance(ansicht, str) else 0.0)
        szene = pyrender.Scene(bg_color=self.hintergrund, ambient_light=(0.35, 0.35, 0.35))
        szene.add(self._mesh(pyrender))
        lage = self._kamera(grad, ausschnitt)
        zur_kamera = lage[:3, 3] - np.array([0.0, float(self.punkte[:, 1].mean()), 0.0])
        zur_kamera = zur_kamera / max(1e-6, np.linalg.norm(zur_kamera))
        versatz = np.eye(4)
        versatz[:3, 3] = zur_kamera * 0.12
        for teil in self._rig(pyrender):
            szene.add(teil, pose=versatz)
        kamera = pyrender.PerspectiveCamera(yfov=np.deg2rad(self.YFOV), aspectRatio=breite / hoehe)
        szene.add(kamera, pose=lage)
        licht = self._blick(lage[:3, 3] + np.array([0.6, 1.2, 0.0]), lage[:3, 3] - lage[:3, 2])
        szene.add(pyrender.DirectionalLight(color=np.ones(3), intensity=3.0), pose=licht)
        werk = pyrender.OffscreenRenderer(breite, hoehe)
        try:
            farbe, _ = werk.render(szene, flags=pyrender.RenderFlags.RGBA)
        finally:
            werk.delete()
        return np.asarray(farbe)

    # ------------------------------------------------------ Fotokamera

    #: Wie weit die Rig-Kugeln zur Kamera rücken, damit sie nicht in der Figur verschwinden (m).
    ZUR_KAMERA = 0.12

    def bild_kamera(self, kamera, hoehe=640):
        """Das Netz aus der Kamera des Fotos — derselbe Ausschnitt, dieselbe Pose (Edgar,
        20.09.2026: „Immer das 3D Modell in genau der gleichen pose und ausschnitt wie das 2D
        Bild!!!"). `kamera`: fx, fy, cx, cy in Fotopixeln, breite, hoehe des Fotos; die Punkte
        dieser Instanz liegen in OpenGL-Sicht (Kamera im Ursprung, Blick −z, y oben — der Runner
        hat OpenCVs y und z negiert). Das Bild wird auf `hoehe` Pixel verkleinert, fx/fy/cx/cy
        mit; gibt `(bild, breite_px, hoehe_px)`."""
        import pyrender

        faktor = float(hoehe) / float(kamera['hoehe'])
        breite_px = max(8, int(round(kamera['breite'] * faktor)))
        hoehe_px = max(8, int(round(kamera['hoehe'] * faktor)))
        szene = pyrender.Scene(bg_color=self.hintergrund, ambient_light=(0.35, 0.35, 0.35))
        szene.add(self._mesh(pyrender))
        if self.gelenke is not None and len(self.gelenke) >= 2:
            # Jede Kugel ein Stück zur Kamera (Ursprung) — je Gelenk in seine Blickrichtung.
            richtung = -self.gelenke
            laenge = np.maximum(1e-6, np.linalg.norm(richtung, axis=1, keepdims=True))
            vorn = (self.gelenke + richtung / laenge * self.ZUR_KAMERA).astype(np.float32)
            for teil in self._rig(pyrender, vorn):
                szene.add(teil)
        szene.add(pyrender.IntrinsicsCamera(
            fx=kamera['fx'] * faktor, fy=kamera['fy'] * faktor,
            cx=kamera['cx'] * faktor, cy=kamera['cy'] * faktor, znear=0.05, zfar=50.0,
        ), pose=np.eye(4))
        licht = np.eye(4)
        licht[:3, 3] = [0.6, 1.2, 0.0]
        szene.add(pyrender.DirectionalLight(color=np.ones(3), intensity=3.0), pose=licht)
        werk = pyrender.OffscreenRenderer(breite_px, hoehe_px)
        try:
            farbe, _ = werk.render(szene, flags=pyrender.RenderFlags.RGBA)
        finally:
            werk.delete()
        return np.asarray(farbe), breite_px, hoehe_px

    def speichern_kamera(self, pfad, kamera, hoehe=640):
        """`bild_kamera` als PNG; gibt `(breite_px, hoehe_px)`."""
        from PIL import Image

        bild, breite_px, hoehe_px = self.bild_kamera(kamera, hoehe)
        Image.fromarray(bild, 'RGBA').save(str(pfad))
        return breite_px, hoehe_px
