# -*- coding: utf-8 -*-
"""Kostuemoptimierer — Weg A des Kostüm-Kreislaufs: Werte verändern, rendern, benoten, das Bessere behalten.

Eine (1+λ)-Evolutionsstrategie: Je Runde entstehen λ Kandidaten aus dem BESTEN bisherigen Wertesatz; jeder
ändert 1–4 zufällig gewählte Maße/Farben/Haltungswerte um eine Normalverteilung mit Breite `schritt × Spanne`.
Ist einer besser als der Beste, wird er es und `schritt` wächst (× 1,25), sonst schrumpft er (× 0,9) — die
1/5-Erfolgsregel in einfacher Form: große Sprünge, solange sie etwas bringen, dann feiner. Der Zufall hängt an
Auftrag und Rundennummer: dieselbe Runde auf demselben Stand schlägt dieselben Kandidaten vor.

TEILE SCHALTET ER NICHT. Im ersten echten Lauf (29.09.2026) hat er den Hut abgeschaltet und damit 14 %
gewonnen — die Normierung auf die Figurhöhe bestraft eine zu hohe Hutspitze, und „weg" war der größere Sprung
als „niedriger". Welche Teile es gibt, entscheidet die Prüf-KI (sie sieht das Bild); der Optimierer passt an,
was da ist. Werte ausgeschalteter Teile fasst er nicht an — Rechenzeit für etwas, das man nicht sieht.
"""

import hashlib

import numpy as np

from .kostuemparameter import Kostuemparameter

__all__ = ['Kostuemoptimierer']


class Kostuemoptimierer:
    SCHRITT_START = 0.08
    SCHRITT_MIN, SCHRITT_MAX = 0.01, 0.3
    WACHSEN, SCHRUMPFEN = 1.25, 0.9
    AENDERUNGEN = (1, 4)
    #: Welche Teile eine Farbe trägt (die übrigen Stoffe sind immer zu sehen).
    FARBE_TEILE = {'stab': ('stab',), 'bart': ('bart', 'haar')}

    def __init__(self, kennung, schritt=None):
        self.kennung = kennung
        self.schritt = float(schritt or self.SCHRITT_START)

    def _zufall(self, runde):
        saat = int(hashlib.sha256(('%s:%d' % (self.kennung, runde)).encode()).hexdigest()[:12], 16)
        return np.random.default_rng(saat)

    @classmethod
    def veraenderlich(cls, werte):
        """Die stetigen Werte, die zu einem sichtbaren Teil gehören."""
        schema = Kostuemparameter.schema()

        def an(teil):
            schalter = '%s.an' % teil
            return schalter not in schema or werte.get(schalter, 1) >= 0.5

        aus = []
        for k, e in schema.items():
            if e['art'] != 'mass':
                continue
            teile = cls.FARBE_TEILE.get(k.split('.')[1], ()) if k.startswith('farbe.') else (k.split('.')[0],)
            if not teile or any(an(t) for t in teile):
                aus.append(k)
        return aus

    def kandidaten(self, bester, anzahl, runde):
        schema = Kostuemparameter.schema()
        stetig = self.veraenderlich(bester)
        zufall = self._zufall(runde)
        aus = []
        for _ in range(anzahl):
            neu = dict(bester)
            n = int(zufall.integers(self.AENDERUNGEN[0], self.AENDERUNGEN[1] + 1))
            for k in zufall.choice(stetig, size=min(n, len(stetig)), replace=False):
                e = schema[k]
                neu[k] = float(neu[k]) + float(zufall.normal(0.0, self.schritt * (e['max'] - e['min'])))
            aus.append(Kostuemparameter.pruefen(neu))
        return aus

    def anpassen(self, verbessert):
        faktor = self.WACHSEN if verbessert else self.SCHRUMPFEN
        self.schritt = min(self.SCHRITT_MAX, max(self.SCHRITT_MIN, self.schritt * faktor))
        return self.schritt
