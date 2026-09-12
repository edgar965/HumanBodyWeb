# -*- coding: utf-8 -*-
u"""Effektbeobachter — nur die `Effekte:`-Zeilen zaehlen als Fortschritt.

WARUM (12.09.2026): Blender schreibt beim Start Fremdes ins Protokoll; die
letzte Zeile des Nachschubs war auf der Seite einmal
`ValueError: expected Panel, HUMANBODY_PT_main …`. Gegenprobe: Der
Logbeobachter selbst (ohne Filter) nimmt genau diese Zeile — sonst pruefte
der Test nichts.
"""
from django.test import SimpleTestCase

from core.effekte.effektbeobachter import Effektbeobachter
from core.pipelines.logbeobachter import Logbeobachter


class Auftragsattrappe:
    progress = 0
    progress_detail = ''

    def save(self, update_fields=None):
        pass


NACHSCHUB = ('Effekte: Simulation Bild 30 von 300 — 30 / 600\n'
             '[MB-Lab.file_ops] Character data loaded\n'
             'ValueError: expected Panel, HUMANBODY_PT_main class "draw"\n')


class EffektbeobachterTest(SimpleTestCase):

    def test_nimmt_die_letzte_effekte_zeile_ohne_praefix(self):
        auftrag = Auftragsattrappe()
        self.assertTrue(Effektbeobachter(auftrag, 'x.log', 300).auswerten(NACHSCHUB, jetzt=10.0))
        self.assertEqual(auftrag.progress, int(30 / 600 * Logbeobachter.DECKEL))
        self.assertTrue(auftrag.progress_detail.startswith('Simulation Bild 30 von 300'))
        self.assertNotIn('ValueError', auftrag.progress_detail)

    def test_ohne_effekte_zeile_bleibt_alles_wie_es_war(self):
        auftrag = Auftragsattrappe()
        self.assertFalse(Effektbeobachter(auftrag, 'x.log', 300).auswerten(
            'ValueError: irgendwas\n', jetzt=10.0))
        self.assertEqual(auftrag.progress_detail, '')

    def test_gegenprobe_der_ungefilterte_beobachter_naehme_die_fremde_zeile(self):
        auftrag = Auftragsattrappe()
        Logbeobachter(auftrag, 'x.log', 300).auswerten(NACHSCHUB, jetzt=10.0)
        self.assertIn('ValueError', auftrag.progress_detail)
