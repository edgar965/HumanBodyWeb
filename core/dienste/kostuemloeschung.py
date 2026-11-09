# -*- coding: utf-8 -*-
"""Kostuemloeschung — Runden aus der Tabelle „Iterationen" löschen (einzeln oder viele auf einmal).

Gelöscht wird der Eintrag in `ergebnis['iterationen']` und alles, was zu ihm gehört: Vergleichstafel, Renders
je Blickwinkel, Fototextur-Ansichten, Modell-GLB, .blend, Bericht (`dateien`, `je_ansicht[].render/.textur`).
Die Kurve (`ergebnis['kostuem']['verlauf']`) und der beste Wertesatz bleiben — sie sind Geschichte bzw. Stand
des Kreislaufs, kein Anzeigestück.

Während eines Laufs schreibt NUR der Lauf in `ergebnis`: Er hält es minutenlang im Speicher und würde eine
Löschung der Seite bei der nächsten Runde wieder wegspeichern (dieselbe Falle wie
`Blendermodellauftrag.bilder_sichern`). Die Seite legt deshalb eine Liste an (`arbeit/rundenloeschen.json`),
und der Lauf arbeitet sie zu Beginn jeder Runde ab (`Kostuemkreislauf`). Ohne Lauf arbeitet der Endpunkt sie
selbst ab.
"""

import json
import logging
from pathlib import Path

from ..daten.blendermodellablage import Blendermodellablage
from .iterationsloeschung import Iterationsloeschung

logger = logging.getLogger('core')

__all__ = ['Kostuemloeschung']


class Kostuemloeschung:
    LISTE = 'rundenloeschen.json'

    def __init__(self, job):
        self.job = job
        self.ablage = Blendermodellablage(job.kennung)

    def _pfad(self):
        return self.ablage.arbeit(self.LISTE)

    def vorgemerkt(self):
        """Die Rundennummern, die auf das Löschen warten."""
        try:
            with open(self._pfad(), encoding='utf-8') as f:
                return sorted({int(n) for n in json.load(f)})
        except OSError, ValueError, TypeError:
            return []

    vormerken = Iterationsloeschung.vormerken          # dieselbe Rechnung wie `Iterationsloeschung.vormerken` (bis 08.11.2026 eine Kopie hier)

    abarbeiten = Iterationsloeschung.abarbeiten          # dieselbe Rechnung wie `Iterationsloeschung.abarbeiten` (bis 08.11.2026 eine Kopie hier)

    def _dateien_loeschen(self, eintrag):
        namen = {str(v) for v in (eintrag.get('dateien') or {}).values()}
        for a in eintrag.get('je_ansicht') or []:
            if isinstance(a, dict):
                namen |= {str(a[k]) for k in ('render', 'textur', 'sicht') if a.get(k)}
        for name in namen:
            if Path(name).name != name:  # nie aus dem Ordner „iterationen" heraus
                logger.warning(
                    'BlenderModel %s: Dateiname %r der Runde %s übergangen',
                    self.job.kennung,
                    name,
                    eintrag.get('runde'),
                )
                continue
            try:
                self.ablage.iterationen(name).unlink(missing_ok=True)
            except OSError as fehler:  # gesperrt (wird gerade ausgeliefert): der Eintrag geht trotzdem
                logger.warning('BlenderModel %s: %s nicht gelöscht: %s', self.job.kennung, name, fehler)
