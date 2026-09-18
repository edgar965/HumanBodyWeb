# -*- coding: utf-8 -*-
u"""Unterteilungsablage — fertige Unterteiler-Teile unter `media/unterteilung/`.

Warum: siehe `humanbody_core/unterteilungsbau.py` (drei Stufen bauen 66 s,
laden unter einer Sekunde). Der Dateiname trägt Geschlecht, Stufen und den
Schlüssel über alle Eingaben — eine Ablage passt nur zu genau dem Netz, aus
dem sie entstand (Regel `artefakte-benennen`). Liegt im Projekt, nicht in
System-Temp; `.gitignore` nimmt `media/unterteilung/` aus.
"""
import logging
import time
from pathlib import Path

from django.conf import settings

from humanbody_core.catmull_clark import CatmullClarkSubdivider
from humanbody_core.unterteilungsbau import Unterteilungsbau

logger = logging.getLogger('core')

__all__ = ['Unterteilungsablage']


class Unterteilungsablage:

    ORDNER = Path(settings.MEDIA_ROOT) / 'unterteilung'

    @classmethod
    def pfad(cls, geschlecht, stufen, schluessel):
        return cls.ORDNER / ('%s_s%d_%s.npz' % (geschlecht, stufen, schluessel))

    @classmethod
    def unterteiler(cls, geschlecht, netz, stufen):
        u"""Ein `CatmullClarkSubdivider` für `netz` (MeshData) mit `stufen` —
        aus der Ablage, sonst gebaut und abgelegt."""
        eingaben = (netz.faces, netz.face_materials, netz.uvs, stufen,
                    getattr(netz, 'uv_loops', None))
        pfad = cls.pfad(geschlecht, stufen, Unterteilungsbau.schluessel(*eingaben))
        teile = cls._laden(pfad)
        beginn = time.perf_counter()
        if teile is None:
            teile = Unterteilungsbau.bauen(*eingaben)
            logger.info('Unterteilung %s, %d Stufen: gebaut in %.1f s',
                        geschlecht, stufen, time.perf_counter() - beginn)
            cls._speichern(pfad, teile)
        else:
            logger.info('Unterteilung %s, %d Stufen: aus %s geladen (%.2f s)',
                        geschlecht, stufen, pfad.name, time.perf_counter() - beginn)
        return CatmullClarkSubdivider(netz.faces, teile=teile)

    @staticmethod
    def _laden(pfad):
        if not pfad.is_file():
            return None
        try:
            return Unterteilungsbau.laden(pfad)
        except Exception as fehler:                              # noqa: BLE001
            # stumm gewollt: eine kaputte Ablage wird neu gebaut, nicht zum Fehler
            logger.warning('Unterteilungsablage %s unlesbar (%s) — wird neu gebaut',
                           pfad.name, fehler)
            return None

    @classmethod
    def _speichern(cls, pfad, teile):
        try:
            cls.ORDNER.mkdir(parents=True, exist_ok=True)
            vorlaeufig = pfad.with_suffix('.neu.npz')
            Unterteilungsbau.speichern(vorlaeufig, teile)
            vorlaeufig.replace(pfad)
        except OSError as fehler:
            logger.warning('Unterteilungsablage %s nicht schreibbar: %s',
                           pfad, fehler)
