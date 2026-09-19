# -*- coding: utf-8 -*-
"""Bildmodellzielproportionen — Edgars Proportionen formen das Zielnetz.

Edgar (19.09.2026): „Mit einem Popup kommt ein Fenster, wo ich diese anpassen
kann. Diese Proportionen nutzt du dann für deine Berechnung."

Das Modell folgt dem Zielnetz auf unter 1 mm (Damira: Regler 8,2 mm, mit
Restmorph 0,7 mm) — was an den Proportionen falsch ist, ist das Ziel des
Schätzers. Darum greifen die Eingaben (`optionen.proportionen`, cm je
Schlüssel aus `G9proportionen.MASSE`) VOR der Ausgleichung am Zielnetz:
`G9proportionsformung` skaliert den betroffenen Bereich lokal, das
Ergebnis liegt als `ziel_prop.npz` neben `ziel.npz`; Ausgleichung, Rest,
Vorschau und Maße lesen dann das geformte Ziel (`Bildmodellanpassung.
_ziel_laden`). Ohne Eingaben wird die Datei entfernt — es gilt das rohe
Ziel. Der Bericht (`ergebnis.anpassung.proportionen`) nennt je Maß
vorher, Ziel, nachher in cm — gemessen am geformten Netz.
"""

import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Bildmodellzielproportionen']


class Bildmodellzielproportionen:
    """Zielnetz nach den Eingaben formen und ablegen."""

    DATEI = 'ziel_prop.npz'

    def __init__(self, job, ablage, optionen):
        self.job = job
        self.ablage = ablage
        self.optionen = optionen

    def eingaben_m(self):
        """`{schluessel: Meter}` der gültigen Eingaben (Katalog prüft die Grenzen)."""
        roh = self.optionen.get('proportionen')
        if not isinstance(roh, dict):
            roh = (self.job.optionen or {}).get('proportionen') or {}
        aus = {}
        for k, v in roh.items():
            try:
                cm = float(v)
            except TypeError, ValueError:
                continue
            if cm > 0:
                aus[str(k)] = cm / 100.0
        return aus

    def pfad(self):
        return self.ablage.ergebnis() / self.DATEI

    def formen(self, punkte, gewicht, gelenke):
        """`(punkte, gelenke, bericht)` — geformt, wenn Eingaben da sind; sonst unverändert.

        `bericht` ist None ohne Eingaben, sonst `{schluessel: {vorher, ziel, nachher}}` in cm.
        """
        ziele = self.eingaben_m()
        pfad = self.pfad()
        if not ziele:
            if pfad.is_file():
                pfad.unlink()
            return punkte, gelenke, None
        from Genesis9.proportionsformung import G9proportionsformung

        p, g, bericht = G9proportionsformung().formen(punkte, gelenke, ziele, gewicht > 0)
        np.savez_compressed(
            pfad,
            punkte=p.astype(np.float32),
            gewicht=np.asarray(gewicht, dtype=np.float32),
            gelenknamen=np.array(list(g)),
            gelenke=np.array([g[k] for k in g], dtype=np.float32),
        )
        aus = {
            k: {
                'vorher': round(b['vorher'] * 100, 1),
                'ziel': round(b['ziel'] * 100, 1),
                'nachher': round(b['nachher'] * 100, 1) if b.get('nachher') is not None else None,
            }
            for k, b in bericht.items()
        }
        logger.info('Bildmodell %s: Zielnetz auf %d Proportionen geformt: %s',
                    self.job.kennung, len(aus), aus)
        return p, g, aus
