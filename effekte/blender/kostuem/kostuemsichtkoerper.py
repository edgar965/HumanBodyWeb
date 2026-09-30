# -*- coding: utf-8 -*-
"""Kostuemsichtkoerper — der Sichtkörper der Vorlage als Netz: die Silhouetten aller Fotos, in Schichten zu einem Mantel.

Die Umriss-Hülle (`Kostuemhuelle`) sagt für jeden Punkt im Raum, ob ihn alle Fotos für Figur halten. Hier wird aus ihr eine
Fläche: Je Höhe (`SCHICHT`) eine Schnittfläche — Mitte aus einem groben Raster, dann 72 Strahlen von der Mitte bis an den
Rand der Hülle —, die Schnittkurven übereinander zu einem Netz (`Rohr`: Ringe → Vierecke, Unterteilung, Stoffdicke).
Der Umriss stimmt dann in jeder der Ansichten (Abweichung nur noch die Öffnung der Masken und die Stufen der Schichten); was
innen liegt — Ärmel, Kapuze, Bart, Haar — kommt aus der Fototextur (`Fototextur`), nicht aus der Form.

Voraussetzung ist, dass jede Schnittfläche von ihrer Mitte aus „sternförmig" ist (der Strahl verlässt die Hülle nur einmal): Der
Stab, der als dünnes Teil neben dem Körper steht, fiele weg (die Masken sind geöffnet) — er bleibt ein eigenes Teil.
"""

import numpy as np

from effekte.blender.kostuem.rohr import Rohr

__all__ = ['Kostuemsichtkoerper']


class Kostuemsichtkoerper:
    #: Höhenabstand der Schnittflächen (m) und Strahlen je Fläche.
    SCHICHT = 0.015
    STRAHLEN = 72
    #: Suchraum je Fläche: Raster (Kantenlänge m, Schritt m) für die Mitte, größter Strahl (m), Strahlschritt (m).
    RASTER = (1.5, 0.03)
    STRAHL_MAX = 0.85
    STRAHL_SCHRITT = 0.012
    #: Glättung der Radien über die Höhe (Gewichte oben/Mitte/unten) und über den Winkel.
    GLAETTEN_Z = (0.25, 0.5, 0.25)
    #: Schichten, unter denen die Hülle leer ist (Knöchel: dünner als die Öffnung der Maske), trennen Teile; Teile mit
    #: weniger Schichten (Schuhe, Stabkopf) bleiben weg — dafür gibt es eigene Teile.
    MINDESTSCHICHTEN = 20

    def __init__(self, huelle, boden, hoehe, farbe):
        """`huelle`: `Kostuemhuelle` mit Normierung; `boden`/`hoehe`: Fußboden und Körperhöhe (m); `farbe`: sRGB."""
        self.huelle = huelle
        self.boden = boden
        self.hoehe = hoehe
        self.farbe = farbe

    def _mitte(self, z):
        """Schwerpunkt der Hülle in Höhe `z` (Raster) oder None, wenn dort nichts liegt."""
        kante, schritt = self.RASTER
        achse = np.arange(-kante / 2, kante / 2 + 1e-9, schritt)
        gx, gy = np.meshgrid(achse, achse)
        punkte = np.column_stack([gx.ravel(), gy.ravel(), np.full(gx.size, z)])
        drin = self.huelle.innen(punkte) >= self.huelle.ANTEIL
        if drin.sum() < 6:
            return None
        # Der Median, nicht der Mittelwert: In Hutspitzenhöhe steht neben dem Hut der Stabkopf — der Mittelwert läge
        # zwischen beiden, außerhalb der Hülle. Fällt auch der Median daneben, nimmt man den nächsten Punkt darin.
        innen = punkte[drin, :2]
        mitte = np.median(innen, axis=0)
        naechster = innen[np.argmin(np.linalg.norm(innen - mitte, axis=1))]
        return float(naechster[0]), float(naechster[1])

    def _radien(self, mitte, z):
        """Der erste Austritt aus der Hülle je Strahl (m) — bis auf Millimeter eingegabelt; 0 = Mitte nicht drin."""
        winkel = np.linspace(0.0, 2 * np.pi, self.STRAHLEN, endpoint=False)
        richtung = np.column_stack([np.cos(winkel), np.sin(winkel)])
        r = np.arange(0.0, self.STRAHL_MAX, self.STRAHL_SCHRITT)
        xy = np.asarray(mitte) + richtung[:, None, :] * r[None, :, None]
        raster = np.concatenate([xy, np.full(xy.shape[:2] + (1,), z)], axis=2).reshape(-1, 3)
        drin = (self.huelle.innen(raster) >= self.huelle.ANTEIL).reshape(xy.shape[:2])
        if not drin[:, 0].all():
            return None
        erster = np.argmax(~drin, axis=1)
        erster = np.where(drin.all(axis=1), len(r) - 1, erster)
        lo, hi = r[np.maximum(erster - 1, 0)], r[erster]
        for _ in range(4):
            m = (lo + hi) / 2
            xy_m = np.asarray(mitte) + richtung * m[:, None]
            gut = self.huelle.innen(np.column_stack([xy_m, np.full(len(m), z)])) >= self.huelle.ANTEIL
            lo, hi = np.where(gut, m, lo), np.where(gut, hi, m)
        return lo

    def schichten(self):
        """[(z, mitte, radien)] von unten nach oben, in Teile getrennt: [[…], […]]."""
        teile, aktuell = [], []
        for z in np.arange(self.boden + 0.01, self.boden + 1.15 * self.hoehe, self.SCHICHT):
            mitte = self._mitte(z)
            radien = self._radien(mitte, z) if mitte is not None else None
            if radien is None:
                if aktuell:
                    teile.append(aktuell)
                aktuell = []
                continue
            aktuell.append((float(z), mitte, radien))
        if aktuell:
            teile.append(aktuell)
        return [t for t in teile if len(t) >= self.MINDESTSCHICHTEN]

    #: Fenster der Median-Filter (ungerade): Ein Strahl, der durch eine Lücke zwischen Arm und Körper der Silhouette
    #: austritt, liefert einen Ausreißer (Zacke oder Delle) — der Median entfernt ihn, der Mittelwert verschmierte ihn.
    MEDIAN_WINKEL = 11
    MEDIAN_HOEHE = 9

    @staticmethod
    def _median(radien, fenster, achse, ring):
        """Gleitender Median über `fenster` Werte entlang `achse` (`ring`: der Rand schließt sich, sonst wird er wiederholt)."""
        halb = fenster // 2
        if ring:
            stapel = [np.roll(radien, d, axis=achse) for d in range(-halb, halb + 1)]
        else:
            breit = np.pad(
                radien, [(halb, halb) if a == achse else (0, 0) for a in range(radien.ndim)], mode='edge'
            )
            n = radien.shape[achse]
            stapel = [np.take(breit, range(d, d + n), axis=achse) for d in range(fenster)]
        return np.median(np.stack(stapel), axis=0)

    def _glaetten(self, teil):
        radien = np.array([r for _, _, r in teil])
        aus = self._median(radien, self.MEDIAN_WINKEL, 1, ring=True)
        aus = self._median(aus, self.MEDIAN_HOEHE, 0, ring=False)
        a, b, c = self.GLAETTEN_Z
        glatt = aus.copy()
        glatt[1:-1] = a * aus[:-2] + b * aus[1:-1] + c * aus[2:]
        # entlang des Rings: (0,25 / 0,5 / 0,25)
        return 0.25 * np.roll(glatt, 1, axis=1) + 0.5 * glatt + 0.25 * np.roll(glatt, -1, axis=1)

    def bauen(self):
        """→ Liste von Blender-Objekten (`Rohr`), je zusammenhängendem Teil eins."""
        winkel = np.linspace(0.0, 2 * np.pi, self.STRAHLEN, endpoint=False)
        objekte = []
        for nr, teil in enumerate(self.schichten()):
            radien = self._glaetten(teil)
            rohr = Rohr('Sichtkoerper_%d' % nr, self.farbe)
            rohr.SEGMENTE = self.STRAHLEN
            # von oben nach unten (wie der Mantel): der Deckel schließt den ersten Ring, hier die Spitze
            for (z, mitte, _), r in reversed(list(zip(teil, radien, strict=True))):
                rohr.ringe.append(
                    np.column_stack(
                        [mitte[0] + r * np.cos(winkel), mitte[1] + r * np.sin(winkel), np.full(len(r), z)]
                    )
                )
            # Ohne Stoffdicke: eine Fläche genügt (von außen gesehen), und die Hälfte der Punkte spart 15 MB GLB. Die Ringe laufen
            # von oben nach unten, gegen den Uhrzeigersinn: Die Flächennormalen zeigen dann NACH INNEN (mit Stoffdicke dreht das
            # Solidify um) — die Fototextur gewichtet nach der Normalen, mit falscher Richtung nähme sie die Rückseite.
            obj = rohr.bauen(dicke=0.0, glaetten=1, deckel_oben=True)
            obj.data.flip_normals()
            objekte.append(obj)
        return objekte
