# -*- coding: utf-8 -*-
"""`/api/character/garment/download/available/` — ohne Netz.

WARUM EIGENE DATEI: Dieser Endpunkt ist der einzige der 120, der ins INTERNET
greift (`MakeHumanDownloader` fragt GitHub nach Asset-Paketen). In der
Sammeltabelle in `test_endpunkte.py` hat er deshalb nichts zu suchen: Ein Test,
der ohne Netz rot wird, wird abgeschaltet — und schaltet die anderen 119 mit ab.

Hier wird stattdessen der Netzzugriff umgelenkt. Geprüft wird, was das Projekt
verantwortet:

* Der Endpunkt antwortet mit 200 und den beiden Schlüsseln, die
  `kleiderdownload.js` liest (`packs`, `builtin_assets`).
* **Fällt die Abfrage der eingebauten Assets aus, bleibt die Antwort stehen.**
  Der Endpunkt fängt das ab und liefert eine leere Liste — sonst wäre die
  Kleider-Seite bei jeder GitHub-Störung leer.

Die Umlenkung fasst JEDES Modul an, das den Namen führt: `garment_download_available`
holt `MakeHumanDownloader` erst im Rumpf aus `GarmentFitter`, also wird dort
gepatcht. Greift der Patch ins Leere, wirft dieser Test — eine stumme
Nulloperation wäre genau der Fehler, den Test-Umleitungen sonst machen.
"""

from django.test import Client, SimpleTestCase, override_settings

ADRESSE = '/api/character/garment/download/available/'


class Downloaderattrappe:
    """Antwortet wie der echte, ohne ins Netz zu gehen."""

    #: Wird auf True gesetzt, wenn `list_builtin_assets` werfen soll.
    bricht_ein = False

    def __init__(self, *args, **kwargs):
        pass

    def list_available_packs(self):
        return [{'name': 'shirts01', 'files': 3}]

    def list_builtin_assets(self):
        if Downloaderattrappe.bricht_ein:
            raise OSError('GitHub nicht erreichbar')
        return [{'name': 'jeans01'}]


@override_settings(ALLOWED_HOSTS=['*'])
class KleiderDownloadTest(SimpleTestCase):

    def setUp(self):
        import GarmentFitter
        self._echt = GarmentFitter.MakeHumanDownloader
        GarmentFitter.MakeHumanDownloader = Downloaderattrappe
        Downloaderattrappe.bricht_ein = False
        self.addCleanup(setattr, GarmentFitter, 'MakeHumanDownloader', self._echt)

    def test_die_umlenkung_greift_wirklich(self):
        """Null Treffer wäre ein Fehler, kein stilles Weiter."""
        import GarmentFitter
        self.assertIs(GarmentFitter.MakeHumanDownloader, Downloaderattrappe)

    def test_liefert_pakete_und_eingebaute(self):
        antwort = Client().get(ADRESSE)
        self.assertEqual(antwort.status_code, 200)
        daten = antwort.json()
        self.assertEqual([p['name'] for p in daten['packs']], ['shirts01'])
        self.assertEqual([a['name'] for a in daten['builtin_assets']], ['jeans01'])

    def test_ausfall_der_eingebauten_laesst_die_antwort_stehen(self):
        """Sonst wäre die Kleider-Seite bei jeder GitHub-Störung leer."""
        Downloaderattrappe.bricht_ein = True
        antwort = Client().get(ADRESSE)
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(antwort.json()['builtin_assets'], [])
        self.assertTrue(antwort.json()['packs'])
