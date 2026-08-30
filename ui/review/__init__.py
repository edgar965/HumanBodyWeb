# -*- coding: utf-8 -*-
u"""Codebereiche fuer Hilfe -> Review, nach Themen getrennt.

Aus ui/review_bereiche.py herausgeloest (17.08.2026): 965 Zeilen,
59 Bereiche in einer Liste — der Spitzenbefund von `dateigroesse`.
Wer am Retarget-Bereich arbeitete, scrollte durch Blender,
VideoToBVH und djangoBase.

Die Pfade sind relativ zu DJANGOBASE["review_wurzel"] (dem
Arbeitsverzeichnis); ein Bereich darf mit "wurzel" eine eigene
angeben (djangoBase liegt daneben).

REIHENFOLGE = ANZEIGEREIHENFOLGE auf der Review-Seite. Sie folgt
der Schichtung: Kern, Browser, Studio, Blender, ML-Kette,
Stoffsimulation, Django-Teil, geteilte Bibliothek.
"""
from .kern import BEREICHE as KERN
from .frontend import BEREICHE as FRONTEND
from .bvhstudio import BEREICHE as STUDIO
from .blender import BEREICHE as BLENDER
from .videotobvh import BEREICHE as VIDEOTOBVH
from .kollision import BEREICHE as KOLLISION
from .web_api import BEREICHE as WEB_API
from .web import BEREICHE as WEB
from .djangobase import BEREICHE as DJANGOBASE

REVIEW_BEREICHE = (
    KERN + FRONTEND + STUDIO + BLENDER + VIDEOTOBVH + KOLLISION
    + WEB_API + WEB + DJANGOBASE)
