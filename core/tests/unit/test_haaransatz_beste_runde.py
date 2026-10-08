# -*- coding: utf-8 -*-
"""Haaransatz und Stand = beste Runde (06.10.2026): `Haaransatz.anheben`, `IterationHaaransatz`, `Haarumbau.ansatz`, `Engine2d3dKleiderstandmodell._beste` — Kunstdaten, kein Render, keine Ablage."""
from types import SimpleNamespace

import numpy as np
from core.dienste.engine2d3dkleiderstandmodell import Engine2d3dKleiderstandmodell
from core.dienste.haaransatz import Haaransatz
from core.dienste.haarumbau import Haarumbau
from django.test import SimpleTestCase
from iterationen2d3d.iterationhaaransatz import IterationHaaransatz


class DerAnsatz(SimpleTestCase):
    @staticmethod
    def _feld():
        feld = np.zeros((36, 72), bool)
        feld[26:, :] = True                                  # Haar von 40° (Zeile 26) bis zum Scheitel in jeder Spalte
        return feld

    def test_1_die_mitte_verliert_zeilen_die_seite_nichts(self):
        aus = Haaransatz.anheben(self._feld(), 10.0, 5.0)    # 10° = zwei Zeilen
        self.assertEqual(int(aus[:, 0].sum()), int(self._feld()[:, 0].sum()) - 2)       # Spalte 0: Azimut 2,5°
        self.assertEqual(int(aus[:, 71].sum()), int(self._feld()[:, 71].sum()) - 2)     # Spalte 71: −2,5°
        self.assertEqual(int(aus[:, 12].sum()), int(self._feld()[:, 12].sum()))         # Spalte 12: 62,5° — außerhalb von `AZIMUT`
        self.assertEqual(int(aus[:, 6].sum()), int(self._feld()[:, 6].sum()) - 1)       # 32,5°: halb so stark, auf eine Zeile gerundet

    def test_2_ohne_anhebung_unveraendert_und_das_original_bleibt(self):
        feld = self._feld()
        vorher = feld.copy()
        self.assertTrue((Haaransatz.anheben(feld, 0.0, 5.0) == feld).all())
        Haaransatz.anheben(feld, 20.0, 5.0)
        self.assertTrue((feld == vorher).all())

    def test_3_wange_unter_dem_ansatz_zaehlt_nicht(self):
        feld = np.zeros((36, 72), bool)
        feld[22:34, 0] = True                               # Haarfelder von 20° an: Wange und Bartschatten bis 30°, darüber die Stirn
        aus = Haaransatz.anheben(feld, 10.0, 5.0)
        self.assertEqual(int(aus[:, 0].sum()), int(feld[:, 0].sum()) - 2)
        self.assertTrue(aus[22:24, 0].all())                # die Felder unter `AB_EL` bleiben stehen

    def test_4_hoechstens_30_grad(self):
        feld = self._feld()
        self.assertTrue((Haaransatz.anheben(feld, 90.0, 5.0) == Haaransatz.anheben(feld, 30.0, 5.0)).all())


class DieRegel(SimpleTestCase):
    @staticmethod
    def _befund(haut, verhaeltnis=1.0, teil='herrenhaar_0'):
        return {'haarabgleich': {'farbe': {'verhaeltnis': verhaeltnis}, 'teile': {teil: {'haut': haut}}}}

    VORN = [[None, None, 0.0, 0.9, 0.8, 0.0, None, None]] * 3

    def test_1_ueber_der_schwelle_wird_angehoben(self):
        modell = SimpleNamespace(haltung_werte={})
        self.assertEqual(IterationHaaransatz(modell, self._befund(self.VORN)).aufrufe(), ['m.haar_ansatz(20.0)'])

    def test_2_der_naechste_schritt_geht_vom_jetzigen_aus_bis_zur_grenze(self):
        modell = SimpleNamespace(haltung_werte={'haarlinie': {'vorn': 20.0}})
        self.assertEqual(IterationHaaransatz(modell, self._befund(self.VORN)).aufrufe(), ['m.haar_ansatz(30.0)'])
        modell.haltung_werte['haarlinie']['vorn'] = 30.0
        self.assertEqual(IterationHaaransatz(modell, self._befund(self.VORN)).aufrufe(), [])

    def test_3_erst_die_farbe_dann_die_form(self):
        modell = SimpleNamespace(haltung_werte={})
        self.assertEqual(IterationHaaransatz(modell, self._befund(self.VORN, verhaeltnis=0.77)).aufrufe(), [])

    def test_4_unter_der_schwelle_oder_ohne_eigenes_haar_nichts(self):
        modell = SimpleNamespace(haltung_werte={})
        wenig = [[None, None, 0.0, 0.1, 0.2, 0.0, None, None]] * 3
        self.assertEqual(IterationHaaransatz(modell, self._befund(wenig)).aufrufe(), [])
        self.assertEqual(IterationHaaransatz(modell, self._befund(self.VORN, teil='mavick_hair')).aufrufe(), [])      # die Garderobenfrisur: die Zeile wirkt dort nicht
        self.assertEqual(IterationHaaransatz(modell, {}).aufrufe(), [])

    def test_5_der_bart_zaehlt_nicht(self):
        modell = SimpleNamespace(haltung_werte={})
        self.assertEqual(IterationHaaransatz(modell, self._befund(self.VORN, teil='herrenhaar_0_beard')).aufrufe(), [])

    def test_6_haarumbau_liest_den_wert_aus_dem_modell(self):
        self.assertEqual(Haarumbau.ansatz(SimpleNamespace(haltung_werte={'haarlinie': {'vorn': 12.5}})), 12.5)
        self.assertEqual(Haarumbau.ansatz(SimpleNamespace(haltung_werte={})), 0.0)
        self.assertEqual(Haarumbau.ansatz(SimpleNamespace()), 0.0)


class DieBesteRunde(SimpleTestCase):
    @staticmethod
    def _stand(runden, kreislauf):
        job = SimpleNamespace(kennung='x', ergebnis={'iterationen': runden, 'kreislauf': kreislauf}, stellung=lambda: {})
        return Engine2d3dKleiderstandmodell(job, ablage=SimpleNamespace())

    RUNDEN = [{'runde': 1, 'werte': {'tag': 'eins'}}, {'runde': 3, 'werte': {'tag': 'drei'}}, {'runde': 5, 'werte': {'tag': 'fuenf'}, 'auswahl': {'aktion': 'probe'}}]

    def test_1_der_stand_ist_die_beste_runde_nicht_die_letzte(self):
        stand = self._stand(self.RUNDEN, {'runde_bester': 3, 'modell': {'tag': 'aus_kreislauf'}})
        self.assertEqual(stand._beste()['runde'], 3)             # noqa: SLF001
        self.assertEqual(stand._kreislaufmodell(), {'tag': 'drei'})    # noqa: SLF001
        self.assertEqual(stand._beste_runde(), 3)                # noqa: SLF001

    def test_2_ohne_runde_bester_gilt_kreislauf_modell(self):
        stand = self._stand(self.RUNDEN, {'modell': {'tag': 'aus_kreislauf'}})
        self.assertIsNone(stand._beste())                        # noqa: SLF001
        self.assertEqual(stand._kreislaufmodell(), {'tag': 'aus_kreislauf'})   # noqa: SLF001

    def test_3_eine_beste_runde_ohne_werte_faellt_auf_kreislauf_modell_zurueck(self):
        stand = self._stand([{'runde': 3}], {'runde_bester': 3, 'modell': {'tag': 'aus_kreislauf'}})
        self.assertEqual(stand._kreislaufmodell(), {'tag': 'aus_kreislauf'})   # noqa: SLF001
