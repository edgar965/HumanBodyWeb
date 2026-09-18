# -*- coding: utf-8 -*-
"""Attrappen fuer die Pruefungen der Wertklassen.

Fuehrender Unterstrich mit Absicht: `testaufbau` erkennt daran, dass
hier keine Testdatei liegt. Herausgeloest aus
`test_ungepruefte_klassen.py` (Befund `klassen-je-datei`, 27.08.2026).
"""


class Vorlagenattrappe:
    """Was `Kleidungsregler.aus_parametern` von einer Kleidervorlage liest."""

    def __init__(self, offset=0.01, stiffness=0.4, color=(0.1, 0.2, 0.3)):
        self.offset = offset
        self.stiffness = stiffness
        self.color = color


class Sammelstrom:
    """Attrappe fuer stdout — merkt sich, was geschrieben wurde."""

    def __init__(self):
        self.stuecke = []

    def write(self, text):
        self.stuecke.append(text)
        return len(text)

    def flush(self):
        pass

    @property
    def text(self):
        return ''.join(self.stuecke)
