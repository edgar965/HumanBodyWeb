# -*- coding: utf-8 -*-
"""Haarenginefilm — Schritt „film" von „Haar Engine": GLB + BVH → Genesis Haar Engine → Video
(30.09.2026).

Ersetzt den Schritt „blender" von BlenderModel: Dort rechnete ein Blender-Prozess (Figur laden, BVH
auflegen, rendern); hier ruft der Schritt die Genesis Haar Engine (`Genesishaarengine.film`). Alles
davor ist unverändert:

    1. die BVH-Datei aus der Option `film.bvh` auf Genesis 9 retargeten (`Haarenginebewegung`, im Django-Prozess)
    2. die Bewegung als `ergebnis/film_bewegung.json` ablegen und SOFORT im Auftrag vermerken — die Bühne spielt sie live auf der
       Figur ab (`Haarengineanimation`), auch wenn die Engine den Film noch nicht rechnet
    3. die Engine rendert den Film: Figur mit Rig (`ergebnis/figur.glb`, Schritt „export") und, wenn die Iterationen ein Modell
       geliefert haben, das Haar (`ergebnis/haar.glb`); Video als `ergebnis/film_video.mp4`

Ohne BVH-Datei wird der Schritt mit einer Meldung übersprungen — die Figur ist dann trotzdem fertig, nur
ohne Bewegung. Die Zahlen stehen unter `job.ergebnis['film']`; gerechnet wird in `arbeit/film/`.
"""

import os
import shutil

from .genesishaarengine import Genesishaarengine
from .haarenginebewegung import Haarenginebewegung
from .haarengineoptionen import Haarengineoptionen

__all__ = ['Haarenginefilm']


class Haarenginefilm:
    ORDNER = 'film'
    #: `bewegung` liegt in `ergebnis/` (nicht nur unter `arbeit/`, das der Datei-Endpunkt nicht ausliefert —
    #: `Haarengineablage.LESBAR`): Die Bühne spielt die Bewegung live auf dem Genesis-9-Modell ab.
    VIDEO, BEWEGUNG = 'film_video.mp4', 'film_bewegung.json'

    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage
        self.optionen = Haarengineoptionen.film(self.job.optionen)

    def haarmodell(self):
        """`ergebnis/haar.glb` der Iterationen (Figur + Haar am Rig) oder None."""
        name = (self.job.ergebnis.get('kreislauf') or {}).get('glb')
        pfad = self.ablage.ergebnis(name) if name else None
        return pfad if pfad is not None and pfad.is_file() else None

    def ausfuehren(self):
        bvh = str(self.optionen.get('bvh') or '').strip()
        if not bvh:
            self.job.ergebnis['film'] = {'uebersprungen': 'Keine BVH-Datei gewählt'}
            self.lauf.melden(1.0, 'Film übersprungen: keine BVH-Datei')
            return
        if not (os.path.isfile(bvh) and bvh.lower().endswith('.bvh')):
            raise RuntimeError('BVH-Datei nicht gefunden: %s' % bvh)
        glb = self.ablage.ergebnis((self.job.ergebnis.get('export') or {}).get('datei') or 'figur.glb')
        if not glb.is_file():
            raise RuntimeError('Keine GLB mit Rig — erst der Schritt „export"')
        aus = self.ablage.arbeit(self.ORDNER)
        aus.mkdir(parents=True, exist_ok=True)
        self.lauf.melden(0.02, 'Bewegung wird auf Genesis 9 gerechnet')
        bewegung_pfad, bewegung = Haarenginebewegung(self.lauf).rechnen(bvh, aus)
        shutil.copyfile(bewegung_pfad, self.ablage.ergebnis(self.BEWEGUNG))
        # Die Bewegung steht jetzt fest: Sie wird gespeichert, bevor die Engine rechnet (scheitert sie, bleibt sie sichtbar).
        self.job.ergebnis['film'] = {
            'bewegung': self.BEWEGUNG,
            'bvh': bvh,
            'bewegung_bilder': bewegung.frame_count,
        }
        self.lauf.sichern('ergebnis')
        self.lauf.melden(0.1, 'Die Haar Engine rendert den Film')
        o = self.optionen
        bericht = Genesishaarengine(self.lauf).film(
            glb,
            bewegung_pfad,
            aus,
            int(o['bilder']),
            int(o['breite']),
            int(o['hoehe']),
            haarmodell=self.haarmodell(),
            fortschritt=lambda text: self.lauf.melden(0.5, text),
        )
        video = bericht.get('video')
        if video and (aus / video).is_file():
            shutil.copyfile(aus / video, self.ablage.ergebnis(self.VIDEO))
        self.job.ergebnis['film'].update(
            video=self.VIDEO if video else '',
            bilder=bericht.get('bilder', 0),
            bildrate=bericht.get('bildrate', 0),
            sekunden=bericht.get('sekunden'),
            bildnummern=bericht.get('bildnummern'),
            teile=bericht.get('teile'),
        )
        self.lauf.melden(
            1.0, 'Film: %d Bilder bei %d fps' % (bericht.get('bilder', 0), bericht.get('bildrate', 0))
        )
        return bericht
