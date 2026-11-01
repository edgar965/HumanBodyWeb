# -*- coding: utf-8 -*-
"""Ai2d3dteilflaeche — decken Hände und Füße der Genesis-Figur die Hände und Füße im Foto? (30.10.2026, Edgar mit einem Bild der Figur: „hände - finger verdreht und kaputt“,
„Füße vorne kaputt“.)

Je Foto und Teil (Sapiens2-Klassen der linken bzw. rechten Hand, des linken bzw. rechten Fußes samt Socke und Schuh): Umkreis = die Pixel des Teils, um UMKREIS_MM erweitert. Darin
die Person des Fotos gegen die gerasterte Figur (`Ai2d3dgenesisansicht`, alle Stücke):
  fehlt    Pixel des Teils (um BAND_MM eingezogen) ohne Figur — ein Finger, der im Foto woanders liegt
  zuviel   Figur außerhalb der Person (um BAND_MM erweitert)
  kerben   Einschnitte der Figur, die das Foto nicht hat: was ein Schließen mit KERBE_MM an der Figur füllt, am Foto aber nicht (um BAND_MM erweitert) — Zehen, die einzeln aus
           der Socke stehen, ein Finger, der vom Nachbarn absteht
Ein Saum von BAND_MM zählt nicht (den misst der Umriss-Test). Teile unter MIN_MM2 im Foto (verdeckt, im Profil hinter dem Körper) zählen nicht. Grenzen je Teil in mm² (Setzung,
30.10.2026: eine Fingerbreite ~15 mm, ein Fingerglied ~25 mm lang → ein falsch liegendes Glied ~400 mm²).

    erg = Ai2d3dteilflaeche(ansicht).messen('haende')      # [(Foto, Seite, Fläche mm², fehlt, zuviel, kerben)]
"""
import numpy as np
from scipy import ndimage

__all__ = ['Ai2d3dteilflaeche']


class Ai2d3dteilflaeche:
    TEILE = {'haende': {'links': ('Left_Hand',), 'rechts': ('Right_Hand',)},
             'fuesse': {'links': ('Left_Foot', 'Left_Sock', 'Left_Shoe'), 'rechts': ('Right_Foot', 'Right_Sock', 'Right_Shoe')}}
    UMKREIS_MM, BAND_MM, KERBE_MM, MIN_MM2 = 15.0, 1.0, 5.0, 1500.0

    def __init__(self, ansicht):
        self.a = ansicht
        self.p = ansicht.p

    @staticmethod
    def _runde(maske, mm, mm_px, weiter):
        n = int(round(mm / mm_px))
        if n <= 0:
            return maske
        return ndimage.binary_dilation(maske, iterations=n) if weiter else ndimage.binary_erosion(maske, iterations=n)

    @classmethod
    def _kerben(cls, maske, mm_px):
        n = max(1, int(round(cls.KERBE_MM / mm_px)))
        rund = ndimage.generate_binary_structure(2, 1)
        zu = ndimage.binary_closing(np.pad(maske, n), structure=ndimage.iterate_structure(rund, n))[n:-n, n:-n]
        return zu & ~maske

    def messen(self, teil, figur_von=None):
        """`figur_von(nr, f, raster)` ersetzt die Figurmaske (h, w) bool (Gegenproben)."""
        aus = []
        for nr, f in self.p.fotos():
            r = self.a.rastern(nr, f)
            figur = figur_von(nr, f, r) if figur_von else r['stueck'] >= 0
            k = self.p.klassen(f['datei'])
            if k is None:
                continue
            h, w = figur.shape
            k = self.a.verkleinern(k)[:h, :w]
            person = k > 0
            mm_px = self.p.mm_je_px(nr) / self.a.m
            aussen = self._runde(person, self.BAND_MM, mm_px, True)
            kerben = self._kerben(figur, mm_px) & ~self._runde(self._kerben(person, mm_px), self.BAND_MM, mm_px, True)
            for seite, namen in self.TEILE[teil].items():
                stueck = np.isin(k, self.p.klassen_index(*namen))
                flaeche = stueck.sum() * mm_px ** 2
                if flaeche < self.MIN_MM2:
                    continue
                umkreis = self._runde(stueck, self.UMKREIS_MM, mm_px, True)
                fehlt = (self._runde(stueck, self.BAND_MM, mm_px, False) & ~figur).sum() * mm_px ** 2
                zuviel = (umkreis & figur & ~aussen).sum() * mm_px ** 2
                kerbe = (umkreis & kerben).sum() * mm_px ** 2
                aus.append((f['datei'], seite, int(flaeche), int(fehlt), int(zuviel), int(kerbe)))
        return aus
