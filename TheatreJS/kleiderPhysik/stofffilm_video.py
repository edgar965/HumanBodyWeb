# -*- coding: utf-8 -*-
u"""Macht aus `stofffilm.npz` ein MP4: der Stoff faellt auf den Koerper.

Laeuft in `python14` (pyrender, trimesh, cv2), waehrend die Simulation in
`python10_Garment` rechnet. Bruecke ist die `.npz`.

Der Koerper wird MITGERENDERT, sonst schwebt der Stoff im Nichts und man
sieht nicht, dass er sich anlegt. Er kommt aus demselben Ordner, auf dem
simuliert wurde — nicht aus einem anderen: Genau diese Verwechslung hat am
06.09.2026 einen ganzen Messtag gekostet.

Aufruf:  python stofffilm_video.py [--aus <ziel.mp4>]
"""
import argparse
import os
import sys

import numpy as np

ORDNER = os.path.dirname(os.path.abspath(__file__))
GC = os.path.join('A:', os.sep, '3DTools', 'Assets', 'GarmentCode')


class Stoffvideo:
    u"""Rendert Stoffbahn und Koerper schattiert."""

    HINTERGRUND = (0.94, 0.94, 0.96)
    ABSTAND = 2.3
    BLICKHOEHE = 0.62

    def __init__(self, npz, obj_koerper, obj_stoff, breite=640, hoehe=860):
        # ZENTIMETER -> METER. Die Simulation rechnet in cm (gemessen:
        # Stoffhuelle y 93 bis 143), der Koerper steht in Metern (0 bis
        # 1,68). Ohne Umrechnung liegt der Stoff hundertfach zu gross weit
        # ausserhalb des Bildes — im Video sieht man dann nur den Koerper
        # und haelt das fuer eine fehlgeschlagene Simulation.
        self.bahn = np.load(npz)['punkte'].astype(np.float64) / 100.0
        self.k_punkte, self.k_flaechen = self._obj(obj_koerper)
        _p, self.s_flaechen = self._obj(obj_stoff)
        self.breite, self.hoehe = int(breite), int(hoehe)

    @staticmethod
    def _obj(pfad):
        u"""Punkte und Dreiecke einer OBJ. Vierecke werden geteilt."""
        punkte, flaechen = [], []
        for zeile in open(pfad):
            if zeile.startswith('v '):
                punkte.append([float(x) for x in zeile.split()[1:4]])
            elif zeile.startswith('f '):
                ecken = [int(t.split('/')[0]) - 1 for t in zeile.split()[1:]]
                for i in range(1, len(ecken) - 1):
                    flaechen.append([ecken[0], ecken[i], ecken[i + 1]])
        return np.array(punkte, dtype=np.float64), np.array(flaechen,
                                                            dtype=np.int64)

    def _kamera(self):
        u"""Ausschnitt aus dem KOERPER, nicht aus der Stoffbahn.

        Im ersten Bild haengt der Schnitt als flaches Panel weit vor dem
        Koerper; eine Huelle darueber macht die Figur winzig.
        """
        unten, oben = self.k_punkte[:, 1].min(), self.k_punkte[:, 1].max()
        hoehe = float(oben - unten)
        mitte = self.k_punkte.mean(axis=0)
        lage = np.eye(4)
        lage[:3, 3] = [mitte[0], unten + self.BLICKHOEHE * hoehe,
                       mitte[2] + self.ABSTAND * hoehe]
        return lage, hoehe

    def bilder(self):
        import trimesh
        import pyrender
        lage, hoehe = self._kamera()
        kamera = pyrender.PerspectiveCamera(yfov=np.deg2rad(40.0))
        licht = pyrender.DirectionalLight(color=np.ones(3), intensity=3.4)
        lichtlage = np.array(lage)
        lichtlage[:3, 3] = lage[:3, 3] + np.array([hoehe, hoehe, 0.6 * hoehe])
        haut = pyrender.MetallicRoughnessMaterial(
            baseColorFactor=[0.86, 0.79, 0.72, 1.0], metallicFactor=0.0,
            roughnessFactor=0.8)
        stoff = pyrender.MetallicRoughnessMaterial(
            baseColorFactor=[0.25, 0.45, 0.78, 1.0], metallicFactor=0.0,
            roughnessFactor=0.55)
        koerpernetz = trimesh.Trimesh(vertices=self.k_punkte,
                                      faces=self.k_flaechen, process=False)
        werk = pyrender.OffscreenRenderer(self.breite, self.hoehe)
        try:
            for punkte in self.bahn:
                szene = pyrender.Scene(
                    bg_color=list(self.HINTERGRUND) + [1.0],
                    ambient_light=[0.38, 0.38, 0.40])
                szene.add(pyrender.Mesh.from_trimesh(koerpernetz, smooth=True,
                                                     material=haut))
                netz = trimesh.Trimesh(vertices=punkte,
                                       faces=self.s_flaechen, process=False)
                szene.add(pyrender.Mesh.from_trimesh(netz, smooth=True,
                                                     material=stoff))
                szene.add(kamera, pose=lage)
                szene.add(licht, pose=lichtlage)
                farbe, _t = werk.render(szene)
                yield np.asarray(farbe[:, :, :3], dtype=np.uint8)
        finally:
            werk.delete()

    def schreiben(self, ziel, fps=25, halten=25):
        u"""`halten` haengt das Endbild an — sonst ist es kaum zu sehen."""
        import cv2
        os.makedirs(os.path.dirname(ziel) or '.', exist_ok=True)
        gesammelt = list(self.bilder())
        h, b = gesammelt[0].shape[:2]
        schreiber = cv2.VideoWriter(ziel, cv2.VideoWriter_fourcc(*'mp4v'),
                                    float(fps), (b, h))
        if not schreiber.isOpened():
            raise SystemExit(u'VideoWriter liess sich nicht oeffnen.')
        try:
            for bild in gesammelt + [gesammelt[-1]] * int(halten):
                schreiber.write(cv2.cvtColor(bild, cv2.COLOR_RGB2BGR))
        finally:
            schreiber.release()
        return ziel, len(gesammelt) + int(halten)


def main():
    zerleger = argparse.ArgumentParser(description=__doc__)
    zerleger.add_argument('--npz', default=os.path.join(ORDNER,
                                                        'stofffilm.npz'))
    zerleger.add_argument('--koerper', default=None)
    zerleger.add_argument('--stoff', default=os.path.join(
        GC, 'ausgabe', 't-shirt_female', 't-shirt_female_sim.obj'))
    zerleger.add_argument('--aus', default=os.path.join(
        r'A:\3DTools\Docu\Ergebnisse', 'kleiderphysik_tshirt.mp4'))
    werte = zerleger.parse_args()

    koerper = werte.koerper
    if not koerper:
        ordner = os.path.join(GC, 'koerper', 'female')
        obj = sorted(f for f in os.listdir(ordner) if f.endswith('.obj'))
        koerper = os.path.join(ordner, obj[0])

    video = Stoffvideo(werte.npz, koerper, werte.stoff)
    print(u'Stoffbahn %d Bilder, %d Punkte, %d Dreiecke'
          % (len(video.bahn), video.bahn.shape[1], len(video.s_flaechen)))
    print(u'Koerper   %s, %d Punkte'
          % (os.path.basename(koerper), len(video.k_punkte)))
    if video.bahn.shape[1] != int(video.s_flaechen.max()) + 1:
        print(u'ACHTUNG: %d Punkte, aber Dreiecke bis Index %d — die '
              u'Flaechen passen nicht zu dieser Bahn.'
              % (video.bahn.shape[1], int(video.s_flaechen.max())))
    pfad, zahl = video.schreiben(werte.aus)
    print(u'Video     %s (%d Bilder, %.1f KB)'
          % (pfad, zahl, os.path.getsize(pfad) / 1024.0))
    return 0


if __name__ == '__main__':
    sys.exit(main())
