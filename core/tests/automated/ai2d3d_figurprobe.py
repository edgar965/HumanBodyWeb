# -*- coding: utf-8 -*-
"""Ai2d3dfigurprobe — die geometrische Figur eines 2d-3d-AI-Laufs (`<Job>/abnahme/training_figur.json`, `Trainingfigur`) gegen die Fotos des Jobs: Projektion, Sichtbarkeit,
Masken der Person. Gemeinsam für die Tests Geschlecht, Textur und Augen (29.10.2026 abends). Nur numpy, nur lesen; ohne Django (der Test reicht den Ordner herein).

  Projektion  wie `KoerperKI_Fotos.Fotoeinpassung.bild`: Lochkamera aus der Kamera der Seite (ort, ziel, oben, fov) mit dem Bildpunkt des Ziels `versatz_px` — das Ziel liegt im
              Foto nicht in der Bildmitte (ohne ihn 120–280 px daneben, `diag_mesh_pruefungen.py`)
  sichtbar    Tiefenpuffer über Ecken und Dreiecksmitten in Zellen von ZELLE_PX: sichtbar ist, wer höchstens TIEFE_MM hinter dem vordersten Punkt seiner Zelle liegt
  Masken      Sapiens2 je Foto aus der Segmentablage des Jobs (`<arbeitsordner>/segmente/<Foto>_*.npz`, `KopfKI.Fotosegmentablage`): person, haut, haar, bart; die jüngste Datei

    p = Ai2d3dfigurprobe(objects_root, 'EdgarTrip')
    for nr, f in p.fotos():   uv, z = p.projektion(f, x);   sb = p.sichtbar(uv, z, f)
"""
import base64
import json
from pathlib import Path

import numpy as np

__all__ = ['Ai2d3dfigurprobe']


class Ai2d3dfigurprobe:
    ZELLE_PX, TIEFE_MM = 12, 15.0

    def __init__(self, objects_root, job):
        self.ordner = Path(objects_root) / 'ai2d3d' / job
        self.job = json.loads((self.ordner / 'job.json').read_text(encoding='utf-8'))
        datei = self.ordner / 'abnahme' / 'training_figur.json'
        self.figur = json.loads(datei.read_text(encoding='utf-8')) if datei.is_file() else None
        datei = self.ordner / 'abnahme' / 'training.json'
        self.training = json.loads(datei.read_text(encoding='utf-8')) if datei.is_file() else None
        self.dreiecke = self.feld(self.figur['dreiecke'], '<u4', 3).astype(np.int64) if self.figur else None
        self._masken = {}

    @staticmethod
    def feld(text, typ, breite=None):
        a = np.frombuffer(base64.b64decode(text), dtype=typ)
        return a.reshape(-1, breite) if breite else a

    def fotos(self):
        """[(nr, Eintrag des Fotos in training_figur.json)] — nur Fotos mit Kamera samt Bildversatz."""
        return [(nr, f) for nr, f in (self.figur or {}).get('fotos', {}).items() if 'versatz_px' in f.get('kamera', {})]

    def punkte(self, f):
        return self.feld(f['punkte'], '<f4', 3).astype(np.float64)

    def mm_je_px(self, nr):
        return float(self.training['fotos'][nr]['mm_je_px'])

    @staticmethod
    def projektion(f, x):
        """(uv (N, 2) px, Tiefe (N,) m) der Punkte x (N, 3) im Foto."""
        k = f['kamera']
        ort, ziel, oben = (np.asarray(k[n], dtype=np.float64) for n in ('ort', 'ziel', 'oben'))
        vor = (ziel - ort) / np.linalg.norm(ziel - ort)
        rechts = np.cross(vor, oben)
        rechts /= np.linalg.norm(rechts)
        hoch = np.cross(rechts, vor)
        d = x - ort
        z = d @ vor
        brenn = k['hoehe'] / 2 / np.tan(np.radians(k['fov']) / 2)
        t = k['versatz_px']
        return np.stack([t[0] + brenn * (d @ rechts) / z, t[1] - brenn * (d @ hoch) / z], 1), z

    def sichtbar(self, uv, z, f, dreiecke=None):
        """(N,) bool — Tiefenpuffer über Ecken und Dreiecksmitten (`dreiecke`: Vorgabe die der Figur)."""
        tri = self.dreiecke if dreiecke is None else dreiecke
        h, w = f['kamera']['hoehe'], f['kamera']['breite']
        a_uv = np.concatenate([uv, uv[tri].mean(1)])
        a_z = np.concatenate([z, z[tri].mean(1)])
        zx, zy = np.floor(a_uv[:, 0] / self.ZELLE_PX).astype(np.int64), np.floor(a_uv[:, 1] / self.ZELLE_PX).astype(np.int64)
        breite, hoehe = w // self.ZELLE_PX + 2, h // self.ZELLE_PX + 2
        gut = (zx >= 0) & (zy >= 0) & (zx < breite) & (zy < hoehe)
        zelle = np.where(gut, zy * breite + zx, 0)
        vorn = np.full(breite * hoehe, np.inf)
        np.minimum.at(vorn, zelle[gut], a_z[gut])
        n = len(z)
        return gut[:n] & (z <= vorn[zelle[:n]] + self.TIEFE_MM / 1000)

    def masken(self, datei):
        """{person, haut, haar, bart, …: (H, W) bool} des Fotos aus der Segmentablage des Jobs, oder None."""
        if datei not in self._masken:
            ablage = Path(self.job.get('arbeitsordner', '')) / 'segmente'
            alle = sorted(ablage.glob('%s_*.npz' % Path(datei).stem), key=lambda p: p.stat().st_mtime) if ablage.is_dir() else []
            if not alle:
                self._masken[datei] = None
            else:
                with np.load(alle[-1]) as z:
                    self._masken[datei] = {k: z[k].astype(bool) for k in z.files if z[k].ndim == 2}
        return self._masken[datei]

    def bild(self, datei):
        """(H, W, 3) int64 — das Foto des Jobs mit diesem Dateinamen."""
        from PIL import Image
        pfad = next(Path(f['datei']) for f in self.job['fotos'] if Path(f['datei']).name == datei)
        return np.asarray(Image.open(pfad).convert('RGB')).astype(np.int64)

    @staticmethod
    def pixel(uv, form):
        """(ix, iy) gerundet und ins Bild geklemmt."""
        h, w = form
        return np.clip(uv[:, 0].round().astype(np.int64), 0, w - 1), np.clip(uv[:, 1].round().astype(np.int64), 0, h - 1)
