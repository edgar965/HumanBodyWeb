# -*- coding: utf-8 -*-
"""Testfigur — die Endpunkte der Seite „Test → Character".

Aus `core/test_character_api.py` (564 Zeilen, Spitzenbefund von `dateigroesse`)
am 17.08.2026 hierher aufgeteilt:

    testkern.py       die getrennt geladene Testfassung samt ihrer Daten
    netzansichten.py  Netz, Regler, Hautgewichte, Skelett
    quellenschau.py   Quelltext und Datenbestand für die Anzeige
    verwaltung.py     Fassung anzeigen, neu laden, Figur wechseln

Die URL-Namen sind unverändert; `urls.py` ruft weiter
`testfigur.test_character_mesh` und Geschwister.
"""

from .netzansichten import (test_character_mesh, test_character_morphs,
                            test_character_rigify_skeleton,
                            test_character_skin_weights)
from .quellenschau import Quellenschau
from .testkern import Testkern
from .verwaltung import (Figurenwechsel, test_character_source, test_reload,
                         test_switch_character, test_version_info)

__all__ = [
    'Testkern', 'Quellenschau', 'Figurenwechsel',
    'test_character_mesh', 'test_character_morphs',
    'test_character_skin_weights', 'test_character_rigify_skeleton',
    'test_version_info', 'test_character_source', 'test_reload',
    'test_switch_character',
]
