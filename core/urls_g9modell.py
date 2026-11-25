# -*- coding: utf-8 -*-
"""Routen an der Genesis-Figur, die zu gespeicherten Modellen gehören (23.11.2026; hier, weil `urls_charakter.py` und `urls.py` über 300 Zeilen liegen):
die MB-Lab-Vorlagen als Auswahl „Preset“ im Reglerabschnitt HumanBody (`G9reglerapi.mblab_vorlagen`) und Haar und Bart der Haar-Engine eines gespeicherten
Modells (`G9haarnetzapi`, `Modellhaarnetze`). Seit 25.11.2026 auch das Feld eines Reglerzugs (`G9reglerzugapi`) und der genaue Zug in einer
Antwort (`G9nachformenapi`)."""
from django.urls import path

from .api.g9haarnetzapi import G9haarnetzapi
from .api.g9nachformen import G9nachformenapi
from .api.g9reglerapi import G9reglerapi
from .api.g9reglerzug import G9reglerzugapi

__all__ = ['G9MODELL']

G9MODELL = [
    path('api/character/genesis9-figur/garderobe/<str:kennung>/reglerzug/', G9reglerzugapi.stueck, name='g9_figur_stueckreglerzug'),
    path('api/character/genesis9-figur/<str:name>/reglerzug/', G9reglerzugapi.feld, name='g9_figur_reglerzug'),
    path('api/character/genesis9-figur/<str:name>/nachformen/', G9nachformenapi.netz, name='g9_figur_nachformen'),
    path('api/character/genesis9-figur/mblab-vorlagen/', G9reglerapi.mblab_vorlagen, name='g9_figur_mblab_vorlagen'),
    path('api/character/genesis9-figur/haarnetz/<str:name>/netz/', G9haarnetzapi.netz, name='g9_figur_haarnetz'),
    path('api/character/genesis9-figur/haarnetz/<str:name>/bild/<str:datei>', G9haarnetzapi.bild, name='g9_figur_haarnetz_bild'),
]
