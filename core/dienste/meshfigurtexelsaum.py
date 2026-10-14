# -*- coding: utf-8 -*-
"""Meshfigurtexelsaum — der Schatten am Rand von Armband, Uhr und Manschette in der Armkachel (14.10.2026).

Anlass (Edgar4, Handkachel 1004): auf dem Handrücken unter dem Armband standen dunkelbraune, gezackte Splitter und ein dunkler Streifen um die Löcher am Handgelenk. Sie stehen schon in den Rohdaten (`arbeit/meshtextur.npz`): das Netz hat
den Schatten des Bandes in die Haut daneben eingebacken, und die Ausreißerprüfung (`Meshfigurtexelpruefung`, dunkler als 0,6 × das Feld der Umgebung) lässt sie durch, weil die Umgebung selbst dunkel ist. Zwei Versuche am selben Tag taugten nicht (höhere Schwelle: größere
Flecken; Texel neben einem Loch nicht mehr als gut zählen: dunkle Ringe an der Saumkante).

Hier: ein Texel, das höchstens `PX` Pixel von einer Fläche liegt, die das Netz getroffen hat und die keine Haut ist (blau, grau, schwarz: Band, Gehäuse), und dunkler ist als `FAKTOR` × das Feld der guten Texel, die weiter weg liegen, gilt nicht als gut — es bekommt wie jedes
ungültige Hauttexel das Feld der guten Nachbarn (samt Zeichnung, `Meshfigurtexeldetail`).

Nur in der Armkachel (UDIM 1004): an den behaarten Beinen (1003) änderte die Regel mit jeder Einstellung 5–10 % der Hauttexel in den Haaren, nicht am Saum (`ProjektTemp/_wegwerf/mesh3d/schatten_alle.py`). Einzelne dunkle Härchen am Unterarm bleiben auch hier: ein Schatten zählt nur
als zusammenhängender Fleck mit einem Kern von `FLECK_PX` Pixeln Halbbreite, die Fremdfläche ab `GROESSE_PX` (mit 6 blieb ein Teil des Streifens, weil das Armband in der UV aus schmalen Streifen besteht).
"""

import numpy as np

__all__ = ['Meshfigurtexelsaum']


class Meshfigurtexelsaum:
    #: Die Kachel, in der die Regel gilt (Arme und Hände).
    KACHEL = 1004
    #: Reichweite des Schattens in Pixeln der 2048er-Kachel und seine Dunkelheit gegen das Feld der Haut dahinter. `PX` 0 schaltet ab.
    PX = 30
    FAKTOR = 0.85
    GROESSE_PX = 1
    FLECK_PX = 3
    #: Breite des Feldes aus der Haut jenseits des Schattens und der Füllung (wie `Meshfigurtexelpruefung.GROB_PX` und `FEIN_PX`).
    FELD_PX = 48.0
    FEIN_PX = 12.0
    #: Die Füllung aus dem Grund der Haut (`grund`); False: wie in den anderen Kacheln.
    FUELL_GRUND = True

    def __init__(self, seite, glatt):
        """`glatt(bild, maske, sigma) → (Farbe, Stütze)`: die normierte Faltung der Texelprüfung."""
        self.seite = int(seite)
        self.glatt = glatt

    def schatten(self, drin, fremd, hell, farbe, gut):
        """(n,) bool: gute Texel im Schatten eines Fremdkörpers. `fremd` (n,): Treffer, die keine Haut sind; `hell` (n,): ihre Helligkeit (Y); `farbe` (n, 3): RGB; `gut` (n,): die echte Netzhaut."""
        if not self.PX or not fremd.any():
            return np.zeros_like(gut)
        from scipy import ndimage

        marke = self._bild(drin, fremd)
        marke = ndimage.binary_opening(marke, iterations=self.GROESSE_PX)
        if not marke.any():
            return np.zeros_like(gut)
        nah = ndimage.distance_transform_edt(~marke)[drin] <= self.PX
        bild = np.zeros((self.seite, self.seite, 3))
        bild[drin] = farbe
        feld, stuetze = self.glatt(bild, self._bild(drin, gut & ~nah), self.FELD_PX)
        dunkel = gut & nah & (stuetze[drin] > 1e-3) & (hell < self.FAKTOR * (feld[drin] @ np.array([0.299, 0.587, 0.114])))
        return self._flecken(drin, dunkel)

    def grund(self, drin, gut, farbe, fuellung, ziel=None):
        """Die Füllung der Armkachel aus dem GRUND der Haut statt aus ihrem Mittel: nur gute Texel, die nicht dunkler sind als das erste Feld an ihrer Stelle, bilden das Feld (wie `Meshfigurtexelzone` für nie getroffene Zonen). Der eingebackene Schatten des Netzes
        zwischen Daumen und Handfläche und am Band lag sonst als dunkle, scharfkantige Scherben in der Füllung (Edgar4, sternförmige Flecken am Handrücken: 317 Füllungstexel im Ausschnitt unter 0,8 × der Helligkeit der Umgebung, alle ungetroffen, alle aus dunklen Nachbarn gefüllt).
        `fuellung` (n, 3) wird an Ort und Stelle ersetzt, wo das neue Feld Stütze hat und `ziel` (n,) bool gilt (die zu füllenden Texel; None: alle); gibt die Zahl der geänderten Texel zurück. `FUELL_GRUND` False: unverändert."""
        if not self.FUELL_GRUND or not gut.any():
            return 0
        bild = np.zeros((self.seite, self.seite, 3))
        bild[drin] = farbe
        gewicht = np.array([0.299, 0.587, 0.114])
        erste = self._feld(bild, self._bild(drin, gut))
        hell = gut & ((farbe @ gewicht) >= (erste[drin] @ gewicht))
        if not hell.any():
            return 0
        zweite, stuetze = self._feld(bild, self._bild(drin, hell), mit_stuetze=True)
        wahl = stuetze[drin] > 1e-3
        if ziel is not None:
            wahl &= ziel
        fuellung[wahl] = zweite[drin][wahl]
        return int(wahl.sum())

    def _feld(self, bild, maske, mit_stuetze=False):
        """Fein (`FEIN_PX`), wo genug Stütze da ist, sonst grob (`FELD_PX`) — wie die Füllung der Texelprüfung."""
        fein, m_fein = self.glatt(bild, maske, self.FEIN_PX)
        grob, m_grob = self.glatt(bild, maske, self.FELD_PX)
        feld = np.where((m_fein > 0.15)[..., None], fein, grob)
        return (feld, m_grob) if mit_stuetze else feld

    def _bild(self, drin, werte):
        bild = np.zeros((self.seite, self.seite), dtype=bool)
        bild[drin] = werte
        return bild

    def _flecken(self, drin, dunkel):
        """Nur zusammenhängende Flecken: dunkle Härchen (1–3 Pixel breit) bleiben, ein Schatten mit dickem Kern geht ganz (Rekonstruktion vom Kern aus). `FLECK_PX` 0: alles."""
        if not self.FLECK_PX or not dunkel.any():
            return dunkel
        from scipy import ndimage

        bild = self._bild(drin, dunkel)
        kern = ndimage.binary_opening(bild, iterations=self.FLECK_PX)
        if not kern.any():
            return np.zeros_like(dunkel)
        return ndimage.binary_propagation(kern, mask=bild, structure=np.ones((3, 3), dtype=bool))[drin]
