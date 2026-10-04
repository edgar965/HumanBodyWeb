# -*- coding: utf-8 -*-
"""Engine2d3dKleiderreferenz — das Referenzvideo eines Auftrags „2D3D Kleider": ein fremdes Ergebnis (zum Beispiel Franks Blender-Video), mit dem der Nutzer den Film vergleicht (04.10.2026).

Edgar: „füge franks ergebnis video rechts neben den Vorlagebildern als Frame ein, mit play soll ich das abspielen können" (Datei `Model_Jobs/Frank/Randy/vid2.mp4`).
Der Nutzer nennt den Pfad einer Videodatei; der Server kopiert sie nach `referenz/<name>` im Auftragsordner (nur dort liefert der Datei-Endpunkt sie aus) und merkt sich Name und
Quelle in `arbeit/referenz.json`. Die Seite zeigt das Video neben den Vorlagebildern; der Zustand des Auftrags trägt `referenz` (`bericht()`).
"""

import json
import logging
import re
import shutil
from pathlib import Path

from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleiderreferenz']


class Engine2d3dKleiderreferenz:
    DATEI = 'referenz.json'
    ENDUNGEN = ('.mp4', '.webm', '.mov', '.m4v')

    def __init__(self, job):
        self.job = job
        self.ablage = Engine2d3dKleiderablage(job.kennung)

    def _merkdatei(self):
        return self.ablage.arbeit(self.DATEI)

    def bericht(self):
        """`{video, quelle, bytes}` — `video` ist None, solange keines übernommen ist oder die Kopie fehlt."""
        pfad = self._merkdatei()
        try:
            stand = json.loads(pfad.read_text(encoding='utf-8')) if pfad.is_file() else {}
        except (OSError, ValueError) as fehler:
            logger.warning('2D3D Kleider %s: arbeit/%s nicht lesbar (%s)', self.job.kennung, self.DATEI, fehler)
            stand = {}
        name = str(stand.get('video') or '')
        kopie = self.ablage.referenz(name) if name else None
        if kopie is None or not kopie.is_file():
            return {'video': None, 'quelle': str(stand.get('quelle') or ''), 'bytes': 0}
        return {'video': name, 'quelle': str(stand.get('quelle') or ''), 'bytes': kopie.stat().st_size}

    def uebernehmen(self, quelle):
        """Die Videodatei `quelle` nach `referenz/` kopieren und merken. → `bericht()`; `ValueError` mit der Meldung für die Seite."""
        text = str(quelle or '').strip().strip('"')
        if not text:
            raise ValueError('Pfad des Videos fehlt')
        pfad = Path(text)
        if not pfad.is_file():
            raise ValueError('Datei nicht gefunden: %s' % text)
        if pfad.suffix.lower() not in self.ENDUNGEN:
            raise ValueError('Kein Video (%s): %s' % (', '.join(self.ENDUNGEN), pfad.name))
        name = re.sub(r'[^A-Za-z0-9._-]+', '_', pfad.name)
        ziel = self.ablage.referenz(name)
        ziel.parent.mkdir(parents=True, exist_ok=True)
        if not ziel.is_file() or ziel.stat().st_size != pfad.stat().st_size or ziel.stat().st_mtime < pfad.stat().st_mtime:
            shutil.copyfile(pfad, ziel)
        zwischen = self._merkdatei().with_name(self.DATEI + '.teil')
        zwischen.parent.mkdir(parents=True, exist_ok=True)
        zwischen.write_text(json.dumps({'video': name, 'quelle': str(pfad)}, ensure_ascii=False, indent=1), encoding='utf-8')
        zwischen.replace(self._merkdatei())
        return self.bericht()
