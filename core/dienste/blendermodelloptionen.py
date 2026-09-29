# -*- coding: utf-8 -*-
"""Blendermodelloptionen — was der Bereich „BlenderModel" einstellen lässt, mit Vorgaben.

Drei Gruppen, je mit ihrem eigenen Katalog geprüft (gleichnamige Felder meinen in den Katalogen
Verschiedenes):

    figur    Grundfigur und „Als Modell speichern" (`Meshfiguroptionen` — nur diese zwei Felder, siehe unten)
    kostuem  Kostüm-Kreislauf: Runden, Kandidaten, Stillstand, Prüf-KI (`Kostuemoptionen`)
    blender  BVH, Bilder, Größe, Renderer (`Blendermodellblenderoptionen`)

Bis 29.09.2026 (abends) gab es eine vierte Gruppe `netz` (Formmodell TRELLIS.2/Hunyuan3D, Auflösung, …) und
die ganze Figur-Gruppe von „Mesh to 3D" (Körper-Runden, Gesichtskette, Frisur, …). Beides gehörte zur Kette
„Netz aus Fotos → Figur", die ausgebaut ist (Edgar: „trellis soll nicht laufen", `blendermodelllauf.py`). Alte
Aufträge tragen die Gruppe `netz` noch in der Datenbank; `pruefen` lässt sie fallen.

`figur.modell` hat hier die Vorgabe „aus" (in „Mesh to 3D" „an"): Jeder Lauf würde sonst ein Genesis-Modell in
die Modellbibliothek schreiben (`HumanBody/data/models`). Gespeichert wird über den Knopf „Modell speichern".
"""

from .blendermodellblenderoptionen import Blendermodellblenderoptionen
from .kostuemoptionen import Kostuemoptionen
from .meshfiguroptionen import Meshfiguroptionen
from .meshoptionen import Meshoptionen

__all__ = ['Blendermodelloptionen']


class Blendermodelloptionen:
    GRUPPEN = ('figur', 'kostuem', 'blender')
    #: Felder, die im Formular erscheinen (None = alle des Katalogs).
    SICHTBAR = {'figur': ('basis', 'modell'), 'kostuem': None, 'blender': None}
    #: Vorgaben, die hier von der Vorlage abweichen.
    ABWEICHUNGEN = {'figur': {'modell': 'aus'}, 'kostuem': {}, 'blender': {}}
    PRUEFER = (
        ('figur', Meshfiguroptionen),
        ('kostuem', Kostuemoptionen),
        ('blender', Blendermodellblenderoptionen),
    )

    @classmethod
    def katalog(cls):
        """`{figur: {optionen}, kostuem: {optionen}, blender: {optionen}, rollen}` für das Formular."""
        gruppen = {
            'figur': Meshfiguroptionen.katalog()['optionen'],
            'kostuem': Kostuemoptionen.katalog()['optionen'],
            'blender': Blendermodellblenderoptionen.katalog()['optionen'],
        }
        aus = {}
        for gruppe in cls.GRUPPEN:
            felder = []
            for feld in gruppen[gruppe]:
                sichtbar = cls.SICHTBAR[gruppe]
                if sichtbar is not None and feld['schluessel'] not in sichtbar:
                    continue
                felder.append(
                    dict(feld, vorgabe=cls.ABWEICHUNGEN[gruppe].get(feld['schluessel'], feld['vorgabe']))
                )
            aus[gruppe] = {'optionen': felder}
        # Die Rollen der Bildauswahl (vorne/links/rechts/hinten geben dem Kostüm-Kreislauf den Blickwinkel).
        aus['rollen'] = Meshoptionen.katalog()['rollen']
        return aus

    @classmethod
    def pruefen(cls, roh):
        """Jede Gruppe gegen ihren Katalog — bekannte Schlüssel, gültige Werte, sonst Vorgabe."""
        roh = roh if isinstance(roh, dict) else {}
        aus = {}
        for gruppe, pruefer in cls.PRUEFER:
            gruppenwerte = roh.get(gruppe)
            werte = {**cls.ABWEICHUNGEN[gruppe], **(gruppenwerte if isinstance(gruppenwerte, dict) else {})}
            aus[gruppe] = pruefer.pruefen(werte)
        return aus

    @classmethod
    def mischen(cls, alt, neu):
        """`neu` über `alt` legen, Gruppe für Gruppe (eine Seite schickt nur, was sie kennt) — geprüft."""
        alt, neu = (alt if isinstance(alt, dict) else {}), (neu if isinstance(neu, dict) else {})
        return cls.pruefen(
            {
                g: {
                    **(alt.get(g) if isinstance(alt.get(g), dict) else {}),
                    **(neu.get(g) if isinstance(neu.get(g), dict) else {}),
                }
                for g in cls.GRUPPEN
            }
        )

    @classmethod
    def figur(cls, optionen):
        """Die Optionen der Figur — dieselbe Form wie `Meshfiguroptionen.pruefen`."""
        return cls.pruefen(optionen)['figur']

    @classmethod
    def kostuem(cls, optionen):
        return cls.pruefen(optionen)['kostuem']

    @classmethod
    def blender(cls, optionen):
        """Die Optionen des Blender-Teils (BVH, Bilder, Größe, Renderer)."""
        return cls.pruefen(optionen)['blender']
