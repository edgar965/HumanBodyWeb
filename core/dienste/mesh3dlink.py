# -*- coding: utf-8 -*-
"""Mesh3dlink — die Adresse eines Mesh-3D-Auftrags mit seinem Namen darin (13.10.2026).

Edgar: „verändere die Links der Jobs, die sollen die Namen enthalten im Link, z. B. /mesh-3D/2026.10.11.21.18.17/ — neu: /mesh-3D/edgar_2026.10.11.21.18.17/".

Die Adresse ist `/mesh-3D/<name>_<kennung>/`; der Name ist ein Wegweiser für Menschen (kleingeschrieben, nur a–z, 0–9 und `_`, Umlaute ausgeschrieben), die KENNUNG hinter dem letzten Unterstrich entscheidet. Deshalb:
- jede Adresse mit richtiger Kennung findet den Auftrag, auch die alte `/mesh-3D/<kennung>/` und eine mit dem Namen von früher;
- die Seite leitet auf die gültige Adresse um (`Mesh3dendpunkte.seite`), wenn die aufgerufene nicht genau ihr entspricht — nach einem Umbenennen führt der alte Link also auf den neuen;
- die Daten-Adressen (`/api/mesh3d/<kennung>/…`) bleiben bei der reinen Kennung: der Name steht nur in der Seite.
"""

import re
import unicodedata

from ..daten.auftragskennung import Auftragskennung

__all__ = ['Mesh3dlink']


class Mesh3dlink:
    #: Höchste Länge des Namens im Link (Zeichen).
    NAME_MAX = 40
    _ORT = re.compile(r'^(?:(?P<name>[a-z0-9_]*?)_)?(?P<kennung>%s)$' % Auftragskennung.MUSTER)
    _UMLAUTE = str.maketrans({'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss', 'Ä': 'ae', 'Ö': 'oe', 'Ü': 'ue'})

    @classmethod
    def name_im_link(cls, name):
        """Der Name als Teil der Adresse: `Spiralballerina ohne Zweitarm` → `spiralballerina_ohne_zweitarm`; nichts Brauchbares → leer."""
        roh = unicodedata.normalize('NFKD', str(name or '').translate(cls._UMLAUTE))
        ascii_ = roh.encode('ascii', 'ignore').decode('ascii').lower()
        sauber = re.sub(r'[^a-z0-9]+', '_', ascii_).strip('_')
        return sauber[:cls.NAME_MAX].strip('_')

    @classmethod
    def ort(cls, kennung, name):
        """Das Pfadstück `<name>_<kennung>` (ohne Namen nur die Kennung)."""
        teil = cls.name_im_link(name)
        return '%s_%s' % (teil, kennung) if teil else str(kennung)

    @classmethod
    def pfad(cls, kennung, name):
        """Die ganze Adresse: `/mesh-3D/<name>_<kennung>/`."""
        return '/mesh-3D/%s/' % cls.ort(kennung, name)

    @classmethod
    def kennung_aus(cls, ort):
        """Die Kennung hinter dem Namen in einem Pfadstück — `None`, wenn es keine trägt."""
        treffer = cls._ORT.match(str(ort or ''))
        return treffer.group('kennung') if treffer else None
