# -*- coding: utf-8 -*-
"""Netz-Vorschau der 3D-Ansicht, gebaut schon im Lauf (12.10.2026): Edgar: „bei Edgar dauert es ewig, bis das Mesh in der 3D-View angezeigt wird“ — der Bau (125 s am Netz mit 1,97 Mio. Dreiecken)
begann erst beim Öffnen der Seite und stand dann jedes Mal still, wenn ein Lauf `koerper.glb` neu geschrieben hatte.

Ohne Blender, ohne GPU, ohne Datenbank — Kunstdaten in `ProjektTemp`. Nicht gelaufen — läuft nur auf Ansage.

    VorabTest        nur Aufträge der Jobseite „Mesh-3D“, ein Fehler bricht nichts ab, der Bau wird angestoßen
    QuelleTest       `koerper.glb` des Imports vor dem Eingang des Auftrags; ein Stempel der alten Fassung (aus dem Eingang) gilt weiter
    AufruferTest     Wächter: die beiden Schritte „koerper“ rufen `vorab` (Quelltext gelesen, nichts gestartet)
    VorstufeTest     die Gitter-Vereinfachung liefert ein Netz in der Größenordnung des Ziels, und zu grobe Vorstufen fallen auf den alten Weg zurück
"""

import json
import tempfile
from pathlib import Path
from unittest import mock

import numpy as np
import trimesh
from django.test import SimpleTestCase

from core.daten.blendimportablage import Blendimportablage
from core.dienste import blendimportkoerper, blendimportnetz
from core.dienste.mesh3dnetzansicht import Mesh3dnetzansicht


def _ordner():
    return tempfile.TemporaryDirectory(dir=str(Path(__file__).resolve().parents[3] / 'ProjektTemp'))


class VorabTest(SimpleTestCase):
    databases = set()

    def test_1_nur_die_jobseite_mesh3d_bekommt_eine_vorschau(self):
        with mock.patch.object(Blendimportablage, 'stand', return_value={'bereich': 'charakter'}), \
                mock.patch.object(Mesh3dnetzansicht, 'anstossen') as anstossen:
            self.assertIsNone(Mesh3dnetzansicht.vorab('2026.10.12.10.00.00'))
        anstossen.assert_not_called()

    def test_2_ein_auftrag_der_jobseite_stoesst_den_bau_an(self):
        with mock.patch.object(Blendimportablage, 'stand', return_value={'bereich': 'mesh3d'}), \
                mock.patch.object(Mesh3dnetzansicht, 'anstossen', return_value={'status': 'baut'}) as anstossen:
            self.assertEqual(Mesh3dnetzansicht.vorab('2026.10.12.10.00.00'), {'status': 'baut'})
        anstossen.assert_called_once_with()

    def test_3_ein_fehler_bricht_den_import_nie_ab(self):
        with mock.patch.object(Blendimportablage, 'stand', return_value={'bereich': 'mesh3d'}), \
                mock.patch.object(Mesh3dnetzansicht, 'anstossen', side_effect=OSError('Platte voll')):
            self.assertIsNone(Mesh3dnetzansicht.vorab('2026.10.12.10.00.00'))


class QuelleTest(SimpleTestCase):
    databases = set()

    def _ansicht(self, ordner):
        arbeit = Path(ordner) / 'arbeit'
        arbeit.mkdir()
        ansicht = Mesh3dnetzansicht('2026.10.12.10.00.00')
        patch = mock.patch.object(Blendimportablage, 'arbeit', side_effect=lambda name='': arbeit / name if name else arbeit)
        return ansicht, arbeit, patch

    def test_1_die_datei_des_imports_ist_die_quelle_noch_ohne_auftrag(self):
        with _ordner() as o:
            ansicht, arbeit, patch = self._ansicht(o)
            (arbeit / 'koerper.glb').write_bytes(b'x' * 10)
            with patch, mock.patch.object(Mesh3dnetzansicht, '_figurnetz', return_value=None):
                self.assertEqual(ansicht.quelle(), arbeit / 'koerper.glb')

    def test_2_ohne_die_datei_gilt_das_netz_im_eingang(self):
        with _ordner() as o:
            ansicht, arbeit, patch = self._ansicht(o)
            eingang = Path(o) / 'koerper.glb'
            eingang.write_bytes(b'x')
            with patch, mock.patch.object(Mesh3dnetzansicht, '_figurnetz', return_value=eingang):
                self.assertEqual(ansicht.quelle(), eingang)

    def test_3_ein_alter_stempel_aus_dem_eingang_gilt_weiter(self):
        with _ordner() as o:
            ansicht, arbeit, patch = self._ansicht(o)
            eigene, eingang = arbeit / 'koerper.glb', Path(o) / 'koerper.glb'
            eigene.write_bytes(b'x' * 10)
            eingang.write_bytes(b'y' * 12)
            (arbeit / 'ansicht').mkdir()
            (arbeit / 'ansicht' / Mesh3dnetzansicht.DATEI).write_bytes(b'GLB')
            (arbeit / 'ansicht' / Mesh3dnetzansicht.STAND).write_text(json.dumps({'stempel': Mesh3dnetzansicht.stempel(eingang)}), encoding='utf-8')
            with patch, mock.patch.object(Mesh3dnetzansicht, '_figurnetz', return_value=eingang):
                self.assertTrue(ansicht.aktuell(eigene))
            (arbeit / 'ansicht' / Mesh3dnetzansicht.STAND).write_text(json.dumps({'stempel': [1, 1, 1, 1]}), encoding='utf-8')
            with patch, mock.patch.object(Mesh3dnetzansicht, '_figurnetz', return_value=eingang):
                self.assertFalse(ansicht.aktuell(eigene))


class AufruferTest(SimpleTestCase):
    """Wie `test_schammessung_aufrufer`: wer `koerper.glb` schreibt, stößt die Vorschau an — nimmt jemand den Aufruf heraus, wird das rot."""

    databases = set()

    def test_1_beide_koerperschritte_rufen_vorab(self):
        for modul in (blendimportnetz, blendimportkoerper):
            text = Path(modul.__file__).read_text(encoding='utf-8')
            self.assertIn('Mesh3dnetzansicht.vorab(self.ablage.kennung)', text, modul.__name__)


class VorstufeTest(SimpleTestCase):
    databases = set()

    def _netz(self, ordner):
        pfad = Path(ordner) / 'kugel.glb'
        trimesh.creation.icosphere(subdivisions=5, radius=1.0).export(str(pfad))
        return pfad

    def test_1_mit_vorstufe_entsteht_ein_netz_in_der_groessenordnung_des_ziels(self):
        with _ordner() as o, mock.patch.object(Mesh3dnetzansicht, 'VORSTUFE_AB', 5000):
            quelle = self._netz(o)
            flaechen, punkte = Mesh3dnetzansicht.vereinfachen(quelle, Path(o) / 'aus.glb', flaechen=4000, farben=False, vorstufe=True)
            self.assertGreaterEqual(flaechen, 3000)
            self.assertLessEqual(flaechen, 4100)
            klein = trimesh.load(str(Path(o) / 'aus.glb'), process=False)
            klein = klein.to_geometry() if isinstance(klein, trimesh.Scene) else klein
            self.assertAlmostEqual(float(np.ptp(klein.vertices[:, 1])), 2.0, delta=0.05)

    def test_2_eine_zu_grobe_vorstufe_faellt_auf_den_alten_weg_zurueck(self):
        with _ordner() as o, mock.patch.object(Mesh3dnetzansicht, 'VORSTUFE_AB', 5000), mock.patch.object(Mesh3dnetzansicht, 'VORSTUFE_PROZENT', 60.0):
            quelle = self._netz(o)
            flaechen, _ = Mesh3dnetzansicht.vereinfachen(quelle, Path(o) / 'aus.glb', flaechen=4000, farben=False, vorstufe=True)
            self.assertGreaterEqual(flaechen, 3000)
