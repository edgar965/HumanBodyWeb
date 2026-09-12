# -*- coding: utf-8 -*-
u"""/process/VideoToBVH/: Karten nach Rang, beim Laden alle eingeklappt.

Auftrag Edgar (12.09.2026): „ordne die pipelines nach der Ranking, alle
sollen per default eingeklappt sein (GVHMR ist im Moment aufgeklappt)".
Vorher klappte die Wahl einer Pipeline ihren Block auf, und beim Laden war
die zuletzt gewaehlte Karte offen. Jetzt gehoert zu jeder Karte ein Knopf,
der genau ihren Block steuert; eine Pipeline bleibt gewaehlt, aber zu.
"""
import re

from django.test import Client, TestCase

from core.dienste.pipelinekarten import Pipelinekarten


class DieSeite(TestCase):

    ADRESSE = '/process/VideoToBVH/'
    KARTE = re.compile(r'class="pipeline-card[^"]*"[^>]*data-pipeline="(\w+)"')
    RADIO = re.compile(r'<input type="radio" name="pipeline"[^>]*>')
    KNOPF = re.compile(r'<button[^>]*class="pipeline-card-klappe"[^>]*>')
    ABZEICHEN = re.compile(r'class="pipeline-card-rang[^"]*"[^>]*>([^<]*)<')

    def setUp(self):
        self.client = Client()
        antwort = self.client.get(self.ADRESSE)
        self.assertEqual(antwort.status_code, 200)
        self.text = antwort.content.decode('utf-8')

    def test_die_karten_stehen_in_der_folge_des_rangs(self):
        self.assertEqual(self.KARTE.findall(self.text),
                         Pipelinekarten.reihenfolge())

    def test_beim_laden_ist_keine_karte_aufgeklappt(self):
        self.assertNotIn('pipeline-settings visible', self.text)
        self.assertNotIn('aria-expanded="true"', self.text)
        self.assertEqual(self.text.count('aria-expanded="false"'),
                         len(Pipelinekarten.reihenfolge()))

    def test_jede_karte_hat_einen_knopf_auf_ihren_eigenen_block(self):
        knoepfe = self.KNOPF.findall(self.text)
        self.assertEqual(len(knoepfe), len(Pipelinekarten.reihenfolge()))
        for karte in Pipelinekarten.reihenfolge():
            with self.subTest(karte=karte):
                self.assertIn('id="settings-%s"' % karte, self.text)
                self.assertTrue(any('aria-controls="settings-%s"' % karte in k
                                    for k in knoepfe))

    def test_der_knopf_steht_neben_der_wahl_nicht_im_label(self):
        u"""Ein Knopf IM <label> waehlte beim Klick die Pipeline mit."""
        for knopf in self.KNOPF.finditer(self.text):
            davor = self.text[:knopf.start()]
            self.assertGreater(davor.rfind('</label>'),
                               davor.rfind('<label class="pipeline-card-wahl">'))

    def test_genau_eine_pipeline_ist_gewaehlt(self):
        radios = self.RADIO.findall(self.text)
        self.assertEqual(len(radios), len(Pipelinekarten.reihenfolge()))
        self.assertEqual(sum('checked' in r for r in radios), 1)

    def test_jede_karte_traegt_ihr_rang_abzeichen_vor_dem_titel(self):
        u"""Edgar (12.09.2026): „mach das Rang abzeichen" — der Rang wie auf
        der Hilfeseite, ohne Rang ein Strich, in der Wahl vor dem Titel."""
        erwartet = [str(e['rang']) if e['rang'] else '&ndash;'
                    for e in Pipelinekarten.eintraege()]
        self.assertEqual([t.strip() for t in self.ABZEICHEN.findall(self.text)],
                         erwartet)
        self.assertIn('von %d im Vergleich' % Pipelinekarten.rang_von(), self.text)
        for titel in re.finditer('class="pipeline-card-title"', self.text):
            davor = self.text[:titel.start()]
            self.assertGreater(davor.rfind('class="pipeline-card-rang'),
                               davor.rfind('<label class="pipeline-card-wahl">'))
