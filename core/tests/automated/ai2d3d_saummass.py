# -*- coding: utf-8 -*-
"""Ai2d3dsaummass — die Ränder eines Kleidungsstücks: glatter Saum oder ausgefranste Kante? (02.11.2026,
Edgar zur Jobseite EdgarTrip: „saum T-short und hose“ kaputt.)

Am Netz, nicht im Bild — darum für beide Zeilen der Seite gleich und ohne Kamera:
  Ränder  Kanten, die nur ein Dreieck hat, zu geschlossenen Schleifen verkettet (über gerichtete Kanten,
          damit Punkte mit zwei Randstücken nicht verwechselt werden)
  Saum    eine Schleife ab LOCH_MM Länge (Bund, Ärmel, Hosenbein, Ausschnitt); kürzere sind Löcher im Stoff
  Zacken  je Saum die Abweichung der Randpunkte von derselben Schleife, längs des Rands mit einem Gauß von
          GLAETTE_MM geglättet (gleichmäßig auf SCHRITT_MM umgetastet, kreisförmig gefaltet), davon das P95
          in mm; dazu Länge / geglättete Länge (eine ausgefranste Kante ist viel länger als ihr Verlauf)
Setzung GLAETTE_MM = 8: ein glatter Kreis von 55 mm Halbmesser (Ärmel) schrumpft dabei um 0,6 mm und wird
1,1 % kürzer, Zähne alle 20 mm gehen zu 96 % durch. Mit 15 mm (erste Fassung, 02.11.2026) bekam derselbe glatte
Kreis schon 2,0 mm „Zacken“ und 3,8 % Überlänge — die geraden Ärmelschnitte von `Fotosaum` maßen 2,9–3,0 mm.

    erg = Ai2d3dsaummass.messen(punkte, dreiecke)
    # {'saeume': [{'laenge_mm', 'zacken_mm', 'verhaeltnis', 'punkte'}], 'loecher': Zahl,
    #  'loch_mm': Länge aller Löcher}
"""
import numpy as np

__all__ = ['Ai2d3dsaummass']


class Ai2d3dsaummass:
    LOCH_MM, GLAETTE_MM, SCHRITT_MM = 150.0, 8.0, 1.0

    @staticmethod
    def schleifen(dreiecke):
        """[Punktnummern in Reihenfolge] je Randschleife."""
        t = np.asarray(dreiecke, dtype=np.int64)
        gerichtet = np.concatenate([t[:, [0, 1]], t[:, [1, 2]], t[:, [2, 0]]])
        alle = set(map(tuple, gerichtet.tolist()))
        weiter = {}
        for a, b in gerichtet.tolist():
            if (b, a) not in alle:
                weiter.setdefault(a, []).append(b)
        aus = []
        while weiter:
            start = next(iter(weiter))
            kette, p = [start], start
            while True:
                nach = weiter.get(p)
                if not nach:
                    break
                q = nach.pop()
                if not nach:
                    del weiter[p]
                if q == start:
                    break
                kette.append(q)
                p = q
            if len(kette) >= 3:
                aus.append(np.array(kette))
        return aus

    @classmethod
    def glaetten(cls, x):
        """(n, 3) Schleife → (dieselbe Schleife geglättet an denselben Stellen, Länge, geglättete Länge)."""
        d = np.linalg.norm(np.roll(x, -1, 0) - x, axis=1)
        s = np.concatenate([[0], np.cumsum(d)])
        laenge = s[-1]
        n = max(16, int(np.ceil(laenge / (cls.SCHRITT_MM / 1000))))
        u = np.linspace(0, laenge, n, endpoint=False)
        zu = np.vstack([x, x[:1]])
        g = np.stack([np.interp(u, s, zu[:, k]) for k in range(3)], 1)
        sigma = cls.GLAETTE_MM / 1000 / (laenge / n)
        kern = np.exp(-2 * (np.pi * np.fft.rfftfreq(n) * sigma) ** 2)
        glatt = np.fft.irfft(np.fft.rfft(g, axis=0) * kern[:, None], n=n, axis=0)
        zu_g, uu = np.vstack([glatt, glatt[:1]]), np.concatenate([u, [laenge]])
        an = np.stack([np.interp(s[:-1], uu, zu_g[:, k]) for k in range(3)], 1)
        return an, laenge, np.linalg.norm(np.roll(glatt, -1, 0) - glatt, axis=1).sum()

    @classmethod
    def messen(cls, punkte, dreiecke):
        x = np.asarray(punkte, dtype=np.float64)
        saeume, loecher, loch = [], 0, 0.0
        for k in cls.schleifen(dreiecke):
            p = x[k]
            laenge = np.linalg.norm(np.roll(p, -1, 0) - p, axis=1).sum()
            if laenge * 1000 < cls.LOCH_MM:
                loecher += 1
                loch += laenge * 1000
                continue
            an, laenge, glatt = cls.glaetten(p)
            ab = np.linalg.norm(p - an, axis=1) * 1000
            saeume.append({'laenge_mm': round(float(laenge) * 1000, 1),
                           'zacken_mm': round(float(np.percentile(ab, 95)), 2),
                           'verhaeltnis': round(float(laenge / max(glatt, 1e-9)), 3), 'punkte': len(k)})
        saeume.sort(key=lambda s: -s['laenge_mm'])
        return {'saeume': saeume, 'loecher': loecher, 'loch_mm': round(loch, 1)}
