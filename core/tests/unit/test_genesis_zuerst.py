# -*- coding: utf-8 -*-
"""„Genesis zuerst“ (12.11.2026, Edgar: „mach den Umbau“): Häkchen, Schritte der Kette, Vorgabe Weg z, Prüfung „Proportionen wie im Foto“, `Npztorch`.

Kunstdaten in einem eigenen Ordner unter `ProjektTemp/_wegwerf/tests_genesis_zuerst/` (nie System-Temp), danach weggeräumt. Kein GPU-Lauf, keine echten Netze.

Sabotage, je Fall rot:
  - `Kikleiderliste.garderobe_entscheidet` immer False → test_2 (Zeile a bietet k statt z an).
  - in `Meshgenesisrechenlauf.schritte` das Einfügen von „garderobe“ streichen → test_3.
  - in `Proportionen.vergleichen` die Grenze auf 1,0 setzen → test_4 (Gegenprobe Beine ×1,25 grün).
  - in `Npztorch.feld` `fortran` übergehen → test_5 (Spalten vertauscht).

Geschrieben am 12.11.2026, nicht gelaufen (Tests nur auf Ansage).
"""
import ast
import json
import shutil
import struct
import sys
import tempfile
import zipfile
from pathlib import Path

import torch
from django.conf import settings
from django.test import SimpleTestCase

MESHGENESIS = str(Path(settings.TOOLS_ROOT) / 'meshgenesis')
if MESHGENESIS not in sys.path:
    sys.path.insert(0, MESHGENESIS)


def _npy(descr, form, daten, fortran=False):
    """NPY-Inhalt von Hand (ohne numpy): Kopf Fassung 1, auf 64 Byte aufgefüllt."""
    kopf = repr({'descr': descr, 'fortran_order': fortran, 'shape': tuple(form)}).encode('latin1')
    rest = 64 - (10 + len(kopf) + 1) % 64
    kopf = kopf + b' ' * rest + b'\n'
    assert ast.literal_eval(kopf.decode('latin1').strip())['descr'] == descr
    return b'\x93NUMPY\x01\x00' + struct.pack('<H', len(kopf)) + kopf + daten


class GenesisZuerstTest(SimpleTestCase):

    def setUp(self):
        wurzel = Path(settings.TOOLS_ROOT) / 'ProjektTemp' / '_wegwerf' / 'tests_genesis_zuerst'
        wurzel.mkdir(parents=True, exist_ok=True)
        self.ordner = Path(tempfile.mkdtemp(dir=wurzel))

    def tearDown(self):
        shutil.rmtree(self.ordner, ignore_errors=True)

    def _eintrag(self, pfad, **felder):
        pfad.mkdir(parents=True, exist_ok=True)
        (pfad / 'eintrag.json').write_text(json.dumps(felder, ensure_ascii=False), encoding='utf-8')

    def test_1_haekchen_vorgabe_aus_und_setzbar(self):
        from core.dienste.fotogenesispshuman import Fotogenesispshuman
        self.assertFalse(Fotogenesispshuman.lesen({})['genesis_zuerst'])
        self.assertTrue(Fotogenesispshuman.lesen({'pshuman': {'genesis_zuerst': True}})['genesis_zuerst'])
        self.assertIn('genesis_zuerst', Fotogenesispshuman.auswahl())

    def test_2_weg_z_entscheidet_nur_mit_haekchen(self):
        from meshgenesis_kikleiderliste import Kikleiderliste
        test = self.ordner / 'test'
        kleider = test / 'kleider_maennlich'
        self._eintrag(kleider / 'k' / 'ki_oberteil', id='ki_oberteil', name='Robe', art='oberteil', region='oberteil', kostuem=True)
        self._eintrag(kleider / 'k' / 'ki_hose', id='ki_hose', name='Hose', art='hose', region='hose', kostuem=True)
        self._eintrag(kleider / 'z' / 'ki_oberteil', id='ki_oberteil', name='Robe', art='oberteil', region='oberteil', kennung='gc_monks_robe')
        self._eintrag(kleider / 'z' / 'ki_hose', id='ki_hose', name='Hose', art='hose', region='hose', fehler='Liegt unter der Robe')
        (kleider / 'z' / 'garderobe.json').write_text('{}', encoding='utf-8')
        (test / 'einstellung.json').write_text(json.dumps({'genesis_zuerst': True}), encoding='utf-8')
        Kikleiderliste.schreiben(kleider)
        zeilen = {z['id']: z for z in json.loads((kleider / 'ki.json').read_text(encoding='utf-8'))['stuecke']}
        self.assertEqual(zeilen['ki_oberteil']['ki_vorgabe'], ['z'])
        self.assertEqual(zeilen['ki_hose']['ki_vorgabe'], [])
        self.assertIn('Robe', zeilen['ki_hose']['ki_aus'])
        (test / 'einstellung.json').write_text('{}', encoding='utf-8')
        Kikleiderliste.schreiben(kleider)
        zeilen = {z['id']: z for z in json.loads((kleider / 'ki.json').read_text(encoding='utf-8'))['stuecke']}
        self.assertEqual(zeilen['ki_oberteil']['ki_vorgabe'][0], 'k')          # ohne Häkchen: der Kostüm-Weg wie bisher

    def test_3_schritte_der_kette(self):
        from core.dienste.meshgenesisrechenlauf import Meshgenesisrechenlauf
        lauf = Meshgenesisrechenlauf.__new__(Meshgenesisrechenlauf)
        lauf.test = self.ordner
        lauf.kennung = 'kunst'
        alt = [s[0] for s in lauf.schritte()]
        (self.ordner / 'einstellung.json').write_text(json.dumps({'genesis_zuerst': True}), encoding='utf-8')
        neu = lauf.schritte()
        schluessel = [s[0] for s in neu]
        self.assertEqual(schluessel.index('proportionen'), schluessel.index('zeile1') + 1)
        self.assertEqual(schluessel.index('garderobe'), schluessel.index('kleider') + 1)
        self.assertEqual(len(schluessel), len(alt) + 2)
        argumente = {s[0]: s[2] for s in neu}
        self.assertIn('--nur-regler', argumente['zeile1'])
        self.assertEqual(argumente['pruefung'][-2:], ['--weg', 'z'])
        self.assertIn('--ohne-kleider', argumente['haut'])                       # Weg g bleibt im alten Weg, hier nicht (12.11.2026, „optimiere“)
        self.assertNotIn('--ohne-kleider', dict((s[0], s[2]) for s in Meshgenesisrechenlauf.SCHRITTE)['haut'])

    def test_4_proportionen_gegenprobe(self):
        from meshgenesis_proportionen import Proportionen
        laengen = {s[0]: 0.3 + 0.01 * i for i, s in enumerate(Proportionen.STRECKEN)}
        _z, rot = Proportionen.vergleichen(laengen, dict(laengen))
        self.assertEqual(rot, [])
        lang = {n: v * (Proportionen.GEGENPROBE_FAKTOR if n in Proportionen.BEINE else 1.0) for n, v in laengen.items()}
        _z, rot = Proportionen.vergleichen(lang, laengen)
        self.assertTrue(set(Proportionen.BEINE) <= set(rot))

    def test_5_npztorch_liest_zahlen_text_und_fortran(self):
        from KoerperKI_alle.npztorch import Npztorch
        werte = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        datei = self.ordner / 'kunst.npz'
        with zipfile.ZipFile(datei, 'w', compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr('a.npy', _npy('<f4', (2, 3), struct.pack('<6f', *werte)))
            z.writestr('f.npy', _npy('<f8', (2, 3), struct.pack('<6d', *werte), fortran=True))
            z.writestr('namen.npy', _npy('<U4', (2,), 'nose'.encode('utf-32-le') + 'eye\x00'.encode('utf-32-le')))
            z.writestr('o.npy', _npy('|O', (1,), b'\x00' * 8))
        felder = Npztorch.laden(datei, ('a', 'f', 'namen'))
        self.assertEqual(felder['a'].dtype, torch.float32)
        self.assertEqual(felder['a'].tolist(), [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
        self.assertEqual(felder['f'].tolist(), [[1.0, 3.0, 5.0], [2.0, 4.0, 6.0]])
        self.assertEqual(felder['namen'], ['nose', 'eye'])
        with self.assertRaises(ValueError):
            Npztorch.laden(datei, ('o',))
