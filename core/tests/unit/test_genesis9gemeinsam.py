# -*- coding: utf-8 -*-
"""„Gemeinsam anziehen" auf Genesis 9 — der Weg nimmt die Figur der Szene.

Edgar, 20.09.2026, mit Bild („funktioniert auch nicht"): Auf Kin1 drapierte
der gemeinsame Lauf Hose und T-Shirt auf der HumanBody-Figur
(`figur_39afa3ff2d9c`), weil der Endpunkt `figurart`/`regler_figur` nicht
weiterreichte. Hier mit Attrappen: `Genesis9gemeinsam.lauf` holt Figur,
Masse und Koerperablage von `Genesis9drapierung`, baut die Schnitte und
die eine Drapierung ueber `Garmentgemeinsam`, verteilt auf den
Genesis-9-Traeger und nennt die Figurart im Ergebnis; der Endpunkt
verzweigt an `figurart`.
"""

import sys
from unittest import mock

from django.conf import settings
from django.test import SimpleTestCase

if str(settings.ASSETS_ROOT) not in sys.path:  # pragma: no cover
    sys.path.insert(0, str(settings.ASSETS_ROOT))

from GarmentCode.genesis9gemeinsam import Genesis9gemeinsam  # noqa: E402


class Figurattrappe:
    def punkte(self):
        return 'roh'

    def projekt(self, punkte):
        return 'projekt_' + str(punkte)

    def dreiecke(self):
        return 'dreiecke'

    def geschlecht(self):
        return 'female'

    def sichtbar(self):
        return ('fein_p', [[0, 1, 2]])

    def haut(self):
        return {'index': [[0, 1]], 'gewicht': [[0.5, 0.5]], 'knochen': ['hip', 'chest']}


class Genesis9gemeinsamTest(SimpleTestCase):
    databases = set()

    def test_der_lauf_nimmt_die_genesis_figur_und_ihren_traeger(self):
        stuecke = [{'vorlage': 'hose', 'regler': {}}, {'vorlage': 'oberteil', 'regler': {}}]
        figur = Figurattrappe()
        with mock.patch('GarmentCode.genesis9drapierung.Genesis9drapierung.figur',
                        return_value=figur), \
                mock.patch('GarmentCode.genesis9drapierung.Genesis9drapierung.masse',
                           return_value=({'height': 172.0}, {})), \
                mock.patch('GarmentCode.genesis9drapierung.Genesis9drapierung.bereitstellen',
                           return_value={'name': 'genesis9_abc', 'ordner': 'k'}) as bereit, \
                mock.patch('GarmentCode.gemeinsamdienst.Garmentgemeinsam._pruefen',
                           return_value=stuecke), \
                mock.patch('GarmentCode.gemeinsamdienst.Garmentgemeinsam._schnitte',
                           return_value=['s1', 's2']) as schnitte, \
                mock.patch('GarmentCode.gemeinsamdienst.Garmentgemeinsam._drapieren',
                           return_value={'netz': 'n.obj'}) as drapieren, \
                mock.patch('GarmentCode.gemeinsamablage.Gemeinsamablage.verteilen_auf',
                           return_value=['b1', 'b2']) as verteilen:
            ergebnis = Genesis9gemeinsam.lauf(stuecke, {'a': 1})
        bereit.assert_called_once_with(figur, 'projekt_roh', 'dreiecke', {'height': 172.0}, None)
        # Der Ordner traegt die Figurart — nicht dieselbe Ablage wie HumanBody.
        marke = schnitte.call_args[0][2]
        self.assertTrue(marke.startswith('gemeinsam_genesis9_female_'), marke)
        drapieren.assert_called_once_with(['s1', 's2'], marke, {'name': 'genesis9_abc', 'ordner': 'k'})
        traeger = verteilen.call_args[0][2]
        self.assertEqual((traeger.name, traeger.knochen), ('Genesis 9', ['hip', 'chest']))
        self.assertEqual(traeger.gewichte, [[[0, 0.5], [1, 0.5]]])
        self.assertEqual(traeger.sichtbar[0], 'projekt_fein_p')
        self.assertEqual(ergebnis['figurart'], 'genesis9')
        self.assertEqual(ergebnis['stuecke'], ['b1', 'b2'])

    def test_der_endpunkt_verzweigt_an_der_figurart(self):
        from core.api import garmentgemeinsam

        quelle = open(garmentgemeinsam.__file__, encoding='utf-8').read()
        self.assertIn("if anfrage.figurart == 'genesis9':", quelle)
        self.assertIn('Genesis9gemeinsam.lauf(', quelle)
        self.assertIn("'figurart': ergebnis.get('figurart')", quelle)
