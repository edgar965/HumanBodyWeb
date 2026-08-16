# -*- coding: utf-8 -*-
"""Waechter fuer Bvhverwaltung — die sieben Aktionen der BVH-Bibliothek.

WARUM (Umbau 16.08.2026)
------------------------
`bvh_manage` war eine Funktion mit 149 Zeilen und sieben `elif`-Zweigen ohne
jeden Test. Beim Zerlegen fiel auf, dass die Cache-Behandlung nie gegriffen hat:
Geloescht, umbenannt und verschoben wurde `<name>.json` — die Zwischenspeicher
heissen aber `<name>_retarget_<pruefsumme>.json`. In der echten Bibliothek:
7.067 BVH-Dateien, 40 Cache-Dateien, null Treffer fuer das gesuchte Muster.

Die Tests laufen ausschliesslich in einem Wegwerfverzeichnis. An die echte
Bibliothek unter HumanBody/data/ fasst hier nichts.

Das Wegwerfverzeichnis liegt unter ProjektTemp (MEDIA_ROOT/tmp), NICHT im
System-Temp: `tempfile.TemporaryDirectory()` ohne `dir=` schreibt auf C:, und
das ist in diesem Projekt verboten — es hat dort einmal rund 100 GB
Datenmuell hinterlassen. Der erste Wurf dieser Datei hatte genau den Fehler.
"""
import shutil
from pathlib import Path

from django.test import SimpleTestCase, override_settings

from core.dienste.bvhverwaltung import Bvhverwaltung, BvhFehler
from core.projekt_temp import ProjektTemp


class BvhverwaltungTest(SimpleTestCase):
    """Jede Aktion einmal — und die Cache-Dateien dabei im Auge."""

    def setUp(self):
        self._temp = ProjektTemp.ordner(prefix='bvhtest_')
        # bvh_wurzel() nimmt das Elternverzeichnis, ausser der Ordner heisst
        # schon 'bvh'. Also legen wir genau so einen an.
        self.wurzel = Path(self._temp) / 'bvh'
        (self.wurzel / 'Aist').mkdir(parents=True)
        self._ueberschreibung = override_settings(HUMANBODY_BVH_DIR=str(self.wurzel))
        self._ueberschreibung.enable()

    def tearDown(self):
        self._ueberschreibung.disable()
        shutil.rmtree(self._temp, ignore_errors=True)

    def _anlegen(self, kategorie, name, caches=()):
        pfad = self.wurzel / kategorie / f'{name}.bvh'
        pfad.parent.mkdir(parents=True, exist_ok=True)
        pfad.write_text('HIERARCHY\nFrames: 2\n', encoding='utf-8')
        for h in caches:
            (pfad.parent / f'{name}_retarget_{h}.json').write_text('{}',
                                                                   encoding='utf-8')
        return pfad

    # ------------------------------------------------------------------ Dateien

    def test_loeschen_nimmt_die_caches_mit(self):
        """Der Kern des Befunds: Zwischenspeicher blieben bisher liegen."""
        pfad = self._anlegen('Aist', 'Tanz', caches=('881259c8', 'eb045f10'))
        Bvhverwaltung.ausfuehren({'action': 'delete', 'category': 'Aist',
                                  'name': 'Tanz'})
        self.assertFalse(pfad.exists())
        self.assertEqual(list(pfad.parent.glob('*.json')), [])

    def test_loeschen_meldet_fehlende_datei(self):
        with self.assertRaises(BvhFehler) as f:
            Bvhverwaltung.ausfuehren({'action': 'delete', 'category': 'Aist',
                                      'name': 'GibtsNicht'})
        self.assertEqual(f.exception.kennzahl, 404)

    def test_umbenennen_zieht_die_caches_nach(self):
        self._anlegen('Aist', 'Alt', caches=('881259c8',))
        Bvhverwaltung.ausfuehren({'action': 'rename', 'category': 'Aist',
                                  'name': 'Alt', 'new_name': 'Neu'})
        ordner = self.wurzel / 'Aist'
        self.assertTrue((ordner / 'Neu.bvh').is_file())
        self.assertFalse((ordner / 'Alt.bvh').exists())
        self.assertEqual([p.name for p in ordner.glob('*.json')],
                         ['Neu_retarget_881259c8.json'])

    def test_umbenennen_ueberschreibt_nicht(self):
        self._anlegen('Aist', 'Alt')
        self._anlegen('Aist', 'Belegt')
        with self.assertRaises(BvhFehler) as f:
            Bvhverwaltung.ausfuehren({'action': 'rename', 'category': 'Aist',
                                      'name': 'Alt', 'new_name': 'Belegt'})
        self.assertEqual(f.exception.kennzahl, 409)
        self.assertTrue((self.wurzel / 'Aist' / 'Alt.bvh').is_file())

    def test_verschieben_nimmt_die_caches_mit(self):
        self._anlegen('Aist', 'Tanz', caches=('881259c8',))
        Bvhverwaltung.ausfuehren({'action': 'move', 'category': 'Aist',
                                  'name': 'Tanz', 'new_category': 'Mixamo'})
        ziel = self.wurzel / 'Mixamo'
        self.assertTrue((ziel / 'Tanz.bvh').is_file())
        self.assertTrue((ziel / 'Tanz_retarget_881259c8.json').is_file())
        self.assertFalse((self.wurzel / 'Aist' / 'Tanz.bvh').exists())

    def test_kopieren_laesst_das_original_stehen(self):
        self._anlegen('Aist', 'Tanz')
        Bvhverwaltung.ausfuehren({'action': 'copy', 'category': 'Aist',
                                  'name': 'Tanz', 'new_name': 'Tanz_Kopie'})
        self.assertTrue((self.wurzel / 'Aist' / 'Tanz.bvh').is_file())
        self.assertTrue((self.wurzel / 'Aist' / 'Tanz_Kopie.bvh').is_file())

    # ------------------------------------------------------------------- Ordner

    def test_ordner_anlegen_und_loeschen(self):
        Bvhverwaltung.ausfuehren({'action': 'create_folder',
                                  'folder_name': 'Neuer Ordner'})
        self.assertTrue((self.wurzel / 'Neuer Ordner').is_dir())
        Bvhverwaltung.ausfuehren({'action': 'delete_folder',
                                  'category': 'Neuer Ordner'})
        self.assertFalse((self.wurzel / 'Neuer Ordner').exists())

    def test_voller_ordner_bleibt_stehen(self):
        self._anlegen('Aist', 'Tanz')
        with self.assertRaises(BvhFehler) as f:
            Bvhverwaltung.ausfuehren({'action': 'delete_folder',
                                      'category': 'Aist'})
        self.assertEqual(f.exception.kennzahl, 409)
        self.assertTrue((self.wurzel / 'Aist' / 'Tanz.bvh').is_file())

    def test_ordner_umbenennen(self):
        self._anlegen('Aist', 'Tanz')
        Bvhverwaltung.ausfuehren({'action': 'rename_folder', 'category': 'Aist',
                                  'new_name': 'Ballett'})
        self.assertTrue((self.wurzel / 'Ballett' / 'Tanz.bvh').is_file())

    # ------------------------------------------------------------- Abweisungen

    def test_unbekannte_aktion(self):
        with self.assertRaises(BvhFehler) as f:
            Bvhverwaltung.ausfuehren({'action': 'formatiere_festplatte'})
        self.assertEqual(f.exception.kennzahl, 400)

    def test_ausbruch_aus_der_bibliothek(self):
        """`..` in der Kategorie darf nicht aus der Bibliothek fuehren."""
        with self.assertRaises(BvhFehler) as f:
            Bvhverwaltung.ausfuehren({'action': 'delete', 'category': '../..',
                                      'name': 'geheim'})
        self.assertIn(f.exception.kennzahl, (400, 404))

    def test_fehlende_pflichtfelder(self):
        with self.assertRaises(BvhFehler) as f:
            Bvhverwaltung.ausfuehren({'action': 'rename', 'category': 'Aist'})
        self.assertEqual(f.exception.kennzahl, 400)
