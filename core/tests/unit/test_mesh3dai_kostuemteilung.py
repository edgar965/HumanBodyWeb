"""Bau und Prüfung getrennt, nur ein Geschlecht gebaut: was die Seite dazu sagt (06.11.2026).
`Mesh3daitestgeschlechtstand.fuer`:
    1  beide Geschlechter aus demselben Lauf: nichts zu sagen
    2  das andere Geschlecht trägt den jüngeren Lauf: Hinweis mit beiden Zeiten
    3  dieses Geschlecht hat keinen Kostüm-Lauf, das andere schon: Hinweis, `lauf` None
    4  kein Kostüm-Lauf: nichts zu sagen
    5  dieses Geschlecht ist das jüngere: nichts zu sagen
`Mesh3daitestgeschlechtstand.text`:
    6  nennt beide Geschlechter mit Umlaut und beide Zeiten als Datum
    7  nichts zu sagen: None
`Mesh3daitestfaelle.fuer_test`:
    8  Tabelle und Stücke aus demselben Lauf: kein `stuecke_lauf`
    9  Stücke aus einem neueren Lauf (Prüfung steht aus): `stuecke_lauf` nennt ihn
Sabotage (von Hand): in `fuer` den Vergleich `>=` zu `<=` drehen → Fall 2 und 5 rot; in `fuer_test` den Vergleich `!=` zu `==` → Fall 8 und 9 rot.
"""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from django.conf import settings

from core.dienste.mesh3daitestfaelle import Mesh3daitestfaelle
from core.dienste.mesh3daitestgeschlechtstand import Mesh3daitestgeschlechtstand


def _ki(ordner, geschlecht, lauf):
    kleider = ordner / ('kleider_%s' % geschlecht)
    kleider.mkdir(parents=True, exist_ok=True)
    (kleider / 'ki.json').write_text(json.dumps({'kostuem': {'lauf': lauf}}), encoding='utf-8')
    return kleider


class _Ablage(unittest.TestCase):
    databases = []

    def setUp(self):
        ablage = tempfile.TemporaryDirectory(dir=settings.TOOLS_ROOT / 'ProjektTemp')
        self.addCleanup(ablage.cleanup)
        self.test = Path(ablage.name)


class TestGeschlechtstand(_Ablage):
    def test_derselbe_lauf(self):
        _ki(self.test, 'weiblich', '2026.11.06.17.23_kostuem_stufe1')
        _ki(self.test, 'maennlich', '2026.11.06.17.23_kostuem_stufe1')
        self.assertIsNone(Mesh3daitestgeschlechtstand.fuer(self.test, 'maennlich'))

    def test_anderes_ist_juenger(self):
        _ki(self.test, 'weiblich', '2026.11.06.17.23_kostuem_stufe1')
        _ki(self.test, 'maennlich', '2026.10.31.15.58_kostuem_stufe1')
        self.assertEqual(Mesh3daitestgeschlechtstand.fuer(self.test, 'maennlich'),
                         {'geschlecht': 'maennlich', 'anderes': 'weiblich', 'lauf': '2026.10.31.15.58', 'lauf_anderes': '2026.11.06.17.23'})

    def test_eigener_lauf_fehlt(self):
        _ki(self.test, 'weiblich', '2026.11.06.17.23_kostuem_stufe1')
        stand = Mesh3daitestgeschlechtstand.fuer(self.test, 'maennlich')
        self.assertIsNone(stand['lauf'])
        self.assertEqual(stand['lauf_anderes'], '2026.11.06.17.23')

    def test_kein_lauf(self):
        self.assertIsNone(Mesh3daitestgeschlechtstand.fuer(self.test, 'weiblich'))

    def test_eigener_lauf_juenger(self):
        _ki(self.test, 'weiblich', '2026.11.06.17.23_kostuem_stufe1')
        _ki(self.test, 'maennlich', '2026.10.31.15.58_kostuem_stufe1')
        self.assertIsNone(Mesh3daitestgeschlechtstand.fuer(self.test, 'weiblich'))

    def test_text(self):
        _ki(self.test, 'weiblich', '2026.11.06.17.23_kostuem_stufe1')
        _ki(self.test, 'maennlich', '2026.10.31.15.58_kostuem_stufe1')
        self.assertEqual(Mesh3daitestgeschlechtstand.text(self.test, 'maennlich'),
                         'Für männlich stammen die Kleider aus einem älteren Lauf (31.10.2026 15:58), zuletzt gerechnet wurde weiblich (06.11.2026 17:23). Neu rechnen baut sie für männlich.')

    def test_text_nichts_zu_sagen(self):
        self.assertIsNone(Mesh3daitestgeschlechtstand.text(self.test, 'weiblich'))


class TestPruefungOffen(_Ablage):
    def _tabelle(self, kleider, lauf):
        (kleider / 'k').mkdir(exist_ok=True)
        (kleider / 'k' / Mesh3daitestfaelle.DATEI).write_text(json.dumps({'lauf': lauf, 'tests': []}), encoding='utf-8')

    def _lesen(self):
        with mock.patch('core.dienste.mesh3daitestfaelle.Mesh3daitest.pfad', return_value=self.test):
            return Mesh3daitestfaelle.fuer_test('probe', 'weiblich')

    def test_tabelle_passt(self):
        self._tabelle(_ki(self.test, 'weiblich', '2026.11.06.17.23_kostuem_stufe1'), '2026.11.06.17.23_kostuem_stufe1')
        self.assertNotIn('stuecke_lauf', self._lesen())

    def test_pruefung_steht_aus(self):
        self._tabelle(_ki(self.test, 'weiblich', '2026.11.06.18.40_kostuem_stufe1'), '2026.11.06.17.23_kostuem_stufe1')
        self.assertEqual(self._lesen()['stuecke_lauf'], '2026.11.06.18.40_kostuem_stufe1')
