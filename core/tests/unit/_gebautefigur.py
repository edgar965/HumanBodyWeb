# -*- coding: utf-8 -*-
"""Gebautefigur — eine echte gebaute Genesis-Figur als Grundlage der Tests von `KoerperKI_alle.Koerpernetz` und `Koerpermodell` (24.10.2026).

Quelle: die Figur des Foto-Genesis-Jobs EdgarTrip `3DObjects/fotogenesis/EdgarTrip/figur/form_maennlich` (bis 25.10.2026 16:17 der Mesh-Genesis-Test `_test/edgar_foto`, seither getrennt; Regler aus `modell.json`, Anzeigenetz, `kinematik.json`). Die drei Dateien werden in eine eigene
Ablage kopiert (`Pruefablage`), gelesen wird nur die Kopie. Fehlt die Figur, überspringt der Test. Die älteren Figuren unter `3DObjects/meshgenesis/` taugen nicht: Ursula1, Mann1 und Damira0
haben keine `modell.json`, und ihr Anzeigenetz weicht von der Formung ohne Regler um 25–47 mm ab (gemessen 24.10.2026, `ProjektTemp/_wegwerf/fotogenesis/koerpernetz_probe.py`).
Während eines Einpass-Laufs (`nurfotos_einpassen.py`) baut der Lauf diese Figur neu — dann nicht testen.
"""
import json
import shutil
import sys
import tempfile
from pathlib import Path

from django.conf import settings

from ._pruefablage import Pruefablage
import sys as _npz_sys  # noqa: E402
if r'A:\3DTools' not in _npz_sys.path:
    _npz_sys.path.append(r'A:\3DTools')
from KoerperKI_alle.npztorch import Npztorch  # noqa: E402

sys.path.insert(0, str(settings.TOOLS_ROOT))
sys.path.insert(0, str(settings.TOOLS_ROOT / 'meshgenesis'))


class Gebautefigur:
    QUELLE = Path(settings.TOOLS_ROOT) / '3DObjects' / 'fotogenesis' / 'EdgarTrip' / 'figur' / 'form_maennlich'
    DATEIEN = ('modell.json', 'kinematik.json', 'anzeige/netz.npz')

    @classmethod
    def da(cls):
        return all(Npztorch.da(cls.QUELLE / d) for d in cls.DATEIEN)

    @classmethod
    def kopieren(cls):
        """→ (Ordner der Kopie, Regler der Figur)."""
        ziel = Path(tempfile.mkdtemp(prefix='gebautefigur_', dir=Pruefablage.wurzel()))
        for d in cls.DATEIEN:
            (ziel / d).parent.mkdir(parents=True, exist_ok=True)
            Npztorch.kopieren(cls.QUELLE / d, ziel / d)
        return ziel, json.loads((ziel / 'modell.json').read_text(encoding='utf-8'))['figur']['regler']

    @staticmethod
    def weg(ordner):
        shutil.rmtree(ordner, ignore_errors=True)
