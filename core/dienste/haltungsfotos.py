# -*- coding: utf-8 -*-
"""Haltungsfotos — die Haltung der Arme auf den Vorlagenfotos eines Laufs (01.10.2026), aus denselben Posenlandmarken
wie der Blickwinkel (`Fotolandmarken`, je Datei einmal gerechnet und abgelegt).

`fuer_lauf(z, referenzen)` schreibt `kreislauf.haltung_foto` = `Haltungsschaetzung.schaetzen` über die Fotos (dazu `ansichten`: `Haltungsschaetzung.je_foto` je Foto, für `Haltungsansichten`), die in
der Runde zählen (`Iterationsreferenz` — ein Foto, das die Fotoprüfung aussortiert hat, fehlt dort schon). Die Runde
gibt es im Befund weiter, `IterationModell.haltung` stellt danach Arme und Ellbogen; `G9haltungshaut` häutet Körper,
Kleider und Haar für Render und Note in diese Haltung. Ein Fehler des Wrappers hält den Lauf nicht auf — dann bleibt
die A-Pose.
"""

import json
import logging

from iterationen2d3d.haltungsschaetzung import Haltungsschaetzung

from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
from .fotolandmarken import Fotolandmarken

logger = logging.getLogger('core')

__all__ = ['Haltungsfotos']


class Haltungsfotos:
    FELD = 'haltung_foto'

    def __init__(self, job, ablage):
        self.job = job
        self.ablage = ablage

    def _drehungen(self):
        """`{datei: Grad}` — um wie viel der Schritt „Vorbereitung" jedes Foto gedreht hat (gegen den Uhrzeigersinn, `Ausrichtung`: `rotate(-grad)`); nur Fotos, deren vorbereitetes Bild es gibt (die Projektion liest dieses). Die Landmarken stammen vom
        ORIGINAL, die Fotohaut vom gedrehten Foto."""
        ordner = self.ablage.unter(Engine2d3dKleiderablage.VORBEREITET)
        try:
            daten = json.loads((ordner / 'vorbereitung.json').read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return {}
        aus = {}
        for b in daten.get('bilder') or []:
            a = b.get('ausrichtung') or {}
            if a.get('gedreht') and a.get('grad') and (ordner / (str(b.get('datei')).rsplit('.', 1)[0] + '.png')).is_file():
                aus[str(b['datei'])] = -float(a['grad'])
        return aus

    def fuer_lauf(self, z, referenzen):
        """`z` = `kreislauf`; → die Schätzung (oder None)."""
        try:
            eingang = self.ablage.unter(Engine2d3dKleiderablage.EINGANG)
            befunde = Fotolandmarken(self.ablage).holen([eingang / r.datei for r in referenzen])
            drehungen = self._drehungen()
            welt = {name: Haltungsschaetzung.gedreht(b['pose_welt'], drehungen.get(name, 0.0)) for name, b in befunde.items() if b.get('pose_welt')}   # im Rahmen des gedrehten Fotos
            haltung = Haltungsschaetzung.schaetzen(list(welt.values()))
        except (OSError, ValueError, RuntimeError, KeyError) as fehler:
            logger.warning('2D3D Kleider %s: Haltung der Fotos nicht geschätzt (%s)', self.job.kennung, fehler)
            haltung = None
        if haltung:
            haltung['fotos'] = sorted(befunde)
            haltung['ansichten'] = {name: Haltungsschaetzung.je_foto(punkte) for name, punkte in welt.items()}     # Glied für Glied je Foto (`Haltungsansichten`)
            haltung['drehung'] = drehungen
        z[self.FELD] = haltung
        return haltung
