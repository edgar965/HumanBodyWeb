# -*- coding: utf-8 -*-
"""Meshfigurdauerprozess (12.10.2026): ein python-Prozess rechnet mehrere Schritte nacheinander — mit einem Ersatz-Kind, das dasselbe Protokoll spricht wie `_run_meshfigur.py --dauer` (Befehl als JSON-Zeile auf stdin,
Antwort `[fortschritt]`, `[ergebnis]`, `[ende] <schritt>` auf stdout), ohne Torch und GPU.

Geprüft: derselbe Prozess für zwei Schritte; ein Fehler im Kind beendet es und der nächste Schritt startet frisch; ein Abbruch durch den Aufrufer (Anhalten) und Stille beenden den Prozess; `schliessen` lässt das Kind enden und ist
wiederholbar. NICHT gelaufen (Tests nur auf Ansage). Sabotage: `_verwerfen()` im `except BaseException` von `rechnen` streichen macht `test_ein_abbruch_beendet_den_prozess` rot.
"""

import os
import sys
import time
import unittest
from pathlib import Path

from core.dienste.meshfigurdauerprozess import Meshfigurdauerprozess
from core.pipeline_process import PipelineStille

from ..unit._pruefablage import Pruefablage

KIND = '''
import json, os, sys, time
for zeile in sys.stdin:
    zeile = zeile.strip()
    if zeile == "ende":
        sys.exit(0)
    befehl = json.loads(zeile)
    schritt = befehl["schritt"]
    if schritt == "still":
        time.sleep(60)
    print("[fortschritt] 50 halb", flush=True)
    if schritt == "fehler":
        print('[fehler] {"fehler": "kaputt"}', flush=True)
        print("[ende] fehler", flush=True)
        sys.exit(1)
    print("[ergebnis] " + json.dumps({"pid": os.getpid(), "schritt": schritt, "runde": befehl.get("runde")}), flush=True)
    print("[ende] " + schritt, flush=True)
'''


class DauerprozessTest(unittest.TestCase):
    def setUp(self):
        self.dauer = Meshfigurdauerprozess()
        self.addCleanup(self.dauer.schliessen)
        self._ablage = Pruefablage.ordner()
        self.ordner = self._ablage.__enter__()
        self.addCleanup(self._ablage.__exit__, None, None, None)
        self.skript = Path(self.ordner) / 'kind.py'
        self.skript.write_text(KIND, encoding='utf-8')
        self.zeilen = []

    def _rechnen(self, schritt, runde=1, bei_zeile=None, stille_s=30):
        self.zeilen = []
        return self.dauer.rechnen([sys.executable, str(self.skript)], Path(self.ordner) / 'auftrag.json', schritt, runde, {}, self.ordner, bei_zeile or self.zeilen.append, stille_s)

    def _ergebnis_pid(self):
        import json

        zeile = next(z for z in self.zeilen if z.startswith('[ergebnis] '))
        return json.loads(zeile[11:])['pid']

    def test_zwei_schritte_im_selben_prozess(self):
        self._rechnen('koerper', 1)
        erst = self._ergebnis_pid()
        self.assertIn('[fortschritt] 50 halb', self.zeilen)
        self.assertTrue(self.dauer.lebt())
        self._rechnen('gesicht', 2)
        self.assertEqual(self._ergebnis_pid(), erst)
        self.assertEqual(self.dauer.pid, erst)

    def test_ein_fehler_im_kind_beendet_es_und_der_naechste_schritt_startet_frisch(self):
        self._rechnen('koerper')
        erst = self._ergebnis_pid()
        self._rechnen('fehler')
        self.assertIn('[fehler] {"fehler": "kaputt"}', self.zeilen)             # die Zeilen des Fehlers kommen an; das [ende] nicht
        for _ in range(50):
            if not self.dauer.lebt():
                break
            time.sleep(0.1)
        self.assertFalse(self.dauer.lebt())
        self._rechnen('rest')
        self.assertNotEqual(self._ergebnis_pid(), erst)

    def test_ein_abbruch_beendet_den_prozess(self):
        class Angehalten(Exception):
            pass

        def anhalten(zeile):
            raise Angehalten()

        self._rechnen('koerper')
        erst = self._ergebnis_pid()
        with self.assertRaises(Angehalten):
            self._rechnen('gesicht', bei_zeile=anhalten)
        self.assertFalse(self.dauer.lebt())
        self._rechnen('rest')
        self.assertNotEqual(self._ergebnis_pid(), erst)

    def test_stille_beendet_den_prozess(self):
        with self.assertRaises(PipelineStille):
            self._rechnen('still', stille_s=1)
        self.assertFalse(self.dauer.lebt())

    def test_schliessen_laesst_das_kind_enden_und_ist_wiederholbar(self):
        self._rechnen('koerper')
        pid = self.dauer.pid
        self.dauer.schliessen()
        self.assertFalse(self.dauer.lebt())
        self.assertIsNone(self.dauer.pid)
        self.dauer.schliessen()
        if os.name == 'nt':
            import subprocess

            aus = subprocess.run(['tasklist', '/FI', 'PID eq %d' % pid], capture_output=True, text=True, check=False).stdout
            self.assertNotIn(str(pid), aus.split('PID')[-1] if 'PID' in aus else aus)

    def test_ein_totes_kind_ohne_ende_ist_ein_fehler(self):
        tot = Path(self.ordner) / 'tot.py'
        tot.write_text('import sys\nsys.stdin.readline()\nprint("[fortschritt] 1 x", flush=True)\nsys.exit(3)\n', encoding='utf-8')
        with self.assertRaises(RuntimeError):
            self.dauer.rechnen([sys.executable, str(tot)], 'a.json', 'koerper', 1, {}, self.ordner, lambda z: None, 30)
        self.assertFalse(self.dauer.lebt())


if __name__ == '__main__':
    unittest.main()
