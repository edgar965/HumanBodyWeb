# -*- coding: utf-8 -*-
"""Meshfigurabnahmekoerper — Abnahme der Figur gegen das Netz: Abstand je Körperteil, Stoff im Körper, Maße (13.10.2026).

Die drei Messungen stammen aus Wegwerfskripten dieses Tages (`koerperteil_abstand.py`, `kleid_durchstich.py`, `masse_messen.py`) und laufen jetzt bei jedem Lauf — wer zwei Läufe oder zwei Einstellungen
vergleichen will (Jobseite Mesh-3D, „Varianten"), liest sie aus `ergebnis.abnahme` statt sie von Hand zu rechnen.

* **Abstand je Körperteil:** je Netzfläche, die Sapiens (≥ `MIN_STIMMEN` Pixel) einer Klasse zuordnet, der Abstand der Flächenmitte zum nächsten Käfigpunkt (`posiert.npy`, Lage der Erkennung); Median in mm.
  Zeigt Hände und Füße, die neben dem Netz stehen, unabhängig von Farbe und Stoff. Ohne Segmentierung (`sapiens_flaechen.npz`) fehlt sie.
* **Stoff im Körper:** wie tief die Kleidungspunkte unter der Oberfläche des Käfigs liegen (Vorzeichen: Vertexnormale am nächsten Käfigpunkt; negativ = der Körper ragt durch den Stoff). Näherung (nächster
  Punkt statt nächste Fläche), gut auf Zentimeter. Anteil unter 0 mm und unter −5 mm, dazu je Höhenband von 0,2 m.
* **Maße:** Umfänge und Breiten der Endfigur in Ruhe (`G9massband`, `genesis_ende.npz`) — an der Figur, nicht am Netz: das Netz ist bekleidet.
"""

import numpy as np

__all__ = ['Meshfigurabnahmekoerper']


class Meshfigurabnahmekoerper:
    #: Sapiens-Klassen je Körperteil (Nummern der 28 Klassen, `sapiens_klassen.py`).
    KLASSEN = {'Gesicht': (2,), 'Hand L': (5,), 'Hand R': (14,), 'Unterarm L': (6,), 'Unterarm R': (15,), 'Fuß L': (4,), 'Fuß R': (13,), 'Schuh L': (8,), 'Schuh R': (17,),
               'Socke L': (9,), 'Socke R': (18,), 'Unterschenkel L': (7,), 'Unterschenkel R': (16,), 'Torso': (21,)}
    MIN_STIMMEN = 4.0
    #: Weniger Flächen einer Klasse geben keinen Median.
    MIN_FLAECHEN = 30
    BAND_M = 0.2
    #: Die Maße der Endfigur, die der Vergleich zeigt (Schlüssel von `G9massband.messen`).
    MASSE = ('groesse', 'brust_umfang', 'taille_umfang', 'huefte_umfang', 'oberarm_umfang', 'unterarm_umfang', 'oberschenkel_umfang', 'knie_umfang', 'wade_umfang', 'knoechel_umfang',
             'schulter_breite', 'huefte_breite')

    def __init__(self, lauf, scan):
        self.ablage = lauf.ablage
        self.scan = scan

    def abstand_je_teil(self):
        """`{Körperteil: mm oder None}` — oder `{'hinweis': …}` ohne Segmentierung."""
        from scipy.spatial import cKDTree

        pfad = self.ablage.arbeit('sapiens_flaechen.npz')
        if not pfad.is_file():
            return {'hinweis': 'ohne Segmentierung nicht messbar'}
        flaechen, punkte = np.asarray(self.scan.flaechen), np.asarray(self.scan.punkte)
        with np.load(pfad) as d:
            klassen = d['klassen']
        if len(klassen) != len(flaechen):
            return {'hinweis': 'Flächenzahl der Segmentierung passt nicht zum Netz'}
        abstand, _ = cKDTree(np.load(self.ablage.arbeit('posiert.npy')).astype(np.float64)).query(punkte[flaechen].mean(axis=1))
        gesehen = klassen.max(axis=1) >= self.MIN_STIMMEN
        stark = klassen.argmax(axis=1)
        aus = {}
        for name, nummern in self.KLASSEN.items():
            m = gesehen & np.isin(stark, nummern)
            aus[name] = round(1000.0 * float(np.median(abstand[m])), 1) if m.sum() >= self.MIN_FLAECHEN else None
        return aus

    def stoff_im_koerper(self):
        """`{punkte, unter_0_prozent, unter_5mm_prozent, median_mm, baender}` — oder `{'hinweis': …}` ohne Kleidungsmaske."""
        from scipy.spatial import cKDTree

        maske = self.ablage.arbeit('kleidung_maske.npz')
        if not maske.is_file():
            return {'hinweis': 'keine Kleidungsmaske'}
        flaechen, punkte = np.asarray(self.scan.flaechen), np.asarray(self.scan.punkte)
        with np.load(maske) as d:
            kleidung = d['kleidung']
        if len(kleidung) != len(flaechen) or not kleidung.any():
            return {'hinweis': 'keine Kleidung erkannt'}
        kaefig = np.load(self.ablage.arbeit('posiert.npy')).astype(np.float64)
        with np.load(self.ablage.arbeit('genesis_ende.npz')) as d:
            dreiecke = d['dreiecke']
        normalen = self._normalen(kaefig, dreiecke)
        ids = np.unique(flaechen[kleidung].ravel())
        _, nahe = cKDTree(kaefig).query(punkte[ids])
        tiefe = np.einsum('ij,ij->i', punkte[ids] - kaefig[nahe], normalen[nahe])           # Meter, negativ = im Körper
        hoehe = punkte[ids, 1]
        baender = []
        for von in np.arange(0.0, 2.2, self.BAND_M):
            m = (hoehe >= von) & (hoehe < von + self.BAND_M)
            if m.sum() >= 30:
                baender.append({'von_m': round(float(von), 1), 'punkte': int(m.sum()), 'unter_0_prozent': round(100.0 * float((tiefe[m] < 0).mean()), 1),
                                'unter_5mm_prozent': round(100.0 * float((tiefe[m] < -0.005).mean()), 1), 'median_mm': round(1000.0 * float(np.median(tiefe[m])), 1)})
        return {'punkte': int(len(ids)), 'unter_0_prozent': round(100.0 * float((tiefe < 0).mean()), 2), 'unter_5mm_prozent': round(100.0 * float((tiefe < -0.005).mean()), 2),
                'median_mm': round(1000.0 * float(np.median(tiefe)), 1), 'baender': baender}

    @staticmethod
    def _normalen(kaefig, dreiecke):
        """Vertexnormalen des Käfigs, nach außen (Vorzeichen des Volumens)."""
        n = np.zeros_like(kaefig)
        v0, v1, v2 = kaefig[dreiecke[:, 0]], kaefig[dreiecke[:, 1]], kaefig[dreiecke[:, 2]]
        fn = np.cross(v1 - v0, v2 - v0)
        for k in range(3):
            np.add.at(n, dreiecke[:, k], fn)
        n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
        if np.einsum('ij,ij->i', v0, np.cross(v1, v2)).sum() < 0:
            n = -n
        return n

    def masse(self):
        """`{Maß: cm}` der Endfigur in Ruhe (`G9massband`)."""
        from Genesis9.haut import G9haut
        from Genesis9.massband import G9massband

        with np.load(self.ablage.arbeit('genesis_ende.npz'), allow_pickle=True) as d:
            punkte = d['punkte'].astype(np.float64) + d['jcm'].astype(np.float64)
            gelenke, knochen = d['kopf'].astype(np.float64), [str(n) for n in d['knochen']]
        gemessen = G9massband.genesis(punkte, G9haut.holen(), gelenke, knochen).messen()
        return {m: round(float(gemessen[m]), 1) for m in self.MASSE if isinstance(gemessen.get(m), (int, float))}
