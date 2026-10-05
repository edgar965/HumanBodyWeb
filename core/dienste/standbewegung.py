# -*- coding: utf-8 -*-
"""Standbewegung — die BVH-Bewegung auf der Figur des Auftrags, sobald es eine Figur gibt (04.10.2026).

Edgar: „play der animation im 3Dview nicht verfügbar, Render einstellungen usw" — an einem Auftrag, der bis „Kleiderstücke" gerechnet war. Die Bühne spielt die Bewegung nur ab, wenn
`ergebnis.film.bewegung` steht (`Engine2d3dKleideranimation._pruefen`), und die schrieb bisher nur der Schritt „film" (`Engine2d3dKleiderfilm`) — ganz am Ende, nach den Iterationen und
dem Export. Die Bewegung selbst braucht aber nur die Stellung der Figur und die BVH-Datei (`Engine2d3dKleiderbewegung`, CPU, im Arbeitsprozess); der Film der Engine ist erst der Teil danach.

Diese Klasse rechnet sie schon nach der Figur (Körper, Grundfigur, Kleiderstücke) und legt sie so ab, wie der Film-Schritt es tut: `ergebnis/film_bewegung.json` und `ergebnis.film`
(`bewegung`, `bvh`, `bewegung_bilder`). Was der Film-Schritt dort schon abgelegt hat (Video, Bilder, Bildrate), bleibt stehen. Der Film-Schritt rechnet die Bewegung weiter selbst neu.

Zum Rechnen gehört ein Fingerabdruck (`bewegung_stand`: BVH-Datei samt Änderungszeit, Stellung, Körperhöhe): Ist er gleich, bleibt die Datei, wie sie ist.
"""

import hashlib
import json
import logging
import os
import shutil

from .engine2d3dkleiderbewegung import Engine2d3dKleiderbewegung
from .engine2d3dkleideroptionen import Engine2d3dKleideroptionen

logger = logging.getLogger('core')

__all__ = ['Standbewegung']


class Standbewegung:
    ORDNER = 'film'
    BEWEGUNG = 'film_bewegung.json'

    def __init__(self, job, ablage):
        self.job = job
        self.ablage = ablage

    def bvh(self):
        """Pfad der BVH-Datei aus den Optionen („Film → BVH-Datei") — leer, wenn keine gewählt ist oder es sie nicht gibt."""
        pfad = str(Engine2d3dKleideroptionen.film(self.job.optionen).get('bvh') or '').strip()
        return pfad if pfad.lower().endswith('.bvh') and os.path.isfile(pfad) else ''

    def fingerabdruck(self, bvh):
        roh = json.dumps([bvh, os.stat(bvh).st_mtime_ns, self.job.stellung(), (self.job.optionen.get('figur') or {}).get('hoehe_cm')],
                         sort_keys=True, default=str)
        return hashlib.md5(roh.encode('utf-8')).hexdigest()[:12]

    def sichern(self):
        """Die Bewegung rechnen und ablegen → True, wenn `ergebnis.film` sich geändert hat (der Aufrufer speichert `ergebnis`). Ohne Figur oder BVH: False, nichts geschieht."""
        bvh = self.bvh()
        if not bvh or not self.job.stellung():
            return False
        stand = self.fingerabdruck(bvh)
        film = dict((self.job.ergebnis or {}).get('film') or {})
        if film.get('bewegung_stand') == stand and self.ablage.ergebnis(self.BEWEGUNG).is_file():
            return False
        aus = self.ablage.arbeit(self.ORDNER)
        aus.mkdir(parents=True, exist_ok=True)
        pfad, bewegung = Engine2d3dKleiderbewegung(self).rechnen(bvh, aus)
        shutil.copyfile(pfad, self.ablage.ergebnis(self.BEWEGUNG))
        film.pop('uebersprungen', None)             # „Keine BVH-Datei gewählt" eines früheren Laufs gilt nicht mehr
        film.update(bewegung=self.BEWEGUNG, bvh=bvh, bewegung_bilder=bewegung.frame_count, bewegung_stand=stand)
        self.job.ergebnis = dict(self.job.ergebnis or {}, film=film)
        logger.info('2D3D Kleider %s: Bewegung %s auf der Figur (%d Bilder)', self.job.kennung, os.path.basename(bvh), bewegung.frame_count)
        return True
