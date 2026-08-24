# -*- coding: utf-8 -*-
"""GvhmrAusgabe — die Rendervideos eines GVHMR-Laufs in den Ausgabeordner legen.

Herausgeloest aus `core/pipelines/werkzeuge.py` (Befund `freie-funktionen`,
18.08.2026).

GVHMR schreibt seine Videos in einen Unterordner mit dem Namen des Videos
(`<ausgabe>/<videoname>/incam.mp4`, `global.mp4`, `incam_global_horiz.mp4`).
Der Nutzer erwartet sie aber dort, wo seine Videos liegen — deshalb werden sie
kopiert, nicht verschoben: Der Lauf soll seine eigenen Dateien behalten, falls
er sie noch braucht.

DABEI ENTFERNT (18.08.2026): Eine Liste `suffixes = ['incam.mp4', 'global.mp4',
'incam_global_horiz.mp4']` stand da und wurde NIE benutzt — kopiert wurde jede
`.mp4` im Ordner. Entweder war die Filterung gemeint und ist nie angeschlossen
worden, oder sie war ueberholt. Ich habe das jetzige Verhalten behalten (alle
MP4) und die tote Liste entfernt, statt eine Filterung einzufuehren, die seit
Monaten niemand hatte.
"""

import logging
import shutil
from pathlib import Path

from ..models import AppSettings

logger = logging.getLogger('core')


class GvhmrAusgabe:
    """Rendervideos eines Laufs in den eingestellten Ordner kopieren."""

    def __init__(self, job, ausgabeordner):
        self.job = job
        self.ausgabeordner = Path(ausgabeordner)

    @property
    def videostamm(self):
        return self.job.name.rsplit('.', 1)[0]

    def zielordner(self):
        """Auftragseigene Einstellung schlaegt die allgemeine — sonst `None`."""
        parameter = self.job.pipeline_params or {}
        gewaehlt = parameter.get('video_output_dir',
                                 AppSettings.load().video_output_dir)
        if not gewaehlt or not str(gewaehlt).strip():
            return None
        ziel = Path(gewaehlt)
        ziel.mkdir(parents=True, exist_ok=True)
        return ziel

    def kopieren(self):
        """Liefert die Zahl der kopierten Dateien."""
        ziel = self.zielordner()
        quelle = self.ausgabeordner / self.videostamm
        if ziel is None or not quelle.is_dir():
            return 0
        kopiert = 0
        for datei in quelle.iterdir():
            if datei.suffix != '.mp4':
                continue
            kopiert += self._kopieren(datei, ziel)
        return kopiert

    def _kopieren(self, datei, ziel):
        name = f'{self.videostamm}_{datei.stem}.mp4'
        try:
            shutil.copy2(str(datei), str(ziel / name))
            return 1
        except OSError as fehler:
            logger.warning('GVHMR video copy failed: %s', fehler)
            return 0
