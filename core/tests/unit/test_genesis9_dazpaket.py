# -*- coding: utf-8 -*-
u"""Daz-Studio-Zips in die Bibliothek (`G9dazpaket`, 16.11.2026).

Edgar, 16.11.2026: „ich möchte die in die genesis Assets / kleider eingebaut haben“ — die Freebies legen ihre Inhaltswurzel jedes anders ab
(`Content/`, `My Library/`, ohne Hülle, Zip im Zip). Hier eine Wegwerf-Bibliothek und kleine Zips. Zusagen:

1. Die Wurzel ist der erste Daz-Ordner im Pfad (`Content/People/…`, `My Library/data/…`, `Data/…`); Hüllendateien (Manifest.dsx), Poser
   (`Runtime/Libraries`) und innere Zips bleiben draußen.
2. Ohne `installieren` wird nichts geschrieben; vorhanden mit gleicher Größe = gleich; andere Größe = Konflikt, und dann schreibt das Zip nichts.
3. Ohne eigenen Daz-Inhalt zählen die inneren Zips (Vorlath), mit `innen` nur die genannten.
4. `entfernen` löscht genau die geschriebenen Dateien — eine danach veränderte bleibt.

Sabotage: in `ziel_von` die Prüfung auf `POSER` weg -> Fall 1 rot; in `installieren` den Abbruch bei Konflikt weg -> Fall 2 rot.
"""
import io
import tempfile
import zipfile
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase
from Genesis9.dazpaket import G9dazpaket
from Genesis9.pfade import G9pfade


def _zip(pfad, dateien):
    with zipfile.ZipFile(pfad, 'w') as zf:
        for name, inhalt in dateien.items():
            zf.writestr(name, inhalt)
    return pfad


class DazpaketTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.ordner = tempfile.TemporaryDirectory(dir=str(Path(__file__).parent))
        self.wurzel = Path(self.ordner.name)
        self.bib = self.wurzel / 'bibliothek'
        self.bib.mkdir()
        self._eigen = mock.patch.object(G9pfade, 'eigene_daten', classmethod(lambda cls: self.wurzel / 'eigen'))
        self._eigen.start()

    def tearDown(self):
        self._eigen.stop()
        self.ordner.cleanup()

    def test_1_wurzel_huelle_poser(self):
        self.assertEqual(G9dazpaket.ziel_von('Content/People/Genesis 9/Clothing/x.duf'), 'People/Genesis 9/Clothing/x.duf')
        self.assertEqual(G9dazpaket.ziel_von('My Library/data/kaos/x.dsf'), 'data/kaos/x.dsf')
        self.assertEqual(G9dazpaket.ziel_von('Data/Excessive/Hair/x.dsf'), 'Data/Excessive/Hair/x.dsf')
        self.assertEqual(G9dazpaket.ziel_von('KT Lori G9/Content/Runtime/Textures/a.jpg'), 'Runtime/Textures/a.jpg')
        for huelle in ('Manifest.dsx', 'Content/', 'readme.txt', 'x/Runtime/Libraries/Pose/a.pz2', 'People/a/b.zip', '../data/x.dsf'):
            self.assertIsNone(G9dazpaket.ziel_von(huelle), huelle)

    def test_2_plan_gleich_konflikt(self):
        z = _zip(self.wurzel / 'a.zip', {'Content/data/v/a.dsf': b'12345', 'Content/data/v/b.dsf': b'xy', 'Manifest.dsx': b'<x/>'})
        paket = G9dazpaket(z, ziel=self.bib)
        plan = paket.plan()
        self.assertEqual(sorted(r for r, _g in plan['neu']), ['data/v/a.dsf', 'data/v/b.dsf'])
        self.assertFalse((self.bib / 'data').exists(), 'der Plan schreibt nichts')
        (self.bib / 'data' / 'v').mkdir(parents=True)
        (self.bib / 'data' / 'v' / 'a.dsf').write_bytes(b'12345')            # gleich
        (self.bib / 'data' / 'v' / 'b.dsf').write_bytes(b'anders!')          # Konflikt
        plan = paket.installieren()
        self.assertEqual(plan['gleich'], ['data/v/a.dsf'])
        self.assertEqual(len(plan['konflikt']), 1)
        self.assertEqual((self.bib / 'data' / 'v' / 'b.dsf').read_bytes(), b'anders!', 'bei Konflikt wird nichts geschrieben')
        self.assertFalse(G9dazpaket.manifest_datei('a.zip').exists())

    def test_3_innere_zips(self):
        innen = io.BytesIO()
        with zipfile.ZipFile(innen, 'w') as zf:
            zf.writestr('Content/People/Genesis 9/Clothing/S/s.duf', b'{}')
        anderes = io.BytesIO()
        with zipfile.ZipFile(anderes, 'w') as zf:
            zf.writestr('Content/People/Genesis 8 Female/Clothing/S/s.duf', b'{}')
        z = _zip(self.wurzel / 'v.zip', {'IM00000002-01_G9.zip': innen.getvalue(), 'AR07298691-01_G8F.zip': anderes.getvalue()})
        alle = G9dazpaket(z, ziel=self.bib).plan()
        self.assertEqual(alle['zips'], 2)
        nur = G9dazpaket(z, innen=['IM00000002-01_G9.zip'], ziel=self.bib).plan()
        self.assertEqual([r for r, _g in nur['neu']], ['People/Genesis 9/Clothing/S/s.duf'])

    def test_4_entfernen_genau_das_geschriebene(self):
        z = _zip(self.wurzel / 'e.zip', {'data/v/a.dsf': b'1', 'data/v/b.dsf': b'2'})
        G9dazpaket(z, ziel=self.bib).installieren()
        self.assertTrue((self.bib / 'data/v/a.dsf').exists())
        (self.bib / 'data/v/b.dsf').write_bytes(b'veraendert')
        weg, geaendert = G9dazpaket.entfernen('e.zip')
        self.assertEqual(weg, ['data/v/a.dsf'])
        self.assertEqual(geaendert, ['data/v/b.dsf'])
        self.assertTrue((self.bib / 'data/v/b.dsf').exists())
