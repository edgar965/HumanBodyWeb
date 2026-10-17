# -*- coding: utf-8 -*-
"""Mesh3daiwege — mehrere Wege zum Rig derselben Probe auf der Jobseite von Mesh3D-AI (16.10.2026, Job UrsulaSpagat).

Edgar zur Seite `/mesh-3D-AI/ursulaspagat/`: „ist ja noch sehr schlecht, sowohl das Rig bei dem Mesh ist falsch als das Ergebnis" — die Seite zeigte nur, was das Netz direkt auf der Spagat-Pose
liefert (280,5 mm), nicht die Vorstufe, die er vorgeschlagen hatte (Rig → Netz in die A-Pose → Netz). `ProjektTemp/_wegwerf/mesh3dai_spagat_wege.py` rechnet je Weg die 138 Gelenke und die
Drehungen der Daz-Winkel (dieselbe Anpassung wie beim Netz, damit die Seite die Figur wie das Ziel häuten kann) und legt sie in den Ordner DES LAUFS, dessen Netz sie benutzen:
    wege.npz   nr (P,), <schlüssel>_rig (P, 138, 3), <schlüssel>_dreh (P, 138, 3, 3)
    wege.json  {fassung, lauf, standard, wege: [{schluessel, name, text}], proben: {nr: {schlüssel: {mm, …}}}}
Fehlt eine der Dateien, ist die Fassung eine andere oder passt die Form nicht, gibt es keine Wege (Warnung im Log) — die Seite zeigt dann den Lauf wie bisher.
"""

import json
import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Mesh3daiwege']


class Mesh3daiwege:
    NPZ = 'wege.npz'
    JSON = 'wege.json'
    #: Fassung der Ablage; eine andere wird nicht gezeigt (`artefakte-benennen.md`).
    FASSUNG = 1

    @classmethod
    def stand(cls, lauf):
        """Stempel beider Dateien (für die Ablage von `Mesh3daidaten`) — None, wenn eine fehlt."""
        try:
            return tuple((lauf / name).stat().st_mtime_ns for name in (cls.NPZ, cls.JSON))
        except OSError:
            return None

    @classmethod
    def lesen(cls, lauf, knochen):
        """`{standard, wege: [{schluessel, name, text}], proben: {nr: {schluessel: (rig (138, 3), dreh (138, 3, 3))}}}` oder None."""
        if cls.stand(lauf) is None:
            return None
        try:
            bericht = json.loads((lauf / cls.JSON).read_text(encoding='utf-8'))
            if int(bericht.get('fassung', 0)) != cls.FASSUNG:
                logger.warning('Mesh3daiwege: %s hat Fassung %s statt %s — keine Wege', lauf / cls.JSON, bericht.get('fassung'), cls.FASSUNG)
                return None
            wege = [w for w in bericht['wege'] if w.get('schluessel')]
            proben = {}
            with np.load(lauf / cls.NPZ) as d:
                nummern = [int(x) for x in d['nr']]
                for w in wege:
                    rig, dreh = d['%s_rig' % w['schluessel']], d['%s_dreh' % w['schluessel']]
                    if rig.shape != (len(nummern), knochen, 3) or dreh.shape != (len(nummern), knochen, 3, 3):
                        logger.warning('Mesh3daiwege: %s, Weg %s hat die Form %s / %s — keine Wege', lauf / cls.NPZ, w['schluessel'], rig.shape, dreh.shape)
                        return None
                    for i, nr in enumerate(nummern):
                        proben.setdefault(nr, {})[w['schluessel']] = (rig[i].astype(float), dreh[i].astype(float))
            standard = bericht.get('standard') if bericht.get('standard') in {w['schluessel'] for w in wege} else wege[0]['schluessel']
        except (OSError, KeyError, ValueError, IndexError) as fehler:
            logger.warning('Mesh3daiwege: %s nicht lesbar (%s) — keine Wege', lauf, fehler)
            return None
        return {'standard': standard, 'wege': [{'schluessel': w['schluessel'], 'name': w.get('name', w['schluessel']), 'text': w.get('text', '')} for w in wege], 'proben': proben}
