"""„Haar – Generisch" und die Formachsen (30.09.2026) — Sammeleintrag, Umleitung, Parametersatz.

Edgar: „Ich brauche ein neues Asset: Genesis – Generic Hair … Darin sollen ALLE aktuellen Genesis Haare
mit ihren Morphs zusammengefasst werden" und „an erster Stelle mit dem Namen Haar - Generisch".

Alles an einer erfundenen Garderobe (`mock.patch.object`), ohne Daz-Bibliothek, ohne Datenbank, ohne GPU:
Die echte Liste kostet Sekunden und hängt daran, was auf dem Rechner installiert ist.
"""

import unittest
from unittest import mock

import numpy as np
from Genesis9.haarachsen import G9haarachsen
from Genesis9.haargenerisch import G9haargenerisch

#: Zwei Frisuren, wie sie in der Garderobenliste stehen (`G9garderobeeintrag`).
FRISUREN = [
    {'id': 'kin_hair', 'name': 'Kin Hair', 'art': 'haar', 'zeigbar': True,
     'regler': [{'name': 'Bangs', 'anzeige': 'Bangs', 'min': -1.0, 'max': 1.0, 'vorgabe': 0.0,
                 'gruppe': 'Movement'}]},
    {'id': 'toulouse_hair', 'name': 'Toulouse Hair', 'art': 'haar', 'zeigbar': True,
     'regler': [{'name': 'Volume', 'anzeige': 'Volume', 'min': 0.0, 'max': 2.0, 'vorgabe': 0.0,
                 'gruppe': 'Style'}]},
]


class SammeleintragTest(unittest.TestCase):
    """Der Eintrag, den die Garderobenliste zusätzlich führt."""

    def setUp(self):
        self.frisuren = mock.patch.object(G9haargenerisch, 'frisuren', classmethod(lambda cls: FRISUREN))
        self.frisuren.start()
        self.addCleanup(self.frisuren.stop)
        self.achsen = mock.patch.object(G9haarachsen, 'vorhanden', classmethod(lambda cls, k: True))
        self.achsen.start()
        self.addCleanup(self.achsen.stop)

    def test_1_eintrag_sieht_aus_wie_ein_stueck(self):
        e = G9haargenerisch.eintrag()
        self.assertEqual(e['id'], 'haar_generisch')
        self.assertEqual(e['name'], 'Haar – Generisch')
        self.assertEqual(e['art'], 'haar')          # sonst landet er nicht in der Kategorie „Haare"
        self.assertTrue(e['zeigbar'])
        self.assertEqual(e['sorten'], 2)
        # Kein eigenes Netz: Farbvarianten und Stile führt er bewusst nicht.
        self.assertEqual(e['varianten'], [])
        self.assertEqual(e['stile'], [])

    def test_2_je_frisur_eine_gruppe_mit_anteil_morphs_und_achsen(self):
        regler = G9haargenerisch.eintrag()['regler']
        gruppen = {}
        for r in regler:
            gruppen.setdefault(r['gruppe'], []).append(r['name'])
        self.assertEqual(set(gruppen), {'Kin Hair', 'Toulouse Hair'})
        kin = gruppen['Kin Hair']
        self.assertEqual(kin[0], 'sorte.kin_hair')              # der Anteil steht oben
        self.assertIn('kin_hair.Bangs', kin)                    # der echte Daz-Morph
        self.assertIn('kin_hair.achse.laenge', kin)             # die gemeinsame Formachse
        self.assertEqual(len(kin), 1 + 1 + len(G9haarachsen.KANAELE))

    def test_3_die_grenzen_des_echten_morphs_bleiben(self):
        regler = {r['name']: r for r in G9haargenerisch.eintrag()['regler']}
        self.assertEqual((regler['toulouse_hair.Volume']['min'],
                          regler['toulouse_hair.Volume']['max']), (0.0, 2.0))
        self.assertEqual((regler['toulouse_hair.achse.dutt']['min'],
                          regler['toulouse_hair.achse.dutt']['max']), (0.0, 1.0))

    def test_4_aufloesen_nimmt_den_groessten_anteil(self):
        kennung, werte = G9haargenerisch.aufloesen({
            'sorte.kin_hair': 0.3, 'sorte.toulouse_hair': 0.9,
            'toulouse_hair.Volume': 1.5, 'kin_hair.Bangs': 1.0})
        self.assertEqual(kennung, 'toulouse_hair')
        # Das Präfix ist weg, und die Regler der ANDEREN Frisur sind nicht dabei.
        self.assertEqual(werte, {'Volume': 1.5})

    def test_5_ohne_anteil_gilt_die_vorgabe(self):
        kennung, werte = G9haargenerisch.aufloesen({})
        self.assertEqual(kennung, G9haargenerisch.VORGABE)
        self.assertEqual(werte, {})

    def test_6_ist_generisch(self):
        self.assertTrue(G9haargenerisch.ist_generisch('haar_generisch'))
        self.assertFalse(G9haargenerisch.ist_generisch('kin_hair'))
        self.assertFalse(G9haargenerisch.ist_generisch(None))


class AchsenTest(unittest.TestCase):
    """Die Formachsen als Deltas — Reglerform und Anwenden."""

    def test_1_fuenf_regler_in_der_gruppe_form(self):
        regler = G9haarachsen.regler()
        self.assertEqual(len(regler), 5)
        self.assertEqual({r['gruppe'] for r in regler}, {'Form'})
        self.assertEqual([r['name'] for r in regler],
                         ['achse.laenge', 'achse.kurz', 'achse.dichte', 'achse.wellig', 'achse.dutt'])
        for r in regler:
            self.assertEqual((r['min'], r['max'], r['vorgabe']), (0.0, 1.0, 0.0))

    def test_2_werte_zieht_auf_null_bis_eins_und_laesst_fremdes_liegen(self):
        werte = G9haarachsen.werte({'achse.laenge': 2.0, 'achse.kurz': -1.0, 'achse.dutt': 0.4,
                                    'Bangs': 1.0, 'achse.wellig': 0.0})
        self.assertEqual(werte, {'laenge': 1.0, 'dutt': 0.4})   # gekappt; 0 und Fremdes fallen weg

    def test_3_anwenden_addiert_je_teil_und_laesst_ungenannte_punkte_stehen(self):
        punkte = np.zeros((4, 3))
        delta = np.array([[0.0, -0.5, 0.0]])
        folger = mock.Mock(kennung='geo1')
        teile = [(folger, None)]
        with mock.patch.object(G9haarachsen, 'deltas', classmethod(
                lambda cls, k: {'geo1': {'laenge': (np.array([2]), delta)}})):
            aus = G9haarachsen.anwenden('x', teile, [punkte], {'laenge': 1.0})
        self.assertEqual(len(aus), 1)
        np.testing.assert_allclose(aus[0][2], [0.0, -0.5, 0.0])
        np.testing.assert_allclose(aus[0][[0, 1, 3]], np.zeros((3, 3)))
        np.testing.assert_allclose(punkte, np.zeros((4, 3)))    # das Original bleibt unberührt

    def test_4_halber_wert_ist_der_halbe_weg(self):
        """Daz-Morphe sind linear — darauf beruht der Deltavorrat der Engine."""
        punkte = np.zeros((2, 3))
        delta = np.array([[0.0, -1.0, 0.0]])
        folger = mock.Mock(kennung='geo1')
        with mock.patch.object(G9haarachsen, 'deltas', classmethod(
                lambda cls, k: {'geo1': {'laenge': (np.array([0]), delta)}})):
            halb = G9haarachsen.anwenden('x', [(folger, None)], [punkte], {'laenge': 0.5})
        np.testing.assert_allclose(halb[0][0], [0.0, -0.5, 0.0])

    def test_5_ohne_werte_und_ohne_ablage_bleiben_die_punkte(self):
        punkte = np.ones((3, 3))
        folger = mock.Mock(kennung='geo1')
        self.assertIs(G9haarachsen.anwenden('x', [(folger, None)], [punkte], {})[0], punkte)
        with mock.patch.object(G9haarachsen, 'deltas', classmethod(lambda cls, k: None)):
            self.assertIs(G9haarachsen.anwenden('x', [(folger, None)], [punkte],
                                                {'laenge': 1.0})[0], punkte)

    def test_6_die_fassung_steht_im_dateinamen(self):
        """Sonst liest ein späterer Lauf still die Deltas eines anderen Stands
        (`~/.claude/rules/artefakte-benennen.md`)."""
        pfad = G9haarachsen._pfad('kin_hair', '.npz')
        self.assertIn('_f%d' % G9haarachsen.FASSUNG, pfad.name)
        self.assertTrue(pfad.name.startswith('kin_hair_f'))


if __name__ == '__main__':
    unittest.main()
