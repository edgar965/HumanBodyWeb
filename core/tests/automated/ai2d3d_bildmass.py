# -*- coding: utf-8 -*-
"""Ai2d3dbildmass — ein Bild der Figur aus der Kamera eines Fotos gegen das Foto, je Körperteil, das
Sapiens2 im Foto sieht (02.11.2026, Edgar zur Jobseite EdgarTrip: „Textur beine / arme ist kaputt, saum
T-short und hose … Hast du testcases für die Textur und den Saum? erzeuge welche, Die müssen rot sein“ und
„schreibe testcases für die 2. Zeile, das Genesis modell muss viel besser sein als die erste Zeile“).

Dasselbe Maß für beide Zeilen der Seite, damit sie vergleichbar sind: Zeile 1 als Raster der Genesis-Figur der
Mesh-Methode (`Ai2d3dgenesisansicht`), Zeile 2 als Rendering der Seite selbst (`Ai2d3dzeile2.bild`,
`window.__ai2d3d.seitenbilder()`). Beide im Maßstab MASSSTAB des Fotos.

  Gruppen  Pixel des Fotos je GRUPPEN (Sapiens-Klassen, innerhalb der Person), um RAND_PX eingezogen;
           geprüft wird, wo das Bild dort die Figur zeigt (wo es leer ist, ist es eine Frage der Form,
           nicht der Textur — `leer` zählt das mit)
  Abstand  größter Kanal (sRGB) zwischen der Farbe des Bilds und der Farbe des Fotos im Umkreis von
           SPIEL_MM (nur Pixel derselben Gruppe), das kleinste davon; das Foto vorher je Kanal auf die
           Helligkeit des Bilds gebracht (Summenverhältnis über alle Pixel der Person, die das Bild zeigt —
           die Seite rendert unter Licht)
  falsch   Abstand über ABSTAND; eine Zelle von ZELLE_MM mit mindestens ANTEIL falscher Pixel und MIN_MM2
           ist ein Fehler (wie `Ai2d3dgenesisfarbmass`)
  ueber    Pixel der Figur außerhalb der um SPIEL_MM erweiterten Person, der nächsten Gruppe des Fotos
           zugeschlagen (02.11.2026 nachmittags: bis dahin zählte eine Figur, die über die Person hinausragt,
           nirgends — Zeile 2 ragte 5.263 px hinaus, 4.680 davon das Oberteil an den Schultern, Zeile 1 233;
           `ProjektTemp/_wegwerf/ergaenzung/ueberstand_diag.py`)

    erg = Ai2d3dbildmass(probe, lambda nr, f, form: (rgb, figur)).messen()
    # {'gruppen': {Gruppe: {'geprueft', 'falsch', 'leer', 'ueber', 'anteil'}},
    #  'zellen': [(Foto, Gruppe, Mitte px, Anteil, mm²)]}
"""
import numpy as np
from scipy import ndimage

__all__ = ['Ai2d3dbildmass']


class Ai2d3dbildmass:
    MASSSTAB = 0.25
    RAND_PX, SPIEL_MM, ABSTAND = 1, 6.0, 60
    ZELLE_MM, ANTEIL, MIN_MM2 = 30.0, 0.3, 150.0
    GRUPPEN = {'arme': ('Left_Upper_Arm', 'Left_Lower_Arm', 'Right_Upper_Arm', 'Right_Lower_Arm'),
               'beine': ('Left_Upper_Leg', 'Left_Lower_Leg', 'Right_Upper_Leg', 'Right_Lower_Leg'),
               'haende': ('Left_Hand', 'Right_Hand'), 'gesicht': ('Face_Neck',), 'haar': ('Hair',),
               'oberteil': ('Upper_Clothing',), 'unterteil': ('Lower_Clothing',),
               'socken': ('Left_Sock', 'Right_Sock', 'Left_Shoe', 'Right_Shoe')}

    def __init__(self, probe, bilder):
        """`bilder(nr, f, (h, w))` → (rgb (h, w, 3) sRGB 0–255, figur (h, w) bool) — das Bild der Figur im
        Foto `nr` im Maßstab MASSSTAB, oder None."""
        self.p = probe
        self.bilder = bilder

    def verkleinern(self, feld, mittel=False):
        q = int(round(1 / self.MASSSTAB))
        h, w = feld.shape[0] // q, feld.shape[1] // q
        if mittel:
            return feld[:h * q, :w * q].reshape(h, q, w, q, *feld.shape[2:]).mean((1, 3))
        return feld[q // 2::q, q // 2::q][:h, :w]

    def foto(self, f):
        """(Foto (h, w, 3), Klassen (h, w), Person (h, w)) im Maßstab, oder None ohne Segmente."""
        m, k = self.p.masken(f['datei']), self.p.klassen(f['datei'])
        if m is None or k is None:
            return None
        bild = self.verkleinern(self.p.bild(f['datei']).astype(np.float64), mittel=True)
        return bild, self.verkleinern(k), self.verkleinern(m['person'])

    def _scheibe(self, nr):
        rad = max(1, int(round(self.SPIEL_MM / (self.p.mm_je_px(nr) / self.MASSSTAB))))
        dy, dx = np.meshgrid(np.arange(-rad, rad + 1), np.arange(-rad, rad + 1), indexing='ij')
        rund = dy ** 2 + dx ** 2 <= rad ** 2
        return dy[rund], dx[rund]

    def je_foto(self, nr, f):
        """{Gruppe: (geprüft, falsch, leer, über — je (h, w) bool)} des Fotos, oder None."""
        fo = self.foto(f)
        if fo is None:
            return None
        bild, kl, person = fo
        h, w = kl.shape
        b = self.bilder(nr, f, (h, w))
        if b is None:
            return None
        rgb, figur = b
        rgb, figur = rgb[:h, :w].astype(np.float64), figur[:h, :w]
        auf = person & figur
        gain = rgb[auf].sum(0) / np.maximum(bild[auf].sum(0), 1e-6) if auf.any() else np.ones(3)
        ziel = bild * gain
        dy, dx = self._scheibe(nr)
        ueber = figur & ~ndimage.binary_dilation(person, iterations=int(np.abs(dy).max()))
        gruppe = np.full((h, w), -1)
        for i, namen in enumerate(self.GRUPPEN.values()):
            gruppe[np.isin(kl, self.p.klassen_index(*namen)) & person] = i
        quelle = ndimage.distance_transform_edt(gruppe < 0, return_distances=False, return_indices=True)
        naechste = gruppe[tuple(quelle)]
        aus = {}
        for i, (g, namen) in enumerate(self.GRUPPEN.items()):
            maske = np.isin(kl, self.p.klassen_index(*namen)) & person
            if not maske.any():
                continue
            innen = ndimage.binary_erosion(maske, iterations=self.RAND_PX)
            pruef = innen & figur
            d = np.full((h, w), np.inf)
            iy, ix = np.nonzero(pruef)
            for oy, ox in zip(dy, dx, strict=True):
                qy, qx = (iy + oy).clip(0, h - 1), (ix + ox).clip(0, w - 1)
                e = np.abs(rgb[iy, ix] - ziel[qy, qx]).max(1)
                d[iy, ix] = np.minimum(d[iy, ix], np.where(maske[qy, qx], e, np.inf))
            aus[g] = (pruef, pruef & (d > self.ABSTAND), innen & ~figur, ueber & (naechste == i))
        return aus

    def zellen(self, nr, form):
        px = self.ZELLE_MM / self.p.mm_je_px(nr) * self.MASSSTAB
        h, w = form
        zy, zx = np.meshgrid(np.arange(h) // px, np.arange(w) // px, indexing='ij')
        return (zy * (w // px + 2) + zx).astype(np.int64)

    def messen(self):
        gruppen, zellen = {}, []
        for nr, f in self.p.fotos():
            je = self.je_foto(nr, f)
            if je is None:
                continue
            mm_px = self.p.mm_je_px(nr) / self.MASSSTAB
            for g, (pruef, falsch, leer, ueber) in je.items():
                s = gruppen.setdefault(g, {'geprueft': 0, 'falsch': 0, 'leer': 0, 'ueber': 0})
                s['geprueft'] += int(pruef.sum())
                s['falsch'] += int(falsch.sum())
                s['leer'] += int(leer.sum())
                s['ueber'] += int(ueber.sum())
                zelle = self.zellen(nr, pruef.shape)
                n = np.bincount(zelle[pruef], minlength=zelle.max() + 1)
                b = np.bincount(zelle[falsch], minlength=zelle.max() + 1)
                fehler = (b >= self.ANTEIL * np.maximum(n, 1)) & (b * mm_px ** 2 >= self.MIN_MM2)
                for z in np.nonzero(fehler)[0]:
                    yx = np.argwhere(falsch & (zelle == z)).mean(0) / self.MASSSTAB
                    zellen.append((f['datei'], g, (int(yx[1]), int(yx[0])), round(float(b[z] / n[z]), 2),
                                   int(b[z] * mm_px ** 2)))
        for s in gruppen.values():
            s['anteil'] = s['falsch'] / max(s['geprueft'], 1)
        return {'gruppen': gruppen, 'zellen': sorted(zellen, key=lambda z: -z[4])}
