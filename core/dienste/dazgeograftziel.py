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

    def __init__(self, name):
        """`name`: Anzeigename des Stücks, z. B. `cute girl Scham`."""
        from Genesis9.pfade import G9pfade

        self.name = name
        self._netz, self._farbe = None, None
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

    def farbe_an(self, punkte):
        """`(N, 3)` Farbe (0–255) des Original-Atlas am nächsten Punkt der Fläche zu jedem der `punkte` — für `Schammessungtextur.gegen_original`."""
        import trimesh

        if self._netz is None:
            self._netz = trimesh.Trimesh(self.punkte, self.dreiecke, process=False)
            self._farbe = self.bild('farbe')
        if self._farbe is None:
            return None
        stelle, _abstand, dreieck = trimesh.proximity.closest_point(self._netz, np.asarray(punkte, dtype=np.float64))
        bary = trimesh.triangles.points_to_barycentric(self._netz.triangles[dreieck], stelle)
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
