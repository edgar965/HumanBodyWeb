# -*- coding: utf-8 -*-
"""Jeder sichtbare Punkt der Genesis-Figur der Mesh-Methode (Jobseite, oberste Zeile, Feld 3) hat die Farbe, die die Fotos an ihm zeigen — Haut wie die Haut, Hemd wie das Hemd.

WARUM: Edgar, 30.10.2026, mit einem Bild der Figur von schräg hinten (Lauf 2026.10.29.23.02): „Textur T-Shirt hinten kaputt“, „Textur an den Armen seitlich kaputt (schwarzer
streifen)“, „texturfehler am Hals und oberen T-shirt (weisse flecken)“. Nachgestellt (`ProjektTemp/_wegwerf/ai2d3d/diag_genesis_ansicht.py 3 --dreh=-35`): der Rand des Unterarms
holte im Profilfoto das Hemd dahinter (die Figur steht dort ein paar mm anders als die Person), die Seite des Rumpfs den Arm davor, und der Körper schien mit seinen eigenen Farben
durch das Hemd (`test_ai2d3d_genesis_durchstoss`).

Maß: `Ai2d3dgenesisfarbmass` — je Punkt, der in einer Ansicht (Foto, ±45°) zu sehen ist: Abstand zur Farbe der Fotos, die ihn sehen und dort DIESELBE Klasse zeigen (größter Kanal,
4 mm Spiel; ohne die Klasse dort bis 40 mm daneben); über 70 ist er falsch gefärbt. Zeigt ihn kein Foto, gilt der Abstand zu den Fotofarben seiner Nachbarn im selben Stück
(30 mm) — so fallen die geratenen Farben auf (Lauf 08.24: weiße Flecken an der Hüfte, Farbe der Tür hinter dem Rumpf). Fehler = Zelle von 30 mm mit mindestens 30 % falscher
Pixel und 150 mm².

    manage.py test core.tests.automated.test_ai2d3d_genesis_farbe
"""
import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from .ai2d3d_figurprobe import Ai2d3dfigurprobe
from .ai2d3d_genesisansicht import Ai2d3dgenesisansicht
from .ai2d3d_genesisfarbmass import Ai2d3dgenesisfarbmass


class Ai2d3dGenesisFarbe(SimpleTestCase):
    databases = set()
    JOB = 'EdgarTrip'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.probe = Ai2d3dfigurprobe(settings.OBJECTS_ROOT, cls.JOB)
        cls.ansicht = Ai2d3dgenesisansicht(cls.probe) if cls.probe.figur and cls.probe.figur.get('genesis') else None
        cls._erg = None

    def _mass(self):
        if self.ansicht is None or self.probe.training is None:
            self.skipTest('kein Lauf mit Genesis-Figur: training_figur.json ohne genesis')
        self.assertTrue(self.ansicht.g.get('farben'), 'Genesis-Figur ohne Farben')
        return Ai2d3dgenesisfarbmass(self.ansicht)

    def _messen(self):
        if type(self)._erg is None:
            type(self)._erg = self._mass().messen()
        return type(self)._erg

    @staticmethod
    def _text(erg):
        return '%d von %d geprüften Punkten falsch gefärbt; Zellen: %s' % (erg['punkte'], erg['geprueft'], '; '.join(
            '%s %+d° bei %s px Anteil %.2f, %d mm²' % z for z in erg['zellen'][:10]))

    def test_jeder_sichtbare_punkt_hat_die_farbe_der_fotos(self):
        erg = self._messen()
        self.assertGreater(erg['geprueft'], 1000, self._text(erg))
        self.assertFalse(erg['zellen'], 'Lauf %s — %s' % (self.probe.figur['lauf'], self._text(erg)))

    def _fotofarben(self):
        """{Stück: (N, 3)} — je Punkt die Fotofarbe, Punkte ohne Foto die ihres nächsten Punkts mit Foto (so füllte ein richtiges Auffüllen)."""
        from scipy.spatial import cKDTree
        ff, aus = self._messen()['fotofarbe'], {}
        for name, x, _tri, _fa in self.ansicht.stuecke(self.probe.fotos()[0][0]):
            if name not in ff:
                continue
            mit = ~np.isnan(ff[name]).any(1)
            aus[name] = ff[name].copy()
            if mit.any() and not mit.all():
                aus[name][~mit] = ff[name][mit][cKDTree(x[mit]).query(x[~mit])[1]]
        return aus

    def test_gegenprobe_fotofarben_als_figurfarben_besteht(self):
        mass = self._mass()
        ff = self._fotofarben()
        erg = mass.messen(lambda name, fa: np.where(np.isnan(ff[name]), fa, ff[name]) if name in ff else fa)
        self.assertFalse(erg['zellen'], self._text(erg))

    def test_gegenprobe_ungesehene_punkte_hell_fallen_durch(self):
        """Die Punkte der Kleidung, die kein Foto zeigt, weiß (wie die Flecken an der Hüfte, deren Farbe geraten ist) — sonst richtig gefärbt; muss durchfallen."""
        mass = self._mass()
        ff, roh = self._fotofarben(), self._messen()['fotofarbe']
        kleid = ('oberteil', 'unterteil', 'socken', 'kleid')
        erg = mass.messen(lambda n, fa: np.where(np.isnan(roh[n]), 250.0 if n in kleid else ff[n], ff[n]) if n in ff else fa)
        self.assertTrue(erg['zellen'], self._text(erg))

    def test_gegenprobe_heller_fleck_faellt_durch(self):
        """Ein weißer Fleck von 160 mm auf dem größten Kleidungsstück (wie die Flecken an Hals und Schulter) — muss durchfallen."""
        mass = self._mass()
        nr = self.probe.fotos()[0][0]
        name, x, _tri, _fa = max((t for t in self.ansicht.stuecke(nr) if t[0] != 'koerper'), key=lambda t: len(t[1]))
        # Mitte auf einem Punkt des Stücks: der Schwerpunkt zweier Socken liegt zwischen den Füßen, dort wäre der Fleck leer (30.10.2026, seit die Socken das Stück mit den
        # meisten Punkten sind)
        mitte = x[np.linalg.norm(x - x.mean(0), axis=1).argmin()]
        fleck = np.linalg.norm(x - mitte, axis=1) < 0.08
        self.assertGreater(int(fleck.sum()), 50, '%s: Fleck ohne Punkte' % name)
        erg = mass.messen(lambda n, fa: np.where(fleck[:, None], 250.0, fa) if n == name else fa)
        self.assertTrue(erg['zellen'], '%s: %s' % (name, self._text(erg)))
