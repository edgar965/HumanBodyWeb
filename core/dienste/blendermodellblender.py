# -*- coding: utf-8 -*-
"""Blendermodellblender — Schritt „blender" von „BlenderModel": GLB + BVH → Blender → Video (29.09.2026).

Blender läuft als eigener Prozess ohne Fenster mit dem Werksprofil (`effekte/blender/blendermodell.py`):
Figur laden, BVH retargeten (BVH Retargeter, Rig „Genesis 9"), rendern. Seine Zeilen `Blendermodel: …`
und `Effekte: Rendern Bild n von N` werden zum Fortschritt; am Ende liest der Schritt `bericht.json`
und legt Video und `.blend` unter festen Namen nach `ergebnis/` (`blender_video.mp4`, `blender_figur.blend`),
die Zahlen unter `job.ergebnis['blender']`. Gerechnet wird in `arbeit/blender/`.

Die Optionen kommen aus der Gruppe `blender` (`Blendermodellblenderoptionen`): BVH-Datei, Bilder, Größe,
Renderer. Ohne BVH-Datei wird der Schritt mit einer Meldung übersprungen — die Figur ist dann trotzdem
fertig, nur ohne Bewegung.
"""

import json
import os
import re
import shutil
from pathlib import Path

from django.conf import settings

from ..pipeline_process import PipelineProzess, PipelineStille
from .blendermodellbewegung import Blendermodellbewegung
from .blendermodelloptionen import Blendermodelloptionen

__all__ = ['Blendermodellblender']


class Blendermodellblender:
    SKRIPT = Path(settings.BASE_DIR) / 'effekte' / 'blender' / 'blendermodell.py'
    ORDNER = 'blender'
    #: `bewegung` liegt zusätzlich hier (nicht nur unter `arbeit/`, das der Datei-Endpunkt nicht
    #: ausliefert — `Blendermodellablage.LESBAR`): Die Bühne spielt die Bewegung LIVE auf dem
    #: Genesis-9-Modell ab (`Blendermodellanimation`, dieselbe `THREE.AnimationMixer`-Kette wie das
    #: BVH-Studio), statt nur das gebackene Video zu zeigen (Edgar, 29.09.2026: „Play soll im
    #: Hauptausgabefenster funktionieren").
    VIDEO, BLEND, BEWEGUNG = 'blender_video.mp4', 'blender_figur.blend', 'blender_bewegung.json'
    #: So lange darf Blender schweigen (ein Renderbild).
    STILLE_S = 600
    RENDERZEILE = re.compile(r'Rendern Bild (\d+) von (\d+)')

    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage
        self.optionen = Blendermodelloptionen.blender(self.job.optionen)

    def befehl(self, glb, bewegung, aus):
        o = self.optionen
        return [str(settings.BLENDER_EXE), '-b', '--factory-startup', '--python', str(self.SKRIPT), '--',
                '--glb', str(glb), '--bewegung', str(bewegung), '--aus', str(aus), '--bilder', str(o['bilder']),
                '--breite', str(o['breite']), '--hoehe', str(o['hoehe']), '--renderer', str(o['renderer'])]

    def ausfuehren(self):
        bvh = str(self.optionen.get('bvh') or '').strip()
        if not bvh:
            self.job.ergebnis['blender'] = {'uebersprungen': 'Keine BVH-Datei gewählt'}
            self.lauf.melden(1.0, 'Blender übersprungen: keine BVH-Datei')
            return
        if not (os.path.isfile(bvh) and bvh.lower().endswith('.bvh')):
            raise RuntimeError('BVH-Datei nicht gefunden: %s' % bvh)
        glb = self.ablage.ergebnis((self.job.ergebnis.get('export') or {}).get('datei') or 'figur.glb')
        if not glb.is_file():
            raise RuntimeError('Keine GLB mit Rig — erst der Schritt „export"')
        aus = self.ablage.arbeit(self.ORDNER)
        aus.mkdir(parents=True, exist_ok=True)
        self.lauf.melden(0.02, 'Bewegung wird auf Genesis 9 gerechnet')
        bewegung_pfad, bewegung = Blendermodellbewegung(self.lauf).rechnen(bvh, aus)
        shutil.copyfile(bewegung_pfad, self.ablage.ergebnis(self.BEWEGUNG))
        self.lauf.melden(0.1, 'Blender startet')
        bericht = self._blender(self.befehl(glb, bewegung_pfad, aus), aus)
        for quelle, ziel in ((bericht.get('video'), self.VIDEO), (bericht.get('blend'), self.BLEND)):
            if quelle and (aus / quelle).is_file():
                shutil.copyfile(aus / quelle, self.ablage.ergebnis(ziel))
        bericht['video'] = self.VIDEO if bericht.get('video') else ''
        bericht['blend'] = self.BLEND if bericht.get('blend') else ''
        bericht['bewegung'] = self.BEWEGUNG
        bericht['bvh'] = bvh
        bericht['bewegung_bilder'] = bewegung.frame_count
        self.job.ergebnis['blender'] = bericht
        self.lauf.melden(1.0, 'Video: %d Bilder bei %d fps' % (bericht.get('bilder', 0), bericht.get('bildrate', 0)))
        return bericht

    def _blender(self, befehl, aus):
        tmp = self.ablage.arbeit('tmp')
        tmp.mkdir(parents=True, exist_ok=True)
        pp = PipelineProzess.starten(befehl, cwd=str(self.SKRIPT.parent),
                                     env_extra={'TMP': str(tmp), 'TEMP': str(tmp), 'PYTHONIOENCODING': 'utf-8'})
        try:
            for zeile in pp.stdout_zeilen(stille_timeout=self.STILLE_S):
                zeile = zeile.rstrip('\n')
                if zeile.startswith('Blendermodel: '):
                    self.lauf.melden(0.1 if 'Retarget' in zeile else 0.3, zeile[14:])
                treffer = self.RENDERZEILE.search(zeile)
                if treffer:
                    n, gesamt = int(treffer.group(1)), max(1, int(treffer.group(2)))
                    self.lauf.melden(0.3 + 0.65 * n / gesamt, 'Rendern Bild %d von %d' % (n, gesamt))
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
