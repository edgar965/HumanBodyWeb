# -*- coding: utf-8 -*-
"""Kleidhautfilter — welche Pixel eines Fotos für die Fotoprojektion eines Kleidungsstücks NICHT zählen, weil sie Haut zeigen (06.10.2026).

Die Teilmaske des Stücks wird um `Fotoprojektion.TOLERANZ` Pixel erweitert (der Umriss des Modells sitzt nie auf den Bildpunkt genau); neben dem Saum, am Ärmel und am Hals liegt dort Haut des Fotos. Sie landete als hautfarbene
Zellen in der Textur der Hose (Zelle für Zelle im Atlas des Fotostücks sichtbar, `kleidtexturen/…hose…foto_…png`) und im Render als hautfarbener Keil am Hosensaum hinten (Auftrag „Edgar - Sapiens", Iteration 1).

Das Maß ist der nächste Mittelpunkt in der FARBE (Lab a, b — ohne Helligkeit): ein Pixel zählt als Haut, wenn sein Farbton näher an dem der Haut liegt als an dem des Stücks, beide aus demselben Foto (Haut: unter der Maske des Körpers
im Render, Stück: unter seiner Teilmaske). Die Helligkeit bleibt draußen — in RGB galt der helle Glanz eines dunklen Satins (heller als sein Mittel, näher an der Haut) als Haut und die Hose verlor ihre Lichter (erste Fassung, gemessen
am Bild). Unterscheiden sich beide Farbtöne kaum (`MIN_ABSTAND`: ein hautfarbenes Hemd), gibt es keinen Ausschluss — ein Stück, das so aussieht wie die Haut, wird nie weggefiltert.

Der Farbton des Stücks kommt aus der REINSTEN Ansicht (`reinster`), nicht aus jeder für sich: Im Seitenfoto hängt die Hand vor der Hose und deckt 45 % ihrer Maske — das Mittel der Maske liegt dort an der Haut (Abstand 2,1 gegen 19,5 vorn),
der Filter schaltete sich ab, und die Hand landete als hautfarbener Fleck in der Textur der Hose (Auftrag „Edgar - Sapiens", 06.10.2026, erster Lauf mit dem Seitenfoto als Farbquelle).
"""

import numpy as np

__all__ = ['Kleidhautfilter']


class Kleidhautfilter:
    #: Kleinster Abstand der Farbtöne beider Mittel (Lab a, b), ab dem der Filter wirkt.
    MIN_ABSTAND = 10.0
    #: Mindestens so viele Pixel braucht eine Mittelfarbe (sonst ist sie keine).
    MIN_PIXEL = 50
    _WEISS = np.array([0.95047, 1.0, 1.08883])
    _M = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])

    @classmethod
    def ab(cls, farbe):
        """(…, 2): Lab a und b zu sRGB 0…1 (D65)."""
        c = np.clip(np.asarray(farbe, dtype=np.float64), 0.0, 1.0)
        linear = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
        xyz = (linear @ cls._M.T) / cls._WEISS
        f = np.where(xyz > 216.0 / 24389.0, np.cbrt(xyz), (24389.0 / 27.0 * xyz + 16.0) / 116.0)
        return np.stack([500.0 * (f[..., 0] - f[..., 1]), 200.0 * (f[..., 1] - f[..., 2])], axis=-1)

    @classmethod
    def _mittel(cls, farbe, maske):
        n = int(np.count_nonzero(maske))
        return farbe[maske].mean(axis=0) if n >= cls.MIN_PIXEL else None

    @classmethod
    def bezug(cls, foto_farbe, foto_maske, stueck_maske, koerper_maske):
        """(Farbton des Stücks, Farbton der Haut) als Lab (a, b) EINER Ansicht — oder None (zu wenig Pixel). Argumente wie `haut`."""
        farbe = np.asarray(foto_farbe, dtype=np.float64)
        figur = np.asarray(foto_maske, dtype=bool)
        stoff = cls._mittel(farbe, figur & np.asarray(stueck_maske, dtype=bool))
        haut = cls._mittel(farbe, figur & np.asarray(koerper_maske, dtype=bool))
        return None if stoff is None or haut is None else (cls.ab(stoff), cls.ab(haut))

    @classmethod
    def reinster(cls, bezuege):
        """Der Bezug mit dem größten Abstand zwischen Stück und Haut aus den Bezügen aller Ansichten (Liste von `bezug`, auch None) — oder None, wenn keiner `MIN_ABSTAND` erreicht.
        Das Stück hat in jeder Ansicht denselben Farbton; wo eine Hand oder ein Arm davor hängt (Seitenfoto: die Hand vor der Hose, 45 % der Maske), liegt sein Mittel an der Haut — dort taugt der Bezug nicht."""
        gueltig = [b for b in bezuege if b is not None]
        if not gueltig:
            return None
        beste = max(gueltig, key=lambda b: float(np.linalg.norm(b[0] - b[1])))
        return beste if float(np.linalg.norm(beste[0] - beste[1])) >= cls.MIN_ABSTAND else None

    @classmethod
    def haut(cls, foto_farbe, foto_maske, stueck_maske, koerper_maske, stoff_ab=None):
        """(H, B) bool: Foto-Pixel, deren Farbton näher an der Haut liegt als am Stück — oder None (zu wenig Pixel, Farbtöne zu ähnlich).
        `foto_farbe` (H, B, 3) sRGB 0…1, `foto_maske` (H, B) die Figur im Foto, `stueck_maske` (H, B) die Teilmaske des Stücks, `koerper_maske` (H, B) die Haut im Render (der Körper).
        `stoff_ab`: Farbton des Stücks (a, b) aus einer anderen, reineren Ansicht (`reinster`) statt aus der Maske dieser Ansicht."""
        farbe = np.asarray(foto_farbe, dtype=np.float64)
        if stoff_ab is None:
            eigen = cls.bezug(farbe, foto_maske, stueck_maske, koerper_maske)
            if eigen is None:
                return None
            stoff_ab, haut_ab = eigen
        else:
            haut = cls._mittel(farbe, np.asarray(foto_maske, dtype=bool) & np.asarray(koerper_maske, dtype=bool))
            if haut is None:
                return None
            stoff_ab, haut_ab = np.asarray(stoff_ab, dtype=np.float64), cls.ab(haut)
        if float(np.linalg.norm(stoff_ab - haut_ab)) < cls.MIN_ABSTAND:
            return None
        ab = cls.ab(farbe)
        return np.linalg.norm(ab - haut_ab, axis=-1) < np.linalg.norm(ab - stoff_ab, axis=-1)
