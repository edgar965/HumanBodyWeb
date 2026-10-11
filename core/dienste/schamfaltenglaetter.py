# -*- coding: utf-8 -*-
"""Schamfaltenglaetter — Haarnadel-Falten im Innern eines Scham-Stücks glätten, ohne Ring und Naht anzufassen (11.10.2026).

BEFUND (Probebau „cute girl Daz Scham", `falten_herkunft.py`): 283 von 12.430 Kanten (2,28 %, Schwelle 2 %) knicken über 90° — nur 57 davon stehen schon im rohen Geograft (213 = 1,71 %),
225 entstehen neu bei der Anpassung (roh im Median 14°, danach 114°); die Anpassung selbst beseitigt 156 der geerbten. Die neuen liegen im Median 25 mm vom Ring (6 von 225 näher als 8 mm), und bei
146 von 283 ist das kleinere der beiden Dreiecke unter 0,02 mm² groß: Haarnadeln aus zwei Sliver-Dreiecken, wo das Original eine Falte hat, die das grobe Netz (≈ 4 mm) nicht trägt.
Frühere Versuche (10.10.–11.10.2026): Laplace-Glättung der Punkte nahe am Ring, schwerer als hier, verschlechterte die Naht; Laplace nur an den Falten (120°/5 und 90°/10 Schritte) senkte die Falten auf 1,7 %,
machte aber Naht und Form schlechter — dort war weder der Ring ausgenommen noch der Weg begrenzt. Ein Schritt für ALLE Faltenpunkte auf einmal senkte die Zahl hier nicht (283 → 283): was an einer
Falte hilft, schafft an der Nachbarkante eine neue.

HIER: Punkt für Punkt. Jeder Punkt an einer Falte (Ecken der beiden Dreiecke) probiert den halben und den ganzen Weg zum Mittel seiner Nachbarn und behält ihn nur, wenn die Zahl der Falten an seinen
Dreiecken (alle Kanten zu deren Nachbardreiecken) sinkt. Punkte, die weniger als `RING_ABSTAND_M` vom Ring liegen, bleiben stehen, und kein Punkt entfernt sich mehr als `MAX_SCHRITT_M` von seiner
Ausgangslage. Mehrere Durchgänge, bis nichts mehr besser wird.
"""
import numpy as np

__all__ = ['Schamfaltenglaetter']


class Schamfaltenglaetter:
    #: Kanten, an denen die Flächennormalen der beiden Dreiecke mehr als so viel Grad auseinanderstehen, gelten als Falte.
    GRENZE_GRAD = 90.0
    #: Punkte näher als das (m) am Ring bleiben stehen; kein Punkt entfernt sich weiter (m) von seiner Ausgangslage.
    RING_ABSTAND_M, MAX_SCHRITT_M = 0.008, 0.0015
    #: Versuchte Anteile des Wegs zum Mittel der Nachbarn (der erste, der Falten abbaut, gilt), höchste Zahl der Durchgänge.
    ANTEILE, DURCHGAENGE = (0.5, 1.0), 8

    @classmethod
    def glaetten(cls, punkte, dreiecke, ring):
        """`(neue Punkte, bericht)`; `bericht`: `{vorher, nachher, bewegt, max_mm}` (Zahl der Falten, bewegte Punkte, größter Weg). `ring`: `(K, 3)` Lage der Ringecken."""
        from scipy.spatial import cKDTree

        p = np.array(punkte, dtype=np.float64)
        d = np.asarray(dreiecke, dtype=np.int64).reshape(-1, 3)
        start = p.copy()
        frei = cKDTree(np.asarray(ring, dtype=np.float64)).query(p)[0] >= cls.RING_ABSTAND_M
        flaechen_am_punkt, nachbar_flaechen, nachbarn = cls._netz(d, len(p))
        n = cls._normalen(p, d)
        grenze = np.cos(np.radians(cls.GRENZE_GRAD))
        vorher = cls._zaehlen(n, nachbar_flaechen, range(len(d)), grenze) // 2          # jede Kante steht bei beiden Dreiecken
        for _durchgang in range(cls.DURCHGAENGE):
            geaendert = 0
            for v in cls._kandidaten(n, d, nachbar_flaechen, flaechen_am_punkt, frei, grenze):
                geaendert += cls._versuchen(p, start, n, d, v, flaechen_am_punkt[v], nachbar_flaechen, nachbarn[v], grenze)
            if not geaendert:
                break
        weg = np.linalg.norm(p - start, axis=1)
        nachher = cls._zaehlen(cls._normalen(p, d), nachbar_flaechen, range(len(d)), grenze) // 2
        return p, {'vorher': int(vorher), 'nachher': int(nachher), 'bewegt': int((weg > 0).sum()), 'max_mm': round(float(weg.max()) * 1000.0, 2)}

    @classmethod
    def _versuchen(cls, p, start, n, d, v, flaechen, nachbar_flaechen, nachbarn, grenze):
        """Punkt `v` auf den Wegen zum Mittel seiner Nachbarn probieren; sinkt die Zahl der Falten an seinen `flaechen`, bleibt der erste solche Weg → 1, sonst 0 (`p`, `n` ändern sich dann)."""
        vorher = cls._zaehlen(n, nachbar_flaechen, flaechen, grenze)
        if not vorher:
            return 0
        mittel = p[nachbarn].mean(axis=0)
        alt = p[v].copy()
        for anteil in cls.ANTEILE:
            weg = alt + anteil * (mittel - alt) - start[v]
            laenge = float(np.linalg.norm(weg))
            if laenge > cls.MAX_SCHRITT_M:
                weg *= cls.MAX_SCHRITT_M / laenge
            p[v] = start[v] + weg
            neu = cls._normalen(p, d[flaechen])
            alt_n = n[flaechen].copy()
            n[flaechen] = neu
            if cls._zaehlen(n, nachbar_flaechen, flaechen, grenze) < vorher:
                return 1
            n[flaechen] = alt_n
        p[v] = alt
        return 0

    @staticmethod
    def _netz(dreiecke, n_punkte):
        """`(Dreiecke je Punkt, Nachbardreiecke je Dreieck (über Kanten), Nachbarpunkte je Punkt)`."""
        am_punkt = [[] for _ in range(n_punkte)]
        nachbarn = [set() for _ in range(n_punkte)]
        kante = {}
        for f, (a, b, c) in enumerate(dreiecke):
            for x, y, z in ((a, b, c), (b, c, a), (c, a, b)):
                am_punkt[x].append(f)
                nachbarn[x] |= {int(y), int(z)}
                kante.setdefault((min(x, y), max(x, y)), []).append(f)
        nb = [[] for _ in range(len(dreiecke))]
        for paar in kante.values():
            if len(paar) == 2:
                nb[paar[0]].append(paar[1])
                nb[paar[1]].append(paar[0])
        return am_punkt, nb, [sorted(s) for s in nachbarn]

    @staticmethod
    def _normalen(punkte, dreiecke):
        """Einheitsnormalen der Dreiecke (entartete: Nullvektor)."""
        ecken = punkte[dreiecke]
        n = np.cross(ecken[:, 1] - ecken[:, 0], ecken[:, 2] - ecken[:, 0])
        laenge = np.linalg.norm(n, axis=1, keepdims=True)
        return np.where(laenge > 1e-30, n / np.maximum(laenge, 1e-30), 0.0)

    @classmethod
    def _zaehlen(cls, n, nachbar_flaechen, flaechen, grenze=None):
        """Zahl der Falten an den Kanten der `flaechen` zu ihren Nachbardreiecken (Kante zwischen zwei Dreiecken der Menge zählt doppelt — vorher wie nachher gleich)."""
        grenze = np.cos(np.radians(cls.GRENZE_GRAD)) if grenze is None else grenze
        return sum(int(n[f] @ n[g] < grenze) for f in flaechen for g in nachbar_flaechen[f])

    @classmethod
    def _kandidaten(cls, n, d, nachbar_flaechen, flaechen_am_punkt, frei, grenze):
        """Freie Punkte an Dreiecken mit einer Falte, die meisten Falten zuerst."""
        zahl = {}
        for f in range(len(d)):
            fa = sum(int(n[f] @ n[g] < grenze) for g in nachbar_flaechen[f])
            if fa:
                for v in d[f]:
                    zahl[int(v)] = zahl.get(int(v), 0) + fa
        return [v for v, _ in sorted(zahl.items(), key=lambda x: -x[1]) if frei[v]]
