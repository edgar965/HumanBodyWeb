# -*- coding: utf-8 -*-
"""Warteschlange im Reiter „Lauf Aktuell“ auf /mesh-3D-AI/ (18.10.2026): `Mesh3daiwarteschlange` liest Ketten und Schritte aus `ProjektTemp/mia_daten/warteschlange.json` und den Logs.
Ohne Datenbank und ohne Prozesse (die Ketten-Prozesse kommen als Liste wie aus `Mesh3dailaufprozesse`), Dateien in `Pruefablage`.

Sabotage-Gegenprobe (von Hand): in `_kette` die Suche ab `pos` durch 0 ersetzen → Fall 2 rot (die Marke „== a 1 “ des zweiten Werts träfe nicht mehr hinter dem ersten);
in `_zustand` den Zweig „übersprungen“ streichen → Fall 2 rot; `lebt` immer wahr → Fall 3 rot; in `_fortschritt` `reversed` streichen → Fall 4 rot (Phase B statt C);
in `_zeit` den Rückschritt um einen Tag streichen → Fall 5 rot; in `_kette` die Altersgrenze streichen → Fall 6 rot.
"""

import json
import os
from datetime import datetime
from pathlib import Path

from django.test import SimpleTestCase, override_settings

from core.dienste.mesh3daiwarteschlange import Mesh3daiwarteschlange as W

from ._pruefablage import Pruefablage

JETZT = 1_800_000_000.0


class WarteschlangeTest(SimpleTestCase):
    def _ablage(self, o, ketten, logs, alter=None):
        ordner = Path(o) / 'ProjektTemp' / 'mia_daten'
        ordner.mkdir(parents=True, exist_ok=True)
        (ordner / 'warteschlange.json').write_text(json.dumps({'ketten': ketten}, ensure_ascii=False), encoding='utf-8')
        for name, zeilen in logs.items():
            datei = ordner / name
            datei.write_text('\n'.join(zeilen) + '\n', encoding='utf-8')
            zeit = JETZT - (alter or {}).get(name, 0)
            os.utime(datei, (zeit, zeit))
        return override_settings(TOOLS_ROOT=Path(o))

    @staticmethod
    def _prozess(name, pid=1):
        return {'name': name, 'pid': pid, 'start': JETZT - 600, 'fuehrt_aus': False, 'doppelt': False}

    def test_1_fertig_laeuft_wartet_und_nummern(self):
        ketten = [
            {'skript': 'a.sh', 'titel': 'A', 'log': 'a.log', 'ende': 'A FERTIG', 'schritte': [{'marke': '== 1 ', 'titel': 'eins'}]},
            {'skript': 'b.sh', 'titel': 'B', 'log': 'b.log', 'ende': 'B FERTIG', 'wartet_auf': {'log': 'a.log', 'marke': 'A FERTIG'},
             'schritte': [{'marke': '== 2 ', 'titel': 'zwei'}, {'marke': '== 3 ', 'titel': 'drei'}]},
            {'skript': 'c.sh', 'titel': 'C', 'log': 'c.log', 'ende': 'C FERTIG', 'wartet_auf': {'log': 'b.log', 'marke': 'B FERTIG'},
             'schritte': [{'marke': '== 4 ', 'titel': 'vier'}]}]
        logs = {'a.log': ['== 1 los 10:00:00', 'A FERTIG 10:30:00'], 'b.log': ['== 2 los 10:31:00', 'Zeile'], 'c.log': []}
        with Pruefablage.ordner('warteschlange_') as o, self._ablage(o, ketten, logs):
            w = W.lesen([self._prozess('b.sh'), self._prozess('c.sh', 2)], [], JETZT)
        self.assertIsNone(w['fehler'])
        a, b, c = w['ketten']
        self.assertEqual((a['zustand'], b['zustand'], c['zustand']), ('fertig', 'läuft', 'wartet'))
        self.assertEqual([s['zustand'] for s in a['schritte'] + b['schritte'] + c['schritte']], ['fertig', 'läuft', 'wartet', 'wartet'])
        self.assertEqual([s['nr'] for s in a['schritte'] + b['schritte'] + c['schritte']], [1, 2, 3, 4])
        self.assertEqual(a['schritte'][0]['dauer_s'], 1800)
        self.assertEqual(c['wartet_auf'], {'titel': 'B', 'marke': 'B FERTIG', 'erreicht': False})
        self.assertTrue(b['wartet_auf']['erreicht'])

    def test_2_je_wert_aus_dem_log_und_uebersprungen(self):
        ketten = [{'skript': 'p.sh', 'titel': 'P', 'log': 'p.log', 'ende': 'P FERTIG', 'je': {'werte': ['x', 'y', 'z'], 'zeile': r'^== Paare (\S+)'},
                   'schritte': [{'marke': '== {je} 1 ', 'titel': '{je} eins'}, {'marke': '== {je} 2 ', 'titel': '{je} zwei'}]}]
        logs = {'p.log': ['== Paare a,b 09:00:00', '== a 2 los 09:01:00', '== b 1 los 09:05:00', '== b 2 übersprungen 09:06:00', 'P FERTIG 09:07:00']}
        with Pruefablage.ordner('warteschlange_') as o, self._ablage(o, ketten, logs):
            w = W.lesen([], [], JETZT)
        schritte = w['ketten'][0]['schritte']
        self.assertEqual([s['titel'] for s in schritte], ['a eins', 'a zwei', 'b eins', 'b zwei'])
        self.assertEqual([s['zustand'] for s in schritte], ['übersprungen', 'fertig', 'fertig', 'übersprungen'])

    def test_3_abgebrochen_ohne_prozess(self):
        ketten = [{'skript': 'b.sh', 'log': 'b.log', 'ende': 'B FERTIG', 'schritte': [{'marke': '== 2 '}, {'marke': '== 3 '}]}]
        with Pruefablage.ordner('warteschlange_') as o, self._ablage(o, ketten, {'b.log': ['== 2 los 10:31:00']}):
            w = W.lesen([], [], JETZT)
        k = w['ketten'][0]
        self.assertEqual(k['zustand'], 'abgebrochen')
        self.assertEqual([s['zustand'] for s in k['schritte']], ['abgebrochen', 'wartet'])

    def test_4_fortschritt_vom_job_sonst_gezaehlt(self):
        ketten = [{'skript': 'b.sh', 'log': 'b.log', 'schritte': [{'marke': '== 2 ', 'prozess': 'daten_lauf'}]},
                  {'skript': 'k.sh', 'log': 'k.log', 'schritte': [{'marke': '== 3 ', 'prozess': 'nicht_da', 'zaehlen': r'\bganz\s+\d', 'einheit': 'Figuren'}]}]
        logs = {'b.log': ['== 2 los 10:31:00', '== B MIA', 'Block 1'], 'k.log': ['== 3 los 10:40:00', 'F1 ganz 12.0', 'F2 ganz 13.5', 'Mittel']}
        balken = [{'name': 'MIA', 'fertig': 10, 'gesamt': 12}, {'name': 'Wolken', 'fertig': 4, 'gesamt': 12}, {'name': 'leer', 'fertig': 0, 'gesamt': 12}]
        job = {'skript': 'starter.py', 'argumente': ['daten_lauf.py', '--k', '1'], 'pid': 77, 'fortschritt': balken, 'lauf': None}
        with Pruefablage.ordner('warteschlange_') as o, self._ablage(o, ketten, logs):
            w = W.lesen([self._prozess('b.sh'), self._prozess('k.sh', 2)], [job], JETZT)
        b, k = (x['schritte'][0] for x in w['ketten'])
        self.assertEqual((b['fortschritt']['name'], b['job'], b['abschnitt'], b['letzte_zeile']), ('Wolken', 77, '== B MIA', 'Block 1'))
        self.assertEqual((k['fortschritt']['fertig'], k['fortschritt']['text'], k['job']), (2, '2 Figuren', None))

    def test_5_zeit_nach_dem_log_gehoert_zum_vortag(self):
        ketten = [{'skript': 'a.sh', 'log': 'a.log', 'ende': 'A FERTIG', 'schritte': [{'marke': '== 1 '}]}]
        with Pruefablage.ordner('warteschlange_') as o:
            zeilen = ['== 1 los 23:50:00', 'A FERTIG 00:10:00']
            with self._ablage(o, ketten, {'a.log': zeilen}):
                datei = Path(o) / 'ProjektTemp' / 'mia_daten' / 'a.log'
                kurz_nach = datetime(2026, 10, 19, 0, 15).timestamp()
                os.utime(datei, (kurz_nach, kurz_nach))
                w = W.lesen([], [], kurz_nach)
        s = w['ketten'][0]['schritte'][0]
        self.assertEqual(s['start'], datetime(2026, 10, 18, 23, 50).timestamp())
        self.assertEqual(s['dauer_s'], 1200)

    def test_6_alte_kette_faellt_weg_unbeschriebene_bleibt(self):
        ketten = [{'skript': 'a.sh', 'teilskripte': ['a_teil.sh'], 'log': 'a.log', 'ende': 'A FERTIG', 'schritte': [{'marke': '== 1 '}]},
                  {'skript': 'b.sh', 'log': 'b.log', 'ende': 'B FERTIG', 'schritte': [{'marke': '== 2 '}]}]
        logs = {'a.log': ['== 1 los 10:00:00', 'A FERTIG 10:30:00'], 'b.log': ['== 2 los 10:00:00', 'B FERTIG 10:30:00']}
        with Pruefablage.ordner('warteschlange_') as o, self._ablage(o, ketten, logs, alter={'a.log': 2 * 86400}):
            w = W.lesen([self._prozess('a_teil.sh'), self._prozess('fremd.sh', 3)], [], JETZT)
        self.assertEqual([k['skript'] for k in w['ketten']], ['b.sh'])
        self.assertEqual([k['name'] for k in w['unbeschrieben']], ['fremd.sh'])

    def test_7_ohne_datei_ein_fehler_kein_absturz(self):
        with Pruefablage.ordner('warteschlange_') as o, override_settings(TOOLS_ROOT=Path(o)):
            w = W.lesen([self._prozess('x.sh')], [], JETZT)
        self.assertEqual((w['ketten'], w['unbeschrieben']), ([], []))
        self.assertIn('fehlt', w['fehler'])
