"""`Kostuemhautfarbe._hautsaum` (Regel 6) und `Kostuemsaumfarbe` auf Kunstdaten (06.11.2026, heller gezackter Rand am Beinsaum von Edgar 1).
Streifen aus Flächenreihen: unten Haut, darüber die Probe, darüber Stoff.
    1  heller Streifen im Farbton der Haut (Licht) zwischen Haut und Stoff: wird Haut, der Stoff bleibt
    2  weißer Besatz: bleibt (anderer Farbton)
    3  Stoff nah am Hautton: bleibt (die Farbe trennt nicht)
    4  Streifen ohne Haut daneben: bleibt
    5  Requisit und Haar: bleiben
    6  Regel 6 wächst Ring für Ring, höchstens `schritte` Reihen
    7  `Kostuemsaumfarbe.art`: ohne Datei die Art der Szene
Sabotage (von Hand): `farbton_abstand` in `_hautsaum` weglassen → Fall 2 rot; `trennt` weglassen → Fall 3 rot; `haut_p[self.fs].any(1)` weglassen → Fall 4 rot; `NIE_HAUT` leeren → Fall 5 rot.
"""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT / 'mesh3dai'))

TON = (64.0, 15.0, 20.0)
HELL = (83.0, 11.0, 12.5)
WEISS = (90.0, 0.0, 0.0)
BLAU = (50.0, 4.0, -15.0)
BEIGE = (60.0, 10.0, 12.0)


def streifen(reihen):
    """Reihen (Art, Lab) von unten nach oben, je Reihe 4 Dreiecke über 2 Felder → (Flächen, Art, Lab, Punktzahl)."""
    n = 3
    flaechen, arten, lab = [], [], []
    for r, (art, farbe) in enumerate(reihen):
        for x in range(2):
            a, b, c, d = r * n + x, r * n + x + 1, (r + 1) * n + x + 1, (r + 1) * n + x
            flaechen += [[a, b, c], [a, c, d]]
            arten += [art, art]
            lab += [farbe, farbe]
    return np.array(flaechen), np.array(arten), np.array(lab, dtype=np.float64), (len(reihen) + 1) * n


@unittest.skipUnless(__import__('torch').cuda.is_available(), 'Kostuemgpu rechnet nur auf der Karte')
class Fall(unittest.TestCase):
    def setUp(self):
        from mesh3dai_kostuem_hautfarbe import Kostuemhautfarbe
        from mesh3dai_kostuemarten import Kostuemarten
        from mesh3dai_kostuemgpu import Kostuemgpu
        self.k = Kostuemgpu.an()
        self.a = Kostuemarten
        self.klasse = Kostuemhautfarbe
        self.haut, self.haar = Kostuemarten.nummer('haut'), Kostuemarten.nummer('haar')
        self.hose = Kostuemarten.nummer('hose')

    def rechne(self, reihen, schritte=8):
        t = self.k.t
        f, art, lab, n_p = streifen(reihen)
        h = self.klasse.__new__(self.klasse)
        h.k, h.fs, h.lab = self.k, self.k.feld(f, t.int64), self.k.feld(lab, t.float64)
        ton = self.k.feld(np.array(TON), t.float64)
        return h._hautsaum(self.k.feld(art, t.int64), ton, n_p, self.haut, self.haar, schritte)

    def je_reihe(self, art):
        return art.cpu().numpy()[::4].tolist()

    def test_heller_streifen_wird_haut(self):
        art, gewechselt = self.rechne([(self.haut, TON), (self.hose, HELL), (self.hose, BLAU), (self.hose, BLAU)])
        self.assertEqual(self.je_reihe(art), [self.haut, self.haut, self.hose, self.hose])
        self.assertEqual(int(gewechselt.sum()), 4)

    def test_weisser_besatz_bleibt(self):
        art, gewechselt = self.rechne([(self.haut, TON), (self.hose, WEISS), (self.hose, BLAU), (self.hose, BLAU)])
        self.assertFalse(bool(gewechselt.any()))
        self.assertEqual(self.je_reihe(art)[1], self.hose)

    def test_nah_am_hautton_trennt_nicht(self):
        _art, gewechselt = self.rechne([(self.haut, TON), (self.hose, HELL), (self.hose, BEIGE), (self.hose, BEIGE)])
        self.assertFalse(bool(gewechselt.any()))

    def test_ohne_haut_daneben_bleibt(self):
        ober = self.a.nummer('oberteil')
        _art, gewechselt = self.rechne([(ober, BLAU), (self.hose, HELL), (self.hose, BLAU), (self.hose, BLAU)])
        self.assertFalse(bool(gewechselt.any()))

    def test_requisit_und_haar_bleiben(self):
        requisit = self.a.nummer('requisit')
        for art_nr in (requisit, self.haar):
            _art, gewechselt = self.rechne([(self.haut, TON), (art_nr, HELL), (art_nr, BLAU), (art_nr, BLAU)])
            self.assertFalse(bool(gewechselt.any()), self.a.ARTEN[art_nr])

    def test_ringe(self):
        reihen = [(self.haut, TON)] + [(self.hose, HELL)] * 3 + [(self.hose, BLAU)] * 8
        art, _g = self.rechne(reihen, schritte=2)
        self.assertEqual(self.je_reihe(art)[:4], [self.haut, self.haut, self.haut, self.hose])

    def test_art_ohne_datei(self):
        from mesh3dai_kostuem_saumfarbe import Kostuemsaumfarbe
        marke = object()
        szene = SimpleNamespace(k=self.k, eingang_art=marke, eingang_obj=SimpleNamespace(dreiecke=np.zeros((2, 3))))
        self.assertIs(Kostuemsaumfarbe.art(Path(settings.BASE_DIR) / 'gibt_es_nicht', szene), marke)
