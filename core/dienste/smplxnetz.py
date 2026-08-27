# -*- coding: utf-8 -*-
"""SmplxNetz — Zugang zum SMPL-X-Netzgenerator aus VideoToBVH.

WARUM (Umbau 15.08.2026): Dreimal stand in core/api/foto.py derselbe Block —
`sys.path` um das Wrapper-Verzeichnis erweitern, `generate_mesh` importieren,
`sys.path` im `finally` wieder aufraeumen. Dreimal dieselbe Reihenfolge, dreimal
eine eigene Fehlerbehandlung. Einmal reicht.

Der Pfadumweg ist noetig, weil die Wrapper nicht als Paket installiert sind; er
gehoert deshalb an EINE Stelle und nicht in jeden Endpunkt.
"""
import logging

from ..daten.wrapperpfad import Wrapperpfad

logger = logging.getLogger('core')


class SmplxNetzFehler(RuntimeError):
    """Der Generator ist nicht da oder liefert nichts."""


class SmplxNetz:
    """Erzeugt ein SMPL-X-Netz aus Formparametern."""

    #: SMPL-X hat 10.475 Vertices, SMPL 6.890. Die Topologien sind unvereinbar;
    #: wer beides verwechselt, bekommt ein Flickenmuster (im Projekt dreimal
    #: aufgetreten, zuletzt am 13.08.2026).
    SMPLX_VERTICES = 10475
    SMPL_VERTICES = 6890

    @classmethod
    def erzeugen(cls, betas, geschlecht='neutral'):
        """(vertices, faces, netz) — wirft `SmplxNetzFehler`, wenn es nicht geht."""
        try:
            with Wrapperpfad():
                from smplest_x_wrapper import generate_mesh
                netz = generate_mesh(betas, geschlecht)
        except ImportError as e:
            raise SmplxNetzFehler('SMPL-X-Wrapper nicht gefunden: %s' % e) from e
        if netz is None:
            raise SmplxNetzFehler('SMPL-X-Modell nicht verfuegbar')
        import numpy as np
        vertices = np.asarray(netz['vertices']).reshape(netz['n_verts'], 3)
        faces = np.asarray(netz['faces']).reshape(netz['n_faces'], 3)
        return vertices, faces, netz

    @classmethod
    def ist_smplx(cls, anzahl_vertices):
        """Passt diese Vertexzahl zur SMPL-X-Topologie?"""
        return anzahl_vertices >= cls.SMPLX_VERTICES
