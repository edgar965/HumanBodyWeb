# -*- coding: utf-8 -*-
"""Ueberlagerungskamera — Weltpositionen in Videopixel, wie im Browser.

Aus `bvh_projektion._parse_bvh_to_2d` herausgelöst (17.08.2026).

DIESE RECHNUNG MUSS ZU `fitOverlayCamera` PASSEN
================================================
Das Skelettvideo wird über das echte Video gelegt. Der Browser rechnet dieselbe
Projektion in `static/viewer/bvh_studio/playback.js`; weicht diese Fassung ab,
liegt das gezeichnete Skelett neben der Person — und zwar gleichmäßig verschoben,
was nach einem Kalibrierfehler der Pipeline aussieht und keiner ist.

Drei Punkte, an denen genau das passieren würde:

  * **Nur das ERSTE Bild bestimmt den Bildausschnitt.** Der Browser ruft
    `fitOverlayCamera` einmal; wer je Bild neu einpasst, bekommt eine Kamera, die
    der Bewegung folgt (das Skelett bleibt in der Mitte, das Video nicht).
  * **Der Zuschlag von 1,5** um die Skelettgröße ist derselbe wie dort.
  * **Y ist gespiegelt**: BVH zählt nach oben, Bildpunkte zählen nach unten.
"""


class Ueberlagerungskamera:
    """Orthografische Projektion auf Videopixel — Ausschnitt aus Bild 1."""

    #: Zuschlag um die Skelettgröße, damit nichts am Rand klebt. Muss mit
    #: `playback.js` übereinstimmen.
    ZUSCHLAG = 1.5

    def __init__(self, positionen, video_w, video_h):
        self.video_w = video_w
        self.video_h = video_h
        erste = positionen[0]
        x = [p[0] for p in erste.values()]
        y = [p[1] for p in erste.values()]
        self.mitte_x = (min(x) + max(x)) / 2
        self.mitte_y = (min(y) + max(y)) / 2
        halb_x = ((max(x) - min(x) or 1) * self.ZUSCHLAG) / 2
        halb_y = ((max(y) - min(y) or 1) * self.ZUSCHLAG) / 2
        self.halb_x, self.halb_y = self._seitenverhaeltnis(halb_x, halb_y)

    def _seitenverhaeltnis(self, halb_x, halb_y):
        """Den Ausschnitt auf das Videoformat aufziehen — nie beschneiden."""
        video = self.video_w / self.video_h
        skelett = halb_x / max(halb_y, 0.001)
        if video > skelett:
            return halb_y * video, halb_y
        return halb_x, halb_x / video

    def punkt(self, position):
        """(x, y) in Pixeln; Y gespiegelt."""
        x = ((position[0] - self.mitte_x + self.halb_x)
             / (2 * self.halb_x) * self.video_w)
        y = ((self.mitte_y + self.halb_y - position[1])
             / (2 * self.halb_y) * self.video_h)
        return x, y

    def bilder(self, positionen):
        """[{Gelenk: (x, y, 1.0)}, …] — das Format der Zeichenschicht.

        Die 1.0 ist die „Zuversicht" des Punktes: Die 2D-Erkenner liefern dort
        ihre Trefferwahrscheinlichkeit, und die Zeichenschicht blendet unsichere
        Punkte aus. Aus einer BVH gerechnete Punkte sind immer sicher.
        """
        aus = []
        for bild in positionen:
            punkte = {}
            for gelenk, position in bild.items():
                x, y = self.punkt(position)
                punkte[gelenk] = (x, y, 1.0)
            aus.append(punkte)
        return aus
