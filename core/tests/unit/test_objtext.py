# -*- coding: utf-8 -*-
"""`KoerperKI_alle.objtext.Objtext` — EIN Schreiber für OBJ-Zeilen (25.11.2026, Edgar: „immer gemeinsamer Code!“).

1. Dieselben Zeilen wie die alte Schreibweise (je Zahl aus dem Feld): Tensoren auf der Karte, Listen, Listen von Zeilentensoren, Vierecke, verschobene Nummern, UV je Ecke.
2. Jeder Schreiber im Projekt benutzt ihn — keine eigene `v %.6f`-Schleife über ein Feld mehr.

Sabotage-Gegenprobe: `ab=0` gibt andere Flächenzeilen (als Probe gefahren, `_wegwerf/ladezeit_charakter/objtext_gleich.py`); eine wieder eingebaute Schleife macht Fall 2 rot (nicht gefahren).
Geschrieben, nicht gelaufen (nur auf Ansage).
"""
import re
import unittest
from pathlib import Path

import torch
from django.conf import settings
from django.test import SimpleTestCase
from KoerperKI_alle.objtext import Objtext

WURZEL = Path(settings.BASE_DIR).parent
#: Wer eigene Zeilen schreiben darf: nur der Baustein selbst (die Simulationsausgabe schreibt vollen float32-Text, kein `%.6f`).
FREI = {'KoerperKI_alle/objtext.py'}


class ObjtextTest(SimpleTestCase):
    databases = set()

    @unittest.skipUnless(torch.cuda.is_available(), 'braucht die Grafikkarte')
    def test_1_wie_die_alte_schreibweise(self):
        g = torch.Generator(device='cuda').manual_seed(4)
        punkte = (torch.rand((40, 3), device='cuda', generator=g, dtype=torch.float64) - 0.5) * 3
        uv = torch.rand((30, 2), device='cuda', generator=g, dtype=torch.float32)
        dreiecke = torch.randint(0, 40, (10, 3), device='cuda', generator=g)
        soll_v = ['v %.6f %.6f %.6f' % (p[0], p[1], p[2]) for p in punkte]
        for form in (punkte, punkte.tolist(), list(punkte)):
            self.assertEqual(Objtext.v(form), soll_v)
        self.assertEqual(Objtext.vt(uv), ['vt %.6f %.6f' % (t[0], t[1]) for t in uv])
        self.assertEqual(Objtext.f(dreiecke), ['f %d %d %d' % (d[0] + 1, d[1] + 1, d[2] + 1) for d in dreiecke])
        self.assertEqual(Objtext.f(dreiecke, ab=78), ['f %d %d %d' % (d[0] + 78, d[1] + 78, d[2] + 78) for d in dreiecke])
        self.assertEqual(Objtext.f([[0, 1, 2], [3, 4, 5, 6]]), ['f 1 2 3', 'f 4 5 6 7'])
        self.assertEqual(Objtext.f_ecken(dreiecke), ['f %d/%d %d/%d %d/%d' % (a + 1, 3 * i + 1, b + 1, 3 * i + 2, c + 1, 3 * i + 3) for i, (a, b, c) in enumerate(dreiecke)])
        self.assertNotEqual(Objtext.f(dreiecke, ab=0), Objtext.f(dreiecke))

    def test_2_kein_zweiter_schreiber(self):
        muster = re.compile(r"'v %\.6f|\"v %\.6f|'v %\.\*f")
        eigene = []
        for ordner in ('Assets/GarmentCode', 'Genesis9', 'KoerperKI_alle', 'meshgenesis', 'SMPL', 'HumanBodyWeb/core'):
            for datei in (WURZEL / ordner).rglob('*.py'):
                name = datei.relative_to(WURZEL).as_posix()
                if name in FREI or '/tests/' in name or '/upstream/' in name or '/_wegwerf' in name:
                    continue
                if muster.search(datei.read_text(encoding='utf-8', errors='replace')):
                    eigene.append(name)
        self.assertEqual(eigene, [], 'schreibt OBJ-Punkte selbst statt über Objtext')
