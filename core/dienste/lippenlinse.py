# -*- coding: utf-8 -*-
"""Lippenlinse — die MB-Lab-Lippenmaske auf die Form der Lippen beschneiden.

WARUM (Edgar, 13.09.2026, Bild der Szene: „die Lippen sind fehlerhaft"):
`human_female_lipmap.png` ist eine weiche, runde Fläche — gemalt für den
MB-Lab-Shader, der damit nur den Glanz über die Albedo legt. Für eine
eigene Materialgruppe mit kräftiger Farbe ist sie zu großzügig: An den
Mundwinkeln reicht sie als Keil bis 35 mm nach außen, die Lippen enden bei
±20,6 mm (gemessen am Basiskörper, `ProjektTemp/lippen_kruemmung.py`); die
Zickzack-Ränder kamen aus den Hautdreiecken, die in diesen Keilen liegen.
In der Mitte stimmt sie: Oberlippe bis 8 mm über die Mundlinie (Wulst bei
1,509 m), Unterlippe 11 mm darunter — beides deckt sich mit der Wölbung des
Netzes.

Die Linse nimmt von der Maske die Höhe in der Mitte und vom Netz die
Mundwinkel: Wo die Mundlinie (der tiefste Punkt der Mittellinie) endet, ist
der Mundwinkel. Dazwischen laufen Ober- und Unterlippe mit
`(1 − t²)^POTENZ` auf null zu. Gemessen bei x = ±11,5 mm: Oberlippe 7 mm,
Unterlippe 8,7 mm über bzw. unter der Mundlinie — die Parabel (1,0) ist dort
zu schmal, die Ellipse (0,5) an den Winkeln zu dick; 0,6 lässt dazu die eine
Reihe zu, die der Browser am Rand verliert (ein Dreieck ist erst Lippe, wenn
alle drei Ecken es sind, `gemeinsam/lippengruppe.js`).

Punkte, die nicht vorn liegen (Mundhöhle, Innenseiten der Lippen), bleiben
markiert: Sie sind hinter der Haut verborgen, und an der Mundlinie
schließen sie die Lippen nach innen ab. „Vorn" heißt: nicht mehr als
`TIEFE` hinter dem vordersten Punkt seiner Nachbarschaft in der Ansicht von
vorn — die Normalen taugen dafür nicht, am Mund zeigen sie nach innen.
Aber nur bis `HOEHLE` dahinter: Der NACKEN liegt in derselben Ansicht im
Umriss der Linse, 100 mm hinter den Lippen, und trug die Lippenfarbe als
rosa Fleck (Edgar, 13.09.2026, Bild vom Nacken). Gemessen am Basiskörper:
verborgene Hautpunkte der Mundhöhle liegen höchstens 5 mm hinter der
Lippenfront, die 28 Nackenpunkte über 100 mm; dazwischen nur Zunge und Zähne.

`abstand` liefert je Punkt den VORZEICHENABSTAND zum Linsenrand in
Millimetern (innen positiv). Der Browser legt ihn als Attribut ans Netz und
mischt die Lippenfarbe je Bildpunkt (`gemeinsam/lippenhaut.js`): Ein
Dreieck ist dann nicht ganz Lippe oder ganz Haut, der Rand läuft glatt
durch die Dreiecke — vorher stand er als Zickzack auf den Kanten.

Alles in Blender-Koordinaten des Netzes (x rechts, y nach hinten, z hoch).
"""
import logging

import numpy as np

logger = logging.getLogger(__name__)


class Lippenlinse:
    """Maskenpunkte → Lippenpunkte, beschnitten auf eine Linse um die Mundlinie."""

    #: Verlauf der Lippenhöhe zu den Mundwinkeln: (1 − t²)^POTENZ.
    POTENZ = 0.6
    #: Zelle der Ansicht von vorn und wie weit hinter dem vordersten Punkt der
    #: 3×3-Nachbarschaft noch „vorn" gilt (m) — 2 mm verkraften die schrägen Mundwinkel.
    ZELLE = 0.001
    TIEFE = 0.002
    #: Bis hierhin (m) hinter der Front gilt ein verborgener Punkt im Umriss noch als Mundhöhle.
    HOEHLE = 0.025
    #: Breite der Mittellinie und Höhe des Bandes um die Mundlinie (m).
    MITTE = 0.0015
    BAND = 0.002
    #: Abstand vom oberen/unteren Rand, in dem die Mundlinie NICHT gesucht wird (m).
    RAND = 0.003
    #: Abstand (mm) für Punkte ohne Rechnung: weit außen bzw. verborgen innen.
    AUSSEN = -10.0
    INNEN = 10.0

    @classmethod
    def beschneiden(cls, maske, punkte):
        """`maske` (bool, N) und `punkte` (N, 3) → bool (N) der Lippenpunkte."""
        return cls.abstand(maske, punkte) > 0

    @classmethod
    def abstand(cls, maske, punkte):
        """Je Punkt der Abstand zum Linsenrand in mm — innen positiv (N, float).

        Vorne entscheidet die Linse (auch für Punkte außerhalb der Maske: sie
        liefert nur die Höhe in der Mitte); verborgene Punkte im Umriss der
        Linse sind INNEN, alles andere AUSSEN. Lässt sich die Linse nicht bestimmen (zu
        wenige Punkte), gilt die rohe Maske — lieber die alte Form als keine
        Lippen.
        """
        maske = np.asarray(maske, dtype=bool)
        p = np.asarray(punkte, dtype=float)
        roh = np.where(maske, cls.INNEN, cls.AUSSEN)
        if p.ndim != 2 or p.shape[0] != maske.shape[0] or maske.sum() < 50:
            return roh
        x, hoch, vorn = p[:, 0], p[:, 2], -p[:, 1]
        tiefe = cls.tiefe(x, hoch, vorn)
        front = tiefe <= cls.TIEFE
        kand = maske & front
        linse = cls.linse(x[kand], hoch[kand], vorn[kand])
        if linse is None:
            logger.warning('Lippenlinse: Mundlinie nicht gefunden, Maske bleibt roh')
            return roh
        # Verborgene Punkte im Umriss der Linse gelten als innen — auch ohne
        # Maske: An den Mundwinkeln lugte sonst die Innenseite der Lippe als
        # hautfarbener Zipfel hervor. Jenseits des Umrisses bleiben sie Haut:
        # Die kleinen Lappen der Mundhöhle neben den Winkeln fallen hautfarben
        # weniger auf als rot. Und nur bis HOEHLE dahinter — sonst der Nacken.
        aus = np.full(len(x), cls.AUSSEN)
        hinten = ~front
        hoehle = (cls.rand(x[hinten], hoch[hinten], linse) > 0) & (tiefe[hinten] <= cls.HOEHLE)
        aus[hinten] = np.where(hoehle, cls.INNEN, cls.AUSSEN)
        aus[front] = cls.rand(x[front], hoch[front], linse)
        logger.info('Lippenlinse: Mundwinkel ±%.1f mm, Mundlinie %.4f m, Lippen %d Punkte vorn (Maske %d)',
                    1000 * linse['xc'], linse['ym'], int((aus[front] > 0).sum()), int(kand.sum()))
        return aus

    @classmethod
    def vorderseite(cls, x, hoch, vorn):
        """Vorn ist, wer nicht weiter als TIEFE hinter dem vordersten Punkt seiner Nachbarschaft liegt."""
        return cls.tiefe(x, hoch, vorn) <= cls.TIEFE

    @classmethod
    def tiefe(cls, x, hoch, vorn):
        """Je Punkt, wie weit (m) er hinter dem vordersten Punkt seiner Nachbarschaft liegt.

        Nachbarschaft = die eigene 1-mm-Zelle (x, hoch) und ihre acht Nachbarn.
        Die eigene Zelle allein reicht nicht: Die Haut hat nur alle ~1 mm einen
        Punkt, und eine Zelle ohne Hautpunkt hielte den Mundhöhlenpunkt darin
        für vorn (so fand die erste Fassung die Mundlinie 4 mm zu tief).
        """
        zx = np.floor(x / cls.ZELLE).astype(np.int64)
        zy = np.floor(hoch / cls.ZELLE).astype(np.int64)
        zx -= zx.min() - 1
        zy -= zy.min() - 1
        raster = np.full((zx.max() + 2, zy.max() + 2), -np.inf)
        np.maximum.at(raster, (zx, zy), vorn)
        umgebung = raster.copy()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                umgebung[1:-1, 1:-1] = np.maximum(
                    umgebung[1:-1, 1:-1], raster[1 + dx:raster.shape[0] - 1 + dx, 1 + dy:raster.shape[1] - 1 + dy])
        return umgebung[zx, zy] - vorn

    @classmethod
    def linse(cls, x, hoch, vorn):
        """Mitte, Mundwinkel und Höhen aus den vorderen Maskenpunkten — oder None."""
        mitte = np.abs(x - np.median(x)) < cls.MITTE
        if mitte.sum() < 5:
            return None
        oben, unten = hoch[mitte].max(), hoch[mitte].min()
        # Mundlinie: der tiefste Punkt der Mittellinie, abseits der Ränder
        innen = mitte & (hoch < oben - cls.RAND) & (hoch > unten + cls.RAND)
        if not innen.any():
            return None
        ym = hoch[innen][np.argmin(vorn[innen])]
        band = np.abs(hoch - ym) < cls.BAND
        if band.sum() < 5:
            return None
        links, rechts = x[band].min(), x[band].max()
        x0, xc = (links + rechts) / 2, (rechts - links) / 2
        if xc < 0.005:
            return None
        ecken = band & ((x < links + cls.BAND) | (x > rechts - cls.BAND))
        return {'x0': x0, 'xc': xc, 'ym': ym, 'yecke': float(hoch[ecken].mean()),
                'u0': oben - ym, 'd0': ym - unten}

    @classmethod
    def drin(cls, x, hoch, linse):
        """Welche Punkte innerhalb der Linse liegen."""
        return cls.rand(x, hoch, linse) > 0

    @classmethod
    def rand(cls, x, hoch, linse):
        """Vorzeichenabstand zum Linsenrand in mm, innen positiv.

        Innerhalb der Mundwinkel der senkrechte Abstand zur näheren Randkurve
        (an den steilen Enden etwas zu groß, für den 1-mm-Saum egal), jenseits
        der Mundwinkel der waagerechte zum Winkel — nach außen begrenzt auf AUSSEN.
        """
        t = (x - linse['x0']) / linse['xc']
        ym = linse['ym'] + (linse['yecke'] - linse['ym']) * t * t
        faktor = np.clip(1 - t * t, 0, 1) ** cls.POTENZ
        oben = ym + linse['u0'] * faktor - hoch
        unten = hoch - (ym - linse['d0'] * faktor)
        senkrecht = np.minimum(oben, unten)
        seitlich = -(np.abs(t) - 1) * linse['xc']
        abstand = 1000 * np.where(np.abs(t) <= 1, senkrecht, np.minimum(senkrecht, seitlich))
        return np.clip(abstand, cls.AUSSEN, cls.INNEN)
