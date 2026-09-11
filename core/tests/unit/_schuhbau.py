# -*- coding: utf-8 -*-
u"""Schuhbau — einen Schuh gegen pygarment bauen, ohne Simulation.

Dasselbe Vorbereiten wie in `test_schuhschnitt.py` (Upstream in den
Suchpfad, tabellierte Kurvenzerlegung, `default.yaml` plus Schuhregler,
Referenzkörper plus die gemessenen Fussmasse), für weitere Prüfmodule —
die Datei dort ist voll.
"""
import copy
import os

import yaml

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.assets()
from GarmentCode.entwurf import Entwurf                      # noqa: E402


class Schuhbau:
    u"""Entwurf und Körper einmal laden, dann beliebig oft bauen."""

    UPSTREAM = Entwurf.REPO
    _entwurf = None
    _body = None

    @classmethod
    def vorbereiten(cls, fuss):
        u"""`fuss`: die Fussmasse (cm), die in den Körper gemischt werden."""
        if cls._entwurf is not None:
            return
        import sys
        if cls.UPSTREAM not in sys.path:
            sys.path.insert(0, cls.UPSTREAM)
        alt = os.getcwd()
        os.chdir(cls.UPSTREAM)
        try:
            import pygarment.garmentcode.edge as edge_modul
            from GarmentCode.kurvenzerlegung import Kurvenzerlegung
            Kurvenzerlegung.einhaengen(edge_modul)
            from GarmentCode.schuh.schuhentwurf import Schuhentwurf
            pfad = os.path.join(cls.UPSTREAM, 'assets', 'design_params',
                                'default.yaml')
            with open(pfad, 'r', encoding='utf-8') as datei:
                entwurf = yaml.safe_load(datei)['design']
            Schuhentwurf.mischen(entwurf)
            with open(os.path.join(cls.UPSTREAM, 'assets', 'bodies',
                                   'mean_female.yaml'), 'r') as datei:
                body = yaml.safe_load(datei)['body']
            body.update(fuss)
            cls._entwurf, cls._body = entwurf, body
        finally:
            os.chdir(alt)

    @classmethod
    def entwurf(cls, art, **regler):
        u"""Ein Entwurf mit Baustein `art` und Reglern `{'shoe.heel': 7}`."""
        entwurf = copy.deepcopy(cls._entwurf)
        entwurf['meta']['feet']['v'] = art
        for pfad, wert in regler.items():
            gruppe, feld = pfad.split('.')
            entwurf[gruppe][feld]['v'] = wert
        return entwurf

    @classmethod
    def bauen(cls, art, **regler):
        u"""Das Paar (`Schuhgarment`) für Baustein und Regler."""
        from GarmentCode.schuh.schuhgarment import Schuhgarment
        return Schuhgarment('probe', cls._body, cls.entwurf(art, **regler))

    @classmethod
    def body(cls):
        return dict(cls._body)
