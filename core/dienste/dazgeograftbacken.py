# -*- coding: utf-8 -*-
"""Dazgeograftbacken — Farbe, Rauheit und Normalen der Original-Scham auf das angepasste Daz-Geograft übertragen (10.10.2026).

Das angepasste Netz (`Dazgeograftanpassung`) hat die Form des Originals nur in groben Zügen (Punktabstand ≈ 4 mm gegen ≈ 1 mm des Originals). Was darunter liegt, holt der Bake:

    Farbe, Rauheit  je Texel der nächste Punkt der Original-Scham (`Dazgeograftziel`, Atlas aus der Originaltextur); weiter als `NAH_M` weg (Rand des Originals, dort geht die
                    Scham in die Haut über) blendet es bis `FERN_M` in die gebackene Hauttextur der Figur über (`haut_<kachel>_<kanal>.klein.jpg`, gleiche Quelle)
    Normalen        die Normale des Originals am nächsten Punkt, in den Tangentenraum des Geografts umgerechnet (OpenGL, G nach +v): die Falten, die das grobe Netz nicht trägt, stehen
                    als Normalenkarte darauf. Wo das Original fehlt, bleibt die glatte Normale des Netzes (flach)
Texel ohne Dreieck füllen sich vom Rand her (`Dazgeograftraster.auffuellen`). Ergebnis: Dateien in `ausgabe`, dazu ein Bericht mit Zahlen.
"""
import numpy as np

from .dazgeograftraster import Dazgeograftraster

__all__ = ['Dazgeograftbacken']


class Dazgeograftbacken:
    #: Abstand zum Original (m): bis `NAH_M` gilt nur dessen Atlas, bis `FERN_M` blendet die Haut der Figur dazu.
    NAH_M, FERN_M = 0.004, 0.009
    #: Umkreis (m) um die Mitte des Lochs, dessen Hautdreiecke als Quelle der Hautfarbe zählen.
    HAUT_UMKREIS_M = 0.14
    #: Größte Neigung (Grad) der gebackenen Normale gegen die glatte des Geografts.
    MAX_NEIGUNG_GRAD = 60.0

    def __init__(self, ziel, figur, haut_ordner, aufloesung=1024):
        """`ziel`: `Dazgeograftziel`; `figur`: `{punkte, dreiecke, uv, kachel}` der Figur (`Dazgeografthaut.grundfigur`); `haut_ordner`: Ordner der gebackenen `haut_*`-Bilder."""
        import trimesh

        self.ziel, self.figur, self.haut_ordner, self.r = ziel, figur, haut_ordner, int(aufloesung)
        self.ziel_netz = trimesh.Trimesh(ziel.punkte, ziel.dreiecke, process=False)
        self._haut = {}

    # ------------------------------------------------------------ Hilfen

    @staticmethod
    def _abtasten(bild, uv):
        """`(M, 3)` Werte des Bildes (H, W, 3) an `uv` (v nach oben), bilinear."""
        from scipy.ndimage import map_coordinates

        h, w = bild.shape[:2]
        koordinaten = [(1.0 - uv[:, 1]) * h - 0.5, uv[:, 0] * w - 0.5]
        return np.column_stack([map_coordinates(bild[..., k].astype(np.float32), koordinaten, order=1, mode='nearest') for k in range(3)]).astype(np.float64)

    @staticmethod
    def _baryzentrisch(netz, dreieck, punkte):
        import trimesh

        return trimesh.triangles.points_to_barycentric(netz.triangles[dreieck], punkte)

    def _kachelbild(self, kachel, kanal):
        from PIL import Image

        schluessel = (int(kachel), kanal)
        if schluessel not in self._haut:
            pfad = self.haut_ordner / ('haut_%d_%s.klein.jpg' % schluessel)
            self._haut[schluessel] = np.asarray(Image.open(pfad).convert('RGB')) if pfad.is_file() else None
        return self._haut[schluessel]

    def _hautwerte(self, punkte, kanal, mitte):
        """Der Wert der gebackenen Hauttextur `kanal` am nächsten Punkt der Figurfläche um `mitte` → `(M, 3)`."""
        import trimesh

        f = self.figur
        nah = np.flatnonzero(np.linalg.norm(f['punkte'][f['dreiecke']].mean(axis=1) - mitte, axis=1) < self.HAUT_UMKREIS_M)
        netz = trimesh.Trimesh(f['punkte'], f['dreiecke'][nah], process=False)
        stelle, _abstand, dreieck = trimesh.proximity.closest_point(netz, punkte)
        bary = self._baryzentrisch(netz, dreieck, stelle)
        ecken = f['dreiecke'][nah][dreieck]
        uv = np.einsum('mk,mkj->mj', bary, f['uv'][ecken])
        kachel = f['kachel'][nah][dreieck]
        aus = np.full((len(punkte), 3), 128.0)
        for k in np.unique(kachel):
            bild = self._kachelbild(k, kanal)
            if bild is not None:
                m = kachel == k
                aus[m] = self._abtasten(bild, uv[m])
        return aus

    # ------------------------------------------------------------ Bake

    def backen(self, punkte, dreiecke, uv_ecken, ausgabe):
        """Die drei Bilder nach `ausgabe` (Ordner) schreiben → `({kanal: Pfad}, bericht)`."""
        import trimesh

        punkte = np.asarray(punkte, dtype=np.float64)
        dreiecke = np.asarray(dreiecke, dtype=np.int64)
        netz = trimesh.Trimesh(punkte, dreiecke, process=False)
        t = Dazgeograftraster.texel(punkte, dreiecke, uv_ecken, self.r, np.asarray(netz.vertex_normals))
        pos, zeile, spalte = t['position'], t['zeile'], t['spalte']
        stelle, abstand, dreieck = trimesh.proximity.closest_point(self.ziel_netz, pos)
        bary = self._baryzentrisch(self.ziel_netz, dreieck, stelle)
        uv_orig = np.einsum('mk,mkj->mj', bary, self.ziel.uv_ecken[dreieck])
        w = 1.0 - self._glatt((abstand - self.NAH_M) / (self.FERN_M - self.NAH_M))
        mitte = pos.mean(axis=0)
        bericht = {'aufloesung': self.r, 'texel': int(len(pos)), 'original_voll': float((w >= 0.999).mean()), 'abstand_median_mm': round(float(np.median(abstand) * 1000), 2)}
        dateien = {}
        for kanal in ('farbe', 'rauheit'):
            atlas = self.ziel.bild(kanal)
            wert = self._abtasten(atlas, uv_orig) if atlas is not None else np.full((len(pos), 3), 128.0)
            fern = np.flatnonzero(w < 0.999)
            if len(fern):
                haut = self._hautwerte(pos[fern], kanal, mitte)
                if kanal == 'farbe':
                    nah = np.flatnonzero(w >= 0.999)[:20000]
                    bericht['haut_gegen_original'] = round(float(np.abs(self._hautwerte(pos[nah], kanal, mitte) - wert[nah]).mean()), 1) if len(nah) else None
                wert[fern] = w[fern, None] * wert[fern] + (1.0 - w[fern, None]) * haut
            dateien[kanal] = self._schreiben(wert, zeile, spalte, ausgabe / ('baked_%s.%s' % (kanal, 'jpg' if kanal == 'farbe' else 'png')))
        dateien['normalen'] = self._normalen(t, netz, dreieck, bary, w, ausgabe)
        return dateien, bericht

    def _normalen(self, t, netz, dreieck, bary, w, ausgabe):
        """Normalenkarte: Normale des Originals am nächsten Punkt (zur Außenseite des Geografts gedreht), im Tangentenraum des Geografts."""
        n_orig = np.einsum('mk,mkj->mj', bary, np.asarray(self.ziel_netz.vertex_normals)[self.ziel.dreiecke[dreieck]])
        n_orig /= np.maximum(np.linalg.norm(n_orig, axis=1, keepdims=True), 1e-12)
        n_orig *= np.sign(np.einsum('ij,ij->i', n_orig, t['normale']) + 1e-12)[:, None]
        n_welt = w[:, None] * n_orig + (1.0 - w[:, None]) * t['normale']
        n_welt /= np.maximum(np.linalg.norm(n_welt, axis=1, keepdims=True), 1e-12)
        ts = np.column_stack([np.einsum('ij,ij->i', n_welt, t[k]) for k in ('tangente', 'bitangente', 'normale')])
        # Die Neigung gegen die glatte Normale des Geografts ist begrenzt: wo das Original schärfer faltet als das grobe Netz, entstünden sonst Wirbel (am Spalt gesehen).
        neigung = np.hypot(ts[:, 0], ts[:, 1])
        grenze = np.sin(np.radians(self.MAX_NEIGUNG_GRAD))
        ts[:, :2] *= np.minimum(1.0, grenze / np.maximum(neigung, 1e-12))[:, None]
        ts[:, 2] = np.sqrt(np.maximum(1.0 - ts[:, 0] ** 2 - ts[:, 1] ** 2, 0.0))
        return self._schreiben((ts * 0.5 + 0.5) * 255.0, t['zeile'], t['spalte'], ausgabe / 'baked_normalen.png')

    @staticmethod
    def _glatt(x):
        x = np.clip(x, 0.0, 1.0)
        return x * x * (3.0 - 2.0 * x)

    def _schreiben(self, wert, zeile, spalte, pfad):
        from PIL import Image

        bild = np.zeros((self.r, self.r, 3), dtype=np.float64)
        bild[zeile, spalte] = wert
        bild = Dazgeograftraster.auffuellen(bild, zeile, spalte)
        pfad.parent.mkdir(parents=True, exist_ok=True)
        ausgabebild = Image.fromarray(np.clip(bild + 0.5, 0, 255).astype(np.uint8))
        if pfad.suffix == '.jpg':
            ausgabebild.save(pfad, quality=93)
        else:
            ausgabebild.save(pfad)
        return pfad
