# -*- coding: utf-8 -*-
"""Meshto3dpfad — `A:\\3dTools\\meshto3d` (und die gemeinsamen Wrapper daneben) für die Dauer EINES Imports.

„Mesh to 3D" (Netz → Genesis-Figur) rechnet seine Registrierung in python10: `_run_meshfigur.py` und die `meshfigur_*.py` liegen seit dem 11.10.2026 in `meshto3d`, nicht mehr in
`VideoToBVH/wrappers` (Edgar: „es geht doch rein um die Erzeugung eines 3D Modells aus einem Mesh"). Sie brauchen aber `mesh_basis`, `posenerkennung` und `gesicht68`, die in
`VideoToBVH/wrappers` geblieben sind — darum stellt dieser Kontext BEIDE Ordner voran und räumt sie danach wieder weg (Grund wie `Wrapperpfad`: ein dauerhaft fremder Suchpfad beschattet
gleichnamige Module).

    with Meshto3dpfad():
        from meshfigur_daten import Meshfigurdaten
"""

import os
import sys

from django.conf import settings

__all__ = ['Meshto3dpfad']


class Meshto3dpfad:
    """Kontext, der `meshto3d` und `VideoToBVH/wrappers` nur während des Blocks führt."""

    def __init__(self):
        #: Reihenfolge der Suche: zuerst `meshto3d`, dann die gemeinsamen Wrapper.
        self.verzeichnisse = [self.pfad(), self.wrapper()]
        #: Nur was wir selbst eingehängt haben, räumen wir weg.
        self._eigen = []

    @staticmethod
    def pfad():
        """`…/3dTools/meshto3d` (`settings.MESHTO3D_DIR`)."""
        return os.path.normpath(str(settings.MESHTO3D_DIR))

    @staticmethod
    def wrapper():
        """`…/3dTools/VideoToBVH/wrappers` (`settings.WRAPPERS_DIR`) — dort liegen `mesh_basis`, `posenerkennung`, `gesicht68`."""
        return os.path.normpath(str(settings.WRAPPERS_DIR))

    def __enter__(self):
        for verzeichnis in reversed(self.verzeichnisse):
            if verzeichnis not in sys.path:
                sys.path.insert(0, verzeichnis)
                self._eigen.append(verzeichnis)
        return self

    def __exit__(self, *_ausnahme):
        for verzeichnis in self._eigen:
            if verzeichnis in sys.path:
                sys.path.remove(verzeichnis)
        self._eigen = []
        return False
