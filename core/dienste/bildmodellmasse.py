# -*- coding: utf-8 -*-
"""Bildmodellmasse — Außenmaße Foto / Zielnetz / Modell nebeneinander.

Edgar (19.09.2026): „was gänzlich fehlt in dem Tool sind die Außenproportionen
des Modells, z.B. Hüftbreite, Nase, Brustform und Brustgröße."

Vier Breiten (`G9silhouettenmasse`: Schulter, Brust, Taille, Hüfte) als
Anteil der Körperhöhe und in cm, dreimal mit derselben Messfunktion:
am FOTO (Personenmaske der frontalen Hauptbilder, Median), am ZIELNETZ
(SMPL-X aus den Betas, orthografisch gerendert) und am MODELL (Genesis-
Käfig mit Reglern und Restmorph). So sieht man, wo eine Abweichung
entsteht — beim Schätzer (Foto → Zielnetz) oder bei den Reglern
(Zielnetz → Modell). Läuft im Schritt „vorschau", Ergebnis in
`ergebnis.masse`, Tabelle auf der Seite (`ergebnisansicht.js`).
"""

import logging

import numpy as np

from ..daten.wrapperpfad import Wrapperpfad

logger = logging.getLogger('core')

__all__ = ['Bildmodellmasse']


class Bildmodellmasse:
    def __init__(self, job, stellung):
        self.job = job
        self.stellung = stellung

    def hoehe_cm(self):
        z = self.job.ergebnis.get('ziel') or {}
        return z.get('hoehe_ziel_cm') or None

    def foto(self):
        """Median der Maße über die frontalen, neutral stehenden Hauptbilder mit Maske und Rig."""
        from Genesis9.silhouettenmasse import G9silhouettenmasse

        werte = []
        for b in self.job.bilder:
            # Nur neutrale Haltung: in der Hocke ist die „Hüftbreite" die Beinspreizung
            # (Damira, posiertes Bild: 74,5 cm).
            if b.get('kategorie') != 'koerper' or float(b.get('gewicht') or 0) <= 0:
                continue
            if b.get('haltung') != 'neutral':
                continue
            m = G9silhouettenmasse.vom_foto(b, self.hoehe_cm())
            if m:
                werte.append(m)
        if not werte:
            return None
        aus = {}
        for k in G9silhouettenmasse.MASSE:
            gueltig = [w[k] for w in werte if w.get(k) is not None]
            if not gueltig:
                continue
            aus[k] = round(float(np.median(gueltig)), 4)
            aus[k + '_bilder'] = len(gueltig)
            if self.hoehe_cm():
                aus[k + '_cm'] = round(aus[k] * float(self.hoehe_cm()), 1)
        aus['bilder'] = len(werte)
        aus['arme_anliegend'] = sum(1 for w in werte if w.get('arme_anliegend'))
        return aus

    def zielnetz(self):
        from Genesis9.silhouettenmasse import G9silhouettenmasse
        from Genesis9.zielnetz import G9zielnetz

        s = self.job.ergebnis.get('schaetzung') or {}
        if not s.get('betas'):
            return None
        z = G9zielnetz.aus(s['betas'], symmetrisch=True)
        k = G9zielnetz.koerper()
        # Gelenke des SMPL-X-Netzes: Schultern 16/17, Hüften 1/2 (SMPL-X-Reihenfolge).
        gelenke = {
            'l_upperarm': z.gelenke[16],
            'r_upperarm': z.gelenke[17],
            'l_thigh': z.gelenke[1],
            'r_thigh': z.gelenke[2],
        }
        return G9silhouettenmasse.vom_kaefig(z.punkte, k.faces, gelenke, self.hoehe_cm())

    def modell(self):
        from Genesis9.formung import G9formung
        from Genesis9.reglerableitung import G9reglerableitung
        from Genesis9.silhouettenmasse import G9silhouettenmasse
        from Genesis9.vorschaubild import G9vorschaubild

        f = G9formung(self.stellung)
        p, _, _ = G9reglerableitung.lage(f)
        # `lage` hebt die Punkte auf den Boden; `gelenkknochen()` hebt die Gelenke selbst.
        gelenke = {e['name']: e['kopf'] for e in f.skelett().gelenkknochen()}
        hoehe = float(p[:, 1].max() - p[:, 1].min()) * 100.0
        return G9silhouettenmasse.vom_kaefig(p, G9vorschaubild(p)._dreiecke(), gelenke, hoehe)

    def alle(self):
        """`{foto, zielnetz, modell, masse}` — jedes None, wo nichts messbar ist."""
        with Wrapperpfad():
            aus = {}
            for name, fn in (('foto', self.foto), ('zielnetz', self.zielnetz), ('modell', self.modell)):
                try:
                    aus[name] = fn()
                except Exception as fehler:  # noqa: BLE001
                    logger.warning('Bildmodell %s: Maße %s nicht messbar: %s', self.job.kennung, name, fehler)
                    aus[name] = None
        from Genesis9.silhouettenmasse import G9silhouettenmasse

        aus['masse'] = list(G9silhouettenmasse.MASSE)
        return aus
