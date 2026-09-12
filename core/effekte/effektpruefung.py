# -*- coding: utf-8 -*-
u"""Effektpruefung — darf ein Effektauftrag so starten?

Herausgeloest aus `Effektendpunkte._pruefen` (12.09.2026), als die zweite
Pipeline kam. Je Pipeline gilt anderes:

    kleid_wind  BVH mit SMPL-Gelenken (der Blender-Retargeter kennt nur
                die), ein Kleid aus der Bibliothek, `Effektparameter`.
    figur_def   BVH in einem Format, das der Retarget der Web-App erkennt
                (CMU, Mixamo, MocapNET, OpenPose, SMPL/AIST …), ein
                gespeichertes Modell, `Figurparameter`.

Die BVH kommt entweder als Pfad (Auftraege aus „Process Videos") oder als
Bibliotheksadresse `/api/character/bvh/<kategorie>/<name>/` (der
Animationsbrowser) — `bvh_pfad()` macht daraus den Pfad, ueber dieselbe
Pruefung wie der Videoweg der Szene (`Figurvideo._bvh_pfad`).
"""
import os

from effekte.bvhnamen import Bvhnamen
from effekte.effektparameter import Effektparameter
from effekte.figurparameter import Figurparameter
from ..dienste.modellvorlagen import Modellvorlagen
from ..models import Effektauftrag
from .effektquellen import Effektquellen

__all__ = ['Effektpruefung']


class Effektpruefung:

    BIBLIOTHEK = '/api/character/bvh/'

    def __init__(self, daten):
        self.daten = daten
        self.pipeline = daten.get('pipeline') or 'kleid_wind'
        self.bvh = ''

    @property
    def mit_modell(self):
        return self.pipeline in Effektauftrag.MIT_MODELL

    # -------------------------------------------------------------- Pruefen

    def grund(self):
        u"""Der Grund, warum der Auftrag nicht starten darf — oder `''`."""
        if dict(Effektauftrag.PIPELINE_CHOICES).get(self.pipeline) is None:
            return 'Unbekannte Pipeline'
        try:
            self.bvh = self.bvh_pfad(self.daten.get('bvh'))
        except ValueError as e:
            return str(e)
        ausgabe = self.daten.get('ausgabe') or ''
        if not ausgabe.lower().endswith('.mp4'):
            return 'Ausgabedatei muss auf .mp4 enden'
        if self.mit_modell:
            return self._figur(ausgabe)
        return self._kleid(ausgabe)

    def _kleid(self, ausgabe):
        unbekannt = Bvhnamen.lesen(self.bvh).unbekannte()
        if unbekannt:
            return 'BVH mit unbekannten Gelenken (%s …)' % unbekannt[0]
        kleid = self.daten.get('kleid')
        if not kleid or not os.path.isfile(kleid):
            return 'Kleid fehlt: %s' % (kleid,)
        return self._parameter(Effektparameter, bvh=self.bvh, kleid=kleid,
                               ausgabe=ausgabe)

    def _figur(self, ausgabe):
        format_ = Effektquellen.format(Bvhnamen.lesen(self.bvh).gelenke())
        if not format_:
            return ('BVH-Format nicht erkannt (%s) — der Retarget kennt CMU, '
                    'Mixamo, MocapNET, OpenPose, Bandai und SMPL'
                    % os.path.basename(self.bvh))
        modell = self.daten.get('modell') or ''
        pfad = Modellvorlagen.pfad(modell)
        if pfad is None:
            return 'Modell fehlt: %s' % (modell or '(keins gewählt)')
        return self._parameter(Figurparameter, modell=str(pfad), bvh=self.bvh,
                               ausgabe=ausgabe)

    def _parameter(self, klasse, **pflicht):
        try:
            klasse(**pflicht, **(self.daten.get('parameter') or {}))
        except (ValueError, TypeError) as e:
            return 'Parameter: %s' % e
        return ''

    # ------------------------------------------------------------------ BVH

    @classmethod
    def bvh_pfad(cls, angabe):
        u"""Pfad oder Bibliotheksadresse -> vorhandene Datei, sonst `ValueError`."""
        angabe = (angabe or '').strip()
        if not angabe:
            raise ValueError('Keine BVH gewählt')
        if angabe.startswith(cls.BIBLIOTHEK):
            from ..dienste.figurvideo import Figurvideo
            return Figurvideo._bvh_pfad(angabe)
        if not os.path.isfile(angabe):
            raise ValueError('BVH-Datei fehlt: %s' % angabe)
        return angabe

    # -------------------------------------------------------------- Anlegen

    def anlegen(self):
        u"""Den geprueften Auftrag anlegen (nach `grund() == ''`)."""
        from pathlib import Path
        ausgabe = self.daten['ausgabe']
        return Effektauftrag.objects.create(
            name=self.daten.get('name') or Path(ausgabe).stem,
            pipeline=self.pipeline, bvh_pfad=self.bvh,
            kleid='' if self.mit_modell else (self.daten.get('kleid') or ''),
            modell=(self.daten.get('modell') or '') if self.mit_modell else '',
            ausgabe=ausgabe, parameter=self.daten.get('parameter') or {})
