# -*- coding: utf-8 -*-
"""Blendimportfeindetail — die Füllung einer Haut-Kachel trägt das Feindetail der gebackenen Haut (10.10.2026).

Edgar, 10.10.2026, mit Bild (Rainy ohne Hemd): „hast du die Haut und Textur auch hier interpoliert? Mach das besser." Gemessen an Rainy
(`ProjektTemp/_wegwerf/blendimport_massstab/haut_tonsprung.py`): In Kachel 1002 (Rumpf) liegt unter der Körperkante (0,911 m) keine gebackene Haut —
49,1 % der Insel sind Füllung (Ersatzkachel von „Mesh to 3D", `Blendimportfarbangleich`); in Kachel 1003 (Beine) alles. Der TON stimmt an der Grenze
(Lab-Abstand 0,9; Kachel 1004: 3,0), das DETAIL nicht: die mittlere senkrechte Helligkeitsableitung ist in der Füllung 0,02, in der gebackenen Haut
0,55 (1004: 0,54 gegen 0,76) — die Füllung ist glatt wie Plastik, die gebackene Haut hat Poren und Körnung.

HIER: Aus der gebackenen Haut (nicht dem Gesicht) wird EIN Muster geschnitten — ein Quadrat ganz gebackener Texel (`MUSTER_PX`, bei 8192 px) —, davon
der Hochpass der Helligkeit (Pixel minus Gaußtiefpass, `SIGMA_PX`) und auf die Füllung gelegt, gespiegelt gekachelt (an den Kanten der Kachel stoßen
gleiche Werte aufeinander, keine Naht). Das Muster hat Mittelwert 0: Ton und Helligkeit der Füllung bleiben, wie `Blendimportfarbangleich` sie legt.
Unter den Fenstern gewinnt das mit den wenigsten Kanten (99. Perzentil des Betrags): Tätowierung, Muttermal, Naht gehören nicht ins Muster
(Rainy trägt am Brustbein eine Tätowierung).

Nicht geprüft: wie das Muster am Browser wirkt — die Zahlen oben sind Zahlen der Kachel, nicht des Bildes.
"""

import numpy as np

__all__ = ['Blendimportfeindetail']


class Blendimportfeindetail:
    #: Seite des Musters in Pixeln bei einer Kachel von 8192 px; kleinere Kacheln rechnen mit entsprechend kleinerem Muster.
    MUSTER_PX = 512
    #: Breite des Gaußtiefpasses (Pixel bei 8192): was feiner ist, zählt als Detail.
    SIGMA_PX = 6.0
    #: Größte Abweichung des Details (Helligkeitsstufen von 255) — ein Ausreißer prägt sich sonst als Punkt in die Füllung ein.
    GRENZE = 14.0
    #: Ein Fenster, dessen 99. Perzentil des Details (Betrag, vor der Grenze) darüber liegt, enthält Kanten und fällt aus.
    KANTEN_MAX = 22.0
    #: Raster der Fenstersuche (Pixel je Zelle) und höchstens so viele Fenster je Kachel.
    ZELLE = 16
    KANDIDATEN = 24
    #: Zeilen je Streifen beim Anwenden (Speicher).
    STREIFEN = 512
    #: Helligkeit: Gewichte der Kanäle (Rec. 601).
    GEWICHT = (0.299, 0.587, 0.114)

    @classmethod
    def seite(cls, hoehe):
        """Die Seite des Musters für eine Kachel der Höhe `hoehe` (gerade, mindestens 32)."""
        return max(32, int(round(cls.MUSTER_PX * hoehe / 8192.0 / 2.0)) * 2)

    @classmethod
    def fenster(cls, gueltig, seite):
        """Mitten möglicher Fenster `[(Zeile, Spalte), …]`: Zellen, deren Abstand zur nächsten Fehlstelle mindestens die halbe Seite plus eine Zelle
        beträgt; höchstens `KANDIDATEN`, gleichmäßig über die Menge verteilt."""
        from scipy import ndimage

        z = cls.ZELLE
        h, w = gueltig.shape
        zelle = gueltig[:h // z * z, :w // z * z].reshape(h // z, z, w // z, z).all(axis=(1, 3))
        abstand = ndimage.distance_transform_edt(zelle) * z
        ok = np.argwhere(abstand >= seite / 2 + z)
        if not len(ok):
            return []
        schritt = max(1, len(ok) // cls.KANDIDATEN)
        return [(int(a * z + z // 2), int(b * z + z // 2)) for a, b in ok[::schritt][:cls.KANDIDATEN]]

    @classmethod
    def detail(cls, farbe, mitte, seite):
        """Das Detail (Hochpass der Helligkeit) des Fensters um `mitte` als `(seite, seite)` float32, unbegrenzt."""
        from scipy import ndimage

        halb = seite // 2
        a, b = mitte
        stueck = farbe[a - halb:a + halb, b - halb:b + halb].astype(np.float32)
        hell = stueck @ np.asarray(cls.GEWICHT, dtype=np.float32)
        sigma = max(1.0, cls.SIGMA_PX * farbe.shape[0] / 8192.0)
        return hell - ndimage.gaussian_filter(hell, sigma, mode='reflect')

    @classmethod
    def bestes(cls, farbe, gueltig):
        """`(Kanten, Muster)` — das kantenärmste Fenster der Kachel (Muster begrenzt auf `GRENZE`) — oder None ohne Fenster oder ohne ein Fenster
        unter `KANTEN_MAX`. `farbe` (H, W, 3) uint8, `gueltig` (H, W) bool: gebackene Texel."""
        seite = cls.seite(farbe.shape[0])
        beste = None
        for mitte in cls.fenster(gueltig, seite):
            d = cls.detail(farbe, mitte, seite)
            kanten = float(np.percentile(np.abs(d), 99))
            if kanten <= cls.KANTEN_MAX and (beste is None or kanten < beste[0]):
                beste = (kanten, d)
        if beste is None:
            return None
        return beste[0], np.clip(beste[1], -cls.GRENZE, cls.GRENZE).astype(np.float32)

    @staticmethod
    def spiegeln(n, seite):
        """Index `0 … n−1` → Index im Muster, gespiegelt gekachelt (… 0 1 … s−1 s−1 … 1 0 0 1 …)."""
        i = np.arange(n) % (2 * seite)
        return np.where(i >= seite, 2 * seite - 1 - i, i)

    @classmethod
    def anwenden(cls, farbe, stelle, muster):
        """Das gekachelte Muster auf die Texel `stelle` (H, W) bool von `farbe` (H, W, 3) uint8 legen — verändert `farbe` und gibt die Zahl der
        Texel zurück."""
        seite = muster.shape[0]
        zeilen, spalten = cls.spiegeln(farbe.shape[0], seite), cls.spiegeln(farbe.shape[1], seite)
        anzahl = 0
        for a in range(0, farbe.shape[0], cls.STREIFEN):
            b = min(a + cls.STREIFEN, farbe.shape[0])
            st = stelle[a:b]
            if not st.any():
                continue
            zusatz = muster[zeilen[a:b, None], spalten[None, :]]
            teil = farbe[a:b]
            teil[st] = np.clip(teil[st].astype(np.float32) + zusatz[st][:, None], 0, 255).astype(np.uint8)
            anzahl += int(st.sum())
        return anzahl
