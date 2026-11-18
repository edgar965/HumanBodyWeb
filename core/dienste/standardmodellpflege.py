# -*- coding: utf-8 -*-
"""Standardmodellpflege — Standard-Modelle im Dialog „Charakter hinzufügen“ umbenennen und ausblenden (16.11.2026).

Edgar, 16.11.2026: „bei den gespeicherten Modellen gibt es Buttons zum Ändern des Namens und löschen. Mach das auch bei den Standard Modellen rein“.
Ein Standard-Modell ist keine eigene Datei: Genesis-9-Charaktere sind Reglerstellungen aus der Daz-Bibliothek, die Körpertypen von HumanBody kommen aus
MB-Lab, SMPL-X und MakeHuman aus ihren Modelldateien. Umbenennen ändert deshalb nur den ANZEIGENAMEN, Löschen BLENDET AUS — die Daten bleiben, wie
bei einem Daz-Stück der Garderobe (`G9garderobepflege`). Der Name des Eintrags (`name`, damit lädt der Dialog) bleibt immer derselbe.

    {"genesis9": {"namen": {"kt_margie_g8": "Margie"}, "ausgeblendet": ["mblab_typ_w_type_giant"]}, "modell": {…}}

Datei `3DObjects/models/standardmodelle_pflege.json` (neben `modellordner.json`), unteilbar geschrieben (`AtomarSchreiber`) unter einer Sperre.
"""

import json
import logging
import threading
from pathlib import Path

from django.conf import settings

from ..atomic_write import AtomarSchreiber

logger = logging.getLogger('core')

__all__ = ['Standardmodellpflege']


class Standardmodellpflege:
    #: Reiter des Dialogs (`Figurkataloge.QUELLEN`).
    QUELLEN = ('genesis9', 'modell', 'smpl', 'makehuman', 'uma', 'umapython')
    HOECHSTENS = 80
    _sperre = threading.Lock()

    @staticmethod
    def datei():
        return Path(settings.OBJECTS_ROOT) / 'models' / 'standardmodelle_pflege.json'

    @classmethod
    def lesen(cls):
        """`{quelle: {namen: {name: anzeige}, ausgeblendet: [name]}}`; fehlt die Datei: leer."""
        try:
            daten = json.loads(cls.datei().read_text(encoding='utf-8'))
        except FileNotFoundError:
            return {}
        except (OSError, ValueError):
            logger.exception('Standardmodellpflege: %s nicht lesbar', cls.datei())
            raise
        return daten if isinstance(daten, dict) else {}

    @classmethod
    def _quelle(cls, quelle):
        if quelle not in cls.QUELLEN:
            raise ValueError('Unbekannter Reiter: %s' % quelle)
        return quelle

    @classmethod
    def umbenennen(cls, quelle, name, neu):
        """Den Anzeigenamen setzen; leer oder gleich dem Namen = zurück zur Vorgabe. Gibt den neuen Anzeigenamen zurück."""
        quelle, name, neu = cls._quelle(str(quelle)), str(name or '').strip(), str(neu or '').strip()
        if not name:
            raise ValueError('Kein Modell genannt')
        if len(neu) > cls.HOECHSTENS:
            raise ValueError('Name zu lang (höchstens %d Zeichen)' % cls.HOECHSTENS)
        with cls._sperre:
            daten = cls.lesen()
            eintrag = daten.setdefault(quelle, {'namen': {}, 'ausgeblendet': []})
            namen = eintrag.setdefault('namen', {})
            if neu:
                namen[name] = neu
            else:
                namen.pop(name, None)
            cls._schreiben(daten)
        logger.info('Standard-Modell umbenannt: %s/%s -> %s', quelle, name, neu or '(Vorgabe)')
        return neu

    @classmethod
    def ausblenden(cls, quelle, name):
        quelle, name = cls._quelle(str(quelle)), str(name or '').strip()
        if not name:
            raise ValueError('Kein Modell genannt')
        with cls._sperre:
            daten = cls.lesen()
            eintrag = daten.setdefault(quelle, {'namen': {}, 'ausgeblendet': []})
            weg = eintrag.setdefault('ausgeblendet', [])
            if name not in weg:
                weg.append(name)
            cls._schreiben(daten)
        logger.info('Standard-Modell ausgeblendet: %s/%s', quelle, name)
        return True

    @classmethod
    def _schreiben(cls, daten):
        ziel = cls.datei()
        ziel.parent.mkdir(parents=True, exist_ok=True)
        AtomarSchreiber.json_schreiben(ziel, daten)
