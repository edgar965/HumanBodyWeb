# -*- coding: utf-8 -*-
"""Ai2d3dmodell — „Als Modell speichern“ der Exportleiste von 2d-3d-AI: die Figur aus den Fotos (`<Job>/figur/`) als Genesis-Modell (31.10.2026; bis dahin war der Knopf gesperrt,
„noch nicht gebaut“, Edgar: „mach alles was offen ist“).

Derselbe Weg wie „Übernehmen und als Modell speichern“ von Mesh3D-AI (`Mesh3daitestmodell`, eigener Prozess, Stand in `kleider_<g>/modell_stand.json`), nur die Quelle ist der Ordner des Jobs
(`Ai2d3dfigur`): Regler aus `form_<g>/modell.json`, die Stücke aus den Fotos in der wirksamen Wahl der Seite (`Ai2d3dfigur.kleider`, Vorgabe „ki“) als eigene Genesis-Stücke
(`Mesh3daitesteigenstueck`; Stücke nur mit Punktfarben bekommen dort eine Abwicklung und ein gebackenes Bild), die Haut als Fotohaut aus den Kacheln `haut_<g>/10??.jpg`, die beim
Speichern neben das Modell kopiert werden (`Modelltexturen.sichern`, `Texturquelle`). Das Modell steht danach unter „Charakter hinzufügen → Genesis 9 → Gespeicherte Modelle“.

    Ai2d3dmodell.starten(job, geschlecht, name)   # (Antwort, HTTP-Status) wie `Mesh3daitestmodell.starten`
    Ai2d3dmodell.stand(job, geschlecht)
"""

import json

from .ai2d3dfigur import Ai2d3dfigur
from .mesh3daitestmodell import Mesh3daitestmodell

__all__ = ['Ai2d3dmodell']


class Ai2d3dmodell(Mesh3daitestmodell):
    BEFEHL = 'ai2d3d_modell'
    HERKUNFT = '2d-3d-ai'
    STUECKE = 'ki.json'

    @classmethod
    def geschlecht(cls, kennung):
        p = Ai2d3dfigur.ordner(kennung)
        return Ai2d3dfigur.geschlecht(p) if p is not None else None

    @classmethod
    def ordner(cls, kennung, geschlecht):
        p = Ai2d3dfigur.ordner(kennung)
        return p / ('kleider_%s' % geschlecht) if p is not None and geschlecht in Ai2d3dfigur.GESCHLECHTER else None

    @classmethod
    def form(cls, kennung, geschlecht):
        return json.loads((Ai2d3dfigur.ordner(kennung) / ('form_%s' % geschlecht) / 'modell.json').read_text(encoding='utf-8'))

    @classmethod
    def liste(cls, kennung, geschlecht):
        return Ai2d3dfigur.kleider(kennung, geschlecht)

    @classmethod
    def kacheln(cls, kennung, geschlecht):
        p = Ai2d3dfigur.ordner(kennung)
        return (Ai2d3dfigur._kacheln(kennung, p, geschlecht) or None) if p is not None else None
