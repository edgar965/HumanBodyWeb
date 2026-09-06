# -*- coding: utf-8 -*-
u"""Modellablage — eine HumanBody-Modellvorgabe umbenennen oder löschen.

Eine Vorgabe ist EINE Datei: `<name>.json` unter `HUMANBODY_MODELS_DIR`. Die
gleichnamige `<name>.scene.json` daneben ist eine SZENE und gehört nicht dazu
(`Modelldateien.modellliste` blendet sie aus); sie bleibt unangetastet.

Der Ordner liegt unter `HumanBody/data/models/`. Das ist der einzige Ort in
`data/`, den die Anwendung beschreibt — dort speichert der Nutzer seine
eigenen Modelle (`Modelldateien.modell_sichern`), es sind keine
Produktionsassets wie Morphs oder Netze. Gelöscht wird deshalb genau eine
Datei, nie ein Verzeichnis und nichts rekursiv. 06.09.2026.
"""
import logging
import os

from django.conf import settings

from ..daten.modellpfad import Modellpfad
from .umaablage import Ablagefehler

logger = logging.getLogger(__name__)

__all__ = ['Modellablage']


class Modellablage:

    ENDUNG = '.json'

    @classmethod
    def ordner(cls):
        return str(settings.HUMANBODY_MODELS_DIR)

    @classmethod
    def pfad(cls, name):
        u"""Der volle Pfad zu `<name>.json`, geprüft gegen Ausbrüche."""
        pfad = Modellpfad.geprueft(cls.ordner(), name, cls.ENDUNG)
        if pfad is None:
            raise Ablagefehler(u'Ungültiger Name: %s' % name)
        return pfad

    @classmethod
    def umbenennen(cls, alt, neu):
        alt_pfad, neu_pfad = cls.pfad(alt), cls.pfad(neu)
        if not os.path.isfile(alt_pfad):
            raise Ablagefehler(u'Modell nicht gefunden: %s' % alt)
        if os.path.exists(neu_pfad):
            raise Ablagefehler(u'Es gibt schon ein Modell %s' % neu)
        os.rename(alt_pfad, neu_pfad)
        logger.info(u'Modell umbenannt: %s -> %s', alt, neu)
        return neu

    @classmethod
    def loeschen(cls, name):
        pfad = cls.pfad(name)
        if not os.path.isfile(pfad):
            raise Ablagefehler(u'Modell nicht gefunden: %s' % name)
        os.remove(pfad)
        logger.info(u'Modell gelöscht: %s', name)
        return True
