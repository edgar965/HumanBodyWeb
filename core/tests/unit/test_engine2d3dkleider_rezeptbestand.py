# -*- coding: utf-8 -*-
"""`Engine2d3dKleiderrezeptbestand` (Namen im Rezept gegen die Bibliothek) und `Rezeptaufzeichnung` (dieselben Aufrufe als Rezeptzeilen), 05.10.2026.

Der Bestand ist mit `mock.patch.object` gesetzt, die Funktionen kommen vom echten `ModellMitKleidern` (kein Zugriff auf die Garderobe, keine Datenbank). Geschrieben, nicht gelaufen (`testsuite-nur-auf-ansage`).
"""

from types import SimpleNamespace
from unittest import mock

from django.test import SimpleTestCase

from core.dienste.engine2d3dkleiderrezeptbestand import Engine2d3dKleiderrezeptbestand
from core.dienste.rezeptaufzeichnung import Rezeptaufzeichnung


class DerRezeptbestand(SimpleTestCase):
    def setUp(self):
        self.pruefer = Engine2d3dKleiderrezeptbestand(SimpleNamespace(ergebnis={}))
        for ziel, wert in (('stuecke', {'g9_base_shirt', 'eigen_foto_a_hose', 'mavick_hair'}), ('kanaele', {'body_bs_BodyMass', 'body_ctrl_BodyMuscular'})):
            halter = mock.patch.object(self.pruefer, ziel, return_value=wert)
            halter.start()
            self.addCleanup(halter.stop)

    def test_bekannte_namen_gehen_durch(self):
        self.pruefer.pruefen("m.kleid_nur('g9_base_shirt', 'eigen_foto_a_hose')\nm.haar_nur('mavick_hair')\nm.koerper_regler_setzen(body_bs_BodyMass=-0.2)\nm.haltung(arme_grad=35.0)")

    def test_ein_erfundenes_stueck_ist_ein_fehler_mit_zeile_und_aehnlichem_namen(self):
        with self.assertRaises(ValueError) as fehler:
            self.pruefer.pruefen("m.haltung(arme_grad=35.0)\nm.kleid_nur('g9_base_shirts')")
        self.assertIn('Zeile 2: kleid_nur', str(fehler.exception))
        self.assertIn('g9_base_shirt', str(fehler.exception))                        # ähnlich

    def test_die_namen_der_ersten_iteration_werden_abgelehnt(self):
        with self.assertRaises(ValueError) as fehler:
            self.pruefer.pruefen("m.kleid_nur('oberteil')\nm.kleid_farbe('#808080')\nm.koerper_regler_setzen(FBMHeavy=0.2, PBMBellySize=0.1)")
        text = str(fehler.exception)
        self.assertIn('„oberteil"', text)
        self.assertIn('„FBMHeavy"', text)
        self.assertIn('„PBMBellySize"', text)

    def test_ein_stueck_das_kleid_schnitt_im_selben_rezept_anlegt_gilt_als_bekannt(self):
        self.pruefer.pruefen("m.kleid_schnitt('hose', titel='Hose')\nm.kleid_anteil('gc_hose', 0.8)")
        with self.assertRaises(ValueError):
            self.pruefer.pruefen("m.kleid_anteil('gc_hose', 0.8)")                   # ohne kleid_schnitt gibt es kein gc_hose

    def test_eigene_morphe_der_koerperregler_gelten(self):
        self.pruefer.pruefen("m.koerper_regler('eigen:ort_bauch', 0.5)")


class DieRezeptaufzeichnung(SimpleTestCase):
    class _Modell:
        def __init__(self):
            self.aufrufe = []

        def kleid_nur(self, *kennungen):
            self.aufrufe.append(kennungen)
            return self

        def haar_farbe(self, hexfarbe):
            self.aufrufe.append(hexfarbe)
            return self

        def als_dict(self):
            return {'ok': True}

    def test_aufrufe_laufen_durch_und_stehen_als_zeilen_da(self):
        modell = self._Modell()
        huelle = Rezeptaufzeichnung(modell)
        self.assertIs(huelle.kleid_nur('a', 'b'), huelle)                              # Verkettung bleibt in der Hülle
        huelle.haar_farbe('#373737')
        self.assertEqual(huelle.zeilen, ["m.kleid_nur('a', 'b')", "m.haar_farbe('#373737')"])
        self.assertEqual(modell.aufrufe, [('a', 'b'), '#373737'])
        self.assertEqual(huelle.als_dict(), {'ok': True})                             # eine Abfrage ist kein Rezeptaufruf
        self.assertEqual(len(huelle.zeilen), 2)
