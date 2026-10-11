# -*- coding: utf-8 -*-
"""Hautschattungbau — baut aus den Rohdaten eines exportierten Netzes (`blendexport.py`, `blendnetzattribute.py`) die `Hautbackenschattung` des lokalen Backers, mit denselben
Normalen und Tangenten, die Cycles in Blender benutzt:

    schattung = Hautschattungbau.aus_export(punkte, npz, info)         # punkte: Ruhelage (N, 3)
    tangenten = Hautschattungbau.figur_tangenten(figur)                 # (M, 3, 4) für `Hautbackengraph.backen`

* Normalen: Blenders `polygon_normals`/`vertex_normals`/`corner_normals` für die Punkte der Ruhelage (`Hautbackenblendernormalen`, aus den Polygonen des Netzes, nicht aus den
  Dreiecken). Bei Domain „Ecke" liest Cycles die Eckennormalen (`dreieck_ecken`), sonst die Punktnormalen.
* Tangenten je UV-Karte: MikkTSpace wie Cycles (`Hautbackentangenten`, Modus `cycles`: gepackte Normalen, Glatt-Flag des Netzes).
* Tangenten der Figur (Backziel): Blenders eigener Weg beim Backen (`calc_tangents`, Modus `blender`).
"""

import numpy as np

from ..hautbackenblendernormalen import Hautbackenblendernormalen
from ..hautbackentangenten import Hautbackentangenten
from .hautschattung import Hautbackenschattung

__all__ = ['Hautschattungbau']


class Hautschattungbau:
    @staticmethod
    def aus_export(punkte, npz, info, geraet='cuda:0'):
        punkte = np.ascontiguousarray(punkte, dtype=np.float32)
        dreiecke = np.asarray(npz['dreiecke'])
        n = Hautbackenblendernormalen.berechnen(
            punkte, npz['poly_start'], npz['poly_punkte'], npz.get('kanten'), npz.get('ecke_kante'), npz.get('scharf_kante'), npz.get('scharf_flaeche'),
            npz.get('eigene_normale'))
        if info.get('normalen_domain') not in (None, n['domain']):
            raise ValueError('Normalen-Domain: Blender meldet %s, die Rechnung ergibt %s' % (info.get('normalen_domain'), n['domain']))
        ecke = n['domain'] == 'CORNER'
        ecken_normalen = n['ecken'][np.asarray(npz['dreieck_ecken'])] if ecke else n['punkte'][dreiecke]
        glatt = np.asarray(npz['glatt'], dtype=bool) if 'glatt' in npz else np.ones(len(dreiecke), dtype=bool)

        def tangenten(uv_index):
            return Hautbackentangenten.berechnen(punkte, dreiecke, npz['uv_%d' % uv_index], normalen=None if ecke else n['punkte'], glatt=glatt,
                                                 ecken_normalen=ecken_normalen if ecke else None)

        return Hautbackenschattung(punkte, dreiecke, npz, info, ecken_normalen, tangenten, geraet)

    @staticmethod
    def figur_tangenten(figur):
        """`(M, 3, 4)` float32: Tangente (xyz) und Vorzeichen (w) je Ecke der Figur, wie Blender sie beim Backen in den Tangentenraum der Figur rechnet."""
        t, s = Hautbackentangenten.berechnen(figur.punkte, figur.dreiecke, figur.uv_ecken, modus='blender')
        return np.concatenate([t, s[..., None]], axis=2).astype(np.float32)
