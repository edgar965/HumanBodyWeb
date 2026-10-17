# -*- coding: utf-8 -*-
"""`G9lebensalter`: der Sammelregler „Lebensalter" vom Baby bis 90 Jahre (17.10.2026). Geschrieben, nicht gelaufen (Tests nur auf Ansage).

WARUM (Edgar, 17.10.2026: „Kriegt man jetzt alles mit von Kind bis 100-jaehriger Mann?"): MakeHumans Alterskurve hat vier Stuetzstellen (1, 10, 25, 90 Jahre); die Zielgewichte laufen
dazwischen linear, deshalb tragen drei Morphs (Baby − jung, Kind − jung, Alt − jung) die ganze Kurve EXAKT. Geprueft:

1. Die Stuetzstellen: v = −1 → 1 Jahr, −0,625 → 10 Jahre, 0 → 25, +1 → 90; dazwischen linear (`jahre`).
2. Die Gewichte: 0 → nichts; −0,625 → nur Kind; −1 → nur Baby; dazwischen Baby und Kind SUMMIEREN ZU 1 (Gegenprobe: nie beide ueber 1); > 0 → Alt = v UND `alter:gesamt` = v.
3. `aufloesen` nimmt den Schieber aus den Reglern, summiert mit vorhandenen Werten und begrenzt auf die Grenzen der Einzelregler; ohne gebaute MakeHuman-Morphs bleibt nur der Teil ueber
   `alter:gesamt`.
4. Der Schieber fuer das Bedienfeld traegt `skala` und `einheit` (die Anzeige in Jahren).
"""
from unittest import mock

from django.test import SimpleTestCase
from Genesis9.alter import G9alter
from Genesis9.lebensalter import G9lebensalter

KIND, BABY, ALT = G9lebensalter.KIND, G9lebensalter.BABY, G9lebensalter.ALT


def alle_da():
    return mock.patch.multiple('Genesis9.lebensalter.G9mhmorphe', vorhanden=mock.Mock(return_value=True), grenzen=mock.Mock(return_value=(0.0, 1.0)))


class LebensalterTest(SimpleTestCase):
    databases = set()

    def test_1_stuetzstellen_und_linearer_verlauf_in_jahren(self):
        for v, jahre in ((-1.0, 1.0), (-0.625, 10.0), (0.0, 25.0), (1.0, 90.0)):
            self.assertAlmostEqual(G9lebensalter.jahre(v), jahre, places=6)
        self.assertAlmostEqual(G9lebensalter.jahre(-0.8125), 5.5, places=6)       # Mitte zwischen 1 und 10
        self.assertAlmostEqual(G9lebensalter.jahre(0.5), 57.5, places=6)          # Mitte zwischen 25 und 90
        self.assertAlmostEqual(G9lebensalter.jahre(7.0), 90.0, places=6, msg='begrenzt auf den Bereich')

    def test_2_gewichte_baby_kind_alt(self):
        self.assertEqual(G9lebensalter.beitraege(0.0), {})
        self.assertEqual(G9lebensalter.beitraege(-0.625), {KIND: 1.0})
        self.assertEqual(G9lebensalter.beitraege(-1.0), {BABY: 1.0})
        halb = G9lebensalter.beitraege(-0.8125)
        self.assertAlmostEqual(halb[BABY], 0.5, places=6)
        self.assertAlmostEqual(halb[KIND], 0.5, places=6)
        kind = G9lebensalter.beitraege(-0.3125)                                   # halber Weg Vorgabe → Kind
        self.assertEqual(set(kind), {KIND})
        self.assertAlmostEqual(kind[KIND], 0.5, places=6)
        alt = G9lebensalter.beitraege(0.4)
        self.assertEqual(alt, {ALT: 0.4, G9alter.NAME: 0.4})

    def test_3_baby_und_kind_summieren_immer_zu_eins(self):
        for i in range(0, 101):
            v = -1.0 + i * 0.00375
            b = G9lebensalter.beitraege(v)
            self.assertAlmostEqual(b.get(BABY, 0.0) + b.get(KIND, 0.0), 1.0, places=6, msg='v = %.4f' % v)

    def test_4_aufloesen_nimmt_den_schieber_heraus_summiert_und_begrenzt(self):
        with alle_da():
            aus = G9lebensalter.aufloesen({G9lebensalter.NAME: -0.8125, KIND: 0.8, 'x': 3.0})
        self.assertNotIn(G9lebensalter.NAME, aus)
        self.assertEqual(aus['x'], 3.0)
        self.assertAlmostEqual(aus[BABY], 0.5, places=6)
        self.assertAlmostEqual(aus[KIND], 1.0, places=6, msg='0,8 + 0,5 begrenzt auf 1')
        with alle_da():
            alt = G9lebensalter.aufloesen({G9lebensalter.NAME: 1.0, G9alter.NAME: 0.5})
        self.assertEqual(alt[G9alter.NAME], 1.0, 'summiert und auf 1 begrenzt')
        self.assertAlmostEqual(alt[ALT], 1.0, places=6)

    def test_5_ohne_makehuman_morphs_bleibt_nur_alter_gesamt(self):
        with mock.patch('Genesis9.lebensalter.G9mhmorphe.vorhanden', return_value=False):
            kind = G9lebensalter.aufloesen({G9lebensalter.NAME: -1.0})
            alt = G9lebensalter.aufloesen({G9lebensalter.NAME: 0.6})
        self.assertEqual(kind, {})
        self.assertEqual(alt, {G9alter.NAME: 0.6})

    def test_6_ohne_den_schieber_kommt_dieselbe_hand_zurueck(self):
        regler = {'a': 1.0}
        self.assertIs(G9lebensalter.aufloesen(regler), regler)

    def test_7_der_schieber_traegt_skala_und_einheit_fuer_die_anzeige(self):
        with mock.patch('Genesis9.lebensalter.G9mhmorphe.vorhanden', return_value=True):
            r = G9lebensalter.regler()
        self.assertEqual((r['name'], r['min'], r['max'], r['vorgabe'], r['bereich']), (G9lebensalter.NAME, -1.0, 1.0, 0.0, 'alter'))
        self.assertEqual(r['einheit'], 'Jahre')
        self.assertEqual(r['skala'], [[-1.0, 1.0], [-0.625, 10.0], [0.0, 25.0], [1.0, 90.0]])
        with mock.patch('Genesis9.lebensalter.G9mhmorphe.vorhanden', return_value=False):
            self.assertIn('NICHT gebaut', G9lebensalter.regler()['hinweis'])
