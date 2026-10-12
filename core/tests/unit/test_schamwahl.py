# -*- coding: utf-8 -*-
"""Wächter für die Scham-Methode der Blender-Importe (Einstellungen → Genesis, 11.10.2026).

Edgar: „in Einstellungen mache eine neue Seite Genesis, darin die zwei Optionen, wie die Scham eingebaut wird, die alte Methode (Eigen) oder die neue (DAZ)."
Drei Dinge dürfen nicht kippen: Ohne Einstellung gilt Eigen; ein unbekannter Wert heißt Eigen (nie stillschweigend DAZ); und bei Eigen baut der Import KEINE Daz-Scham
(sonst liefe bei jedem Import das Geograft mit).
"""

from unittest import TestCase
from unittest.mock import patch

from core.dienste.blendimportschamdaz import Blendimportschamdaz
from core.dienste.schamwahl import Schamwahl


class SchamwahlTest(TestCase):
    def test_ohne_einstellung_gilt_eigen(self):
        self.assertEqual(Schamwahl.aus({}), Schamwahl.EIGEN)
        self.assertEqual(Schamwahl.aus(None), Schamwahl.EIGEN)

    def test_daz_wird_gelesen(self):
        self.assertEqual(Schamwahl.aus({Schamwahl.SCHLUESSEL: 'daz'}), Schamwahl.DAZ)

    def test_unbekannter_wert_heisst_eigen(self):
        self.assertEqual(Schamwahl.aus({Schamwahl.SCHLUESSEL: 'irgendwas'}), Schamwahl.EIGEN)

    def test_beide_methoden_stehen_zur_auswahl(self):
        self.assertEqual(list(Schamwahl.WAHLEN), [Schamwahl.EIGEN, Schamwahl.DAZ])


class BlendimportschamdazTest(TestCase):
    def test_bei_eigen_passiert_nichts(self):
        with patch.object(Schamwahl, 'gewaehlt', return_value=Schamwahl.EIGEN):
            self.assertIsNone(Blendimportschamdaz.bauen('cute girl', {'scham': 'objekt'}))

    def test_bei_daz_aber_mann_wird_nicht_gebaut_und_der_grund_steht_im_ergebnis(self):
        with patch.object(Schamwahl, 'gewaehlt', return_value=Schamwahl.DAZ):
            ergebnis = Blendimportschamdaz.bauen('cute girl', {'scham': 'mann'})
        self.assertIn('aus', ergebnis)

    def test_ein_fehler_im_bau_beendet_den_import_nicht(self):
        with patch.object(Schamwahl, 'gewaehlt', return_value=Schamwahl.DAZ), \
                patch('core.dienste.dazgeograftangepasst.Dazgeograftangepasst', side_effect=FileNotFoundError('keine Daz-Bibliothek')):
            ergebnis = Blendimportschamdaz.bauen('cute girl', {'scham': 'objekt'})
        self.assertEqual(ergebnis, {'fehler': 'keine Daz-Bibliothek'})
