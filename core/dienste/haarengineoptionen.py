# -*- coding: utf-8 -*-
"""Haarengineoptionen — was der Bereich „2D3D Kleider" (`haarengine`) einstellen lässt, mit Vorgaben (30.09.2026).

Fünf Gruppen, je mit ihrem eigenen Katalog geprüft (gleichnamige Felder meinen in den Katalogen
Verschiedenes):

    figur        Grundfigur und „Als Modell speichern" (`Meshfiguroptionen` — nur diese zwei Felder)
    netz         Netz aus den Fotos: Formmodell, Auflösung, Freistellen (`Meshoptionen`, Reiter „Mesh")
    koerper      woher die Figur kommt: übernehmen aus „Mesh to 3D" oder rechnen (`Haarenginekoerperoptionen`)
    iterationen  Iterationen: Begutachtung oder automatisch, Runden, Kandidaten, Prüf-KI (`Iterationsoptionen`)
    film         BVH, Bilder, Größe (`Haarenginefilmoptionen`)

`figur.modell` hat hier die Vorgabe „aus" (in „Mesh to 3D" „an"): Jeder Lauf würde sonst ein Genesis-Modell
in die Modellbibliothek schreiben (`HumanBody/data/models`). Gespeichert wird über den Knopf „Modell
speichern".
"""

from .haarenginefilmoptionen import Haarenginefilmoptionen
from .haarenginekoerperoptionen import Haarenginekoerperoptionen
from .iterationsoptionen import Iterationsoptionen
from .meshfiguroptionen import Meshfiguroptionen
from .meshoptionen import Meshoptionen

__all__ = ['Haarengineoptionen']


class Haarengineoptionen:
    GRUPPEN = ('figur', 'netz', 'koerper', 'iterationen', 'film')
    #: Felder, die im Formular erscheinen (None = alle des Katalogs).
    SICHTBAR = {
        'figur': ('basis', 'modell'),
        'netz': ('formmodell', 'aufloesung', 'freistellen', 'licht'),
        'koerper': None,
        'iterationen': None,
        'film': None,
    }
    #: Vorgaben, die hier von der Vorlage abweichen.
    ABWEICHUNGEN = {'figur': {'modell': 'aus'}, 'netz': {}, 'koerper': {}, 'iterationen': {}, 'film': {}}
    PRUEFER = (
        ('figur', Meshfiguroptionen),
        ('netz', Meshoptionen),
        ('koerper', Haarenginekoerperoptionen),
        ('iterationen', Iterationsoptionen),
        ('film', Haarenginefilmoptionen),
    )

    @classmethod
    def katalog(cls):
        """`{figur: {optionen}, netz: …, koerper: …, iterationen: …, film: …, rollen}` für das Formular."""
        aus = {}
        for gruppe, pruefer in cls.PRUEFER:
            felder = []
            for feld in pruefer.katalog()['optionen']:
                sichtbar = cls.SICHTBAR[gruppe]
                if sichtbar is not None and feld['schluessel'] not in sichtbar:
                    continue
                felder.append(
                    dict(feld, vorgabe=cls.ABWEICHUNGEN[gruppe].get(feld['schluessel'], feld['vorgabe']))
                )
            aus[gruppe] = {'optionen': felder}
        # Die Rollen der Bildauswahl (vorne/links/rechts/hinten geben den Blickwinkel der Iterationen).
        aus['rollen'] = [{'wert': w, 'text': t} for w, t in Meshoptionen.ROLLEN]
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
    def netz(cls, optionen):
        return cls.pruefen(optionen)['netz']

    @classmethod
    def koerper(cls, optionen):
        return cls.pruefen(optionen)['koerper']

    @classmethod
    def iterationen(cls, optionen):
        return cls.pruefen(optionen)['iterationen']

    @classmethod
    def film(cls, optionen):
        """Die Optionen des Films (BVH, Bilder, Größe)."""
        return cls.pruefen(optionen)['film']
