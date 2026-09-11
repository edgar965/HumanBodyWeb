# -*- coding: utf-8 -*-
u"""Die HumanBody-Figur in Bewegung, angezogen — ein Video.

WARUM (Edgar, 10.09.2026: „ich brauche ein Video das du mit MEINEM
humanBody modell erzeugt hast mit einer Animation und Kleider Physik"):
Bisher gab es beides nur getrennt — den simulierten Koerper ohne Kleidung
und den fallenden Stoff auf einer stehenden Figur.

Zwei Quellen, ein Bild:

    Koerper   `figur/hb_female_walk.bin`   FastProjectiveSkinning, also
                                           MIT Weichgewebe-Simulation
    Stoff     `t-shirt_female_sim_rig.json`  das drapierte T-Shirt samt
                                           Hautgewichten fuer 176 Knochen

Der Stoff folgt ueber lineares Blend-Skinning denselben Knochen, die auch
die Koerperbewegung treiben. Die STOFFDYNAMIK steckt in der Drapierung
(sie ist in `kleiderphysik_tshirt.mp4` zu sehen), nicht in dieser
Bewegung — das steht so in der Meldung, damit die Zahl nicht mehr
verspricht als sie haelt.

Aufruf:  python angezogen_video.py [--bilder 60]
"""
import argparse
import json
import os
import sys

import numpy as np

from bakedatei import Bakedatei
from figur_nach_cody import Codyfigur

ORDNER = os.path.dirname(os.path.abspath(__file__))
STOFF = os.path.join('A:', os.sep, '3DTools', 'Assets', 'GarmentCode',
                     'ausgabe', 't-shirt_female',
                     't-shirt_female_sim_rig.json')
BVH = os.path.join('A:', os.sep, '3DTools', '3DObjects', 'animations', 'bvh',
                   'Walk', '01_01.bvh')
FIGURHOEHE = 1.68


class Angezogen:
    u"""Koerperbahn aus FPS, Stoff per Skinning, beides in Metern."""

    HINTERGRUND = (0.94, 0.94, 0.96)
    ABSTAND = 2.3
    BLICKHOEHE = 0.55

    def __init__(self, bake_pfad, stoff_pfad, bvh_pfad, bilder=60):
        self.bake = Bakedatei(bake_pfad)
        self.koerper = self._in_metern()
        with open(stoff_pfad) as datei:
            self.stoff = json.load(datei)
        self.s_punkte = np.asarray(self.stoff['punkte'], dtype=np.float64)
        if self.s_punkte.ndim == 1:
            self.s_punkte = self.s_punkte.reshape(-1, 3)
        self.s_dreiecke = np.asarray(self.stoff['dreiecke'],
                                     dtype=np.int64).reshape(-1, 3)
        self.bilder = min(bilder, self.bake.bilder)
        self._skinning(bvh_pfad)

    def _in_metern(self):
        u"""Die Bake-Bahn auf Meter und auf den Boden.

        Der Massstab kommt aus dem ERSTEN Bild, nicht aus einer Konstanten
        — die `.skel` traegt den Faktor der Figur (Regel `artefakte-benennen`).
        """
        erstes = self.bake.daten[0]
        faktor = float(erstes[:, 2].max() - erstes[:, 2].min()) / FIGURHOEHE
        punkte = self.bake.daten / faktor
        boden = float(punkte[0][:, 2].min())
        mitte = punkte[0].reshape(-1, 3).mean(axis=0)
        punkte[:, :, 0] -= mitte[0]
        punkte[:, :, 1] -= mitte[1]
        punkte[:, :, 2] -= boden
        return punkte

    def _skinning(self, bvh_pfad):
        u"""Stoffbahn: dieselben Knochen wie der Koerper, per LBS."""
        from bvh_nach_anim import Animschreiber
        figur = Codyfigur('female', mit_fingern=True)
        figur.VORLAUF = 0
        daten = Animschreiber('hb_female').spuren(bvh_pfad)
        namen = list(self.stoff['knochen'])
        # Die Gewichte liegen DUENNBESETZT je Punkt: [[knochennummer,
        # wert], ...] — bis zu vier Eintraege. Als dichte Matrix ist das
        # 7290 x 176 und damit klein genug.
        gewichte = np.zeros((len(self.s_punkte), len(namen)))
        for zeile, eintraege in enumerate(self.stoff['gewichte']):
            for nummer, wert in eintraege:
                gewichte[zeile, int(nummer)] = float(wert)

        # Die Ruhelage jedes Knochens — und ihre Umkehrung. Ohne die waere
        # es keine Verformung, sondern ein Versetzen in den Weltursprung.
        ruhe = figur._welt()
        ruhe_um = {}
        for name in namen:
            if name not in ruhe:
                continue
            punkt, quat = ruhe[name]
            dreh = self._dreh(quat)
            ruhe_um[name] = (dreh.T, -dreh.T @ np.asarray(punkt))

        bahn = np.zeros((self.bilder, len(self.s_punkte), 3))
        ort0 = None
        if daten.position_track:
            roh = np.asarray(daten.position_track['values'],
                             dtype=np.float64).reshape(-1, 3)
            orte = np.column_stack([roh[:, 0], -roh[:, 2], roh[:, 1]])
            ort0 = orte[Codyfigur.ERSTES_BILD]
        for nummer in range(self.bilder):
            quelle = Codyfigur.ERSTES_BILD + nummer
            ort = None if ort0 is None else orte[quelle] - ort0
            welt = figur._welt(daten.tracks, quelle, ort)
            ziel = np.zeros_like(self.s_punkte)
            summe = np.zeros((len(self.s_punkte), 1))
            for spalte, name in enumerate(namen):
                if name not in ruhe_um or name not in welt:
                    continue
                w = gewichte[:, spalte:spalte + 1]
                if not w.any():
                    continue
                punkt, quat = welt[name]
                dreh = self._dreh(quat)
                rum, tum = ruhe_um[name]
                ziel += w * ((self.s_punkte @ rum.T + tum) @ dreh.T
                             + np.asarray(punkt))
                summe += w
            bahn[nummer] = ziel / np.maximum(summe, 1e-9)
        self.stoffbahn = bahn
        self.ruheprobe = float(np.abs(self._lbs_ruhe(namen, gewichte, ruhe,
                                                     ruhe_um)
                                      - self.s_punkte).max())

    def _lbs_ruhe(self, namen, gewichte, ruhe, ruhe_um):
        u"""DIE PROBE: Skinning in der RUHELAGE muss den Stoff unveraendert
        lassen. Faellt sie durch, stimmt eine Konvention nicht — und in
        Bewegung sieht auch ein falsches Skinning plausibel aus."""
        ziel = np.zeros_like(self.s_punkte)
        summe = np.zeros((len(self.s_punkte), 1))
        for spalte, name in enumerate(namen):
            if name not in ruhe_um:
                continue
            w = gewichte[:, spalte:spalte + 1]
            if not w.any():
                continue
            punkt, quat = ruhe[name]
            dreh = self._dreh(quat)
            rum, tum = ruhe_um[name]
            ziel += w * ((self.s_punkte @ rum.T + tum) @ dreh.T
                         + np.asarray(punkt))
            summe += w
        return ziel / np.maximum(summe, 1e-9)

    @staticmethod
    def _dreh(quat):
        from anim_umsetzung import Animumsetzung
        return np.column_stack([Animumsetzung.drehen(quat, e)
                                for e in np.eye(3)])

    # ------------------------------------------------------------- Ausgabe

    def bilder_rendern(self, breite=640, hoehe=860):
        import trimesh
        import pyrender
        figurhoehe = float(self.koerper[0][:, 2].max())
        drehung = np.array([[1.0, 0.0, 0.0],
                            [0.0, 0.0, 1.0],
                            [0.0, -1.0, 0.0]])
        lage = np.eye(4)
        lage[:3, 3] = [0.0, self.BLICKHOEHE * figurhoehe,
                       self.ABSTAND * figurhoehe]
        kamera = pyrender.PerspectiveCamera(yfov=np.deg2rad(40.0))
        licht = pyrender.DirectionalLight(color=np.ones(3), intensity=3.4)
        lichtlage = np.eye(4)
        lichtlage[:3, 3] = [1.2 * figurhoehe, 1.6 * figurhoehe,
                            1.8 * figurhoehe]
        haut = pyrender.MetallicRoughnessMaterial(
            baseColorFactor=[0.86, 0.79, 0.72, 1.0], metallicFactor=0.0,
            roughnessFactor=0.8)
        tuch = pyrender.MetallicRoughnessMaterial(
            baseColorFactor=[0.25, 0.45, 0.78, 1.0], metallicFactor=0.0,
            roughnessFactor=0.55)
        werk = pyrender.OffscreenRenderer(breite, hoehe)
        try:
            for nummer in range(self.bilder):
                szene = pyrender.Scene(
                    bg_color=list(self.HINTERGRUND) + [1.0],
                    ambient_light=[0.38, 0.38, 0.40])
                k = trimesh.Trimesh(vertices=self.koerper[nummer] @ drehung.T,
                                    faces=self.bake.dreiecke, process=False)
                szene.add(pyrender.Mesh.from_trimesh(k, smooth=True,
                                                     material=haut))
                s = trimesh.Trimesh(
                    vertices=self.stoffbahn[nummer] @ drehung.T,
                    faces=self.s_dreiecke, process=False)
                szene.add(pyrender.Mesh.from_trimesh(s, smooth=True,
                                                     material=tuch))
                szene.add(kamera, pose=lage)
                szene.add(licht, pose=lichtlage)
                farbe, _t = werk.render(szene)
                yield np.asarray(farbe[:, :, :3], dtype=np.uint8)
        finally:
            werk.delete()

    def schreiben(self, ziel, fps=20, schleifen=2):
        import cv2
        os.makedirs(os.path.dirname(ziel) or '.', exist_ok=True)
        gesammelt = list(self.bilder_rendern())
        h, b = gesammelt[0].shape[:2]
        schreiber = cv2.VideoWriter(ziel, cv2.VideoWriter_fourcc(*'mp4v'),
                                    float(fps), (b, h))
        if not schreiber.isOpened():
            raise SystemExit(u'VideoWriter liess sich nicht oeffnen.')
        try:
            for _ in range(max(1, int(schleifen))):
                for bild in gesammelt:
                    schreiber.write(cv2.cvtColor(bild, cv2.COLOR_RGB2BGR))
        finally:
            schreiber.release()
        return ziel, len(gesammelt) * max(1, int(schleifen))


def main():
    zerleger = argparse.ArgumentParser(description=__doc__)
    zerleger.add_argument('--bake', default=os.path.join(
        ORDNER, 'figur', 'hb_female_walk.bin'))
    zerleger.add_argument('--stoff', default=STOFF)
    zerleger.add_argument('--bvh', default=BVH)
    zerleger.add_argument('--bilder', type=int, default=60)
    zerleger.add_argument('--aus', default=os.path.join(
        r'A:\3DTools\Docu\Ergebnisse', 'hb_angezogen_walk.mp4'))
    werte = zerleger.parse_args()

    video = Angezogen(werte.bake, werte.stoff, werte.bvh, werte.bilder)
    print(u'Koerper   %d Bilder, %d Punkte, %d Dreiecke (FPS-Simulation)'
          % (video.bilder, video.bake.punkte, len(video.bake.dreiecke)))
    print(u'Stoff     %d Punkte, %d Dreiecke'
          % (len(video.s_punkte), len(video.s_dreiecke)))
    print(u'RUHEPROBE %.6f m (Skinning in Ruhe darf den Stoff nicht bewegen)'
          % video.ruheprobe)
    weg = np.linalg.norm(video.stoffbahn[-1] - video.stoffbahn[0], axis=1)
    print(u'Stoffweg  Median %.0f mm, groesster %.0f mm'
          % (float(np.median(weg)) * 1000.0, float(weg.max()) * 1000.0))
    pfad, zahl = video.schreiben(werte.aus)
    print(u'Video     %s (%d Bilder, %.1f KB)'
          % (pfad, zahl, os.path.getsize(pfad) / 1024.0))
    return 0


if __name__ == '__main__':
    sys.exit(main())
