# -*- coding: utf-8 -*-
"""Ai2d3dtexturmass — „Hintergrund in der Textur“ einer Figur gegen die Fotos (29.10.2026 abends, Edgar mit einem Bild der geometrischen Figur: weiße Fingerspitzen, weißer Fleck
an der Wölbung — „testcase für textur in der Mesherzeugung und fixen (z.B. handtextur ist falsch)“).

Ein Punkt hat seine Farbe aus dem Hintergrund, wenn er in einem Foto sichtbar DEUTLICH neben der Person liegt (Personenmaske um RAND_PX erweitert) und seine Farbe der Farbe des
Fotos dort um mindestens MARGE näher ist als jeder Farbe, die er in einem Foto AUF der Person hat (Maske um RAND_PX eingezogen, sichtbar) — und Hintergrund und Person dort
unterscheidbar sind (mindestens TRENN). Abstand zweier Farben = größter Kanal (sRGB 0–255). Punkte ohne Foto, das sie auf der Person zeigt, zählen nicht (nicht zu beurteilen).
Gezählt je Zelle von ZELLE_MM im Foto, in dem der Punkt neben der Person liegt: eine Zelle mit mindestens MIN_PUNKTE solchen Punkten ist ein Fehler — örtlich wie der Umriss-Test.

    erg = Ai2d3dtexturmass(probe).messen(farben)      # {'punkte': n, 'zellen': [(Foto, (x, y) px, Zahl)]}
"""
import numpy as np
from scipy import ndimage

__all__ = ['Ai2d3dtexturmass']


class Ai2d3dtexturmass:
    RAND_PX, MARGE, TRENN, ZELLE_MM, MIN_PUNKTE = 3, 10, 40, 60.0, 5

    def __init__(self, probe):
        self.p = probe

    def _je_foto(self):
        """{Foto: (uv, sichtbar, Farbe des Fotos je Punkt, auf der Person, deutlich daneben, mm/px)}."""
        aus = {}
        for nr, f in self.p.fotos():
            m = self.p.masken(f['datei'])
            if m is None:
                continue
            x = self.p.punkte(f)
            uv, z = self.p.projektion(f, x)
            sb = self.p.sichtbar(uv, z, f)
            ix, iy = self.p.pixel(uv, m['person'].shape)
            innen = ndimage.binary_erosion(m['person'], iterations=self.RAND_PX)[iy, ix]
            daneben = ~ndimage.binary_dilation(m['person'], iterations=self.RAND_PX)[iy, ix]
            aus[f['datei']] = (uv, sb, self.p.bild(f['datei'])[iy, ix], sb & innen, sb & daneben, self.p.mm_je_px(nr))
        return aus

    def messen(self, farben):
        """`farben` (N, 3) Farben der Figur je Punkt (sRGB) → {'punkte': Zahl der Punkte mit Hintergrundfarbe, 'zellen': [(Foto, Mitte px, Zahl)] mit ≥ MIN_PUNKTE}."""
        je = self._je_foto()
        c = np.asarray(farben, dtype=np.int64)
        n = len(c)
        # je Punkt der kleinste Abstand seiner Farbe zu einer Fotofarbe AUF der Person, und die Fotofarben dazu
        zur_person = np.full(n, np.inf)
        auf = []
        for (_uv, _sb, foto, innen, _d, _mm) in je.values():
            d = np.where(innen[:n], np.abs(c - foto[:n]).max(1), np.inf)
            zur_person = np.minimum(zur_person, d)
            auf.append((innen[:n], foto[:n]))
        gesamt, zellen = np.zeros(n, dtype=bool), []
        for datei, (uv, _sb, foto, _innen, daneben, mm) in je.items():
            hg = foto[:n]
            trenn = np.full(n, np.inf)
            for innen, fp in auf:
                trenn = np.minimum(trenn, np.where(innen, np.abs(fp - hg).max(1), np.inf))
            schlecht = daneben[:n] & np.isfinite(zur_person) & (np.abs(c - hg).max(1) + self.MARGE <= zur_person) & (trenn >= self.TRENN)
            gesamt |= schlecht
            if schlecht.any():
                z = np.floor(uv[:n][schlecht] / (self.ZELLE_MM / mm)).astype(np.int64)
                for zelle, zahl in zip(*np.unique(z, axis=0, return_counts=True), strict=True):
                    if zahl >= self.MIN_PUNKTE:
                        zellen.append((datei, tuple(((zelle + 0.5) * self.ZELLE_MM / mm).round().astype(int).tolist()), int(zahl)))
        return {'punkte': int(gesamt.sum()), 'zellen': sorted(zellen, key=lambda z: -z[2])}
