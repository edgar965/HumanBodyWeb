# -*- coding: utf-8 -*-
"""Modell des letzten Stands von „2D3D Kleider" (01.10.2026): `Standmodellglb` und `Haarenginestandmodell`.

Kunstskelett und Kunstauftrag, keine Daz-Bibliothek, keine Datenbank:

1. Die Bindematrizen sind das Inverse der VOLLEN Weltlage (Verschiebung UND Ruhedrehung) — mit der reinen Verschiebung
   (`G9rigglb.skelett`) stand `figur.glb` in three.js verzerrt (gemessen 75 mm im Mittel, 651 mm höchstens).
2. Unbekannte Knochen binden an den Ersatz und werden gezählt; Gewichte summieren auf 1.
3. Farbfaktoren gehen linear in die GLB (Daz-Farben sind sRGB) — sonst stehen die Brauen hellgrau da.
4. `eintrag()`: keine Figur → None; keine Datei → `datei` None; alte Fassung → `aktuell` falsch; gescheiterter Bau
   derselben Fassung → `fehler`.
"""

import json
import shutil
import tempfile
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from django.test import SimpleTestCase

from core.dienste.haarenginestandmodell import Haarenginestandmodell
from core.dienste.standmodellglb import Standmodellglb


class StandmodellglbTest(SimpleTestCase):
    #: Hüfte, Wirbel um 90° um Z gedreht, Kopf — `pos`/`quat` elternrelativ wie `Gelenkskelett.bauplan()`.
    KNOCHEN = [
        {'name': 'hip', 'eltern': None, 'kopf': [0.0, 1.0, 0.0], 'pos': [0.0, 1.0, 0.0], 'quat': [0, 0, 0, 1]},
        {'name': 'spine1', 'eltern': 'hip', 'kopf': [0.0, 1.2, 0.0], 'pos': [0.0, 0.2, 0.0],
         'quat': [0, 0, 0.7071068, 0.7071068]},
        {'name': 'head', 'eltern': 'spine1', 'kopf': [0.0, 1.5, 0.0], 'pos': [0.3, 0.0, 0.0], 'quat': [0, 0, 0, 1]},
        {'name': 'hilfe_ende', 'eltern': 'head', 'kopf': [0.0, 1.6, 0.0], 'pos': [0.1, 0.0, 0.0], 'ende': True},
    ]

    def test_1_bindung_ist_inverse_weltlage_mit_drehung(self):
        glb = Standmodellglb(self.KNOCHEN)
        gelenke = glb.gltf['skins'][0]['joints']
        self.assertEqual(len(gelenke), 3, 'Endknochen sind kein Ziel der Haut')
        lage = glb.welt(gelenke)
        roh = glb.gltf['bufferViews'][glb.gltf['accessors'][glb.gltf['skins'][0]['inverseBindMatrices']]['bufferView']]
        bind = np.frombuffer(bytes(glb.puffer[roh['byteOffset']:roh['byteOffset'] + roh['byteLength']]),
                             dtype=np.float32).reshape(-1, 4, 4)
        for i, g in enumerate(gelenke):
            # glTF speichert spaltenweise: die gelesene Matrix ist die transponierte
            np.testing.assert_allclose(lage[g] @ bind[i].T, np.eye(4), atol=1e-5)
        np.testing.assert_allclose(lage[gelenke[2]][:3, 3], [0.0, 1.5, 0.0], atol=1e-6)

    def test_2_unbekannter_knochen_an_den_ersatz(self):
        glb = Standmodellglb(self.KNOCHEN)
        haut = {'knochen': ['head', 'zopf_7'], 'index': [[0, 1, 0, 0], [1, 1, 1, 1]],
                'gewicht': [[3.0, 1.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]]}
        index, gewicht = glb._haut(haut, 2)
        self.assertEqual(glb.fehlend, {'zopf_7'})
        self.assertEqual(int(index[0, 1]), glb.nummer['hip'])
        np.testing.assert_allclose(gewicht.sum(axis=1), [1.0, 1.0])
        np.testing.assert_allclose(gewicht[0, :2], [0.75, 0.25])

    def test_3_farbfaktor_linear(self):
        glb = Standmodellglb(self.KNOCHEN)
        punkte = np.array([[0.0, 1.6, 0.0], [0.1, 1.6, 0.0], [0.0, 1.7, 0.0]])
        haut = glb._haut(None, 3)
        glb._netz('koerper_brauen__probe_g0', punkte, [[0, 1, 2]], None, None, haut, faktor=(0.2196, 0.1647, 0.1451))
        faktor = glb.gltf['materials'][-1]['pbrMetallicRoughness']['baseColorFactor']
        self.assertAlmostEqual(faktor[0], 0.0395, places=3)
        self.assertLess(faktor[0], 0.2196, 'sRGB 0,22 ist linear deutlich dunkler')
        self.assertEqual(glb.gltf['nodes'][-1]['skin'], 0)


class HaarenginestandmodellTest(SimpleTestCase):

    def setUp(self):
        self.ordner = Path(tempfile.mkdtemp(prefix='standmodell_', dir=str(Path(__file__).resolve().parents[3]
                                                                             / 'ProjektTemp')))
        (self.ordner / 'ergebnis').mkdir()
        self.ablage = SimpleNamespace(ergebnis=lambda name='': self.ordner / 'ergebnis' / name if name
                                      else self.ordner / 'ergebnis')

    def tearDown(self):
        shutil.rmtree(self.ordner, ignore_errors=True)

    def _stand(self, stellung=None, ergebnis=None):
        job = SimpleNamespace(kennung='probe', stellung=lambda: dict(stellung or {}), ergebnis=ergebnis or {})
        return Haarenginestandmodell(job, self.ablage)

    def test_4_ohne_figur_kein_eintrag(self):
        self.assertIsNone(self._stand().eintrag())

    def test_5_ohne_datei_bestellbar(self):
        e = self._stand({'body_bs_Probe': 0.5}).eintrag()
        self.assertIsNone(e['datei'])
        self.assertFalse(e['aktuell'])
        self.assertEqual(e['soll'], e['fassung'])

    def test_6_alte_fassung_ist_nicht_aktuell(self):
        stand = self._stand({'body_bs_Probe': 0.5})
        (self.ordner / 'ergebnis' / 'stand_alt.glb').write_bytes(b'glTF')
        (self.ordner / 'ergebnis' / Haarenginestandmodell.BERICHT).write_text(
            json.dumps({'datei': 'stand_alt.glb', 'fassung': 'alt'}), encoding='utf-8')
        e = stand.eintrag()
        self.assertEqual((e['datei'], e['fassung'], e['aktuell']), ('stand_alt.glb', 'alt', False))
        self.assertNotEqual(e['soll'], 'alt')
        # Eine neue Runde ändert die Fassung — die Körperregler der Iterationen gehören zum Stand.
        neu = self._stand({'body_bs_Probe': 0.5}, {'kreislauf': {'modell': {'koerper': {'body_bs_Waist': 0.2}}}})
        self.assertNotEqual(neu.fassung(), stand.fassung())
        self.assertEqual(neu.stellung()['body_bs_Waist'], 0.2)

    def test_7_gescheitert_wird_nicht_wieder_bestellt(self):
        stand = self._stand({'body_bs_Probe': 0.5})
        stand.scheitern(RuntimeError('kein Netz'))
        self.assertEqual(stand.eintrag()['fehler'], 'kein Netz')
        anders = self._stand({'body_bs_Probe': 0.6})
        self.assertNotIn('fehler', anders.eintrag(), 'der Fehler gilt nur für seine Fassung')
