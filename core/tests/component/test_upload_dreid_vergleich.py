# -*- coding: utf-8 -*-
u"""/process/VideoToBVH/: der Bereich „Vergleich 3D Pipelines" folgt der Messung.

Auftrag Edgar (12.09.2026): „passe den Bereich Vergleich 3D Pipelines an
aufgrund der empfohlenen Pipelines, nutze auch Hilfe → Video to BVH". Vorher
stand dort eine Handtabelle mit Paperwerten (PA-MPJPE) und „GVHMR ★
Empfohlen" — die Karten darüber waren längst nach der Messung geordnet.
Jetzt kommt die Tabelle aus `Pipelinevergleich.dreid_rangfolge()`.
"""
import re

from django.test import Client, TestCase
from django.urls import reverse

from core.dienste.pipelinevergleich import Pipelinevergleich


class DerVergleich(TestCase):

    ADRESSE = '/process/VideoToBVH/'

    def setUp(self):
        self.client = Client()
        antwort = self.client.get(self.ADRESSE)
        self.assertEqual(antwort.status_code, 200)
        self.text = antwort.content.decode('utf-8')
        start = self.text.index('Vergleich 3D Pipelines')
        self.tabelle = self.text[start:self.text.index('SMPL-Lizenz', start)]

    def test_nur_3d_und_hybrid_mit_rang_in_rangfolge(self):
        eintraege = Pipelinevergleich.dreid_rangfolge()
        self.assertTrue(eintraege)
        self.assertEqual([e['rang'] for e in eintraege], sorted(e['rang'] for e in eintraege))
        self.assertTrue(all(e['art'] in ('3D', 'Hybrid') for e in eintraege))
        self.assertNotIn('mediapipe', [e['schluessel'] for e in eintraege])
        namen = re.findall(r'<td><strong>([^<]+)</strong>', self.tabelle)
        self.assertEqual(namen, [e['name'] for e in eintraege])

    def test_rang_eins_ist_empfohlen_und_die_handtabelle_ist_weg(self):
        erster = Pipelinevergleich.dreid_rangfolge()[0]
        self.assertEqual(erster['rang'], 1)
        self.assertEqual(self.tabelle.count('Empfohlen'), 1)
        zeile = self.tabelle[self.tabelle.index(erster['name']):]
        self.assertLess(zeile.index('Empfohlen'), zeile.index('</tr>'))
        self.assertNotIn('PA-MPJPE', self.text)
        self.assertNotIn('RTX 3060', self.text)

    def test_messung_und_verweis_auf_die_hilfe(self):
        self.assertIn(Pipelinevergleich.MESSUNG['video'], self.tabelle)
        self.assertIn('href="%s"' % reverse('hilfe_video_to_bvh'), self.tabelle)
        for e in Pipelinevergleich.dreid_rangfolge():
            with self.subTest(pipeline=e['kennung']):
                self.assertIn(str(e['dauer_s']), self.tabelle)
