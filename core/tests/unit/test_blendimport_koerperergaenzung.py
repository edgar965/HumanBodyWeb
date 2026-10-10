# -*- coding: utf-8 -*-
"""Körperergänzung für „Mesh to 3D" (10.10.2026): die Beine unter einer Strumpfhose (Rosemary Winters).

Nur die Geometrie: `Blendimportkoerperergaenzung.ergaenzen` liest die Kleidungsnetze aus der Ablage — hier liefert eine
Unterklasse die Arrays direkt, damit der Test ohne Datei und ohne Blender auskommt.

1. Ein Strumpf unter der Körperkante liefert Punkte, Dreiecke und die Stückliste; die Indizes passen.
2. Ein Kleidungsnetz ganz über der Körperkante liefert nichts (None).
3. Die neuen Punkte rücken nach innen, höchstens um DICKE_M (Stoffdicke), nie nach außen.
4. Nur Netze mit Rolle „kleid" zählen; ein Auge unter dem Körper bleibt außen vor.

Sabotage-Gegenprobe: `DICKE_M` auf 0 → Fall 3 rot (kein Versatz); Rolle-Filter entfernen → Fall 4 rot.

Nicht gelaufen (Stand 10.10.2026) — läuft nur auf Ansage.
"""

import numpy as np
from django.test import SimpleTestCase

from core.dienste.blendimportkoerperergaenzung import Blendimportkoerperergaenzung


def _ring(z0, z1, radius=0.1, n=8):
    """Zwei Ringe (unten, oben) mit Dreiecken dazwischen — ein kurzer Zylinder um die z-Achse."""
    winkel = np.linspace(0, 2 * np.pi, n, endpoint=False)
    unten = np.column_stack([radius * np.cos(winkel), radius * np.sin(winkel), np.full(n, z0)])
    oben = np.column_stack([radius * np.cos(winkel), radius * np.sin(winkel), np.full(n, z1)])
    punkte = np.vstack([unten, oben])
    dreiecke = []
    for i in range(n):
        j = (i + 1) % n
        dreiecke.append([i, j, n + i])
        dreiecke.append([j, n + j, n + i])
    return punkte, np.array(dreiecke, dtype=np.int64)


class _Ergaenzung(Blendimportkoerperergaenzung):
    """Liefert die Netze aus dem Speicher statt aus der Ablage."""

    def __init__(self, netze, rollen):
        super().__init__(None, {'netze': [{'name': n, 'datei': n} for n in netze]}, rollen)
        self.netze = netze

    def _laden(self, name):
        punkte, dreiecke = self.netze[name]
        return {'punkte': punkte, 'dreiecke': dreiecke}


def _koerper(kante=0.5):
    """Ein Körper, dessen tiefster Punkt auf `kante` liegt."""
    punkte, _ = _ring(kante, kante + 1.0)
    return {'punkte': punkte}


class KoerperergaenzungTest(SimpleTestCase):
    databases = set()

    def test_1_strumpf_unter_der_koerperkante_liefert_punkte_dreiecke_und_stueckliste(self):
        strumpf = _ring(0.0, 0.1)  # Oberkante 0,1 m, Körperkante 0,5 m: liegt darunter
        mod = _Ergaenzung({'sock': strumpf}, [{'name': 'sock', 'rolle': 'kleid'}])
        ergebnis = mod.ergaenzen(_koerper(0.5))
        self.assertIsNotNone(ergebnis)
        self.assertEqual(ergebnis['kleider'], ['sock'])
        self.assertEqual(len(ergebnis['punkte']), len(ergebnis['winkel']))
        self.assertEqual(len(ergebnis['punkte']), len(ergebnis['hoehe']))
        self.assertTrue(np.all(ergebnis['dreiecke'] < len(ergebnis['punkte'])))
        self.assertTrue(np.all(np.isfinite(ergebnis['winkel'])))

    def test_2_kleidung_ganz_ueber_der_koerperkante_liefert_nichts(self):
        ueber = _ring(0.6, 0.7)  # Körperkante 0,5 m; der Strumpf liegt darüber
        mod = _Ergaenzung({'hemd': ueber}, [{'name': 'hemd', 'rolle': 'kleid'}])
        self.assertIsNone(mod.ergaenzen(_koerper(0.5)))

    def test_3_neue_punkte_ruecken_nach_innen_hoechstens_um_die_stoffdicke(self):
        strumpf_punkte, strumpf_dreiecke = _ring(0.0, 0.1)
        mod = _Ergaenzung({'sock': (strumpf_punkte, strumpf_dreiecke)}, [{'name': 'sock', 'rolle': 'kleid'}])
        ergebnis = mod.ergaenzen(_koerper(0.5))
        # Alle 16 Punkte liegen auf Radius 0,1 m; die Nachbarn eines Punkts (gleiche Schicht, 8 cm) symmetrisch um ihn —
        # die Richtung zur Mitte ist also genau radial, der Versatz genau DICKE_M.
        alt = np.hypot(strumpf_punkte[:, 0], strumpf_punkte[:, 1])
        neu = np.hypot(ergebnis['punkte'][:, 0], ergebnis['punkte'][:, 1])
        self.assertTrue(np.all(neu < alt.min()), 'kein Punkt wurde nach innen versetzt')
        versatz = alt.min() - neu
        self.assertTrue(np.all(versatz <= Blendimportkoerperergaenzung.DICKE_M + 1e-6))
        self.assertTrue(np.all(versatz > 0.5 * Blendimportkoerperergaenzung.DICKE_M))

    def test_4_nur_kleidung_zaehlt_ein_auge_unter_dem_koerper_bleibt_aussen_vor(self):
        strumpf = _ring(0.0, 0.1)
        auge = _ring(0.0, 0.1, radius=0.01)
        mod = _Ergaenzung({'sock': strumpf, 'auge': auge},
                          [{'name': 'sock', 'rolle': 'kleid'}, {'name': 'auge', 'rolle': 'auge'}])
        ergebnis = mod.ergaenzen(_koerper(0.5))
        self.assertEqual(ergebnis['kleider'], ['sock'])
        self.assertEqual(len(ergebnis['punkte']), 8 * 2)
