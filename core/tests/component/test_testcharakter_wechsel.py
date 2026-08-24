# -*- coding: utf-8 -*-
"""`test_switch_character` leert ein Verzeichnis — und nimmt kein GET mehr an.

DER BEFUND (17.08.2026): Die Ansicht stand auf `@require_GET` und macht ein
`shutil.rmtree` auf `TestCharakter/data/humanBody`, um es aus
`charmorph_data/<name>/` neu aufzubauen. Ein `<img src="…/switch/?name=x">` auf
einer fremden Seite hat damit ein Verzeichnis geleert. Gefunden vom Werkzeug
`schreibrouten`, das nach Ansichten sucht, die im Rumpf löschen und trotzdem GET
beantworten.

Der Test ruft **nie mit einem gültigen Namen** — sonst würde er das
Verzeichnis tatsächlich neu aufbauen. Ein unbekannter Name endet vor dem
`rmtree` mit 400, und genau das wird geprüft.
"""

from django.test import Client, SimpleTestCase

ADRESSE = '/api/character-test/switch/'


class TestcharakterWechselTest(SimpleTestCase):

    def test_get_wird_abgewiesen(self):
        """405, nicht 400: Die Methodenprüfung greift VOR der Ansicht."""
        antwort = Client().get(ADRESSE + '?name=mb_male')
        self.assertEqual(antwort.status_code, 405,
                         'GET auf diese Adresse leert ein Verzeichnis')

    def test_post_mit_unbekanntem_namen_ist_400(self):
        """Gegenprobe: Der Schutz sperrt die Oberfläche nicht aus. 400 heisst
        „Ansicht lief, Charakter gibt es nicht" — und zwar bevor gelöscht wird.
        """
        antwort = Client().post(ADRESSE + '?name=gibtesnicht_xyz')
        self.assertEqual(antwort.status_code, 400)
        self.assertIn('error', antwort.json())

    def test_post_ohne_namen_listet_auf(self):
        """Ohne Namen antwortet die Ansicht mit den verfügbaren Charakteren —
        auch das erst nach der Methodenprüfung."""
        antwort = Client().post(ADRESSE)
        self.assertEqual(antwort.status_code, 400)
        self.assertIn('available', antwort.json())
