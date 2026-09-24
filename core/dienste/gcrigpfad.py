# -*- coding: utf-8 -*-
u"""Gcrigpfad — die Rig-Datei eines getragenen GarmentCode-Stuecks, geprueft.

Aus `Garmentcode._rigpfad` (core/api/garmentcode.py) herausgeloest am
24.09.2026: Seit GarmentCode-Stuecke auch in der Lagenrechnung der Daz-Stuecke
stehen (`G9lagenanfrage`, Edgar: „GarmentCode Pants Harem zieht die Kleider bei
Genesis nicht ueber existierende Genesis-Kleider"), braucht ein Dienst dieselbe
Pruefung — und ein Dienst importiert nicht aus der API.

Ein Eintrag `{ordner, rig_datei}` fuehrt nur unterhalb des Ausgabeordners zu
einer `*_rig.json`, die es gibt; sonst None, nicht gemeldet.
"""
import os

__all__ = ['Gcrigpfad']


class Gcrigpfad:
    u"""`pfad(eintrag)` -> absoluter Pfad oder None."""

    ENDUNG = '_rig.json'

    @staticmethod
    def wurzel():
        from GarmentCode.entwurf import Entwurf
        return os.path.abspath(Entwurf.AUSGABE)

    @classmethod
    def pfad(cls, eintrag, wurzel=None):
        u"""Der Pfad eines Eintrags `{ordner, rig_datei}` — oder None, wenn er
        nicht die Form hat, aus der Wurzel fuehrt oder nicht existiert."""
        if not isinstance(eintrag, dict):
            return None
        wurzel = wurzel or cls.wurzel()
        ordner = os.path.basename(str(eintrag.get('ordner') or ''))
        name = str(eintrag.get('rig_datei') or '')
        if not ordner or not name.endswith(cls.ENDUNG):
            return None
        pfad = os.path.abspath(os.path.join(wurzel, ordner, name))
        if pfad.startswith(wurzel + os.sep) and os.path.isfile(pfad):
            return pfad
        return None
