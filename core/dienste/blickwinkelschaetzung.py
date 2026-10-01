# -*- coding: utf-8 -*-
"""Blickwinkelschaetzung — der Blickwinkel eines Vorlagenfotos, wenn ihn niemand angegeben hat (01.10.2026; der Ersatz
für fSpy: statt Fluchtlinien die 3D-Weltpunkte der MediaPipe-Pose, `iterationen2d3d.blickwinkel.Blickwinkel`).

`Iterationsreferenz` ließ ein Foto ohne Winkel (Rolle „Automatisch", fremder Name) bisher aus — die Note mag breite
Umrisse, eine Suche über die Note fand den Winkel nicht (BlenderModel). Hier wird er GEMESSEN: `nachholen(z)` holt
für jedes Foto der Bildauswahl, das keinen Winkel trägt, die Landmarken (`Fotolandmarken`, einmal je Datei) und schreibt
den geschätzten Winkel nach `kreislauf.winkel_geschaetzt[datei]` — der Lauf sichert das Ergebnis, `Iterationsreferenz`
liest es als vierte Quelle. Ein Foto ohne erkennbare Person bleibt ausgelassen, mit Grund.
"""

import logging

from iterationen2d3d.blickwinkel import Blickwinkel

from ..daten.haarengineablage import Haarengineablage
from .fotolandmarken import Fotolandmarken
from .iterationsreferenz import Iterationsreferenz

logger = logging.getLogger('core')

__all__ = ['Blickwinkelschaetzung']


class Blickwinkelschaetzung:
    FELD = 'winkel_geschaetzt'

    def __init__(self, job, ablage):
        self.job = job
        self.ablage = ablage

    def offene(self):
        """Die Einträge der Bildauswahl, die zählen sollen, aber keinen Winkel haben."""
        aus = []
        for eintrag in self.job.bilder or []:
            if eintrag.get('rolle') == 'aus' or float(eintrag.get('gewicht') or 0) <= 0:
                continue
            if Iterationsreferenz.winkel_von(eintrag) is None:
                aus.append(eintrag)
        return aus

    def fuer_lauf(self):
        """Vor den Runden: `kreislauf` des Auftrags mit den nachgeholten Winkeln (auch im Ergebnis abgelegt) — ein Fehler
        des Wrappers hält den Lauf nicht auf."""
        z = dict(self.job.ergebnis.get('kreislauf') or {})
        try:
            if self.nachholen(z):
                self.job.ergebnis['kreislauf'] = z
        except (OSError, ValueError, RuntimeError) as fehler:
            logger.warning('2D3D Kleider %s: Blickwinkel nicht geschätzt (%s)', self.job.kennung, fehler)
        return z

    def nachholen(self, z):
        """`z` = `kreislauf`: den Winkel je offenem Foto schätzen und unter `winkel_geschaetzt` ablegen → Anzahl neu."""
        bekannt = dict(z.get(self.FELD) or {})
        offene = [e for e in self.offene() if e['datei'] not in bekannt]
        if not offene:
            return 0
        eingang = self.ablage.unter(Haarengineablage.EINGANG)
        befunde = Fotolandmarken(self.ablage).holen([eingang / e['datei'] for e in offene])
        neu = 0
        for e in offene:
            b = befunde.get(e['datei']) or {}
            welt = b.get('pose_welt')
            winkel = None
            if welt:
                welt = {i: {'x': p[0], 'y': p[1], 'z': p[2], 'sichtbar': p[3]} for i, p in enumerate(welt)}
                winkel = Blickwinkel.schaetzen(welt)
            bekannt[e['datei']] = {'winkel': winkel, 'rolle': Blickwinkel.rolle(winkel), 'quelle': 'pose'}
            neu += 1
            logger.info('Blickwinkel %s: %s (%s)', e['datei'], winkel, Blickwinkel.rolle(winkel) or 'keine Person')
        z[self.FELD] = bekannt
        return neu
