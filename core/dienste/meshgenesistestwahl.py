# -*- coding: utf-8 -*-
"""Meshgenesistestwahl — die Häkchen „Haut-KI“ und „Keine Kleider“ eines Tests ohne Job (06.11.2026, Punkt 6 der
Lückenliste beider Pipelines; Edgar: „mach den besten code den wir haben in beiden pipelines“).

Am Job stehen sie in der job.json (`Fotogenesispshuman`). Ein Test ohne Job hat nur `einstellung.json`, die bisher
von Hand geschrieben werden musste. Die Kette liest beides selbst: `Hautohneki` und `Kostuemohnekleider`, der
Job geht vor. Darum gibt es die Häkchen nur bei Tests ohne Job (`Meshgenesisjobtest`), und sie wirken erst beim
nächsten Rechnen. Vorgaben wie in der Kette: Haut-KI an, Keine Kleider aus.

    Meshgenesistestwahl.lesen('venus')                         # {'haut_ki': True, 'keine_kleider': False}
    Meshgenesistestwahl.setzen('venus', 'keine_kleider', True) # True
"""
import json

from ..atomic_write import AtomarSchreiber
from .meshgenesisjobtest import Meshgenesisjobtest
from .meshgenesistest import Meshgenesistest

__all__ = ['Meshgenesistestwahl']


class Meshgenesistestwahl:
    DATEI = 'einstellung.json'
    VORGABE = {'haut_ki': True, 'keine_kleider': False}

    @classmethod
    def _ordner(cls, kennung):
        """Ordner eines Tests ohne Job, auch eines noch nicht gerechneten; sonst None."""
        if kennung in Meshgenesisjobtest.kennungen():
            return None
        return Meshgenesistest.pfad(kennung) or Meshgenesistest.angelegt(kennung)

    @classmethod
    def _inhalt(cls, ordner):
        try:
            wert = json.loads((ordner / cls.DATEI).read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return {}
        return wert if isinstance(wert, dict) else {}

    @classmethod
    def lesen(cls, kennung):
        """Die Häkchen des Tests; None bei einem Test eines Jobs (job.json entscheidet) oder ohne Test."""
        ordner = cls._ordner(kennung)
        if ordner is None:
            return None
        inhalt = cls._inhalt(ordner)
        return {k: inhalt[k] if isinstance(inhalt.get(k), bool) else v for k, v in cls.VORGABE.items()}

    @classmethod
    def setzen(cls, kennung, name, wert):
        """Ein Häkchen speichern, die übrige Datei bleibt. False bei fremdem Namen, Wert oder Test."""
        ordner = cls._ordner(kennung)
        if ordner is None or name not in cls.VORGABE or not isinstance(wert, bool):
            return False
        AtomarSchreiber.json_schreiben(ordner / cls.DATEI, {**cls._inhalt(ordner), name: wert})
        return True
