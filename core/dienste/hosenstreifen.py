# -*- coding: utf-8 -*-
"""Hosenstreifen — das Muster des Seitenstreifens der Vorlage entlang der Außennaht beider Hosenbeine (04.10.2026).

Anlass (Edgar, 04.10.2026: „Hose (Textur-Streifen)", Original-Vergleich): Die Vorlage zeigt an der Außennaht jedes Beins vom Gürtel bis zum Saum EINEN Streifen — vorn eine rote Linie, dann
ein schmaler weißer Spalt, eine schwarze Linie, dahinter ein zweireihiges Schwarz-Weiß-Karo (`ProjektTemp/_wegwerf/randy/vergleich/hose_streifen.png`, Zuschnitte der Profilansichten; Breiten
nach Augenmaß aus dem Bild gegen den Beindurchmesser: rot ≈ 1,0 cm, Spalt 0,4, schwarz 0,5, Karo 2 × 1,4 cm). Die Fotoprojektion lieferte ihn nur stückweise (am Hüftansatz, an den Waden
nur Rot); `Hosenkoerper.textur` malt ihn deshalb aus diesem Muster ins Hosenbild.

    farbe, deckung = Hosenstreifen.muster(u, y, oben, unten)     # u: Bogenlänge um das Bein (m, 0 = Außennaht, positiv nach vorn), y: Höhe (m); beide (H, B)
                                                                 # → farbe (H, B, 3) in 0…255, deckung (H, B) in 0…1"""

import numpy as np

__all__ = ['Hosenstreifen']


class Hosenstreifen:
    ROT, SPALT, SCHWARZ = 0.010, 0.004, 0.005
    KARO = 0.014                 # Kante eines Karos (m); zwei Spalten
    SPALTEN = 2
    VORN = 0.5 * (ROT + SPALT + SCHWARZ + SPALTEN * KARO)     # u des vorderen Streifenrandes (Streifen mittig auf der Naht)
    OBEN_ABSTAND = 0.045         # unterhalb des oberen Hosenrandes (Bund) beginnt der Streifen
    KANTE = 0.0012               # Weichheit der Streifenkanten (m)
    FARBEN = {'rot': (196, 28, 36), 'schwarz': (22, 22, 26), 'karo_hell': (242, 238, 230)}

    @staticmethod
    def _kante(x, breite):
        """0…1 mit weicher Kante: x ≥ 0 innen."""
        return np.clip(x / breite + 0.5, 0.0, 1.0)

    @classmethod
    def muster(cls, u, y, oben, unten):
        k = cls.KANTE
        rot = (cls.VORN, cls.VORN - cls.ROT)
        schwarz = (rot[1] - cls.SPALT, rot[1] - cls.SPALT - cls.SCHWARZ)
        karo_vorn = schwarz[1]
        karo_hinten = karo_vorn - cls.SPALTEN * cls.KARO

        def band(von, bis):
            return np.minimum(cls._kante(von - u, k), cls._kante(u - bis, k))

        in_hoehe = np.minimum(cls._kante(oben - cls.OBEN_ABSTAND - y, k), cls._kante(y - unten, k))
        a_rot, a_schwarz, a_karo = band(*rot), band(*schwarz), band(karo_vorn, karo_hinten)
        spalte = np.floor((karo_vorn - u) / cls.KARO)
        zeile = np.floor(y / cls.KARO)
        schwarz_karo = ((spalte + zeile) % 2) == 0
        farbe = np.zeros(u.shape + (3,))
        farbe[:] = cls.FARBEN['karo_hell']
        farbe[schwarz_karo & (a_karo > 0.5)] = cls.FARBEN['schwarz']
        farbe[a_schwarz > 0.5] = cls.FARBEN['schwarz']
        farbe[a_rot > 0.5] = cls.FARBEN['rot']
        deckung = np.maximum.reduce([a_rot, a_schwarz, a_karo]) * in_hoehe
        return farbe, np.nan_to_num(deckung)
