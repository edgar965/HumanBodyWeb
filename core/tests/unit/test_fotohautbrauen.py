# -*- coding: utf-8 -*-
"""`Fotohautbrauen`: die aufgemalten Brauen aus der Kopfkachel nehmen (10.10.2026, Edgar, Asian: „ändern funktioniert nicht").

Die Kachel eines Imports trägt die Brauen des Originals, das Netz des gewählten Brauenstils liegt genau darauf. Geprüft an künstlichen
Kacheln (Hautfläche, Brauen und Störungen mit bekannter Lage; die echten Kacheln stehen in `ProjektTemp/_wegwerf/import_serie/brauen_probe_*.png`):

1. Eine dünne dunkle Braue in der Zone verschwindet (Mittel der Stelle ≈ Haut), alles außerhalb der Zone bleibt Pixel für Pixel.
2. Ohne Braue: dasselbe Bild zurück (kein Neuschreiben), Bericht `braue_px` 0.
3. Eine dicke dunkle Fläche (Haar, Schatten) bleibt — nur Striche sind Brauen.
4. Eine dünne Linie über den Augen (Wimpern, Lidlinie) bleibt.
5. Eine Kachel voller dunkler Muster (Kunsthaut, nicht Gesichtshaut) bleibt unverändert, mit Hinweis.
6. Gleiches Ergebnis bei doppelter Auflösung (gerechnet wird auf einer verkleinerten Zone, `ARBEIT_PX`).
7. `datei`: legt die Retusche unter dem Namen mit Fassung ab, ein zweiter Aufruf liest sie nur; ohne Braue kommt die Quelle zurück.

Sabotage-Gegenprobe (Läufer `ProjektTemp/_wegwerf/import_serie/py_trocken.py`, ohne Django-Start): `augenmaske` leer → Fall 4 rot; `HOECHSTENS` 1 → Fall 5 rot;
`DICKE` 0,002 → Fälle 1, 6, 7 rot (nichts gilt mehr als dünn); `DICKE` 0,3 → Fall 3 rot (die dicke Fläche gilt als Strich).
"""

from pathlib import Path

import numpy as np
from django.test import SimpleTestCase, override_settings
from PIL import Image

from core.dienste.fotohautbrauen import Fotohautbrauen as F

from ._pruefablage import Pruefablage

HAUT = (212, 168, 148)
BRAUE = (112, 84, 64)


def kachel(groesse=800, zeichnen=None):
    """Eine glatte Hautfläche; `zeichnen(feld, x, y)` malt hinein (`x(u)`, `y(v)` rechnen UV in Pixel um)."""
    feld = np.zeros((groesse, groesse, 3), dtype=np.uint8)
    feld[:] = HAUT
    x = lambda u: int(round(u * groesse))
    y = lambda v: int(round((1 - v) * groesse))
    if zeichnen:
        zeichnen(feld, x, y)
    return Image.fromarray(feld)


def strich(feld, x, y, u0, u1, v, dicke, farbe=BRAUE):
    """Ein waagrechter Strich von u0 bis u1 auf der Höhe v mit `dicke` Pixeln."""
    mitte = y(v)
    feld[mitte - dicke // 2: mitte + (dicke + 1) // 2, x(u0): x(u1)] = farbe


class FotohautbrauenTest(SimpleTestCase):
    databases = set()

    def test_1_eine_duenne_braue_verschwindet(self):
        bild = kachel(zeichnen=lambda f, x, y: strich(f, x, y, 0.40, 0.48, 0.63, 8))
        neu, bericht = F.retuschieren(bild)
        self.assertGreater(bericht['braue_px'], 0)
        a, b = np.asarray(bild, dtype=float), np.asarray(neu, dtype=float)
        y = int(round((1 - 0.63) * 800))
        stelle = (slice(y - 3, y + 3), slice(int(0.41 * 800), int(0.47 * 800)))
        self.assertLess(np.abs(b[stelle] - np.array(HAUT)).max(), 14, 'die Braue steht noch')
        self.assertGreater(np.abs(a[stelle] - np.array(HAUT)).max(), 60, 'die Probe hatte gar keine Braue')
        u0, u1, v0, v1 = F.ZONE
        aussen = np.ones(a.shape[:2], dtype=bool)
        aussen[int((1 - v1) * 800): int((1 - v0) * 800) + 1, int(u0 * 800) - 1: int(u1 * 800) + 1] = False
        self.assertTrue(np.array_equal(a[aussen], b[aussen]), 'außerhalb der Zone wurde etwas verändert')

    def test_2_ohne_braue_dasselbe_bild(self):
        bild = kachel()
        neu, bericht = F.retuschieren(bild)
        self.assertIs(neu, bild)
        self.assertEqual(bericht['braue_px'], 0)

    def test_3_eine_dicke_dunkle_flaeche_bleibt(self):
        def haar(f, x, y):
            f[y(0.64): y(0.60), x(0.42): x(0.47)] = BRAUE          # 32 × 40 px
        bild = kachel(zeichnen=haar)
        neu, bericht = F.retuschieren(bild)
        self.assertTrue(np.array_equal(np.asarray(bild), np.asarray(neu)), bericht)

    def test_4_eine_linie_ueber_den_augen_bleibt(self):
        bild = kachel(zeichnen=lambda f, x, y: strich(f, x, y, 0.40, 0.46, 0.575, 6))     # v 0,575: Wimpern-/Lidlinie
        neu, bericht = F.retuschieren(bild)
        self.assertTrue(np.array_equal(np.asarray(bild), np.asarray(neu)), bericht)

    def test_5_kunsthaut_bleibt_unveraendert(self):
        def streifen(f, x, y):
            for zeile in range(y(0.665), y(0.568), 4):                  # dichte dunkle Streifen: mehr als ein Drittel der Zone
                f[zeile: zeile + 3, x(0.34): x(0.66)] = BRAUE
        bild = kachel(zeichnen=streifen)
        neu, bericht = F.retuschieren(bild)
        self.assertTrue(np.array_equal(np.asarray(bild), np.asarray(neu)), bericht)
        self.assertIn('hinweis', bericht)

    def test_6_gleiches_ergebnis_bei_doppelter_aufloesung(self):
        def male(f, x, y):
            strich(f, x, y, 0.40, 0.48, 0.63, f.shape[0] // 100)
        klein, gross = kachel(800, male), kachel(1600, male)
        _a, bericht_klein = F.retuschieren(klein)
        neu_gross, bericht_gross = F.retuschieren(gross)
        self.assertGreater(bericht_klein['braue_px'], 0)
        self.assertGreater(bericht_gross['braue_px'], 0)
        y = int(round((1 - 0.63) * 1600))
        stelle = (slice(y - 6, y + 6), slice(int(0.41 * 1600), int(0.47 * 1600)))
        self.assertLess(np.abs(np.asarray(neu_gross, dtype=float)[stelle] - np.array(HAUT)).max(), 14)

    def test_7_datei_legt_ab_und_liest_nur(self):
        with Pruefablage.ordner('fotohautbrauen_') as wurzel, override_settings(MEDIA_ROOT=wurzel):
            modell = Path(wurzel) / 'Modell'
            modell.mkdir()
            quelle = modell / 'haut_1001_farbe.jpg'
            kachel(zeichnen=lambda f, x, y: strich(f, x, y, 0.40, 0.48, 0.63, 8)).save(quelle, quality=95)
            ziel = F.datei(quelle)
            self.assertNotEqual(ziel, quelle)
            self.assertIn('_f%d' % F.FASSUNG, ziel.name)
            self.assertEqual(ziel.parent, F.ordner())
            stand = ziel.stat().st_mtime_ns
            self.assertEqual(F.datei(quelle), ziel)
            self.assertEqual(ziel.stat().st_mtime_ns, stand, 'ein zweiter Aufruf hat neu geschrieben')
            leer = modell / 'haut_1001_leer.jpg'
            kachel().save(leer, quality=95)
            self.assertEqual(F.datei(leer), leer, 'ohne Braue muss die Quelle zurückkommen')
