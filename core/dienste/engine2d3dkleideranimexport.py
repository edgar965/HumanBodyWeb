# -*- coding: utf-8 -*-
"""Engine2d3dKleideranimexport — das fertige Modell eines Auftrags „2D3D Kleider" MIT Bewegung als GLB und Blender-Datei.

Edgar (01.10.2026): „Export als glb / blender inkl. animation". Der Knopf „Figur als GLB exportieren" nimmt die Figur
der Bühne (Grundfigur, ohne Kleider) und die Animation des Studios — beides nicht, was hier gemeint ist. Dieser Weg
nimmt das MODELL der besten Runde (`kreislauf.runde_bester` → `iterationen/runde_NNN_modell.glb`, Körper mit Rig,
Kleider, Haar) und die Bewegung des Schritts „film" (`ergebnis/film_bewegung.json`), schreibt sie als glTF-Animation hinein
(`G9glbanimation`) und lässt Blender daraus eine `.blend` machen (dasselbe Skript wie der Modellexport,
`effekte/blender/modellexportblend.py` — Bildrate und Bildbereich setzt es aus der Animation).

Ergebnis in `ergebnis/`: `modell_animiert.glb`, `modell_animiert.blend`; Bericht unter `job.ergebnis['animexport']`.
"""

import json
import logging
import subprocess

from django.conf import settings

from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleideranimexport']


class Engine2d3dKleideranimexport:
    GLB, BLEND, BEWEGUNG = 'modell_animiert.glb', 'modell_animiert.blend', 'film_bewegung.json'
    BLENDER_TIMEOUT_S = 300

    def __init__(self, job):
        self.job = job
        self.ablage = Engine2d3dKleiderablage(job.kennung)

    def quelle(self):
        """Pfad der Modell-GLB der besten Runde (sonst `ergebnis/modell.glb`) — oder None."""
        e = self.job.ergebnis or {}
        beste = int(((e.get('kreislauf') or {}).get('runde_bester')) or 0)
        if beste:
            pfad = self.ablage.iterationen('runde_%03d_modell.glb' % beste)
            if not pfad.is_file():                  # die Runden schreiben keine GLB mehr: einmal hier bauen
                from .begutachtungswerkzeug import Begutachtungswerkzeug
                Begutachtungswerkzeug(self.job, self.ablage).bestes_glb(e.get('kreislauf') or {}, 'modell.glb')
            if pfad.is_file():
                return pfad, beste
        pfad = self.ablage.ergebnis('modell.glb')
        return (pfad, None) if pfad.is_file() else (None, None)

    def ausfuehren(self, blend=True):
        """→ Bericht (Dict, geht als JSON hinaus und in `job.ergebnis['animexport']`)."""
        from Genesis9.glbanimation import G9glbanimation
        quelle, runde = self.quelle()
        if quelle is None:
            raise ValueError('Es gibt noch kein Modell — erst die Iterationen rechnen')
        bewegung_pfad = self.ablage.ergebnis(self.BEWEGUNG)
        if not bewegung_pfad.is_file():
            raise ValueError('Es gibt noch keine Bewegung — erst den Schritt „film" rechnen (BVH in den Optionen)')
        with open(bewegung_pfad, encoding='utf-8') as d:
            bewegung = json.load(d)
        glb = G9glbanimation(quelle)
        bericht = glb.einbauen(bewegung, name='tanz')
        ziel = self.ablage.ergebnis(self.GLB)
        bericht['glb'] = {'datei': self.GLB, 'bytes': glb.schreiben(ziel)}
        bericht.update(runde=runde, quelle=quelle.name)
        if blend:
            bericht['blend'] = self._blend(ziel, bewegung)
        # Dictionary gewollt: geht als JSON in die Antwort und in `job.ergebnis`.
        self.job.ergebnis = dict(self.job.ergebnis or {}, animexport=bericht)
        self.job.save(update_fields=['ergebnis', 'updated_at'])
        return bericht

    def _blend(self, glb, bewegung):
        ziel = self.ablage.ergebnis(self.BLEND)
        bilder = max(1, len(bewegung.get('times') or []))
        fps = round(bilder / float(bewegung.get('duration') or 1.0)) if bewegung.get('duration') else 30
        befehl = [str(settings.BLENDER_EXE), '-b', '--factory-startup', '--python',
                  str(settings.MODELLEXPORT_BLENDER_SKRIPT), '--', '--glb', str(glb), '--blend', str(ziel),
                  '--fps', str(int(fps)), '--polygone', '1.0']
        try:
            lauf = subprocess.run(befehl, capture_output=True, text=True, timeout=self.BLENDER_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            return {'fehler': 'Blender hat das Zeitlimit überschritten (%d s)' % self.BLENDER_TIMEOUT_S}
        if lauf.returncode != 0 or not ziel.is_file():
            logger.error('2D3D Kleider %s: Blender-Export gescheitert (%d): %s', self.job.kennung, lauf.returncode,
                         lauf.stderr[-2000:])
            return {'fehler': 'Blender konnte keine .blend schreiben (siehe Log)'}
        return {'datei': self.BLEND, 'bytes': ziel.stat().st_size, 'fps': int(fps)}
