# -*- coding: utf-8 -*-
"""Bildmodellmasse — Außenmaße Foto / Zielnetz / Modell nebeneinander.

Edgar (19.09.2026): „was gänzlich fehlt in dem Tool sind die Außenproportionen
des Modells, z.B. Hüftbreite, Nase, Brustform und Brustgröße."

Vier Breiten (`G9silhouettenmasse`: Schulter, Brust, Taille, Hüfte) als
Anteil der Körperhöhe und in cm, dreimal mit derselben Messfunktion:
am FOTO (Personenmaske der frontalen Hauptbilder, Median), am ZIELNETZ
(gepaarter Genesis-Käfig, orthografisch gerendert) und am MODELL (Genesis-
Käfig mit Reglern und Restmorph). So sieht man, wo eine Abweichung
entsteht — beim Schätzer (Foto → Zielnetz) oder bei den Reglern
(Zielnetz → Modell). Läuft im Schritt „vorschau", Ergebnis in
`ergebnis.masse`, Tabelle auf der Seite (`ergebnisansicht.js`).
"""

import logging

import numpy as np

from ..daten.wrapperpfad import Wrapperpfad
from .bildmodellbildtypen import Bildmodellbildtypen

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
            if b.get('kategorie') != 'koerper' or not Bildmodellbildtypen.fuer_form(b):
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
        """Am GEPAARTEN Zielkäfig (Genesis-Topologie, ggf. mit Proportionen geformt).

        Am SMPL-X-Netz selbst lag die Hüfte bei 36,3 statt 33,4 cm — dessen
        Hände hängen im Hüftband, die Silhouette maß Rumpf mit Hand
        (19.09.2026). Käfig gegen Käfig hat dieselbe Definition wie `modell()`.
        """
        from Genesis9.silhouettenmasse import G9silhouettenmasse
        from Genesis9.vorschaubild import G9vorschaubild

        from ..daten.bildmodellablage import Bildmodellablage
        from .bildmodellanpassung import Bildmodellanpassung

        p, _, gelenke = Bildmodellanpassung(self.job, Bildmodellablage(self.job.kennung), {})._ziel_laden()
        hoehe = float(p[:, 1].max() - p[:, 1].min()) * 100.0
        return G9silhouettenmasse.vom_kaefig(p, G9vorschaubild(p)._dreiecke(), gelenke, hoehe)

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
