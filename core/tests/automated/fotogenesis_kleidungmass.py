# -*- coding: utf-8 -*-
"""Fotogenesiskleidungmass — trägt die Genesis-Figur jedes Kleidungsstück dort, wo das Foto es zeigt? (30.10.2026, Edgar mit einem Bild der Figur von hinten: „Unterhose nicht erkannt
(stattdessen T-Shirt an der Stelle gebaut)“.)

Sapiens2 unterscheidet im Foto Oberteil (`Upper_Clothing`), Unterteil (`Lower_Clothing`) und Socken/Schuhe; die Figur zeigt je Art ein eigenes Stück (`ARTEN`, Namen wie in
`genesis` von training_figur.json). Je Foto gerastert (`Fotogenesisgenesisansicht`, Kamera des Fotos) und in Zellen von ZELLE_MM geteilt: Füllt eine Art mindestens MIN_ANTEIL einer
Zelle (Maske um RAND_PX Rasterpixel eingezogen, sonst zählt der Saum), muss die Figur auf mindestens TREFFER dieser Pixel das Stück dieser Art zeigen — sonst ist die Zelle ein Fehler.
Ein Stück ohne Art (`kleid`, Läufe vor dem 30.10.2026) trifft keine.

Sapiens2 irrt sich in einzelnen Fotos: im Profil nennt es Flecken auf Schienbein und Socke „Lower_Clothing“, bis 11.000 mm² groß — größer als ein Teil der Unterhose, die der
Arm verdeckt, also nicht über die Größe zu trennen (`ProjektTemp/_wegwerf/fotogenesis/diag_kleidung_inseln.py`). Eine zusammenhängende Fläche einer Art zählt deshalb nur, wenn die
ANDEREN Fotos sie bestätigen (`einig`): von den Körperpunkten der Figur, die auf die Fläche fallen (alle Schichten — hängt der Arm der Figur davor, zählt das Becken dahinter
mit), nach ihrer Fläche gewichtet (das Genesis-Netz ist an den Händen viel dichter als am Becken), trägt mindestens KONSENS in den anderen Fotos, die sie sehen, mehrheitlich
dieselbe Art. Gemessen an Lauf 01.26 (`diag_kleidung_einig.py`): Kleidung 0,36–0,95, Flecken 0,00–0,17.

    erg = Fotogenesiskleidungmass(ansicht).messen()
    # {'zellen': [(Foto, Art, Mitte px, Anteil getroffen)], 'arten': {Art: Zahl der Zellen mit der Art}, 'uneinig': [(Foto, Art, mm², Mitte px, bestätigt)]}
"""
import numpy as np
from scipy import ndimage

__all__ = ['Fotogenesiskleidungmass']


class Fotogenesiskleidungmass:
    ARTEN = {'oberteil': ('Upper_Clothing',), 'unterteil': ('Lower_Clothing',), 'socken': ('Left_Sock', 'Right_Sock', 'Left_Shoe', 'Right_Shoe')}
    ZELLE_MM, MIN_ANTEIL, TREFFER, RAND_PX = 40.0, 0.4, 0.5, 2
    #: |Normale · Blick| ab dem ein Punkt im Foto zählt — streifend gesehen fällt er auf den Rand der Person und damit oft auf den Hintergrund (wie `Fotogenesisgenesisfarbmass`)
    NEIGUNG = 0.3
    #: bestätigter Anteil, ab dem eine Fläche zählt (Setzung zwischen 0,17 und 0,36, 30.10.2026)
    KONSENS = 0.25

    def __init__(self, ansicht):
        self.a = ansicht
        self.p = ansicht.p
        self._punktarten = None

    def _koerper(self, nr):
        return next((t for t in self.a.stuecke(nr) if t[0] == 'koerper'), None)

    def punktarten(self):
        """{nr: (V,) je Körperpunkt der Figur die Art des Fotos an seinem Bildpunkt — Index in ARTEN, −1 keine Kleidung, −2 im Foto nicht (oder nur streifend) sichtbar}."""
        if self._punktarten is None:
            tabelle = np.full(len(self.p.SAPIENS), -1)
            for i, namen in enumerate(self.ARTEN.values()):
                tabelle[self.p.klassen_index(*namen)] = i
            self._punktarten = {}
            for nr, f in self.p.fotos():
                k, koerper = self.p.klassen(f['datei']), self._koerper(nr)
                if k is None or koerper is None:
                    continue
                uv, z = self.p.projektion(f, koerper[1])
                ix, iy = self.p.pixel(uv, k.shape)
                gut = self.p.sichtbar(uv, z, f, koerper[2]) & (self.a._neigung(koerper[1], koerper[2], np.asarray(f['kamera']['ort'], dtype=np.float64)) >= self.NEIGUNG)
                self._punktarten[nr] = np.where(gut, tabelle[k[iy, ix]], -2)
        return self._punktarten

    @staticmethod
    def _flaeche(x, tri):
        """(V,) Fläche je Punkt (ein Drittel der anliegenden Dreiecke)."""
        fl = np.linalg.norm(np.cross(x[tri[:, 1]] - x[tri[:, 0]], x[tri[:, 2]] - x[tri[:, 0]]), axis=1) / 6
        aus = np.zeros(len(x))
        for j in range(3):
            np.add.at(aus, tri[:, j], fl)
        return aus

    def einig(self, nr, f, art, marke, zahl):
        """(zahl + 1,) je Fläche (`marke` aus ndimage.label im Raster) der bestätigte Anteil für die Art `art` (Index in ARTEN); NaN, wo kein anderes Foto einen ihrer Punkte sieht."""
        andere = [a for n, a in self.punktarten().items() if n != nr]
        koerper = self._koerper(nr)
        if not andere or koerper is None:
            return np.full(zahl + 1, np.nan)
        andere = np.stack(andere)
        gesehen = (andere != -2).sum(0)
        mehr = (gesehen > 0) & (2 * (andere == art).sum(0) >= gesehen)
        uv, _z = self.p.projektion(f, koerper[1])
        ix, iy = np.floor(uv[:, 0] * self.a.m).astype(np.int64), np.floor(uv[:, 1] * self.a.m).astype(np.int64)
        h, w = marke.shape
        drin = (ix >= 0) & (iy >= 0) & (ix < w) & (iy < h)
        auf = np.zeros(len(ix), dtype=np.int64)
        auf[drin] = marke[iy[drin], ix[drin]]
        gew = self._flaeche(koerper[1], koerper[2])
        n = np.bincount(auf[gesehen > 0], gew[gesehen > 0], minlength=zahl + 1)
        ja = np.bincount(auf[mehr], gew[mehr], minlength=zahl + 1)
        return np.where(n > 0, ja / np.maximum(n, 1e-30), np.nan)

    def foto_arten(self, nr, f, form):
        """({Art: (h, w) bool} im Raster — Pixel der Art im Foto, nur bestätigte Flächen, eingezogen; [(Foto, Art, mm², Mitte px, bestätigt)] der verworfenen) oder (None, [])."""
        k = self.p.klassen(f['datei'])
        if k is None:
            return None, []
        k = self.a.verkleinern(k)[:form[0], :form[1]]
        mm2 = (self.p.mm_je_px(nr) / self.a.m) ** 2
        aus, weg = {}, []
        for i, (art, namen) in enumerate(self.ARTEN.items()):
            m = np.isin(k, self.p.klassen_index(*namen))
            marke, zahl = ndimage.label(m)
            if zahl:
                anteil = self.einig(nr, f, i, marke, zahl)
                schlecht = anteil < self.KONSENS
                schlecht[0] = False
                for c in np.nonzero(schlecht)[0]:
                    yx = np.argwhere(marke == c).mean(0) / self.a.m
                    weg.append((f['datei'], art, int((marke == c).sum() * mm2), (int(yx[1]), int(yx[0])), round(float(anteil[c]), 2)))
                m &= ~schlecht[marke]
            aus[art] = ndimage.binary_erosion(m, iterations=self.RAND_PX)
        return aus, weg

    def messen(self, stueck_von=None, namen=None):
        """`stueck_von(nr, f, raster)` ersetzt die Stücke der Figur je Pixel (Gegenproben) — (h, w) Index in `namen` (Vorgabe die der Ansicht) wie `raster['stueck']`."""
        namen = self.a.namen if namen is None else namen
        zellen, arten, uneinig = [], {}, []
        for nr, f in self.p.fotos():
            r = self.a.rastern(nr, f)
            st = stueck_von(nr, f, r) if stueck_von else r['stueck']
            foto, weg = self.foto_arten(nr, f, st.shape)
            if foto is None:
                continue
            uneinig += weg
            zelle = self.a.zellen(nr, st.shape, self.ZELLE_MM)
            px = (self.ZELLE_MM / self.p.mm_je_px(nr) * self.a.m) ** 2
            for art, maske in foto.items():
                figur = st == (namen.index(art) if art in namen else -2)
                n = np.bincount(zelle[maske], minlength=zelle.max() + 1)
                treffer = np.bincount(zelle[maske & figur], minlength=zelle.max() + 1)
                voll = n >= self.MIN_ANTEIL * px
                arten[art] = arten.get(art, 0) + int(voll.sum())
                for z in np.nonzero(voll & (treffer < self.TREFFER * n))[0]:
                    yx = np.argwhere(maske & (zelle == z)).mean(0) / self.a.m
                    zellen.append((f['datei'], art, (int(yx[1]), int(yx[0])), round(float(treffer[z] / n[z]), 2)))
        return {'zellen': zellen, 'arten': arten, 'uneinig': uneinig}
