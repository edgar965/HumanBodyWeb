"""Bestandteile (`Kleidung/bestandteile.py`): aus den Begriffs-Stimmen von SAM 3 die Bestandteile des Netzes (13.10.2026).

Kunstnetz: ein Dreiecksstreifen (Dreieck i = Punkte i, i+1, i+2; Nachbarn teilen eine Kante), jedes Dreieck 100 cm². Geschrieben, nicht gelaufen.
"""
import unittest

import numpy as np

from Kleidung.bestandteile import Bestandteile


def streifen(n):
    return np.array([[i, i + 1, i + 2] for i in range(n)], dtype=np.int64)


def daten(stimmen, begriffe, gruppen, treffer, bestwert, pixel=None):
    return {'begriffe': begriffe, 'gruppen': gruppen, 'stimmen': np.asarray(stimmen, dtype=np.float32), 'treffer': np.asarray(treffer), 'bestwert': np.asarray(bestwert, dtype=np.float32), 'pixel': pixel}


class BestandteileTest(unittest.TestCase):

    def test_ein_begriff_in_einer_einzigen_ansicht_zaehlt_nicht(self):
        st = np.zeros((10, 1))
        st[:, 0] = 20
        teile = Bestandteile.zerlegen(daten(st, ['sword'], ['requisit'], [1], [0.83]), streifen(10), np.full(10, 100.0))
        self.assertEqual(teile, [])                                         # Sabotage: MIN_ANSICHTEN = 1 → ein Treffer, rot

    def test_ein_begriff_in_mehreren_ansichten_wird_ein_bestandteil(self):
        st = np.zeros((10, 1))
        st[2:8, 0] = 20
        teile = Bestandteile.zerlegen(daten(st, ['staff'], ['requisit'], [4], [0.7]), streifen(10), np.full(10, 100.0))
        self.assertEqual(len(teile), 1)
        self.assertEqual(teile[0]['name'], 'staff')
        self.assertEqual(int(teile[0]['maske'].sum()), 6)
        self.assertEqual(teile[0]['cm2'], 600.0)

    def test_begriffe_derselben_gruppe_auf_derselben_flaeche_sind_ein_bestandteil(self):
        # „hat“, „crown“, „headdress“ am Kopfschmuck der Spiralballerina: eine Fläche, drei Namen.
        st = np.zeros((10, 3))
        st[2:8, 0], st[2:8, 1], st[3:8, 2] = 20, 18, 15
        teile = Bestandteile.zerlegen(daten(st, ['hat', 'crown', 'headdress'], ['kopf'] * 3, [2, 2, 4], [0.91, 0.89, 0.92]), streifen(10), np.full(10, 100.0))
        self.assertEqual(len(teile), 1)                                     # Sabotage: MIN_UEBERLAPP = 2 → drei Bestandteile, rot
        self.assertEqual(teile[0]['name'], 'headdress')                     # der Begriff mit dem besten Wert
        self.assertEqual(sorted(teile[0]['synonyme']), ['crown', 'hat'])

    def test_verschiedene_gruppen_verschmelzen_nicht(self):
        st = np.zeros((10, 2))
        st[2:8, 0], st[2:8, 1] = 20, 10
        teile = Bestandteile.zerlegen(daten(st, ['staff', 'beard'], ['requisit', 'haar'], [4, 3], [0.7, 0.8]), streifen(10), np.full(10, 100.0))
        self.assertEqual([t['name'] for t in teile], ['staff'])             # die Fläche gehört dem Begriff mit den meisten Stimmen

    def test_schwache_flaechen_am_kern_gehoeren_dazu_wenn_die_mehrheit_der_pixel_stimmt(self):
        # Ein dünner Teil: der Kern (≥ 4 Pixel) hat Lücken aus Flächen mit 1–3 Pixeln — ohne Hysterese zerfällt er.
        st = np.zeros((10, 1))
        st[[0, 1, 2, 3, 6, 7, 8, 9], 0] = 20
        st[[4, 5], 0] = 2
        pixel = np.full(10, 20.0)
        pixel[[4, 5]] = 3
        ohne = Bestandteile.zerlegen(daten(st, ['staff'], ['requisit'], [4], [0.7], pixel=None), streifen(10), np.full(10, 100.0))
        mit = Bestandteile.zerlegen(daten(st, ['staff'], ['requisit'], [4], [0.7], pixel=pixel), streifen(10), np.full(10, 100.0))
        self.assertEqual(int(ohne[0]['maske'].sum()), 8)
        self.assertEqual(ohne[0]['stuecke'], 2)
        self.assertEqual(int(mit[0]['maske'].sum()), 10)                    # Sabotage: Hysterese streichen → 8, rot
        self.assertEqual(mit[0]['stuecke'], 1)

    def test_kleine_stuecke_fallen_weg(self):
        st = np.zeros((10, 1))
        st[0, 0] = 20                                                        # 100 cm² — und ein 1-Dreieck-Stück bei MIN_CM2 150
        flaechen = streifen(10)
        alte = Bestandteile.MIN_CM2
        Bestandteile.MIN_CM2 = 150.0
        try:
            teile = Bestandteile.zerlegen(daten(st, ['staff'], ['requisit'], [4], [0.7]), flaechen, np.full(10, 100.0))
        finally:
            Bestandteile.MIN_CM2 = alte
        self.assertEqual(teile, [])

    def test_laden_verlangt_dieselbe_flaechenzahl(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory(dir=str(Path(__file__).resolve().parents[3] / 'ProjektTemp')) as ordner:
            pfad = Path(ordner) / 'teile.npz'
            np.savez(pfad, begriffe=np.array(['staff']), gruppen=np.array(['requisit']), stimmen=np.zeros((5, 1), dtype=np.float32), treffer=np.array([4]), bestwert=np.array([0.7], dtype=np.float32),
                     pixel=np.zeros(5, dtype=np.float32), flaechen=5)
            self.assertIsNotNone(Bestandteile.laden(pfad, 5))
            self.assertIsNone(Bestandteile.laden(pfad, 6))                  # Stimmen eines anderen Netzes gelten nie
            self.assertIsNone(Bestandteile.laden(Path(ordner) / 'fehlt.npz', 5))


if __name__ == '__main__':
    unittest.main()
