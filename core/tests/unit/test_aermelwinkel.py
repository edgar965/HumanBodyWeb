# -*- coding: utf-8 -*-
"""Der Ärmel wird für den Arm geschnitten, an dem er hängt (`Aermelwinkel`, 20.10.2026).

Edgar: „fixe das" — seine Katalogstücke trugen Ärmel mit 10° (`default.yaml`), die Arme
unserer Figuren hängen bei 32° (HumanBody) bzw. 40–50° (Genesis 9); der Stoff staute sich
unter der Achsel, das Stück kam nie zur Ruhe. Ohne gestellten Regler gilt jetzt die
Armhaltung der Figur. Messungen: `Assets/GarmentCode/aermelwinkel.py`.
"""

import inspect
import sys
from unittest import mock

from django.conf import settings
from django.test import SimpleTestCase

if str(settings.ASSETS_ROOT) not in sys.path:  # pragma: no cover
    sys.path.insert(0, str(settings.ASSETS_ROOT))

from GarmentCode.aermelwinkel import Aermelwinkel  # noqa: E402
from GarmentCode.arbeiter import Arbeiter  # noqa: E402
from GarmentCode.entwurf import Entwurf  # noqa: E402

GENESIS = {'arm_pose_angle': 46.3}
WINKEL = 'sleeve.sleeve_angle'
LINKS = 'left.sleeve.sleeve_angle'


class AermelwinkelTest(SimpleTestCase):
    databases = set()

    def test_ohne_regler_gilt_die_armhaltung_der_figur(self):
        for vorlage in ('oberteil', 'kleid', 'anzug'):
            regler, hinweise = Aermelwinkel.anwenden({}, GENESIS, vorlage)
            self.assertEqual(regler.get(WINKEL), 46, vorlage)
            self.assertEqual(len(hinweise), 1, vorlage)
            self.assertIn(u'46°', hinweise[0])

    def test_unter_40_grad_bleibt_die_vorgabe_und_die_meldung_sagt_es(self):
        """HumanBody (Arm 32,6°): mit 33° mehr Stoff im Körper als mit 10° — gemessen, daher `AB_GRAD`."""
        regler, hinweise = Aermelwinkel.anwenden({}, {'arm_pose_angle': 32.4}, 'oberteil')
        self.assertNotIn(WINKEL, regler)
        self.assertEqual(len(hinweise), 1)
        self.assertIn(u'32.4°', hinweise[0])
        self.assertEqual(Aermelwinkel.anwenden({}, {'arm_pose_angle': 40.0}, 'oberteil')[0][WINKEL], 40)

    def test_ein_gestellter_wert_gilt_auch_10(self):
        regler, hinweise = Aermelwinkel.anwenden({WINKEL: 10}, GENESIS, 'oberteil')
        self.assertEqual(regler[WINKEL], 10)
        self.assertEqual(hinweise, [])

    def test_ohne_aermel_bleibt_alles(self):
        """Ärmellos (Trägertop, BH, gestellt) und ohne Oberteil (Hose): kein Winkel."""
        for vorlage, werte in (('traegertop', {}), ('unterwaesche', {}), ('hose', {}),
                               ('oberteil', {'sleeve.sleeveless': True})):
            regler, hinweise = Aermelwinkel.anwenden(werte, GENESIS, vorlage)
            self.assertNotIn(WINKEL, regler, vorlage)
            self.assertEqual(hinweise, [], vorlage)

    def test_geklemmt_auf_den_bereich_des_reglers(self):
        self.assertEqual(Aermelwinkel.anwenden({}, {'arm_pose_angle': 61.0}, 'oberteil')[0][WINKEL], 50)

    def test_der_linke_aermel_nur_bei_asymmetrie(self):
        self.assertNotIn(LINKS, Aermelwinkel.anwenden({}, GENESIS, 'oberteil')[0])
        regler, _ = Aermelwinkel.anwenden({'left.enable_asym': True, 'left.sleeve.sleeveless': False},
                                          GENESIS, 'oberteil')
        self.assertEqual(regler[LINKS], 46)

    def test_ohne_armmass_und_ohne_katalog_bleibt_alles(self):
        with self.assertLogs('GarmentCode.aermelwinkel', 'WARNING'):
            self.assertEqual(Aermelwinkel.anwenden({}, {}, 'oberteil'), ({}, []))
        self.assertEqual(Aermelwinkel.anwenden({}, GENESIS, 'gibt_es_nicht'), ({}, []))

    def test_der_schieber_zeigt_figur(self):
        self.assertEqual(Aermelwinkel.vorgabe_text(WINKEL), u'Figur')
        self.assertEqual(Aermelwinkel.vorgabe_text(LINKS), u'Figur')
        self.assertIsNone(Aermelwinkel.vorgabe_text('sleeve.length'))


class EntwurfAermelwinkelTest(SimpleTestCase):
    """`Entwurf.erzeugen` schickt den Winkel wirklich an den Schnitt (Attrappe statt Arbeiter)."""
    databases = set()

    class Attrappe:
        def __init__(self):
            self.auftraege = []

        def senden(self, auftrag):
            self.auftraege.append(auftrag)
            return {'ordner': 'x', 'dateien': [], 'hinweise': []}

    def _bauen(self, **art):
        attrappe = self.Attrappe()
        with mock.patch.object(Arbeiter, 'gemeinsam', return_value=attrappe):
            ergebnis = Entwurf('oberteil', dict(GENESIS), **art).erzeugen(name='_test_aermelwinkel')
        return attrappe.auftraege[0], ergebnis

    def test_die_attrappe_kennt_die_echte_signatur(self):
        echte = set(inspect.signature(Arbeiter.senden).parameters) - {'self'}
        self.assertEqual(echte, set(inspect.signature(self.Attrappe.senden).parameters) - {'self'})

    def test_der_winkel_geht_an_den_schnitt_und_in_die_meldung(self):
        auftrag, ergebnis = self._bauen(regler={'sleeve.length': 0.5})
        self.assertEqual(auftrag['regler'][WINKEL], 46)
        self.assertEqual(auftrag['regler']['sleeve.length'], 0.5)
        self.assertTrue(any(u'Armhaltung' in h for h in ergebnis['hinweise']))

    def test_ein_vollstaendiger_entwurf_bleibt_unberuehrt(self):
        auftrag, _ = self._bauen(entwurfswerte={'meta': {}}, regler={})
        self.assertNotIn(WINKEL, auftrag['regler'] or {})
