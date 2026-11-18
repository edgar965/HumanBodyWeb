# -*- coding: utf-8 -*-
"""Unterteilungsablage — fertige Unterteiler-Teile unter `media/unterteilung/`.

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
import sys as _npz_sys  # noqa: E402
if r'A:\3DTools' not in _npz_sys.path:
    _npz_sys.path.append(r'A:\3DTools')
from KoerperKI_alle.npztorch import Npztorch  # noqa: E402

logger = logging.getLogger('core')

__all__ = ['Unterteilungsablage']


class Unterteilungsablage:
    ORDNER = Path(settings.MEDIA_ROOT) / 'unterteilung'

    @classmethod
    def pfad(cls, geschlecht, stufen, schluessel):
        return cls.ORDNER / ('%s_s%d_%s.npz' % (geschlecht, stufen, schluessel))

    @classmethod
    def unterteiler(cls, geschlecht, netz, stufen):
        """Ein `CatmullClarkSubdivider` für `netz` (MeshData) mit `stufen` —
        aus der Ablage, sonst gebaut und abgelegt."""
        eingaben = (netz.faces, netz.face_materials, netz.uvs, stufen, getattr(netz, 'uv_loops', None))
        pfad = cls.pfad(geschlecht, stufen, Unterteilungsbau.schluessel(*eingaben))
        teile = cls._laden(pfad)
        beginn = time.perf_counter()
        if teile is None:
            teile = Unterteilungsbau.bauen(*eingaben)
            logger.info(
                'Unterteilung %s, %d Stufen: gebaut in %.1f s',
                geschlecht,
                stufen,
                time.perf_counter() - beginn,
            )
            cls._speichern(pfad, teile)
        else:
            logger.info(
                'Unterteilung %s, %d Stufen: aus %s geladen (%.2f s)',
                geschlecht,
                stufen,
                pfad.name,
                time.perf_counter() - beginn,
            )
        return CatmullClarkSubdivider(netz.faces, teile=teile)

    @staticmethod
    def _laden(pfad):
        # `.pt` daneben oder die alte `.npz` (`Npztorch.datei`): `Unterteilungsbau.speichern` schreibt seit der torch-Umstellung `.pt`, `laden` liest beide — bis 18.11.2026
        # prüfte diese Stelle nur die `.npz`, und jeder neue Prozess baute die Unterteiler neu.
        if Npztorch.datei(pfad) is None:  # npz geprüft: echte Datei über Npztorch.datei
            return None
        try:
            return Unterteilungsbau.laden(pfad)  # npz geprüft: ohne torch
        except Exception as fehler:  # noqa: BLE001
            # stumm gewollt: eine kaputte Ablage wird neu gebaut, nicht zum Fehler
            logger.warning('Unterteilungsablage %s unlesbar (%s) — wird neu gebaut', pfad.name, fehler)
            return None

    @classmethod
    def _speichern(cls, pfad, teile):
        try:
            cls.ORDNER.mkdir(parents=True, exist_ok=True)
            vorlaeufig = pfad.with_suffix('.neu.npz')
            Unterteilungsbau.speichern(vorlaeufig, teile)  # npz geprüft: ohne torch
            Npztorch.ersetzen(vorlaeufig, pfad)
        except OSError as fehler:
            logger.warning('Unterteilungsablage %s nicht schreibbar: %s', pfad, fehler)
