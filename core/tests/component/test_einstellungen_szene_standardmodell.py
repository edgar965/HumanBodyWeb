# -*- coding: utf-8 -*-
"""Einstellungen → Szene: das Standard-Modell in jeder Figurart.

WARUM (Edgar, 19.09.2026): „in /settings/scene/ fehlt die Möglichkeit, auch
ein Genesis, UMA usw. als Standard-Modell auszuwählen. Mach die
Modellauswahl in einem Dialog." Das Formular trägt seither drei Felder —
Name (`default_model_scene`, die Spalte wie bisher), Figurart und Bereich
(`ui_prefs`) —, und die Szene liest alle drei über `/api/settings/humanbody/`.

1. Die Seite zeigt die drei Felder mit dem gespeicherten Stand und den Knopf
   zum Dialog; kein `<select>` mehr.
2. Speichern legt Figurart und Bereich in `ui_prefs`, der Name in der Spalte.
3. Die Schnittstelle der Szene liefert beides.
4. Ohne die neuen Felder (altes Formular) bleiben gespeicherte Figurart und
   Bereich stehen — ein leeres Feld löscht nichts.
"""

from django.test import Client, TestCase
from django.urls import reverse

from core.models import AppSettings


class SzeneStandardmodell(TestCase):

    def setUp(self):
        self.client = Client(HTTP_HOST='127.0.0.1')

    def _speichern(self, **felder):
        antwort = self.client.post(reverse('settings_scene'), felder)
        self.assertEqual(antwort.status_code, 302)
        return AppSettings.load()

    def test_seite_zeigt_felder_und_knopf(self):
        s = AppSettings.load()
        s.default_model_scene = 'Victoria 9'
        s.ui_prefs = {**(s.ui_prefs or {}), 'default_model_scene_quelle': 'genesis9',
                      'default_model_scene_bereich': 'standard'}
        s.save()
        text = self.client.get(reverse('settings_scene')).content.decode('utf-8')
        self.assertRegex(text, r'name="default_model_scene" data-feld="name"\s+value="Victoria 9"')
        self.assertRegex(text, r'name="default_model_scene_quelle" data-feld="quelle"\s+value="genesis9"')
        self.assertRegex(text, r'name="default_model_scene_bereich" data-feld="bereich"\s+value="standard"')
        self.assertIn('data-tun="waehlen"', text)
        self.assertIn('standardmodell.js', text)
        self.assertIn('figurwahldialog.css', text)
        self.assertNotIn('id="default-model-scene"', text)

    def test_speichern_legt_figurart_und_bereich_ab(self):
        s = self._speichern(default_model_scene='Anprobe_a.glb',
                            default_model_scene_quelle='uma',
                            default_model_scene_bereich='gespeichert')
        self.assertEqual(s.default_model_scene, 'Anprobe_a.glb')
        self.assertEqual(s.ui_prefs['default_model_scene_quelle'], 'uma')
        self.assertEqual(s.ui_prefs['default_model_scene_bereich'], 'gespeichert')

    def test_schnittstelle_der_szene_liefert_beides(self):
        self._speichern(default_model_scene='Female_Caucasian',
                        default_model_scene_quelle='modell',
                        default_model_scene_bereich='standard')
        daten = self.client.get(reverse('humanbody_settings_api')).json()
        self.assertEqual(daten['scene'], 'Female_Caucasian')
        self.assertEqual(daten['ui_prefs']['default_model_scene_quelle'], 'modell')
        self.assertEqual(daten['ui_prefs']['default_model_scene_bereich'], 'standard')

    def test_leere_felder_loeschen_nichts(self):
        self._speichern(default_model_scene='Victoria 9',
                        default_model_scene_quelle='genesis9',
                        default_model_scene_bereich='standard')
        s = self._speichern(default_model_scene='Victoria 9')
        self.assertEqual(s.ui_prefs['default_model_scene_quelle'], 'genesis9')
        self.assertEqual(s.ui_prefs['default_model_scene_bereich'], 'standard')
