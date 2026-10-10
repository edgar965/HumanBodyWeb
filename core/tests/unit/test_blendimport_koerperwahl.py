# -*- coding: utf-8 -*-
u"""Blender-Import: Körper-Wahl ohne Gewichte nach Hautmaterial, Beinergänzung nur aus schmalen Netzen (10.10.2026, seori).

Edgar: „auch seori kaputt". Mit richtigem Maßstab (`test_blendimport_gesamthoehe.py`) scheiterte „Mesh to 3D" in der Erkennung („index 11 is out of
bounds for axis 0 with size 0"): seori hat den Körper in ZWEI Netzen — `head` (Material „body": Kopf, Schultern, Arme; z 0,74–1,66 m der 1,74 m) und
`head.002` (Material „sock": die Beine, z 0–1,28 m). Ohne Gewichte galt „das höchste Netz" als Körper, also die Beine ohne Kopf.

1. Ein Netz mit Hautmaterial, das mindestens 40 % der Figur hoch ist, geht vor dem höchsten (seori: `head`).
2. Ohne Hautmaterial bleibt es beim höchsten Netz (die Asian girl); `bodysuit` und ähnliche Wörter zählen nicht als Haut.
3. Die Körperergänzung nimmt unter der Körperkante nur Netze, deren Teil dort höchstens 1,25 × so breit ist wie der Körper (Beine 0,99–1,08 gemessen,
   Mantel 1,44 und 3,33), und lässt den Mantel aus.
4. Eine Ergänzung aus schmalen Netzen bleibt, wie sie war (Gegenprobe zu 3).

Sabotage: in `Blendimportrollen.koerper` den Zweig `if haut:` streichen -> Fall 1 rot; `HAUT_MATERIAL` ohne Wortgrenzen -> Fall 2 rot; `MAX_BREITE` auf 100 -> Fall 3 rot.

Nicht gelaufen (Stand 10.10.2026) — läuft nur auf Ansage. Gegenprobe an echten Daten: `ProjektTemp/_wegwerf/blendimport_massstab/rollen_vergleich.py` (nur seori ändert sich)
und `ergaenzung_alle.py`; Vorlauf `2026.10.10.18.33.37` (Körper `head`, Ergänzung aus `head.002`, `pant`, `sock`).
"""

import tempfile
from pathlib import Path

import numpy as np
from django.test import SimpleTestCase

from core.dienste.blendimportkoerperergaenzung import Blendimportkoerperergaenzung
from core.dienste.blendimportrollen import Blendimportrollen

WEGWERF = Path(__file__).resolve().parent / '_wegwerf'


def netz(name, z0, z1, punkte, material, breite=0.5):
    return {'name': name, 'datei': name + '.npz', 'punkte': punkte, 'min': [0.0, 0.0, z0], 'max': [breite, breite, z1], 'gewichte': {},
            'materialien': [{'name': material, 'farbe': 'a.png'}]}


def seori():
    u"""Maße von seori nach dem Maßstab (Inventar `2026.10.10.18.33.37`)."""
    return {'netze': [
        netz('coat', 0.35, 1.39, 8483, 'coat', 0.9),
        netz('eyes', 1.55, 1.57, 1540, 'eyes', 0.1),
        netz('hair', 0.66, 1.68, 52470, 'hair.001', 0.6),
        netz('head', 0.743, 1.665, 35090, 'body', 1.0),
        netz('head.002', 0.0, 1.28, 21014, 'sock', 0.35),
        netz('pant', -0.069, 1.16, 12455, 'pant', 0.6),
        netz('shirt', 0.88, 1.52, 14863, 'shirt', 0.9),
    ], 'armaturen': 0, 'ohne_rig': True, 'ohne_armatur': []}


class Koerperwahl(SimpleTestCase):

    def _koerper(self, inventar):
        return [r['name'] for r in Blendimportrollen(inventar).zuordnen() if r['rolle'] == 'koerper']

    def test_1_hautmaterial_geht_vor_dem_hoechsten_netz(self):
        self.assertEqual(self._koerper(seori()), ['head'], 'nicht `head.002` (die Beine, 1,28 m, Material „sock")')

    def test_2_ohne_hautmaterial_bleibt_es_beim_hoechsten(self):
        inventar = seori()
        inventar['netze'][3]['materialien'] = [{'name': 'bodysuit', 'farbe': 'a.png'}]
        self.assertEqual(self._koerper(inventar), ['head.002'], '`bodysuit` ist kein Hautmaterial')
        inventar['netze'][3]['materialien'] = [{'name': 'Std_Skin_Body', 'farbe': 'a.png'}]
        self.assertEqual(self._koerper(inventar), ['head'], '`Std_Skin_Body` (Character Creator) schon')

    def test_2b_ein_kleines_netz_mit_hautmaterial_wird_kein_koerper(self):
        inventar = seori()
        inventar['netze'].append(netz('face', 1.45, 1.66, 3000, 'skin_face', 0.2))      # 12 % der Figur
        self.assertEqual(self._koerper(inventar), ['head'])


class Beinergaenzung(SimpleTestCase):

    def _ablage(self, ordner):
        class Ablage:
            @staticmethod
            def export(datei):
                return ordner / datei
        return Ablage()

    @staticmethod
    def _rohr(name, ordner, z0, z1, breite):
        u"""Ein Rohr (Beine oder Mantelsaum) als Dreiecksstreifen um die z-Achse: Ringe in 1 cm Abstand."""
        winkel = np.linspace(0, 2 * np.pi, 24, endpoint=False)
        ringe = np.arange(z0, z1 + 1e-9, 0.01)
        punkte = np.array([[0.5 * breite * np.cos(w), 0.3 * breite * np.sin(w), z] for z in ringe for w in winkel])
        dreiecke = []
        for r in range(len(ringe) - 1):
            for k in range(len(winkel)):
                a, b = r * 24 + k, r * 24 + (k + 1) % 24
                dreiecke += [[a, b, a + 24], [b, b + 24, a + 24]]
        np.savez(ordner / (name + '.npz'), punkte=punkte, dreiecke=np.array(dreiecke), uv_ecken=np.zeros((len(dreiecke), 3, 2)), material=np.zeros(len(dreiecke), dtype=int))
        return {'name': name, 'datei': name + '.npz', 'punkte': len(punkte), 'min': list(punkte.min(axis=0)), 'max': list(punkte.max(axis=0)), 'materialien': []}

    def _lauf(self, breiten):
        WEGWERF.mkdir(exist_ok=True)
        ordner = tempfile.TemporaryDirectory(dir=WEGWERF)
        self.addCleanup(ordner.cleanup)
        ordner = Path(ordner.name)
        winkel = np.linspace(0, 2 * np.pi, 24, endpoint=False)
        koerper = {'punkte': np.array([[0.15 * np.cos(w), 0.1 * np.sin(w), z] for z in (0.80, 0.82, 0.90, 1.2) for w in winkel])}   # Ring 0,30 m breit
        netze = [self._rohr(name, ordner, 0.0, 1.0, breite) for name, breite in breiten.items()]
        rollen = [{'name': n['name'], 'rolle': 'kleid'} for n in netze]
        ergaenzung = Blendimportkoerperergaenzung(self._ablage(ordner), {'netze': netze}, rollen)
        return ergaenzung.ergaenzen(koerper)

    def test_3_der_mantel_ist_kein_bein(self):
        aus = self._lauf({'bein': 0.31, 'mantel': 0.90})
        self.assertEqual(aus['kleider'], ['bein'], 'der Mantel (3-fach so breit wie der Körper) bleibt draußen')

    def test_4_schmale_netze_bleiben(self):
        aus = self._lauf({'hose': 0.33, 'strumpf': 0.32, 'bein': 0.31})
        self.assertEqual(sorted(aus['kleider']), ['bein', 'hose', 'strumpf'])
