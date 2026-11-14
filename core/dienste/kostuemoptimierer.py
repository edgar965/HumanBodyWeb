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

from KoerperKI_alle.zufallsstrom import Zufallsstrom

from .kostuemparameter import Kostuemparameter
from .iterationsoptimierer import Iterationsoptimierer

__all__ = ['Kostuemoptimierer']


class Kostuemoptimierer:
    PARAMETER = Kostuemparameter            # Parameterklasse der Familie (`Iterationsoptimierer.kandidaten`, `veraenderlich`)
    SCHRITT_START = 0.08
    SCHRITT_MIN, SCHRITT_MAX = 0.01, 0.3
    WACHSEN, SCHRUMPFEN = 1.25, 0.9
    AENDERUNGEN = (1, 4)
    #: Faktor der weiten Sprünge (jeder zweite Kandidat), gegenüber `schritt`.
    GROB = 6.0
    #: Farben würfelt der Optimierer NICHT (seit Modell Version 2): Eine Farbe, die auf wenig Bildpunkten liegt (Gürtel,
    #: Stab), hat kaum Gegendruck durch die Note und wanderte im Lauf vom 29./30.09.2026 bis zu reinem Grün (Gürtel), grellem
    #: Gelb (Unterkleid) und reinem Weiß (Bart). Die Startwerte sind an der Vorlage gemessen (`Kostuemparameter.FARBEN`).
    FARBEN_FEST = True
    #: Welche Teile eine Farbe trägt (die übrigen Stoffe sind immer zu sehen).
    FARBE_TEILE = {
        'stab': ('stab',),
        'kristall': ('stab',),
        'bart': ('bart', 'haar'),
        'hut': ('hut',),
        'schuhe': ('schuhe',),
        'borte': ('borte',),
    }

    def __init__(self, kennung, schritt=None):
        self.kennung = kennung
        self.schritt = float(schritt or self.SCHRITT_START)

    def _zufall(self, runde):
        saat = int(hashlib.sha256(('%s:%d' % (self.kennung, runde)).encode()).hexdigest()[:12], 16)
        return Zufallsstrom.default_rng(saat)

    veraenderlich = classmethod(Iterationsoptimierer.veraenderlich.__func__)          # dieselbe Rechnung wie `Iterationsoptimierer.veraenderlich` (bis 08.11.2026 eine Kopie hier)

    kandidaten = Iterationsoptimierer.kandidaten          # dieselbe Rechnung wie `Iterationsoptimierer.kandidaten` (bis 08.11.2026 eine Kopie hier)

    def anpassen(self, verbessert):
        faktor = self.WACHSEN if verbessert else self.SCHRUMPFEN
        self.schritt = min(self.SCHRITT_MAX, max(self.SCHRITT_MIN, self.schritt * faktor))
        return self.schritt
