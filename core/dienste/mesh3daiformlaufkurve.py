# -*- coding: utf-8 -*-
"""Mesh3daiformlaufkurve — der Verlauf eines Trainingslaufs als SVG für /mesh-3D-AI/formtraining/<lauf>/ (18.10.2026).

Eine Linie je Messgröße des Verlaufs (`lauf_ergebnis.json` → `verlauf`, während des Laufs die Epochenzeilen des Logs); Training durchgezogen, Prüfung gestrichelt. Die y-Achse ist
LOGARITHMISCH: die Werte reichen in einem Lauf von rund 5 bis 560 mm, linear läge alles Spätere als Strich am Boden. Gezeichnet auf dem Server (keine Bibliothek im Browser); Schrift und Gitter
in `currentColor`, damit beide Themes lesbar sind.

    Mesh3daiformlaufkurve.zeichnen(verlauf) -> None | {'svg': SafeString, 'reihen': [{name, farbe, gestrichelt, letzter}]}
"""

import math

from django.utils.html import escape
from django.utils.safestring import mark_safe

from .mesh3daiformlaufnamen import Mesh3daiformlaufnamen as N
from .mesh3daiformzellen import Mesh3daiformzellen as Z

__all__ = ['Mesh3daiformlaufkurve']


class Mesh3daiformlaufkurve:
    BREITE, HOEHE = 1500, 380   # flach: die Karte ist so breit wie die Seite (2.032 px gemessen), bei 960 × 320 stand die Kurve 677 px hoch
    RAND = (58, 16, 14, 36)   # links, rechts, oben, unten
    FARBEN = ('#e94560', '#4fc1ff', '#73daca', '#ff9940', '#bb9af7', '#e0c341', '#9ece6a', '#ff7eb6', '#7aa2f7', '#2ac3de', '#e0af68', '#a9b1d6')
    OHNE = ('epoche', 's')

    @classmethod
    def zeichnen(cls, verlauf):
        punkte = [v for v in verlauf if isinstance(v.get('epoche'), (int, float))]
        schluessel = []
        for v in punkte:
            for k, w in v.items():
                if k not in cls.OHNE and k not in schluessel and isinstance(w, (int, float)) and not isinstance(w, bool):
                    schluessel.append(k)
        werte = [w for v in punkte for k, w in v.items() if k in schluessel and isinstance(w, (int, float)) and w > 0]
        if not punkte or not werte:
            return None
        x0, x1 = min(v['epoche'] for v in punkte), max(v['epoche'] for v in punkte)
        x1 = x1 if x1 > x0 else x0 + 1
        y0, y1 = math.log10(min(werte)), math.log10(max(werte))
        y0, y1 = (y0 - 0.05, y1 + 0.05) if y1 - y0 > 0.1 else (y0 - 0.3, y1 + 0.3)
        links, rechts, oben, unten = cls.RAND
        bx, by = cls.BREITE - links - rechts, cls.HOEHE - oben - unten

        def px(e):
            return links + bx * (e - x0) / (x1 - x0)

        def py(w):
            return oben + by * (1.0 - (math.log10(w) - y0) / (y1 - y0))

        teile = ['<svg class="mesh3dai-kurve" viewBox="0 0 %d %d" role="img"><title>Verlauf des Trainings, logarithmische Achse</title>' % (cls.BREITE, cls.HOEHE)]
        for w in cls._yteilung(y0, y1):
            y = py(w)
            teile.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="currentColor" stroke-opacity="0.15"/>' % (links, y, cls.BREITE - rechts, y))
            teile.append('<text x="%d" y="%.1f" font-size="12" fill="currentColor" text-anchor="end" dominant-baseline="middle">%s</text>' % (links - 6, y, cls._zahl(w)))
        for e in cls._xteilung(x0, x1):
            x = px(e)
            teile.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="currentColor" stroke-opacity="0.12"/>' % (x, oben, x, cls.HOEHE - unten))
            teile.append('<text x="%.1f" y="%d" font-size="12" fill="currentColor" text-anchor="middle">%d</text>' % (x, cls.HOEHE - unten + 16, e))
        teile.append('<text x="%d" y="%d" font-size="12" fill="currentColor" text-anchor="end">Epoche</text>' % (cls.BREITE - rechts, cls.HOEHE - 4))
        teile.append('<text x="4" y="%d" font-size="12" fill="currentColor">mm</text>' % (oben + 10))
        reihen = []
        for i, k in enumerate(schluessel):
            farbe = cls.FARBEN[i % len(cls.FARBEN)]
            gestrichelt = k.startswith('pruefung')
            reihe = [(v['epoche'], v[k]) for v in punkte if isinstance(v.get(k), (int, float)) and v[k] > 0]
            if not reihe:
                continue
            pfad = ' '.join('%.1f,%.1f' % (px(e), py(w)) for e, w in reihe)
            teile.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"%s><title>%s</title></polyline>' % (
                pfad, farbe, ' stroke-dasharray="6 4"' if gestrichelt else '', escape(N.name(k))))
            if len(reihe) <= 40:
                teile.extend('<circle cx="%.1f" cy="%.1f" r="2.6" fill="%s"/>' % (px(e), py(w), farbe) for e, w in reihe)
            reihen.append({'name': N.name(k), 'schluessel': k, 'farbe': farbe, 'gestrichelt': gestrichelt, 'letzter': Z.mm(reihe[-1][1]), 'epoche': reihe[-1][0]})
        teile.append('</svg>')
        return {'svg': mark_safe(''.join(teile)), 'reihen': reihen}

    @staticmethod
    def _yteilung(y0, y1):
        """Teilstriche 1 · 2 · 5 × 10^n zwischen den Grenzen (Logarithmen)."""
        aus = []
        for n in range(math.floor(y0) - 1, math.ceil(y1) + 1):
            for m in (1, 2, 5):
                w = m * 10.0 ** n
                if y0 <= math.log10(w) <= y1:
                    aus.append(w)
        return aus

    @staticmethod
    def _xteilung(x0, x1):
        spanne = x1 - x0
        schritt = next((s for s in (1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000) if spanne / s <= 10), 1000)
        erster = int(math.ceil(x0 / schritt) * schritt)
        return list(range(erster, int(x1) + 1, schritt))

    @staticmethod
    def _zahl(w):
        return ('%g' % w).replace('.', ',')
