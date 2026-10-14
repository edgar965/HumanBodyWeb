# -*- coding: utf-8 -*-
"""Mesh3dnetzauswahl — Orte aus der Mesh-Ansicht in Flächen des Netzes übersetzen (13.10.2026, „Netz bearbeiten“).

Eine Auswahl ist eine Liste von Schritten; jeder fügt Flächen hinzu (`plus`, Vorgabe) oder nimmt sie weg (`minus`):

    {"art": "insel",  "punkt": [x, y, z]}                     der zusammenhängende Teil, dessen Fläche dem Punkt am nächsten liegt (Klick auf das Netz)
    {"art": "rahmen", "ebenen": [[nx, ny, nz, d], …]}         alle Flächen, deren Mitte hinter allen Ebenen liegt (n·x + d ≥ 0) — das Prisma eines gezogenen Rechtecks, ohne Tiefe
    {"art": "kasten", "min": [x, y, z], "max": [x, y, z]}     achsenparalleler Kasten
    {"art": "farbe",  "punkt": [x, y, z], "radius": r, "toleranz": t}
                                                                 alle Flächen im Umkreis `radius` um den Punkt, deren Farbe (Lab, Textur an der Flächenmitte) höchstens ΔE `toleranz` von der Fläche unter dem Punkt abweicht — ohne
                                                                 Zusammenhang über Kanten: der Flügel am Arm der Ballerina (13.10.2026) hängt nur lose an Arm und Riemen, ein Rahmen träfe den Arm mit, ein Zauberstab über Kanten riss ab
    {"art": "umkehren"}                                          alles, was NICHT ausgewählt ist

Die Koordinaten sind die der Szene der Datei (`Mesh3dnetzkatalog`). Was der Browser für die Vorschau markiert, ist seine Rechnung auf der gezeigten (vielleicht vereinfachten) Kopie; maßgeblich ist DIESE auf dem
Original. Ungültige Schritte (fremde Art, keine Zahlen, zu viele Ebenen) sind ein `ValueError` mit dem Grund — nie ein stilles Auslassen.
"""

import math

import numpy as np

__all__ = ['Mesh3dnetzauswahl']


class Mesh3dnetzauswahl:
    #: Höchstzahl der Schritte einer Auswahl und der Ebenen eines Rahmens (Schutz gegen Unsinn aus dem Netz).
    SCHRITTE_MAX = 400
    EBENEN = (3, 8)
    #: Grenzen der Auswahl nach Farbe: Umkreis um den Klick (Einheiten der Szene, die Mesh-Ansicht rechnet cm in diese um) und Farbabstand ΔE (CIE76).
    RADIUS_MAX = 5.0
    TOLERANZ_MAX = 80.0
    #: Höchstabstand zwischen dem Klickpunkt und dem DREIECK der vom Browser genannten Fläche (Einheiten der Szene; der Raycast trifft auf 0,00002), ohne Datei zur MITTE (`START_M`).
    AUF_FLAECHE_M = 0.004
    START_M = 0.03

    def __init__(self, katalog):
        self.katalog = katalog

    def maske(self, schritte):
        """(F,) bool: die Flächen, die die Schritte der Reihe nach ergeben."""
        if not isinstance(schritte, (list, tuple)):
            raise ValueError('Die Auswahl muss eine Liste von Schritten sein')
        if len(schritte) > self.SCHRITTE_MAX:
            raise ValueError('Zu viele Schritte (%d, höchstens %d)' % (len(schritte), self.SCHRITTE_MAX))
        maske = np.zeros(self.katalog.flaechen, dtype=bool)
        for schritt in schritte:
            if not isinstance(schritt, dict):
                raise ValueError('Ein Schritt der Auswahl ist kein Objekt')
            art = schritt.get('art')
            if art == 'umkehren':
                maske = ~maske
                continue
            teil = self._flaechen(art, schritt)
            aktion = schritt.get('aktion', 'plus')
            if aktion not in ('plus', 'minus'):
                raise ValueError('Unbekannte Aktion „%s“' % aktion)
            if aktion == 'plus':
                maske |= teil
            else:
                maske &= ~teil
        return maske

    # ------------------------------------------------------------------ Schritte

    def _flaechen(self, art, schritt):
        if art == 'insel':
            punkt = self._zahlen(schritt.get('punkt'), 3, 'punkt')
            return self.katalog.insel == self.katalog.insel[self.katalog.naechste_flaeche(punkt)]
        if art == 'rahmen':
            ebenen = schritt.get('ebenen')
            if not isinstance(ebenen, (list, tuple)) or not self.EBENEN[0] <= len(ebenen) <= self.EBENEN[1]:
                raise ValueError('Ein Rahmen braucht %d bis %d Ebenen' % self.EBENEN)
            drin = np.ones(self.katalog.flaechen, dtype=bool)
            for ebene in ebenen:
                e = self._zahlen(ebene, 4, 'ebene')
                drin &= self.katalog.mitte @ np.asarray(e[:3], dtype=np.float32) + np.float32(e[3]) >= 0
            return drin
        if art == 'kasten':
            unten, oben = self._zahlen(schritt.get('min'), 3, 'min'), self._zahlen(schritt.get('max'), 3, 'max')
            return ((self.katalog.mitte >= np.asarray(unten, dtype=np.float32)) & (self.katalog.mitte <= np.asarray(oben, dtype=np.float32))).all(axis=1)
        if art == 'farbe':
            punkt = self._zahlen(schritt.get('punkt'), 3, 'punkt')
            radius, toleranz = self._zahlen([schritt.get('radius'), schritt.get('toleranz')], 2, 'radius und toleranz')
            if not 0 < radius <= self.RADIUS_MAX or not 0 < toleranz <= self.TOLERANZ_MAX:
                raise ValueError('Farbe: Radius muss in (0, %g] und Toleranz in (0, %g] liegen' % (self.RADIUS_MAX, self.TOLERANZ_MAX))
            lab = self.katalog.farben_lab()
            start = self._startflaeche(punkt, schritt.get('flaeche'))
            nah = np.linalg.norm(self.katalog.mitte - np.asarray(punkt, dtype=np.float32), axis=1) <= radius
            return nah & (np.linalg.norm(lab - lab[start], axis=1) <= toleranz)
        raise ValueError('Unbekannte Art der Auswahl: %s' % (art,))

    def _startflaeche(self, punkt, nummer):
        """Die Fläche unter dem Klick. Liegen zwei Flächen übereinander (ein Flügel auf dem Arm, 5 mm darüber), trifft „die Mitte am nächsten“ oft die falsche: schickt der Browser die Nummer der getroffenen Fläche mit und liegt der Punkt auf diesem
        DREIECK (höchstens `AUF_FLAECHE_M` davon entfernt — bei einer vereinfachten Kopie sind die Nummern andere), gilt sie; sonst die Fläche, auf der der Punkt liegt (`naechste_flaeche_genau`).
        Der Abstand zur MITTE taugt dafür nicht (14.10.2026, Ballerina: Dreiecke mit 0,4 m Kanten, Mitte 3,8 cm vom Klick; der Server nahm eine Armfläche darunter, die Hautfarbe war die Referenz, der Unterarm wurde entfernt).
        Ein Katalog ohne Datei (Prüfkatalog) kennt keine Dreiecke und bleibt beim Abstand zur Mitte (`START_M`)."""
        if isinstance(nummer, (int, float)) and not isinstance(nummer, bool) and 0 <= nummer < self.katalog.flaechen:
            abstand = self.katalog.abstand_zu_flaechen(punkt, [int(nummer)])
            if abstand is not None:
                if float(abstand[0]) <= self.AUF_FLAECHE_M:
                    return int(nummer)
            elif float(np.linalg.norm(self.katalog.mitte[int(nummer)] - np.asarray(punkt, dtype=np.float32))) <= self.START_M:
                return int(nummer)
        return self.katalog.naechste_flaeche_genau(punkt)

    @staticmethod
    def _zahlen(werte, anzahl, name):
        if not isinstance(werte, (list, tuple)) or len(werte) != anzahl:
            raise ValueError('„%s“ braucht %d Zahlen' % (name, anzahl))
        try:
            zahlen = [float(w) for w in werte]
        except (TypeError, ValueError) as fehler:
            raise ValueError('„%s“ enthält keine Zahlen' % name) from fehler
        if not all(math.isfinite(z) for z in zahlen):
            raise ValueError('„%s“ enthält keine endlichen Zahlen' % name)
        return zahlen
