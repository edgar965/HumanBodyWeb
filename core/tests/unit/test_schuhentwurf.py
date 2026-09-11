# -*- coding: utf-8 -*-
u"""Der Schuh als vierter Baustein: Katalog, Regler, Titel, Erkennung.

WARUM (11.09.2026, Edgar: „es gibt bei GarmentCode keine Schuhe … Überlege
erstmal ein Konzept, wie man Schuhe als neues Item in die Liste bei
GarmentCode übernehmen könnte")
======================================================================
GarmentCodes `MetaGarment` kennt drei Bausteine. Der vierte (`meta.feet`)
liegt in `Assets/GarmentCode/schuh/` und wird über `entwuerfe/schuh.yaml`
in jeden Entwurf gemischt. Was hier festgehalten wird:

1. Der Katalog führt die fünf Schuhe, und jeder trägt `meta.feet`.
2. Die Reglergruppen kommen mit — `shoe` bei jedem Schuh, `boot` nur mit
   Schaft. Eine Hose bekommt keine Schuhregler.
3. Jeder Schuhregler hat einen deutschen Titel und einen Hilfetext: Ein
   Regler ohne Erklärung erschiene englisch, und ein Hilfetext ohne
   Stellenangabe wäre geraten (`reglertexte.py`).
4. Ein fertiger Schnitt ist am Inhalt als Schuh zu erkennen — daran
   entscheidet `drapierlauf.py`, ob die Simulation einen Boden bekommt.
   Ohne ihn fiel die Ballerina 14 cm durch den Boden.
"""
import json
import os
import shutil

from django.conf import settings
from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.assets()
from GarmentCode.katalog import Katalog                      # noqa: E402
from GarmentCode.regler import Regler                        # noqa: E402
from GarmentCode.reglerhilfe import Reglerhilfe              # noqa: E402
from GarmentCode.reglertexte import Reglertexte              # noqa: E402
from GarmentCode.reglertitel import Reglertitel              # noqa: E402
from GarmentCode.schuh.schuhentwurf import Schuhentwurf      # noqa: E402

SCHUHE = ('ballerina', 'slipper', 'stiefelette', 'stiefel', 'socke')


class SchuhkatalogTest(SimpleTestCase):

    databases = []

    def test_der_katalog_fuehrt_die_fuenf_schuhe(self):
        namen = {eintrag['name'] for eintrag in Katalog.liste()}
        for schuh in SCHUHE:
            self.assertIn(schuh, namen)

    def test_jeder_schuh_traegt_den_vierten_baustein(self):
        for schuh in SCHUHE:
            entwurf = Katalog.entwurf(schuh)
            self.assertIn(Schuhentwurf.baustein(entwurf),
                          ('Halbschuh', 'Stiefel'), schuh)
            # Kein Oberteil, kein Bund, kein Unterteil: `MetaGarment`
            # bekäme sonst ein leeres Stück und würfe.
            for feld in ('upper', 'wb', 'bottom'):
                self.assertIsNone(entwurf['meta'][feld]['v'], (schuh, feld))

    def test_eine_hose_bleibt_ohne_schuh(self):
        entwurf = Katalog.entwurf('hose')
        self.assertIsNone(Schuhentwurf.baustein(entwurf))
        gruppen = [g['gruppe'] for g in Regler.fuer(entwurf)]
        self.assertNotIn('shoe', gruppen)
        self.assertNotIn('boot', gruppen)

    def test_die_reglergruppen_folgen_dem_schaft(self):
        ohne = [g['gruppe'] for g in Katalog.regler('ballerina')]
        mit = [g['gruppe'] for g in Katalog.regler('stiefel')]
        self.assertEqual(ohne, ['shoe'])
        self.assertEqual(mit, ['shoe', 'boot'])

    def test_die_schuhregler_sind_vollstaendig_beschriftet(self):
        u"""Titel UND Hilfetext für jedes Feld — englische Reste fallen auf."""
        for gruppe in Katalog.regler('stiefel'):
            self.assertNotEqual(Reglertitel.gruppe(gruppe['gruppe']),
                                gruppe['gruppe'])
            for feld in gruppe['felder']:
                pfad = feld['pfad']
                self.assertNotEqual(feld['titel'], feld['feld'], pfad)
                self.assertTrue(Reglertexte.fuer(pfad), pfad)
                self.assertIn('.py', Reglertexte.fuer(pfad), pfad)

    def test_die_zehenformen_haben_deutsche_namen(self):
        for wert, titel in (('round', u'Rund'), ('pointed', u'Spitz'),
                            ('square', u'Eckig')):
            self.assertEqual(Reglerhilfe.wert(wert), titel)

    def test_die_werte_der_yaml_liegen_in_ihren_bereichen(self):
        u"""Ein Vorgabewert ausserhalb des Bereichs klemmt am Anschlag."""
        quelle = Schuhentwurf.lesen()
        for gruppe in Schuhentwurf.GRUPPEN:
            for name, eintrag in quelle[gruppe].items():
                if eintrag['type'] in ('float', 'int'):
                    unten, oben = eintrag['range']
                    self.assertTrue(unten <= eintrag['v'] <= oben,
                                    '%s.%s' % (gruppe, name))
                else:
                    self.assertIn(eintrag['v'], eintrag['range'],
                                  '%s.%s' % (gruppe, name))


class SchuhentwurfTest(SimpleTestCase):

    databases = []

    def test_mischen_ergaenzt_nur_was_fehlt(self):
        entwurf = {'meta': {'upper': {'v': 'Shirt'}},
                   'shoe': {'length': {'v': 9.9, 'range': [0, 10],
                                       'type': 'float'}}}
        Schuhentwurf.mischen(entwurf)
        self.assertIn('feet', entwurf['meta'])
        self.assertIn('boot', entwurf)
        # Vorhandenes bleibt: der Nutzerwert 9,9 wird nicht überschrieben.
        self.assertEqual(entwurf['shoe']['length']['v'], 9.9)
        self.assertEqual(entwurf['meta']['upper']['v'], 'Shirt')

    def test_lesen_liefert_eine_kopie(self):
        a = Schuhentwurf.lesen()
        a['shoe']['length']['v'] = -1
        self.assertNotEqual(Schuhentwurf.lesen()['shoe']['length']['v'], -1)


class SchuhschnittErkennungTest(SimpleTestCase):

    databases = []

    def setUp(self):
        self.ordner = os.path.join(settings.BASE_DIR, '_wegwerf',
                                   'test_schuhentwurf')
        os.makedirs(self.ordner, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.ordner, ignore_errors=True)

    def _spec(self, panels):
        pfad = os.path.join(self.ordner, 'x_specification.json')
        with open(pfad, 'w', encoding='utf-8') as datei:
            json.dump({'pattern': {'panels': {n: {} for n in panels}}}, datei)
        return pfad

    def test_ein_schnitt_mit_sohle_ist_ein_schuh(self):
        self.assertTrue(Schuhentwurf.ist_schuhschnitt(
            self._spec(['probe_l_sohle', 'probe_l_blatt'])))

    def test_ein_kleid_ist_keiner(self):
        self.assertFalse(Schuhentwurf.ist_schuhschnitt(
            self._spec(['front', 'back', 'sleeve_l'])))

    def test_eine_fehlende_datei_ist_keiner(self):
        self.assertFalse(Schuhentwurf.ist_schuhschnitt(
            os.path.join(self.ordner, 'gibtsnicht.json')))
