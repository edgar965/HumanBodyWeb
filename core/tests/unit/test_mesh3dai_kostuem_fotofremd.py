# -*- coding: utf-8 -*-
"""Regel „Fotofarbe aus fremdem Glied“ Fassung 2 (`Kostuemfotofremd.fremd_je_texel`) — dieselbe Regel für die Kostüm-Prüfung und den Schritt „fotohaut“ (`Fotohautwahl`), auf der CPU.

Anlass (Edgar, 08.11.2026 zu edgar_fotos: „textur der hand auf körper“): Fassung 1 verglich nur drei Glieder und meldete Grenzsäume (Oberschenkel auf dem Gesäß), die Hand auf dem Körper ging unter.
Die Teilkarte der Haut (`abschnitt_da`, sonst aus `Hautteilkarte`) ist hier eine Kunstkarte 1 × 10 × 4 × 4: links Rumpf, rechts linker Arm. Zusagen:
    1  Hand auf dem Rumpf ist fremd, Rumpf auf dem Rumpf nicht.
    2  Oberschenkel auf dem Gesäß (Rumpfkachel) ist erlaubt — der Grenzsaum aus Fassung 1.
    3  Die rechte Hand auf dem linken Arm ist fremd, auf dem eigenen Arm nicht.
    4  Keine Haut (Kleidung, Klasse −1) ist nie fremd — die Regel betrifft nur Hautfarbe.
    5  Der Schritt „fotohaut“ ruft dieselbe Regel (Quelltext), keine zweite Fassung.
Sabotage gefahren 09.11.2026 (`ProjektTemp/_wegwerf/mehrfoto/stab_test_sabotage.py`, per mock): Oberschenkel ohne Rumpf erlaubt → Fall 2 rot; keine Klasse erlaubt → Fall 1 rot.
"""
import sys
import unittest
from pathlib import Path
from unittest import mock

from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))
sys.path.insert(0, str(settings.TOOLS_ROOT / 'mesh3dai'))


@unittest.skipUnless(__import__('importlib').util.find_spec('torch'), 'torch fehlt')
class KostuemfotofremdTest(unittest.TestCase):
    databases = set()

    @staticmethod
    def karte():
        """(1, A, 4, 4): Spalten 0–1 Rumpf, Spalten 2–3 linker Arm (Bildpunkte der Karte = halbe Texel)."""
        import torch
        from mesh3dai_kostuem_fotofremd import Kostuemfotofremd
        da = torch.zeros((1, len(Kostuemfotofremd.ABSCHNITTE), 4, 4), dtype=torch.bool)
        da[0, Kostuemfotofremd.ABSCHNITTE.index('rumpf'), :, :2] = True
        da[0, Kostuemfotofremd.ABSCHNITTE.index('arm_links'), :, 2:] = True
        return da

    def fremd(self, klassen, spalten):
        """Je (Sapiens-Name oder None für −1, Texelspalte) → fremd?"""
        import torch
        from mesh3dai_kostuem_fotofremd import Kostuemfotofremd
        from Sapiens2Torch.segmentierung import S2segmentierung
        kl = torch.tensor([S2segmentierung.NAMEN.index(n) if n else -1 for n in klassen])
        n = len(klassen)
        with mock.patch.object(Kostuemfotofremd, 'abschnitt_da', return_value=self.karte()):
            aus = Kostuemfotofremd.fremd_je_texel('weiblich', [1002], torch.zeros(n, dtype=torch.int64), torch.zeros(n, dtype=torch.int64), torch.tensor(spalten), kl)
        return aus.tolist()

    def test_1_hand_auf_dem_rumpf_ist_fremd(self):
        self.assertEqual(self.fremd(['Right_Hand', 'Left_Hand', 'Torso'], [0, 1, 0]), [True, True, False])

    def test_2_oberschenkel_auf_dem_gesaess_ist_erlaubt(self):
        self.assertEqual(self.fremd(['Left_Upper_Leg', 'Right_Upper_Leg'], [1, 2]), [False, False])

    def test_3_rechte_hand_auf_dem_linken_arm_ist_fremd(self):
        self.assertEqual(self.fremd(['Right_Hand', 'Left_Hand', 'Left_Lower_Arm'], [5, 5, 6]), [True, False, False])

    def test_4_keine_haut_ist_nie_fremd(self):
        self.assertEqual(self.fremd(['Upper_Clothing', 'Hair', None], [0, 0, 0]), [False, False, False])

    def test_5_fotohaut_ruft_dieselbe_regel(self):
        quelle = (Path(settings.TOOLS_ROOT) / 'mesh3dai' / 'mesh3dai_fotohaut_wahl.py').read_text(encoding='utf-8')
        self.assertIn('Kostuemfotofremd.fremd_je_texel(', quelle)


if __name__ == '__main__':
    unittest.main()
