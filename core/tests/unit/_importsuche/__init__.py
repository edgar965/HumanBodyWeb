# -*- coding: utf-8 -*-
"""Importsuche — die Hilfsklassen von `test_lokale_importe`.

Fuehrender Unterstrich mit Absicht: `testaufbau` erkennt daran, dass hier
keine Testdatei liegt.

Bis zum 27.08.2026 stand alles in einer Datei `_importsuche.py` — drei
eigenstaendige Klassen nebeneinander, gemeldet von `klassen-je-datei`.

* `Modulnamen`    — welche Namen ein Modul auf Modulebene fuehrt, ohne es
                    auszufuehren
* `Lokalerimport` — ein Import, der unterhalb einer Funktion steht
* `Modulsuche`    — sammelt sie aus einem Verzeichnis

Warum das ueberhaupt geprueft wird, steht im Kopf von
`test_lokale_importe.py`.
"""

from .grundwerte import AUSSEN, EIGENE, WURZEL
from .lokalerimport import Lokalerimport
from .modulnamen import Modulnamen
from .modulsuche import Modulsuche

__all__ = ['AUSSEN', 'EIGENE', 'WURZEL', 'Lokalerimport', 'Modulnamen',
           'Modulsuche']
