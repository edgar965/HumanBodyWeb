# -*- coding: utf-8 -*-
"""`Engine2d3dKleiderrenderlaeufe.loeschen` — Render-Läufe aus der Tabelle der Exportleiste löschen (31.10.2026 nachts, Edgar: „mit Löschen button und batch löschen“), an einer
Kunstablage: Einträge und Dateien der genannten Läufe sind weg, der Rest und fremde Dateien bleiben, unbekannte Nummern werden übergangen.
"""
import json
import shutil
import unittest
from pathlib import Path
from types import SimpleNamespace

from django.conf import settings

from core.dienste.engine2d3dkleiderrenderlaeufe import Engine2d3dKleiderrenderlaeufe

WURZEL = Path(settings.TOOLS_ROOT) / 'ProjektTemp' / '_wegwerf' / 'tests' / 'renderlaeufe_loeschen'


class Renderlaeufeloeschentest(unittest.TestCase):

    def setUp(self):
        shutil.rmtree(WURZEL, ignore_errors=True)
        (WURZEL / 'ergebnis').mkdir(parents=True)
        (WURZEL / 'arbeit').mkdir()
        laeufe = [{'nr': n, 'video': 'render_lauf_%03d.mp4' % n, 'blatt': 'render_lauf_%03d.png' % n} for n in (1, 2, 3)]
        for e in laeufe:
            (WURZEL / 'ergebnis' / e['video']).write_bytes(b'v')
            (WURZEL / 'ergebnis' / e['blatt']).write_bytes(b'b')
        (WURZEL / 'ergebnis' / 'fremd.mp4').write_bytes(b'x')
        (WURZEL / 'arbeit' / 'laeufe.json').write_text(json.dumps(laeufe), encoding='utf-8')
        ablage = SimpleNamespace(ergebnis=lambda name=None: WURZEL / 'ergebnis' / name if name else WURZEL / 'ergebnis')
        self.laeufe = Engine2d3dKleiderrenderlaeufe(SimpleNamespace(_datei=lambda name: WURZEL / 'arbeit' / name, ablage=ablage, job=SimpleNamespace(kennung='test')))

    def tearDown(self):
        shutil.rmtree(WURZEL, ignore_errors=True)

    def test_loescht_eintraege_und_dateien_der_nummern(self):
        self.assertEqual(self.laeufe.loeschen([1, 3, 7]), [1, 3])
        self.assertEqual(sorted(p.name for p in (WURZEL / 'ergebnis').iterdir()), ['fremd.mp4', 'render_lauf_002.mp4', 'render_lauf_002.png'])
        self.assertEqual([e['nr'] for e in self.laeufe.lesen()], [2])


if __name__ == '__main__':
    unittest.main()
