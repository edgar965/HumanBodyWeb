# -*- coding: utf-8 -*-
"""Figurenwechsel — eine abgelegte CharMorph-Figur aktiv setzen.

Aus `core/test_character_api.py` herausgelöst (17.08.2026).
`test_switch_character` hatte 85 Zeilen: Prüfen, Verzeichnis leeren, kopieren,
`commit_info.json` fortschreiben und sechs `global`-Angaben zum Zurücksetzen.
Das Kopieren steht jetzt in `Figurenwechsel`, das Zurücksetzen in
`Testkern.vergessen()` — es stand vorher zweimal wörtlich da.

Die vier Endpunkte, die diese Klasse benutzen, stehen seit dem 27.08.2026 in
`testfigur/verwaltungsendpunkte.py` (Befunde `freie-funktionen`,
`klassen-je-datei`).
"""

import logging
import os
import shutil


from .quellenschau import Quellenschau
from .testkern import Testkern

logger = logging.getLogger(__name__)


class Figurenwechsel:
    """Setzt eine der abgelegten CharMorph-Figuren als aktive Testdaten."""

    #: Ohne diese Datei ist ein Ordner keine brauchbare Figur.
    KENNDATEI = 'faces.npy'

    def __init__(self, name):
        self.name = name or ''
        self.ablage = os.path.join(Testkern.WURZEL, 'charmorph_data')
        self.quelle = os.path.join(self.ablage, self.name)
        self.ziel = Testkern.datenordner()

    @property
    def vorhanden(self):
        return bool(self.name) and os.path.isdir(self.quelle)

    def auswahl(self):
        """Die Figuren, die zur Verfügung stehen."""
        if not os.path.isdir(self.ablage):
            return []
        return sorted(
            d for d in os.listdir(self.ablage)
            if os.path.isdir(os.path.join(self.ablage, d))
            and os.path.isfile(os.path.join(self.ablage, d, self.KENNDATEI)))

    def umschalten(self):
        """Zielordner leeren, Figur hineinkopieren, Fassungsinfo fortschreiben."""
        if os.path.isdir(self.ziel):
            shutil.rmtree(self.ziel)
        os.makedirs(self.ziel, exist_ok=True)
        self._kopieren()
        self._fassung_vermerken()
        Testkern.vergessen()
        logger.info('Testfigur gewechselt auf %s', self.name)

    def _kopieren(self):
        for ordner, _unterordner, dateien in os.walk(self.quelle):
            for name in dateien:
                quelle = os.path.join(ordner, name)
                ziel = os.path.join(self.ziel,
                                    os.path.relpath(quelle, self.quelle))
                os.makedirs(os.path.dirname(ziel), exist_ok=True)
                shutil.copy2(quelle, ziel)

    def _fassung_vermerken(self):
        daten = Quellenschau.fassung()
        if daten is None:
            return
        daten['character'] = self.name
        daten['message'] = 'CharMorphPlugin %s character' % self.name
        Quellenschau.fassung_schreiben(daten)
