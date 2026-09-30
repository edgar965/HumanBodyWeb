# -*- coding: utf-8 -*-
"""Genesishaarrender — Figur mit Frisur als freigestelltes Bild, je Blickwinkel (30.09.2026).

Was die Iterationen zum Vergleichen brauchen (`Iterationsbild`, `Iterationsnote`): die Figur vor
NICHTS — ein PNG mit Alpha, in dem nur die Figur steht. Der Umriss ist die halbe Note, also darf kein
Hintergrund hineinzählen; das Alpha kommt aus der Tiefenkarte (wo pyrender nichts getroffen hat, ist
Tiefe 0).

**Orthografisch, nicht perspektivisch:** Die Note vergleicht Umrisse, nachdem `Iterationsbild` beide
Bilder an der Figur ausgerichtet hat (Höhe und Schwerpunkt des Rumpfbands). Eine perspektivische Kamera
verschiebt Kopf und Füße je nach Abstand gegeneinander — die Ausrichtung könnte das nicht mehr
herausrechnen.

Der Winkel zählt in Grad ab vorn, positiv zur LINKEN Seite der Figur (der Vertrag in
`Genesishaarengine`, dieselbe Drehrichtung wie `Durchschimmerprobe.ANSICHTEN`).

Läuft im Arbeitsprozess (`haarengine_fahren`, python14), nie im Django-Server — pyrender belegt die
Grafikkarte (`Haar/haarbild.py` hält es ebenso).
"""

import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Genesishaarrender']


class Genesishaarrender:
    """`bild(punkte, dreiecke, farbe, winkel, pfad)` → Pfad des freigestellten PNG."""

    #: Bildgröße (Breite × Höhe) — hochkant wie eine stehende Figur.
    BREITE, HOEHE = 512, 768
    #: Rand um die Figur, als Anteil ihrer Höhe.
    RAND = 0.06
    UMGEBUNG = 0.55
    LICHT = 2.2
    #: Die Haut, wenn der Körper keine eigene Farbe trägt (die Note vergleicht Farbflächen).
    HAUT = (0.82, 0.68, 0.60)

    def __init__(self, koerper=None):
        """`koerper`: Pfad einer GLB (die Grundfigur mit Rig) oder `(punkte, dreiecke)` — sie steht in
        jedem Bild mit, sonst verglichen wir eine Frisur ohne Kopf."""
        self._koerper = self._laden(koerper)
        self._renderer = None

    # -------------------------------------------------------------- Netze

    @staticmethod
    def _laden(koerper):
        if koerper is None:
            return None
        if isinstance(koerper, tuple):
            return (np.asarray(koerper[0], dtype=np.float64), np.asarray(koerper[1], dtype=np.int64))
        import trimesh
        netz = trimesh.load(str(koerper), force='mesh', process=False)
        return (np.asarray(netz.vertices, dtype=np.float64), np.asarray(netz.faces, dtype=np.int64))

    def renderer(self):
        if self._renderer is None:
            import pyrender
            self._renderer = pyrender.OffscreenRenderer(self.BREITE, self.HOEHE)
        return self._renderer

    def schliessen(self):
        if self._renderer is not None:
            try:
                self._renderer.delete()
            except Exception:  # noqa: BLE001 — beim Aufräumen zählt nur, dass es weitergeht
                logger.debug('Haarrender: Renderer ließ sich nicht schließen', exc_info=True)
            self._renderer = None

    # ------------------------------------------------------------- Bilder

    @staticmethod
    def _hex(farbe):
        roh = str(farbe or '').lstrip('#')
        if len(roh) != 6:
            return (0.28, 0.20, 0.15)
        return tuple(int(roh[i:i + 2], 16) / 255.0 for i in (0, 2, 4))

    def _szene(self, pyrender, teile, mitte, hoehe, winkel):
        szene = pyrender.Scene(bg_color=(0, 0, 0, 0), ambient_light=(self.UMGEBUNG,) * 3)
        for punkte, dreiecke, farbe in teile:
            if punkte is None or dreiecke is None or not len(dreiecke):
                continue
            import trimesh
            netz = trimesh.Trimesh(vertices=np.asarray(punkte, dtype=np.float64),
                                   faces=np.asarray(dreiecke, dtype=np.int64), process=False)
            material = pyrender.MetallicRoughnessMaterial(
                baseColorFactor=(*farbe, 1.0), metallicFactor=0.0, roughnessFactor=0.75,
                doubleSided=True)
            szene.add(pyrender.Mesh.from_trimesh(netz, material=material, smooth=False))
        # Orthografisch: die halbe Bildhöhe in Metern ist `ymag`; die Breite folgt dem Seitenverhältnis.
        halb = 0.5 * hoehe * (1.0 + 2.0 * self.RAND)
        kamera = pyrender.OrthographicCamera(xmag=halb * self.BREITE / self.HOEHE, ymag=halb)
        bogen = np.radians(float(winkel))
        c, s = np.cos(bogen), np.sin(bogen)
        lage = np.eye(4)
        lage[:3, :3] = np.array([[c, 0.0, s], [0.0, 1.0, 0.0], [-s, 0.0, c]])
        lage[:3, 3] = mitte + max(2.0 * hoehe, 2.0) * np.array([s, 0.0, c])
        szene.add(kamera, pose=lage)
        szene.add(pyrender.DirectionalLight(color=np.ones(3), intensity=self.LICHT), pose=lage)
        return szene

    def bild(self, punkte, dreiecke, farbe, winkel, pfad):
        """Figur + Frisur aus `winkel` Grad, freigestellt nach `pfad` (PNG mit Alpha)."""
        teile = []
        if self._koerper is not None:
            teile.append((self._koerper[0], self._koerper[1], self.HAUT))
        if punkte is not None and dreiecke is not None:
            teile.append((punkte, dreiecke, self._hex(farbe)))
        return self.bild_teile(teile, winkel, pfad)

    def bild_teile(self, teile, winkel, pfad, groesse=None):
        """Beliebig viele Teile `[(punkte, dreiecke, farbe rgb 0…1)]` — „2D3D Kleider" (Körper, Kleider, Haar)
        aus `winkel` Grad, freigestellt nach `pfad`. `groesse` (Breite, Höhe) statt BREITE × HOEHE: ein kleines
        Bild für die Iterationen, die Note rechnet ohnehin auf 128 × 192."""
        import pyrender
        from PIL import Image

        teile = [(p, d, tuple(float(c) for c in np.asarray(f)[:3])) for p, d, f in teile if p is not None]
        if not teile:
            raise ValueError('Nichts zu rendern — weder Körper noch Frisur')
        if groesse and tuple(groesse) != (self.BREITE, self.HOEHE):
            self.schliessen()
            self.BREITE, self.HOEHE = int(groesse[0]), int(groesse[1])
        alle = np.vstack([t[0] for t in teile])
        mitte = np.array([0.0, 0.5 * (alle[:, 1].min() + alle[:, 1].max()), 0.0])
        hoehe = float(alle[:, 1].max() - alle[:, 1].min()) or 1.0
        szene = self._szene(pyrender, teile, mitte, hoehe, winkel)
        farbbild, tiefe = self.renderer().render(szene)
        alpha = (np.asarray(tiefe) > 0).astype(np.uint8) * 255
        rgba = np.dstack([np.asarray(farbbild)[..., :3], alpha])
        pfad.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(rgba, mode='RGBA').save(pfad)
        return pfad
