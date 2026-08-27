# -*- coding: utf-8 -*-
"""Component-Test der Kleider-Verwaltung: Route, JSON, Statuscodes.

Aus `core/tests/unit/test_kleiderverwaltung.py` herausgeloest (17.08.2026): Dort
standen zwei eigenstaendige Klassen in einer Datei, und die zweite fuhr HTTP —
das ist kein Unit-Test. Der Dienst wird weiter drueben einzeln geprueft; hier
geht es nur um die Schale.

Genau diese Adresse FEHLTE bis zum 17.08.2026, obwohl acht Aufrufstellen im
Frontend sie riefen: vier tote Kontextmenue-Punkte in zwei Listen.

Die Tests laufen ausschliesslich in einem Wegwerfverzeichnis unter ProjektTemp
(MEDIA_ROOT/tmp) — nicht im System-Temp auf C:, und nicht in der echten
Bibliothek unter `HumanBody/data/garment_library`.
"""
import shutil
from pathlib import Path

from django.test import Client, SimpleTestCase, override_settings
from django.urls import resolve

from core.dienste.kleiderbibliothek import Kleiderbibliothek
from core.projekt_temp import ProjektTemp

ADRESSE = '/api/character/garment/manage/'


class GarmentManageEndpunktTest(SimpleTestCase):
    """Route vorhanden, Fehler als JSON mit der richtigen Kennzahl."""

    def setUp(self):
        self._temp = ProjektTemp.ordner(prefix='kleiderhttp_')
        self.wurzel = Path(self._temp) / 'garment_library'
        (self.wurzel / 'Tops' / 'shirt').mkdir(parents=True)
        (self.wurzel / 'Tops' / 'shirt' / 'meta.json').write_text(
            '{}', encoding='utf-8')
        # Ohne Netzdatei nimmt `GarmentLibrary.scan()` den Ordner NICHT in den
        # Katalog auf (`load_metadata` verlangt garment.json, .mhclo oder .obj).
        (self.wurzel / 'Tops' / 'shirt' / 'shirt.obj').write_text(
            'o shirt\n', encoding='utf-8')
        self._ueberschreibung = override_settings(
            HUMANBODY_GARMENT_LIBRARY_DIR=str(self.wurzel))
        self._ueberschreibung.enable()
        # `Kleiderbibliothek._katalog` haengt an der KLASSE und lebt bis zum
        # Prozessende. Ohne dieses Leeren traegt der erste Test seinen Katalog
        # in alle folgenden — und in den echten Serverlauf danach.
        Kleiderbibliothek._katalog = None

    def tearDown(self):
        Kleiderbibliothek._katalog = None
        self._ueberschreibung.disable()
        shutil.rmtree(self._temp, ignore_errors=True)

    def test_route_existiert(self):
        self.assertEqual(resolve(ADRESSE).func.__name__, 'verwalten')

    def test_umbenennen_ueber_http(self):
        antwort = Client().post(ADRESSE,
                                data='{"action":"rename","id":"Tops/shirt",'
                                     '"new_name":"hemd"}',
                                content_type='application/json')
        self.assertEqual(antwort.status_code, 200, antwort.content)
        self.assertTrue((self.wurzel / 'Tops' / 'hemd').is_dir())

    def test_umbenennen_frischt_den_zwischenspeicher_auf(self):
        """DER BEFUND VOM 27.08.2026: Der Katalog blieb stehen.

        `garment_manage` schrieb `_garment_library = None` — eine Modulvariable,
        die es seit dem 18.08.2026 nicht mehr gibt (der Zwischenspeicher liegt
        in `Kleiderbibliothek`). `global` legte sie stumm neu an, niemand las
        sie, und die Kleiderliste zeigte bis zum Serverneustart Pfade, die es
        nicht mehr gab. Ohne Fehlermeldung.

        Gegenprobe: Nimmt man `Kleiderbibliothek.neu_einlesen()` in
        `Kleiderendpunkte.verwalten` wieder heraus, faellt dieser Test.
        """
        Kleiderbibliothek.holen()          # Katalog steht, mit „shirt"
        vorher = [s['id'] for s in Kleiderbibliothek.holen().catalog]
        self.assertTrue(any('shirt' in s for s in vorher), vorher)

        antwort = Client().post(ADRESSE,
                                data='{"action":"rename","id":"Tops/shirt",'
                                     '"new_name":"hemd"}',
                                content_type='application/json')
        self.assertEqual(antwort.status_code, 200, antwort.content)

        nachher = [s['id'] for s in Kleiderbibliothek.holen().catalog]
        self.assertFalse(any('shirt' in s for s in nachher),
                         'Der alte Pfad steht noch im Katalog: %s' % nachher)

    def test_unbekanntes_kleid_gibt_404_als_json(self):
        antwort = Client().post(ADRESSE,
                                data='{"action":"delete","id":"Tops/weg"}',
                                content_type='application/json')
        self.assertEqual(antwort.status_code, 404)
        self.assertIn('error', antwort.json())

    def test_kaputtes_json_gibt_400(self):
        antwort = Client().post(ADRESSE, data='{kein json',
                                content_type='application/json')
        self.assertEqual(antwort.status_code, 400)

    def test_get_ist_nicht_erlaubt(self):
        """Eine Adresse, die Dateien verschiebt, darf kein GET beantworten —
        sonst genügt ein <img src> auf einer fremden Seite."""
        self.assertEqual(Client().get(ADRESSE).status_code, 405)
