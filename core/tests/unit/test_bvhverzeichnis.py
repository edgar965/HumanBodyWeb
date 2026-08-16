# -*- coding: utf-8 -*-
"""Tests fuer Bvhverzeichnis und Animationsliste.

Beide sind aus dem Performance-Durchgang vom 16.08.2026 entstanden:
`/api/character/animations/` brauchte 201 ms fuer eine Antwort, die vollstaendig
aus dem Zwischenspeicher kam. Festgehalten wird hier vor allem, was beim
Umstellen von `os.listdir` auf `os.scandir` leicht kaputtgeht — die
REIHENFOLGE — und dass der Zwischenspeicher wirklich greift, also keine Datei
zweimal gelesen wird.

Der Testbaum liegt unter ProjektTemp, nicht in `HumanBody/data/`.
"""

import shutil
import tempfile
from pathlib import Path

from django.conf import settings
from django.test import TestCase

from core.dienste.animationsliste import Animationsliste
from core.dienste.bvhverzeichnis import Bvhverzeichnis
from core.models import BVHFile

KOPF = ('HIERARCHY\nROOT Hips\n{\n}\nMOTION\nFrames: %d\n'
        'Frame Time: 0.033333\n')


class BvhBaum:
    """Testbaum mit Namen, die die Sortierung auf die Probe stellen."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        basis = Path(settings.BASE_DIR).parent / 'ProjektTemp'
        basis.mkdir(exist_ok=True)
        cls.wurzel = tempfile.mkdtemp(prefix='bvhverz_', dir=str(basis))
        cls.inhalt = {
            # 'a b.bvh' und 'a.bvh': mit Endung sortiert steht 'a b' VORNE
            # (Leerzeichen 0x20 < Punkt 0x2E), ohne Endung dahinter.
            'Aist': {'a b.bvh': 5, 'a.bvh': 7, 'b.bvh': 9},
            'Bandai 1': {'gehen.bvh': 12},
        }
        for kategorie, dateien in cls.inhalt.items():
            ordner = Path(cls.wurzel) / kategorie
            ordner.mkdir(parents=True)
            for name, bilder in dateien.items():
                (ordner / name).write_text(KOPF % bilder, encoding='utf-8')
        (Path(cls.wurzel) / 'Leer').mkdir()
        (Path(cls.wurzel) / 'Aist' / 'liesmich.txt').write_text('x', encoding='utf-8')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.wurzel, ignore_errors=True)
        super().tearDownClass()

    def verzeichnis(self):
        return Bvhverzeichnis(wurzel=self.wurzel)


class BvhverzeichnisTest(BvhBaum, TestCase):

    def test_kategorienamen_sortiert(self):
        self.assertEqual(self.verzeichnis().kategorienamen(),
                         ['Aist', 'Bandai 1', 'Leer'])

    def test_dateien_ohne_endung_im_namen(self):
        namen = [d.name for d in self.verzeichnis().dateien('Aist')]
        self.assertEqual(namen, ['a b', 'a', 'b'])

    def test_reihenfolge_wie_listdir_mit_endung(self):
        """Kern des Umbaus: 'a b.bvh' steht vor 'a.bvh', wie bei sorted(listdir)."""
        eigene = [d.name for d in self.verzeichnis().dateien('Aist')]
        vergleich = sorted(self.inhalt['Aist'])
        self.assertEqual(eigene, [n[:-4] for n in vergleich])

    def test_fremde_dateien_zaehlen_nicht(self):
        self.assertEqual(self.verzeichnis().anzahl('Aist'), 3)
        self.assertEqual(len(self.verzeichnis().dateien('Aist')), 3)

    def test_leerer_ordner(self):
        self.assertEqual(self.verzeichnis().anzahl('Leer'), 0)
        self.assertEqual(self.verzeichnis().dateien('Leer'), [])

    def test_unbekannte_kategorie_wirft_nicht(self):
        self.assertEqual(self.verzeichnis().dateien('gibtsnicht'), [])
        self.assertEqual(self.verzeichnis().anzahl('gibtsnicht'), 0)

    def test_fehlende_wurzel_wirft_nicht(self):
        weg = Bvhverzeichnis(wurzel=self.wurzel + '_weg')
        self.assertEqual(weg.kategorienamen(), [])

    def test_zeitstempel_kommt_mit(self):
        for datei in self.verzeichnis().dateien('Aist'):
            self.assertGreater(datei.mtime_ns, 0)


class AnimationslisteTest(BvhBaum, TestCase):

    def liste(self):
        return Animationsliste(verzeichnis=self.verzeichnis())

    def test_gruppiert_nach_kategorie(self):
        ergebnis = self.liste().nach_kategorie()
        self.assertEqual(sorted(ergebnis), ['Aist', 'Bandai 1'])
        self.assertNotIn('Leer', ergebnis)

    def test_felder_je_eintrag(self):
        eintrag = self.liste().nach_kategorie()['Bandai 1'][0]
        self.assertEqual(eintrag, {
            'name': 'gehen', 'category': 'Bandai 1',
            'url': '/api/character/bvh/Bandai 1/gehen/', 'frames': 12})

    def test_bildzahlen_aus_der_datei(self):
        eintraege = self.liste().nach_kategorie()['Aist']
        self.assertEqual({e['name']: e['frames'] for e in eintraege},
                         {'a b': 5, 'a': 7, 'b': 9})

    def test_erster_lauf_legt_die_zeilen_an(self):
        liste = self.liste()
        liste.nach_kategorie()
        self.assertEqual(liste.gelesen, 4)
        self.assertEqual(BVHFile.objects.count(), 4)

    def test_zweiter_lauf_liest_keine_datei_mehr(self):
        """Der Zwischenspeicher ist der Sinn der Uebung — sonst 7.067 Dateien."""
        self.liste().nach_kategorie()
        zweite = self.liste()
        zweite.nach_kategorie()
        self.assertEqual(zweite.gelesen, 0)
        self.assertEqual(BVHFile.objects.count(), 4)

    def test_geaenderte_datei_wird_neu_gelesen(self):
        self.liste().nach_kategorie()
        datei = Path(self.wurzel) / 'Bandai 1' / 'gehen.bvh'
        datei.write_text(KOPF % 99, encoding='utf-8')
        # Zeitstempel sicher verschieben — sonst haengt der Test an der
        # Aufloesung der Uhr des Dateisystems.
        import os
        stand = datei.stat()
        os.utime(datei, ns=(stand.st_atime_ns, stand.st_mtime_ns + 10 ** 9))
        dritte = self.liste()
        ergebnis = dritte.nach_kategorie()
        self.assertEqual(dritte.gelesen, 1)
        self.assertEqual(ergebnis['Bandai 1'][0]['frames'], 99)
        self.assertEqual(BVHFile.objects.get(name='gehen').frame_count, 99)
