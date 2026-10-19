# -*- coding: utf-8 -*-
u"""Die Bilder einer Genesis-Figur darf der Browser behalten (19.10.2026): `G9texturbuendelapi` per GET mit ETag, `G9garderobeapi.textur` über `Auftragsdatei`.

Gemessen an Mann1 (Mesh3D-AI): jedes Laden übertrug alle Bilder neu (das Bündel war ein POST, das Einzelbild `no-store`) — ein Bündel mit 48,6 MB in 5,2 s. Danach kam
dasselbe Bündel als 304 aus dem Speicher des Browsers (0,2–0,9 s).

1. Bündel per GET: 200, Inhalt wie per POST, ETag und `no-cache`; mit derselben Marke in `If-None-Match` 304 ohne Inhalt; ändert sich ein Bild (Größe/Zeit), ändert sich die Marke.
2. POST (ältere Tabs) wie bisher: kein ETag.
3. Einzelbild: Art aus `G9material.bildart`, ETag, 304 auf die eigene Marke.

Sabotage (von Hand, nicht als Lauf): in `G9texturbuendelapi.marke` die Änderungszeit weglassen → Fall 1 rot („neue Marke"); in `Auftragsdatei.antwort` `art` übergehen → Fall 3 rot.
Geschrieben am 19.10.2026.
"""
import json
import os
import time
import unittest
from pathlib import Path
from unittest import mock

from asgiref.sync import async_to_sync
from django.test import RequestFactory

from core.api.g9garderobe import G9garderobeapi
from core.api.g9texturbuendel import G9texturbuendelapi

from ._pruefablage import Pruefablage


class G9texturcacheTest(unittest.TestCase):

    def _welt(self, wurzel):
        dateien = {}
        for name, inhalt in (('a.jpg', b'\xff\xd8 eins'), ('b.png', b'\x89PNG zwei')):
            pfad = Path(wurzel) / name
            pfad.write_bytes(inhalt)
            dateien[name] = pfad
        art = {'a.jpg': 'image/jpeg', 'b.png': 'image/png'}
        return (mock.patch('core.api.g9texturbuendel.G9material.datei', side_effect=lambda p: dateien.get(p)),
                mock.patch('core.api.g9texturbuendel.G9material.bildart', side_effect=lambda p: art.get(p)),
                mock.patch('core.api.g9garderobe.G9material.datei', side_effect=lambda p: dateien.get(p)),
                mock.patch('core.api.g9garderobe.G9material.bildart', side_effect=lambda p: art.get(p)), dateien)

    @staticmethod
    def _inhalt(antwort):
        return b''.join(antwort.streaming_content) if getattr(antwort, 'streaming', False) else antwort.content

    def test_1_buendel_per_get_mit_marke(self):
        with Pruefablage.ordner('texturcache_') as wurzel:
            *flicken, dateien = self._welt(wurzel)
            with flicken[0], flicken[1]:
                f = RequestFactory()
                eins = async_to_sync(G9texturbuendelapi.buendel)(f.get('/b/', {'p': ['a.jpg', 'b.png']}))
                self.assertEqual(eins.status_code, 200)
                self.assertIn('no-cache', eins['Cache-Control'])
                marke = eins['ETag']
                post = async_to_sync(G9texturbuendelapi.buendel)(f.post('/b/', json.dumps({'pfade': ['a.jpg', 'b.png']}), content_type='application/json'))
                self.assertEqual(eins.content, post.content)
                self.assertFalse(post.has_header('ETag'))
                zwei = async_to_sync(G9texturbuendelapi.buendel)(f.get('/b/', {'p': ['a.jpg', 'b.png']}, HTTP_IF_NONE_MATCH=marke))
                self.assertEqual((zwei.status_code, zwei.content), (304, b''))
                dateien['a.jpg'].write_bytes(b'\xff\xd8 eins, neu')
                os.utime(dateien['a.jpg'], (time.time() + 5, time.time() + 5))
                drei = async_to_sync(G9texturbuendelapi.buendel)(f.get('/b/', {'p': ['a.jpg', 'b.png']}, HTTP_IF_NONE_MATCH=marke))
                self.assertEqual(drei.status_code, 200)
                self.assertNotEqual(drei['ETag'], marke, 'neue Marke')

    def test_3_einzelbild_mit_art_und_marke(self):
        with Pruefablage.ordner('texturcache_') as wurzel:
            *flicken, _dateien = self._welt(wurzel)
            with flicken[2], flicken[3]:
                f = RequestFactory()
                eins = G9garderobeapi.textur(f.get('/t/b.png'), 'b.png')
                self.assertEqual((eins.status_code, eins['Content-Type']), (200, 'image/png'))
                self.assertEqual(self._inhalt(eins), b'\x89PNG zwei')
                eins.close()                                    # die Datei freigeben (Windows: sonst bleibt der Prüfordner liegen)
                zwei = G9garderobeapi.textur(f.get('/t/b.png', HTTP_IF_NONE_MATCH=eins['ETag']), 'b.png')
                self.assertEqual(zwei.status_code, 304)
                self.assertEqual(G9garderobeapi.textur(f.get('/t/x.png'), 'x.png').status_code, 404)
