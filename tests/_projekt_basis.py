# -*- coding: utf-8 -*-
"""Beiwerk der Projekt-Roundtrip-Tests: Speichern, Laden, vier Vorlagen.

Fuehrender Unterstrich mit Absicht: `testaufbau` erkennt daran, dass das keine
Testdatei ist. Aus `project_tests.py` herausgeloest (17.08.2026, 425 Zeilen).

Die vier Vorlagen fahren je EINEN Speichern-Laden-Umlauf und merken sich das
Ergebnis. Alle Tests der beiden Kategorien lesen daraus — deshalb stehen sie
hier und nicht in einer der beiden.

UMBAU 27.08.2026 (Befunde `freie-funktionen`, `klassenreif` Frage 1,
`globaler-zustand`, `klassen-kandidat`): vier freie Funktionen mit vier
`global`-Anweisungen. Die Umlaeufe sind teuer — je zwei HTTP-Aufrufe — und
werden von ueber zwanzig Pruefungen gebraucht; ihr Ergebnis haengt jetzt als
KLASSENFELD an `Projektvorlagen` und laesst sich mit `.leeren()` zuruecksetzen.
"""

from ._speicherprobe import Speicherprobe


class Projektvorlagen:
    """Vier Studio-Projekte, je einmal gespeichert und zurueckgelesen.

    Jede Vorlage prueft eine andere Ecke des Speicherformats:

        licht         Eigenschaften einer eigenen Lichtspur samt Keyframe
        szenenlichter Ueberschreibungen der Standardlichter (Key, Ambient)
        geloeschter_kf ein Keyframe, den das Laden NICHT wiederbringen darf
        boden         Farbe, Textur, Rauheit und Groesse des Bodens
    """

    #: {Name: Ergebnis} — einmal gerechnet, bis zum Prozessende.
    _umlaeufe = {}

    @classmethod
    def leeren(cls):
        """Alle Umlaeufe verwerfen — fuer eine Pruefung, die neu messen will."""
        cls._umlaeufe = {}

    @classmethod
    def _umlauf(cls, name, projekt):
        if name not in cls._umlaeufe:
            cls._umlaeufe[name] = Speicherprobe.fahren(projekt).als_dict()
        return cls._umlaeufe[name]

    # ------------------------------------------------------------------ Licht

    @classmethod
    def licht(cls):
        """Eine eigene Lichtspur mit allen Eigenschaften und einem Keyframe."""
        return cls._umlauf('licht', {
            'name': 'T', 'fps': 30, 'tracks': [{
                'name': 'TestSpot', 'type': 'light', 'color': '#ffc107',
                'muted': False, 'position': [0, 0, 0],
                'lightColor': '#ff00ff', 'lightIntensity': 7.5,
                'lightPosition': {'x': 1.5, 'y': 3.5, 'z': 2.5},
                'lightTarget': {'x': 0, 'y': 1, 'z': 0},
                'lightAngle': 0.7854, 'lightPenumbra': 0.42,
                'lightDistance': 30.0, 'lightVisible': True,
                'lightType': 'spot',
                'clips': [{
                    'type': 'light_kf', 'name': 'KF1', 'startFrame': 60,
                    'data': {'intensity': 12.0, 'fade': False,
                             'angle': 0.5236, 'visible': True},
                }],
            }],
        })

    @classmethod
    def szenenlichter(cls):
        """Ueberschriebene Standardlichter — eines stummgeschaltet."""
        return cls._umlauf('szenenlichter', {
            'name': 'T', 'fps': 30, 'tracks': [],
            'sceneLights': {
                'Key Light': {
                    'color': '#ff5733', 'intensity': 8.5,
                    'position': {'x': 1, 'y': 2, 'z': 3},
                    'visible': True, 'muted': True,
                    'clips': [
                        {'type': 'light_kf', 'name': 'Licht 1',
                         'startFrame': 30,
                         'data': {'intensity': 5.0, 'fade': False}},
                    ],
                },
                'Ambient': {
                    'color': '#aabbcc', 'intensity': 0.5,
                    'position': {'x': 0, 'y': 0, 'z': 0},
                    'visible': False, 'muted': False, 'clips': [],
                },
            },
        })

    @classmethod
    def geloeschter_kf(cls):
        """Ein Standard-Keyframe am Ende — er darf nicht wiederkommen."""
        return cls._umlauf('geloeschter_kf', {
            'name': 'T', 'fps': 30, 'tracks': [],
            'sceneLights': {
                'Key Light': {
                    'color': '#fff', 'intensity': 3.0,
                    'position': {'x': 2, 'y': 4, 'z': -5},
                    'visible': True, 'muted': False,
                    'clips': [
                        {'type': 'light_kf', 'name': 'Standard Ende',
                         'startFrame': 300,
                         'data': {'visible': True, 'fade': True}},
                    ],
                },
            },
        })

    @classmethod
    def boden(cls):
        """Bodenfarbe, Textur, Rauheit, Metallanteil und Groesse."""
        return cls._umlauf('boden', {
            'name': 'T', 'fps': 30, 'tracks': [],
            'sceneFloor': {
                'color': '#8b4513', 'texture': 'none',
                'roughness': 0.7, 'metalness': 0.15, 'size': 10.0,
                'muted': False,
            },
        })
