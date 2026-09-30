# -*- coding: utf-8 -*-
"""Huellenstand — die Umriss-Hülle eines Blender-Prozesses: Masken einmal laden, Normierung je Ausgangsmodell
halten.

Die Hülle (`Kostuemhuelle`) braucht die Normierung der Vorlage auf das Modell (`Projektion.abbildung`: Höhe
und Schwerpunkt des Umrisses im Render). Sie stammt aus einem Render des AUSGANGSMODELLS (Auftrag `basis`,
ohne Hülle gebaut) — nicht aus dem Kandidaten selbst, der ja erst mit der Hülle entsteht. Damit hängt das
Ergebnis eines Kandidaten nur von ihm und vom Ausgangsmodell ab, nicht davon, welcher Prozess ihn rechnet oder
was dieser vorher gebaut hat. Wechselt das Ausgangsmodell (eine Runde wurde übernommen), kostet die neue
Normierung einen Bau und einen Render (~1 s).
"""

import json
import os
import shutil

from effekte.blender.kostuem.kostuem import Kostuem
from effekte.blender.kostuem.kostuemhuelle import Kostuemhuelle

__all__ = ['Huellenstand']


class Huellenstand:
    def __init__(self, bau):
        """`bau`: der `Kostuembau` (Ansichten, Projektion, Haltung)."""
        self.bau = bau
        self.huelle = None
        self._masken = None
        self._basis = None

    def fuer(self, auftrag, aus):
        """Die Hülle für diesen Auftrag, auf sein Ausgangsmodell normiert — oder None (Auftrag ohne `masken`)."""
        masken = auftrag.get('masken')
        if not masken:
            return None
        schluessel = json.dumps(masken, sort_keys=True)
        if self._masken != schluessel:
            self.huelle = Kostuemhuelle(masken, self.bau.projektion)
            self._masken, self._basis = schluessel, None
        basis = auftrag.get('basis') or auftrag['kandidaten'][0]['parameter']
        if self._basis != json.dumps(basis, sort_keys=True):
            self._normieren(basis, auftrag['winkel'], aus)
            self._basis = json.dumps(basis, sort_keys=True)
        return self.huelle

    def _normieren(self, basis, winkel, aus):
        bau = self.bau
        Kostuem.entfernen()
        gestellt = bau.gestellt(basis)
        Kostuem(gestellt, bau.kopf['vorn_grad']).bauen(basis)
        # Mehrere Arbeiter teilen sich `aus` — jeder braucht seinen eigenen Ordner (sonst räumt einer dem
        # anderen weg).
        ordner = os.path.join(aus, '_normierung_%d' % os.getpid())
        try:
            dateien = bau.ansichten.rendern(winkel, ordner)
            self.huelle.normieren(
                {
                    w: bau.projektion.abbildung(os.path.join(ordner, dateien[str(int(round(w)))]))
                    for w in self.huelle.masken
                    if str(int(round(w))) in dateien
                }
            )
        finally:
            shutil.rmtree(ordner, ignore_errors=True)
            Kostuem.entfernen()
