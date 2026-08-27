# -*- coding: utf-8 -*-
"""Das Ergebnis des Kamera-Speichern-Laden-Umlaufs — benannt statt als Dict.

ANLASS (Befund `rueckgabedict`, 27.08.2026): `Kamerabasis._auswerten` gab ein
Woerterbuch mit sieben Schluesseln zurueck, und je nach Abbruchstelle waren es
zwei, drei oder sieben. Zehn Pruefungen lasen daraus mit `.get()` — wer den
Schluessel vertippt, bekommt `None`, und `None is True` ist schlicht `False`:
ein Test, der aus dem falschen Grund rot wird, oder schlimmer, einer der aus
dem falschen Grund gruen bleibt.

DAZU: `Kamerabasis.umlauf_ergebnis` hatte den Speichern-Laden-Umlauf NOCH
EINMAL ausgeschrieben, obwohl `Speicherprobe` daneben genau das tut. Jetzt
faehrt diese Klasse die Probe und wertet nur noch aus.
"""

from ._speicherprobe import Speicherprobe


class Kameraumlauf:
    """Was nach Speichern und Laden von der Kamera-Spur uebrig ist."""

    def __init__(self, probe):
        #: Die Speicherprobe darunter — sie haelt Statuscodes und Flaggen.
        self.probe = probe
        self.spuren = 0
        self.klips = 0
        self.kamera_aktiv = None
        self.kf1 = {}
        self.kf2 = {}
        if probe.geladen:
            self._auswerten(probe.projekt)

    @classmethod
    def fahren(cls, projektdaten):
        return cls(Speicherprobe.fahren(projektdaten))

    def _auswerten(self, projekt):
        spuren = [s for s in projekt.get('tracks', [])
                  if s.get('type') == 'camera']
        klips = spuren[0].get('clips', []) if spuren else []
        self.spuren = len(spuren)
        self.klips = len(klips)
        self.kamera_aktiv = spuren[0].get('cameraActive') if spuren else None
        self.kf1 = klips[0] if len(klips) > 0 else {}
        self.kf2 = klips[1] if len(klips) > 1 else {}

    # ------------------------------------------------------- Durchgereicht

    @property
    def gespeichert(self):
        return self.probe.gespeichert

    @property
    def geladen(self):
        return self.probe.geladen

    @property
    def speichercode(self):
        return self.probe.speichercode

    @property
    def ladecode(self):
        return self.probe.ladecode

    # ------------------------------------------------------ Keyframe-Felder

    @staticmethod
    def feld(keyframe, name, vorgabe=None):
        """Ein Feld aus `keyframe['data']` — ohne zwei `.get()` je Abfrage."""
        return (keyframe or {}).get('data', {}).get(name, vorgabe)
