# -*- coding: utf-8 -*-
u"""Projekteigene Hilfeseiten unter `/hilfe/`.

`ui/urls.py` bindet djangoBase unter `hilfe/` ein; dieses Modul haengt
darunter einen engeren Praefix (`hilfe/kleidung/`).

Die Reihenfolge ist NICHT kritisch — Django setzt die Suche fort, wenn in
einem `include` nichts passt. Nachgeprueft, statt es zu glauben: Mit dem
eigenen Pfad hinter dem djangoBase-include antworten beide Seiten
weiterhin mit 200 (07.09.2026). Er steht trotzdem vorn, als Vorsorge fuer
den Tag, an dem djangoBase ein Auffangmuster bekommt.

Die Menuepunkte kommen ueber `hilfe_extra` in der djangoBase-Konfiguration
(`ui/settings/djangobase_menue.py`) — so bleiben die mitgelieferten
Hilfeseiten stehen. Ein Projekt, das die Gruppe selbst nachbaut, verliert
sie; genau das ist CamTrack passiert (djangoBase-Konfiguration, 24.08.2026).
"""

from django.urls import path

from .api.hilfe_garmentcode import KleidungGarmentcode
from .api.hilfe_kleidung import KleidungAllgemein

urlpatterns = [
    path('', KleidungAllgemein.ansicht(), name='hilfe_kleidung'),
    path('garmentcode/', KleidungGarmentcode.ansicht(),
         name='hilfe_kleidung_garmentcode'),
]
