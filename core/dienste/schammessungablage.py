# -*- coding: utf-8 -*-
"""Schammessungablage — die Scham-Messung im Blender-Import: jetzt das Stück, später die Farbe am Ring (10.10.2026).

Der Import baut das Scham-Stück im Schritt „stuecke", die Hautkacheln aber erst im Schritt „haut" (Stunden später). Deshalb zwei Aufrufe:

    messen      nach dem Bau des Stücks: Form, Naht, Symmetrie (`Schammessung.sicher`) — das Original ist der Körper des Imports in Ruhelage; dabei legt es die Daten des Stücks ab
    nachtragen  am Ende von `Blendimporthaut.backen`: die Farbe am Ring gegen die gebackene Haut-Kachel daneben (`Schammessung.sicher_farbe`)
Beide laufen IMMER; ohne Scham-Stück (`scham = figur`, Figur trifft das Original) melden sie das.
"""
import numpy as np

__all__ = ['Schammessungablage']


class Schammessungablage:
    DATEI = 'scham_messung.npz'

    @classmethod
    def messen(cls, ablage, d, material, figur, ordner):
        """`d`: Rückgabe von `Blendimportscham.bauen`; `material`: Material des Stücks (`bild` = Farbatlas); `figur`: `Blendimportlage.genesis()`; `ordner`: Arbeitsordner des Stücks."""
        from .schammessung import Schammessung

        original = d.get('original') or {}
        vorgabe = {'punkte': original['punkte'], 'dreiecke': original['dreiecke'], 'teil': False} if original else None
        bericht = Schammessung.sicher(ordner=ordner, punkte=d['punkte'], dreiecke=d['dreiecke'], uv_ecken=d['uv_ecken'], figur=figur, loch=d.get('loch'),
                                      vorgabe=vorgabe, farbe_pfad=material.get('bild'))
        loch = d.get('loch') or {}
        np.savez(ablage.arbeit(cls.DATEI), punkte=d['punkte'], dreiecke=d['dreiecke'], uv_ecken=d['uv_ecken'], farbe_pfad=np.array(str(material.get('bild') or '')),
                 loch_dreiecke=np.asarray(loch.get('dreiecke', []), dtype=np.int64), ring=np.asarray(loch.get('ring', np.zeros((0, 3))), dtype=np.float64),
                 ring_punkte=np.asarray(loch.get('ring_punkte', []), dtype=np.int64), hat_loch=np.array(bool(loch)))
        return bericht

    @classmethod
    def nachtragen(cls, ablage, figur):
        """Die Farbe am Ring nach dem Backen der Haut → Bericht; ohne Stück `{'hinweis': …}`."""
        from .schammessung import Schammessung

        pfad = ablage.arbeit(cls.DATEI)
        if not pfad.is_file():
            return {'hinweis': 'kein Scham-Stück in diesem Import (keine Messung)'}
        with np.load(pfad) as a:
            loch = {'dreiecke': a['loch_dreiecke'], 'ring': a['ring'], 'ring_punkte': a['ring_punkte']} if bool(a['hat_loch']) else None
            farbe = str(a['farbe_pfad']) or None
            return Schammessung.sicher_farbe(punkte=a['punkte'], dreiecke=a['dreiecke'], uv_ecken=a['uv_ecken'], figur=figur, loch=loch, farbe_pfad=farbe,
                                             kachelbild=lambda kachel: ablage.ergebnis('haut_%d_farbe.jpg' % kachel))
