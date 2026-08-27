# -*- coding: utf-8 -*-
"""Testfigur — die Endpunkte der Seite „Test → Character".

Aus `core/test_character_api.py` (564 Zeilen, Spitzenbefund von `dateigroesse`)
am 17.08.2026 hierher aufgeteilt, am 27.08.2026 in Klassen gefasst
(Befunde `freie-funktionen`, `klassen-je-datei`):

    testkern.py                die getrennt geladene Testfassung samt Daten
    netzansichten.py           `Testnetz` — die Netzantwort einer Anfrage
    netzendpunkte.py           `Testendpunkte` — Netz, Regler, Gewichte, Skelett
    quellenschau.py            Quelltext und Datenbestand für die Anzeige
    verwaltung.py              `Figurenwechsel` — Figur aktiv setzen
    verwaltungsendpunkte.py    `Testverwaltung` — Fassung, Neuladen, Wechsel

Die URL-Namen sind unverändert; `urls.py` ruft die Klassenmethoden.
"""

from .netzansichten import Testnetz
from .netzendpunkte import Testendpunkte
from .quellenschau import Quellenschau
from .testkern import Testkern
from .verwaltung import Figurenwechsel
from .verwaltungsendpunkte import Testverwaltung

__all__ = ['Testkern', 'Testnetz', 'Testendpunkte', 'Quellenschau',
           'Figurenwechsel', 'Testverwaltung']
