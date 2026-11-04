# -*- coding: utf-8 -*-
"""Zeile 2 der Jobseite (Genesis-Modell, Feld 3): Oberteil und Hose haben glatte Säume und keine Löcher — und
glattere als die Zeile 1 (Mesh-Methode).

WARUM: Edgar, 02.11.2026, zur Jobseite EdgarTrip: „saum T-short und hose“ kaputt (Zeile 1: ausgefranste
Kanten am Shirt und an den Hosenbeinen), „das Genesis modell muss viel besser sein als die erste Zeile“.

Maß: `Ai2d3dsaummass` am Netz der Stücke (Zeile 2 `figur/kleider_*/k/*/anzeige/netz.npz`, Zeile 1
`genesis.oberteil/unterteil` in training_figur.json). Gemessen 02.11.2026 mit Glättung 8 mm
(`ProjektTemp/_wegwerf/ergaenzung/zeile2_saum_staende.py`): die Säume der Zeile 1, die Edgar ausgefranst
nennt, Zacken (P95) 2,1–3,3 mm bei 3,5–7,2 % Überlänge; Bund und Ausschnitt der Zeile 2 (Etikett der Fotos,
glatte Kante) 2,6–4,7 mm bei 5,6–33 %; die geraden Schnitte von `Fotosaum` an Ärmeln und Hosenbeinen
0,8–1,15 mm bei 0,6–1,6 %. Grenze dazwischen: ZACKEN_MM, UEBERLAENGE. „Glatter als Zeile 1“ (Setzung): der
schlechteste Saum der Zeile 2 hat höchstens VIEL_BESSER der Zacken und der Überlänge des schlechtesten der
Zeile 1.

    manage.py test core.tests.automated.test_ai2d3d_zeile2_saum
    AI2D3D_TESTJOB=EdgarTrip--<probe> manage.py test …      # einen Probejob (`nurfotos_probejob.py`) prüfen
"""
import os

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from .ai2d3d_figurprobe import Ai2d3dfigurprobe
from .ai2d3d_saummass import Ai2d3dsaummass
from .ai2d3d_zeile2 import Ai2d3dzeile2


class Ai2d3dZeile2Saum(SimpleTestCase):
    databases = set()
    JOB = os.environ.get('AI2D3D_TESTJOB', 'EdgarTrip')
    ZACKEN_MM, UEBERLAENGE, VIEL_BESSER = 1.6, 0.025, 0.5
    #: Art des Stücks in Zeile 2 → Name in Zeile 1
    STUECKE = {'oberteil': 'oberteil', 'hose': 'unterteil'}

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.zeile2 = Ai2d3dzeile2(settings.OBJECTS_ROOT, cls.JOB)
        cls.probe = Ai2d3dfigurprobe(settings.OBJECTS_ROOT, cls.JOB)

    def _zeile2(self):
        aus = {art: self.zeile2.stueck(art) for art in self.STUECKE}
        if not any(t is not None for t in aus.values()):
            self.skipTest('Zeile 2 ohne Oberteil und Hose')
        return {art: Ai2d3dsaummass.messen(*t) for art, t in aus.items() if t is not None}

    def _zeile1(self):
        g = (self.probe.figur or {}).get('genesis')
        if not g:
            self.skipTest('Zeile 1 ohne Genesis-Figur')
        nr, feld = self.probe.fotos()[0][0], self.probe.feld
        aus = {}
        for art, n in self.STUECKE.items():
            if g.get(n):
                punkte, dreiecke = feld(g[n]['fotos'][nr], '<f4', 3), feld(g[n]['dreiecke'], '<u4', 3)
                aus[art] = Ai2d3dsaummass.messen(punkte, dreiecke)
        return aus

    def _schlecht(self, erg):
        return [(art, s) for art, e in erg.items() for s in e['saeume']
                if s['zacken_mm'] > self.ZACKEN_MM or s['verhaeltnis'] - 1 > self.UEBERLAENGE]

    def test_saeume_von_oberteil_und_hose_sind_glatt(self):
        erg = self._zeile2()
        grenze = 'Zacken > %.1f mm oder Überlänge > %.1f %%' % (self.ZACKEN_MM, 100 * self.UEBERLAENGE)
        self.assertFalse(self._schlecht(erg), 'ausgefranste Säume (%s): %s' % (grenze, self._schlecht(erg)))

    def test_oberteil_und_hose_ohne_loecher(self):
        erg = self._zeile2()
        loecher = {art: (e['loecher'], e['loch_mm']) for art, e in erg.items() if e['loecher']}
        self.assertFalse(loecher, 'Löcher (Zahl, Randlänge mm): %s' % loecher)

    def test_saeume_glatter_als_zeile1(self):
        def schlechtester(erg):
            s = [x for e in erg.values() for x in e['saeume']]
            return max(x['zacken_mm'] for x in s), max(x['verhaeltnis'] - 1 for x in s)
        (z1, u1), (z2, u2) = schlechtester(self._zeile1()), schlechtester(self._zeile2())
        text = 'Zeile 1 Zacken %.2f mm, Überlänge %.1f %%; Zeile 2 Zacken %.2f mm, Überlänge %.1f %%' % (
            z1, 100 * u1, z2, 100 * u2)
        self.assertLessEqual(z2, self.VIEL_BESSER * z1, text)
        self.assertLessEqual(u2, self.VIEL_BESSER * u1, text)

    @staticmethod
    def _schlauch(zacke_mm=0.0, n=360, r=0.09):
        """Gegenproben: ein Schlauch (Hosenbein, Halbmesser r) aus zwei Ringen; der untere Ring mit
        Sägezähnen von `zacke_mm` Höhe alle 20 mm."""
        w = np.linspace(0, 2 * np.pi, n, endpoint=False)
        zahn = (np.arange(n) * (2 * np.pi * r / n) / 0.02) % 1.0
        oben = np.stack([r * np.cos(w), r * np.sin(w), np.full(n, 0.2)], 1)
        unten = np.stack([r * np.cos(w), r * np.sin(w), zacke_mm / 1000 * zahn], 1)
        i = np.arange(n)
        j = (i + 1) % n
        dreiecke = np.concatenate([np.stack([i, j, i + n], 1), np.stack([j, j + n, i + n], 1)])
        return np.vstack([oben, unten]), dreiecke

    def test_gegenprobe_glatter_schlauch_besteht(self):
        """Glatte Ringe von 90 mm (Hosenbein) und 55 mm Halbmesser (Ärmel): die Glättung darf enge Kreise nicht als
        Zacken zählen."""
        for r in (0.09, 0.055):
            erg = {'schlauch': Ai2d3dsaummass.messen(*self._schlauch(r=r))}
            self.assertEqual(len(erg['schlauch']['saeume']), 2, erg)
            self.assertFalse(self._schlecht(erg), erg)

    def test_gegenprobe_saegezahn_saum_faellt_durch(self):
        """Zähne von 10 mm alle 20 mm — wie die ausgefransten Kanten der Zeile 1 — muss durchfallen."""
        erg = {'schlauch': Ai2d3dsaummass.messen(*self._schlauch(10.0))}
        self.assertTrue(self._schlecht(erg), erg)
