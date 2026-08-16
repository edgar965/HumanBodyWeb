# -*- coding: utf-8 -*-
"""SmplxArchiv — Rohdaten einer Fotoanalyse dauerhaft ablegen.

Aus `analyze_photo` herausgeloest (Umbau 15.08.2026). Je Auftrag entstehen zwei
Dateien unter HumanBody/data/photoTo3D/SMPLX:

    <job>.json   Parameter, Masse, Kameraangaben — lesbar
    <job>.npz    Netz, Gelenke, Gewichte, optional die posierten Vertices

Das Ablegen darf die Antwort nie aufhalten: Wer ein Foto analysiert, will das
Ergebnis sehen, auch wenn das Archiv gerade nicht schreibbar ist.
"""
import json
import logging
import os

import numpy as np
from django.conf import settings

from .smplxnetz import SmplxNetz, SmplxNetzFehler

logger = logging.getLogger('core')


class SmplxArchiv:
    """Schreibt Parameter und Netz einer Analyse auf die Platte."""

    @staticmethod
    def verzeichnis():
        pfad = os.path.join(str(settings.BASE_DIR), '..', 'HumanBody', 'data',
                            'photoTo3D', 'SMPLX')
        os.makedirs(pfad, exist_ok=True)
        return pfad

    @classmethod
    def ablegen(cls, ergebnis, job, dateiname):
        """Beides schreiben; Fehler werden protokolliert, nicht geworfen."""
        try:
            ordner = cls.verzeichnis()
            cls._parameter_schreiben(ordner, ergebnis, job, dateiname)
            cls._netz_schreiben(ordner, ergebnis, job)
        except Exception as e:                                    # noqa: BLE001
            logger.error('SMPL-X-Archiv fuer %s nicht schreibbar: %s',
                         job.id, e, exc_info=True)

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
        inhalt = dict(
            vertices=netz['vertices'], faces=netz['faces'],
            joints=netz['joints'],
            parents=np.array(netz['parents'], dtype=np.int32),
            skin_indices=netz['skin_indices'],
            skin_weights=netz['skin_weights'],
            betas=np.array(ergebnis.betas, dtype=np.float32),
            expression=np.array(ergebnis.roh.get('expression', []),
                                dtype=np.float32),
        )
        posiert = cls._posierte_vertices(ergebnis)
        if posiert is not None:
            inhalt['posed_vertices'] = posiert.astype(np.float32)
        np.savez_compressed(os.path.join(ordner, '%s.npz' % job.id), **inhalt)

    @staticmethod
    def _posierte_vertices(ergebnis):
        """Die vom Unterprozess abgelegten Vertices holen UND aufraeumen.

        Die Zwischendatei gehoert dem Unterprozess; bleibt sie liegen, sammelt
        sich je Analyse ein Netz auf der Platte."""
        pfad = ergebnis.roh.get('posed_vertices_path')
        if not (pfad and os.path.isfile(pfad)):
            return None
        try:
            vertices = np.load(pfad)
        except Exception:                                         # noqa: BLE001
            logger.error('Posierte Vertices nicht ladbar: %s', pfad)
            return None
        try:
            os.remove(pfad)
        except OSError as e:
            logger.debug('Zwischendatei %s bleibt liegen: %s', pfad, e)
        return vertices
