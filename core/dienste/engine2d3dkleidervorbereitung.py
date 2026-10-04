# -*- coding: utf-8 -*-
"""Engine2d3dKleidervorbereitung — Schritt „vorbereitung" von „2D3D Kleider": die Fotos aufbereiten (03.10.2026).

Edgar (03.10.2026): „vielleicht machst du auf der Jobseite einen ersten Vorschritt mit Hintergrund entfernen und diesen Skalierungen. Dieser Schritt ist
getrennt startbar. Zeige die Bilder nach dem Schritt unter den Originalbildern."

Der Schritt ist der erste Teil des Runners `_run_mesh.py` (Freistellen, auf Wunsch Ausrichten, Zuschnitt, Licht — `vorbereitung()`), allein gerechnet: dieselbe Auftragsbeschreibung wie
der Schritt „Netz" (`Engine2d3dKleidernetz`), mit `bis = vorbereitung`. Der Runner legt die Ergebnisse in `vorbereitet/` ab (die PNG in voller Größe, `vorschau_<stamm>.webp` und
`vorbereitung.json`, siehe `mesh_vorbereitungsstand`); die Seite zeigt sie unter den Originalen (`Engine2d3dKleidervorbereitungsliste`). Der Schritt „Netz" übernimmt sie, wenn Fotos und
Optionen noch dazu passen, und lädt BiRefNet sonst selbst.
"""

import logging

from .engine2d3dkleidernetz import Engine2d3dKleidernetz

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleidervorbereitung']


class Engine2d3dKleidervorbereitung(Engine2d3dKleidernetz):
    def beschreibung(self):
        return dict(super().beschreibung(), bis='vorbereitung')

    def _abschluss(self):
        """Kein Netz: Der Runner meldet nur die Zahl der Fotos; die Bilder stehen in `vorbereitet/`."""
        self.job.ergebnis = {**(self.job.ergebnis or {}), 'vorbereitung': dict(self._ergebnis)}
        self.lauf.sichern('ergebnis')
        logger.info('2D3D Kleider %s: Vorbereitung fertig (%s Fotos)', self.job.kennung, self._ergebnis.get('vorbereitung'))
