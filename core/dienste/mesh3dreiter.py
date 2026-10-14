# -*- coding: utf-8 -*-
"""Mesh3dreiter — in welchem Reiter der Seite „Mesh-3D“ ein Auftrag steht (13.10.2026).

Edgar: „mach mir in /mesh-3D/ einen neuen Reiter, das soll eine Kopie der aktuellen Seite sein, aber nur mit ausgewählten Testaufträgen. Es soll möglich sein, Jobs aus einem Tab zum
anderen zu verschieben.“ Die Reiter sind dieselbe Liste, nur nach Zuordnung gefiltert; verschoben wird die Zuordnung, nie der Auftrag.

Die Zuordnung steht in EINER Datei neben den Aufträgen, `<OBJECTS_ROOT>/blendimport/mesh3d_reiter.json` (`{kennung: reiter}`), nicht in `stand.json`: Den schreibt der Arbeitsprozess eines
rechnenden Auftrags aus seinem eigenen Wörterbuch neu und risse ein dort ergänztes Feld mit weg. Was nicht in der Datei steht, liegt im ersten Reiter („Aufträge“) — ein neuer Auftrag, eine
Kopie ohne Eintrag und jeder Auftrag von vor diesem Umbau. Ein Eintrag für einen Auftrag, den es nicht mehr gibt, schadet nicht und wird beim nächsten Schreiben mit aufgeräumt.
"""

import json
import logging

from ..atomic_write import AtomarSchreiber
from ..daten.blendimportablage import Blendimportablage

logger = logging.getLogger('core')

__all__ = ['Mesh3dreiter']


class Mesh3dreiter:
    DATEI = 'mesh3d_reiter.json'
    #: (Schlüssel, Titel, Symbol) in der Reihenfolge der Leiste; der erste ist der Reiter für alles, was nirgends zugeordnet ist.
    REITER = (
        ('auftraege', 'Aufträge', 'fa-cube'),
        ('test', 'Testaufträge', 'fa-flask'),
    )

    @classmethod
    def schluessel(cls):
        return [r[0] for r in cls.REITER]

    @classmethod
    def erster(cls):
        return cls.REITER[0][0]

    @classmethod
    def pfad(cls):
        return Blendimportablage.wurzel() / cls.DATEI

    @classmethod
    def zuordnung(cls):
        """`{kennung: reiter}` aus der Datei; fehlt sie oder ist sie unlesbar, ist alles im ersten Reiter (und die Datei bleibt unberührt)."""
        try:
            daten = json.loads(cls.pfad().read_text(encoding='utf-8'))
        except FileNotFoundError:
            return {}
        except (OSError, ValueError):
            logger.warning('Mesh-3D: %s nicht lesbar — alle Aufträge stehen im Reiter „%s“', cls.pfad(), cls.erster())
            return {}
        return {str(k): v for k, v in daten.items() if v in cls.schluessel()} if isinstance(daten, dict) else {}

    @classmethod
    def von(cls, kennung, zuordnung=None):
        return (zuordnung if zuordnung is not None else cls.zuordnung()).get(str(kennung), cls.erster())

    @classmethod
    def aufteilen(cls, kennungen):
        """`{reiter: [kennung, …]}` mit allen Reitern (auch leeren), die Reihenfolge der Kennungen bleibt."""
        zuordnung = cls.zuordnung()
        aus = {k: [] for k in cls.schluessel()}
        for kennung in kennungen:
            aus[cls.von(kennung, zuordnung)].append(kennung)
        return aus

    @classmethod
    def setzen(cls, kennungen, reiter):
        """Die Aufträge in einen Reiter legen → Zahl der Aufträge, die dadurch wirklich den Reiter wechseln. Unbekannte Kennungen und Reiter sind ein `ValueError`."""
        if reiter not in cls.schluessel():
            raise ValueError('Unbekannter Reiter: %s' % reiter)
        vorhanden = set(Blendimportablage.alle())
        unbekannt = [k for k in kennungen if k not in vorhanden]
        if unbekannt:
            raise ValueError('Kein Auftrag %s' % ', '.join(unbekannt))
        zuordnung = cls.zuordnung()
        gewechselt = sum(1 for k in kennungen if cls.von(k, zuordnung) != reiter)
        zuordnung.update({k: reiter for k in kennungen})
        # Aufgeräumt wird beim Schreiben: nur Aufträge, die es gibt, und nur, was vom ersten Reiter abweicht.
        cls._schreiben({k: v for k, v in zuordnung.items() if k in vorhanden and v != cls.erster()})
        logger.info('Mesh-3D: %d Auftrag/Aufträge in den Reiter „%s“ gelegt (%s)', len(kennungen), reiter, ', '.join(kennungen))
        return gewechselt

    @classmethod
    def erben(cls, quelle, kopie):
        """Eine Kopie steht im Reiter ihrer Quelle — wer in „Testaufträge“ kopiert, sucht die Kopie dort, nicht im anderen Reiter."""
        reiter = cls.von(quelle)
        if reiter != cls.erster():
            cls.setzen([kopie], reiter)

    @classmethod
    def _schreiben(cls, zuordnung):
        cls.pfad().parent.mkdir(parents=True, exist_ok=True)
        AtomarSchreiber.json_schreiben(cls.pfad(), dict(sorted(zuordnung.items())))
