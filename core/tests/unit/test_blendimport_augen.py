# -*- coding: utf-8 -*-
"""Blender-Import: die Originalaugen als eigenes Objekt (Edgar, 08.10.2026) — die Teile ohne Blender, ohne GPU, ohne Genesis-Bau.

Edgar zu „cute girl": „die augen hast du nicht importiert (als extra objekt)". Bis dahin ging nur die Iris auf die Genesis-Augen.
Jetzt wird aus `L_eyes` und `R_eyes` ein Stück „<Figur> Augen" (starr am Kopf, unter Zubehör); solange es sitzt, blendet der Browser
die Genesis-Augen aus (`G9stueckersatz` → `ersetzt` in der Netzantwort → `genesis9ersatz.js`).

1. Beide Augennetze werden zu EINEM zusammengelegt: Punkte hintereinander, die Dreiecksnummern des zweiten um die Punktzahl des ersten
   verschoben, UV unverändert hinterher.
2. Eine Rolle `auge` wird nur gebaut, wenn die Einstellung `objekt` lautet; die anderen Werte lassen die Augen aus dem Stück-Lauf.
3. Das Augenbild der .blend (`Eye_BaseColor.tga`) geht als PNG ins Stück — der Browser liest kein TGA; PNG und JPG bleiben unberührt.
4. Das Stück schreibt `<name>.ersetzt.json` (`{"ersetzt": ["augen"]}`); `G9stueckersatz.von` liest sie, kennt nur erlaubte Namen
   und liefert bei kaputter oder fehlender Datei `[]`.

Sabotage-Gegenprobe: im Zusammenlegen den Versatz `+ int(a)` streichen → Fall 1 rot; `self.augen_objekt and` aus `bauen` nehmen →
Fall 2 rot; in `browserbild` die Prüfung auf `BROWSER_FORMATE` streichen → Fall 3 (PNG bleibt) rot; in `schreiben` die Prüfung
auf `ERLAUBT` streichen → Fall 4 rot.

Nicht gelaufen (Stand 08.10.2026) — läuft nur auf Ansage.
"""

import json
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import numpy as np
from django.test import SimpleTestCase
from Genesis9.stueckersatz import G9stueckersatz

from core.dienste.blendimportstuecke import Blendimportstuecke

from ._pruefablage import Pruefablage


class AugenstueckTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        gebaut = Pruefablage.ordner('augen_')
        self.ordner = Path(gebaut.__enter__())
        self.addCleanup(gebaut.__exit__, None, None, None)
        for name, punkte in (('03.npz', 4), ('04.npz', 5)):
            np.savez(self.ordner / name, punkte=np.arange(punkte * 3, dtype=float).reshape(punkte, 3),
                     dreiecke=np.array([[0, 1, 2], [1, 2, 3]]), uv_ecken=np.full((6, 2), float(punkte)))
        self.inventar = {'netze': [{'name': 'L_eyes', 'datei': '03.npz', 'materialien': [{'name': 'eyes'}]},
                                   {'name': 'R_eyes', 'datei': '04.npz', 'materialien': [{'name': 'eyes'}]}]}
        self.ablage = SimpleNamespace(export=lambda name='': self.ordner / name, kennung='2026.10.08.00.00.00')
        self.rollen = [{'name': 'L_eyes', 'rolle': 'auge'}, {'name': 'R_eyes', 'rolle': 'auge'},
                       {'name': 'body', 'rolle': 'koerper'}]
        # Die Lage liest beim Anlegen die Scan-Lage des Auftrags „Mesh to 3D" — hier nicht gebraucht.
        lage = mock.patch('core.dienste.blendimportstuecke.Blendimportlage', return_value=SimpleNamespace())
        lage.start()
        self.addCleanup(lage.stop)

    def _stuecke(self, augen):
        job = SimpleNamespace(kennung='2026.10.08.00.00.00', stellung=lambda: {})
        return Blendimportstuecke(self.ablage, job, self.inventar, self.rollen, 'cute girl', None, augen)

    def test_1_beide_augen_werden_zu_einem_netz(self):
        netz = self._stuecke('objekt')._netz({'name': 'L_eyes', 'namen': ['L_eyes', 'R_eyes'], 'rolle': 'auge'})
        self.assertEqual(len(netz['punkte']), 9)
        self.assertEqual(netz['dreiecke'].tolist(), [[0, 1, 2], [1, 2, 3], [4, 5, 6], [5, 6, 7]])
        self.assertEqual(netz['uv_ecken'].shape, (12, 2))
        eines = self._stuecke('objekt')._netz({'name': 'L_eyes'})
        self.assertEqual(len(eines['punkte']), 4, 'eine Rolle ohne `namen` bleibt, wie sie ist')

    def test_2_die_augenrolle_kommt_nur_bei_der_einstellung_objekt_in_den_lauf(self):
        gebaut = []

        def stueck(selbst, rolle):
            gebaut.append(rolle['rolle'])
            return 'kennung', {}

        with mock.patch.object(Blendimportstuecke, 'stueck', stueck):
            self._stuecke('objekt').bauen()
            mit = list(gebaut)
            gebaut.clear()
            self._stuecke('original').bauen()
            self._stuecke('genesis').bauen()
        self.assertEqual(mit, ['auge'], 'ein Augenstück für beide Augen')
        self.assertEqual(gebaut, [], 'ohne `objekt` keine Augen im Stück-Lauf')

    def test_3_das_tga_wird_png_und_png_bleibt(self):
        from PIL import Image
        tga = self.ordner / 'Eye_BaseColor.tga'
        Image.new('RGB', (8, 8), (10, 120, 30)).save(tga)
        png = self.ordner / 'schon.png'
        Image.new('RGB', (8, 8)).save(png)
        ziel = self.ordner / 'k_farbe.png'
        self.assertEqual(Blendimportstuecke.browserbild(str(png), ziel), str(png), 'PNG geht unverändert durch')
        self.assertFalse(ziel.exists())
        aus = Blendimportstuecke.browserbild(str(tga), ziel)
        self.assertEqual(aus, str(ziel))
        with Image.open(aus) as bild:
            self.assertEqual((bild.format, bild.size, bild.getpixel((0, 0))), ('PNG', (8, 8), (10, 120, 30)))

    def test_4_die_ersatzdatei_ist_klein_und_streng(self):
        duf = self.ordner / 'cute girl Augen.duf'
        duf.write_text('{}', encoding='utf-8')
        pfad = G9stueckersatz.schreiben(duf, ['augen'])
        self.assertEqual(pfad.name, 'cute girl Augen.ersetzt.json')
        self.assertEqual(json.loads(pfad.read_text(encoding='utf-8')), {'ersetzt': ['augen']})
        self.assertEqual(G9stueckersatz.von(duf), ['augen'])
        with self.assertRaises(ValueError):
            G9stueckersatz.schreiben(duf, ['haut'])
        pfad.write_text('{kaputt', encoding='utf-8')
        self.assertEqual(G9stueckersatz.von(duf), [], 'kaputte Datei: nichts ersetzt')
        pfad.write_text(json.dumps({'ersetzt': ['augen', 'haut', 7]}), encoding='utf-8')
        self.assertEqual(G9stueckersatz.von(duf), ['augen'], 'unbekannte Namen fallen weg')
        self.assertEqual(G9stueckersatz.von(self.ordner / 'gibt es nicht.duf'), [])
        self.assertEqual(G9stueckersatz.fuer({}), [], 'Eintrag ohne Dateiangabe: nichts ersetzt')
