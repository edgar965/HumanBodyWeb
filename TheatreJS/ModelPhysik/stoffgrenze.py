# -*- coding: utf-8 -*-
u"""Haelt den Physik-Zuschlag aus dem Koerper heraus.

DER BEFUND, DER DAZU GEFUEHRT HAT (11.09.2026): Velocity Skinning ist fuer
KOERPER entworfen — dort ist jeder Punkt an Knochen gebunden, und ein
Zuschlag von 20 mm bleibt Gewebe. Ein Kleidungsstueck haengt dagegen lose,
und sein Abstand zur Haut ist gemessen 13 mm (T-Shirt) bzw. 27 mm (Hose).
Ein Zuschlag von 28 mm schiebt es glatt durch den Koerper: im Bild klaffen
Loecher, durch die die Haut sieht.

DIE GRENZE STEHT NICHT IM ORIGINAL, und das ist kein Versehen des
Upstream — er animiert keine Kleidung. Sie ist auch keine Simulation:
Der Zuschlag wird je Punkt so weit gekuerzt, dass ein Mindestabstand zur
Haut bleibt. Nach aussen bleibt er ungekuerzt; ein Stueck, das vom Koerper
wegschwingt, soll das duerfen.

Gemessen wird gegen den KOERPER DESSELBEN BILDES, nicht gegen die
Ruhelage — beim Gehen wandert die Haut unter dem Stoff.
"""
import numpy as np


class Stoffgrenze:
    u"""Kuerzt Verschiebungen, die in den Koerper hineinzeigen."""

    #: So nah darf der Stoff der Haut kommen. Der Kollisionsabstand der
    #: Drapierung liegt bei 6 mm (CLAUDE.md, 08.09.2026, nach dem Befund
    #: „Haut scheint durch die Hose"); darunter zu gehen hiesse, den dort
    #: teuer erarbeiteten Abstand wieder herzugeben.
    MINDESTABSTAND = 0.006

    def __init__(self, koerperpunkte, koerperdreiecke):
        from scipy.spatial import cKDTree
        self.punkte = np.asarray(koerperpunkte, dtype=np.float64)
        self.dreiecke = np.asarray(koerperdreiecke, dtype=np.int64)
        self.baum = cKDTree(self.punkte)
        self.normalen = self._normalen()

    def _normalen(self):
        u"""Punktnormalen des Koerpers, aus den Flaechennormalen gemittelt.

        DIE RICHTUNG MUSS AUS DEM KOERPER KOMMEN, nie aus dem Stoff. Die
        Flaechennormale eines Schnittteils haengt an seiner Wickelrichtung
        und kann zum Koerper zeigen — dieselbe Falle hat im Projekt schon
        viermal zugeschlagen (`stoffkorrektur.py`, 06.09.2026).
        """
        a = self.punkte[self.dreiecke[:, 0]]
        b = self.punkte[self.dreiecke[:, 1]]
        c = self.punkte[self.dreiecke[:, 2]]
        flaeche = np.cross(b - a, c - a)
        aus = np.zeros_like(self.punkte)
        for spalte in range(3):
            np.add.at(aus, self.dreiecke[:, spalte], flaeche)
        laengen = np.linalg.norm(aus, axis=1, keepdims=True)
        aus = aus / np.maximum(laengen, 1e-12)
        return aus * self._aussen(aus)

    def _aussen(self, normalen):
        u"""+1 oder -1 — zeigen die Normalen nach aussen?

        Nicht angenommen, sondern geprueft: die Mehrheit gegen den
        Schwerpunkt. Ein nach innen gewickeltes Netz kehrte sonst die
        ganze Grenze um, und der Stoff wuerde in den Koerper GEZOGEN.
        """
        mitte = self.punkte.mean(axis=0)
        nach_aussen = self.punkte - mitte
        zeichen = np.sum(np.sum(nach_aussen * normalen, axis=1) > 0)
        return 1.0 if zeichen * 2 >= len(self.punkte) else -1.0

    def kuerzen(self, stoffpunkte, versatz):
        u"""Der erlaubte Teil des Zuschlags, je Punkt.

        Rueckgabe ist der gekuerzte Versatz und die Zahl der Punkte, bei
        denen gekuerzt wurde.
        """
        _abstand, naechster = self.baum.query(stoffpunkte)
        normale = self.normalen[naechster]
        rest = stoffpunkte - self.punkte[naechster]
        # Der vorzeichenbehaftete Abstand: positiv = ausserhalb.
        aussen = np.sum(rest * normale, axis=1)
        # Wieviel darf der Punkt nach INNEN? Nur so weit, wie er ueber
        # dem Mindestabstand liegt.
        spielraum = np.maximum(aussen - self.MINDESTABSTAND, 0.0)
        nach_innen = -np.sum(versatz * normale, axis=1)
        zuviel = nach_innen > spielraum
        if not zuviel.any():
            return versatz, 0
        gekuerzt = np.array(versatz)
        # Nur den EINWAERTS gerichteten Anteil kuerzen, den Rest lassen:
        # Ein Stueck, das seitlich mitschwingt, soll das weiter tun.
        ueberschuss = (nach_innen - spielraum)[zuviel]
        gekuerzt[zuviel] += ueberschuss[:, None] * normale[zuviel]
        return gekuerzt, int(zuviel.sum())

    #: Tiefer als das muss ein Punkt stecken, um zu zaehlen. Ohne Toleranz
    #: meldete der Messer am T-Shirt 6,09 % „im Koerper" — bei einem
    #: tiefsten Punkt von 0,1 mm. Das sind Punkte, die AUF der Haut
    #: liegen und je nach Normale um Bruchteile eines Millimeters
    #: innen landen; sichtbar ist davon nichts.
    TOLERANZ = 0.001

    def durchdringung(self, stoffpunkte):
        u"""Anteil der Stoffpunkte IM Koerper, und die groesste Tiefe.

        Die Probe, die zaehlt. Sie fragt je STOFFpunkt, ob er im Koerper
        steckt — nicht je Koerperpunkt, ob Stoff dahinter liegt: Der
        Koerper ist geschlossen, „innen" ist dort wohldefiniert, und
        offene Saeume spielen keine Rolle (CLAUDE.md, 07.09.2026, nachdem
        der Messer viermal falsch herum stand).
        """
        _abstand, naechster = self.baum.query(stoffpunkte)
        rest = stoffpunkte - self.punkte[naechster]
        aussen = np.sum(rest * self.normalen[naechster], axis=1)
        drin = aussen < -self.TOLERANZ
        # `aussen` ist innen NEGATIV — der tiefste Punkt ist das MINIMUM.
        # Bis zum 11.09.2026 stand hier `.max()`, also der flachste Punkt,
        # als „groesste Tiefe" in jeder Bilanz. Gefunden hat es die
        # JavaScript-Gegenprobe (`test_js_stoffgrenze.py`): 19,0 mm gegen
        # 1,0 mm bei denselben Punkten.
        return (float(drin.mean()) * 100.0,
                float(-aussen[drin].min()) * 1000.0 if drin.any() else 0.0)
