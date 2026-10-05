# -*- coding: utf-8 -*-
"""Haarklemme, Genesis-Hemd statt Fotostück und angeglichene Strähnengruppen (04.10.2026, Edgar: „Haar oben viel zu lang", „Haar seitlich braun", „T-short ist verfranst … nimmst du ein Genesis T-Shirt?").

Kleine Kunstdaten, keine Netze und keine Datenbank: `Haarklemme` mit einer Kugelhülle, `Kleiderwahl.mit_oberteil`, `G9texturschicht.grau` mit `gleich`, das Vorab-Modell mit Hemd der Bibliothek.
Geschrieben, nicht gelaufen (`testsuite-nur-auf-ansage`).
"""

from types import SimpleNamespace
from unittest import mock

import numpy as np
from django.test import SimpleTestCase
from Genesis9.texturschicht import G9texturschicht
from iterationen2d3d.kleiderwahl import Kleiderwahl

from core.dienste.engine2d3dkleiderkoerperoptionen import Engine2d3dKleiderkoerperoptionen
from core.dienste.haarklemme import Haarklemme
from core.dienste.standvorabkleider import Standvorabkleider


def _kugelhuelle(radius, hoehe=36, breite=72):
    return np.full((hoehe, breite), radius)


class DieHaarklemme(SimpleTestCase):
    MITTE = (0.0, 1.6, 0.0)

    def test_ein_punkt_weit_ueber_der_huelle_endet_eine_toleranz_darueber(self):
        klemme = Haarklemme(_kugelhuelle(0.10), self.MITTE)
        punkte = np.array([[0.0, 1.6 + 0.15, 0.0]])
        neu, anzahl, weit = klemme.klemmen(punkte)
        r = float(np.linalg.norm(neu[0] - np.array(self.MITTE)))
        self.assertEqual(anzahl, 1)
        self.assertAlmostEqual(r, 0.10 + Haarklemme.TOLERANZ_M * np.tanh(0.05 / Haarklemme.TOLERANZ_M), places=5)
        self.assertLess(r, 0.10 + Haarklemme.TOLERANZ_M + 1e-9)
        self.assertGreater(weit, 0.03)

    def test_innerhalb_der_huelle_bleibt_alles(self):
        klemme = Haarklemme(_kugelhuelle(0.10), self.MITTE)
        punkte = np.array([[0.05, 1.6, 0.0], [0.0, 1.6, -0.09], [0.0, 1.6 + 0.099, 0.0]])
        neu, anzahl, _weit = klemme.klemmen(punkte)
        self.assertEqual(anzahl, 0)
        np.testing.assert_allclose(neu, punkte)

    def test_ein_kleiner_ueberstand_bleibt_fast_ein_kleiner_ueberstand(self):
        klemme = Haarklemme(_kugelhuelle(0.10), self.MITTE)
        neu, _n, _w = klemme.klemmen(np.array([[0.0, 1.6 + 0.102, 0.0]]))
        self.assertAlmostEqual(float(np.linalg.norm(neu[0] - np.array(self.MITTE))) - 0.10, 0.002, places=4)

    def test_felder_ohne_netzhaar_klemmen_nichts(self):
        karte = _kugelhuelle(0.10)
        karte[:, 0:36] = np.nan                         # die eine Hälfte der Richtungen hat kein Netzhaar (Gesicht)
        klemme = Haarklemme(karte, self.MITTE)
        # Mitten in den Hälften (Azimut 90° und 270°), nicht auf der Grenze: Die Hülle wird nach außen um ein Feld geglättet (Maximum der Nachbarn, `Haarklemme.__init__`),
        # ein Punkt genau auf der Grenze zwischen belegter und leerer Hälfte (Azimut 0°/180°) wird deshalb mitgeklemmt.
        vorn_leer = np.array([[0.2, 1.6, 0.0], [-0.2, 1.6, 0.0]])
        neu, anzahl, _w = klemme.klemmen(vorn_leer)
        self.assertEqual(anzahl, 1)                     # eines liegt in der leeren Hälfte, eines in der belegten
        np.testing.assert_allclose(neu[0], vorn_leer[0])
        self.assertFalse(np.allclose(neu[1], vorn_leer[1]))

    def test_bart_und_koerper_werden_nicht_geklemmt(self):
        klemme = Haarklemme(_kugelhuelle(0.10), self.MITTE)
        weit = np.array([[0.0, 1.6 + 0.3, 0.0], [0.0, 1.6, 0.3], [0.1, 1.6, 0.0]])
        bart = {'art': 'haar', 'sorte': 'mavick_beard', 'punkte': weit.copy()}
        koerper = {'art': 'koerper', 'sorte': 'koerper', 'punkte': weit.copy()}
        haar = {'art': 'haar', 'sorte': 'mavick_hair', 'punkte': weit.copy()}
        aus = klemme.anwenden([bart, koerper, haar])
        np.testing.assert_allclose(aus[0]['punkte'], weit)
        np.testing.assert_allclose(aus[1]['punkte'], weit)
        self.assertLess(float(np.abs(aus[2]['punkte'][:, 1] - 1.6).max()), 0.2)
        np.testing.assert_allclose(haar['punkte'], weit)            # das Original bleibt (der Teilevorrat hält es)

    def test_straehnen_werden_mitgeklemmt(self):
        klemme = Haarklemme(_kugelhuelle(0.10), self.MITTE)
        kurve = {'punkte': np.array([[0.0, 1.9, 0.0]], dtype=np.float32), 'reihe': np.array([0])}
        teil = {'art': 'haar', 'sorte': 'x', 'punkte': np.array([[0.0, 1.9, 0.0]]), 'kurven': kurve}
        aus = klemme.anwenden([teil])[0]
        self.assertLess(float(aus['kurven']['punkte'][0, 1]), 1.72)
        self.assertEqual(aus['kurven']['punkte'].dtype, np.float32)

    def test_die_huelle_laeuft_um_den_azimut_herum(self):
        karte = _kugelhuelle(0.10)
        karte[:, 0] = 0.20                              # nur das erste Azimutfeld (0–5°) ist weiter
        klemme = Haarklemme(karte, self.MITTE)
        nahe_359 = np.array([[np.sin(np.radians(359.5)) * 0.15, 1.6, np.cos(np.radians(359.5)) * 0.15]])
        neu, anzahl, _w = klemme.klemmen(nahe_359)
        self.assertEqual(anzahl, 0)                     # dort gilt 0,20 (Nachbarfeld über die Naht), 0,15 liegt darunter


class DasHemdDerBibliothek(SimpleTestCase):
    STUECKE = {'oberteil': 'eigen_foto_o', 'hose': 'eigen_foto_h', 'socken': 'eigen_foto_s'}

    def test_mit_oberteil_tauscht_nur_das_oberteil(self):
        self.assertEqual(Kleiderwahl.mit_oberteil(self.STUECKE, 'bibliothek'), {'oberteil': Kleiderwahl.OBERTEIL, 'hose': 'eigen_foto_h', 'socken': 'eigen_foto_s'})
        self.assertEqual(Kleiderwahl.mit_oberteil(self.STUECKE, 'foto'), self.STUECKE)
        self.assertEqual(self.STUECKE['oberteil'], 'eigen_foto_o')              # die Eingabe bleibt

    def test_ohne_fotooberteil_bleibt_alles(self):
        ohne = {'hose': 'eigen_foto_h'}
        self.assertEqual(Kleiderwahl.mit_oberteil(ohne, 'bibliothek'), ohne)
        self.assertEqual(Kleiderwahl.mit_oberteil(None, 'bibliothek'), None)

    def test_die_option_hat_die_vorgabe_bibliothek_und_prueft_ihren_wert(self):
        self.assertEqual(Engine2d3dKleiderkoerperoptionen.vorgaben()['oberteil'], 'bibliothek')
        self.assertEqual(Engine2d3dKleiderkoerperoptionen.pruefen({'oberteil': 'foto'})['oberteil'], 'foto')
        self.assertEqual(Engine2d3dKleiderkoerperoptionen.pruefen({'oberteil': 'quatsch'})['oberteil'], 'bibliothek')
        self.assertEqual(Engine2d3dKleiderkoerperoptionen.oberteil(SimpleNamespace(optionen={'koerper': {'oberteil': 'foto'}})), 'foto')
        self.assertEqual(Engine2d3dKleiderkoerperoptionen.oberteil(SimpleNamespace(optionen=None)), 'bibliothek')

    @staticmethod
    def _job(oberteil):
        return SimpleNamespace(kennung='x', ergebnis={'fotostuecke': {'stuecke': dict(DasHemdDerBibliothek.STUECKE), 'stand': [1]}},
                               stellung=lambda: {}, optionen={'koerper': {'oberteil': oberteil}})

    def test_das_standmodell_traegt_das_genesis_hemd_in_der_farbe_des_fotos(self):
        with mock.patch.object(Standvorabkleider, 'hemdfarbe', return_value=[0.31, 0.29, 0.28]):
            kleidung = Standvorabkleider.modell(self._job('bibliothek'))['kleidung']
        self.assertEqual(kleidung['sorte.' + Kleiderwahl.OBERTEIL], 1.0)         # nicht abgelegt: es IST das Hemd
        self.assertNotIn('sorte.eigen_foto_o', kleidung)
        self.assertEqual(kleidung['sorte.eigen_foto_h'], 1.0)
        self.assertGreater(kleidung['%s.bild.grau' % Kleiderwahl.OBERTEIL], 0.0)    # Daz-Farbe durch Grau ersetzt, dann getönt

    def test_mit_der_wahl_foto_bleibt_das_fotostueck_und_das_standardhemd_liegt_ab(self):
        kleidung = Standvorabkleider.modell(self._job('foto'))['kleidung']
        self.assertEqual(kleidung['sorte.eigen_foto_o'], 1.0)
        self.assertEqual(kleidung['sorte.' + Kleiderwahl.OBERTEIL], 0.0)

    def test_die_fassung_haengt_an_der_wahl(self):
        self.assertNotEqual(Standvorabkleider.fingerabdruck(self._job('bibliothek')), Standvorabkleider.fingerabdruck(self._job('foto')))


class DieStraehnengruppenDerFrisur(SimpleTestCase):
    @staticmethod
    def _flach(farbe, gleich):
        grund = np.ones((4, 4, 3), dtype=np.float32) * np.asarray(farbe, dtype=np.float32)
        return float((G9texturschicht.grau(grund, 1.0, flach=True, gleich=gleich) @ np.asarray(G9texturschicht.HELLIGKEIT, dtype=np.float32)).mean())

    def test_ohne_gleich_bleibt_die_staffelung(self):
        self.assertAlmostEqual(self._flach((0.19, 0.19, 0.19), 0.0), 0.19, places=4)

    def test_mit_gleich_eins_sind_alle_gruppen_gleich_hell(self):
        self.assertAlmostEqual(self._flach((0.19, 0.19, 0.19), 1.0), G9texturschicht.GRAU_MITTEL, places=3)
        self.assertAlmostEqual(self._flach((0.60, 0.60, 0.60), 1.0), G9texturschicht.GRAU_MITTEL, places=3)

    def test_dazwischen_liegt_es_geometrisch_dazwischen(self):
        mitte = self._flach((0.19, 0.19, 0.19), 0.6)
        self.assertAlmostEqual(mitte, 0.19 ** 0.4 * G9texturschicht.GRAU_MITTEL ** 0.6, places=3)
        self.assertTrue(0.19 < mitte < G9texturschicht.GRAU_MITTEL)

    def test_die_schicht_ist_gueltig_und_ohne_datei(self):
        from Genesis9.kleidtexturen import G9kleidtexturen
        self.assertTrue(G9kleidtexturen.NAME.match('grau_gleich'))
        self.assertIn('grau_gleich', G9kleidtexturen.OHNE_DATEI)
        self.assertEqual(G9kleidtexturen.art_von('grau_gleich'), 'grau')
