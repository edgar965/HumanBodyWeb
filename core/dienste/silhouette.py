# -*- coding: utf-8 -*-
"""Silhouette — Umriss eines Koerpernetzes ueber einem Foto.

Aus `photo_silhouette_data` herausgeloest (Umbau 15.08.2026, 338 Zeilen in einem
Endpunkt). Der Ablauf ist immer derselbe: Netz auf die Bildflaeche projizieren,
vorderseitige Dreiecke rastern, Umriss abnehmen. Zwei Wege gibt es nur bei der
Projektion — mit gespeicherter Pose (dann liegen 2D-Punkte schon vor) oder
orthographisch aus den Vertices.
"""
import logging

import numpy as np

from ..daten.bildrahmen import Bildrahmen

logger = logging.getLogger('core')


class Silhouette:
    """Projektion und Umriss eines Netzes in Bildkoordinaten."""

    #: Kantenlaenge der Rastermaske. 512 ist genau genug fuer eine Kontur, die
    #: anschliessend ohnehin mit `approxPolyDP` vereinfacht wird.
    MASKE = 512
    #: Rand, den die orthographische Projektion frei laesst.
    RAND = 0.05

    def __init__(self, vertices, faces, breite, hoehe):
        self.vertices = vertices
        self.faces = faces
        self.breite = breite
        self.hoehe = hoehe
        self.projektion = None
        self.vorderseiten = None
        self.posiert = False
        self.anzahl_posiert = len(vertices)

    # ------------------------------------------------------------- projizieren

    def posierte_projektion(self, punkte_2d, versatz=None):
        """Fertige 2D-Punkte uebernehmen (aus der gespeicherten Pose).

        `versatz` ist die Feinkorrektur aus dem Assistenten: Verschiebung und
        Skalierung um den Schwerpunkt der gueltigen Punkte."""
        proj = np.asarray(punkte_2d, dtype=np.float32).copy()
        if versatz:
            gueltig = ~np.isnan(proj).any(axis=1)
            mx = proj[gueltig, 0].mean()
            my = proj[gueltig, 1].mean()
            s = versatz.get('scale', 1)
            proj[gueltig, 0] = (proj[gueltig, 0] - mx) * s + mx + versatz.get('dx', 0)
            proj[gueltig, 1] = (proj[gueltig, 1] - my) * s + my + versatz.get('dy', 0)
        self.projektion = proj
        self.posiert = True
        self.vorderseiten = self._vorderseiten_im_bild(proj)
        return proj

    def orthographische_projektion(self, koerpertransformation=None):
        """Netz mittig auf die Bildflaeche legen.

        Ohne Transformation wird die HOEHE eingepasst, nicht die Breite: Die
        T-Pose macht das Netz breit, und auf einem Hochformat waere die Figur
        sonst winzig."""
        v = self.vertices
        x_min, y_min = v[:, 0].min(), v[:, 1].min()
        x_max, y_max = v[:, 0].max(), v[:, 1].max()
        breite_netz, hoehe_netz = x_max - x_min, y_max - y_min
        s_x = self.breite * (1 - 2 * self.RAND) / max(breite_netz, 1e-6)
        s_y = self.hoehe * (1 - 2 * self.RAND) / max(hoehe_netz, 1e-6)
        grund = min(s_x, s_y)
        cx, cy = (x_min + x_max) / 2, (y_min + y_max) / 2

        proj = np.zeros((len(v), 2), dtype=np.float32)
        if koerpertransformation:
            bt = koerpertransformation
            s = grund * bt['scale']
            proj[:, 0] = (v[:, 0] - cx) * s + bt['center_x']
            proj[:, 1] = (cy - v[:, 1]) * s + bt['center_y']
        else:
            proj[:, 0] = (v[:, 0] - cx) * s_y + self.breite / 2
            proj[:, 1] = (cy - v[:, 1]) * s_y + self.hoehe / 2
        self.projektion = proj
        self.posiert = False
        self.vorderseiten = self._vorderseiten_3d()
        return proj

    def _vorderseiten_3d(self):
        """Dreiecke, die zur Kamera zeigen — Kreuzprodukt in der XY-Ebene."""
        v0 = self.vertices[self.faces[:, 0]]
        v1 = self.vertices[self.faces[:, 1]]
        v2 = self.vertices[self.faces[:, 2]]
        e1, e2 = v1 - v0, v2 - v0
        kreuz_z = e1[:, 0] * e2[:, 1] - e1[:, 1] * e2[:, 0]
        return np.where(kreuz_z > 0)[0]

    def _vorderseiten_im_bild(self, proj):
        """Dasselbe in Bildkoordinaten: Y zeigt nach unten, also ist im
        Uhrzeigersinn vorne (kreuz_z < 0)."""
        p0, p1, p2 = proj[self.faces[:, 0]], proj[self.faces[:, 1]], proj[self.faces[:, 2]]
        hat_nan = (np.isnan(p0).any(axis=1) | np.isnan(p1).any(axis=1)
                   | np.isnan(p2).any(axis=1))
        e1, e2 = p1 - p0, p2 - p0
        kreuz_z = e1[:, 0] * e2[:, 1] - e1[:, 1] * e2[:, 0]
        return np.where((kreuz_z < 0) & ~hat_nan)[0]

    # ----------------------------------------------------------------- rastern

    def maske(self, cv2):
        """Binaere Maske der Vorderseite, `MASKE` x `MASKE` Bildpunkte."""
        sx, sy = self.MASKE / self.breite, self.MASKE / self.hoehe
        maske = np.zeros((self.MASKE, self.MASKE), dtype=np.uint8)
        if self.posiert and self.anzahl_posiert < len(self.vertices):
            self._streuen(cv2, maske, sx, sy)
        else:
            self._dreiecke_fuellen(cv2, maske, sx, sy)
        return maske, sx, sy

    def _streuen(self, cv2, maske, sx, sy):
        """Fuer ein SMPL-Netz mit SMPL-X-Dreiecken: Punkte streuen statt rastern.

        Die Topologien passen nicht zueinander (6.890 gegen 10.475 Vertices);
        gerasterte Dreiecke ergaeben ein Flickenmuster. Deshalb werden die
        Punkte gesetzt und morphologisch geschlossen."""
        gueltig = self.projektion[:self.anzahl_posiert]
        gueltig = gueltig[~np.isnan(gueltig).any(axis=1)]
        px = (gueltig[:, 0] * sx).astype(np.int32)
        py = (gueltig[:, 1] * sy).astype(np.int32)
        drin = (px >= 0) & (px < self.MASKE) & (py >= 0) & (py < self.MASKE)
        maske[py[drin], px[drin]] = 255
        kern = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        geschlossen = cv2.morphologyEx(maske, cv2.MORPH_CLOSE, kern)
        weich = cv2.GaussianBlur(geschlossen, (7, 7), 0)
        _, fertig = cv2.threshold(weich, 127, 255, cv2.THRESH_BINARY)
        maske[:] = fertig

    def _dreiecke_fuellen(self, cv2, maske, sx, sy):
        proj = self.projektion
        for fi in self.vorderseiten:
            i0, i1, i2 = self.faces[fi]
            punkte = np.array([
                [proj[i0, 0] * sx, proj[i0, 1] * sy],
                [proj[i1, 0] * sx, proj[i1, 1] * sy],
                [proj[i2, 0] * sx, proj[i2, 1] * sy],
            ], dtype=np.int32).reshape((-1, 1, 2))
            cv2.fillConvexPoly(maske, punkte, 255)

    # ------------------------------------------------------------------ Umriss

    def koerperkontur(self, cv2):
        """Groesster Umriss der Maske, vereinfacht, in Bildkoordinaten."""
        maske, sx, sy = self.maske(cv2)
        konturen, _ = cv2.findContours(maske, cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)
        if not konturen:
            return []
        groesste = max(konturen, key=cv2.contourArea)
        toleranz = 0.001 * cv2.arcLength(groesste, True)
        vereinfacht = cv2.approxPolyDP(groesste, toleranz, True)
        return [[float(p[0][0] / sx), float(p[0][1] / sy)] for p in vereinfacht]

    def netz_rahmen(self):
        """Umschliessendes Rechteck der Projektion (NaN-fest).

        Die Rechnung steht in `Bildrahmen` — sie lag hier und in
        `Gesichtskontur` zweimal, und das Drahtformat `{x, y, w, h}` damit auch
        (17.08.2026).
        """
        return Bildrahmen.um(self.projektion)
