# -*- coding: utf-8 -*-
u"""Effektbefehl — die Kommandozeile fuer den Unterprozess eines Effektauftrags.

    kleid_wind:  blender -b --python kleidwind.py -- --bvh … --kleid … --ausgabe …
    figur_def:   python figurfilm.py --modell … --bvh … --ausgabe …

Die Parameter kommen aus dem Auftrag (`Effektauftrag.parameter`), gefiltert
und begrenzt durch die Parameterklasse der Pipeline — dieselbe Klasse, die
der Unterprozess beim Lesen benutzt. Was hier nicht durchkommt, kommt auch
dort nicht an (12.09.2026).

`figur_def` laeuft mit DEMSELBEN Python wie der Server (python14): pyrender,
trimesh, cv2 und Django liegen dort — wie beim Videoweg der Szene
(`core/dienste/figurvideo.py`).
"""
import sys

from django.conf import settings

from effekte.effektparameter import Effektparameter
from effekte.figurparameter import Figurparameter
from ..dienste.modellvorlagen import Modellvorlagen

__all__ = ['Effektbefehl']


class Effektbefehl:

    def __init__(self, auftrag):
        self.auftrag = auftrag

    def parameter(self):
        werte = dict(self.auftrag.parameter or {})
        if self.auftrag.mit_modell:
            pfad = Modellvorlagen.pfad(self.auftrag.modell)
            if pfad is None:
                raise ValueError('Modell nicht gefunden: %s' % self.auftrag.modell)
            return Figurparameter(modell=str(pfad), bvh=self.auftrag.bvh_pfad,
                                  ausgabe=self.auftrag.ausgabe, **werte)
        return Effektparameter(bvh=self.auftrag.bvh_pfad, kleid=self.auftrag.kleid,
                               ausgabe=self.auftrag.ausgabe, **werte)

    def bauen(self):
        parameter = self.parameter()
        if self.auftrag.mit_modell:
            return ([sys.executable, str(settings.EFFEKTE_FIGUR_SKRIPT)]
                    + parameter.argumente())
        return ([str(settings.BLENDER_EXE), '-b', '--python',
                 str(settings.EFFEKTE_SKRIPT), '--'] + parameter.argumente())

    def bilder(self):
        return self.parameter().bilder
