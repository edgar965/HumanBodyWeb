# -*- coding: utf-8 -*-
u"""Hilfe -> Animationseffekte: die Seite steht, ihre Texte kommen aus Python.

WARUM (Edgar, 12.09.2026: „schreibe schon mal alles hinein in Hilfe -
Animationseffekte"): Was zu Mimik, Haaren, Kleidung und Wind
zusammengetragen wurde, gehoert ins Projekt — sonst steht es nur in einer
Sitzung.

Geprueft wird dreierlei:

1. Die Seite antwortet, haengt im Menue und laesst die djangoBase-Seiten
   stehen (dort ist das Projekt am 27.08.2026 schon einmal hineingelaufen).
2. Jede Zeile der Daten steht auf der Seite — und KEINE steht in der
   Vorlage: Ein Kandidatenname im HTML waere eine Behauptung, die niemand
   mehr nachprueft.
3. Der Stand bleibt ehrlich: Kein Kandidat behauptet „läuft hier" ohne den
   Nachweis im Bestand; Edgars Entscheidung gegen Blender Cloth bleibt
   aufgefuehrt; jede Quelle ist eine Adresse.
"""
from pathlib import Path

from django.conf import settings
from django.test import Client, SimpleTestCase
from django.urls import reverse
from django.utils.html import escape

from core.dienste.animationseffekte import Animationseffekte
from core.dienste.effektkandidaten import Effektkandidaten


class SeiteAnimationseffekte(SimpleTestCase):

    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.antwort = Client().get(reverse('hilfe_animationseffekte'))
        cls.text = cls.antwort.content.decode('utf-8')
        cls.vorlage = (Path(settings.BASE_DIR) / 'templates' / 'hilfe'
                       / 'animationseffekte.html').read_text(encoding='utf-8')

    def test_antwortet_unter_deutscher_adresse(self):
        self.assertEqual(self.antwort.status_code, 200)
        self.assertEqual(reverse('hilfe_animationseffekte'),
                         '/hilfe/animationseffekte/')

    def test_haengt_im_menue_und_djangobase_bleibt_erreichbar(self):
        self.assertIn('href="/hilfe/animationseffekte/"', self.text)
        self.assertEqual(Client().get('/hilfe/versionen/').status_code, 200)

    def test_jede_schicht_jeder_kandidat_jede_quelle_steht_auf_der_seite(self):
        for s in Animationseffekte.schichten():
            self.assertIn(escape(s['schicht']), self.text)
        for k in Effektkandidaten.kandidaten():
            self.assertIn(escape(k['name']), self.text)
            self.assertIn(escape(k['urteil']), self.text)
        for _name, adresse in Effektkandidaten.quellen():
            self.assertIn('href="%s"' % escape(adresse), self.text)
        for titel, _text in Animationseffekte.weg():
            self.assertIn(escape(titel), self.text)
        for was, _befund in Animationseffekte.effekte():
            self.assertIn(escape(was), self.text)
        self.assertIn('href="%s"' % reverse('effekte'), self.text)

    def test_die_vorlage_traegt_keine_daten(self):
        for k in Effektkandidaten.kandidaten():
            self.assertNotIn(k['name'], self.vorlage)
        for _name, adresse in Effektkandidaten.quellen():
            self.assertNotIn(adresse, self.vorlage)
        self.assertNotIn(str(Animationseffekte.MIMIK_WERTE), self.vorlage)

    def test_der_stand_bleibt_ehrlich(self):
        u"""„läuft" ohne Einschraenkung darf nur sagen, was im Bestand als
        laufend steht; Blender Cloth bleibt als Nicht-Wahl aufgefuehrt."""
        laufend = {b['was'] for b in Animationseffekte.bestand()
                   if b['stand'].startswith('läuft')}
        for k in Effektkandidaten.kandidaten():
            if k['laeuft'].startswith('ja'):
                self.assertIn('siehe', k['laeuft'], k['name'])
            self.assertTrue(k['lizenz'] and k['urteil'], k['name'])
        self.assertTrue(laufend)
        self.assertTrue(any(was.startswith('Blender Cloth') for was, _ in Animationseffekte.nicht()))
        for _name, adresse in Effektkandidaten.quellen():
            self.assertTrue(adresse.startswith('https://'), adresse)

    def test_verweist_auf_kleiderphysik_und_koerperphysik(self):
        self.assertIn('href="%s"' % reverse('hilfe_kleidung_physik'), self.text)
        self.assertIn('href="%s"' % reverse('hilfe_koerper_physik'), self.text)
        self.assertIn('href="%s"' % reverse('hilfe_video_to_bvh'), self.text)
