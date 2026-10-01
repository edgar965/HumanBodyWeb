# -*- coding: utf-8 -*-
"""Haltungsfotos — die Haltung der Arme auf den Vorlagenfotos eines Laufs (01.10.2026), aus denselben Posenlandmarken
wie der Blickwinkel (`Fotolandmarken`, je Datei einmal gerechnet und abgelegt).

`fuer_lauf(z, referenzen)` schreibt `kreislauf.haltung_foto` = `Haltungsschaetzung.schaetzen` über die Fotos, die in
der Runde zählen (`Iterationsreferenz` — ein Foto, das die Fotoprüfung aussortiert hat, fehlt dort schon). Die Runde
gibt es im Befund weiter, `IterationModell.haltung` stellt danach Arme und Ellbogen; `G9haltungshaut` häutet Körper,
Kleider und Haar für Render und Note in diese Haltung. Ein Fehler des Wrappers hält den Lauf nicht auf — dann bleibt
die A-Pose.
"""

import logging

from iterationen2d3d.haltungsschaetzung import Haltungsschaetzung

from ..daten.haarengineablage import Haarengineablage
from .fotolandmarken import Fotolandmarken

logger = logging.getLogger('core')

__all__ = ['Haltungsfotos']


class Haltungsfotos:
    FELD = 'haltung_foto'

    def __init__(self, job, ablage):
        self.job = job
        self.ablage = ablage

    def fuer_lauf(self, z, referenzen):
        """`z` = `kreislauf`; → die Schätzung (oder None)."""
        try:
            eingang = self.ablage.unter(Haarengineablage.EINGANG)
            befunde = Fotolandmarken(self.ablage).holen([eingang / r.datei for r in referenzen])
            fotos = [b['pose_welt'] for b in befunde.values() if b.get('pose_welt')]
            haltung = Haltungsschaetzung.schaetzen(fotos)
        except (OSError, ValueError, RuntimeError, KeyError) as fehler:
            logger.warning('2D3D Kleider %s: Haltung der Fotos nicht geschätzt (%s)', self.job.kennung, fehler)
            haltung = None
        if haltung:
            haltung['fotos'] = sorted(befunde)
        z[self.FELD] = haltung
        return haltung
