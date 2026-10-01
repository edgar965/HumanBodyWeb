# -*- coding: utf-8 -*-
u"""Die Reste des Konzepts „2D3D per Blender-Mechanismen" (01.10.2026) — Kunstdaten, keine Bibliothek, keine Ablage
in 3DObjects (Wegwerfordner der Prüfablage).

1. `G9haarzusatz`: Ketten aus Segmenten; Duplikate (Versatz quer zur Strähne, Radius im Rahmen); Zwischensträhnen
   (Gewichte je Punkt summieren zu 1, zwei Quellsträhnen); Rückführung aus Blender (nur neue Strähnen zählen);
   Ablage/Lesen und `anwenden` → `G9strangzusatz` mit erweiterter Punktmenge, Segmenten, Material, Anteil, Haut.
2. `G9haarprofil.bandnetz`: je Strangpunkt zwei Bandpunkte, Breite Wurzel → Spitze, Dreiecke je Segment; `werte`.
3. `G9faltenbacken`: Tangenten eines Vierecks; flache Fläche gegen flache = flache Karte, gekippte Ecke kippt die
   Normale in der Karte; `staerke` 0 → flach.
4. `G9kleidpinsel.kreise`: Kreis mit Radius und Farbe, außerhalb bleibt Alpha 0.
5. `Blickwinkel.schaetzen`: vorn 0°, nach links gedreht +90°, Rücken 180°; ohne Punkte None.
6. `IterationGesicht`: aus einem Verhältnis eine gedämpfte Reglerzeile, unter der Toleranz nichts; Reglername über den
   Anzeigenamen.
7. `G9haarops.curl/braid` bewegen den hängenden Teil, nicht die Kappe (Attrappe der Geometrie).

Sabotage-Gegenproben: in `G9strangzusatz.punkte` den Versatz weglassen → Fall 1 rot (Duplikat liegt auf dem Original);
in `G9faltenbacken.karte` `staerke` ignorieren → Fall 3 rot.
"""
import numpy as np
from django.test import SimpleTestCase
from Genesis9.faltenbacken import G9faltenbacken
from Genesis9.haarprofil import G9haarprofil
from Genesis9.haarzusatz import G9haarzusatz
from Genesis9.haut import G9haut
from Genesis9.kleidpinsel import G9kleidpinsel
from Genesis9.strangzusatz import G9strangzusatz
from Genesis9.uvraster import G9uvraster
from iterationen2d3d.blickwinkel import Blickwinkel
from iterationen2d3d.iterationgesicht import IterationGesicht

from ._pruefablage import Pruefablage


class _Strang:
    u"""Attrappe eines `G9strang`: zwei Strähnen zu je drei Punkten, 1 cm auseinander, ein Material."""
    ART = 'strang'

    def __init__(self):
        self.kennung, self.name = 'strang_a', 'Strang A'
        self.punkte = np.array([[0.0, 1.0, 0.0], [0.0, 0.9, 0.0], [0.0, 0.8, 0.0],
                                [0.01, 1.0, 0.0], [0.01, 0.9, 0.0], [0.01, 0.8, 0.0]])
        self.segmente = np.array([[0, 1], [1, 2], [3, 4], [4, 5]])
        self.material = np.array([0, 0, 1, 1])
        self.anteil = np.array([0.0, 0.5, 1.0, 0.0, 0.5, 1.0], dtype=np.float32)
        self.materialnamen = ['Hair01', 'Hair02']
        self.haut = None

    def haut_von(self, kappe):
        self.haut = G9haut(['head'], np.zeros((6, 4), dtype=np.int32), np.tile([1.0, 0, 0, 0], (6, 1)))
        return self.haut

    def hautantwort(self):
        return self.haut.fuer() if self.haut else None

    def steckbrief(self):
        return {'kennung': self.kennung, 'art': self.ART}


class HaarzusatzTest(SimpleTestCase):
    databases = set()

    def test_1_ketten_duplikate_zwischen_und_proxy(self):
        s = _Strang()
        self.assertEqual([k.tolist() for k in G9haarzusatz.ketten(s.segmente, 6)], [[0, 1, 2], [3, 4, 5]])
        d = G9haarzusatz.duplizieren(s, s.punkte, anzahl=2, radius_mm=4.0, saat=3)
        self.assertEqual(d['l'].tolist(), [3, 3, 3, 3])
        self.assertEqual(d['m'].tolist(), [0, 0, 1, 1])
        laengen = np.linalg.norm(d['v'], axis=1) * 1000.0
        self.assertTrue(np.all(laengen >= 1.6 - 1e-6) and np.all(laengen <= 4.0 + 1e-6))
        self.assertTrue(np.allclose(d['v'][:, 1], 0.0, atol=1e-9))          # quer zur senkrechten Strähne
        i = G9haarzusatz.interpolieren(s, s.punkte, anzahl=1, saat=1)
        self.assertEqual(i['l'].tolist(), [3, 3])
        np.testing.assert_allclose(i['w'].sum(axis=1), 1.0)
        self.assertEqual(set(i['q'][0].tolist()) - {0}, {3} if i['w'][0, 2] > 0 else set(i['q'][0].tolist()) - {0})
        neu = np.vstack([s.punkte, s.punkte[:3] + [0.0, 0.0, 0.003]])
        b = G9haarzusatz.aus_blender(s, s.punkte, neu, [3, 3, 3])
        self.assertEqual(b['l'].tolist(), [3])                                 # die zwei alten zählen nicht
        np.testing.assert_allclose(b['v'], [[0, 0, 0.003]] * 3, atol=1e-7)
        with Pruefablage.ordner('haarzusatz') as ordner:
            from pathlib import Path
            from unittest import mock
            with mock.patch.object(G9haarzusatz, 'ordner', classmethod(lambda cls: Path(ordner))):
                brief = G9haarzusatz.ablegen('sorte_x', 'dup', ['strang_a'], [d], {'art': 'probe'})
                self.assertEqual((brief['straehnen'], brief['punkte']), (4, 12))
                self.assertEqual(G9haarzusatz.regler('sorte_x')[0]['name'], 'str.dup')
                self.assertEqual(G9haarzusatz.werte({'str.dup': 0.7, 'eigen.x': 1, 'str.weg': 0}), {'dup': 0.7})
                teile, kaefige = G9haarzusatz.anwenden('sorte_x', [(s, None)], [s.punkte], {'dup': 1.0})
                proxy = teile[0][0]
                self.assertIsInstance(proxy, G9strangzusatz)
                self.assertEqual(len(kaefige[0]), 6 + 12)
                self.assertEqual((len(proxy.segmente), len(proxy.material), len(proxy.anteil)), (4 + 8, 12, 18))
                self.assertGreater(float(np.linalg.norm(kaefige[0][6:9] - s.punkte[:3], axis=1).min()), 1e-3)
                dreiecke, gruppen = proxy.dreiecke_und_gruppen()
                self.assertEqual((len(dreiecke), len(gruppen)), (12, 2))
                haut = proxy.haut_von(None)
                self.assertEqual(haut.index.shape, (18, 4))
                self.assertEqual(proxy.kennung, 'strang_a')                    # Delegation
                with self.assertRaises(ValueError):
                    G9haarzusatz.ablegen('sorte_x', 'leer', ['strang_a'], [None])

    def test_2_bandnetz_und_profilwerte(self):
        p = np.array([[0.0, 1.0, 0.1], [0.0, 0.9, 0.1], [0.0, 0.8, 0.1]])
        d = np.array([[0, 1, 1], [1, 2, 2]])
        neu, dreiecke, quelle = G9haarprofil.bandnetz(p, d, [0.0, 0.5, 1.0], 1.5, 0.5, mitte=[0.0, 0.0, 0.0])
        self.assertEqual((neu.shape, dreiecke.shape, quelle.tolist()), ((6, 3), (4, 3), [0, 1, 2, 0, 1, 2]))
        self.assertAlmostEqual(float(np.linalg.norm(neu[3] - neu[0])) * 1000.0, 1.5, places=6)
        self.assertAlmostEqual(float(np.linalg.norm(neu[5] - neu[2])) * 1000.0, 0.5, places=6)
        self.assertEqual(G9haarprofil.werte({'profil.wurzel': 3.0}), (3.0, G9haarprofil.SPITZE_MM))
        self.assertEqual(G9haarprofil.werte({'profil.wurzel': 99.0, 'profil.spitze': 'x'}), (6.0, G9haarprofil.SPITZE_MM))
        self.assertEqual(len(G9haarprofil.regler('haar')), 2)
        self.assertEqual(G9haarprofil.regler('kleidung'), [])

    def test_3_falten_backen(self):
        punkte = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]])
        uv = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
        dreiecke = np.array([[0, 1, 2], [0, 2, 3]])
        gruppe = {'name': 'Stoff', 'index_ab': 0, 'index_anzahl': 6}
        t, b = G9faltenbacken.tangenten(punkte, dreiecke, uv)
        np.testing.assert_allclose(t, [[1, 0, 0], [1, 0, 0]], atol=1e-9)
        np.testing.assert_allclose(b, [[0, 1, 0], [0, 1, 0]], atol=1e-9)
        grund = dict(G9uvraster(punkte, dreiecke, uv, [gruppe], groesse=32).karte(gruppe), punkte=punkte)
        flach = G9uvraster(punkte, dreiecke, uv, [gruppe], groesse=32).karte(gruppe)
        karte = G9faltenbacken.karte(grund, flach, dreiecke, uv)
        self.assertTrue(np.allclose(karte[grund['maske']], [0.5, 0.5, 1.0], atol=1e-6))
        gekippt = punkte.copy()
        gekippt[2, 2] = 0.4
        neu = G9uvraster(gekippt, dreiecke, uv, [gruppe], groesse=32).karte(gruppe)
        karte = G9faltenbacken.karte(grund, neu, dreiecke, uv, staerke=1.0)
        kipp = np.linalg.norm(karte[grund['maske']][:, :2] * 2.0 - 1.0, axis=1)
        self.assertGreater(float(kipp.max()), 0.2)
        self.assertTrue(np.allclose(G9faltenbacken.karte(grund, neu, dreiecke, uv, staerke=0.0)[grund['maske']][:, :2],
                                    0.5, atol=1e-6))

    def test_4_pinsel_kreis(self):
        bild = np.zeros((16, 16, 4), dtype=np.float32)
        G9kleidpinsel.kreise(bild, [(8.0, 8.0)], 2.0, np.array([1.0, 0.0, 0.0]))
        self.assertAlmostEqual(float(bild[8, 8, 3]), 1.0, places=5)
        np.testing.assert_allclose(bild[8, 8, :3], [1, 0, 0])
        self.assertEqual(float(bild[0, 0, 3]), 0.0)
        self.assertLess(float(bild[8, 12, 3]), 0.5)

    def test_5_blickwinkel(self):
        def welt(lx, lz, rx, rz, nase=0.9, ohren=0.9, nz=-0.1):
            return {11: {'x': lx, 'y': 0, 'z': lz, 'sichtbar': 1}, 12: {'x': rx, 'y': 0, 'z': rz, 'sichtbar': 1},
                    23: {'x': lx * 0.5, 'y': -0.5, 'z': lz * 0.5, 'sichtbar': 1},
                    24: {'x': rx * 0.5, 'y': -0.5, 'z': rz * 0.5, 'sichtbar': 1},
                    0: {'x': 0, 'y': 0.3, 'z': nz, 'sichtbar': nase},
                    7: {'x': lx * 0.4, 'y': 0.3, 'z': 0, 'sichtbar': ohren}, 8: {'x': rx * 0.4, 'y': 0.3, 'z': 0, 'sichtbar': ohren}}
        self.assertAlmostEqual(Blickwinkel.schaetzen(welt(0.2, 0.0, -0.2, 0.0)), 0.0, places=3)
        self.assertAlmostEqual(Blickwinkel.schaetzen(welt(0.0, -0.2, 0.0, 0.2)), 90.0, places=3)
        self.assertAlmostEqual(abs(Blickwinkel.schaetzen(welt(-0.2, 0.0, 0.2, 0.0, nase=0.1, nz=0.1))), 180.0, places=3)
        self.assertIsNone(Blickwinkel.schaetzen({}))
        self.assertEqual(Blickwinkel.rolle(-80.0), 'rechts')

    def test_6_iterationgesicht(self):
        class M:
            koerper = {}
        regler = [{'name': 'x_Face Width-0x1', 'anzeige': '200+ Face Width'},
                  {'name': 'x_Face Width Upper', 'anzeige': '200+ Face Upper Width'},
                  {'name': 'x_Eyes Distance-0x2', 'anzeige': '200+ Eyes Distance'}]
        befund = {'gesicht': {'verhaeltnis': {'breite': 1.2, 'augen': 1.01, 'mund': 0.8}, 'kopfregler': regler}}
        zeilen = IterationGesicht(M(), befund).aufrufe()
        self.assertEqual(zeilen, ["m.koerper_regler('x_Face Width-0x1', 0.12)"])
        self.assertEqual(IterationGesicht(M(), {}).aufrufe(), [])

    def test_7_curl_und_braid_lassen_die_kappe(self):
        from Genesis9.haarops import G9haarops

        class G:
            mitte = np.array([0.0, 1.6, 0.0])
            nacken = 1.56
        p = np.array([[0.05, 1.65, 0.0], [0.05, 1.50, 0.0], [0.05, 1.30, 0.0], [-0.05, 1.30, -0.05]])
        g = G()
        g.haengt = np.clip(g.nacken - p[:, 1], 0.0, None)
        ops = G9haarops.__new__(G9haarops)
        w = np.ones(len(p))
        curl = ops.curl(g, p, w, radius_cm=2.0, windungen=8.0)
        self.assertAlmostEqual(float(np.linalg.norm(curl[0])), 0.0)
        self.assertGreater(float(np.linalg.norm(curl[2])), 0.005)
        braid = ops.braid(g, p, w, breite_cm=3.0, windungen=6.0)
        self.assertAlmostEqual(float(np.linalg.norm(braid[0])), 0.0)
        self.assertGreater(float(np.abs(braid[2:]).max()), 0.002)
        self.assertIn('curl', G9haarops.OPERATIONEN)
