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

DER KOERPER KOMMT AUCH VON INNEN (Edgar, 11.09.2026, mit Bild: „bei einer
animation kommt der Koerper durch die Kleidung hindurch"). Die erste
Fassung kuerzte nur den EINWAERTS gerichteten Anteil des Stoffzuschlags;
bekam der Koerper selbst einen groesseren Zuschlag als der Stoff darueber,
stand die Haut durch — bei 13 mm Hautabstand (T-Shirt) nie sichtbar, bei
einer Leggings auf 2 mm sofort. Gemessen in der Szene (Dance1, Sprung aus
der T-Pose): Koerperzuschlag 188 mm, Stoff 109 mm, 6,3 % der Leggings-
punkte im Koerper. Deshalb gilt jetzt ein SOLLABSTAND je Punkt: sein
Ruheabstand, hoechstens `MINDESTABSTAND` — und wer darunter liegt, wird
auf ihn gehoben, gleich ob der Stoff nach innen oder der Koerper nach
aussen gegangen ist.
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

        Ueber das SIGNIERTE VOLUMEN, nicht die Mehrheit gegen den
        Schwerpunkt: Die Grenze wird je Bild aus dem POSIERTEN Koerper
        gebaut, und die Mehrheit kippte in Dance1 bei 32 % (11.09.2026,
        feines 70K-Netz) — der Stoff wurde in den Koerper GEZOGEN, im Bild
        lag die Leggings innen. Das Volumen haengt an der Wicklung, und die
        aendert keine Pose. `normalen` bleibt in der Signatur, damit die
        Browser-Fassung (`stoffgrenze.js`) denselben Aufruf traegt.
        """
        a = self.punkte[self.dreiecke[:, 0]]
        b = self.punkte[self.dreiecke[:, 1]]
        c = self.punkte[self.dreiecke[:, 2]]
        vol = float(np.einsum('ij,ij->i', a, np.cross(b, c)).sum())
        return 1.0 if vol >= 0 else -1.0

    def abstand(self, stoffpunkte):
        u"""Der vorzeichenbehaftete Abstand je Stoffpunkt (positiv = aussen)."""
        _abstand, naechster = self.baum.query(stoffpunkte)
        rest = stoffpunkte - self.punkte[naechster]
        return np.sum(rest * self.normalen[naechster], axis=1)

    def sollabstand(self, stoffruhe):
        u"""Je Stoffpunkt: sein Ruheabstand, hoechstens `MINDESTABSTAND`.

        Auf dieser Grenze (aus der RUHELAGE gerechnet) haelt `kuerzen`
        jeden Punkt — eine Leggings auf 2 mm bleibt auf 2 mm, ein T-Shirt
        auf 13 mm wird nicht naeher als 6 mm gelassen.
        """
        return np.minimum(self.abstand(stoffruhe), self.MINDESTABSTAND)

    def kuerzen(self, stoffpunkte, versatz, soll=None):
        u"""Der erlaubte Teil des Zuschlags, je Punkt.

        `soll` ist der Sollabstand je Punkt (`sollabstand`); ohne ihn gilt
        `MINDESTABSTAND` fuer alle. Rueckgabe ist der gekuerzte Versatz und
        die Zahl der Punkte, bei denen gekuerzt wurde.
        """
        _abstand, naechster = self.baum.query(stoffpunkte)
        normale = self.normalen[naechster]
        rest = stoffpunkte - self.punkte[naechster]
        # Der vorzeichenbehaftete Abstand: positiv = ausserhalb.
        aussen = np.sum(rest * normale, axis=1)
        nach_innen = -np.sum(versatz * normale, axis=1)
        # Wo der Punkt MIT Versatz laege, gegen das, was ihm zusteht.
        ist = aussen - nach_innen
        ziel = self.MINDESTABSTAND if soll is None else np.asarray(soll)
        zuviel = ist < ziel
        if not zuviel.any():
            return versatz, 0
        gekuerzt = np.array(versatz)
        # Nur ENTLANG DER NORMALE anheben, den Rest lassen: Ein Stueck, das
        # seitlich mitschwingt, soll das weiter tun.
        ueberschuss = (ziel - ist)[zuviel]
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
