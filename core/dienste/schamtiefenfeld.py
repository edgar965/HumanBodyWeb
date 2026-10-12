# -*- coding: utf-8 -*-
"""Schamtiefenfeld — das Scham-Stück der Tiefe der Haut ringsum anpassen (11.10.2026, „cute girl alt4").

Edgar, 11.10.2026, zu „cute girl alt3": „die Scham ist ca. 1 cm tiefer als die Haut daneben, an den Körper von der Tiefe anpassen" — danach „alt4 ist schon fast perfekt".

Gemessen (`ProjektTemp/_wegwerf/tiefe_profil.py`, Längsschnitte; `absatz_messen.py`): das Stück ist aus dem Original der .blend geschnitten, die Haut der Figur steht seitlich am Ring
10–15 mm davor (Lücke je Ringpunkt Median 2–3 mm, p90 9–10 mm, größte 12–14 mm). Das Randband (höchstens 8 mm) und das Ausklingen der Naht (10–16 mm) überbrücken das nicht: am Rand ist das Stück
bündig, 15–25 mm weiter innen liegt es 5–10 mm hinter der Haut — eine Wand.

Hier läuft die Lücke am Rand als weiches Feld ins Stück: harmonische Fortsetzung der Lücke auf dem Netz (Kotangens-Gewichte, Rand fest), mit dem Netzweg vom Ring ab eingeblendet
(Hermite über `EINBLENDEN_MM`). Dazwischen führt das Ausklingen der Naht (`Blendimportschamnaht.BAND_MM` = `NAHT_BAND_MM`) den Rand lokal starr mit; die Orientierung der Randdreiecke bleibt
die des Originals. Das Relief (Lippen, Falten) bleibt, es verschiebt sich als Ganzes mit dem Feld. Das Randband zur Haut entfällt (`RANDBAND_MAX_MM`).

Messreihe an „cute girl" (alte Figur, `ProjektTemp/_wegwerf/alt4_probe.py`; Knick über die Naht p90 / größter / Kanten über 60° · Absatz hinter dem Ring bei 15 und 25 mm: Punkte unter −5 mm von 100):
    alt3 (Band 16 / 8, Auslauf 16, kein Feld)                      39,3° / 73,4° / 2  ·  9 und 21
    Feld von der ersten Reihe an, Auslauf 0,5                       59,5° / 82,6° / 10 ·  6 und 9    — die Naht wird schlechter: die Randdreiecke werden gemittelt statt mitgeführt
    Feld nach alt3-Rand (Band 16 / 8 + Auslauf 16 + Feld)           46,3° / 75,0° / 5  ·  3 und 17    — das Randband nimmt dem Feld die Lücke
    Auslauf 12, Feld über 12 mm eingeblendet                        36,5° / 55,3° / 0  ·  7 und 9
    **Auslauf 16, Feld über 16 mm eingeblendet (gewählt)**          38,0° / 55,0° / 0  ·  4 und 9
    Auslauf 16, Feld über 24 mm eingeblendet                        40,7° / 58,3° / 0  ·  7 und 10
Preis: Form Original → Modell p90 1,45 → 3,68 mm (das Stück wird bewusst an die Haut gehoben).
Ohne Django.
"""
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spl
from scipy.sparse import csgraph

__all__ = ['Schamtiefenfeld']


class Schamtiefenfeld:
    #: Anteil der Lücke am Rand, der als Feld ins Stück läuft (1 = ganz, 0 = kein Feld).
    STAERKE = 1.0
    #: Netzweg (mm) vom Ring, über den das Feld einblendet (Hermite). Davor führt allein das Ausklingen der Naht den Rand mit. 0 = das Feld wirkt von der ersten Reihe an.
    EINBLENDEN_MM = 16.0
    #: Auslauf des Einrastens (`Blendimportschamnaht.BAND_MM`) für Stücke mit Feld.
    NAHT_BAND_MM = 16.0
    #: Höchster Weg (mm) des Randbands zur Haut (`Blendimportscham.angleichen`) für Stücke mit Feld: keins — das Feld übernimmt die Tiefe.
    RANDBAND_MAX_MM = 0.0
    #: Durchgänge der Glättung der Lücke entlang des Rings (der nächste Punkt des alten Rands wechselt sonst von Ecke zu Ecke).
    GLAETTEN = 10
    #: Kotangens-Gewichte werden nach unten begrenzt (stumpfe Dreiecke gäben negative Gewichte, die das Maximumprinzip brechen).
    GEWICHT_MIN = 1e-3

    @staticmethod
    def randpunkte(dreiecke):
        """Nummern der Punkte an offenen Kanten (Kante in genau einem Dreieck)."""
        kanten = np.sort(np.concatenate([dreiecke[:, [0, 1]], dreiecke[:, [1, 2]], dreiecke[:, [2, 0]]]), axis=1)
        roh, zaehl = np.unique(kanten, axis=0, return_counts=True)
        return np.unique(roh[zaehl == 1])

    @staticmethod
    def aussenring(dreiecke):
        """`(Punktnummern des längsten Randrings in Reihenfolge, Zahl der übrigen Ringe)` — kleine Löcher im Innern sind kein Rand zur Haut."""
        kanten = np.sort(np.concatenate([dreiecke[:, [0, 1]], dreiecke[:, [1, 2]], dreiecke[:, [2, 0]]]), axis=1)
        roh, zaehl = np.unique(kanten, axis=0, return_counts=True)
        nachbarn = {}
        for a, b in roh[zaehl == 1].tolist():
            nachbarn.setdefault(a, []).append(b)
            nachbarn.setdefault(b, []).append(a)
        gesehen, ringe = set(), []
        for start in nachbarn:
            if start in gesehen:
                continue
            folge, vor, cur = [start], -1, start
            gesehen.add(start)
            while True:
                weiter = [x for x in nachbarn[cur] if x != vor]
                nxt = weiter[0] if weiter else nachbarn[cur][0]
                if nxt == start or nxt in gesehen:
                    break
                folge.append(nxt)
                gesehen.add(nxt)
                vor, cur = cur, nxt
            ringe.append(folge)
        ringe.sort(key=len, reverse=True)
        return np.asarray(ringe[0], dtype=np.int64), len(ringe) - 1

    @classmethod
    def gewichte(cls, punkte, dreiecke):
        """Symmetrische Matrix der Kotangens-Gewichte je Kante (halbe Summe der beiden gegenüberliegenden Winkel)."""
        n = len(punkte)
        zeilen, spalten, werte = [], [], []
        for k in range(3):
            i, j, o = dreiecke[:, (k + 1) % 3], dreiecke[:, (k + 2) % 3], dreiecke[:, k]
            u, v = punkte[i] - punkte[o], punkte[j] - punkte[o]
            kot = (u * v).sum(axis=1) / np.maximum(np.linalg.norm(np.cross(u, v), axis=1), 1e-18)
            zeilen += [i, j]
            spalten += [j, i]
            werte += [0.5 * kot, 0.5 * kot]
        w = sp.coo_matrix((np.concatenate(werte), (np.concatenate(zeilen), np.concatenate(spalten))), shape=(n, n)).tocsr()
        w.data = np.maximum(w.data, cls.GEWICHT_MIN)
        return w

    @classmethod
    def fortsetzen(cls, punkte, dreiecke, rand, wert):
        """`(F, bericht)`: die Fortsetzung der Randwerte `wert` (len(rand), 3) auf alle Punkte (Laplace = 0, Rand fest). Punkte ohne Dreieck und der Rand selbst bekommen 0."""
        benutzt = np.unique(dreiecke)
        innen = np.setdiff1d(benutzt, rand)
        w = cls.gewichte(punkte, dreiecke)
        laplace = (sp.diags(np.asarray(w.sum(axis=1)).ravel()) - w).tocsr()
        f = np.zeros((len(punkte), 3))
        f[innen] = spl.splu(laplace[innen][:, innen].tocsc()).solve(np.asarray(-(laplace[innen][:, rand] @ wert)))
        betrag = np.linalg.norm(f[innen], axis=1)
        return f, {'innen': int(len(innen)), 'rand': int(len(rand)), 'f_median_mm': round(float(np.median(betrag)) * 1000.0, 2), 'f_max_mm': round(float(betrag.max()) * 1000.0, 2)}

    @staticmethod
    def netzweg(punkte, dreiecke, rand):
        """Weg (mm) entlang der Kanten vom Ring zu jedem Punkt."""
        n = len(punkte)
        a = np.concatenate([dreiecke[:, 0], dreiecke[:, 1], dreiecke[:, 2]])
        b = np.concatenate([dreiecke[:, 1], dreiecke[:, 2], dreiecke[:, 0]])
        graph = sp.csr_matrix((np.linalg.norm(punkte[a] - punkte[b], axis=1) * 1000.0 + 1e-9, (a, b)), shape=(n, n))
        return csgraph.dijkstra(graph, directed=False, indices=rand, min_only=True)

    @staticmethod
    def entlang_glaetten(wert, durchgaenge):
        """Gleitendes Mittel (1-2-1) entlang des geschlossenen Rings, `durchgaenge` mal."""
        w = np.asarray(wert, dtype=np.float64).copy()
        for _ in range(int(durchgaenge)):
            w = 0.25 * np.roll(w, 1, axis=0) + 0.5 * w + 0.25 * np.roll(w, -1, axis=0)
        return w

    @classmethod
    def anwenden(cls, punkte, dreiecke, rand_vorher):
        """`(neue Punkte, bericht)`. `rand_vorher` (k, 3): die Punkte des Stück-Rands VOR dem Einrasten (`Blendimportschamnaht`, Lage auf dem Original). Die Lücke je Punkt des äußeren Rings
        des fertigen Stücks ist Randpunkt − nächster Punkt aus `rand_vorher`, entlang des Rings geglättet; sie läuft als Feld ins Stück, vom Ring ab über `EINBLENDEN_MM` eingeblendet.
        Der Rand selbst bewegt sich nicht (er liegt schon auf dem Ring)."""
        from scipy.spatial import cKDTree

        punkte = np.asarray(punkte, dtype=np.float64)
        rand, weitere = cls.aussenring(dreiecke)
        luecke = cls.entlang_glaetten(punkte[rand] - rand_vorher[cKDTree(rand_vorher).query(punkte[rand])[1]], cls.GLAETTEN)
        f, bericht = cls.fortsetzen(punkte, dreiecke, rand, luecke * float(cls.STAERKE))
        if cls.EINBLENDEN_MM > 0:
            t = np.clip(cls.netzweg(punkte, dreiecke, rand) / cls.EINBLENDEN_MM, 0.0, 1.0)
            f = f * (t * t * (3.0 - 2.0 * t))[:, None]
        neu = punkte + f
        n0 = np.cross(punkte[dreiecke[:, 1]] - punkte[dreiecke[:, 0]], punkte[dreiecke[:, 2]] - punkte[dreiecke[:, 0]])
        n1 = np.cross(neu[dreiecke[:, 1]] - neu[dreiecke[:, 0]], neu[dreiecke[:, 2]] - neu[dreiecke[:, 0]])
        betrag = np.linalg.norm(luecke, axis=1) * 1000.0
        bericht.update({'weitere_ringe': int(weitere), 'luecke_median_mm': round(float(np.median(betrag)), 2), 'luecke_p90_mm': round(float(np.percentile(betrag, 90)), 2),
                        'luecke_max_mm': round(float(betrag.max()), 2), 'umgeklappt': int(((n0 * n1).sum(axis=1) < 0.0).sum())})
        return neu, bericht
