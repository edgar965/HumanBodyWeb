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

FOTOMASSE (19.09.2026, Testfall Ursula): Wo der Nutzer nichts eingibt, formen
die Maße der Silhouette (`Bildmodellfotomasse`: Hüfte, Taille, Oberschenkel,
Wade von vorn; Brust-, Bauch-, Gesäßtiefe und Brustvorsprung von der Seite)
— sonst blieb das Ziel die schlanke Schätzung (Hüfte 34,6 statt 38,4 cm).
Der Bericht nennt je Maß die `quelle` (eingabe / foto). Option `fotomasse`.
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
        """`{schluessel: Meter}` der gültigen Eingaben (Katalog prüft die Grenzen) — leer mit
        Option `popup: aus` (der GVHMR-Lauf: das Ziel bleibt der Schätzer, 20.09.2026)."""
        if self.optionen.get('popup', 'an') == 'aus':
            return {}
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

    def fotomasse_m(self):
        """`{schluessel: Meter}` aus den Fotos — leer, wenn die Option aus ist."""
        from Genesis9.proportionen import G9proportionen

        from .bildmodellfotomasse import Bildmodellfotomasse

        if not Bildmodellfotomasse.an(self.optionen, self.job):
            return {}
        hoehe = ((self.job.ergebnis or {}).get('ziel') or {}).get('hoehe_ziel_cm')
        cm = Bildmodellfotomasse(self.job, hoehe).messen()['cm']
        return {k: v / 100.0 for k, v in cm.items() if G9proportionen.FORMBAR.get(k) and v > 0}

    def ziele_m(self, ohne_foto=False):
        """`({schluessel: Meter}, {schluessel: quelle})` — Fotomaße, Eingaben darüber.

        `ohne_foto`: der Umriss hat das Ziel schon Zeile für Zeile geformt — dann formen die
        Fotomaße nicht noch einmal (dieselben Silhouetten, an Schulter und Brustvorsprung mit
        anderer Definition: Ursulas Vorsprung 6,2 statt 4,2 cm). Eingaben gelten weiter.
        """
        ziele, quelle = {}, {}
        foto = {} if ohne_foto else self.fotomasse_m()
        for name, werte in (('foto', foto), ('eingabe', self.eingaben_m())):
            for k, v in werte.items():
                ziele[k] = v
                quelle[k] = name
        return ziele, quelle

    def pfad(self):
        return self.ablage.ergebnis() / self.DATEI

    def formen(self, punkte, gewicht, gelenke, vorgeformt=False):
        """`(punkte, gelenke, bericht)` — geformt, wenn Ziele da sind; sonst unverändert.

        `bericht` ist None ohne Ziele, sonst `{schluessel: {vorher, ziel, nachher, quelle}}` in cm.
        `vorgeformt`: die Punkte tragen schon den Umriss (`Bildmodellumriss`) — dann wird
        `ziel_prop.npz` auch ohne Ziele geschrieben, sonst läse die Anpassung das rohe Ziel.
        """
        ziele, quelle = self.ziele_m(ohne_foto=vorgeformt)
        pfad = self.pfad()
        if not ziele and not vorgeformt:
            if pfad.is_file():
                pfad.unlink()
            return punkte, gelenke, None
        from Genesis9.proportionsformung import G9proportionsformung

        if ziele:
            p, g, bericht = G9proportionsformung().formen(punkte, gelenke, ziele, gewicht > 0)
        else:
            p, g, bericht = np.asarray(punkte, float), gelenke, {}
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
                'quelle': quelle.get(k),
            }
            for k, b in bericht.items()
        }
        logger.info('Bildmodell %s: Zielnetz auf %d Proportionen geformt: %s',
                    self.job.kennung, len(aus), aus)
        return p, g, aus
