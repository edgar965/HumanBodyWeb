# -*- coding: utf-8 -*-
"""`G9lebensalter`: der Sammelregler „Lebensalter" vom Baby bis 90 Jahre (17.10.2026). Geschrieben, nicht gelaufen (Tests nur auf Ansage).

WARUM (Edgar, 17.10.2026: „Kriegt man jetzt alles mit von Kind bis 100-jaehriger Mann?"): MakeHumans Alterskurve hat vier Stuetzstellen (1, 10, 25, 90 Jahre); die Zielgewichte laufen
dazwischen linear, deshalb tragen drei Morphs (Baby − jung, Kind − jung, Alt − jung) die ganze Kurve EXAKT. Geprueft:

AB 18 JAHREN (Edgar, 18.10.2026: „Änder die Slider und Wertebereiche bei den alten, so dass sie nur von dem untersten Bereich starten, wofür sie implementiert sind, also circa 18 Jahre“):
Kinder kommen aus Genesis 1; der Schieber beginnt bei −0,29 (18 Jahre) und kennt kein Baby mehr.

1. Die Stuetzstellen der Kurve bleiben MakeHumans (25 → 0, 90 → +1, dazwischen linear); unter dem Anschlag −0,29 gilt 18 Jahre (`jahre`).
2. Die Gewichte: 0 → nichts; −0,29 → Kind 0,464; ein alter Wert darunter (−1 = früher Baby) wie −0,29, NIE ein Baby; > 0 → Alt = v. Das Aussehen steht NICHT hier
   (seit Vorschlag A rechnet `G9alterung` es: `aussehen`, `erwachsen`).
3. `aufloesen` nimmt den Schieber aus den Reglern, summiert mit vorhandenen Werten und begrenzt auf die Grenzen der Einzelregler; ohne gebaute MakeHuman-Morphs bleibt nichts uebrig
   (das Aussehen wirkt trotzdem, ueber `G9alterung`). `alter:gesamt` fasst er nicht an.
4. Der Schieber fuer das Bedienfeld heisst nach seiner Herkunft (MakeHuman), laeuft −0,29…1 und traegt `skala` ab 18 Jahren und `einheit` (die Anzeige in Jahren).
5. `aussehen` (0 bis 25 Jahre, v darueber) und `erwachsen` (1 ab 25 Jahren, 1 − Kind darunter, 1 ohne gebaute Ablage).

Sabotage-Gegenprobe (nicht gefahren): `MIN` zurueck auf −1 → Faelle 1, 2, 4 und 7 rot; in `beitraege` den Baby-Zweig wieder einsetzen → Fall 3 rot.
"""
from unittest import mock

from django.test import SimpleTestCase
from Genesis9.alter import G9alter
from Genesis9.lebensalter import G9lebensalter

KIND, ALT = G9lebensalter.KIND, G9lebensalter.ALT
BABY = 'mh:macro_Alter_Baby'
KIND_18 = 0.29 / 0.625                  # Kind-Gewicht bei 18 Jahren, 0,464


def alle_da():
    return mock.patch.multiple('Genesis9.lebensalter.G9mhmorphe', vorhanden=mock.Mock(return_value=True), grenzen=mock.Mock(return_value=(0.0, 1.0)))


class LebensalterTest(SimpleTestCase):
    databases = set()

    def test_1_stuetzstellen_und_linearer_verlauf_in_jahren(self):
        for v, jahre in ((0.0, 25.0), (1.0, 90.0)):
            self.assertAlmostEqual(G9lebensalter.jahre(v), jahre, places=6)
        self.assertAlmostEqual(G9lebensalter.jahre(-0.29), 18.04, places=6, msg='der Anschlag: 18 Jahre')
        self.assertAlmostEqual(G9lebensalter.jahre(-1.0), 18.04, places=6, msg='unter dem Anschlag gilt 18 Jahre (früher 1 Jahr)')
        self.assertAlmostEqual(G9lebensalter.jahre(0.5), 57.5, places=6)          # Mitte zwischen 25 und 90
        self.assertAlmostEqual(G9lebensalter.jahre(7.0), 90.0, places=6, msg='begrenzt auf den Bereich')

    def test_2_gewichte_kind_alt_ab_18_jahren(self):
        self.assertEqual(G9lebensalter.beitraege(0.0), {})
        anschlag = G9lebensalter.beitraege(-0.29)
        self.assertEqual(set(anschlag), {KIND})
        self.assertAlmostEqual(anschlag[KIND], KIND_18, places=9)
        self.assertEqual(G9lebensalter.beitraege(-1.0), anschlag, 'ein gespeichertes Baby wird 18 Jahre alt')
        self.assertEqual(G9lebensalter.beitraege(-0.625), anschlag, 'ein gespeichertes Kind auch')
        self.assertAlmostEqual(G9lebensalter.beitraege(-0.15)[KIND], 0.24, places=9)
        alt = G9lebensalter.beitraege(0.4)
        self.assertEqual(alt, {ALT: 0.4}, 'nur die Entwicklung: das Aussehen rechnet `G9alterung`')

    def test_3_nie_ein_baby(self):
        for i in range(0, 201):
            b = G9lebensalter.beitraege(-1.0 + i * 0.01)
            self.assertNotIn(BABY, b, 'v = %.2f' % (-1.0 + i * 0.01))
            self.assertLessEqual(b.get(KIND, 0.0), KIND_18 + 1e-9)

    def test_4_aufloesen_nimmt_den_schieber_heraus_summiert_und_begrenzt(self):
        with alle_da():
            aus = G9lebensalter.aufloesen({G9lebensalter.NAME: -0.15, KIND: 0.8, 'x': 3.0})
        self.assertNotIn(G9lebensalter.NAME, aus)
        self.assertEqual(aus['x'], 3.0)
        self.assertNotIn(BABY, aus)
        self.assertAlmostEqual(aus[KIND], 1.0, places=6, msg='0,8 + 0,24 begrenzt auf 1')
        with alle_da():
            alt = G9lebensalter.aufloesen({G9lebensalter.NAME: 1.0, G9alter.NAME: 0.5})
        self.assertEqual(alt[G9alter.NAME], 0.5, '„Wirkt älter / jünger“ fasst er nicht an: es steht unverändert da (`G9alterung` rechnet beide zusammen)')
        self.assertAlmostEqual(alt[ALT], 1.0, places=6)

    def test_5_ohne_makehuman_morphs_bleibt_nichts_uebrig(self):
        with mock.patch('Genesis9.lebensalter.G9mhmorphe.vorhanden', return_value=False):
            kind = G9lebensalter.aufloesen({G9lebensalter.NAME: -1.0})
            alt = G9lebensalter.aufloesen({G9lebensalter.NAME: 0.6})
        self.assertEqual(kind, {})
        self.assertEqual(alt, {}, 'das Aussehen kommt aus `G9alterung`, nicht aus diesem Schieber allein')

    def test_5b_aussehen_und_erwachsen(self):
        self.assertEqual(G9lebensalter.aussehen(-1.0), 0.0)
        self.assertEqual(G9lebensalter.aussehen(-0.29), 0.0, '18 Jahre: kein Alters-Aussehen')
        self.assertEqual(G9lebensalter.aussehen(0.0), 0.0)
        self.assertAlmostEqual(G9lebensalter.aussehen(0.7), 0.7)
        self.assertEqual(G9lebensalter.aussehen(5.0), 1.0, 'begrenzt')
        with alle_da():
            self.assertEqual(G9lebensalter.erwachsen(0.0), 1.0)
            self.assertEqual(G9lebensalter.erwachsen(0.8), 1.0, 'ab 25 Jahren ganz erwachsen')
            self.assertAlmostEqual(G9lebensalter.erwachsen(-0.15), 0.76, places=6)
            self.assertAlmostEqual(G9lebensalter.erwachsen(-0.29), 1.0 - KIND_18, places=6, msg='18 Jahre: 0,536')
            self.assertAlmostEqual(G9lebensalter.erwachsen(-1.0), 1.0 - KIND_18, places=6, msg='unter dem Anschlag wie 18 Jahre')
        with mock.patch('Genesis9.lebensalter.G9mhmorphe.vorhanden', return_value=False):
            self.assertEqual(G9lebensalter.erwachsen(-0.29), 1.0, 'ohne gebaute Ablage gibt es keine Entwicklung')

    def test_6_ohne_den_schieber_kommt_dieselbe_hand_zurueck(self):
        regler = {'a': 1.0}
        self.assertIs(G9lebensalter.aufloesen(regler), regler)

    def test_7_der_schieber_heisst_nach_makehuman_beginnt_bei_18_und_traegt_skala_und_einheit(self):
        with mock.patch('Genesis9.lebensalter.G9mhmorphe.vorhanden', return_value=True):
            r = G9lebensalter.regler()
        self.assertEqual((r['name'], r['min'], r['max'], r['vorgabe'], r['bereich']), (G9lebensalter.NAME, -0.29, 1.0, 0.0, 'alter'))
        self.assertIn('MakeHuman', r['anzeige'])
        self.assertIn('18', r['anzeige'])
        self.assertEqual(r['einheit'], 'Jahre')
        self.assertEqual(r['skala'], [[-0.29, 18.04], [0.0, 25.0], [1.0, 90.0]], 'die Anzeige beginnt bei 18 Jahren, nicht bei 1')
        schritte = (r['vorgabe'] - r['min']) / 0.01
        self.assertAlmostEqual(schritte, round(schritte), places=9, msg='die Vorgabe 0 liegt auf dem Schritt 0,01 ab dem Anschlag (sonst trifft der Schieber 25 Jahre nicht)')
        with mock.patch('Genesis9.lebensalter.G9mhmorphe.vorhanden', return_value=False):
            self.assertIn('NICHT gebaut', G9lebensalter.regler()['hinweis'])
