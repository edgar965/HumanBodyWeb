# -*- coding: utf-8 -*-
"""Tests fuer den BVH-Parser — Leerzeilen und abgeschnittene Bilder.

Anlass (16.08.2026): Die Theatre-Seite bekam bei jedem Aufruf einen Fehler 500.
Ursache war eine LEERZEILE zwischen "Frame Time:" und den Bewegungsdaten in
`Results/nussie1.bvh`. Der Parser las den Bewegungsteil Zeile fuer Zeile und
scheiterte an der leeren:

    ValueError: could not broadcast input array from shape (0,) into shape (3,)

Die Datei ist in Ordnung — Leerzeilen sind in BVH ueblich, viele Werkzeuge
schreiben sie. Der Parser war es nicht.

Gearbeitet wird auf selbst geschriebenen Miniaturdateien unter ProjektTemp, nicht
auf `HumanBody/data/` — das sind Produktionsdaten.
"""

import shutil
import tempfile
from pathlib import Path

from django.conf import settings
from django.test import TestCase

from humanbody_core.skeleton.skeleton import SkeletonRigify

KOPF = """HIERARCHY
ROOT Hips
{
    OFFSET 0.00 0.00 0.00
    CHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation
    JOINT Spine
    {
        OFFSET 0.00 10.00 0.00
        CHANNELS 3 Zrotation Xrotation Yrotation
        End Site
        {
            OFFSET 0.00 10.00 0.00
        }
    }
}
MOTION
Frames: %d
Frame Time: 0.040000
"""

#: Ein Bild: 6 Kanaele Hips + 3 Kanaele Spine.
BILD = '0.0 1.0 0.0 0.0 0.0 0.0 5.0 0.0 0.0'


class BvhParserTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        basis = Path(settings.BASE_DIR).parent / 'ProjektTemp'
        basis.mkdir(exist_ok=True)
        cls.ordner = tempfile.mkdtemp(prefix='bvhparser_', dir=str(basis))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.ordner, ignore_errors=True)
        super().tearDownClass()

    def datei(self, name, inhalt):
        pfad = Path(self.ordner) / name
        pfad.write_text(inhalt, encoding='utf-8')
        return str(pfad)

    def test_saubere_datei(self):
        pfad = self.datei('sauber.bvh', KOPF % 3 + '\n'.join([BILD] * 3) + '\n')
        daten = SkeletonRigify.parse_bvh(pfad)
        self.assertEqual(daten.quats.shape[0], 3)
        self.assertEqual(list(daten.names), ['Hips', 'Spine'])

    def test_leerzeile_vor_den_daten(self):
        """Der eigentliche Befund: eine Leerzeile nach 'Frame Time:'."""
        pfad = self.datei('leerzeile.bvh',
                          KOPF % 3 + '\n' + '\n'.join([BILD] * 3) + '\n')
        daten = SkeletonRigify.parse_bvh(pfad)
        self.assertEqual(daten.quats.shape[0], 3)

    def test_leerzeilen_zwischen_den_bildern(self):
        pfad = self.datei('dazwischen.bvh',
                          KOPF % 3 + BILD + '\n\n' + BILD + '\n\n\n' + BILD + '\n')
        self.assertEqual(SkeletonRigify.parse_bvh(pfad).quats.shape[0], 3)

    def test_leerzeilen_am_ende(self):
        pfad = self.datei('ende.bvh',
                          KOPF % 2 + '\n'.join([BILD] * 2) + '\n\n\n')
        self.assertEqual(SkeletonRigify.parse_bvh(pfad).quats.shape[0], 2)

    def test_abgeschnittenes_bild_bricht_nicht_ab(self):
        """Halbe letzte Zeile: die Datei bleibt lesbar, der Rest wird verworfen."""
        pfad = self.datei('kurz.bvh',
                          KOPF % 3 + BILD + '\n' + BILD + '\n' + '0.0 1.0\n')
        daten = SkeletonRigify.parse_bvh(pfad)
        # Feldgroesse bleibt die angekuendigte, die dritte Drehung bleibt neutral.
        self.assertEqual(daten.quats.shape[0], 3)

    def test_weniger_zeilen_als_angekuendigt(self):
        pfad = self.datei('zuwenig.bvh', KOPF % 10 + '\n'.join([BILD] * 2) + '\n')
        self.assertEqual(SkeletonRigify.parse_bvh(pfad).quats.shape[0], 10)

    def test_echte_datei_mit_leerzeile(self):
        """Gegenprobe an der Datei, die den Fehler 500 ausgeloest hat."""
        pfad = (Path(settings.HUMANBODY_ROOT) / 'data' / 'animations' / 'bvh'
                / 'Results' / 'nussie1.bvh')
        if not pfad.is_file():
            self.skipTest('nussie1.bvh liegt auf diesem Rechner nicht')
        daten = SkeletonRigify.parse_bvh(str(pfad))
        self.assertEqual(daten.quats.shape[0], 3669)
