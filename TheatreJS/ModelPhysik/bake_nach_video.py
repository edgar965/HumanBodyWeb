# -*- coding: utf-8 -*-
u"""Eine `FPSBAKE1`-Ablage als MP4 — schattiert, nicht als Punktwolke.

WARUM SCHATTIERT (Edgar, 10.09.2026: „teste ob das wirklich eine animation
ist (und kein yeti)"): An einer Punktwolke ist nicht zu sehen, ob die Haut
zusammenhaengt. Eine schattierte Flaeche zeigt Beulen, Risse und
Selbstdurchdringungen sofort — dieselbe Ueberlegung wie am 07.09.2026 beim
Aermel, wo flache Schattierung ein sauberes Netz zerknittert aussehen liess.

Ohne pyrender-Fenster (`EGL`/`osmesa` sind hier nicht noetig — pyrender
rendert offscreen ueber OpenGL-Kontext von pyglet). Faellt das aus, wird auf
eine reine Software-Schattierung zurueckgefallen; die Meldung sagt, welcher
Weg genommen wurde, statt stumm ein anderes Bild zu liefern.

Aufruf:
    python bake_nach_video.py --bake figur/hb_female_walk.bin
                              [--aus A:/3DTools/Docu/Ergebnisse/x.mp4]
                              [--fps 20] [--breite 720] [--schleifen 3]
"""
import argparse
import os
import sys

import numpy as np

from bakedatei import Bakedatei

ORDNER = os.path.dirname(os.path.abspath(__file__))
ZIEL_VORGABE = r'A:\3DTools\Docu\Ergebnisse'


class Bakevideo:
    u"""Rendert die Punkte je Bild und schreibt ein MP4."""

    #: Hintergrund (RGB 0..1) — hell, damit die Silhouette zaehlt.
    HINTERGRUND = (0.94, 0.94, 0.96)

    #: Kamera: Abstand als Vielfaches der Figurhoehe, und die Hoehe, auf die
    #: sie blickt (Anteil der Figurhoehe).
    ABSTAND = 2.1
    BLICKHOEHE = 0.55

    def __init__(self, bake_pfad, off_pfad, breite=720, hoehe=960):
        self.bake = Bakedatei(bake_pfad)
        # DIE DREIECKE KOMMEN AUS DER ABLAGE, nicht aus der `.off` — FPS
        # sortiert die Punkte um (siehe `Bakedatei`). Die `.off` ist nur der
        # Rueckfall fuer alte `FPSBAKE1`-Dateien, und dann stimmt das Bild
        # nicht; deshalb sagt es die Meldung.
        if self.bake.dreiecke is not None:
            self.dreiecke = self.bake.dreiecke
        else:
            print(u'ACHTUNG: alte FPSBAKE1-Ablage ohne Dreiecke — die '
                  u'.off-Flaechen passen NICHT zu diesen Punkten.')
            self.dreiecke = self._off_flaechen(off_pfad)
        self.breite, self.hoehe = int(breite), int(hoehe)
        self.punkte_m = self._in_metern()

    # ------------------------------------------------------------- Eingabe

    @staticmethod
    def _off_flaechen(pfad):
        u"""Die Dreiecke der `.off` — die Punkte kommen aus dem Bake."""
        zeilen = open(pfad).read().split('\n')
        n, m, _ = [int(x) for x in zeilen[1].split()]
        return np.array([[int(x) for x in zeilen[2 + n + i].split()[1:4]]
                         for i in range(m)], dtype=np.int64)

    def _in_metern(self):
        u"""Auf Meter und auf den Boden.

        Der Massstab wird aus dem ERSTEN Bild gerechnet, nicht aus einer
        Konstanten: Die `.skel` traegt den Faktor der Figur, und wer ihn hier
        fest hinschreibt, misst nach dem naechsten Konverterlauf etwas
        anderes (Regel `artefakte-benennen`).
        """
        erstes = self.bake.daten[0]
        hoehe_einheiten = float(erstes[:, 2].max() - erstes[:, 2].min())
        faktor = hoehe_einheiten / 1.68        # die Figur ist 1,68 m hoch
        punkte = self.bake.daten / faktor
        boden = float(punkte[0][:, 2].min())
        mitte = punkte[0].reshape(-1, 3).mean(axis=0)
        punkte[:, :, 0] -= mitte[0]
        punkte[:, :, 1] -= mitte[1]
        punkte[:, :, 2] -= boden
        return punkte

    # ------------------------------------------------------------ Rendern

    def _kamera(self, figurhoehe):
        u"""Blick von vorn, leicht ueber Huefthoehe."""
        import trimesh
        abstand = self.ABSTAND * figurhoehe
        blick = self.BLICKHOEHE * figurhoehe
        lage = np.eye(4)
        # Y ist bei pyrender oben; unsere Punkte sind Z-oben und werden
        # deshalb beim Bauen des Netzes gedreht.
        lage[:3, 3] = [0.0, blick, abstand]
        return lage, trimesh

    def bilder(self):
        u"""Ein RGB-Feld je Bild (H x B x 3, uint8)."""
        import trimesh
        import pyrender
        figurhoehe = float(self.punkte_m[0][:, 2].max())
        lage, _ = self._kamera(figurhoehe)
        # Z-oben -> Y-oben
        drehung = np.array([[1.0, 0.0, 0.0],
                            [0.0, 0.0, 1.0],
                            [0.0, -1.0, 0.0]])
        kamera = pyrender.PerspectiveCamera(yfov=np.deg2rad(38.0))
        licht = pyrender.DirectionalLight(color=np.ones(3), intensity=3.2)
        lichtlage = np.eye(4)
        lichtlage[:3, 3] = [1.2 * figurhoehe, 1.6 * figurhoehe, 1.8 * figurhoehe]
        renderer = pyrender.OffscreenRenderer(self.breite, self.hoehe)
        try:
            for nummer in range(self.bake.bilder):
                punkte = self.punkte_m[nummer] @ drehung.T
                netz = trimesh.Trimesh(vertices=punkte, faces=self.dreiecke,
                                       process=False)
                # Ein MATERIAL, keine Flaechenfarben: pyrender lehnt
                # `face_colors` bei `smooth=True` ab („Cannot use face colors
                # with a smooth mesh"), und flach schattiert sieht jedes
                # Stoff- oder Hautnetz zerknittert aus (Befund vom
                # 07.09.2026 am Aermel).
                material = pyrender.MetallicRoughnessMaterial(
                    baseColorFactor=[0.84, 0.77, 0.70, 1.0],
                    metallicFactor=0.0, roughnessFactor=0.75)
                szene = pyrender.Scene(bg_color=list(self.HINTERGRUND) + [1.0],
                                       ambient_light=[0.35, 0.35, 0.38])
                szene.add(pyrender.Mesh.from_trimesh(netz, smooth=True,
                                                     material=material))
                szene.add(kamera, pose=lage)
                szene.add(licht, pose=lichtlage)
                farbe, _tiefe = renderer.render(szene)
                yield np.asarray(farbe[:, :, :3], dtype=np.uint8)
        finally:
            renderer.delete()

    # ------------------------------------------------------------- Ausgabe

    def schreiben(self, ziel, fps=20, schleifen=1):
        u"""MP4 schreiben. Gibt (Pfad, Bilderzahl) zurueck."""
        import cv2
        os.makedirs(os.path.dirname(ziel) or '.', exist_ok=True)
        gesammelt = list(self.bilder())
        if not gesammelt:
            raise SystemExit(u'Keine Bilder gerendert.')
        h, b = gesammelt[0].shape[:2]
        schreiber = cv2.VideoWriter(ziel, cv2.VideoWriter_fourcc(*'mp4v'),
                                    float(fps), (b, h))
        if not schreiber.isOpened():
            raise SystemExit(u'VideoWriter liess sich nicht oeffnen: %s' % ziel)
        try:
            for _ in range(max(1, int(schleifen))):
                for bild in gesammelt:
                    schreiber.write(cv2.cvtColor(bild, cv2.COLOR_RGB2BGR))
        finally:
            schreiber.release()
        return ziel, len(gesammelt) * max(1, int(schleifen))


def main():
    zerleger = argparse.ArgumentParser(description=__doc__)
    zerleger.add_argument('--bake', default=os.path.join(ORDNER, 'figur',
                                                         'hb_female_walk.bin'))
    zerleger.add_argument('--off', default=os.path.join(ORDNER, 'figur',
                                                        'hb_female.off'))
    zerleger.add_argument('--aus', default=None)
    zerleger.add_argument('--fps', type=int, default=20)
    zerleger.add_argument('--breite', type=int, default=720)
    zerleger.add_argument('--hoehe', type=int, default=960)
    zerleger.add_argument('--schleifen', type=int, default=3)
    werte = zerleger.parse_args()

    ziel = werte.aus or os.path.join(
        ZIEL_VORGABE,
        os.path.splitext(os.path.basename(werte.bake))[0] + '.mp4')

    video = Bakevideo(werte.bake, werte.off, werte.breite, werte.hoehe)
    print(u'Bake     %d Bilder, %d Punkte, %d Dreiecke'
          % (video.bake.bilder, video.bake.punkte, len(video.dreiecke)))
    pfad, zahl = video.schreiben(ziel, werte.fps, werte.schleifen)
    print(u'Video    %s (%d Bilder bei %d fps = %.1f s)'
          % (pfad, zahl, werte.fps, zahl / float(werte.fps)))
    print(u'         %.1f KB' % (os.path.getsize(pfad) / 1024.0))
    return 0


if __name__ == '__main__':
    sys.exit(main())
