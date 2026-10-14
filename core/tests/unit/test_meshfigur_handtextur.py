# -*- coding: utf-8 -*-
"""`Meshfigurtextur._hand_nachschlagen` und die Verdrahtung (14.10.2026, Edgar1: „Hände wirken fremd … haben Naht und Textur stimmt nicht“): Hand und Finger nehmen die Farbe von der HAND des Netzes — nahe genug (8 mm), Normale in dieselbe Richtung, Fläche von Sapiens als Hand gesehen.

Kunstdaten ohne GPU und Netz: eine Handprobe auf einem Dreieck, die Suche als Attrappe. Die Nagelkachel behält ihre Daz-Nägel (Wächter am Quelltext).
Sabotage-Gegenproben: `HAND_GRENZE = 1.0` → `test_zu_weit_weg_gilt_nicht` rot; `HAND_NORMALE_AB = -1.0` → `test_eine_abgewandte_flaeche_gilt_nicht` rot.
"""

import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()


def _textur(abstand, haut=True):
    """Eine `Meshfigurtextur` ohne Konstruktor: eine Handprobe (Index 0 der Handproben = Probe 5 des Netzes) mit Normale +z."""
    from meshfigur_textur import Meshfigurtextur

    t = object.__new__(Meshfigurtextur)
    punkte = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    t.scan = SimpleNamespace(punkte=punkte, flaechen=np.array([[0, 1, 2]]), farben=lambda flaeche, anteile: np.tile(np.array([180, 120, 100], dtype=np.uint8), (len(flaeche), 1)))
    t.hand_proben = np.array([5])
    t.pn = np.zeros((6, 3))
    t.pn[5] = [0.0, 0.0, 1.0]
    t.flaeche = np.zeros(6, dtype=np.int64)
    t.bary = np.tile(np.array([1 / 3, 1 / 3, 1 / 3]), (6, 1))
    t.haut_flaeche = np.array([haut])
    t.suche_hand = SimpleNamespace(naechster=lambda orte: (np.full(len(orte), abstand), np.zeros(len(orte), dtype=np.int64)))
    return t


ORTE = np.array([[0.2, 0.2, 0.0], [0.3, 0.3, 0.0]])
NORMALEN = np.array([[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]])


class HandnachschlagenTest(unittest.TestCase):
    def test_nahe_hand_gibt_die_farbe_des_netzes(self):
        t = _textur(0.003)
        farben, gueltig, haut = t._hand_nachschlagen(ORTE, NORMALEN)
        self.assertTrue(gueltig.all())
        self.assertEqual(farben.tolist(), [[180, 120, 100]] * 2)
        self.assertTrue(haut.all())

    def test_zu_weit_weg_gilt_nicht(self):
        t = _textur(0.02)                                           # 2 cm: die Hand der Figur liegt neben der des Netzes
        _, gueltig, _ = t._hand_nachschlagen(ORTE, NORMALEN)
        self.assertFalse(gueltig.any())

    def test_eine_abgewandte_flaeche_gilt_nicht(self):
        t = _textur(0.003)
        _, gueltig, _ = t._hand_nachschlagen(ORTE, -NORMALEN)                  # Handrücken gegen Handfläche
        self.assertFalse(gueltig.any())

    def test_das_urteil_der_hautkarte_wird_mitgegeben(self):
        t = _textur(0.003, haut=False)
        _, _, haut = t._hand_nachschlagen(ORTE, NORMALEN)
        self.assertFalse(haut.any())

    def test_ohne_hautkarte_kein_urteil(self):
        t = _textur(0.003)
        t.haut_flaeche = None
        self.assertIsNone(t._hand_nachschlagen(ORTE, NORMALEN)[2])


class VerdrahtungTest(unittest.TestCase):
    def _quelle(self, *teile):
        return (Path(__file__).resolve().parents[4].joinpath(*teile)).read_text(encoding='utf-8')

    def test_die_nagelkachel_bleibt_ohne_netzfarbe(self):
        quelle = self._quelle('meshto3d', 'meshfigur_textur.py')
        self.assertIn('if self.suche_hand is not None and k != self.NAGELKACHEL:', quelle)
        self.assertIn('NAGELKACHEL = 1005', quelle)
        self.assertIn('HAND_BEREICHE = (2, 3)', quelle)

    def test_der_runner_reicht_die_handflaechen_durch(self):
        quelle = self._quelle('meshto3d', 'meshfigur_runnertextur.py')
        self.assertIn("hand_flaeche=None if self.daten.optionen.get('handtextur') == 'aus' else self._handmaske()", quelle)

    def test_die_texelpruefung_nimmt_haende_nur_mit_treffern_und_nie_in_der_nagelkachel(self):
        quelle = self._quelle('HumanBodyWeb', 'core', 'dienste', 'meshfigurtexelpruefung.py')
        self.assertIn('if kachel != self.NAGELKACHEL and (hand & getroffen).any():', quelle)

    def test_die_handklassen_stimmen_mit_der_django_seite_ueberein(self):
        from core.dienste.meshfigurhalter import Meshfigurhalter

        try:
            from meshfigur_runnertextur import Meshfigurrunnertextur
        except ImportError as fehler:                               # der Runner braucht torch (nur python10)
            self.skipTest('Runner nicht importierbar: %s' % fehler)
        self.assertEqual(tuple(Meshfigurrunnertextur.HAND_KLASSEN), tuple(Meshfigurhalter.HAND_KLASSEN))
        self.assertEqual(float(Meshfigurrunnertextur.HAND_STIMMEN), float(Meshfigurhalter.MIN_STIMMEN))


if __name__ == '__main__':
    unittest.main()
