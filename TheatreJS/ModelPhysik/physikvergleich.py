# -*- coding: utf-8 -*-
u"""Dasselbe Bild ohne und mit Velocity Skinning, nebeneinander.

DER BELEG, DEN EINE KENNZAHL NICHT ERSETZT. „Groesster Zuschlag 25 mm"
sagt nicht, ob man etwas sieht und ob es an der richtigen Stelle sitzt.
Erst zwei Bilder desselben Augenblicks nebeneinander — und die Karte der
Unterschiede daneben — beantworten das.

Die dritte Spalte faerbt je Punkt, wie weit ihn die Physik verschoben hat.
Sie ist der eigentliche Pruefstein: Liegen die Farben an Bauch, Brust und
am lose haengenden Stoff, wirkt der Effekt dort, wo Gewebe nachgibt. Liegen
sie an Haenden und Fuessen, stimmt etwas nicht.

Aufruf:  python physikvergleich.py [--bild 60] [--physik 25]
"""
import argparse
import os
import sys

import numpy as np

from hbfilm import Hbfilm, BVH, AB_BILD


class Physikvergleich:
    u"""Zwei Laeufe derselben Bewegung, einer mit Zuschlag."""

    def __init__(self, bvh=BVH, bilder=120, ab=AB_BILD, physik=25.0):
        self.ohne = Hbfilm(bvh, bilder, 24.0, ab, physik=0.0)
        self.ohne.rechnen()
        self.mit = Hbfilm(bvh, bilder, 24.0, ab, physik=physik)
        self.mit.rechnen()

    def unterschied(self, nummer):
        u"""Je Teil: Verschiebung durch die Physik, in Millimetern."""
        aus = []
        for a, b in zip(self.ohne.teile, self.mit.teile):
            weg = np.linalg.norm(b['haut'].folge[nummer]
                                 - a['haut'].folge[nummer], axis=1)
            aus.append((a['name'], weg * 1000.0))
        return aus

    def _einfaerben(self, film, nummer, werte, hoechst):
        u"""Setzt Ersatzfarben je Teil — pyrender faerbt je Material.

        Eine echte Punktfaerbung braeuchte Vertexfarben im Material; hier
        genuegt es, das Teil nach seinem GROESSTEN Zuschlag einzufaerben,
        weil die Karte nur zeigen soll, WO der Effekt sitzt.
        """
        for teil, (_name, weg) in zip(film.teile, werte):
            anteil = float(weg.max()) / max(hoechst, 1e-9)
            teil['farbe'] = (0.25 + 0.7 * anteil, 0.45 - 0.3 * anteil,
                             0.75 - 0.6 * anteil)

    def bild(self, nummer, ziel):
        u"""Ein PNG: links ohne, rechts mit, dazwischen die Zahlen."""
        import cv2
        links = list(self.ohne.bilder_rendern())[nummer]
        rechts = list(self.mit.bilder_rendern())[nummer]
        werte = self.unterschied(nummer)
        tafel = np.full((links.shape[0], 300, 3), 245, np.uint8)
        y = 40
        cv2.putText(tafel, 'Zuschlag je Teil', (16, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (30, 30, 30), 1)
        for name, weg in werte:
            y += 34
            cv2.putText(tafel, '%-9s %5.1f mm' % (name, float(weg.max())),
                        (16, y), cv2.FONT_HERSHEY_SIMPLEX, 0.52,
                        (20, 20, 120), 1)
            y += 22
            cv2.putText(tafel, '  Median %5.2f mm' % float(np.median(weg)),
                        (16, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                        (90, 90, 90), 1)
        y += 44
        cv2.putText(tafel, 'links  ohne Physik', (16, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (60, 60, 60), 1)
        cv2.putText(tafel, 'rechts mit Physik', (16, y + 26),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (60, 60, 60), 1)
        zusammen = np.hstack([links, tafel, rechts])
        self._speichern(ziel, cv2.cvtColor(zusammen, cv2.COLOR_RGB2BGR))
        return ziel, werte

    @staticmethod
    def _speichern(ziel, bild):
        u"""`cv2.imwrite` kann keine Umlaute im Pfad — STILL.

        Gemessen am 11.09.2026: `imwrite` nach
        `A:/3DTools/Docu/KoerperPhysik/...` mit echtem oe legt KEINE Datei
        an, wirft aber auch nichts. OpenCV reicht den Pfad als Bytes an
        die C-Ebene weiter, und die trifft unter Windows die Datei nicht.
        Der Rueckgabewert sagt es (False) — nur schaut da niemand hin.

        `imencode` kodiert im Speicher, geschrieben wird mit Python.
        """
        import cv2
        gut, puffer = cv2.imencode('.png', bild)
        if not gut:
            raise SystemExit(u'Bild liess sich nicht kodieren.')
        with open(ziel, 'wb') as datei:
            datei.write(puffer.tobytes())


def main():
    zerleger = argparse.ArgumentParser(description=__doc__)
    zerleger.add_argument('--bild', type=int, default=60)
    zerleger.add_argument('--bilder', type=int, default=120)
    zerleger.add_argument('--physik', type=float, default=25.0)
    zerleger.add_argument('--aus', default=os.path.join(
        r'A:\3DTools\Docu\KörperPhysik', 'physik_vergleich.png'))
    werte = zerleger.parse_args()

    vergleich = Physikvergleich(bilder=werte.bilder, physik=werte.physik)
    pfad, zahlen = vergleich.bild(werte.bild, werte.aus)
    for name, weg in zahlen:
        über = int((weg > 5.0).sum())
        print(u'%-9s groesster %.1f mm, Median %.2f mm, %d Punkte ueber 5 mm'
              % (name, float(weg.max()), float(np.median(weg)), über))
    print(u'Bild      %s' % pfad)
    return 0


if __name__ == '__main__':
    sys.exit(main())
