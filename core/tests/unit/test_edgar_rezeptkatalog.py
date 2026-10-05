# -*- coding: utf-8 -*-
"""Paket `Edgar`: `Rezeptkatalog` — der Abschnitt „Was es gibt" des Nachbesserungsprompts (05.10.2026).

Kunstdaten im Aufbau von `GET …/rezeptkatalog/` (`Engine2d3dKleiderrezeptkatalog`). Ohne Django-Datenbank, ohne Server. Geschrieben, nicht gelaufen (`testsuite-nur-auf-ansage`).
"""

from django.test import SimpleTestCase
from Edgar.rezeptkatalog import Rezeptkatalog

DATEN = {
    'auftrag': {'fotostuecke': {'oberteil': 'eigen_foto_a_oberteil', 'hose': 'eigen_foto_a_hose', 'socken': 'eigen_foto_a_socken'}, 'hemd': 'g9_base_shirt', 'startfrisur': 'mavick_hair',
                'kandidaten': ['mavick_hair', 'basic_hair'], 'frisur': {'kennung': 'mavick_hair_style', 'regler': {'ExpandAll': -0.25}, 'farbe': '#595150'}},
    'startrezept': ["m.kleid_nur('g9_base_shirt', 'eigen_foto_a_hose')", "m.haar_nur('mavick_hair_style')"],
    'garderobe': {'kleidung': ['g9_base_shirt', 'angie_jeans'], 'haar': ['mavick_hair'], 'eigene': ['eigen_uhr_l'], 'requisiten': ['staff_l']},
    'regler': {'g9_base_shirt': [{'name': 'body_bs_ExpandAll', 'min': 0.0, 'max': 1.0}]},
    'koerper': {'body_ctrl_': [{'name': 'body_ctrl_BodyMuscular', 'min': 0.0, 'max': 1.0}], 'body_bs_': [{'name': 'body_bs_MassShoulders', 'min': -1.0, 'max': 1.0}]},
    'schnitt': {'hose': {'formen': [], 'regler': [{'pfad': 'pants.flare', 'typ': 'float', 'bereich': [0.5, 1.2], 'wert': 1.0}, {'pfad': 'left.pants.x', 'typ': 'float', 'bereich': [0, 1], 'wert': 0}]},
                'schuh': {'formen': [{'schluessel': 'form_socke', 'titel': 'Socke'}], 'regler': [{'pfad': 'shoe.toe', 'typ': 'select', 'bereich': ['round', 'pointed'], 'wert': 'round'}]}},
    'fehler': [],
}


class DerRezeptkatalog(SimpleTestCase):
    def test_der_text_nennt_stuecke_haare_regler_koerper_und_schnitte_mit_ihren_namen(self):
        text = Rezeptkatalog(DATEN).text()
        for erwartet in ('eigen_foto_a_hose', 'angie_jeans', 'mavick_hair_style', 'body_bs_ExpandAll (0…1)', 'body_ctrl_BodyMuscular (0…1)', 'body_bs_MassShoulders',
                         'pants.flare 0.5…1.2 (Vorgabe 1)', 'form_socke (Socke)', 'shoe.toe (round|pointed)', 'eigen_uhr_l', 'staff_l', 'erfinde keinen Namen'):
            self.assertIn(erwartet, text)
        self.assertNotIn('left.pants.x', text)                                       # die linke Seite (Asymmetrie) steht nicht doppelt da
        self.assertNotIn('Startrezept', text)                                        # ohne `mit_start` kein Startrezept

    def test_mit_start_steht_das_startrezept_im_text(self):
        text = Rezeptkatalog(DATEN).text(mit_start=True)
        self.assertIn("m.kleid_nur('g9_base_shirt', 'eigen_foto_a_hose')", text)
        self.assertIn('vorangestellt', text)

    def test_zu_wenig_platz_laesst_abschnitte_vom_ende_her_weg_und_nennt_sie(self):
        text = Rezeptkatalog(DATEN).text(hoechstens=700)
        self.assertIn('Dieser Auftrag', text)                                        # der wichtigste Abschnitt bleibt
        self.assertNotIn('shoe.toe', text)
        self.assertIn('Aus Platzgründen nicht aufgeführt', text)
        self.assertIn('schnitt', text.split('Aus Platzgründen nicht aufgeführt')[1])

    def test_ein_fehler_des_servers_steht_im_text_statt_zu_verschwinden(self):
        text = Rezeptkatalog(dict(DATEN, fehler=['koerper: Datei fehlt'])).text()
        self.assertIn('Der Server konnte nicht alles lesen: koerper: Datei fehlt', text)
