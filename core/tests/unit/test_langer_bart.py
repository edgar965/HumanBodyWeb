# -*- coding: utf-8 -*-
"""Mesh to 3D, 12.10.2026: ein langer Bart ist Haar, nicht Hals und nicht Kleidung (`Sapienshaar.langer_bart`), und der Hals bekommt den Hautton, nicht die Farbe des Barts (`G9texturfuellung.hautnah`).

Anlass (Edgar am Zauberer: „Bart fehlt, Hals kaputt"): Sapiens sieht den Bart als `Face_Neck`; unter der Schnittebene des Kopfes (`Haarmaske.unten`, 12 cm unter dem Kinn) galt er weder als Haar noch — 279 cm², 13.206 Flächen,
y 132 bis 156 cm — als Kleidung: er stand in keinem Objekt. Und die Kopfkachel füllte Hals und Schulter mit dem MITTEL ALLER Netztexel (Haar, Bart, Hut): (132, 114, 102) statt Hautton (147, 102, 83), grau.
Kunstdaten: eine Kette von Flächen (Nachbarn = Vorgänger/Nachfolger), Stimmen je Klasse.
Sabotage-Gegenproben: in `langer_bart` `& hals` aus `kandidat` streichen → `test_nur_face_neck_zaehlt` rot; `connected_components` durch `ids` ersetzen → `test_nur_zusammenhaengendes_wird_bart` rot;
in `G9texturfuellung.hautnah` die Zeile `(rot >= …)` durch `True` ersetzen → `test_der_ton_der_luecke_kommt_nur_aus_hautnahen_texeln` rot.
"""

import unittest

import numpy as np
from scipy.sparse import diags

from core.dienste.sapienshaar import Sapienshaar
from Genesis9.texturfuellung import G9texturfuellung
from Kleidung.sapienszuordnung import Sapienszuordnung

FACE_NECK = Sapienszuordnung.NAMEN.index('Face_Neck')
UPPER = Sapienszuordnung.NAMEN.index('Upper_Clothing')


def _kette(n):
    return diags([np.ones(n - 1), np.ones(n - 1)], [-1, 1], format='csr')


def _klassen(n, je_flaeche):
    k = np.zeros((n, len(Sapienszuordnung.NAMEN)), dtype=np.float32)
    for i, klasse in enumerate(je_flaeche):
        if klasse is not None:
            k[i, klasse] = 10.0
    return k


class LangerBartTest(unittest.TestCase):
    """Zehn Flächen in einer Kette: 0–1 Haar (Anker), 2–9 liegen unter der Schnittebene."""

    def _lauf(self, klassen, kandidaten, cm2=200.0, anker=(0, 1)):          # 200 cm² je Fläche: schon eine einzelne Fläche reicht für `BART_MIN_CM2`
        n = 10
        a = np.isin(np.arange(n), anker)
        kand = np.isin(np.arange(n), kandidaten)
        return np.flatnonzero(Sapienshaar.langer_bart(klassen, kand, a, _kette(n), np.full(n, cm2)))

    def test_face_neck_unter_der_ebene_am_haar_wird_bart(self):
        klassen = _klassen(10, [None, None] + [FACE_NECK] * 8)
        self.assertEqual(self._lauf(klassen, range(2, 10)).tolist(), [2, 3, 4, 5, 6, 7, 8, 9])

    def test_nur_face_neck_zaehlt(self):
        """Fläche 4 ist Kleidung (Sapiens): sie unterbricht die Kette — 5…9 hängen nicht mehr am Haar."""
        klassen = _klassen(10, [None, None, FACE_NECK, FACE_NECK, UPPER] + [FACE_NECK] * 5)
        self.assertEqual(self._lauf(klassen, range(2, 10)).tolist(), [2, 3])

    def test_nur_zusammenhaengendes_wird_bart(self):
        """Fläche 3 ist kein Kandidat (z. B. Haut): was dahinter liegt, hängt nicht am Haar."""
        klassen = _klassen(10, [None, None] + [FACE_NECK] * 8)
        self.assertEqual(self._lauf(klassen, [2, 4, 5, 6]).tolist(), [2])

    def test_zu_wenig_flaeche_ist_kein_bart(self):
        klassen = _klassen(10, [None, None] + [FACE_NECK] * 8)
        self.assertEqual(self._lauf(klassen, range(2, 10), cm2=1.0).tolist(), [])             # 8 cm² < 100

    def test_ohne_anker_kein_bart(self):
        klassen = _klassen(10, [None, None] + [FACE_NECK] * 8)
        self.assertEqual(self._lauf(klassen, range(2, 10), anker=()).tolist(), [])

    def test_ungesehene_flaechen_zaehlen_nicht(self):
        """Ohne jede Stimme (Innenseite, Rückseite) weiß Sapiens nichts: kein Bart — sonst flösse die Robe von innen herein."""
        klassen = _klassen(10, [None, None, FACE_NECK, FACE_NECK] + [None] * 6)
        self.assertEqual(self._lauf(klassen, range(2, 10)).tolist(), [2, 3])


class VerdrahtungTest(unittest.TestCase):
    """Wächter: die Maske trägt den Schlüssel, das Haar-Objekt nimmt ihn, die Frisurwahl nicht (Quelltext)."""

    def test_der_schritt_haar_legt_den_bart_ab_und_das_objekt_nimmt_ihn(self):
        from pathlib import Path

        quelle = (Path(__file__).resolve().parents[2] / 'dienste' / 'meshfigurhaar.py').read_text(encoding='utf-8')
        self.assertIn("langer_bart=maske.get('langer_bart'", quelle)
        objekt = quelle[quelle.index('def objekt(self)'):quelle.index('def ruhenetz(self)')]
        self.assertIn("d['langer_bart']", objekt)
        ruhenetz = quelle[quelle.index('def ruhenetz(self)'):quelle.index('def hauttest(self)')]
        self.assertNotIn('langer_bart', ruhenetz, 'die Frisurwahl misst die Hülle des KOPFhaars — der Bart gehört nicht hinein')


class HautnahTest(unittest.TestCase):
    HAUT = (149.0, 103.0, 85.0)

    def test_haut_bart_haar_und_hut(self):
        farben = np.array([
            [151, 111, 92],          # Gesicht: rot vor blau, hell wie der Hautton
            [116, 80, 63],           # Gesicht im Schatten
            [152, 136, 123],         # grauer Bart: kaum röter als blau
            [95, 95, 105],           # grauer Hut: bläulich
            [60, 45, 40],            # dunkles Haar: zu dunkel
        ], dtype=np.float64) / 255.0
        self.assertEqual(G9texturfuellung.hautnah(farben[None], self.HAUT)[0].tolist(), [True, True, False, False, False])

    def test_der_ton_der_luecke_kommt_nur_aus_hautnahen_texeln(self):
        """Kopfkachel 64 × 64: links Haut, rechts weißer Bart (beide mit Gewicht 1), unten eine Lücke. Mit `hautton` hat die Lücke den Ton der Haut, ohne den Mittelton aus Haut UND Bart."""
        s = 64
        h_rgb = np.zeros((s, s, 3))
        h_rgb[:, :32] = np.array([151, 111, 92]) / 255.0
        h_rgb[:, 32:] = np.array([200, 195, 190]) / 255.0
        h_a = np.ones((s, s))
        h_a[48:] = 0.0                                              # die Lücke
        drin = np.ones((s, s), dtype=bool)
        grund = np.full((s, s, 3), 0.5)
        ohne, _ = G9texturfuellung.vorbereiten(grund, h_rgb, h_a, drin, kopf=True)
        mit, _ = G9texturfuellung.vorbereiten(grund, h_rgb, h_a, drin, kopf=True, hautton=self.HAUT)
        luecke_ohne, luecke_mit = ohne[56:, :].reshape(-1, 3).mean(axis=0), mit[56:, :].reshape(-1, 3).mean(axis=0)
        rot_ohne, rot_mit = luecke_ohne[0] - luecke_ohne[2], luecke_mit[0] - luecke_mit[2]
        self.assertGreater(rot_mit, rot_ohne + 0.03, 'mit Hautton bleibt die Lücke röter als mit dem Mittel aus Haut und Bart')

    def test_ohne_hautnahe_texel_gilt_der_hautton(self):
        """Eine Kachel ohne ein einziges hautnahes Netztexel (die Beine unter einer Robe: nur Fuß und Saum, grau) füllt ihre Lücken im Hautton — nicht im Ton der Texel, die da sind (Zauberer: Beine grau-braun)."""
        s = 64
        h_rgb = np.full((s, s, 3), np.array([120, 118, 112]) / 255.0)
        h_a = np.ones((s, s))
        h_a[48:] = 0.0
        drin = np.ones((s, s), dtype=bool)
        grund = np.full((s, s, 3), 0.5)
        ohne, _ = G9texturfuellung.vorbereiten(grund, h_rgb, h_a, drin, kopf=False)
        mit, _ = G9texturfuellung.vorbereiten(grund, h_rgb, h_a, drin, kopf=False, hautton=self.HAUT)
        self.assertTrue(np.allclose(ohne[56:].reshape(-1, 3).mean(axis=0), np.array([120, 118, 112]) / 255.0, atol=0.03), 'ohne Hautton: der Ton der vorhandenen Texel')
        self.assertTrue(np.allclose(mit[56:].reshape(-1, 3).mean(axis=0), np.array(self.HAUT) / 255.0, atol=0.03), 'mit Hautton: der Hautton')


if __name__ == '__main__':
    unittest.main()
