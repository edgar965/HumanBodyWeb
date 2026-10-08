# -*- coding: utf-8 -*-
"""08.10.2026, N1 („…22.53.48", Fotos einer nackten Person): findet die Segmentierung KEINE Kleidung, ist das Startrezept nicht leer, sondern „nackt" — sonst bleibt das Standardhemd `g9_base_shirt` des frischen Modells
stehen (Runde 0 trug ein schwarzes Hemd, das Hemd schloss den Rumpf von der Fotohaut aus: Deckung der Rumpfkachel 3,6 %). Kunstdaten, keine Ablage, kein Render."""
from types import SimpleNamespace

from core.dienste.standvorabkleider import Standvorabkleider as Vorab
from django.test import SimpleTestCase
from Genesis9.modellmitkleidern import ModellMitKleidern


def _job(oberteil=0.0, hose=0.0, socken=0.0, zubehoer=6.5, segmentierung=True, stuecke=None):
    kennzahlen = {'stuecke': {
        'nicht Kleidung': {'flaechen': 29903, 'cm2': 6352.0}, 'Oberteil': {'flaechen': 1, 'cm2': oberteil}, 'Hose / Rock': {'flaechen': 1, 'cm2': hose},
        'Socken / Schuhe': {'flaechen': 1, 'cm2': socken}, 'Zubehör': {'flaechen': 33, 'cm2': zubehoer}, 'Haar': {'flaechen': 1829, 'cm2': 412.0}}}
    ergebnis = {'fotostuecke': {'stuecke': stuecke or {}, 'bericht': {}}}
    if segmentierung:
        ergebnis['segmentierung'] = {'kennzahlen': kennzahlen}
    return SimpleNamespace(kennung='2026.01.01.00.00.00', ergebnis=ergebnis, optionen={})


class DieNackteFigur(SimpleTestCase):
    def test_1_ohne_kleidung_in_der_segmentierung_ist_die_figur_nackt(self):
        self.assertTrue(Vorab.nackt(_job()))
        self.assertTrue(Vorab.nackt(_job(oberteil=12.0, hose=3.0, socken=0.0)))             # Reste unter der Schwelle (Rand, Schatten) zählen nicht als Kleidung

    def test_2_jede_kleidung_ueber_der_schwelle_heisst_nicht_nackt(self):
        self.assertFalse(Vorab.nackt(_job(oberteil=1400.0)))
        self.assertFalse(Vorab.nackt(_job(hose=900.0)))
        self.assertFalse(Vorab.nackt(_job(socken=150.0)))

    def test_3_ohne_segmentierung_wird_nichts_vermutet(self):
        self.assertFalse(Vorab.nackt(_job(segmentierung=False)))                            # kein Befund ist kein Urteil: die alte Wahl nach Körperbändern bleibt

    def test_4_mit_fotostuecken_ist_sie_nie_nackt(self):
        self.assertFalse(Vorab.nackt(_job(stuecke={'hose': 'eigen_foto_x_hose_f25'})))

    def test_5_zubehoer_allein_macht_nicht_bekleidet(self):
        self.assertTrue(Vorab.nackt(_job(zubehoer=400.0)))                                  # Uhr, Armband: kommt über `uhren`, nicht über das Hemd

    def test_6_das_modell_der_nackten_figur_traegt_kein_standardhemd(self):
        modell = Vorab.modell(_job())
        self.assertIsNotNone(modell)                                                        # nicht None: das Standmodell hat ein Vorab-Modell
        self.assertEqual(modell['kleidung'].get(ModellMitKleidern.KEINE), 1.0)              # ausdrücklich „nichts tragen": `kleid_aus(Hemd)` allein ließ die Grundsorte einspringen
        self.assertFalse(ModellMitKleidern.aus(modell).kleider())

    def test_7_ohne_kleidung_und_ohne_befund_bleibt_none(self):
        self.assertIsNone(Vorab.modell(_job(segmentierung=False)))

    def test_8_alle_anteile_null_laesst_die_grundsorte_einspringen_kleid_keins_nicht(self):
        nur_null = ModellMitKleidern().kleid_anteil('g9_base_shirt', 0.0)
        self.assertTrue(nur_null.kleider())                                                 # der Grund für `kleid_keins` (G9kleidgenerischwahl: „Stehen alle auf 0, gilt die Grundsorte")
        self.assertEqual(ModellMitKleidern().kleid_keins().kleider(), [])

    def test_9_ein_stueck_nach_kleid_keins_nimmt_die_marke_weg(self):
        modell = ModellMitKleidern().kleid_keins()
        self.assertEqual(modell.kleidung.get(ModellMitKleidern.KEINE), 1.0)
        modell.kleid_nur('g9_base_shirt')
        self.assertNotIn(ModellMitKleidern.KEINE, modell.kleidung)
        self.assertTrue(modell.kleider())

    def test_10_kleid_keins_ist_ein_rezeptaufruf(self):
        from Genesis9.modellrezept import G9rezept
        self.assertIn('kleid_keins', G9rezept.funktionen())
