# -*- coding: utf-8 -*-
"""Schammessungrahmen — das Koordinatensystem und die Zonen der Scham-Messung (10.10.2026).

Edgar: „mach kein Raten und Bildvergleich, sondern Messungen … die Geometrie an verschiedenen Punkten". Alle Messungen der Klasse `Schammessung` lesen ihre Orte aus EINEM Rahmen, damit
„Hügel", „Lippen" und „Damm" in Form, Naht und Textur dieselben Punkte meinen:

    Mitte    Mittelpunkt des Rings (Lochrand in der Haut)
    vorne    mittlere Hautnormale am Ring (nach außen); `quer` = Richtung +x der Figur senkrecht dazu, `laengs` = nach oben (Hügel → Damm)
    Zonen    Drittel der Längsausdehnung des Stücks (oben Hügel, mitte Lippen, unten Damm), je Mitte (|quer| < `MITTE_M`) und seitlich

Keine Zahl hängt an einem Modell: der Rahmen kommt aus dem Ring und dem Stück.
"""
import numpy as np

__all__ = ['Schammessungrahmen']


class Schammessungrahmen:
    #: Halbbreite des Mittelstreifens (m).
    MITTE_M = 0.012
    #: Namen der Drittel von oben nach unten und der beiden Streifen.
    DRITTEL = ('Hügel (oben)', 'Lippen (mitte)', 'Damm (unten)')
    STREIFEN = ('Mitte', 'seitlich')

    def __init__(self, mitte, vorne, stueck_punkte):
        self.mitte = np.asarray(mitte, dtype=np.float64)
        v = np.asarray(vorne, dtype=np.float64)
        self.vorne = v / np.linalg.norm(v)
        e1 = np.cross([0.0, 1.0, 0.0], self.vorne)
        self.quer = e1 / np.linalg.norm(e1)
        self.laengs = np.cross(self.vorne, self.quer)
        k = self.koordinaten(np.asarray(stueck_punkte, dtype=np.float64))
        #: Ausdehnung des Stücks `(min, max)` je Achse quer, längs, vorne (m).
        self.grenzen = [(float(k[:, a].min()), float(k[:, a].max())) for a in range(3)]

    @classmethod
    def von_ring(cls, figur_punkte, figur_normalen, ring_punkte, stueck_punkte):
        """Rahmen aus den Ringpunkten der Haut (Nummern in `figur_punkte`) und den Punkten des Stücks."""
        ring = np.asarray(ring_punkte, dtype=np.int64)
        return cls(np.asarray(figur_punkte)[ring].mean(axis=0), np.asarray(figur_normalen)[ring].mean(axis=0), stueck_punkte)

    def koordinaten(self, punkte):
        """`(N, 3)`: quer, längs, vorne (m) relativ zur Mitte."""
        d = np.asarray(punkte, dtype=np.float64) - self.mitte
        return np.column_stack([d @ self.quer, d @ self.laengs, d @ self.vorne])

    def spiegeln(self, punkte):
        """Die Punkte an der Ebene durch die Mitte senkrecht zu `quer` gespiegelt."""
        p = np.asarray(punkte, dtype=np.float64)
        return p - 2.0 * (((p - self.mitte) @ self.quer)[:, None]) * self.quer

    def zone(self, punkte):
        """Zonennummer je Punkt: `drittel * 2 + streifen` (Drittel 0 = oben, Streifen 0 = Mitte)."""
        k = self.koordinaten(punkte)
        unten, oben = self.grenzen[1]
        rel = np.clip((oben - k[:, 1]) / max(oben - unten, 1e-9), 0.0, 0.999999)
        return (rel * 3).astype(np.int64) * 2 + (np.abs(k[:, 0]) >= self.MITTE_M).astype(np.int64)

    def zonenname(self, nummer):
        return '%s, %s' % (self.DRITTEL[nummer // 2], self.STREIFEN[nummer % 2])

    def tabelle(self, werte_mm, punkte):
        """Zeilen `{zone, n, median, p90, max}` (mm) der Werte je Zone; leere Zonen entfallen."""
        werte, zone = np.asarray(werte_mm, dtype=np.float64), self.zone(punkte)
        zeilen = []
        for z in range(6):
            w = werte[zone == z]
            if len(w):
                zeilen.append({'zone': self.zonenname(z), 'n': int(len(w)), 'median': round(float(np.median(w)), 2),
                               'p90': round(float(np.percentile(w, 90)), 2), 'max': round(float(w.max()), 2)})
        return zeilen

    @staticmethod
    def statistik(werte_mm):
        """`{n, median, p90, max}` (mm) — oder None ohne Werte."""
        w = np.asarray(werte_mm, dtype=np.float64)
        w = w[np.isfinite(w)]
        if not len(w):
            return None
        return {'n': int(len(w)), 'median': round(float(np.median(w)), 2), 'p90': round(float(np.percentile(w, 90)), 2), 'max': round(float(w.max()), 2)}
