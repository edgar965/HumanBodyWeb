# -*- coding: utf-8 -*-
"""Umbenennen und Löschen im Kontextmenü der Garderobe (`G9garderobepflege`, `G9stueckpapierkorb`, 05.10.2026).

Edgar (05.10.2026): „füge im Kontextmenü bei allen ein: Löschen, Umbenennen". Zusagen:

1. Umbenennen ändert nur den Anzeigenamen (die Kennung bleibt: Rezepte nennen sie); leer nimmt es zurück; zu lang oder mit Steuerzeichen → `ValueError`.
2. Ein ausgeblendetes Stück fehlt in der Liste, ein umbenanntes trägt den neuen Namen.
3. Ein Stück der Daz-Bibliothek wird nur ausgeblendet — keine Datei wird angefasst.
4. Ein eigenes Stück geht MIT seinen Dateien (`.duf`, Bild, `data/`, Texturen, eigene `.dsx`) in den Papierkorb, die Pfade unter der Wurzel bleiben; eine `.dsx` mit mehreren Assets bleibt.
5. Scheitert eine Bewegung, geht alles Bisherige zurück.
"""
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase
from Genesis9.garderobepflege import G9garderobepflege
from Genesis9.pfade import G9pfade
from Genesis9.stueckpapierkorb import G9stueckpapierkorb

DSX = '<ContentDBInstall><Assets><Asset VALUE="%s"><ContentType VALUE="Follower/Accessory"/></Asset></Assets></ContentDBInstall>'


class DieGarderobepflege(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.ordner = tempfile.TemporaryDirectory(dir=str(Path(__file__).parent))
        self.addCleanup(self.ordner.cleanup)
        self.basis = Path(self.ordner.name)
        self.objekte, self.eigene = self.basis / 'objekte', self.basis / 'eigene'
        for name, wert in (('objekte', self.objekte), ('eigene', self.eigene)):
            muster = mock.patch.object(G9pfade, name, classmethod(lambda cls, wert=wert: wert))
            muster.start()
            self.addCleanup(muster.stop)
        self.duf = self.eigene / 'People' / 'Genesis 9' / 'Clothing' / 'EIGEN' / 'Eigen Uhr l.duf'
        self.rel = self.duf.relative_to(self.eigene).as_posix()
        self._schreiben(self.duf, 'duf')
        self._schreiben(self.duf.with_suffix('.png'), 'icon')
        self._schreiben(self.eigene / 'data' / 'EIGEN' / 'Eigen Uhr l' / 'geo.dsf', 'geo')
        self._schreiben(self.eigene / 'Runtime' / 'Textures' / 'EIGEN' / 'Eigen Uhr l' / 'textur.png', 'bild')
        self._schreiben(self.eigene / 'Runtime' / 'Support' / 'EIGEN_Eigen_Uhr_l.dsx', DSX % self.rel)
        self._schreiben(self.eigene / 'Runtime' / 'Support' / 'EIGEN_Sammel.dsx', DSX % self.rel + DSX % 'andere.duf')   # zwei Assets: bleibt
        self._schreiben(self.eigene / 'People' / 'Genesis 9' / 'Clothing' / 'EIGEN' / 'Eigen Hut.duf', 'fremd')         # ein anderes Stück: bleibt

    @staticmethod
    def _schreiben(pfad, text):
        pfad.parent.mkdir(parents=True, exist_ok=True)
        pfad.write_text(text, encoding='utf-8')

    def _eintrag(self, **extra):
        return dict({'id': 'eigen_uhr_l', 'name': 'Eigen Uhr l', 'art': 'kleidung', 'datei': 'EIGEN/Eigen Uhr l.duf',
                     'wurzel': 'People/Genesis 9/Clothing', 'eigen': True}, **extra)

    def test_1_umbenennen_aendert_nur_den_anzeigenamen(self):
        stand = G9garderobepflege.umbenennen('eigen_uhr_l', '  Armband   uhr ')
        self.assertEqual(stand['namen'], {'eigen_uhr_l': 'Armband uhr'})
        self.assertEqual(G9garderobepflege.laden()['namen'], {'eigen_uhr_l': 'Armband uhr'})
        self.assertEqual(G9garderobepflege.umbenennen('eigen_uhr_l', '')['namen'], {})
        with self.assertRaises(ValueError):
            G9garderobepflege.umbenennen('eigen_uhr_l', 'x' * 61)
        with self.assertRaises(ValueError):
            G9garderobepflege.umbenennen('eigen_uhr_l', 'a\x00b')

    def test_2_die_liste_ohne_ausgeblendete_und_mit_neuen_namen(self):
        G9garderobepflege.umbenennen('b', 'Zweites')
        G9garderobepflege.loeschen({'id': 'c', 'name': 'C', 'art': 'kleidung', 'datei': 'x.duf'})
        liste = G9garderobepflege.anwenden([{'id': 'a', 'name': 'A'}, {'id': 'b', 'name': 'B'}, {'id': 'c', 'name': 'C'}])
        self.assertEqual([(s['id'], s['name']) for s in liste], [('a', 'A'), ('b', 'Zweites')])
        self.assertEqual(liste[1]['name_bibliothek'], 'B')

    def test_3_ein_daz_stueck_wird_nur_ausgeblendet(self):
        with mock.patch('Genesis9.garderobepflege.G9stueckpapierkorb.entsorgen') as entsorgen:
            ergebnis = G9garderobepflege.loeschen(self._eintrag(eigen=False))
        entsorgen.assert_not_called()
        self.assertEqual(ergebnis, {'art': 'ausgeblendet'})
        self.assertEqual(G9garderobepflege.laden()['ausgeblendet'], ['eigen_uhr_l'])
        G9garderobepflege.loeschen(self._eintrag(eigen=False))                       # zweimal: einmal eingetragen
        self.assertEqual(G9garderobepflege.laden()['ausgeblendet'], ['eigen_uhr_l'])

    def test_4_ein_eigenes_stueck_geht_mit_seinen_dateien_in_den_papierkorb(self):
        G9garderobepflege.umbenennen('eigen_uhr_l', 'Armbanduhr')
        with mock.patch('Genesis9.garderobe.G9garderobe.vergessen') as vergessen:
            ergebnis = G9garderobepflege.loeschen(self._eintrag())
        vergessen.assert_called_once()
        korb = Path(ergebnis['ziel'])
        self.assertEqual(ergebnis['art'], 'papierkorb')
        self.assertEqual(korb.parent, self.objekte / 'models' / 'Genesis9' / 'papierkorb')
        for rel in (self.rel, self.rel.replace('.duf', '.png'), 'data/EIGEN/Eigen Uhr l/geo.dsf',
                    'Runtime/Textures/EIGEN/Eigen Uhr l/textur.png', 'Runtime/Support/EIGEN_Eigen_Uhr_l.dsx'):
            self.assertTrue((korb / rel).is_file(), rel)
            self.assertFalse((self.eigene / rel).exists(), rel)
        self.assertTrue((self.eigene / 'Runtime' / 'Support' / 'EIGEN_Sammel.dsx').is_file())      # gehört auch dem anderen Stück
        self.assertTrue((self.eigene / 'People' / 'Genesis 9' / 'Clothing' / 'EIGEN' / 'Eigen Hut.duf').is_file())
        self.assertEqual(G9garderobepflege.laden()['namen'], {})                     # die Umbenennung des gelöschten Stücks ist hinfällig

    def test_5_scheitert_eine_bewegung_geht_alles_zurueck(self):
        echt = shutil.move
        aufrufe = []

        def move(quelle, ziel):
            aufrufe.append(quelle)
            if len(aufrufe) == 3:
                raise PermissionError('gesperrt')
            return echt(quelle, ziel)
        with mock.patch('Genesis9.stueckpapierkorb.shutil.move', side_effect=move), self.assertRaises(PermissionError):
            G9stueckpapierkorb.entsorgen(self.duf, 'eigen_uhr_l', self.eigene, datetime(2026, 10, 5, 12, 0, 0))
        self.assertTrue(self.duf.is_file())
        self.assertTrue(self.duf.with_suffix('.png').is_file())
        self.assertTrue((self.eigene / 'data' / 'EIGEN' / 'Eigen Uhr l' / 'geo.dsf').is_file())

    def test_6_ein_stueck_ausserhalb_der_wurzel_wird_nicht_angefasst(self):
        fremd = self.basis / 'daz' / 'x.duf'
        self._schreiben(fremd, 'daz')
        with self.assertRaises(ValueError):
            G9stueckpapierkorb.entsorgen(fremd, 'x', self.eigene)
        self.assertTrue(fremd.is_file())
