# -*- coding: utf-8 -*-
"""Kleiderstueckobjekt — das Netz eines gebauten Fotostücks (`Fotostuecke`), aus der OBJ-Datei im Arbeitsordner der Eigenstücke (04.10.2026).

`Fotostuecke._schreiben` legt je Stück `3DObjects/Genesis9/eigene_stuecke/EIGEN_<Name>/stueck.obj` ab (Meter, Y oben, Füße 0 — die Ruhelage der Figur) und schreibt danach das Garderobenstück
(`.duf`, Zentimeter) mit einer Korrektur auf der Grundfigur (`G9gcfigurbau.ruhelage`: Median 0 mm, Maximum 12–21 mm gemessen am Auftrag 2026.10.04.11.11.44). Gemessen wird das OBJ — das Netz
VOR dieser Korrektur —, weil es in Metern und ohne Garderobenbau zu lesen ist.

Der Ordner heißt anders als das Garderobenstück (`EIGEN_Eigen_Foto_04111144_hose_f20` gegen `eigen_foto_04111144_hose_f20`); gefunden wird er über den Namen, nicht über eine nachgebaute Regel.
"""

import re

__all__ = ['Kleiderstueckobjekt']


class Kleiderstueckobjekt:
    @staticmethod
    def _slug(text):
        return re.sub(r'[^a-z0-9]+', '_', str(text).lower()).strip('_')

    @classmethod
    def ordner(cls, stueck):
        """Der Arbeitsordner des Garderobenstücks `stueck` (z. B. `eigen_foto_04111144_hose_f20`) — None, wenn es ihn nicht gibt."""
        from Genesis9.eigenstueck import G9eigenstueck
        basis = G9eigenstueck.arbeitsordner('x').parent
        if not basis.is_dir():
            return None
        ziel = 'eigen_' + cls._slug(stueck)
        for pfad in basis.iterdir():
            if pfad.is_dir() and cls._slug(pfad.name) == ziel:
                return pfad
        return None

    @classmethod
    def laden(cls, stueck):
        """`(punkte, flaechen)` des Stücks in der Ruhelage — None ohne Ordner oder OBJ."""
        from Genesis9.objleser import G9objleser
        ordner = cls.ordner(stueck)
        if ordner is None or not (ordner / 'stueck.obj').is_file():
            return None
        netz = G9objleser.lesen(str(ordner / 'stueck.obj'))
        return netz['punkte'], netz['flaechen']
