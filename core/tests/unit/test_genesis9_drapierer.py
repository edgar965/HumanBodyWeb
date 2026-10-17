# -*- coding: utf-8 -*-
u"""Der Drapierer über dem männlichen Geograft (`Genesis9/drapierer.py`, `drapierhindernis.py`, `drapierung.py`, 16.10.2026).

WARUM (Edgar, 16.10.2026: „bei dem männlichen Geschlechtsteile fitten die Kleider alle nicht" — „das soll schön drapieren, wie ein Kleidungsstück" —
„dieser Drapierer soll auch einstellbar sein"): Hose und Shorts standen als Zackenstern um das Geograft, die Spitze schaute durch. Gemessen an JS Pants
und Shorts (Daz Mann): schneidende Stoffkanten 155 → 0 und 256 → 0 (GarmentCodes Maß `count_body_cloth_intersections`).

Kunstdaten ohne Daz-Bibliothek: das Hindernis ist eine Kugel (Radius 3 cm), der Stoff ein Gitter in der Ebene z = 0 durch ihren Mittelpunkt, Normale +z.

1. `kreuzungen`: eine Strecke durch die Kugel schneidet sie zweimal, eine daneben nie.
2. `drapieren`: der Stoff liegt danach über der Kugel (keine schneidende Kante, keine Punkte darin), wird nirgends gesenkt, bleibt außerhalb der Ausbreitung
   unberührt, alle Werte endlich.
3. Weit weg vom Hindernis bleibt der Stoff, wie er ist.
4. `G9drapierung`: Vorgaben, Begrenzung auf die Reglergrenzen (auch 0 mm Abstand → 0,5 mm), und die Regler hängen nur an Hosen, Shorts, Unterwäsche, Anzügen.

Tests geschrieben, nicht gelaufen (nur auf Ansage). Sabotage-Gegenprobe (nicht gefahren): in `G9drapierer.drapieren` die Zeile `x = x + cls._loesen(…)`
weglassen → Fall 2 rot; in `G9drapierhindernis.kreuzungen` die Bedingung `t <= 1.0` weglassen → Fall 1 rot (die Strecke trifft dann auch Dreiecke hinter ihrem Ende).
"""
import numpy as np
from django.test import SimpleTestCase

from ..unit._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from Genesis9.drapierer import G9drapierer  # noqa: E402
from Genesis9.drapierhindernis import G9drapierhindernis  # noqa: E402
from Genesis9.drapierung import G9drapierung  # noqa: E402

RADIUS = 0.03
SCHRITT = 0.005


def kugel():
    import trimesh
    netz = trimesh.creation.icosphere(subdivisions=2, radius=RADIUS)
    return G9drapierhindernis(np.asarray(netz.vertices, dtype=np.float64), np.asarray(netz.faces, dtype=np.int64))


def tuch(hoehe=0.0, halb=0.05):
    u"""`(punkte, dreiecke, normalen)`: ein Gitter in der Ebene z = `hoehe`, Normale +z."""
    achse = np.arange(-halb, halb + 1e-9, SCHRITT)
    n = len(achse)
    x, y = np.meshgrid(achse, achse)
    punkte = np.column_stack([x.ravel(), y.ravel(), np.full(x.size, hoehe)])
    nummer = np.arange(n * n).reshape(n, n)
    a, b, c, d = nummer[:-1, :-1].ravel(), nummer[:-1, 1:].ravel(), nummer[1:, 1:].ravel(), nummer[1:, :-1].ravel()
    dreiecke = np.vstack([np.column_stack([a, b, c]), np.column_stack([a, c, d])])
    return punkte, dreiecke, np.tile([0.0, 0.0, 1.0], (len(punkte), 1))


class Kreuzungen(SimpleTestCase):
    databases = set()

    def test_1_eine_strecke_durch_die_kugel_schneidet_sie_zweimal(self):
        hindernis = kugel()
        a = np.array([[0.0013, 0.0007, -0.1], [0.2, 0.0, -0.1]])        # leicht neben der Achse: sonst träfe die Strecke eine Kante zweimal
        b = np.array([[0.0013, 0.0007, 0.1], [0.2, 0.0, 0.1]])
        segment, anteil, _dreieck = hindernis.kreuzungen(a, b)
        self.assertEqual(int((segment == 0).sum()), 2, 'durch die Mitte: Eintritt und Austritt')
        self.assertEqual(int((segment == 1).sum()), 0, 'weit daneben: kein Treffer')
        self.assertTrue(((anteil >= 0.0) & (anteil <= 1.0)).all())


class Drapieren(SimpleTestCase):
    databases = set()

    def test_2_der_stoff_liegt_danach_ueber_der_kugel(self):
        hindernis = kugel()
        punkte, dreiecke, normalen = tuch()
        # Ausbreitung 1,5 cm: frei ist, was höchstens so weit von der Kugelfläche liegt — die Gitterränder (Radius ≥ 5 cm) bleiben fest.
        neu, bilanz = G9drapierer.drapieren(punkte, dreiecke, normalen, hindernis, 0.003, 0.015, 0.5)
        self.assertTrue(np.isfinite(neu).all())
        self.assertGreater(bilanz['kreuzend_vorher'], 0, 'die Ebene durch die Mitte schneidet die Kugel')
        self.assertEqual(bilanz['drin_nachher'], 0, 'kein Stoffpunkt mehr in der Kugel')
        self.assertLess(bilanz['kreuzend_nachher'], bilanz['kreuzend_vorher'])
        self.assertGreaterEqual(float(neu[:, 2].min()), -2e-3, 'der Stoff wird nirgends gesenkt (die Glättung darf Millimeter nachgeben)')
        self.assertGreater(float(neu[:, 2].max()), RADIUS, 'der höchste Stoffpunkt liegt über dem Scheitel der Kugel')
        ecke = np.linalg.norm(punkte[:, :2], axis=1) > 0.049
        self.assertLess(float(np.abs(neu[ecke] - punkte[ecke]).max()), 1e-9, 'außerhalb der Ausbreitung bleibt der Stoff, wo er war')

    def test_3_weit_weg_vom_hindernis_aendert_sich_nichts(self):
        hindernis = kugel()
        punkte, dreiecke, normalen = tuch(hoehe=1.0)
        neu, bilanz = G9drapierer.drapieren(punkte, dreiecke, normalen, hindernis, 0.003, 0.04, 0.5)
        np.testing.assert_array_equal(neu, punkte)
        self.assertEqual(bilanz['gehoben'], 0)


class Regler(SimpleTestCase):
    databases = set()

    def test_4_vorgaben_grenzen_und_wo_die_regler_haengen(self):
        self.assertEqual(G9drapierung.werte({}), (0.003, 0.04, 0.5))
        abstand, ausbreitung, glaettung = G9drapierung.werte({G9drapierung.ABSTAND: 0.0, G9drapierung.AUSBREITUNG: 99.0, G9drapierung.GLAETTUNG: -3.0})
        self.assertAlmostEqual(abstand, 0.0005)
        self.assertAlmostEqual(ausbreitung, 0.10)
        self.assertEqual(glaettung, 0.0)
        self.assertEqual(G9drapierung.werte({G9drapierung.ABSTAND: 'zwei'})[0], 0.003, 'Unsinn fällt auf die Vorgabe')
        eintrag = {'art': 'kleidung', 'regler': [{'name': 'x'}]}
        for kategorie in (u'Hosen', u'Shorts', u'Unterwäsche', u'Anzüge'):
            self.assertEqual(len(G9drapierung.erweitern(eintrag, kategorie)), 4, kategorie)
        for kategorie in (u'Oberteile', u'Kleider', u'Schuhe', u'Haare'):
            self.assertEqual(len(G9drapierung.erweitern(eintrag, kategorie)), 1, kategorie)
        self.assertEqual(len(G9drapierung.erweitern({'art': 'haar', 'regler': []}, u'Hosen')), 0, 'nur Kleidung')
