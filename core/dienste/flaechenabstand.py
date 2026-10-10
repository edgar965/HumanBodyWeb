# -*- coding: utf-8 -*-
"""Flaechenabstand — der Abstand von Punkten zur FLÄCHE eines Dreiecksnetzes, schnell auch für Punkte weit weg von ihr (10.10.2026).

Gemessen am Rosemary-Import (10.10.2026): `trimesh.proximity.closest_point` brauchte für 163.810 Körperpunkte gegen die Figur **22,5 Minuten**
und zeitweise 28 GB Arbeitsspeicher (192 Mio. Seitenfehler), obwohl derselbe Aufruf bei 14.000–54.000 Punkten 14–43 s kostete. Die
Ursache steht im Quelltext (`trimesh/proximity.py`, `closest_point`): je Punkt werden ALLE Dreiecke in einem Suchquader mit dem Abstand zum
nächsten Netzpunkt als Radius gesammelt, und die Kandidaten aller Punkte gehen in EINE Liste. Passt die Figur nicht zum Körper (Rosemarys
Körper war ein Torso ohne Beine, der Abstand median 81 mm, p95 230 mm), enthält der Quader je Punkt Hunderte bis Tausende Dreiecke —
Dreiecke × Punkte wird quadratisch.

Hier: je Punkt die `NAECHSTE` nächsten Netzpunkte (KD-Baum), dazu alle Dreiecke, die an ihnen hängen (an einem Netz aus Vierecken und
Dreiecken sind das ~6 je Punkt), und davon der EXAKTE Punkt-Dreieck-Abstand (`trimesh.triangles.closest_point`, dieselbe Rechnung wie
trimesh). Die Kosten wachsen nur mit der Punktzahl, nicht mit dem Abstand; die Punkte gehen blockweise durch (`BLOCK`), der Speicher
bleibt klein. Abweichung gegen `trimesh.proximity.closest_point`: `ProjektTemp/_wegwerf/asian/abstand_vergleich.py` und
`test_flaechenabstand.py`.
"""

import numpy as np

__all__ = ['Flaechenabstand']


class Flaechenabstand:
    #: Nachbarpunkte der Fläche je abgefragtem Punkt; ihre Dreiecke sind die Kandidaten.
    NAECHSTE = 4
    #: Punkte je Durchgang: Kandidaten ≈ BLOCK × NAECHSTE × 6 Dreiecke (neun Zahlen je Dreieck) — wenige Hundert MB höchstens.
    BLOCK = 20000

    @classmethod
    def abstand(cls, punkte, flaeche, dreiecke):
        """Abstand (in den Einheiten der Punkte) jedes Punkts zur Fläche. `flaeche` (V, 3) Netzpunkte, `dreiecke` (T, 3) Indizes."""
        from scipy.spatial import cKDTree
        from trimesh.triangles import closest_point

        punkte = np.asarray(punkte, dtype=np.float64).reshape(-1, 3)
        flaeche = np.asarray(flaeche, dtype=np.float64)
        dreiecke = np.asarray(dreiecke, dtype=np.int64)
        if not len(punkte):
            return np.zeros(0)
        baum = cKDTree(flaeche)
        eckpunkte = flaeche[dreiecke]
        start, dreieck_je_punkt = cls._dreiecke_je_punkt(dreiecke, len(flaeche))
        anzahl = np.diff(start)
        k = min(cls.NAECHSTE, len(flaeche))
        aus = np.empty(len(punkte))
        for a in range(0, len(punkte), cls.BLOCK):
            p = punkte[a:a + cls.BLOCK]
            abstand_punkt, nah = baum.query(p, k=k, workers=-1)
            nah = nah.reshape(len(p), -1)
            abstand_punkt = abstand_punkt.reshape(len(p), -1)
            je_punkt = anzahl[nah].sum(axis=1)                         # Kandidaten je Punkt
            kandidat = cls._ausrollen(start, dreieck_je_punkt, anzahl, nah.reshape(-1))
            besitzer = np.repeat(np.arange(len(p)), je_punkt)
            nah_punkt = closest_point(eckpunkte[kandidat], p[besitzer])
            d = np.linalg.norm(nah_punkt - p[besitzer], axis=1)
            # Kleinster Abstand je Punkt; ein Punkt ohne Kandidaten (nur lose Netzpunkte ohne Dreieck) behält den Abstand zum Netzpunkt.
            ergebnis = abstand_punkt[:, 0].copy()
            gueltig = je_punkt > 0
            anfang = np.cumsum(je_punkt) - je_punkt
            if gueltig.any():
                ergebnis[gueltig] = np.minimum.reduceat(d, anfang[gueltig])
            aus[a:a + len(p)] = ergebnis
        return aus

    @staticmethod
    def _dreiecke_je_punkt(dreiecke, punktzahl):
        """CSR-Liste: `start[v]:start[v+1]` ist der Bereich in `dreieck_je_punkt` mit den Dreiecken, die den Netzpunkt v tragen."""
        knoten = dreiecke.reshape(-1)
        dreieck = np.repeat(np.arange(len(dreiecke)), dreiecke.shape[1])
        ordnung = np.argsort(knoten, kind='stable')
        start = np.searchsorted(knoten[ordnung], np.arange(punktzahl + 1))
        return start, dreieck[ordnung]

    @staticmethod
    def _ausrollen(start, dreieck_je_punkt, anzahl, knoten):
        """Für jeden Netzpunkt in `knoten` seine Dreiecke, hintereinander (die Reihenfolge der Punkte bleibt)."""
        je_knoten = anzahl[knoten]
        gesamt = int(je_knoten.sum())
        if gesamt == 0:
            return np.zeros(0, dtype=np.int64)
        vor_dem_knoten = np.repeat(np.cumsum(je_knoten) - je_knoten, je_knoten)
        stelle = np.repeat(start[knoten], je_knoten) + (np.arange(gesamt) - vor_dem_knoten)
        return dreieck_je_punkt[stelle]
