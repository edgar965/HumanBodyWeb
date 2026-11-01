# -*- coding: utf-8 -*-
"""Die Socken der Genesis-Figur der Mesh-Methode (Jobseite, oberste Zeile, Feld 3) sind glatt — keine Spalten zwischen den Zehen.

WARUM: Edgar, 30.10.2026, mit einem Bild der Figur von schräg hinten: „Füße vorne kaputt“. Die Socke ist die geometrische Figur (`Genesishuellen`), und die hat vorn die einzelnen
Zehen des Genesis-Netzes; im Foto ist die Socke glatt. Der Test der Hände und Füße (`test_ai2d3d_genesis_haende_fuesse`, Kerben am Umriss) sieht das nicht: im Profil liegen die
Spalten innen, nicht am Umriss — Kerben höchstens 41 mm² bei sichtbar einzelnen Zehen (`diag_durchstoss_bild.py 4 0`, Lauf 09.22).
Gemessen vorher mit diesem Maß (`diag_sockenspalt_mass.py`, Lauf 09.22): je Socke 1.070–1.882 mm² ungeglättet, 410–504 mm² mit 40 Runden Taubin und einmal Schließen.

Maß: `Ai2d3dsockenspalt` (σ 8 mm, tiefer als 2 mm, ohne 10 mm am Rand). Grenze je Socke und Foto (Setzung 30.10.2026): 150 mm² — eine Spalte von etwa 4 × 40 mm.

    manage.py test core.tests.automated.test_ai2d3d_genesis_socke
"""
import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from .ai2d3d_figurprobe import Ai2d3dfigurprobe
from .ai2d3d_sockenspalt import Ai2d3dsockenspalt


class Ai2d3dGenesisSocke(SimpleTestCase):
    databases = set()
    JOB = 'EdgarTrip'
    GRENZE_MM2 = 150

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.probe = Ai2d3dfigurprobe(settings.OBJECTS_ROOT, cls.JOB)
        cls.mass = Ai2d3dsockenspalt()

    def _socken(self):
        g = (self.probe.figur or {}).get('genesis') or {}
        s = g.get('socken')
        if not s:
            self.skipTest('kein Lauf mit Socken an der Genesis-Figur: training_figur.json ohne genesis.socken')
        tri = self.probe.feld(s['dreiecke'], '<u4', 3).astype(np.int64)
        return {nr: (self.probe.feld(t, '<f4', 3), tri) for nr, t in sorted(s['fotos'].items())}

    def test_socken_ohne_spalten(self):
        werte = {nr: self.mass.messen(x, tri) for nr, (x, tri) in self._socken().items()}
        self.assertTrue(all(len(w) >= 2 for w in werte.values()), 'nicht zwei Socken je Foto: %s' % werte)
        schlecht = {nr: w for nr, w in werte.items() if any(s > self.GRENZE_MM2 for _f, s, _t in w)}
        self.assertFalse(schlecht, 'Lauf %s, Grenze %d mm² je Socke — (Fläche, Spalten, tiefste mm) je Foto: %s' % (self.probe.figur['lauf'], self.GRENZE_MM2, werte))

    def test_gegenprobe_glatte_kunstsocke_besteht(self):
        self.assertEqual([s for _f, s, _t in self.mass.messen(*Ai2d3dsockenspalt.kunstsocke())], [0])

    def test_gegenprobe_kunstsocke_mit_rillen_faellt_durch(self):
        """Eine Rille von 4 mm Tiefe, 4 mm Breite und 65 mm Länge vorn — wie eine Spalte zwischen zwei Zehen."""
        w = self.mass.messen(*Ai2d3dsockenspalt.kunstsocke(rillen=1, breite_mm=4.0))
        self.assertGreater(w[0][1], self.GRENZE_MM2, w)

    def test_gegenprobe_rand_zaehlt_nicht(self):
        """Eine offene Socke (Kunstsocke ohne die hintere Hälfte) — der Rand zieht beim Glätten nach innen und darf keine Spalte sein."""
        x, tri = Ai2d3dsockenspalt.kunstsocke()
        tri = tri[(x[tri][:, :, 0] > -0.03).all(1)]
        self.assertEqual([s for _f, s, _t in self.mass.messen(x, tri)], [0])
