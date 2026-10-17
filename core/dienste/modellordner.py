# -*- coding: utf-8 -*-
"""Modellordner — Ordner für die gespeicherten Modelle im Dialog „Charakter hinzufügen“ (15.10.2026).

Edgar: „bei Modell hinzufügen (im Fenster Charakter), mach mir ein UI so dass ich Ordner Anlegen kann mit Namen bei den gespeicherten Modellen.
ich möchte Modelle zu den Ordnern verschieben können, auch batch verschieben“.

Ein Ordner ist eine ZUORDNUNG, kein Verzeichnis: die Modelle bleiben `data/models/<Name>.json` (UMA: `Figuren/uma/<Name>.glb`). Jeder Lader — Szene, Studio,
Theatre, Startfigur, Mesh-3D, Export — findet ein Modell über seinen Namen; ein Unterverzeichnis hätte jeden davon gebrochen. Die Zuordnung steht in
`3DObjects/models/modellordner.json` (nicht in `data/`), je Reiter des Dialogs (`quelle`):

    {"genesis9": {"ordner": ["Edgar", "Tests"], "modelle": {"Edgar Mesh 2": "Edgar"}}, "modell": {…}}

Ein Modell ohne Eintrag steht oben ohne Ordner. Umbenennen und Löschen eines Modells ziehen den Eintrag nach (`umbenannt`, `geloescht`, gerufen aus
`Modellablage` und `Umaablage`). Geschrieben wird unteilbar (`AtomarSchreiber`) und unter einer Sperre — zwei Anfragen zugleich verlören sonst eine Änderung.
"""

import json
import logging
import re
import threading
from pathlib import Path

from django.conf import settings

from ..atomic_write import AtomarSchreiber

logger = logging.getLogger('core')

__all__ = ['Modellordner']


class Modellordner:
    #: Reiter des Dialogs mit einem Bereich „Gespeicherte Modelle“ (`Figurkataloge.QUELLEN`).
    QUELLEN = ('genesis9', 'modell', 'smpl', 'uma')
    HOECHSTENS = 60
    _sperre = threading.Lock()

    @staticmethod
    def datei():
        return Path(settings.OBJECTS_ROOT) / 'models' / 'modellordner.json'

    @classmethod
    def lesen(cls):
        """Die ganze Zuordnung; fehlt die Datei: leer. Eine unlesbare Datei wird gemeldet, nicht überschrieben (`_schreiben` liest sie vorher wieder)."""
        try:
            daten = json.loads(cls.datei().read_text(encoding='utf-8'))
        except FileNotFoundError:
            return {}
        except (OSError, ValueError):
            logger.exception('Modellordner: %s nicht lesbar', cls.datei())
            raise
        return daten if isinstance(daten, dict) else {}

    @classmethod
    def _quelle(cls, daten, quelle):
        if quelle not in cls.QUELLEN:
            raise ValueError('Unbekannter Reiter: %s' % quelle)
        q = daten.setdefault(quelle, {})
        q.setdefault('ordner', [])
        q.setdefault('modelle', {})
        return q

    @classmethod
    def name_pruefen(cls, name):
        name = re.sub(r'[\x00-\x1f]', '', re.sub(r'\s+', ' ', str(name or ''))).strip()[: cls.HOECHSTENS]
        if not name:
            raise ValueError('Der Ordner braucht einen Namen')
        return name

    @classmethod
    def _schreiben(cls, daten):
        cls.datei().parent.mkdir(parents=True, exist_ok=True)
        AtomarSchreiber.json_schreiben(cls.datei(), daten)

    @classmethod
    def anlegen(cls, quelle, name):
        name = cls.name_pruefen(name)
        with cls._sperre:
            daten = cls.lesen()
            q = cls._quelle(daten, quelle)
            if any(o.lower() == name.lower() for o in q['ordner']):
                raise ValueError('Den Ordner „%s“ gibt es schon' % name)
            q['ordner'].append(name)
            cls._schreiben(daten)
        logger.info('Modellordner %s: „%s“ angelegt', quelle, name)
        return name

    @classmethod
    def verschieben(cls, quelle, namen, ordner):
        """`namen` in den Ordner `ordner` legen; leerer `ordner` = ohne Ordner. → Anzahl."""
        namen = [str(n) for n in namen or [] if str(n).strip()]
        if not namen:
            raise ValueError('Keine Modelle gewählt')
        with cls._sperre:
            daten = cls.lesen()
            q = cls._quelle(daten, quelle)
            if ordner and ordner not in q['ordner']:
                raise ValueError('Den Ordner „%s“ gibt es nicht' % ordner)
            for n in namen:
                if ordner:
                    q['modelle'][n] = ordner
                else:
                    q['modelle'].pop(n, None)
            cls._schreiben(daten)
        logger.info('Modellordner %s: %d Modelle nach „%s“ (%s)', quelle, len(namen), ordner or 'ohne Ordner', ', '.join(namen[:10]))
        return len(namen)

    @classmethod
    def umbenannt(cls, alt, neu):
        """Ein Modell heißt jetzt `neu` — sein Ordner geht mit (alle Reiter; ein Name gehört genau einer Datei). Wirft nie."""
        cls._nachziehen(lambda m: m.__setitem__(neu, m.pop(alt)) if alt in m else None, 'umbenannt %s -> %s' % (alt, neu))

    @classmethod
    def geloescht(cls, name):
        """Ein Modell ist gelöscht — sein Eintrag geht mit. Wirft nie."""
        cls._nachziehen(lambda m: m.pop(name, None), 'gelöscht %s' % name)

    @classmethod
    def _nachziehen(cls, tun, was):
        try:
            with cls._sperre:
                daten = cls.lesen()
                vorher = json.dumps(daten, sort_keys=True)
                for q in daten.values():
                    if isinstance(q, dict) and isinstance(q.get('modelle'), dict):
                        tun(q['modelle'])
                if json.dumps(daten, sort_keys=True) != vorher:
                    cls._schreiben(daten)
        except Exception:  # noqa: BLE001 — das Modell ist umbenannt/gelöscht; ein liegengebliebener Eintrag zeigt nur auf nichts
            logger.exception('Modellordner nicht nachgezogen (%s)', was)
