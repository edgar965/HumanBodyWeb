# -*- coding: utf-8 -*-
"""Gebautefigur — eine echte gebaute Genesis-Figur als Grundlage der Tests von `KoerperKI_alle.Koerpernetz` und `Koerpermodell` (24.10.2026).

Quelle: die Figur des 2d-3d-AI-Jobs EdgarTrip `3DObjects/ai2d3d/EdgarTrip/figur/form_maennlich` (bis 25.10.2026 16:17 der Mesh3D-AI-Test `_test/edgar_foto`, seither getrennt; Regler aus `modell.json`, Anzeigenetz, `kinematik.json`). Die drei Dateien werden in eine eigene
Ablage kopiert (`Pruefablage`), gelesen wird nur die Kopie. Fehlt die Figur, überspringt der Test. Die älteren Figuren unter `3DObjects/mesh3dai/` taugen nicht: Ursula1, Mann1 und Damira0
haben keine `modell.json`, und ihr Anzeigenetz weicht von der Formung ohne Regler um 25–47 mm ab (gemessen 24.10.2026, `ProjektTemp/_wegwerf/ai2d3d/koerpernetz_probe.py`).
Während eines Einpass-Laufs (`nurfotos_einpassen.py`) baut der Lauf diese Figur neu — dann nicht testen.
"""
import json
import shutil
import sys
import tempfile
from pathlib import Path

from django.conf import settings

from ._pruefablage import Pruefablage

sys.path.insert(0, str(settings.TOOLS_ROOT))
sys.path.insert(0, str(settings.TOOLS_ROOT / 'mesh3dai'))


class Gebautefigur:
    QUELLE = Path(settings.TOOLS_ROOT) / '3DObjects' / 'ai2d3d' / 'EdgarTrip' / 'figur' / 'form_maennlich'
    DATEIEN = ('modell.json', 'kinematik.json', 'anzeige/netz.npz')

    @classmethod
    def da(cls):
        return all((cls.QUELLE / d).is_file() for d in cls.DATEIEN)

    @classmethod
    def kopieren(cls):
        """→ (Ordner der Kopie, Regler der Figur)."""
        ziel = Path(tempfile.mkdtemp(prefix='gebautefigur_', dir=Pruefablage.wurzel()))
        for d in cls.DATEIEN:
            (ziel / d).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(cls.QUELLE / d, ziel / d)
        return ziel, json.loads((ziel / 'modell.json').read_text(encoding='utf-8'))['figur']['regler']

    @staticmethod
    def weg(ordner):
        shutil.rmtree(ordner, ignore_errors=True)
