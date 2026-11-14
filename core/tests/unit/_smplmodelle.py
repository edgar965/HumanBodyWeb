# -*- coding: utf-8 -*-
"""Smplmodelle — die SMPL-Modelldateien für eine Prüfung, oder Übersprung.

Zwei Testklassen in `test_smplkoerper` hielten denselben `setUpClass`
(Befund `doppelrumpf`, 12.09.2026): Modellordner merken, prüfen, ob
`SMPL_FEMALE.npz` und `SMPL_MALE.npz` liegen. Hier steht er einmal; die
Klassen erben ihn und fragen `self.modell(geschlecht)`, das überspringt,
wenn die Dateien fehlen — ein fehlender Datensatz soll nicht grün sein.
"""

import os

from django.conf import settings
import sys as _npz_sys  # noqa: E402
if r'A:\3DTools' not in _npz_sys.path:
    _npz_sys.path.append(r'A:\3DTools')
from KoerperKI_alle.npztorch import Npztorch  # noqa: E402


class Smplmodelle:
    """Mixin für `unittest.TestCase`: `modelle`, `vorhanden`, `modell()`."""

    GESCHLECHTER = ('female', 'male')

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.modelle = str(settings.SMPL_MODELS_DIR)
        cls.vorhanden = all(
            Npztorch.da(os.path.join(cls.modelle, 'SMPL_%s.npz' % g.upper())) for g in cls.GESCHLECHTER
        )

    def modell(self, geschlecht):
        """Das geladene `Smplkoerper`-Modell — oder `skipTest`."""
        if not self.vorhanden:
            self.skipTest('SMPL-Modelldateien nicht vorhanden')
        from GarmentCode.smplkoerper import Smplkoerper

        return Smplkoerper.laden(geschlecht, self.modelle)
