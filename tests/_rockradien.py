# -*- coding: utf-8 -*-
"""Rockradien — prüft, ob ein Bein durch den Rock ragt.

Herausgelöst aus `cloth_engine_tests.test_recent_bake_no_thigh_through_skirt_radial`
(62 Zeilen mit vier Schleifen darin).

DIE IDEE
========
Ein Rock ist um die Beine herum. Auf jeder Höhe (Y-Scheibe) muss der Stoff WEITER
außen liegen als das Bein:

    max(Abstand Körperpunkt -> Mitte)  <=  min(Abstand Stoffpunkt -> Mitte)

Die Mitte ist der XZ-Schwerpunkt des Stoffs auf dieser Höhe, nicht die Weltmitte:
Wer sich zur Seite lehnt, hätte sonst überall eine Verletzung.

DIE ZWEI TOLERANZEN
===================
* **5 mm Abstand** (`TOLERANZ`): Weniger ist Zeichengenauigkeit, nicht
  Durchdringung.
* **10 % der Scheiben** (`GRENZE`): Einzelne Punkte ragen bei jeder Simulation
  heraus (eine Falte, ein Saum). Erst wenn es viele sind, ist der Rock kaputt.

Hüfte und Saum bleiben außen vor (die oberen und unteren 10 % der Höhe): Dort
liegt der Stoff am Körper an, das ist gewollt.
"""

import numpy as np


class Rockradien:
    """Vergleicht Körper- und Stoffradien je Höhenscheibe."""

    #: Dicke einer Scheibe (± um die Höhe).
    SCHEIBE = 0.04
    #: So viele Höhen werden je Segment geprüft.
    HOEHEN = 5
    #: Rand, der außen vor bleibt (Hüfte oben, Saum unten).
    RAND = 0.1
    #: Ab hier gilt es als Durchdringung.
    TOLERANZ = 0.005
    #: Anteil verletzter Scheiben, ab dem der Rock als kaputt gilt.
    GRENZE = 0.1
    #: Unter so vielen Punkten lohnt der Vergleich nicht.
    MINDESTPUNKTE = 3
    #: Flacher Stoff ist ein Fetzen — dafür gibt es einen eigenen Test.
    MINDESTHOEHE = 0.05

    def __init__(self):
        self.geprueft = 0
        self.verletzt = 0
        self.schlimmste = ('', 0.0, 0.0)

    # ------------------------------------------------------------------ Prüfen

    def bake_pruefen(self, daten, bilder=None):
        """Alle Segmente über die Beispielbilder prüfen."""
        koerperbilder = daten['rigid_positions']
        anzahl_segmente = int(daten['n_seg'][0])
        for bild in (bilder if bilder is not None
                     else self.beispielbilder(koerperbilder.shape[0])):
            for segment in range(anzahl_segmente):
                self.segment_pruefen(koerperbilder[bild],
                                     daten['seg%d_positions' % segment][bild],
                                     '%s seg%d' % (bild, segment))
        return self

    @staticmethod
    def beispielbilder(anzahl):
        """Anfang, Mitte, Ende — mehr braucht die Aussage nicht."""
        if anzahl >= 3:
            return [0, anzahl // 2, anzahl - 1]
        return list(range(anzahl))

    def segment_pruefen(self, koerper, stoff, marke):
        if stoff.shape[0] < 10:
            return
        mitte = (float(stoff[:, 0].mean()), float(stoff[:, 2].mean()))
        unten, oben = float(stoff[:, 1].min()), float(stoff[:, 1].max())
        if oben - unten < self.MINDESTHOEHE:
            return
        rand = self.RAND * (oben - unten)
        for hoehe in np.linspace(unten + rand, oben - rand, self.HOEHEN):
            self._hoehe_pruefen(koerper, stoff, mitte, hoehe,
                                '%s y=%.2f' % (marke, hoehe))

    def _hoehe_pruefen(self, koerper, stoff, mitte, hoehe, marke):
        koerper_radius = self._aussen(koerper, mitte, hoehe)
        stoff_radius = self._innen(stoff, mitte, hoehe)
        if koerper_radius is None or stoff_radius is None:
            return
        self.geprueft += 1
        if koerper_radius <= stoff_radius + self.TOLERANZ:
            return
        self.verletzt += 1
        vorher = self.schlimmste[1] - self.schlimmste[2]
        if koerper_radius - stoff_radius > vorher:
            self.schlimmste = (marke, koerper_radius, stoff_radius)

    # ------------------------------------------------------------- Radien

    def _scheibe(self, punkte, hoehe):
        maske = np.abs(punkte[:, 1] - hoehe) < self.SCHEIBE
        gewaehlt = punkte[maske]
        return gewaehlt if gewaehlt.shape[0] >= self.MINDESTPUNKTE else None

    def _radien(self, punkte, mitte):
        return np.sqrt((punkte[:, 0] - mitte[0]) ** 2
                       + (punkte[:, 2] - mitte[1]) ** 2)

    def _aussen(self, punkte, mitte, hoehe):
        """Der äußerste Körperpunkt dieser Höhe."""
        scheibe = self._scheibe(punkte, hoehe)
        return None if scheibe is None else float(self._radien(scheibe, mitte).max())

    def _innen(self, punkte, mitte, hoehe):
        """Der innerste Stoffpunkt dieser Höhe."""
        scheibe = self._scheibe(punkte, hoehe)
        return None if scheibe is None else float(self._radien(scheibe, mitte).min())

    # ------------------------------------------------------------- Ergebnis

    @property
    def anteil(self):
        return 0.0 if not self.geprueft else self.verletzt / self.geprueft

    @property
    def bestanden(self):
        return self.anteil < self.GRENZE

    def bericht(self):
        return ('violations=%d/%d (%.0f%%) worst=%s body_r=%.2f cloth_r=%.2f'
                % (self.verletzt, self.geprueft, self.anteil * 100,
                   self.schlimmste[0], self.schlimmste[1], self.schlimmste[2]))
