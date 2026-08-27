# -*- coding: utf-8 -*-
"""Ein Import, der unterhalb einer Funktion steht.

Aus `_importsuche.py` herausgeloest (Umbau 27.08.2026, Befund
`klassen-je-datei`).
"""

import importlib.util
import logging

from .grundwerte import AUSSEN, EIGENE, WURZEL
from .modulnamen import Modulnamen

logger = logging.getLogger('core')


class Lokalerimport:
    """Ein Import, der unterhalb einer Funktion steht."""

    def __init__(self, datei, knoten, modulname, name=''):
        self.datei = datei
        self.zeile = knoten.lineno
        self.modul = modulname
        #: Der geholte Name bei `from … import name`; leer bei `import x`.
        self.name = name

    def __str__(self):
        kurz = self.datei.relative_to(WURZEL).as_posix()
        ziel = '%s.%s' % (self.modul, self.name) if self.name else self.modul
        return f'{kurz}:{self.zeile} -> {ziel}'

    @property
    def pruefbar(self):
        kopf = self.modul.split('.')[0]
        return kopf in EIGENE and kopf not in AUSSEN

    @property
    def loesbar(self):
        try:
            return importlib.util.find_spec(self.modul) is not None
        except (ImportError, ValueError, AttributeError):
            # Nicht dasselbe wie „gibt es nicht": Hier scheitert schon das
            # Paket DARUEBER. Ohne diese Zeile sehen beide Faelle gleich aus.
            logger.warning('%s: %s nicht aufloesbar', self, self.modul,
                           exc_info=True)
            return False

    @property
    def name_vorhanden(self):
        """Steht der geholte Name im Zielmodul?

        `True`, wenn kein Name geholt wird (`import x`) oder wenn das
        Zielmodul keine Aussage zulaesst (Stern-Import, nicht lesbar) — ein
        Test, der raet, ist schlimmer als einer, der schweigt.
        """
        if not self.name:
            return True
        namen = Modulnamen.von(self.modul)
        if namen is None:
            return True
        if self.name in namen:
            return True
        # Ein Unterpaket wird wie ein Name importiert: `from core import api`.
        # `find_spec` wirft, wenn das Elternteil kein Paket ist — dann ist der
        # Name schlicht nicht da.
        try:
            return importlib.util.find_spec('%s.%s'
                                            % (self.modul, self.name)) is not None
        # stumm gewollt: `find_spec` auf `<modul>.<name>` wirft, wenn das
        # Elternteil kein Paket ist — dann ist der Name schlicht nicht da,
        # und genau das ist die Antwort.
        except (ImportError, ValueError, AttributeError, ModuleNotFoundError):
            return False
