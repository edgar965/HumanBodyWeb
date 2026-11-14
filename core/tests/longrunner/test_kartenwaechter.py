# -*- coding: utf-8 -*-
"""`KoerperKI_alle.Kartenwaechter` (13.11.2026, Edgar: „teste erstmal ob wirklich alles auf torch läuft … mache einen Testcase“) — sieht der Wächter, was er sehen soll, und nichts sonst?

Gegenprobe in jedem Fall: Rechnung nur auf der Karte → kein Fund (0 CPU, 0 Kopien, 0 Wartepunkte, 0 Bibliotheksaufrufe); dann je eine bekannte Sünde → genau diese Art, an der Zeile
dieses Tests:
1. CPU-Tensoren rechnen (`torch.ones(…)` ohne Gerät)           → `cpu`
2. `.cpu()` und `.item()`                                       → `zur_cpu`, `warten`
3. `torch.as_tensor(liste, device='cuda')`                      → `zur_karte`
4. numpy über `tensor.numpy()` und dessen `sum`, PIL `Image.new` → `bibliothek`
5. Danach ist alles zurückgestellt (Dispatch-Stapel leer, Sync-Modus aus, Werkzeugnummer frei).
6. Der Prozesshaken (`kartenwaechter_haken/sitecustomize.py`) schreibt in einem fremden Prozess einen Bericht mit denselben Arten — und ohne `KARTENWAECHTER_ORDNER` keinen.
Braucht die Karte (CUDA-Start > 1 s, darum LongRunner).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import torch
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))

from KoerperKI_alle.kartenwaechter import Kartenwaechter  # noqa: E402

HIER = 'HumanBodyWeb\\core\\tests\\longrunner\\test_kartenwaechter.py'
HAKEN = Path(settings.TOOLS_ROOT) / 'KoerperKI_alle' / 'kartenwaechter_haken'
PROBE = '''import torch
x = torch.arange(1000, device='cuda', dtype=torch.float32)
for _ in range(20):
    x = (x * 1.0001 + 1).sin_()
y = x.cpu()
z = torch.ones(50) * 2  # cpu gewollt: Gegenprobe des Kartenwächters (fremder Prozess)
print(float(y.sum() + z.sum()))
'''


def arten(bericht, art):
    return [s for s in bericht['stellen'] if s['art'] == art]


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Karte')
class KartenwaechterTest(unittest.TestCase):
    def setUp(self):
        self.x = torch.arange(1000, device='cuda', dtype=torch.float32)
        torch.cuda.synchronize()

    def nur_karte(self):
        x = self.x
        for _ in range(50):
            x = (x * 1.0001 + 1).sin_()
        return x

    def test_nur_karte_kein_fund(self):
        with Kartenwaechter() as w:
            self.nur_karte()
        b = w.bericht()
        self.assertGreaterEqual(b['ops']['karte'], 150)
        self.assertEqual({k: v for k, v in b['ops'].items() if k != 'karte'}, dict.fromkeys(('cpu', 'zur_cpu', 'zur_karte', 'gemischt', 'andere'), 0))
        self.assertEqual((b['warten'], b['bibliothek'], b['stellen']), (0, 0, []))

    def test_cpu_rechnung(self):
        with Kartenwaechter() as w:
            self.nur_karte()
            a = torch.ones(300) * 2 + 1  # cpu gewollt: Gegenprobe des Kartenwächters
        b = w.bericht()
        self.assertGreaterEqual(b['ops']['cpu'], 3)
        cpu = arten(b, 'cpu')
        self.assertTrue(cpu and all(HIER in s['stelle'] and 'test_cpu_rechnung' in s['stelle'] for s in cpu), cpu)
        self.assertEqual(sum(s['elemente'] for s in cpu), 900)
        self.assertEqual(float(a[0]), 3.0)

    def test_kopie_zur_cpu_und_warten(self):
        with Kartenwaechter() as w:
            x = self.nur_karte()
            y = x.cpu()
            s = x.sum().item()
        b = w.bericht()
        self.assertEqual(b['ops']['zur_cpu'], 1)
        self.assertGreaterEqual(b['warten'], 2)                       # .cpu() und .item()
        self.assertTrue(all(HIER in s_['stelle'] for s_ in arten(b, 'warten') + arten(b, 'zur_cpu')), b['stellen'])
        self.assertEqual(len(y), 1000)
        self.assertIsInstance(s, float)

    def test_kopie_zur_karte(self):
        with Kartenwaechter() as w:
            t = torch.as_tensor([1.0, 2.0, 3.0], device='cuda')
        b = w.bericht()
        self.assertGreaterEqual(b['ops']['zur_karte'], 1)
        self.assertTrue(all(HIER in s['stelle'] for s in arten(b, 'zur_karte')))
        self.assertEqual(t.device.type, 'cuda')

    def test_bibliotheken(self):
        from PIL import Image
        with Kartenwaechter() as w:
            feld = self.x[:10].cpu().numpy()
            summe = feld.sum()
            bild = Image.new('L', (4, 4))
        b = w.bericht()
        ops = {o for s in arten(b, 'bibliothek') for o in s['ops']}
        self.assertTrue({'torch→python:numpy', 'numpy:sum', 'PIL:new'} <= ops, ops)
        self.assertEqual((float(summe), bild.size), (45.0, (4, 4)))

    def test_aus_stellt_zurueck(self):
        with Kartenwaechter():
            self.nur_karte().sum().item()
        self.assertEqual(torch._C._len_torch_dispatch_stack(), 0)
        self.assertEqual(torch.cuda.get_sync_debug_mode(), 0)
        if hasattr(sys, 'monitoring'):
            self.assertTrue(all(sys.monitoring.get_tool(n) is None for n in Kartenwaechter.WERKZEUG))

    def test_haken_im_fremden_prozess(self):
        wurzel = Path(settings.TOOLS_ROOT) / 'ProjektTemp' / '_wegwerf' / 'kartenwaechter'
        wurzel.mkdir(parents=True, exist_ok=True)
        ordner = Path(tempfile.mkdtemp(prefix='_test_haken_', dir=wurzel))
        try:
            probe = ordner / 'probe.py'
            probe.write_text(PROBE, encoding='utf-8')
            mit, ohne = ordner / 'mit', ordner / 'ohne'
            for bericht in (mit, ohne):
                env = dict(os.environ, PYTHONPATH=str(HAKEN), PYTHONIOENCODING='utf-8')
                env.pop('KARTENWAECHTER_ORDNER', None)
                if bericht is mit:
                    env['KARTENWAECHTER_ORDNER'] = str(mit)
                r = subprocess.run([sys.executable, str(probe)], env=env, capture_output=True, text=True, timeout=120, creationflags=0x08000000)
                self.assertEqual(r.returncode, 0, r.stderr[-2000:])
            self.assertFalse(ohne.exists())
            dateien = list(mit.glob('*.json'))
            self.assertEqual(len(dateien), 1)
            b = json.loads(dateien[0].read_text(encoding='utf-8'))
            self.assertTrue(b['torch'] and b['fehler'] is None, b.get('fehler'))
            self.assertGreaterEqual(b['ops']['karte'], 60)
            self.assertEqual((b['ops']['zur_cpu'], b['ops']['cpu'] >= 2, b['warten'] >= 1), (1, True, True))
            self.assertTrue(all('probe.py' in s['stelle'] for s in b['stellen']), b['stellen'])
        finally:
            shutil.rmtree(ordner, ignore_errors=True)
