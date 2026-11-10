# -*- coding: utf-8 -*-
"""Fotogenesisgenesisansicht — die Genesis-Figur der Mesh-Methode (`genesis` in `<Job>/abnahme/training_figur.json`, `mesh_auf_genesis.figur_eintragen`: Körper und die Stücke
Augen, Haar, Kleidung) je Foto in dessen Kamera gerastert, wie die Jobseite sie zeigt (30.10.2026, Edgar mit einem Bild der Figur von hinten: „Textur T-Shirt hinten kaputt“,
„Textur an den Armen seitlich kaputt“, „texturfehler am Hals“ — „die du erst per testcase feststellen sollst“). Nur numpy, nur lesen.

Je Pixel (im Maßstab MASSSTAB des Fotos) das vorderste Stück: Tiefenpuffer über die dicht abgetasteten Dreiecke (wie `Fotogenesisfigurprobe.sichtbar`, hier je Pixel), Farbe baryzentrisch
aus den Farben der Ecken, der Punkt mit dem größten Anteil und |Normale · Blick| an ihm (`neigung`, 0 = streifend).

    a = Fotogenesisgenesisansicht(probe)
    r = a.rastern(nr, f)       # {'stueck', 'punkt', 'farbe', 'tiefe', 'neigung'}: (h, w) je Pixel; stueck −1 = leer, sonst Index in a.namen
    r = a.rastern(nr, f, a.gedreht(nr, f, 45))      # die Figur um die Hochachse der Kamera gedreht (Schrägansicht ohne Foto)
"""
import numpy as np

__all__ = ['Fotogenesisgenesisansicht']


class Fotogenesisgenesisansicht:
    MASSSTAB = 0.25
    #: die Stücke wie die Seite (`Fotogenesismeshfigur.STUECKE`) — der Körper heißt 'koerper'; Kleidung seit 30.10.2026 je Art (`mesh_auf_genesis.huellen`), 'kleid' = ältere Läufe
    STUECKE = ('augen', 'haar', 'kleid', 'oberteil', 'unterteil', 'socken')

    def __init__(self, probe, massstab=None):
        self.p = probe
        self.g = (probe.figur or {}).get('genesis')
        self.m = self.MASSSTAB if massstab is None else massstab
        self.namen = ['koerper'] + [s for s in self.STUECKE if self.g and self.g.get(s)]
        self._raster = {}

    def stuecke(self, nr):
        """[(Name, Punkte (N, 3), Dreiecke (T, 3), Farben (N, 3) oder None)] der Figur im Foto `nr`."""
        g, aus = self.g, []
        for name in self.namen:
            e = g if name == 'koerper' else g[name]
            if str(nr) not in e.get('fotos', {}):
                continue
            x = self.p.feld(e['fotos'][str(nr)], '<f4', 3).astype(np.float64)
            fa = self.p.feld(e['farben'], 'u1', 3).astype(np.float64) if e.get('farben') else None
            aus.append((name, x, self.p.feld(e['dreiecke'], '<u4', 3).astype(np.int64), fa))
        return aus

    def gedreht(self, nr, f, grad, teile=None):
        """Die Stücke um die Hochachse der Kamera (`oben`) durch die Mitte des Körpers gedreht — Schrägansichten wie auf der Seite."""
        oben = np.asarray(f['kamera']['oben'], dtype=np.float64)
        oben /= np.linalg.norm(oben)
        teile = self.stuecke(nr) if teile is None else teile
        mitte = teile[0][1].mean(0)
        w = np.radians(grad)
        k = np.array([[0, -oben[2], oben[1]], [oben[2], 0, -oben[0]], [-oben[1], oben[0], 0]])
        r = np.eye(3) + np.sin(w) * k + (1 - np.cos(w)) * k @ k
        return [(n, (x - mitte) @ r.T + mitte, tri, fa) for n, x, tri, fa in teile]

    @staticmethod
    def _bary(s):
        a, b = np.meshgrid(np.arange(s + 1), np.arange(s + 1), indexing='ij')
        gut = a + b <= s
        return np.stack([a[gut], b[gut], s - a[gut] - b[gut]], 1) / s

    def _gruppen(self, uv, tri):
        """[(Dreiecke, baryzentrische Abtastung)] — je Dreieck so dicht, dass die Abtastpunkte höchstens ~0,7 Pixel auseinander liegen (Zweierpotenzen, höchstens 64): mit
        fester Dichte blieben Pixel leer, und dahinter liegende Flächen schienen durch (die Augen durch den Hinterkopf)."""
        e = uv[tri] * self.m
        lang = np.max([np.linalg.norm(e[:, i] - e[:, (i + 1) % 3], axis=1) for i in range(3)], axis=0)
        s = 2 ** np.ceil(np.log2(np.clip(lang * 1.5, 1, 64))).astype(np.int64)
        return [(tri[s == k], self._bary(int(k))) for k in np.unique(s)]

    def _proben(self, uv, z, tri, bary, h, w):
        """Je Abtastpunkt (Pixelindex, Tiefe, Dreieck, Abtastnummer) — nur im Bild und vor der Kamera."""
        p_uv = np.einsum('kj,tjc->tkc', bary, uv[tri]).reshape(-1, 2) * self.m
        p_z = np.einsum('kj,tj->tk', bary, z[tri]).reshape(-1)
        ix, iy = np.floor(p_uv[:, 0]).astype(np.int64), np.floor(p_uv[:, 1]).astype(np.int64)
        gut = (ix >= 0) & (iy >= 0) & (ix < w) & (iy < h) & (p_z > 0)
        k = len(bary)
        nr = np.nonzero(gut)[0]
        return iy[gut] * w + ix[gut], p_z[gut], nr // k, nr % k

    @staticmethod
    def _neigung(x, tri, ort):
        """(N,) |Normale · Blick| je Punkt (Normale = Mittel der anliegenden Dreiecke)."""
        n = np.cross(x[tri[:, 1]] - x[tri[:, 0]], x[tri[:, 2]] - x[tri[:, 0]])
        vn = np.zeros_like(x)
        for i in range(3):
            np.add.at(vn, tri[:, i], n)
        vn /= np.linalg.norm(vn, axis=1, keepdims=True).clip(1e-12)
        blick = ort - x
        blick /= np.linalg.norm(blick, axis=1, keepdims=True).clip(1e-12)
        return np.abs((vn * blick).sum(1))

    def rastern(self, nr, f, stuecke=None):
        """Raster der Figur im Foto `nr` (Eintrag `f` aus `probe.fotos()`); `stuecke` ersetzt die Stücke (Schrägansichten, Gegenproben)."""
        if stuecke is None:
            if nr not in self._raster:
                self._raster[nr] = self.rastern(nr, f, self.stuecke(nr))
            return self._raster[nr]
        h, w = int(f['kamera']['hoehe'] * self.m), int(f['kamera']['breite'] * self.m)
        teile = stuecke
        ort = np.asarray(f['kamera']['ort'], dtype=np.float64)
        proj = []
        for name, x, tri, fa in teile:
            uv, z = self.p.projektion(f, x)
            proj.append((name, uv, z, self._gruppen(uv, tri), fa, self._neigung(x, tri, ort)))
        vorn = np.full(h * w, np.inf)
        for _n, uv, z, gruppen, _fa, _ng in proj:
            for tri, bary in gruppen:
                schritt = max(1, 400000 // len(bary))
                for i in range(0, len(tri), schritt):
                    pix, pz, _t, _k = self._proben(uv, z, tri[i:i + schritt], bary, h, w)
                    np.minimum.at(vorn, pix, pz)
        stueck, punkt, farbe, neigung = np.full(h * w, -1), np.full(h * w, -1), np.zeros((h * w, 3)), np.zeros(h * w)
        for name, uv, z, gruppen, fa, ng in proj:
            si = self.namen.index(name) if name in self.namen else len(self.namen)
            for tri, bary in gruppen:
                schritt = max(1, 400000 // len(bary))
                for i in range(0, len(tri), schritt):
                    t = tri[i:i + schritt]
                    pix, pz, ti, ki = self._proben(uv, z, t, bary, h, w)
                    vor = pz <= vorn[pix] + 1e-6
                    pix, ti, ki = pix[vor], ti[vor], ki[vor]
                    stueck[pix] = si
                    punkt[pix] = t[ti, bary[ki].argmax(1)]
                    neigung[pix] = np.einsum('nj,nj->n', bary[ki], ng[t[ti]])
                    if fa is not None:
                        farbe[pix] = np.einsum('nj,njc->nc', bary[ki], fa[t[ti]])
        return {'stueck': stueck.reshape(h, w), 'punkt': punkt.reshape(h, w), 'farbe': farbe.reshape(h, w, 3), 'tiefe': vorn.reshape(h, w),
                'neigung': neigung.reshape(h, w)}

    def verkleinern(self, feld, mittel=False):
        """Foto-großes Feld (H, W[, 3]) auf das Raster: `mittel` = Flächenmittel (Farben), sonst der Pixel in der Zellmitte (Masken, Klassen)."""
        q = int(round(1 / self.m))
        h, w = feld.shape[0] // q, feld.shape[1] // q
        if mittel:
            return feld[:h * q, :w * q].reshape(h, q, w, q, *feld.shape[2:]).mean((1, 3))
        return feld[q // 2::q, q // 2::q][:h, :w]

    def zellen(self, nr, form, zelle_mm):
        """(h, w) Zellnummer je Pixel des Rasters — Zellen von `zelle_mm` im Foto `nr` (mm/px aus training.json)."""
        px = zelle_mm / self.p.mm_je_px(nr) * self.m
        h, w = form
        zy, zx = np.meshgrid(np.arange(h) // px, np.arange(w) // px, indexing='ij')
        return (zy * (w // px + 2) + zx).astype(np.int64)
