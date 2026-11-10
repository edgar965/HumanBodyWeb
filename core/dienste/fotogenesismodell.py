# -*- coding: utf-8 -*-
"""Fotogenesismodell — „Als Modell speichern“ der Exportleiste von Foto-Genesis: die Figur aus den Fotos (`<Job>/figur/`) als Genesis-Modell (31.10.2026; bis dahin war der Knopf gesperrt,
„noch nicht gebaut“, Edgar: „mach alles was offen ist“).

Derselbe Weg wie „Übernehmen und als Modell speichern“ von Mesh-Genesis (`Meshgenesistestmodell`, eigener Prozess, Stand in `kleider_<g>/modell_stand.json`), nur die Quelle ist der Ordner des Jobs
(`Fotogenesisfigur`): Regler aus `form_<g>/modell.json`, die Stücke aus den Fotos in der wirksamen Wahl der Seite (`Fotogenesisfigur.kleider`, Vorgabe „ki“) als eigene Genesis-Stücke
(`Meshgenesistesteigenstueck`; Stücke nur mit Punktfarben bekommen dort eine Abwicklung und ein gebackenes Bild), die Haut als Fotohaut aus den Kacheln `haut_<g>/10??.jpg`, die beim
Speichern neben das Modell kopiert werden (`Modelltexturen.sichern`, `Texturquelle`). Das Modell steht danach unter „Charakter hinzufügen → Genesis 9 → Gespeicherte Modelle“.

    Fotogenesismodell.starten(job, geschlecht, name)   # (Antwort, HTTP-Status) wie `Meshgenesistestmodell.starten`
    Fotogenesismodell.stand(job, geschlecht)
"""

import json

from .fotogenesisfigur import Fotogenesisfigur
from .meshgenesistestmodell import Meshgenesistestmodell

__all__ = ['Fotogenesismodell']


class Fotogenesismodell(Meshgenesistestmodell):
    BEFEHL = 'fotogenesis_modell'
    HERKUNFT = 'foto-genesis'
    STUECKE = 'ki.json'

    @classmethod
    def geschlecht(cls, kennung):
        p = Fotogenesisfigur.ordner(kennung)
        return Fotogenesisfigur.geschlecht(p) if p is not None else None

    @classmethod
    def ordner(cls, kennung, geschlecht):
        p = Fotogenesisfigur.ordner(kennung)
        return p / ('kleider_%s' % geschlecht) if p is not None and geschlecht in Fotogenesisfigur.GESCHLECHTER else None

    @classmethod
    def form(cls, kennung, geschlecht):
        return json.loads((Fotogenesisfigur.ordner(kennung) / ('form_%s' % geschlecht) / 'modell.json').read_text(encoding='utf-8'))

    @classmethod
    def liste(cls, kennung, geschlecht):
        return Fotogenesisfigur.kleider(kennung, geschlecht)

    @classmethod
    def kacheln(cls, kennung, geschlecht):
        p = Fotogenesisfigur.ordner(kennung)
        return (Fotogenesisfigur._kacheln(kennung, p, geschlecht) or None) if p is not None else None
