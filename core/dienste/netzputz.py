# -*- coding: utf-8 -*-
"""Netzputz — kleine Löcher in einem Kleidungsnetz schließen und ausgefranste Ränder glätten (04.10.2026).

Anlass (Edgar, 04.10.2026: „Hemdrand" in der Liste der Unterschiede zur Vorlage; Bühne und Film zeigen den Saum und die Ärmelenden zerfetzt): Gemessen am Hemd des Stands von Runde 59
(`ProjektTemp/_wegwerf/randy/hose/hose_raender.py … kleidung__gc_hemd`), nach Lage verschweißt: ein Saum mit 89 Randpunkten, deren Höhe zwischen y 1,024 und 1,052 m schwankt (Sägezähne),
zwei Ärmelenden mit 40 und 39 Randpunkten, dazu elf kleine Randschleifen von 3 bis 16 Punkten — Löcher im Stoff am Ärmel (x ±0,35…±0,46 m, y 1,0…1,17 m). Die Schnittbahnen wurden
von der Anlegerechnung und der Fotoprojektion zerrissen.

1. `Loch`: eine Randschleife mit höchstens `LOCH_PUNKTE` Punkten und höchstens `LOCH_UMFANG` m Umfang ist ein Loch und wird mit einem Fächer aus ihrem Mittelpunkt geschlossen
   (neue Dreiecke hinten angehängt, Windung gegen die Nachbarfläche; der Mittelpunkt erbt UV, Haut und Farbe vom ersten Punkt der Schleife).
2. `Rand`: eine längere Schleife (Saum, Ärmelende, Kragen) wird als Linienzug geglättet (Taubin, `RAND_SCHRITTE`), die Sägezähne verschwinden. Die Punkte dahinter bleiben, wo sie sind.

Verschweißt wird nach Lage (UV-Nähte verdoppeln Punkte); verändert wird jeder Originalpunkt einer Lage gleich.

    neu = Netzputz.reparieren(punkte, dreiecke, uv=None)    # {punkte, dreiecke, uv, herkunft, loecher, raender}; herkunft[i]: Originalpunkt (neue Mittelpunkte: der erste der Schleife)"""

from collections import defaultdict

import numpy as np

__all__ = ['Netzputz']


class Netzputz:
    LOCH_PUNKTE = 40
    LOCH_UMFANG = 0.35
    RAND_SCHRITTE = 40
    LAM, MU = 0.5, -0.53

    @staticmethod
    def _schleifen(dreiecke):
        """([geordnete Schleifen aus verschweißten Punktnummern], gerichtete Kanten der Fläche) — nur einfache Schleifen (jeder Randpunkt mit genau zwei Randnachbarn)."""
        gerichtet = set()
        zahl = defaultdict(int)
        for a, b, c in dreiecke:
            for u, v in ((a, b), (b, c), (c, a)):
                gerichtet.add((u, v))
                zahl[(min(u, v), max(u, v))] += 1
        nachbar = defaultdict(list)
        for (u, v), n in zahl.items():
            if n == 1:
                nachbar[u].append(v)
                nachbar[v].append(u)
        gesehen, schleifen = set(), []
        for start in sorted(nachbar):
            if start in gesehen or len(nachbar[start]) != 2:
                continue
            kette, vorher, jetzt = [start], None, start
            while True:
                gesehen.add(jetzt)
                weiter = [n for n in nachbar[jetzt] if n != vorher]
                if not weiter:
                    break
                nach = weiter[0]
                if nach == start or nach in gesehen or len(nachbar[nach]) != 2:
                    break
                kette.append(nach)
                vorher, jetzt = jetzt, nach
            if len(kette) >= 3:
                schleifen.append(kette)
        return schleifen, gerichtet

    @classmethod
    def _glaetten(cls, linie):
        """Geschlossener Linienzug (n, 3): Taubin ohne Schrumpfen."""
        p = linie.copy()
        for _ in range(cls.RAND_SCHRITTE):
            p = p + cls.LAM * (0.5 * (np.roll(p, 1, axis=0) + np.roll(p, -1, axis=0)) - p)
            p = p + cls.MU * (0.5 * (np.roll(p, 1, axis=0) + np.roll(p, -1, axis=0)) - p)
        return p

    @classmethod
    def teil(cls, t, dreiecke, haut):
        """Für `Standmodellglb.teile`: das Teil `t` (Wörterbuch aus `Kleidermodellbau.teile`) geputzt → (t, dreiecke, haut) mit neuen Punkten, Dreiecken (neue hinten angehängt: die
        Gruppen behalten ihre Bereiche, die Löcher landen im flachen Rest-Netz), UV und Hautgewichten (neue Mittelpunkte erben vom ersten Punkt ihrer Schleife); Normalen werden neu gerechnet."""
        uv = None if t.get('uv') is None else np.asarray(t['uv'], dtype=np.float64).reshape(-1, 2)
        neu = cls.reparieren(t['punkte'], dreiecke, uv)
        ersatz = dict(t, punkte=neu['punkte'], dreiecke=neu['dreiecke'], normalen=None)
        if uv is not None:
            ersatz['uv'] = neu['uv']
        h = neu['herkunft']
        return ersatz, neu['dreiecke'], (haut[0][h], haut[1][h])

    @classmethod
    def reparieren(cls, punkte, dreiecke, uv=None):
        p = np.asarray(punkte, dtype=np.float64).copy()
        d = np.asarray(dreiecke, dtype=np.int64).reshape(-1, 3)
        schluessel, erste, inv = np.unique(np.round(p * 1e5).astype(np.int64), axis=0, return_index=True, return_inverse=True)
        inv = inv.reshape(-1)
        wd = inv[d]
        ok = (wd[:, 0] != wd[:, 1]) & (wd[:, 1] != wd[:, 2]) & (wd[:, 0] != wd[:, 2])
        schleifen, gerichtet = cls._schleifen(wd[ok])
        wp = p[erste]
        herkunft = list(range(len(p)))
        neue_p, neue_d, neue_uv = [], [], []
        loecher = raender = 0
        n = len(p)
        for s in schleifen:
            q = wp[s]
            umfang = float(np.linalg.norm(q - np.roll(q, -1, axis=0), axis=1).sum())
            if len(s) <= cls.LOCH_PUNKTE and umfang <= cls.LOCH_UMFANG:
                mitte = q.mean(axis=0)
                neue_p.append(mitte)
                for i, a in enumerate(s):
                    b = s[(i + 1) % len(s)]
                    # die Fläche läuft a→b oder b→a; das neue Dreieck läuft gegen sie
                    kante = (erste[a], erste[b]) if (a, b) not in gerichtet else (erste[b], erste[a])
                    neue_d.append([kante[0], kante[1], n])
                herkunft.append(int(erste[s[0]]))
                if uv is not None:
                    neue_uv.append(np.asarray(uv)[erste[s[0]]])
                n += 1
                loecher += 1
            elif len(s) >= 6:
                glatt = cls._glaetten(q)
                for a, ziel in zip(s, glatt, strict=True):
                    p[inv == a] = ziel
                raender += 1
        if neue_p:
            p = np.vstack([p, np.asarray(neue_p)])
            d = np.vstack([d, np.asarray(neue_d, dtype=np.int64)])
        aus = {'punkte': p, 'dreiecke': d, 'herkunft': np.asarray(herkunft, dtype=np.int64), 'loecher': loecher, 'raender': raender}
        if uv is not None:
            aus['uv'] = np.vstack([np.asarray(uv), np.asarray(neue_uv)]) if neue_uv else np.asarray(uv)
        return aus
