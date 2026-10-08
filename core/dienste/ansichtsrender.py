# -*- coding: utf-8 -*-
"""Ansichtsrender — je Vorlage ein Render der Teile einer Runde (`ansicht_<winkel>.png`), danach die Belichtung je Ansicht an das Foto angeglichen (06.10.2026).

Herausgelöst aus `Begutachtungsrunde._runde` (die Datei war bei 299 Zeilen). Der Abgleich (`Belichtung`) rechnet den Anteil weg, den kein Modell ändert — das feste Licht des Renders und die verschiedene Belichtung der Fotos; er gilt für Note, Befund und die
Prüftafel zugleich, die Tafel zeigt also, wonach benotet wird. Option `iterationen.belichtung` (Vorgabe an).
"""

from iterationen2d3d.belichtung import Belichtung

from .iterationsbild import Iterationsbild

__all__ = ['Ansichtsrender']


class Ansichtsrender:
    @staticmethod
    def rendern(render, teile, referenzen, aus, groesse, melden, runde, abgleichen=True, teile_von=None):
        """→ (Pfade der Renders, Belichtungsfaktoren) je Referenz. `render`: der offene `Genesishaarrender`, `aus`: Ordner der Runde, `melden(anteil, text)`: Fortschritt.
        `teile_von(referenz)`: die Teile in der Haltung dieses Fotos (`Haltungsansichten.von`) — ohne gelten `teile` für alle."""
        from .genesishaarrender import Genesishaarrender
        pfade = []
        for nummer, r in enumerate(referenzen):
            melden(0.3 + 0.4 * nummer / max(1, len(referenzen)), 'Runde %d: Rendern %d von %d' % (runde, nummer + 1, len(referenzen)))
            pfad = aus / ('ansicht_%+04d.png' % int(round(r.winkel)))
            render.bild_teile([(t['punkte'], t['dreiecke'], t['farbe'], Genesishaarrender.extra(t)) for t in (teile_von(r) if teile_von else teile)], r.winkel, pfad, groesse=groesse)
            pfade.append(pfad)
        if not abgleichen:
            return pfade, [1.0] * len(pfade)
        faktoren = Belichtung.faktoren([(r.bild, Iterationsbild.aus_render(pfad), r.farbe) for r, pfad in zip(referenzen, pfade)])
        for pfad, faktor in zip(pfade, faktoren):
            Belichtung.anwenden(pfad, faktor)
        return pfade, faktoren
