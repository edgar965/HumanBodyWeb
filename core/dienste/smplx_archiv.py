# -*- coding: utf-8 -*-
"""SmplxArchiv — Rohdaten einer Fotoanalyse dauerhaft ablegen.

Aus `analyze_photo` herausgeloest (Umbau 15.08.2026). Je Auftrag entstehen zwei
Dateien unter 3DObjects/photoTo3D/SMPLX:

    <job>.json   Parameter, Masse, Kameraangaben — lesbar
    <job>.npz    Netz, Gelenke, Gewichte, optional die posierten Vertices

Das Ablegen darf die Antwort nie aufhalten: Wer ein Foto analysiert, will das
Ergebnis sehen, auch wenn das Archiv gerade nicht schreibbar ist.
"""

import json
import logging
import os
from typing import Any

import torch
from KoerperKI_alle.torchfeld import Torchfeld
from KoerperKI_alle.npztorch import Npztorch

from ..daten.smplxablage import Smplxablage
from .smplxnetz import SmplxNetz, SmplxNetzFehler

logger = logging.getLogger('core')


class SmplxArchiv:
    """Schreibt Parameter und Netz einer Analyse auf die Platte."""

    @staticmethod
    def verzeichnis():
        """Der Ablageordner — angelegt, falls er noch fehlt."""
        pfad = Smplxablage.verzeichnis()
        os.makedirs(pfad, exist_ok=True)
        return pfad

    @classmethod
    def ablegen(cls, ergebnis, job, dateiname):
        """Beides schreiben; Fehler werden protokolliert, nicht geworfen."""
        try:
            ordner = cls.verzeichnis()
            cls._parameter_schreiben(ordner, ergebnis, job, dateiname)
            cls._netz_schreiben(ordner, ergebnis, job)
        except Exception as e:  # noqa: BLE001
            logger.error('SMPL-X-Archiv fuer %s nicht schreibbar: %s', job.id, e, exc_info=True)

    @classmethod
    def _parameter_schreiben(cls, ordner, ergebnis, job, dateiname):
        daten = ergebnis.archivdaten(job, dateiname, job.created_at)
        pfad = os.path.join(ordner, '%s.json' % job.id)
        with open(pfad, 'w', encoding='utf-8') as f:
            json.dump(daten, f, indent=2, ensure_ascii=False)

    @classmethod
    def _netz_schreiben(cls, ordner, ergebnis, job):
        try:
            _v, _f, netz = SmplxNetz.erzeugen(ergebnis.betas, ergebnis.geschlecht)
        except SmplxNetzFehler as e:
            logger.warning('Kein SMPL-X-Netz fuer %s: %s', job.id, e)
            return
        inhalt: dict[str, Any] = dict(
            vertices=netz['vertices'],
            faces=netz['faces'],
            joints=netz['joints'],
            parents=Torchfeld.feld(netz['parents'], dtype=torch.int32, copy=True),
            skin_indices=netz['skin_indices'],
            skin_weights=netz['skin_weights'],
            betas=Torchfeld.feld(ergebnis.betas, dtype=torch.float32, copy=True),
            expression=Torchfeld.feld(ergebnis.roh.get('expression', []), dtype=torch.float32, copy=True),
        )
        posiert = cls._posierte_vertices(ergebnis)
        if posiert is not None:
            inhalt['posed_vertices'] = Torchfeld.astype(posiert, torch.float32)
        Npztorch.speichern(os.path.join(ordner, '%s.npz' % job.id), **inhalt, komprimiert=True)

    @staticmethod
    def _posierte_vertices(ergebnis):
        """Die vom Unterprozess abgelegten Vertices holen UND aufraeumen.

        Die Zwischendatei gehoert dem Unterprozess; bleibt sie liegen, sammelt
        sich je Analyse ein Netz auf der Platte."""
        pfad = ergebnis.roh.get('posed_vertices_path')
        if not (pfad and Npztorch.da(pfad)):
            return None
        try:
            vertices = Npztorch.lesen(pfad)
        except Exception:  # noqa: BLE001
            logger.error('Posierte Vertices nicht ladbar: %s', pfad)
            return None
        try:
            Npztorch.loeschen(pfad)          # .pt seit 13.11.2026 (python10 schreibt weiter .npy)
        except OSError as e:
            logger.debug('Zwischendatei %s bleibt liegen: %s', pfad, e)
        return vertices
