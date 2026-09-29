# -*- coding: utf-8 -*-
"""Kostuemblender — einen Stapel Kandidaten in EINEM Blender-Prozess bauen und rendern
(`effekte/blender/kostuembau.py`).

Der Körper wird je Prozess einmal geladen; jeder Kandidat baut nur das Kostüm neu. Blender läuft ohne Fenster
mit dem Werksprofil, als Kindprozess über `PipelineProzess` (Zeitgrenze für Schweigen von hier, `STILLE_S`).
Zwischendateien im Auftrag (`TMP`/`TEMP`), nie im System-Temp.
"""

import json
from pathlib import Path

from django.conf import settings

from ..atomic_write import AtomarSchreiber
from ..pipeline_process import PipelineProzess, PipelineStille

__all__ = ['Kostuemblender']


class Kostuemblender:
    SKRIPT = Path(settings.BASE_DIR) / 'effekte' / 'blender' / 'kostuembau.py'
    STILLE_S = 600
    BREITE, HOEHE = 256, 384

    def __init__(self, lauf):
        self.lauf = lauf
        self.ablage = lauf.ablage

    def rendern(self, koerper, aus, kandidaten, winkel, glb=False, blend=False, fortschritt=None, haltung=True):
        """`kandidaten`: [(name, parameter)] → `bericht.json` des Laufs (dict). Bilder unter `aus/<name>/`.
        `glb`: je Kandidat Figur + Kostüm + Rig; `haltung`: in der gestellten Haltung (sonst Ruhelage des Rigs)."""
        aus = Path(aus)
        aus.mkdir(parents=True, exist_ok=True)
        auftrag = {
            'koerper': str(koerper),
            'aus': str(aus),
            'breite': self.BREITE,
            'hoehe': self.HOEHE,
            'winkel': [float(w) for w in winkel],
            'glb': glb,
            'blend': blend,
            'haltung': haltung,
            'kandidaten': [{'name': n, 'parameter': p} for n, p in kandidaten],
        }
        pfad = aus / 'auftrag.json'
        AtomarSchreiber.json_schreiben(pfad, auftrag)
        befehl = [
            str(settings.BLENDER_EXE),
            '-b',
            '--factory-startup',
            '--python',
            str(self.SKRIPT),
            '--',
            '--auftrag',
            str(pfad),
        ]
        tmp = self.ablage.arbeit('tmp')
        tmp.mkdir(parents=True, exist_ok=True)
        pp = PipelineProzess.starten(
            befehl,
            cwd=str(self.SKRIPT.parent),
            env_extra={'TMP': str(tmp), 'TEMP': str(tmp), 'PYTHONIOENCODING': 'utf-8'},
        )
        try:
            for zeile in pp.stdout_zeilen(stille_timeout=self.STILLE_S):
                zeile = zeile.rstrip('\n')
                if zeile.startswith('Kostuem: ') and fortschritt:
                    fortschritt(zeile[9:])
                if self.lauf.angehalten():
                    pp.beenden()
                    raise self.lauf.Angehalten()
        except PipelineStille as fehler:
            pp.beenden()
            raise RuntimeError('Blender schweigt (%s)' % fehler) from fehler
        rc = pp.warten(timeout=120)
        bericht = aus / 'bericht.json'
        if rc != 0 or not bericht.is_file():
            raise RuntimeError(pp.fehlertext(1500) or 'Blender endete mit %s' % rc)
        with open(bericht, encoding='utf-8') as f:
            return json.load(f)
