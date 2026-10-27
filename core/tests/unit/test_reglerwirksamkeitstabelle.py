# -*- coding: utf-8 -*-
"""Reglerwirksamkeitstabelle: liest die jüngste Ablage, baut die djangoBase-Struktur, sagt, wenn keine da ist (27.10.2026)."""
import json
import os
from pathlib import Path

from django.test import SimpleTestCase

from core.dienste.reglerwirksamkeitstabelle import Reglerwirksamkeitstabelle

from ._pruefablage import Pruefablage


def _regler(name, wirkung, nutzen_netz=True, nutzen_foto=True, doppelt=None):
    z = {'name': name, 'anzeige': name.title(), 'bereich': 'Kopf', 'familie': 'Daz', 'art': 'daz', 'lo': -1.0, 'hi': 1.0, 'ende': 1.0, 'wirkung_mm': wirkung,
         'koerper_mm': wirkung, 'kopf_mm': wirkung, 'gelenke_mm': 0.0, 'netz_mm': wirkung, 'umriss_mm': wirkung, 'gesicht_mm': 0.0, 'in_pruefformen': 1,
         'vorhergesagt': 2, 'gedreht': False, 'mesh3dai': {'nutzen': nutzen_netz, 'grund': 'netz'}, 'ai2d3d': {'nutzen': nutzen_foto, 'grund': 'foto'}}
    if doppelt:
        z['doppelt'] = {'zu': doppelt, 'anzeige': doppelt.title(), 'rest_mm': 0.2, 'wert': 0.5}
    return z


class ReglerwirksamkeitstabelleTest(SimpleTestCase):
    def setUp(self):
        self._ablageblock = Pruefablage.ordner()
        self.ordner = Path(self._ablageblock.__enter__())

    def tearDown(self):
        self._ablageblock.__exit__(None, None, None)

    def _ablage(self, raum, regler, zeit):
        datei = self.ordner / ('regler_wirksamkeit_v8_%s.json' % raum)
        datei.write_text(json.dumps({'fassung': 8, 'raum': raum, 'erzeugt': '27.10.2026 00:00', 'lauf': 'lauf', 'pruefformen': 22,
                                     'schwellen': {'stumm_mm': 1.0, 'netz_mm': 1.0, 'foto_mm': 2.0, 'doppelt_mm': 1.0}, 'regler': regler}), encoding='utf-8')
        os.utime(datei, (zeit, zeit))

    def test_ohne_ablage_leer_mit_befehl(self):
        t = Reglerwirksamkeitstabelle(self.ordner)
        self.assertIsNone(t.kopf())
        self.assertEqual(t.tabelle()['zeilen'], [])
        self.assertIn('mesh3dai_reglerwirksamkeit.py', t.tabelle()['leer'])

    def test_vier_spalten_und_empfehlung(self):
        self._ablage('aaaa', [_regler('nase', 12.5), _regler('zahn', 0.0, False, False), _regler('ohr', 3.0, False, False, doppelt='nase')], 1000)
        t = Reglerwirksamkeitstabelle(self.ordner)
        tab = t.tabelle()
        self.assertEqual([s['label'] for s in tab['spalten']], ['Regler', 'Wirksamkeit', 'Mesh3D-AI', '2d-3d-AI'])
        self.assertEqual(len(tab['zeilen']), 3)
        self.assertEqual(tab['zeilen'][0]['html'].count('<td'), 4)
        self.assertIn('12,5 mm', tab['zeilen'][0]['html'])
        self.assertIn('data-sort="1250"', tab['zeilen'][0]['html'])          # ganze Zahl: die djangoBase-Sortierung liest „12.5“ deutsch als 125
        self.assertIn('weglassen', tab['zeilen'][1]['html'])
        self.assertIn('doppelt zu Nase', tab['zeilen'][2]['html'])
        k = t.kopf()
        self.assertEqual((k['ohne_wirkung'], k['doppelt'], k['mesh3dai'], k['ai2d3d']), (1, 1, 1, 1))

    def test_juengste_ablage_und_andere_genannt(self):
        self._ablage('alt', [_regler('a', 5.0)], 1000)
        self._ablage('neu', [_regler('a', 5.0), _regler('b', 6.0)], 2000)
        t = Reglerwirksamkeitstabelle(self.ordner)
        self.assertEqual(t.kopf()['datei'], 'regler_wirksamkeit_v8_neu.json')
        self.assertEqual(t.kopf()['andere'], ['regler_wirksamkeit_v8_alt.json'])
        self.assertEqual(len(t.tabelle()['zeilen']), 2)
