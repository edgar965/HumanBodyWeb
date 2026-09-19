# -*- coding: utf-8 -*-
"""Fotolinien: wo die Maße auf dem Foto liegen, und was die Tabelle daraus macht (19.09.2026).

Edgar: „eine Tabelle mit Bildern … ein Bild pro Zeile, Popup auf dem Bild
gibt die Maße an … auch die Position verschieben." Die Linien auf dem Foto
sind der Startpunkt zum Ziehen; sie müssen dort liegen, wo das Maß gemessen
wird. Kunstdaten wie in `test_bildmodell_fotomasse` (Figur von vorn, Rumpf
0,20–0,50 der Höhe, getrennte Beine ab 0,56):

1. `G9fotolinien.koerper` (vorn): Hüftlinie in der breitesten Zeile um die
   Hüfte, von Kante zu Kante — ihre Länge ist das Hüftmaß; Taille die
   schmalste; Oberschenkel im Beinsegment (Mitte 0,42); Oberarm quer zum
   Knochen mit dem ZIELWERT (das Foto misst keine Arme).
2. Maßstab: `px_je_m` = Maskenhöhe / Körperhöhe.
3. `Bildmodellfotolinien.alle`: eine Zeile je Hauptbild in Reihenfolge, Ansicht
   der Proportionen, gemerkte Linien nur für dieselbe Datei; `linien_pruefen`
   verwirft Unbekanntes und rundet.
4. Sabotage: eine anliegend-breite Brustzeile (Arm im Segment) bekommt den
   Zielwert um die Mitte, nicht die Armbreite.
5. Spalte „Nr." (20.09.2026): `reihenfolge([...])` nummeriert `reihe` 1..n, die
   Zeilen kommen in dieser Reihe, nicht Genannte hinten nach Typ; unbekannte
   Namen zählen nicht, eine leere Liste nummeriert nichts.
"""

from django.test import SimpleTestCase
from Genesis9.fotolinien import G9fotolinien

from core.dienste.bildmodellfotolinien import Bildmodellfotolinien

from .test_bildmodell_fotomasse import BREITE, HOEHE, _vorn


def _breite(t):
    """Breite (Anteil der Höhe) je Höhenanteil: Schulter 0,30, Taille 0,14 bei 0,40, Hüfte 0,22 bei 0,52."""
    if t < 0.10:
        return 0.09
    if t < 0.18:
        return 0.06
    if t < 0.26:
        return 0.30
    if t < 0.36:
        return 0.20
    if t < 0.44:
        return 0.14
    if t < 0.56:
        return 0.22 if 0.50 <= t < 0.54 else 0.19
    if t < 0.75:
        return 0.09
    return 0.06


class _Job:
    kennung = 'pruef'

    def __init__(self, bilder, optionen=None, ergebnis=None):
        self.bilder = bilder
        self.optionen = optionen or {}
        self.ergebnis = ergebnis or {}


class FotolinienTest(SimpleTestCase):
    def setUp(self):
        self.bild = _vorn(_breite)
        self.bild['datei'] = 'vorn.jpg'
        self.bild['kategorie'] = 'koerper'
        self.bild['gewicht'] = 1.0
        # Arme in der A-Stellung: Ellbogen (7) und Handgelenk (9) links unten außen.
        self.bild['rigs']['yolo']['punkte'][7] = [0.30, 0.35, 1.0]
        self.bild['rigs']['yolo']['punkte'][9] = [0.22, 0.48, 1.0]
        self.ziel = {'oberarm_dicke': 0.08, 'brust_breite': 0.30, 'schulter_breite': 0.42}

    def test_1_linien_liegen_wo_gemessen_wird(self):
        px_je_m, linien = G9fotolinien(self.bild, self.ziel).koerper(1.70)
        huefte = linien['huefte_breite']
        self.assertAlmostEqual(huefte[0][1], huefte[1][1])                     # waagerecht
        self.assertAlmostEqual(huefte[0][1] / HOEHE, 0.52, delta=0.02)          # breiteste Zeile um die Hüfte
        laenge = (huefte[1][0] - huefte[0][0]) / px_je_m
        self.assertAlmostEqual(laenge, 0.22 * 1.70, delta=0.01)                # Kante zu Kante = Hüftmaß
        taille = linien['taille_breite']
        self.assertAlmostEqual((taille[1][0] - taille[0][0]) / px_je_m, 0.14 * 1.70, delta=0.01)
        bein = linien['oberschenkel_dicke']
        # im linken Beinsegment
        self.assertAlmostEqual((bein[0][0] + bein[1][0]) / 2 / BREITE, 0.42, delta=0.02)
        arm = linien['oberarm_dicke']
        self.assertAlmostEqual(((arm[1][0] - arm[0][0]) ** 2 + (arm[1][1] - arm[0][1]) ** 2) ** 0.5 / px_je_m,
                               0.08, delta=0.002)                                         # Zielwert, quer

    def test_2_massstab(self):
        px_je_m, _ = G9fotolinien(self.bild, self.ziel).koerper(1.70)
        self.assertAlmostEqual(px_je_m, HOEHE / 1.70, delta=0.5)
        self.assertEqual(G9fotolinien(self.bild, self.ziel).koerper(None), (None, {}))

    def test_3_tabelle_und_gemerkte_linien(self):
        neben = {'datei': 'hand.jpg', 'kategorie': 'neben', 'teil': 'haende'}
        kopf_seite = dict(self.bild, datei='kopf_seite.jpg', kategorie='kopf', ansicht='seite')
        gemerkt = {'vorn.jpg': {'linien': {'huefte_breite': [[10, 20], [30, 20]]}},
                   'weg.jpg': {'linien': {'huefte_breite': [[1, 1], [2, 2]]}}}
        job = _Job([kopf_seite, neben, self.bild],
                   optionen={'proportionen_linien': gemerkt, 'person': {'groesse_cm': 170}},
                   ergebnis={'proportionen': {'ziel': {'oberarm_dicke': 8.0}}})
        zeilen = Bildmodellfotolinien(job).alle()
        # in Reihe, ohne Nebenbild
        self.assertEqual([z['datei'] for z in zeilen], ['vorn.jpg', 'kopf_seite.jpg'])
        self.assertEqual(zeilen[0]['ansicht'], 'vorn')
        self.assertIsNone(zeilen[1]['ansicht'])          # Kopf von der Seite: keine Linien
        # gemerkt schlägt Startlage
        self.assertEqual(zeilen[0]['linien']['huefte_breite'], [[10, 20], [30, 20]])
        self.assertIn('taille_breite', zeilen[0]['linien'])
        geprueft = Bildmodellfotolinien.linien_pruefen(
            {'vorn.jpg': {'linien': {'huefte_breite': [[1.234, 2], [3, 4]], 'quatsch': [[0, 0], [1, 1]],
                                     'taille_breite': 'kaputt'}}, 'leer.jpg': {'linien': {}}})
        self.assertEqual(geprueft, {'vorn.jpg': {'linien': {'huefte_breite': [[1.2, 2.0], [3.0, 4.0]]}}})

    def test_4_sabotage_arm_im_segment(self):
        # Brustzeile künstlich so breit wie die Schulter (Arm liegt an): die Linie darf nicht 0,30 lang sein.
        breit = dict(_vorn(lambda t: 0.42 if 0.26 <= t < 0.36 else _breite(t)), gewicht=1.0)
        _, linien = G9fotolinien(breit, {'brust_breite': 0.30 * 1.70}).koerper(1.70)
        brust = linien['brust_breite']
        self.assertAlmostEqual((brust[1][0] - brust[0][0]) / (HOEHE / 1.70), 0.30 * 1.70, delta=0.01)
        self.assertAlmostEqual((brust[0][0] + brust[1][0]) / 2 / BREITE, 0.5, delta=0.01)

    def test_5_reihenfolge_von_hand(self):
        seite = dict(self.bild, datei='seite.jpg', ansicht='seite')
        kopf = dict(self.bild, datei='kopf.jpg', kategorie='kopf', ansicht='vorne')
        job = _Job([kopf, seite, self.bild], optionen={'person': {'groesse_cm': 170}})
        f = Bildmodellfotolinien(job)
        self.assertEqual([b['datei'] for b in f.hauptbilder()], ['vorn.jpg', 'seite.jpg', 'kopf.jpg'])
        self.assertEqual(f.reihenfolge(['kopf.jpg', 'quatsch.jpg', 'vorn.jpg']),
                         {'kopf.jpg': 1, 'vorn.jpg': 2})
        self.assertEqual([b['datei'] for b in f.hauptbilder()], ['kopf.jpg', 'vorn.jpg', 'seite.jpg'],
                         'nummerierte zuerst, der Rest nach Typ')
        self.assertEqual([z['reihe'] for z in f.alle()], [1, 2, 3])
        self.assertNotIn('reihe', seite)
        self.assertEqual(f.reihenfolge([]), {})
        self.assertEqual(f.reihenfolge('kopf.jpg'), {}, 'kein Text als Liste')
        self.assertEqual([b['datei'] for b in f.hauptbilder()], ['vorn.jpg', 'seite.jpg', 'kopf.jpg'],
                         'ohne Nummern wieder nach Typ')
