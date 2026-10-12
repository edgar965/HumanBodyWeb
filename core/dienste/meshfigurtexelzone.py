# -*- coding: utf-8 -*-
"""Meshfigurtexelzone — der Übergang von der echten Netzhaut in die nie getroffene Haut unter dem Stoff (12.10.2026).

Anlass (Edgar, Auftrag „Edgar", Unterhose): unter dem Saum der Shorts stand ein glattes Band am Oberschenkel, scharf gegen die behaarte Fotohaut abgesetzt. Dort trifft das Netz nur Stoff; die
Texelprüfung (`Meshfigurtexelpruefung`) füllte die Zone mit dem glatten Feld der guten Nachbartexel — und der Rand des Feldes war genau die Hautzeile am Saum, in der das Netz (Tripo) den Schatten
des Stoffs eingebacken hat: die Füllung kam dunkler und grauer heraus als die Haut zwei Zentimeter tiefer (gemessen an der Beinkachel: Füllung Y 35,2 gegen 39,4 der getroffenen Texel 10–120 px dahinter).

Hier zwei Dinge für jede GROSSE nie getroffene Zone (schmale Löcher und Spalten bleiben, wie sie waren):

1. Der Ton der Zone kommt aus Texeln jenseits des Übergangs (mindestens `FEDER_PX` von der Zone entfernt), mit einem breiten Feld (`FELD_PX`) — ohne den eingebackenen Saumschatten.
2. Die echte Haut geht über `FEDER_PX` Pixel (Hermite-Kurve) in dieses Feld über: die behaarte Haut endet nicht an einer Kante, sondern blendet aus. Die Texel auf der Zone selbst bekommen das Feld ganz.
"""

import numpy as np

__all__ = ['Meshfigurtexelzone']


class Meshfigurtexelzone:
    #: Breite des Übergangs in Pixeln der 2048er-Kachel (etwa 4 cm) und kleinste Breite einer Zone, ab der sie zählt.
    FEDER_PX = 40.0
    ZONE_MIN_PX = 24
    #: Breite des Feldes aus den Texeln jenseits des Übergangs.
    FELD_PX = 96.0

    def __init__(self, seite, glatt):
        """`glatt(bild, maske, sigma) → (Farbe, Stütze)`: die normierte Faltung der Texelprüfung."""
        self.seite = int(seite)
        self.glatt = glatt

    @staticmethod
    def _hell(rgb):
        """Helligkeit (Y der Rohwerte 0..255) je Zeile oder Pixel."""
        return rgb @ np.array([0.299, 0.587, 0.114])

    def anwenden(self, drin, versteckt, gut, farbe, ziel, fuellung):
        """Ändert `farbe` (gute Texel nahe der Zone) und `fuellung` (Texel der Zone) an Ort und Stelle; gibt die Zahl der abgeblendeten Texel zurück.
        `versteckt` (n,): nie getroffene, gefüllte Texel; `gut` (n,): echte Netzhaut; `ziel` (n,): alles, was gefüllt wird."""
        from scipy import ndimage

        zone = np.zeros((self.seite, self.seite), dtype=bool)
        zone[drin] = versteckt
        zone = ndimage.binary_opening(zone, iterations=self.ZONE_MIN_PX // 2)
        if not zone.any():
            return 0
        abstand = ndimage.distance_transform_edt(~zone)[drin]
        bild = np.zeros((self.seite, self.seite, 3))
        maske = np.zeros((self.seite, self.seite), dtype=bool)
        bild[drin] = farbe
        quelle = gut & (abstand >= self.FEDER_PX)
        maske[drin] = quelle
        feld, stuetze = self.glatt(bild, maske, self.FELD_PX)
        # Behaarte Haut besteht aus rosa Grund und dunklen Härchen; der Mittelwert beider liegt grauer und dunkler als alles, was man darauf sieht. Das Feld nimmt den Grund: nur Texel, die nicht dunkler sind als das
        # erste Feld an ihrer Stelle (Haar und Schatten fallen heraus).
        hell = quelle & (self._hell(bild[drin]) >= self._hell(feld[drin]))
        maske[drin] = hell
        feld2, stuetze2 = self.glatt(bild, maske, self.FELD_PX)
        ersatz = stuetze2 <= 1e-3
        feld, stuetze = np.where(ersatz[..., None], feld, feld2), np.where(ersatz, stuetze, stuetze2)
        feld, ok = feld[drin], stuetze[drin] > 1e-3
        auf_zone = zone[drin] & ziel & ok
        fuellung[auf_zone] = feld[auf_zone]
        t = np.clip(abstand / self.FEDER_PX, 0.0, 1.0)
        w = np.where(gut & ok, 1.0 - t * t * (3.0 - 2.0 * t), 0.0)[:, None]
        farbe[:] = farbe * (1.0 - w) + feld * w
        return int((w > 0.0).sum())
