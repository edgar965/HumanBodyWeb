# -*- coding: utf-8 -*-
"""Teilevorrat — Kleidung und Haar eines `Kleidermodellbau` je Prozess aufbewahren, solange ihr Bauplan gleich bleibt
(02.10.2026, Edgar: „eine Runde muss 2–3 s dauern").

Gemessen an Auftrag 2026.10.01.20.10.04, bestes Modell (Fotostücke + Uhr + Mavick mit Bart): `Kleidermodellbau.teile`
kalt 41,7 s (Kleidung 28,9, Haar 10,9), warm 13,5 s (9,1 + 4,4) — die Zeit steckt in der Bindung der Stücke an die Figur
(`Oberflaechenbindung`, `folgernetz`) und der Kollision der Lagen (`kleidmischung`, `kollision`). Beides hängt nur am
Rumpf der Anfrage (Stellung, Werte der Stücke, getragene Stücke), NICHT an den Farben: Eine Runde, die nur umfärbt,
baute trotzdem alles neu.

`antwort(art, rumpf, rechnen, roh)`: gleicher Rumpf wie beim letzten Bau dieser Art → die alte Antwort samt der rohen
Netze (`roh`, für die Farbe), sonst `rechnen()` und merken. Je Art EIN Eintrag (das Haar allein hat 660.000 Flächen).
`farben(netz)`: das Mittel der Textur eines Netzes (`G9kleidfarbe.farben`), je Netz einmal.
"""

import json

__all__ = ['Teilevorrat']


class Teilevorrat:
    _antworten = {}
    _farben = {}

    @staticmethod
    def schluessel(rumpf):
        return json.dumps(rumpf, sort_keys=True, default=str)

    @classmethod
    def antwort(cls, art, rumpf, rechnen, roh):
        schluessel = cls.schluessel(rumpf)
        alt = cls._antworten.get(art)
        if alt is not None and alt[0] == schluessel:
            roh.update(alt[2])
            return alt[1]
        aus = rechnen()
        cls._antworten[art] = (schluessel, aus, dict(roh))
        cls._farben = {k: v for k, v in cls._farben.items() if any(
            k == id(n) for e in cls._antworten.values() for netze in e[2].values() for n in netze)}
        return aus

    @classmethod
    def farben(cls, netz):
        from Genesis9.kleidfarbe import G9kleidfarbe
        if id(netz) not in cls._farben:
            cls._farben[id(netz)] = G9kleidfarbe.farben(netz)
        return cls._farben[id(netz)]

    @classmethod
    def leeren(cls):
        cls._antworten.clear()
        cls._farben.clear()
