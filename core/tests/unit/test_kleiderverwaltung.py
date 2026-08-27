# -*- coding: utf-8 -*-
"""Wächter für Kleiderverwaltung — die vier Aktionen der Kleider-Bibliothek.

WARUM (17.08.2026)
------------------
Die Kontextmenüs der Kleider- und der MakeHuman-Liste bieten Umbenennen,
Verschieben, Kopieren und Löschen an und rufen dafür
`/api/character/garment/manage/`. **Diesen Endpunkt gab es nicht.** Acht
Aufrufstellen in zwei Modulen liefen in eine 404, der umgebende `catch` schrieb
die Meldung nur in die Konsole — für den Benutzer passierte beim Klick nichts.

Gefunden nicht durch Ausprobieren, sondern durch einen Abgleich aller
Adress-Literale des Frontends gegen Djangos URL-Konfiguration. Von 94 Adressen
war genau diese eine unbekannt.

Die Tests laufen ausschliesslich in einem Wegwerfverzeichnis. An die echte
Bibliothek unter `HumanBody/data/garment_library` fasst hier nichts.

Die HTTP-Schale (Route, Statuscodes) steht seit dem 17.08.2026 daneben in
`core/tests/component/test_kleider_endpunkt.py` — zwei eigenstaendige Klassen in
einer Datei waren ein Befund von `klassen-je-datei`, und eine davon fuhr HTTP.

Das Wegwerfverzeichnis liegt unter ProjektTemp (MEDIA_ROOT/tmp), NICHT im
System-Temp: `tempfile.TemporaryDirectory()` ohne `dir=` schreibt auf C:, und
das ist in diesem Projekt verboten.
"""
import shutil
from pathlib import Path

from django.test import SimpleTestCase, override_settings

from core.dienste.kleiderverwaltung import (PAPIERKORB, KleiderFehler,
                                            Kleiderverwaltung)
from core.projekt_temp import ProjektTemp


class KleiderverwaltungTest(SimpleTestCase):
    """Jede Aktion einmal, dazu die Wege aus der Bibliothek heraus."""

    def setUp(self):
        self._temp = ProjektTemp.ordner(prefix='kleidertest_')
        self.wurzel = Path(self._temp) / 'garment_library'
        self.wurzel.mkdir(parents=True)
        self._ueberschreibung = override_settings(
            HUMANBODY_GARMENT_LIBRARY_DIR=str(self.wurzel))
        self._ueberschreibung.enable()

    def tearDown(self):
        self._ueberschreibung.disable()
        shutil.rmtree(self._temp, ignore_errors=True)

    def _anlegen(self, kategorie, name, dateien=('meta.json', 'mesh.obj')):
        """Ein Kleid ist ein VERZEICHNIS mit Metadaten, Netz und Textur."""
        ordner = self.wurzel / kategorie / name
        ordner.mkdir(parents=True, exist_ok=True)
        for datei in dateien:
            (ordner / datei).write_text('{}', encoding='utf-8')
        return ordner

    # ---------------------------------------------------------------- Aktionen

    def test_umbenennen_verschiebt_den_ordner_mitsamt_meta(self):
        self._anlegen('Tops', 'shirt')
        antwort = Kleiderverwaltung.ausfuehren(
            {'action': 'rename', 'id': 'Tops/shirt', 'new_name': 'hemd'})
        self.assertEqual(antwort['id'], 'Tops/hemd')
        self.assertFalse((self.wurzel / 'Tops' / 'shirt').exists())
        self.assertTrue((self.wurzel / 'Tops' / 'hemd' / 'meta.json').is_file())

    def test_verschieben_nimmt_die_dateien_in_die_neue_kategorie_mit(self):
        self._anlegen('Tops', 'shirt')
        antwort = Kleiderverwaltung.ausfuehren(
            {'action': 'move', 'id': 'Tops/shirt', 'target_category': 'Unten'})
        self.assertEqual(antwort['id'], 'Unten/shirt')
        self.assertTrue((self.wurzel / 'Unten' / 'shirt' / 'mesh.obj').is_file())
        self.assertFalse((self.wurzel / 'Tops' / 'shirt').exists())

    def test_kopieren_laesst_das_original_stehen(self):
        self._anlegen('Tops', 'shirt')
        Kleiderverwaltung.ausfuehren(
            {'action': 'copy', 'id': 'Tops/shirt', 'new_name': 'shirt_kopie'})
        self.assertTrue((self.wurzel / 'Tops' / 'shirt' / 'meta.json').is_file())
        self.assertTrue(
            (self.wurzel / 'Tops' / 'shirt_kopie' / 'meta.json').is_file())

    def test_loeschen_geht_in_den_papierkorb(self):
        """Kein `rmtree` in den Produktivdaten — der Ordner zieht um.

        Der Bibliotheks-Scanner überspringt Ordner mit Punkt am Anfang; für die
        Oberfläche ist das Kleid damit weg, auf der Platte bleibt es.
        """
        self._anlegen('Tops', 'shirt')
        antwort = Kleiderverwaltung.ausfuehren(
            {'action': 'delete', 'id': 'Tops/shirt'})
        self.assertFalse((self.wurzel / 'Tops' / 'shirt').exists())
        ziel = self.wurzel / PAPIERKORB / 'Tops__shirt'
        self.assertTrue((ziel / 'meta.json').is_file(), antwort)
        self.assertTrue(PAPIERKORB.startswith('.'),
                        'Der Papierkorb muss vom Scan übersprungen werden')

    def test_zweimal_loeschen_ueberschreibt_nicht(self):
        self._anlegen('Tops', 'shirt', dateien=('erste.json',))
        Kleiderverwaltung.ausfuehren({'action': 'delete', 'id': 'Tops/shirt'})
        self._anlegen('Tops', 'shirt', dateien=('zweite.json',))
        Kleiderverwaltung.ausfuehren({'action': 'delete', 'id': 'Tops/shirt'})
        korb = self.wurzel / PAPIERKORB
        self.assertTrue((korb / 'Tops__shirt' / 'erste.json').is_file())
        self.assertTrue((korb / 'Tops__shirt_2' / 'zweite.json').is_file())

    # ----------------------------------------------------------- Ablehnungen

    def test_unbekannte_aktion(self):
        with self.assertRaises(KleiderFehler) as fall:
            Kleiderverwaltung.ausfuehren({'action': 'formatieren', 'id': 'a/b'})
        self.assertEqual(fall.exception.kennzahl, 400)

    def test_fehlendes_feld(self):
        self._anlegen('Tops', 'shirt')
        with self.assertRaises(KleiderFehler) as fall:
            Kleiderverwaltung.ausfuehren({'action': 'rename',
                                          'id': 'Tops/shirt'})
        self.assertEqual(fall.exception.kennzahl, 400)

    def test_unbekanntes_kleid_ist_404(self):
        with self.assertRaises(KleiderFehler) as fall:
            Kleiderverwaltung.ausfuehren({'action': 'delete',
                                          'id': 'Tops/gibtesnicht'})
        self.assertEqual(fall.exception.kennzahl, 404)

    def test_vorhandenes_ziel_ist_409(self):
        self._anlegen('Tops', 'shirt')
        self._anlegen('Tops', 'hemd')
        with self.assertRaises(KleiderFehler) as fall:
            Kleiderverwaltung.ausfuehren({'action': 'rename',
                                          'id': 'Tops/shirt',
                                          'new_name': 'hemd'})
        self.assertEqual(fall.exception.kennzahl, 409)

    def test_ausbruch_ueber_punktpunkt(self):
        """`new_name` mit `..` wäre ein Weg aus der Bibliothek heraus."""
        self._anlegen('Tops', 'shirt')
        fremd = Path(self._temp) / 'fremd'
        fremd.mkdir()
        for daten in ({'action': 'rename', 'id': 'Tops/shirt',
                       'new_name': '../../fremd/geklaut'},
                      {'action': 'move', 'id': 'Tops/shirt',
                       'target_category': '../fremd'},
                      {'action': 'copy', 'id': 'Tops/shirt',
                       'new_name': '../../fremd/kopie'},
                      {'action': 'delete', 'id': '../../fremd'}):
            with self.assertRaises(KleiderFehler, msg=daten):
                Kleiderverwaltung.ausfuehren(daten)
        self.assertEqual(list(fremd.iterdir()), [])
        self.assertTrue((self.wurzel / 'Tops' / 'shirt').is_dir())

    def test_kennung_ohne_kategorie_wird_abgelehnt(self):
        """`id` ist immer `<kategorie>/<name>` — sonst greift die Prüfung ins
        Leere und ein einzelner Name träfe die Wurzel."""
        for kennung in ('shirt', 'a/b/c', '', 'Tops/'):
            with self.assertRaises(KleiderFehler, msg=kennung):
                Kleiderverwaltung.ausfuehren({'action': 'delete',
                                              'id': kennung})

    def test_punkt_am_anfang_wird_abgelehnt(self):
        """Ein Kleid namens `.x` wäre nach dem Umbenennen unsichtbar — der
        Scanner überspringt solche Ordner. Das sähe wie Datenverlust aus."""
        self._anlegen('Tops', 'shirt')
        with self.assertRaises(KleiderFehler):
            Kleiderverwaltung.ausfuehren({'action': 'rename',
                                          'id': 'Tops/shirt',
                                          'new_name': '.versteckt'})
