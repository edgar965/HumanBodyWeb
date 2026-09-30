# -*- coding: utf-8 -*-
"""Iterationsoptimierer — Weg A der Iterationen: Werte verändern, rendern, benoten, das Bessere behalten.

Eine (1+λ)-Evolutionsstrategie: Je Runde entstehen λ Kandidaten aus dem BESTEN bisherigen Wertesatz; jeder
ändert 1–4 zufällig gewählte Maße um eine Normalverteilung mit Breite `schritt × Spanne`. Ist einer besser
als der Beste, wird er es und `schritt` wächst (× 1,25), sonst schrumpft er (× 0,9) — die 1/5-Erfolgsregel
in einfacher Form: große Sprünge, solange sie etwas bringen, dann feiner. Der Zufall hängt an Auftrag und
Rundennummer: dieselbe Runde auf demselben Stand schlägt dieselben Kandidaten vor.

TEILE SCHALTET ER NICHT (Erfahrung aus BlenderModel: er schaltete einen Teil ab, weil die Normierung auf die
Figurhöhe ihn bestrafte — „weg" war der größere Sprung als „kleiner"). Welche Teile es gibt, entscheidet die
Prüf-KI (sie sieht das Bild); der Optimierer passt an, was da ist. Werte ausgeschalteter Teile fasst er
nicht an. Farben würfelt er nicht (`FARBEN_FEST`): Eine Farbe auf wenigen Bildpunkten hat kaum Gegendruck
durch die Note und wanderte in BlenderModel bis an ihre Grenzen.
"""

import hashlib

import numpy as np

from .haarparameter import Haarparameter

__all__ = ['Iterationsoptimierer']


class Iterationsoptimierer:
    SCHRITT_START = 0.08
    SCHRITT_MIN, SCHRITT_MAX = 0.01, 0.3
    WACHSEN, SCHRUMPFEN = 1.25, 0.9
    AENDERUNGEN = (1, 4)
    #: Faktor der weiten Sprünge (jeder zweite Kandidat), gegenüber `schritt`.
    GROB = 6.0
    #: Farben würfelt der Optimierer NICHT (siehe Kopf der Datei).
    FARBEN_FEST = True
    #: Welche Teile eine Farbe trägt: Stoff → Teile (`<teil>.an`); ein Stoff ohne Eintrag ist immer zu
    #: sehen. Leer, bis die Engine ihre Teile kennt.
    FARBE_TEILE = {}

    def __init__(self, kennung, schritt=None):
        self.kennung = kennung
        self.schritt = float(schritt or self.SCHRITT_START)

    def _zufall(self, runde):
        saat = int(hashlib.sha256(('%s:%d' % (self.kennung, runde)).encode()).hexdigest()[:12], 16)
        return np.random.default_rng(saat)

    @classmethod
    def veraenderlich(cls, werte):
        """Die stetigen Werte, die zu einem sichtbaren Teil gehören."""
        schema = Haarparameter.schema()

        def an(teil):
            schalter = '%s.an' % teil
            return schalter not in schema or werte.get(schalter, 1) >= 0.5

        aus = []
        for k, e in schema.items():
            if e['art'] != 'mass':
                continue
            if k.startswith('farbe.') and cls.FARBEN_FEST:
                continue
            teile = cls.FARBE_TEILE.get(k.split('.')[1], ()) if k.startswith('farbe.') else (k.split('.')[0],)
            if not teile or any(an(t) for t in teile):
                aus.append(k)
        return aus

    def kandidaten(self, bester, anzahl, runde):
        schema = Haarparameter.schema()
        stetig = self.veraenderlich(bester)
        zufall = self._zufall(runde)
        aus = []
        for i in range(anzahl):
            # Jeder zweite Kandidat springt weiter (`GROB`): Die Schrittweite schrumpft in einer langen Flaute bis zum
            # Mindestwert (30.09.2026: 0,01 der Spanne, Abweichung 0,2560 → 0,2559 in 20 Runden), und neue Maße —
            # `hut.seite`, `stab.krone` — brauchten dann Dutzende Erfolge hintereinander, um einen sinnvollen Wert
            # zu erreichen.
            breite = min(self.SCHRITT_MAX, self.schritt * (self.GROB if i % 2 else 1.0))
            neu = dict(bester)
            n = int(zufall.integers(self.AENDERUNGEN[0], self.AENDERUNGEN[1] + 1))
            for k in zufall.choice(stetig, size=min(n, len(stetig)), replace=False):
                e = schema[k]
                neu[k] = float(neu[k]) + float(zufall.normal(0.0, breite * (e['max'] - e['min'])))
            aus.append(Haarparameter.pruefen(neu))
        return aus

    def anpassen(self, verbessert):
        faktor = self.WACHSEN if verbessert else self.SCHRUMPFEN
        self.schritt = min(self.SCHRITT_MAX, max(self.SCHRITT_MIN, self.schritt * faktor))
        return self.schritt
