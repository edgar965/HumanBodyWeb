# -*- coding: utf-8 -*-
"""Einstellungen → Charakter (`/settings/charakter/`): KEIN Standard-Modell mehr.

GESCHICHTE
==========
19.09.2026 (Edgar: „in /settings/scene/ fehlt die Möglichkeit, auch ein Genesis,
UMA usw. als Standard-Modell auszuwählen"): Die Seite bekam drei Felder — Name
(`default_model_scene`), Figurart und Bereich (`ui_prefs`) — samt Figurwahl-Dialog.

30.09.2026 (Edgar: „entferne das Standardmodell und die Standard Animation. Auf der
Seite /Charakter/ soll immer nur der letzte geladene Modell und die letzte Animation
geladen werden"): Die Felder sind weg, die Szene merkt sich selbst, was zuletzt
geladen war (`viewer/charakter/letztewahl.js`). Die Datenbankspalten bleiben stehen
— andere Seiten haben eigene Vorgaben (`szenenseite.py`, `szene-ladezeit.md`).

WAS DIESE DATEI SEITHER ABSICHERT
=================================
1. Die Seite liefert weder die Modell- noch die Animationsfelder aus, und sie lädt
   den Figurwahl-Dialog (`standardmodell.js`) nicht mehr.
2. Speichern der Seite lässt die gespeicherten Werte stehen — Name, Figurart,
   Bereich und Animation. Ein Formular ohne diese Felder darf sie nicht leeren
   (bis zum 30.09. setzte `uebernehmen` den Namen ohne Feld auf
   `femaleWithClothes` zurück).
3. Die Schnittstelle der Szene liefert die stehengebliebenen Werte unverändert.
4. Die übrigen `ui_prefs`-Vorlieben der Seite (`default_pose`,
   `kleider_bone_model`): ein leeres Feld löscht nichts.
"""

from django.test import Client, TestCase
from django.urls import reverse

from core.models import AppSettings


class SzeneOhneStandardmodell(TestCase):
    #: Ein gespeicherter Stand aus der Zeit mit Standard-Modell.
    ALT = {
        'default_model_scene': 'Victoria 9',
        'default_anim_scene': '/api/character/bvh/Aist/tanz_01/',
    }
    ALT_PREFS = {
        'default_model_scene_quelle': 'genesis9',
        'default_model_scene_bereich': 'standard',
    }

    def setUp(self):
        self.client = Client(HTTP_HOST='127.0.0.1')
        s = AppSettings.load()
        for name, wert in self.ALT.items():
            setattr(s, name, wert)
        s.ui_prefs = {**(s.ui_prefs or {}), **self.ALT_PREFS}
        s.save()

    def _speichern(self, **felder):
        antwort = self.client.post(reverse('settings_scene'), felder)
        self.assertEqual(antwort.status_code, 302)
        return AppSettings.load()

    def test_seite_zeigt_keine_modell_und_animationsfelder(self):
        text = self.client.get(reverse('settings_scene')).content.decode('utf-8')
        for fehlt in (
            'name="default_model_scene"',
            'name="default_model_scene_quelle"',
            'name="default_model_scene_bereich"',
            'name="default_anim_scene"',
            'standardmodell.js',
            'data-tun="waehlen"',
            'id="default-model-scene"',
        ):
            self.assertNotIn(fehlt, text)
        # Gegenprobe: die Seite ist die richtige und trägt ihre übrigen Felder.
        self.assertIn('name="show_rig_scene"', text)
        self.assertIn('name="default_pose"', text)

    def test_speichern_laesst_die_alten_werte_stehen(self):
        s = self._speichern(show_rig_scene='on', selection_opacity='0.3')
        self.assertEqual(s.default_model_scene, 'Victoria 9')
        self.assertEqual(s.default_anim_scene, '/api/character/bvh/Aist/tanz_01/')
        self.assertEqual(s.ui_prefs['default_model_scene_quelle'], 'genesis9')
        self.assertEqual(s.ui_prefs['default_model_scene_bereich'], 'standard')

    def test_schnittstelle_der_szene_liefert_die_alten_werte(self):
        self._speichern(show_rig_scene='on')
        daten = self.client.get(reverse('humanbody_settings_api')).json()
        self.assertEqual(daten['scene'], 'Victoria 9')
        self.assertEqual(daten['ui_prefs']['default_model_scene_quelle'], 'genesis9')
        self.assertEqual(daten['ui_prefs']['default_model_scene_bereich'], 'standard')

    def test_leere_felder_loeschen_nichts(self):
        self._speichern(default_pose='t_pose', kleider_bone_model='Rig2')
        s = self._speichern(default_pose='', kleider_bone_model='')
        self.assertEqual(s.ui_prefs['default_pose'], 't_pose')
        self.assertEqual(s.ui_prefs['kleider_bone_model'], 'Rig2')
