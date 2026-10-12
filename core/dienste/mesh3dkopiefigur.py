# -*- coding: utf-8 -*-
"""Mesh3dkopiefigur — den Auftrag „Mesh to 3D“ eines Imports mitkopieren (11.10.2026).

Ein Mesh-3D-Auftrag IST ein Modell-Import; im Schritt „figur“ ruft er einen gewöhnlichen Auftrag „Mesh to 3D“ (`Meshfigurauftrag`), dessen UUID im Stand steht
(`ergebnis.figur.id`). Eine Kopie des Imports „mit allen Daten“ braucht dafür einen EIGENEN Auftrag: Zeigten zwei Imports auf denselben, nähme das Löschen des einen dem anderen
die Figur (`Blendimportloeschen._auftrag_entfernen`). Wie `Engine2d3dKleiderauftragskopie`: der ganze Ordner, die Zeile mit neuer Kennung und ID in den JSON-Feldern; NICHT mit:
`pid`, `error_message` und `modell` (der Name des gespeicherten Modells gehört dem Quellauftrag).
"""

import json
import logging
import uuid

from django.db import transaction
from django.utils import timezone

from ..daten.auftragskennung import Auftragskennung
from ..daten.meshfigurablage import Meshfigurablage
from .ordnerkopie import Ordnerkopie

logger = logging.getLogger('core')

__all__ = ['Mesh3dkopiefigur']


class Mesh3dkopiefigur:
    FELDER = ('status', 'schritt', 'progress', 'progress_detail', 'optionen', 'eingang', 'ergebnis', 'started_at', 'finished_at')
    JSON_FELDER = ('optionen', 'eingang', 'ergebnis')

    def __init__(self, job, name):
        """`job`: der Auftrag „Mesh to 3D“ der Quelle; `name`: sein Name in der Kopie."""
        from ..models import Meshfigurauftrag

        self.job = job
        self.name = name
        self.neue_kennung = Auftragskennung.frei(timezone.now(), lambda k: Meshfigurauftrag.objects.filter(kennung=k).exists())
        self.neue_id = uuid.uuid4()
        #: Was in Zeile und kleinen JSON-Dateien durch die Werte der Kopie ersetzt wird.
        self.ersetzungen = {job.kennung: self.neue_kennung, str(job.id): str(self.neue_id)}
        self.kopie = Ordnerkopie(Meshfigurablage(job.kennung).ordner(), Meshfigurablage(self.neue_kennung).ordner(), self.ersetzungen)

    def _wert(self, feld):
        wert = getattr(self.job, feld)
        if feld in self.JSON_FELDER:
            return json.loads(self.kopie.ersetzen(json.dumps(wert, ensure_ascii=False)))
        return wert

    def kopieren(self):
        """Ordner, dann Zeile → der neue `Meshfigurauftrag`. Scheitert etwas, bleibt weder Ordner noch Zeile."""
        from ..models import Meshfigurauftrag

        zahl, groesse = self.kopie.kopieren()
        try:
            with transaction.atomic():
                neu = Meshfigurauftrag.objects.create(id=self.neue_id, kennung=self.neue_kennung, name=self.name[:200],
                                                      **{feld: self._wert(feld) for feld in self.FELDER})
        except BaseException:
            self.kopie.entfernen()
            raise
        logger.info('Kopie Mesh to 3D: %s (%s) → %s, %d Dateien, %.1f MB', self.job.name, self.job.kennung, self.neue_kennung, zahl, groesse / 1e6)
        return neu

    def zuruecknehmen(self, neu):
        """Zeile und Ordner der Kopie wieder entfernen (der Import, zu dem sie gehört, ist gescheitert)."""
        neu.delete()
        self.kopie.entfernen()
