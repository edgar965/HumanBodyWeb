"""„Haar – Generisch" und die Formachsen (30.09.2026) — Sammeleintrag, Umleitung, Parametersatz.

Edgar: „Ich brauche ein neues Asset: Genesis – Generic Hair … Darin sollen ALLE aktuellen Genesis Haare
mit ihren Morphs zusammengefasst werden" und „an erster Stelle mit dem Namen Haar - Generisch".

Alles an einer erfundenen Garderobe (`mock.patch.object`), ohne Daz-Bibliothek, ohne Datenbank, ohne GPU:
Die echte Liste kostet Sekunden und hängt daran, was auf dem Rechner installiert ist.
"""

import unittest
from pathlib import Path
from unittest import mock

import numpy as np
from Genesis9.haarachsen import G9haarachsen
from Genesis9.haargenerisch import G9haargenerisch
from Genesis9.pfade import G9pfade

from ._pruefablage import Pruefablage

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
        # Ohne eigene Genesis-Daten (`3DObjects/models/Genesis9`): Seit dem 08.10.2026 liest der Code dort wirklich, und die
        # Zusatzsträhnen (`str.*`) der echten Ablage machten aus 26 Reglern 38 — der Test prüfte Edgars Bestand.
        self.daten = mock.patch.object(G9pfade, 'eigene_daten',
                                       classmethod(lambda cls: Path(Pruefablage.wurzel()) / 'ohne_genesis9_daten'))
        self.daten.start()
        self.addCleanup(self.daten.stop)
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
        # Dazu die festen Operationen (`G9standardmorphe.HAAR`, 30.09.2026 nachts) und die vier Ortsregler der Mischung.
        from Genesis9.haarprofil import G9haarprofil
        from Genesis9.standardmorphe import G9standardmorphe
        # Seit 01.10.2026 dazu die Strähnendicke (`G9haarprofil`, 2 Regler); Zusatzsträhnen (`str.*`) nur mit Ablage.
        self.assertEqual(len(kin), 1 + 1 + len(G9haarachsen.KANAELE) + len(G9standardmorphe.HAAR)
                         + len(G9haargenerisch.ORT_REGLER) + len(G9haarprofil.REGLER))
        self.assertIn('kin_hair.eigen.op_trim', kin)
        self.assertIn('kin_hair.ort.sektor_a', kin)

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

    def test_5a_ein_kleiner_anteil_verdraengt_die_getragene_frisur_nicht(self):
        """Edgar, 30.09.2026: „falls ich den Anteil eines anderen Haartyps minimal einfüge,
        ist der Original Type weg, und nur noch der neue Haartyp ist drin". Die Grundsorte
        trägt voll (1,0) — 5 % einer anderen schlagen sie nicht."""
        self.assertEqual(G9haargenerisch.sorte({'sorte.toulouse_hair': 0.05}), 'kin_hair')
        self.assertEqual(G9haargenerisch.sorte({'sorte.toulouse_hair': 0.99}), 'kin_hair')

    def test_5b_ganz_aufgedreht_wechselt_die_frisur(self):
        """Sonst käme man nie von der Grundsorte weg. Bei Gleichstand gewinnt die
        ausdrücklich gestellte — die hat der Nutzer gerade angefasst."""
        self.assertEqual(G9haargenerisch.sorte({'sorte.toulouse_hair': 1.0}), 'toulouse_hair')

    def test_5c_die_grundsorte_laesst_sich_herunterdrehen(self):
        """Wer Kin ausdrücklich auf 0 stellt, trägt Toulouse — auch mit wenig Anteil."""
        self.assertEqual(
            G9haargenerisch.sorte({'sorte.kin_hair': 0.0, 'sorte.toulouse_hair': 0.2}),
            'toulouse_hair')

    def test_5d_der_regler_der_grundsorte_steht_sichtbar_auf_hundert_prozent(self):
        """Der Wert, mit dem gerechnet wird, muss der sein, den der Regler zeigt."""
        regler = {r['name']: r for r in G9haargenerisch.regler()}
        self.assertEqual(regler['sorte.kin_hair']['vorgabe'], 1.0)
        self.assertEqual(regler['sorte.toulouse_hair']['vorgabe'], 0.0)

    def test_5e_eine_kennung_die_es_nicht_mehr_gibt_faellt_weg(self):
        """Ein alter Wertesatz kann Frisuren nennen, die aus der Bibliothek verschwunden sind."""
        self.assertEqual(G9haargenerisch.sorte({'sorte.weg_damit': 1.0}), 'kin_hair')

    def test_6_ist_generisch(self):
        self.assertTrue(G9haargenerisch.ist_generisch('haar_generisch'))
        self.assertFalse(G9haargenerisch.ist_generisch('kin_hair'))
        self.assertFalse(G9haargenerisch.ist_generisch(None))

    # ---- Mischung (Edgar, 30.09.2026: „Summe aller Anteile immer 100%") -------

    def test_7a_die_anteile_ergeben_zusammen_eins(self):
        """70 : 30, wie der Browser es nach einem Zug schickt."""
        anteile = G9haargenerisch.anteile({'sorte.kin_hair': 0.7, 'sorte.toulouse_hair': 0.3})
        self.assertAlmostEqual(anteile['kin_hair'], 0.7)
        self.assertAlmostEqual(anteile['toulouse_hair'], 0.3)
        self.assertAlmostEqual(sum(anteile.values()), 1.0)

    def test_7b_ein_alter_wertesatz_wird_auf_hundert_prozent_gebracht(self):
        """Aus der Rangfolge-Zeit: beide auf 1,0 — das sind jetzt je 50 %, nicht 200 %."""
        anteile = G9haargenerisch.anteile({'sorte.kin_hair': 1.0, 'sorte.toulouse_hair': 1.0})
        self.assertAlmostEqual(anteile['kin_hair'], 0.5)
        self.assertAlmostEqual(anteile['toulouse_hair'], 0.5)

    def test_7c_die_grundsorte_steht_ohne_angabe_auf_ihrer_vorgabe(self):
        """Nicht gestellt heisst 1,0 — genau das, was ihr Regler zeigt."""
        anteile = G9haargenerisch.anteile({'sorte.toulouse_hair': 1.0 / 3.0})
        self.assertAlmostEqual(anteile['kin_hair'], 0.75)
        self.assertAlmostEqual(anteile['toulouse_hair'], 0.25)

    def test_7d_alles_auf_null_wird_nicht_kahl(self):
        anteile = G9haargenerisch.anteile({'sorte.kin_hair': 0.0, 'sorte.toulouse_hair': 0.0})
        self.assertEqual(anteile, {'kin_hair': 1.0})

    def test_7e_die_mischung_nennt_die_hauptsorte_zuerst(self):
        """Die erste Sorte bringt ihre Kappe mit (`G9haarmischbau`)."""
        folge = G9haargenerisch.mischung({'sorte.kin_hair': 0.3, 'sorte.toulouse_hair': 0.7})
        self.assertEqual([k for k, _, _ in folge], ['toulouse_hair', 'kin_hair'])

    def test_7f_jede_sorte_bekommt_ihre_regler_ohne_praefix(self):
        folge = dict((k, r) for k, _, r in G9haargenerisch.mischung({
            'sorte.kin_hair': 0.6, 'sorte.toulouse_hair': 0.4,
            'kin_hair.Bangs': 0.5, 'toulouse_hair.Volume': 1.2, 'toulouse_hair.achse.laenge': 0.3}))
        self.assertEqual(folge['kin_hair'], {'Bangs': 0.5})
        self.assertEqual(folge['toulouse_hair'], {'Volume': 1.2, 'achse.laenge': 0.3})

    def test_7g_bei_gleichstand_zaehlt_die_zuletzt_bewegte(self):
        folge = G9haargenerisch.mischung({'sorte.kin_hair': 0.5, 'sorte.toulouse_hair': 0.5,
                                          'sorte_zuletzt': 'kin_hair'})
        self.assertEqual(folge[0][0], 'kin_hair')
        folge = G9haargenerisch.mischung({'sorte.kin_hair': 0.5, 'sorte.toulouse_hair': 0.5})
        self.assertEqual(folge[0][0], 'toulouse_hair')     # die Grundsorte tritt zurück

    def test_7h_der_eintrag_ist_als_mischbar_markiert(self):
        """„Kleidung – Generisch" nutzt `sorte.*` als WAHL und traegt das Zeichen nicht —
        nur hier zieht der Browser die anderen Regler nach."""
        self.assertTrue(G9haargenerisch.eintrag()['mischbar'])


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
