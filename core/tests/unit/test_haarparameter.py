"""`Haarparameter` seit dem 30.09.2026 — der Wertesatz kommt aus der Garderobe, nicht aus dem Code.

Der entscheidende Punkt: Ein Schlüssel heißt `<frisur>.<maß>`, und dazu gibt es den Schalter
`<frisur>.an`. Nur deshalb fasst `Iterationsoptimierer.veraenderlich` die Maße einer ausgeschalteten
Frisur nicht an — von rund 400 Maßen bleiben je Runde die der getragenen übrig.

Mit einer erfundenen Garderobe (`mock.patch.object`), ohne Daz-Bibliothek und ohne GPU.
"""

import unittest
from unittest import mock

from core.dienste.haarparameter import Haarparameter
from core.dienste.iterationsoptimierer import Iterationsoptimierer

#: (kennung, name, [(kanal, anzeige, min, max)]) — die Form, die `Haarparameter.frisuren` liefert.
FRISUREN = [
    ('kin_hair', 'Kin Hair', [('Bangs', 'Bangs', -1.0, 1.0)]),
    ('toulouse_hair', 'Toulouse Hair', [('Volume', 'Volume', 0.0, 2.0)]),
]


class ParametersatzTest(unittest.TestCase):

    def setUp(self):
        Haarparameter.vergessen()
        self.addCleanup(Haarparameter.vergessen)
        self.p = mock.patch.object(Haarparameter, 'frisuren', classmethod(lambda cls: FRISUREN))
        self.p.start()
        self.addCleanup(self.p.stop)
        from Genesis9.haarachsen import G9haarachsen
        self.a = mock.patch.object(G9haarachsen, 'vorhanden', classmethod(lambda cls, k: True))
        self.a.start()
        self.addCleanup(self.a.stop)

    def test_1_je_frisur_ein_schalter_und_ihre_masse(self):
        s = Haarparameter.schema()
        self.assertEqual(s['kin_hair.an']['art'], 'schalter')
        self.assertEqual(s['toulouse_hair.an']['art'], 'schalter')
        self.assertIn('kin_hair.morph.Bangs', s)
        self.assertIn('kin_hair.achse.laenge', s)
        self.assertIn('toulouse_hair.morph.Volume', s)
        # Die Farbe hängt an keiner Frisur.
        self.assertIn('farbe.haar.r', s)

    def test_2_genau_eine_frisur_ist_am_anfang_an(self):
        start = Haarparameter.start()
        an = [k for k in start if k.endswith('.an') and start[k] >= 0.5]
        self.assertEqual(an, ['kin_hair.an'])
        self.assertEqual(Haarparameter.getragene(start), 'kin_hair')

    def test_3_die_grenzen_des_echten_morphs_bleiben(self):
        s = Haarparameter.schema()
        self.assertEqual((s['toulouse_hair.morph.Volume']['min'],
                          s['toulouse_hair.morph.Volume']['max']), (0.0, 2.0))
        self.assertEqual((s['kin_hair.morph.Bangs']['min'],
                          s['kin_hair.morph.Bangs']['max']), (-1.0, 1.0))

    def test_4_der_titel_nennt_die_frisur(self):
        """Die Titel gehen wörtlich an die Prüf-KI — ohne den Namen wüsste sie nicht, wozu ein Maß gehört."""
        s = Haarparameter.schema()
        self.assertEqual(s['kin_hair.morph.Bangs']['titel'], 'Kin Hair: Bangs')
        self.assertEqual(s['kin_hair.achse.laenge']['titel'], 'Kin Hair: Form Länge')
        self.assertIn('Kin Hair', s['kin_hair.an']['titel'])

    def test_5_der_optimierer_fasst_nur_die_getragene_frisur_an(self):
        werte = Haarparameter.start()
        veraenderlich = Iterationsoptimierer.veraenderlich(werte)
        self.assertTrue(all(k.startswith('kin_hair.') for k in veraenderlich), veraenderlich)
        self.assertEqual(len(veraenderlich), 1 + 5)          # ein Morph, fünf Achsen
        # Umschalten verschiebt die Menge mit.
        andere = dict(werte, **{'kin_hair.an': 0, 'toulouse_hair.an': 1})
        veraenderlich = Iterationsoptimierer.veraenderlich(andere)
        self.assertTrue(all(k.startswith('toulouse_hair.') for k in veraenderlich), veraenderlich)

    def test_6_farben_wuerfelt_der_optimierer_nicht(self):
        self.assertTrue(Iterationsoptimierer.FARBEN_FEST)
        self.assertFalse([k for k in Iterationsoptimierer.veraenderlich(Haarparameter.start())
                          if k.startswith('farbe.')])

    def test_7_pruefen_zieht_auf_die_grenzen_und_macht_schalter_ganz(self):
        aus = Haarparameter.pruefen({'toulouse_hair.morph.Volume': 99.0,
                                     'kin_hair.morph.Bangs': -5.0,
                                     'kin_hair.achse.laenge': 0.25,
                                     'kin_hair.an': 0.7, 'unbekannt': 1.0})
        self.assertEqual(aus['toulouse_hair.morph.Volume'], 2.0)
        self.assertEqual(aus['kin_hair.morph.Bangs'], -1.0)
        self.assertEqual(aus['kin_hair.achse.laenge'], 0.25)
        self.assertEqual(aus['kin_hair.an'], 1)
        self.assertNotIn('unbekannt', aus)
        self.assertEqual(set(aus), set(Haarparameter.schema()))   # vollständig

    def test_8_getragene_nimmt_die_erste_der_garderobe(self):
        """Zwei Netze lassen sich nicht mischen — steht mehr als eine an, gewinnt die erste."""
        werte = {'kin_hair.an': 1, 'toulouse_hair.an': 1}
        self.assertEqual(Haarparameter.getragene(werte), 'kin_hair')
        self.assertIsNone(Haarparameter.getragene({'kin_hair.an': 0}))

    def test_9_ohne_bibliothek_bleibt_alles_leer(self):
        """Auf einem Rechner ohne Daz-Bibliothek darf nichts krachen — nur die Farbe bleibt."""
        with mock.patch.object(Haarparameter, 'frisuren', classmethod(lambda cls: [])):
            Haarparameter.vergessen()
            s = Haarparameter.schema()
            self.assertEqual({k for k in s if not k.startswith('farbe.')}, set())


if __name__ == '__main__':
    unittest.main()
