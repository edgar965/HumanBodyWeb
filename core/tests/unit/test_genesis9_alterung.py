# -*- coding: utf-8 -*-
u"""`G9alterung`: ein Alter, ein Aussehen (17.10.2026, Vorschlag A). Geschrieben, nicht gelaufen (Tests nur auf Ansage).

WARUM (Edgar, 17.10.2026: „die zwei Altersregler widersprechen sich wahrscheinlich, schlage vor, wie man das vereinheitlichen kann“, dann „lebensalter Regler völlig plemplem. Mach A“, dann
„Hast du diese Alters-Regler erfunden?“): Fünf Widersprüche waren an einer Tabelle gemessen (Ursula, Höhe je Lebensalter × Alter, `genesis9-alter.md`). Jeder steht hier als Fall, den die
Neuordnung beantworten muss:

1. DOPPELT GEZÄHLT: „Wirkt älter / jünger“ (`alter:gesamt`) legt kein Kind mehr dazu — Lebensalter −1 und Alter −1 gaben 0,462 m. Größe und Proportionen kommen allein vom Lebensalter.
2. DER KLEINERE GEWINNT NICHT MEHR: die MakeHuman-Gewichte hängen nicht am zweiten Schieber (dasselbe Kind-Gewicht bei Alter −1, 0, +1).
3. EIN AUSSEHEN: Körper UND Falten/Haare lesen dasselbe `aussehen`. Unter 25 Jahren wirkt „Wirkt älter“ nur mit `erwachsen` (18 Jahre: 0,536; seit 18.10.2026 beginnt das Lebensalter dort, ein
   gespeichertes Baby gilt als 18 Jahre), Lebensalter +0,5 mit Alter −0,5 zeigt netto 0 — auf Körper und Haut.
4. EIN NULLPUNKT: beide Schieber haben bei 0 kein Aussehen (25 Jahre).
5. DAS AUSSEHEN HAT UNTEN EINEN ANSCHLAG: unter dem Ausgangsgesicht gibt es nichts (HumanBody kennt nur 18–100 Jahre); „Wirkt jünger“ nimmt nur zurück, was das Alter aufgelegt hat. Die erfundenen
   Jugendkanäle (große Augen, kleine Nase …) und HumanBodys ganze `minus`-Spalte (59 → 18 Jahre) wirken auf ein junges Gesicht nicht mehr.

Sabotage-Gegenprobe (nicht gefahren): in `aussehen` das `erwachsen` weglassen → Fall 3 rot; die Summe durch `max` ersetzen → Fall 3 (netto 0) rot; in `G9alter.beitraege` das Kind wieder dazulegen → Fall 1 rot;
die Kappung bei 0 streichen → Fall 5 rot.
"""
from types import SimpleNamespace
from unittest import mock

from django.test import SimpleTestCase
from Genesis9.alter import G9alter
from Genesis9.alterung import G9alterung
from Genesis9.formung import G9formung
from Genesis9.lebensalter import G9lebensalter

JAHRE, WIRKT = G9lebensalter.NAME, G9alter.NAME
KIND, ALT = G9lebensalter.KIND, G9lebensalter.ALT
BABY = 'mh:macro_Alter_Baby'
ERWACHSEN_18 = 1.0 - 0.29 / 0.625       # 0,536: wie erwachsen 18 Jahre nach MakeHumans Kurve sind
W = G9alter.WEIBLICH


def alle_da():
    return mock.patch.multiple('Genesis9.lebensalter.G9mhmorphe', vorhanden=mock.Mock(return_value=True), grenzen=mock.Mock(return_value=(0.0, 1.0)))


def grenzen():
    u"""Alle Namen der Alterstabellen mit Grenzen −1…1 — so, als gäbe es sie alle (`G9alter._grenzen`)."""
    namen = {k: (-1.0, 1.0) for k in G9alter.beitraege(1.0, True)} | {k: (-1.0, 1.0) for k in G9alter.beitraege(1.0, False)}
    return mock.patch.object(G9alter, '_grenzen', classmethod(lambda cls: dict(namen)))


class AussehenTest(SimpleTestCase):
    databases = set()

    def test_1_die_summe_ist_das_aussehen_ohne_kind_anteil(self):
        with alle_da():
            self.assertAlmostEqual(G9alterung.aussehen({JAHRE: 0.5}), 0.5)
            self.assertAlmostEqual(G9alterung.aussehen({WIRKT: 0.5}), 0.5)
            self.assertAlmostEqual(G9alterung.aussehen({JAHRE: 0.5, WIRKT: -0.25}), 0.25)
            self.assertEqual(G9alterung.aussehen({}), 0.0)

    def test_2_unter_25_jahren_wirkt_aelter_mit_dem_erwachsenen_anteil(self):
        with alle_da():
            self.assertAlmostEqual(G9alterung.aussehen({JAHRE: -0.29, WIRKT: 1.0}), ERWACHSEN_18, places=6, msg='18 Jahre: Kind 0,464, Wirkung 0,536')
            self.assertAlmostEqual(G9alterung.aussehen({JAHRE: -1.0, WIRKT: 1.0}), ERWACHSEN_18, places=6, msg='ein gespeichertes Baby gilt als 18 Jahre')
            self.assertAlmostEqual(G9alterung.aussehen({JAHRE: -0.15, WIRKT: 1.0}), 0.76, places=6)

    def test_3_die_summe_netto_null_gilt_fuer_koerper_und_haut(self):
        with alle_da():
            self.assertAlmostEqual(G9alterung.aussehen({JAHRE: 0.5, WIRKT: -0.5}), 0.0, places=9, msg='Lebensalter +0,5 und Alter −0,5: nichts (vorher zeigte die Haut 0,5)')

    def test_4_das_ende_der_skala_ist_gekappt_und_jung_zieht_zurueck(self):
        with alle_da():
            self.assertEqual(G9alterung.aussehen({JAHRE: 1.0, WIRKT: 1.0}), 1.0)
            self.assertEqual(G9alterung.aussehen({JAHRE: 1.0, WIRKT: 0.0}), 1.0)
            self.assertAlmostEqual(G9alterung.aussehen({JAHRE: 1.0, WIRKT: -0.5}), 0.5, msg='90 Jahre, die jünger wirken: der Schieber wirkt noch (vorher +19 mm gegen den Wunsch)')
            self.assertEqual(G9alterung.aussehen({JAHRE: 7.0, WIRKT: -9.0}), 0.0, 'beide Schieber sind auf −1…1 begrenzt')

    def test_4b_unter_dem_ausgangsgesicht_gibt_es_nichts(self):
        with alle_da():
            self.assertEqual(G9alterung.aussehen({WIRKT: -1.0}), 0.0, 'ein Erwachsener wirkt nicht jünger als die Grundfigur: HumanBody kennt nur 18–100 Jahre')
            self.assertEqual(G9alterung.aussehen({JAHRE: 0.2, WIRKT: -1.0}), 0.0)
            self.assertEqual(G9alterung.aussehen({JAHRE: -0.29, WIRKT: -1.0}), 0.0)

    def test_5_ohne_gebaute_makehuman_morphs_gibt_es_keine_entwicklung(self):
        with mock.patch('Genesis9.lebensalter.G9mhmorphe.vorhanden', return_value=False):
            self.assertEqual(G9alterung.aussehen({JAHRE: -1.0, WIRKT: 1.0}), 1.0)

    def test_6_unlesbare_werte_zaehlen_null(self):
        with alle_da():
            self.assertEqual(G9alterung.aussehen({JAHRE: 'x', WIRKT: None}), 0.0)


class AufloesenTest(SimpleTestCase):
    databases = set()

    def test_7_ohne_die_schieber_kommt_dieselbe_hand_zurueck(self):
        regler = {W: 1.0}
        rest, aussehen = G9alterung.aufloesen(regler)
        self.assertIs(rest, regler)
        self.assertEqual(aussehen, 0.0)

    def test_8_beide_schieber_verschwinden_und_stehen_auf_den_einzelreglern(self):
        with alle_da(), grenzen():
            rest, aussehen = G9alterung.aufloesen({W: 1.0, JAHRE: 1.0, WIRKT: -0.25})
        self.assertNotIn(JAHRE, rest)
        self.assertNotIn(WIRKT, rest)
        self.assertAlmostEqual(aussehen, 0.75)
        self.assertAlmostEqual(rest[ALT], 1.0, msg='die Entwicklung kommt vom Lebensalter')
        self.assertIn('hb:Chin_Tone', rest, 'das Aussehen 0,75 stellt die HumanBody-Morphs')

    def test_9_die_groesse_haengt_nur_am_lebensalter(self):
        with alle_da(), grenzen():
            kind = {w: G9alterung.aufloesen({W: 1.0, JAHRE: -0.25, WIRKT: w})[0] for w in (-1.0, 0.0, 1.0)}
        self.assertEqual({r.get(KIND) for r in kind.values()}, {0.4}, 'dasselbe Kind-Gewicht bei Alter −1, 0 und +1')
        self.assertNotIn(BABY, kind[0.0])
        with alle_da(), grenzen():
            erwachsen = {w: G9alterung.aufloesen({W: 1.0, WIRKT: w})[0] for w in (-1.0, 1.0)}
        for rest in erwachsen.values():
            self.assertNotIn(KIND, rest, 'Alter −1 legt kein Kind mehr dazu (0,462 m bei Lebensalter −1)')

    def test_10_ein_gespeichertes_baby_wird_18_jahre_alt(self):
        with alle_da(), grenzen():
            rest, aussehen = G9alterung.aufloesen({W: 1.0, JAHRE: -1.0, WIRKT: 1.0})
        self.assertAlmostEqual(aussehen, ERWACHSEN_18, places=6)
        self.assertNotIn(BABY, rest, 'das Lebensalter kennt seit 18.10.2026 kein Baby mehr (Kinder: Genesis 1)')
        self.assertAlmostEqual(rest[KIND], 1.0 - ERWACHSEN_18, places=6)

    def test_10b_wirkt_juenger_auf_einem_erwachsenen_legt_nichts_auf(self):
        with alle_da(), grenzen():
            rest, aussehen = G9alterung.aufloesen({W: 1.0, WIRKT: -1.0})
        self.assertEqual(aussehen, 0.0)
        self.assertEqual(rest, {W: 1.0}, 'weder HumanBodys minus-Spalte noch Jugendkanäle')


class FormungTest(SimpleTestCase):
    databases = set()

    def test_11_die_formung_traegt_das_aussehen_und_der_fingerabdruck_unterscheidet_es(self):
        kanaele = SimpleNamespace(kanaele={})
        with alle_da(), grenzen(), mock.patch('Genesis9.formung.G9morphablage.holen', return_value=kanaele):
            alt = G9formung({W: 1.0, JAHRE: 0.4, WIRKT: 0.2})
            gleich = G9formung({W: 1.0, JAHRE: 0.4, WIRKT: 0.2})
            anders = G9formung({W: 1.0, JAHRE: 0.4})
        self.assertAlmostEqual(alt.alter_aussehen, 0.6)
        self.assertNotIn(JAHRE, alt.regler)
        self.assertNotIn(WIRKT, alt.regler)
        self.assertEqual(alt.fingerabdruck(), gleich.fingerabdruck())
        self.assertNotEqual(alt.fingerabdruck(), anders.fingerabdruck())
