# -*- coding: utf-8 -*-
"""Dazgeograftziel — die Scham eines Blender-Imports, auf die das Daz-Geograft angepasst wird (10.10.2026).

Edgar: „im Blender-File war die Scham ja vorgegeben, die sollst du mit Hilfe der Scham aus Genesis nachbauen". Die Vorgabe liegt als Stück „<Figur> Scham" in der eigenen
Bibliothek (`Blendimportstuecke.scham_stueck`): Dreiecke des Originals dort, wo die Figur es nicht trägt (gemessen am cute girl: 2.673 Punkte, 4.986 Dreiecke, bis 28 mm vor der Haut,
Median 15,8 mm), in der Ruhelage der Figur dieses Imports, mit einem Atlas aus der Originaltextur (`…_atlas_farbe.jpg`, `…_normalen.png`, `…_rauheit.png`, 2.048 × 3.832).
Hier wird sie gelesen: Netz, UV je Ecke und die Bilder.
"""
import gzip
import json
from pathlib import Path

import numpy as np

__all__ = ['Dazgeograftziel']


class Dazgeograftziel:
    KANAELE = ('farbe', 'normalen', 'rauheit')
    #: Abstand (m) der Proben, mit denen die Fläche des Originals für die seitenbewusste Suche abgetastet wird (Fehler der UV dabei höchstens die Hälfte).
    PROBE_M = 0.0004
    #: Preis (m) für die Abweichung der Normalen in der Suche: eine Normale, die der gesuchten entgegensteht, kostet 2 · so viel an Abstand. Gemessen 11.10.2026 an „cute girl Scham" gegen
    #: das Daz-Stück (291.045 Texel; Texel mit Normale des nächsten Originalpunkts entgegengesetzt / über 60°, Median des Abstands): ohne Preis 5,8 % / 10,6 %, 1,36 mm; 3 mm: 1,4 % / 4,5 %,
    #: 1,47 mm; **5 mm: 1,2 % / 3,5 %, 1,60 mm**; 10 mm: 0,05 % / 1,6 %, 2,11 mm (die Wahl ist eine Setzung: mehr Preis zieht weiter vom nächsten Punkt weg).
    NORMALEN_PREIS_M = 0.005

    def __init__(self, name):
        """`name`: Anzeigename des Stücks, z. B. `cute girl Scham`."""
        from Genesis9.pfade import G9pfade

        self.name = name
        self._netz, self._farbe, self._proben = None, None, None
        stamm = name.replace(' ', '_')
        self.ordner = G9pfade.eigene() / 'data' / 'EIGEN' / name
        self.bilder_ordner = G9pfade.eigene() / 'Runtime' / 'Textures' / 'EIGEN' / name
        dsf = self._lesen(self.ordner / ('EIGEN_%s.dsf' % stamm))['geometry_library'][0]
        self.punkte = np.asarray(dsf['vertices']['values'], dtype=np.float64) * 0.01
        zeilen = np.asarray(dsf['polylist']['values'], dtype=np.int64)
        if zeilen.shape[1] != 5:
            raise ValueError('%s: erwartet Dreiecke, bekam Flächen mit %d Ecken' % (name, zeilen.shape[1] - 2))
        self.dreiecke = zeilen[:, 2:5]
        uvsatz = self._lesen(self.ordner / 'UV Sets' / 'EIGEN' / 'Base' / 'default.dsf')['uv_set_library'][0]
        self.uv_ecken = self._uv_ecken(np.asarray(uvsatz['uvs']['values'], dtype=np.float64), uvsatz.get('polygon_vertex_indices') or [])

    @staticmethod
    def _lesen(pfad):
        roh = Path(pfad).read_bytes()
        return json.loads((gzip.decompress(roh) if roh[:2] == b'\x1f\x8b' else roh).decode('utf-8'))

    def _uv_ecken(self, uvs, aus_nahten):
        """UV je Dreiecksecke `(T, 3, 2)`: Vorgabe ist die UV des Punkts, Nahtecken (`polygon_vertex_indices`: Dreieck, Punkt, UV-Nummer) nehmen ihre eigene."""
        ecken = uvs[self.dreiecke]
        for dreieck, punkt, nummer in aus_nahten:
            platz = np.flatnonzero(self.dreiecke[dreieck] == punkt)
            if len(platz):
                ecken[dreieck, platz[0]] = uvs[nummer]
        return ecken

    def netz(self):
        """Die Fläche des Originals als `trimesh.Trimesh` (einmal gebaut)."""
        import trimesh

        if self._netz is None:
            self._netz = trimesh.Trimesh(self.punkte, self.dreiecke, process=False)
        return self._netz

    def stelle(self, positionen, normalen=None):
        """`(dreieck, bary)` des Punkts der Fläche zu jeder Position (M, 3). Ohne `normalen` der nächste Punkt. Mit `normalen` (M, 3, die gesuchte Außenrichtung): der Punkt, der Abstand und
        Abweichung der Normale zusammen (`NORMALEN_PREIS_M`) am kleinsten hält — an einem Spalt (Eingang, innere Lippen) liegt der nächste Punkt oft auf der GEGENÜBERLIEGENDEN Wand, mit
        deren Farbe das Stück sonst gefärbt würde (gemessen: 5,8 % der Texel am angepassten Daz-Stück). Die Fläche wird dafür dicht abgetastet (`PROBE_M`); die Normalen sind die der Punkte,
        das Original ist in sich gleich herum gewickelt."""
        import trimesh
        from scipy.spatial import cKDTree

        positionen = np.asarray(positionen, dtype=np.float64)
        if normalen is None:
            stelle, _abstand, dreieck = trimesh.proximity.closest_point(self.netz(), positionen)
            return dreieck, trimesh.triangles.points_to_barycentric(self.netz().triangles[dreieck], stelle)
        if self._proben is None:
            self._proben = self._abtasten()
        baum, dreieck, bary = self._proben
        i = baum.query(np.column_stack([positionen, self.NORMALEN_PREIS_M * np.asarray(normalen, dtype=np.float64)]), workers=-1)[1]
        return dreieck[i], bary[i]

    def _abtasten(self):
        """Dichte Proben auf der Fläche: `(KD-Baum über Ort und Preis · Normale, Dreieck, Schwerpunktkoordinaten je Probe)`."""
        from scipy.spatial import cKDTree

        ecken = self.punkte[self.dreiecke]
        kante = np.maximum.reduce([np.linalg.norm(ecken[:, 1] - ecken[:, 0], axis=1), np.linalg.norm(ecken[:, 2] - ecken[:, 1], axis=1),
                                   np.linalg.norm(ecken[:, 0] - ecken[:, 2], axis=1)])
        teilung = np.maximum(1, np.ceil(kante / self.PROBE_M).astype(np.int64))
        dreieck, bary = [], []
        for m in np.unique(teilung):
            gruppe = np.flatnonzero(teilung == m)
            ij = np.array([(i, j) for i in range(m + 1) for j in range(m + 1 - i)], dtype=np.float64) / m
            b = np.column_stack([ij[:, 0], ij[:, 1], 1.0 - ij.sum(axis=1)])
            dreieck.append(np.repeat(gruppe, len(b)))
            bary.append(np.tile(b, (len(gruppe), 1)))
        dreieck, bary = np.concatenate(dreieck), np.concatenate(bary)
        ort = np.einsum('mk,mkj->mj', bary, ecken[dreieck])
        richtung = np.einsum('mk,mkj->mj', bary, np.asarray(self.netz().vertex_normals)[self.dreiecke[dreieck]])
        richtung /= np.maximum(np.linalg.norm(richtung, axis=1, keepdims=True), 1e-12)
        return cKDTree(np.column_stack([ort, self.NORMALEN_PREIS_M * richtung])), dreieck, bary

    def farbe_an(self, punkte, normalen=None):
        """`(N, 3)` Farbe (0–255) des Original-Atlas am Punkt der Fläche zu jedem der `punkte` (`stelle`: mit `normalen` seitenbewusst) — für `Schammessungtextur.gegen_original`."""
        if self._farbe is None:
            self._farbe = self.bild('farbe')
        if self._farbe is None:
            return None
        dreieck, bary = self.stelle(punkte, normalen)
        uv = np.einsum('mk,mkj->mj', bary, self.uv_ecken[dreieck])
        h, w = self._farbe.shape[:2]
        x = np.clip((uv[:, 0] * w).astype(np.int64), 0, w - 1)
        y = np.clip(((1.0 - uv[:, 1]) * h).astype(np.int64), 0, h - 1)
        return self._farbe[y, x].astype(np.float64)

    def bild(self, kanal):
        """Das Atlasbild `kanal` (`farbe`, `normalen`, `rauheit`) als `(H, W, 3)` uint8 (RGB) — oder None, wenn es fehlt."""
        from PIL import Image

        for endung in ('jpg', 'png'):
            pfad = self.bilder_ordner / ('EIGEN_%s_atlas_%s.%s' % (self.name.replace(' ', '_'), kanal, endung))
            if pfad.is_file():
                return np.asarray(Image.open(pfad).convert('RGB'))
        return None
