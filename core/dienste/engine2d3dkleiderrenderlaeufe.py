# -*- coding: utf-8 -*-
"""Engine2d3dKleiderrenderlaeufe — die Render-Läufe eines Auftrags „2D3D Kleider" als eigene Liste (04.10.2026).

Edgar: „als nächstes, iterativ — evtl. mit getrenntem Abschnitt — die Render jobs. Rendere erstmal nur 10 Frames und verbessere die Qualität … wenn
die ersten 10 Frames gut sind, nimm 30, und dann das ganze BVH." Jeder abgeschlossene Lauf bekommt eine Nummer und bleibt: sein Video als
`ergebnis/render_lauf_NNN.mp4`, ein Bogen mit vier Bildern daraus als `ergebnis/render_lauf_NNN.png` (flach in `ergebnis/`, damit die Datei-
Schnittstelle sie ausliefert) und ein Eintrag in `arbeit/render/laeufe.json` mit dem, was den Lauf ausmacht: Bilder, Größe, Proben je Pixel,
Dauer, Anmerkung (was gegenüber dem Lauf davor geändert wurde). `ergebnis/render_video.mp4` ist weiter der jüngste.

Der Zustand des Auftrags trägt die letzten `ANZEIGE` Läufe (`render.laeufe`, neueste zuerst); die Seite zeigt sie als Tabelle.
"""

import json
import logging
import shutil
import subprocess
import time

__all__ = ['Engine2d3dKleiderrenderlaeufe']

logger = logging.getLogger('core')


class Engine2d3dKleiderrenderlaeufe:
    DATEI = 'laeufe.json'
    ANZEIGE = 30
    FFMPEG = r'A:\archiv2\_AI\tools\ffmpeg.exe'
    BOGEN_BILDER = 4
    BOGEN_BREITE = 320

    def __init__(self, render):
        self.render = render
        self.pfad = render._datei(self.DATEI)

    def lesen(self):
        try:
            return json.loads(self.pfad.read_text(encoding='utf-8')) if self.pfad.is_file() else []
        except (OSError, ValueError) as fehler:
            logger.warning('2D3D Kleider %s: render/%s nicht lesbar (%s)', self.render.job.kennung, self.DATEI, fehler)
            return []

    def neueste(self):
        """Die letzten `ANZEIGE` Läufe, der jüngste zuerst (für die Seite)."""
        return list(reversed(self.lesen()))[:self.ANZEIGE]

    def _bogen(self, video, ziel, sekunden):
        """Vier Bilder des Videos nebeneinander als PNG. → True, wenn die Datei da ist."""
        befehl = [self.FFMPEG, '-y', '-v', 'error', '-i', str(video), '-vf', 'fps=%.4f,scale=%d:-1,tile=%dx1' % (
            self.BOGEN_BILDER / max(sekunden, 0.1), self.BOGEN_BREITE, self.BOGEN_BILDER), '-frames:v', '1', str(ziel)]
        try:
            subprocess.run(befehl, check=True, timeout=120)
        except (OSError, subprocess.SubprocessError) as fehler:
            logger.warning('2D3D Kleider %s: Bogen des Render-Laufs nicht erzeugt (%s)', self.render.job.kennung, fehler)
        return ziel.is_file()

    def eintragen(self, auftrag, video, dauer_s):
        """Den fertigen Lauf ablegen: Video und Bogen mit Nummer in `ergebnis/`, Eintrag in `laeufe.json`. → der Eintrag."""
        laeufe = self.lesen()
        nr = max([int(e.get('nr') or 0) for e in laeufe] + [0]) + 1
        name = 'render_lauf_%03d' % nr
        ablage = self.render.ablage
        kopie = ablage.ergebnis(name + '.mp4')
        shutil.copyfile(video, kopie)
        sekunden = float(auftrag['sekunden'])
        eintrag = {
            'nr': nr, 'zeit': time.strftime('%Y-%m-%d %H:%M:%S'), 'bilder': int(round(sekunden * self.render.FPS)), 'sekunden': sekunden,
            'groesse': '%dx%d' % (auftrag['breite'], auftrag['hoehe']), 'kamera': auftrag['kamera'], 'spp': int(auftrag.get('spp') or 48),
            'licht': auftrag.get('licht') or 'studio', 'ton': bool(auftrag.get('ton')), 'dauer_s': round(dauer_s, 1),
            'bytes': kopie.stat().st_size, 'video': kopie.name, 'anmerkung': str(auftrag.get('anmerkung') or '')[:600],
        }
        if self._bogen(kopie, ablage.ergebnis(name + '.png'), sekunden):
            eintrag['blatt'] = name + '.png'
        laeufe.append(eintrag)
        zwischen = self.pfad.with_name(self.DATEI + '.teil')
        zwischen.write_text(json.dumps(laeufe, ensure_ascii=False, indent=1), encoding='utf-8')
        zwischen.replace(self.pfad)
        return eintrag
