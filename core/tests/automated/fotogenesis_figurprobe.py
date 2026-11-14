# -*- coding: utf-8 -*-
"""Fotogenesisfigurprobe — die geometrische Figur eines Foto-Genesis-Laufs (`<Job>/abnahme/training_figur.json`, `Trainingfigur`) gegen die Fotos des Jobs: Projektion, Sichtbarkeit,
Masken der Person. Gemeinsam für die Tests Geschlecht, Textur und Augen (29.10.2026 abends). Nur numpy, nur lesen; ohne Django (der Test reicht den Ordner herein).

  Projektion  wie `KoerperKI_Fotos.Fotoeinpassung.bild`: Lochkamera aus der Kamera der Seite (ort, ziel, oben, fov) mit dem Bildpunkt des Ziels `versatz_px` — das Ziel liegt im
              Foto nicht in der Bildmitte (ohne ihn 120–280 px daneben, `diag_mesh_pruefungen.py`)
  sichtbar    Tiefenpuffer in Zellen von ZELLE_PX über die dicht abgetasteten Dreiecke: sichtbar ist, wer höchstens TIEFE_MM hinter der vordersten Fläche seiner Zelle liegt
  Masken      Sapiens2 je Foto aus der Segmentablage des Jobs (`<arbeitsordner>/segmente/<Foto>_*.npz`, `KopfKI.Fotosegmentablage`): person, haut, haar, bart; die jüngste Datei

    p = Fotogenesisfigurprobe(objects_root, 'EdgarTrip')
    for nr, f in p.fotos():   uv, z = p.projektion(f, x);   sb = p.sichtbar(uv, z, f)
"""
import base64
import json
from pathlib import Path

import numpy as np
import sys as _npz_sys  # noqa: E402
if r'A:\3DTools' not in _npz_sys.path:
    _npz_sys.path.append(r'A:\3DTools')
from KoerperKI_alle.npztorch import Npztorch  # noqa: E402

__all__ = ['Fotogenesisfigurprobe']


class Fotogenesisfigurprobe:
    ZELLE_PX, TIEFE_MM = 12, 15.0

    def __init__(self, objects_root, job):
        self.ordner = Path(objects_root) / 'fotogenesis' / job
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

    #: Stützpunkte je Dreieckskante für den Tiefenpuffer: (S+1)(S+2)/2 Punkte je Dreieck. Mit Ecken und Mitten allein (bis 29.10.2026 23 Uhr) blieben an den Oberschenkeln
    #: (Dreiecke 40–50 px) Zellen ohne vordere Fläche — im Profil galten Punkte des Schritts HINTER dem Oberschenkel als sichtbar (`diag_mesh_reste.py`, 3.jpg und 4.jpg)
    STUETZ = 8

    def _baryzentrisch(self):
        s = self.STUETZ
        a, b = np.meshgrid(np.arange(s + 1), np.arange(s + 1), indexing='ij')
        gut = a + b <= s
        return np.stack([a[gut], b[gut], s - a[gut] - b[gut]], 1) / s           # (K, 3)

    def sichtbar(self, uv, z, f, dreiecke=None):
        """(N,) bool — Tiefenpuffer über die Dreiecke, je Dreieck dicht abgetastet (`dreiecke`: Vorgabe die der Figur)."""
        tri = self.dreiecke if dreiecke is None else dreiecke
        h, w = f['kamera']['hoehe'], f['kamera']['breite']
        breite, hoehe = w // self.ZELLE_PX + 2, h // self.ZELLE_PX + 2
        vorn = np.full(breite * hoehe, np.inf)
        bary = self._baryzentrisch()
        for i in range(0, len(tri), 8192):
            t = tri[i:i + 8192]
            p_uv = np.einsum('kj,tjc->tkc', bary, uv[t]).reshape(-1, 2)
            p_z = np.einsum('kj,tj->tk', bary, z[t]).reshape(-1)
            zx, zy = np.floor(p_uv[:, 0] / self.ZELLE_PX).astype(np.int64), np.floor(p_uv[:, 1] / self.ZELLE_PX).astype(np.int64)
            gut = (zx >= 0) & (zy >= 0) & (zx < breite) & (zy < hoehe)
            np.minimum.at(vorn, zy[gut] * breite + zx[gut], p_z[gut])
        zx, zy = np.floor(uv[:, 0] / self.ZELLE_PX).astype(np.int64), np.floor(uv[:, 1] / self.ZELLE_PX).astype(np.int64)
        gut = (zx >= 0) & (zy >= 0) & (zx < breite) & (zy < hoehe)
        zelle = np.where(gut, zy * breite + zx, 0)
        return gut & (z <= vorn[zelle] + self.TIEFE_MM / 1000)

    #: Klassen von Sapiens2 (`Sapiens2Torch/segmentierung.py`, `S2segmentierung.KLASSEN`) — Index = Wert in `klassen` der Segmentablage
    SAPIENS = ('Background', 'Apparel', 'Eyeglass', 'Face_Neck', 'Hair', 'Left_Foot', 'Left_Hand', 'Left_Lower_Arm', 'Left_Lower_Leg', 'Left_Shoe', 'Left_Sock',
               'Left_Upper_Arm', 'Left_Upper_Leg', 'Lower_Clothing', 'Right_Foot', 'Right_Hand', 'Right_Lower_Arm', 'Right_Lower_Leg', 'Right_Shoe', 'Right_Sock',
               'Right_Upper_Arm', 'Right_Upper_Leg', 'Torso', 'Upper_Clothing', 'Lower_Lip', 'Upper_Lip', 'Lower_Teeth', 'Upper_Teeth', 'Tongue')

    def arbeitsordner(self):
        """Arbeitsordner der Kette wie `KoerperKI_Fotos.Fotojob` (ohne `arbeitsordner` in der job.json: `Fotojob.ARBEIT/<Job>`, so bei Probejobs — bis 02.11.2026 suchte die
        Probe dort `segmente` im Arbeitsverzeichnis, fand keine Masken und die Tests maßen nichts)."""
        if self.job.get('arbeitsordner'):
            return Path(self.job['arbeitsordner'])
        import sys
        wurzel = str(self.ordner.parents[2])                       # <TOOLS>/3DObjects/fotogenesis/<Job>
        if wurzel not in sys.path:
            sys.path.append(wurzel)
        from KoerperKI_Fotos.fotojob import Fotojob
        return Fotojob.ARBEIT / self.ordner.name

    def _ablage(self, datei):
        ablage = self.arbeitsordner() / 'segmente'
        alle = sorted(ablage.glob('%s_*.npz' % Path(datei).stem), key=lambda p: p.stat().st_mtime) if ablage.is_dir() else []
        return alle[-1] if alle else None

    def masken(self, datei):
        """{person, haut, haar, bart, …: (H, W) bool} des Fotos aus der Segmentablage des Jobs, oder None."""
        if datei not in self._masken:
            pfad = self._ablage(datei)
            if pfad is None:
                self._masken[datei] = None
            else:
                with Npztorch.lesen_numpy(pfad) as z:
                    self._masken[datei] = {k: z[k].astype(bool) for k in z.files if z[k].ndim == 2 and k != 'klassen'}
        return self._masken[datei]

    def klassen(self, datei):
        """(H, W) uint8 — Sapiens-Klasse je Pixel (Index in SAPIENS), oder None."""
        pfad = self._ablage(datei)
        if pfad is None:
            return None
        with Npztorch.lesen_numpy(pfad) as z:
            return z['klassen'] if 'klassen' in z.files else None

    @classmethod
    def klassen_index(cls, *namen):
        return [cls.SAPIENS.index(n) for n in namen]

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
